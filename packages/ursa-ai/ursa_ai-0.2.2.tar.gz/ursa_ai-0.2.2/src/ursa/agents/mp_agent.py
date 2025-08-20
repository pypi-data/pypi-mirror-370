import os
import json
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from mp_api.client import MPRester
from langchain.schema import Document

import os
import pymupdf  
import requests
import feedparser
from PIL import Image
from io import BytesIO
import base64
from urllib.parse import quote
from typing_extensions import TypedDict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, START
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from openai import OpenAI

from .base import BaseAgent




client = OpenAI()

embeddings = OpenAIEmbeddings()

class PaperMetadata(TypedDict):
    arxiv_id: str
    full_text: str

class PaperState(TypedDict, total=False):
    query: str
    context: str
    papers: List[PaperMetadata]
    summaries: List[str]
    final_summary: str


def describe_image(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "You are a scientific assistant who explains plots and scientific diagrams."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this scientific image or plot in detail."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ],
            },
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


def extract_and_describe_images(pdf_path: str, max_images: int = 5) -> List[str]:
    doc = pymupdf.open(pdf_path)
    descriptions = []
    image_count = 0

    for page_index in range(len(doc)):
        if image_count >= max_images:
            break
        page = doc[page_index]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            if image_count >= max_images:
                break
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(BytesIO(image_bytes))

            try:
                desc = describe_image(image)
                descriptions.append(f"Page {page_index + 1}, Image {img_index + 1}: {desc}")
            except Exception as e:
                descriptions.append(f"Page {page_index + 1}, Image {img_index + 1}: [Error: {e}]")
            image_count += 1

    return descriptions


def remove_surrogates(text: str) -> str:
    return re.sub(r'[\ud800-\udfff]', '', text)

class MaterialsProjectAgent(BaseAgent):
    def __init__(
        self,
        llm="openai/o3-mini",
        summarize: bool = True,
        max_results: int = 3,
        database_path: str = 'mp_database',
        summaries_path: str = 'mp_summaries',
        vectorstore_path: str = 'mp_vectorstores',
        **kwargs
    ):
        super().__init__(llm, **kwargs)
        self.summarize        = summarize
        self.max_results      = max_results
        self.database_path    = database_path
        self.summaries_path   = summaries_path
        self.vectorstore_path = vectorstore_path
        
        os.makedirs(self.database_path,    exist_ok=True)
        os.makedirs(self.summaries_path,   exist_ok=True)
        os.makedirs(self.vectorstore_path, exist_ok=True)

        self.embeddings = OpenAIEmbeddings()  # or your preferred embedding
        self.graph = self._build_graph()

    def _fetch_node(self, state: Dict) -> Dict:
        f   = state["query"]
        els = f["elements"]                  # e.g. ["Ga","In"]
        bg  = (f["band_gap_min"], f["band_gap_max"])
        e_above_hull = (0, 0)                # only on-hull (stable)
        mats = []
        with MPRester() as mpr:
            # get ALL matching materials…
            all_results = mpr.materials.summary.search(
                elements=els,
                band_gap=bg,
                energy_above_hull=e_above_hull,
                is_stable=True              # equivalent filter
            )
            # …then take only the first `max_results`
            for doc in all_results[: self.max_results]:
                mid = doc.material_id
                data = doc.dict()
                # cache to disk
                path = os.path.join(self.database_path, f"{mid}.json")
                if not os.path.exists(path):
                    with open(path, "w") as f:
                        json.dump(data, f, indent=2)
                mats.append({"material_id": mid, "metadata": data})

        return {**state, "materials": mats}

    def _get_or_build_vectorstore(self, text: str, mid: str):
        """Build or load a Chroma vectorstore for a single material's description."""
        persist_dir = os.path.join(self.vectorstore_path, mid)
        if os.path.exists(persist_dir):
            store = Chroma(persist_directory=persist_dir, embedding_function=self.embeddings)
        else:
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            docs = splitter.create_documents([text])
            store = Chroma.from_documents(docs, self.embeddings, persist_directory=persist_dir)
        return store.as_retriever(search_kwargs={"k": 5})

    def _summarize_node(self, state: Dict) -> Dict:
        """Summarize each material via LLM over its metadata."""
        # prompt template
        prompt = ChatPromptTemplate.from_template("""
You are a materials-science assistant. Given the following metadata about a material, produce a concise summary focusing on its key properties:

{metadata}
        """)
        chain = prompt | self.llm | StrOutputParser()

        summaries = [None] * len(state["materials"])
        relevancy = [0.0] * len(state["materials"])

        def process(i, mat):
            mid = mat["material_id"]
            meta = mat["metadata"]
            # flatten metadata to text
            text = "\n".join(f"{k}: {v}" for k, v in meta.items())
            # build or load summary
            summary_file = os.path.join(self.summaries_path, f"{mid}_summary.txt")
            if os.path.exists(summary_file):
                with open(summary_file) as f:
                    return i, f.read()
            # optional: vectorize & retrieve, but here we just summarize full text
            result = chain.invoke({"metadata": text})
            with open(summary_file, 'w') as f:
                f.write(result)
            return i, result

        with ThreadPoolExecutor(max_workers=min(8, len(state["materials"]))) as exe:
            futures = [exe.submit(process, i, m) for i, m in enumerate(state["materials"])]
            for future in tqdm(futures, desc="Summarizing materials"):
                i, summ = future.result()
                summaries[i] = summ

        return {**state, "summaries": summaries}

    def _aggregate_node(self, state: Dict) -> Dict:
        """Combine all summaries into a single, coherent answer."""
        combined = "\n\n----\n\n".join(
            f"[{i+1}] {m['material_id']}\n\n{summary}"
            for i, (m, summary) in enumerate(zip(state["materials"], state["summaries"]))
        )

        prompt = ChatPromptTemplate.from_template("""
        You are a materials informatics assistant. Below are brief summaries of several materials:

        {summaries}

        Answer the user’s question in context:

        {context}
                """)
        chain = prompt | self.llm | StrOutputParser()
        final = chain.invoke({"summaries": combined, "context": state["context"]})
        return {**state, "final_summary": final}

    def _build_graph(self):
        g = StateGraph(dict)  # using plain dict for state
        g.add_node("fetch", self._fetch_node)
        if self.summarize:
            g.add_node("summarize", self._summarize_node)
            g.add_node("aggregate", self._aggregate_node)
            g.set_entry_point("fetch")
            g.add_edge("fetch", "summarize")
            g.add_edge("summarize", "aggregate")
            g.set_finish_point("aggregate")
        else:
            g.set_entry_point("fetch")
            g.set_finish_point("fetch")
        return g.compile()

    def run(self, mp_query: str, context: str) -> str:
        state = {"query": mp_query, "context": context}
        out = self.graph.invoke(state)
        if self.summarize:
            return out.get("final_summary", "")
        return json.dumps(out.get("materials", []), indent=2)


if __name__ == "__main__":
    agent = MaterialsProjectAgent()
    resp = agent.run(
        mp_query="LiFePO4",
        context="What is its band gap and stability, and any synthesis challenges?"
    )
    print(resp)
