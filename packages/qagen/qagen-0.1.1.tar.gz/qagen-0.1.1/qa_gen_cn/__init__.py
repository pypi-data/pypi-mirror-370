#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for the qa_gen_cn package.
"""

import json
from typing import List, Dict, Any, Optional

from .llm_factory import LLMFactory
from .generator import QAGenerator
from .validator import QAPairValidator
from .utils import load_document


def generate_qa_pairs(
    doc_path: str,
    llm_provider: str ,
    llm_model: str ,
    show_chunks: bool ,
    validation_config: Optional[Dict[str, Any]] = None,
    output_format: str = 'json',
    **llm_kwargs: Any
) -> List[Dict[str, str]]:
    """
    The main function to generate high-quality QA pairs from a document.

    Args:
        doc_path (str): Path to the input document.
        llm_provider (str): The LLM provider ('ollama' or 'openai').
        llm_model (str): The name of the model to use.
        show_chunks (bool): If True, prints the document chunks before generation.
        validation_config (Optional[Dict]): Configuration for the validation process.
                                           If None, uses default settings.
        output_format (str): The desired output format ('json' or 'list').
        **llm_kwargs: Additional keyword arguments for the LLM provider
                      (e.g., api_key for 'openai').

    Returns:
        A list of validated QA pairs.
    """
    # 1. Create LLM instance
    try:
        llm = LLMFactory.create_llm(llm_provider, llm_model, **llm_kwargs)
    except ValueError as e:
        print(f"Error creating LLM: {e}")
        return []

    # 2. Generate raw QA pairs
    generator = QAGenerator(llm, show_chunks=show_chunks)
    raw_qa_pairs = generator.generate_from_document(doc_path)

    if not raw_qa_pairs:
        print("No QA pairs were generated.")
        return []

    # 3. Validate the QA pairs
    # Use default config if none is provided
    if validation_config is not None:
        config = validation_config
        validator = QAPairValidator(config)
        doc_content = " ".join([doc.page_content for doc in load_document(doc_path)])
        validated_qa_pairs = validator.validate(raw_qa_pairs, doc_content)
    else:
        validated_qa_pairs=raw_qa_pairs



    return validated_qa_pairs
