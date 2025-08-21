#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM Factory for creating instances of language models.
"""

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

class LLMFactory:
    @staticmethod
    def create_llm(provider: str, model: str, **kwargs):
        """
        Creates a language model instance based on the provider.

        Args:
            provider (str): The LLM provider ('ollama' or 'openai').
            model (str): The model name to use.
            **kwargs: Additional arguments for the LLM provider.

        Returns:
            An instance of a LangChain ChatModel.

        Raises:
            ValueError: If the provider is not supported.
        """
        if provider == 'ollama':
            return ChatOllama(model=model, **kwargs)
        elif provider == 'openai':
            api_key = kwargs.get("api_key")
            base_url = kwargs.get("base_url")
            if not api_key:
                raise ValueError("OpenAI API key is required for the 'openai' provider.")
            return ChatOpenAI(model=model, api_key=api_key, base_url=base_url)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
