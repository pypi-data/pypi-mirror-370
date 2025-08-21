#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility functions for the qa_gen_cn package.
"""

from langchain_community.document_loaders import TextLoader
from langchain.docstore.document import Document
from typing import List

def load_document(doc_path: str) -> List[Document]:
    """
    Loads a document from the given path using TextLoader.

    Args:
        doc_path (str): The path to the document file.

    Returns:
        A list containing the loaded Document.
    """
    loader = TextLoader(doc_path, encoding='utf-8')
    return loader.load()
