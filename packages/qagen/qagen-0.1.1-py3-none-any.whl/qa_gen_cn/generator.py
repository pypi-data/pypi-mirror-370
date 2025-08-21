#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QA Pair Generator using a robust LCEL chain with JSON output parsing.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict, Any
from .super_json import SuperJSON,extract_json
from .utils import load_document

# A prompt that is very explicit about the desired JSON output format.
# QWEN_TEMPLATE=""""""
PROMPT_TEMPLATE = """
You are an expert assistant tasked with generating question-and-answer pairs from a given text.

Based on the following text, please generate a list of QA pairs.

The output should be a single, valid JSON object containing a single key "qa_pairs", which holds a list of dictionaries. Each dictionary must have a "question" key and an "answer" key.

Do NOT output any other text, explanations, or markdown formatting before or after the JSON object.

Here is the text:
--- TEXT ---
{text}
--- END TEXT ---

JSON_OUTPUT:
"""

class QAGenerator:
    """
    Generates QA pairs from a document using a robust LCEL chain.
    """
    def __init__(self, llm: Any, show_chunks: bool = False):
        """
        Initializes the QAGenerator.

        Args:
            llm: The language model instance from LLMFactory.
            show_chunks (bool): If True, prints the document chunks.
        """
        self.llm = llm
        self.show_chunks = show_chunks

        # Define the generation chain using LangChain Expression Language (LCEL)
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        parser = JsonOutputParser()
        self.chain = prompt | self.llm | parser

    def _split_documents(self, docs: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
        """
        Splits the documents into smaller chunks.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？"], # More robust separators for Chinese
            keep_separator=True
        )
        return text_splitter.split_documents(docs)

    def generate_from_document(
        self, 
        doc_path: str, 
        chunk_size: int = 4000, 
        chunk_overlap: int = 200
    ) -> List[Dict[str, str]]:
        """
        Loads a document, splits it, and generates QA pairs using the robust chain.

        Args:
            doc_path (str): The path to the document.
            chunk_size (int): The size of each text chunk.
            chunk_overlap (int): The overlap between text chunks.

        Returns:
            A list of generated QA pairs.
        """

        docs = load_document(doc_path)
        chunks = self._split_documents(docs, chunk_size, chunk_overlap)

        if self.show_chunks:
            print("--- Document Chunks ---")
            for i, chunk in enumerate(chunks):
                print(f"Chunk {i+1}: {chunk.page_content.strip()}\n")
            print("-----------------------\n")
        
        qa_pairs = []
        for doc in chunks:
            try:
                # The chain is invoked with the document content
                # 如果langchain的JsonOutputParser没有成功，就会报错
                result = self.chain.invoke({"text": doc.page_content})
                
                print(f"result:{result}")
                if isinstance(result, dict) and "qa_pairs" in result and isinstance(result["qa_pairs"], list):
                    qa_pairs.extend(result["qa_pairs"])
                else:
                    print(f"Warning: Unexpected output format from LLM for a chunk. Skipping.")

            except Exception as e:
                # 处理一些无法返回json的大模型的异常
                # exception会截获不能反悔json的大模型的response，存在e.llm_output里面，因此通过superjon处理一下当前的json
                # result = e.llm_output
                try:
                    result = e.llm_output
                    result_dict =extract_json(result)
                    # print(f"result_dict:{result_dict}")
                    if isinstance(result_dict, dict) and "qa_pairs" in result_dict and isinstance(result_dict["qa_pairs"], list):
                        qa_pairs.extend(result_dict["qa_pairs"])
                except Exception as e:
                    continue 
                continue
            print(f"qa_pairs:{qa_pairs}")
        return qa_pairs