# -*- coding: utf-8 -*-
"""
测试 llm_factory.py 模块
"""

import pytest
from unittest.mock import patch, Mock
from qa_gen_cn.llm_factory import LLMFactory


class TestLLMFactory:
    """测试LLM工厂类"""
    
    @patch('qa_gen_cn.llm_factory.ChatOllama')
    def test_create_ollama_llm(self, mock_chat_ollama):
        """测试创建Ollama LLM"""
        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance
        
        llm = LLMFactory.create_llm(provider='ollama', model='llama3.1:8b')
        
        mock_chat_ollama.assert_called_once_with(model='llama3.1:8b')
        assert llm == mock_instance
    
    @patch('qa_gen_cn.llm_factory.ChatOllama')
    def test_create_ollama_llm_with_kwargs(self, mock_chat_ollama):
        """测试创建Ollama LLM并传递额外参数"""
        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance
        
        llm = LLMFactory.create_llm(
            provider='ollama', 
            model='qwen3:8b',
            temperature=0.7,
            top_p=0.9
        )
        
        mock_chat_ollama.assert_called_once_with(
            model='qwen3:8b',
            temperature=0.7,
            top_p=0.9
        )
        assert llm == mock_instance
    
    @patch('qa_gen_cn.llm_factory.ChatOpenAI')
    def test_create_openai_llm(self, mock_chat_openai):
        """测试创建OpenAI LLM"""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        llm = LLMFactory.create_llm(
            provider='openai',
            model='gpt-3.5-turbo',
            api_key='test-api-key'
        )
        
        mock_chat_openai.assert_called_once_with(
            model='gpt-3.5-turbo',
            api_key='test-api-key',
            base_url=None
        )
        assert llm == mock_instance
    
    @patch('qa_gen_cn.llm_factory.ChatOpenAI')
    def test_create_openai_llm_with_base_url(self, mock_chat_openai):
        """测试创建OpenAI LLM并指定base_url"""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        llm = LLMFactory.create_llm(
            provider='openai',
            model='gpt-4',
            api_key='test-api-key',
            base_url='https://api.openai.com/v1'
        )
        
        mock_chat_openai.assert_called_once_with(
            model='gpt-4',
            api_key='test-api-key',
            base_url='https://api.openai.com/v1'
        )
        assert llm == mock_instance
    
    def test_create_openai_llm_missing_api_key(self):
        """测试创建OpenAI LLM时缺少API key"""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            LLMFactory.create_llm(provider='openai', model='gpt-3.5-turbo')
    
    def test_create_unsupported_provider(self):
        """测试创建不支持的provider"""
        with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
            LLMFactory.create_llm(provider='unsupported', model='test-model')
    
    def test_create_llm_invalid_provider_type(self):
        """测试传入无效的provider类型"""
        with pytest.raises(ValueError, match="Unsupported LLM provider: 123"):
            LLMFactory.create_llm(provider=123, model='test-model')
    
    def test_create_llm_empty_provider(self):
        """测试传入空的provider"""
        with pytest.raises(ValueError, match="Unsupported LLM provider: "):
            LLMFactory.create_llm(provider='', model='test-model')
