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

# Default validation settings, can be overridden by the user
DEFAULT_VALIDATION_CONFIG = {
    "similarity_model": 'paraphrase-multilingual-MiniLM-L12-v2',
    "similarity_threshold": 0.3,
    "keyword_top_n": 20,
    "question_min_length": 5,
    "question_max_length": 100,
    "answer_min_length": 10,
    "answer_max_length": 500,
    "uniqueness_check_enabled": True,
    "uniqueness_distance_threshold": 0.1
}

def generate_qa_pairs(
    doc_path: str,
    llm_provider: str = 'ollama',
    llm_model: str = 'llama3.1:8b',
    show_chunks: bool = False,
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
    config = validation_config if validation_config is not None else DEFAULT_VALIDATION_CONFIG
    validator = QAPairValidator(config)
    
    # Load full document content for validation context
    doc_content = " ".join([doc.page_content for doc in load_document(doc_path)])
    
    validated_qa_pairs = validator.validate(raw_qa_pairs, doc_content)

    print(f"Generated {len(raw_qa_pairs)} raw QA pairs.")
    print(f"Returning {len(validated_qa_pairs)} validated QA pairs.")

    return validated_qa_pairs
