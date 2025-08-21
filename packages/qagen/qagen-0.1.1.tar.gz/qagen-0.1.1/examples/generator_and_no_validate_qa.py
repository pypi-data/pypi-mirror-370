#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demonstration script for the qa_gen_cn package.
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qa_gen_cn import generate_qa_pairs

def main():
    """
    Main function to run the demo.
    """
    # The document is in the parent directory of the 'qa_gen_cn' project folder
    # Adjust the path as needed based on your execution context.
    doc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '1.md'))

    if not os.path.exists(doc_path):
        print(f"Error: Document not found at {doc_path}")
        # As a fallback, create a dummy file for demonstration purposes
        print("Creating a dummy '1.md' file for the demo.")
        dummy_content = """
        大模型（Large Language Model，LLM）是人工智能领域的一项革命性技术。
        它们通过在海量文本数据上进行训练，学习语言的复杂模式和知识。
        目前，最著名的LLM包括OpenAI的GPT系列、Google的Gemini以及Meta的Llama系列。
        这些模型能够执行多种任务，如文本生成、摘要、翻译和问答，极大地推动了人机交互的发展。
        """
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(dummy_content)
        print(f"Dummy file created at {doc_path}")

    print(f"--- Starting QA Pair Generation for: {doc_path} ---")

    # --- Configuration ---
    # Set to True to see the document chunks printed to the console
    show_chunks_flag = True

    # Using the local Ollama model
    # Ensure Ollama is running and the model is pulled, e.g., `ollama pull llama3.1:8b`
    llm_provider = 'ollama'
    llm_model = 'llama3.1:8b'

    # --- Generate QA Pairs ---
    try:
        qa_pairs = generate_qa_pairs(
            doc_path=doc_path,
            llm_provider=llm_provider,
            llm_model=llm_model,
            show_chunks=show_chunks_flag
        )

        # --- Output Results ---
        if qa_pairs:
            print("\n--- Generated QA Pairs (JSON Output) ---")
            # Output as a JSON string
            json_output = json.dumps(qa_pairs, ensure_ascii=False, indent=2)
            print(json_output)
            
            # Optionally, save to a file
            output_file = 'qa_pairs_output.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"\nResults saved to {output_file}")
        else:
            print("\n--- No valid QA pairs were generated. ---")

    except Exception as e:
        print(f"\nAn error occurred during QA pair generation: {e}")
        print("Please ensure that the Ollama service is running and the model is available.")

if __name__ == "__main__":
    main()
