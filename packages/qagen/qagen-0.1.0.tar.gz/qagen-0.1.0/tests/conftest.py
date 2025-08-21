# -*- coding: utf-8 -*-
"""
Pytest configuration and common fixtures
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

@pytest.fixture
def sample_document_content():
    """提供示例文档内容"""
    return """
    人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它企图了解智能的实质，
    并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、
    语言识别、图像识别、自然语言处理和专家系统等。
    
    机器学习是人工智能的一个重要分支，它使计算机能够在没有明确编程的情况下学习和改进。
    深度学习是机器学习的一个子集，使用多层神经网络来模拟人脑的学习过程。
    
    自然语言处理（NLP）是人工智能的另一个重要领域，它使计算机能够理解、解释和生成人类语言。
    近年来，大型语言模型如GPT、BERT等在NLP领域取得了重大突破。
    """

@pytest.fixture
def sample_qa_pairs():
    """提供示例QA pairs"""
    return [
        {
            "question": "什么是人工智能？",
            "answer": "人工智能是计算机科学的一个分支，旨在创建能够模拟人类智能的机器。"
        },
        {
            "question": "机器学习和深度学习的关系是什么？",
            "answer": "机器学习是人工智能的分支，深度学习是机器学习的子集，使用神经网络进行学习。"
        },
        {
            "question": "什么是自然语言处理？",
            "answer": "自然语言处理是使计算机能够理解、解释和生成人类语言的技术。"
        }
    ]

@pytest.fixture
def mock_llm():
    """模拟LLM对象"""
    mock = Mock()
    mock.invoke.return_value = {
        "content": "这是一个模拟的回答",
        "usage": {"total_tokens": 100}
    }
    return mock

@pytest.fixture
def validation_config():
    """提供验证配置"""
    return {
        "similarity_threshold": 0.5,
        "similarity_model": "paraphrase-multilingual-MiniLM-L12-v2",
        "question_min_length": 5,
        "question_max_length": 100,
        "answer_min_length": 10,
        "answer_max_length": 500,
        "keyword_top_n": 10,
        "uniqueness_distance_threshold": 0.1,
        "uniqueness_check_enabled": True
    }

@pytest.fixture
def temp_document_file(sample_document_content):
    """创建临时文档文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(sample_document_content)
        temp_path = f.name
    
    yield temp_path
    
    # 清理临时文件
    os.unlink(temp_path)

@pytest.fixture
def mock_sentence_transformer():
    """模拟SentenceTransformer"""
    mock_model = Mock()
    mock_model.encode.return_value = Mock()  # 返回一个模拟的tensor
    return mock_model

@pytest.fixture
def mock_jieba():
    """模拟jieba分词"""
    # 这里我们不需要真正模拟jieba，因为它是外部库
    # 但在测试中我们可以控制其行为
    return None
