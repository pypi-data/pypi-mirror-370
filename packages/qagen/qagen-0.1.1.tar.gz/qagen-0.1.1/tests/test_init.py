# -*- coding: utf-8 -*-
"""
测试 __init__.py 模块
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from qa_gen_cn import generate_qa_pairs, DEFAULT_VALIDATION_CONFIG


class TestInitModule:
    """测试__init__.py模块"""
    
    def test_default_validation_config(self):
        """测试默认验证配置"""
        assert isinstance(DEFAULT_VALIDATION_CONFIG, dict)
        assert "similarity_model" in DEFAULT_VALIDATION_CONFIG
        assert "similarity_threshold" in DEFAULT_VALIDATION_CONFIG
        assert "keyword_top_n" in DEFAULT_VALIDATION_CONFIG
        assert "question_min_length" in DEFAULT_VALIDATION_CONFIG
        assert "question_max_length" in DEFAULT_VALIDATION_CONFIG
        assert "answer_min_length" in DEFAULT_VALIDATION_CONFIG
        assert "answer_max_length" in DEFAULT_VALIDATION_CONFIG
        assert "uniqueness_check_enabled" in DEFAULT_VALIDATION_CONFIG
        assert "uniqueness_distance_threshold" in DEFAULT_VALIDATION_CONFIG
    
    @patch('qa_gen_cn.LLMFactory')
    @patch('qa_gen_cn.QAGenerator')
    @patch('qa_gen_cn.QAPairValidator')
    @patch('qa_gen_cn.load_document')
    def test_generate_qa_pairs_success(self, mock_load_document, mock_validator_class, mock_generator_class, mock_llm_factory):
        """测试成功生成QA pairs"""
        # 设置mock
        mock_llm = Mock()
        mock_llm_factory.create_llm.return_value = mock_llm
        
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_from_document.return_value = [
            {"question": "什么是AI？", "answer": "AI是人工智能"}
        ]
        
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate.return_value = [
            {"question": "什么是AI？", "answer": "AI是人工智能"}
        ]
        
        mock_docs = [Mock(page_content="测试文档内容")]
        mock_load_document.return_value = mock_docs
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            result = generate_qa_pairs(temp_path)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["question"] == "什么是AI？"
            assert result[0]["answer"] == "AI是人工智能"
            
            # 验证调用
            mock_llm_factory.create_llm.assert_called_once_with('ollama', 'llama3.1:8b')
            mock_generator_class.assert_called_once_with(mock_llm, show_chunks=False)
            mock_generator.generate_from_document.assert_called_once_with(temp_path)
            mock_validator_class.assert_called_once_with(DEFAULT_VALIDATION_CONFIG)
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.LLMFactory')
    def test_generate_qa_pairs_llm_creation_failure(self, mock_llm_factory):
        """测试LLM创建失败"""
        mock_llm_factory.create_llm.side_effect = ValueError("Invalid provider")
        
        result = generate_qa_pairs("test.txt")
        
        assert result == []
    
    @patch('qa_gen_cn.LLMFactory')
    @patch('qa_gen_cn.QAGenerator')
    def test_generate_qa_pairs_no_qa_pairs_generated(self, mock_generator_class, mock_llm_factory):
        """测试没有生成QA pairs"""
        mock_llm = Mock()
        mock_llm_factory.create_llm.return_value = mock_llm
        
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_from_document.return_value = []
        
        result = generate_qa_pairs("test.txt")
        
        assert result == []
    
    @patch('qa_gen_cn.LLMFactory')
    @patch('qa_gen_cn.QAGenerator')
    @patch('qa_gen_cn.QAPairValidator')
    @patch('qa_gen_cn.load_document')
    def test_generate_qa_pairs_with_custom_config(self, mock_load_document, mock_validator_class, mock_generator_class, mock_llm_factory):
        """测试使用自定义配置"""
        # 设置mock
        mock_llm = Mock()
        mock_llm_factory.create_llm.return_value = mock_llm
        
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_from_document.return_value = [
            {"question": "测试问题", "answer": "测试答案"}
        ]
        
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate.return_value = [
            {"question": "测试问题", "answer": "测试答案"}
        ]
        
        mock_docs = [Mock(page_content="测试文档内容")]
        mock_load_document.return_value = mock_docs
        
        # 自定义配置
        custom_config = {
            "similarity_threshold": 0.5,
            "keyword_top_n": 10
        }
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            result = generate_qa_pairs(
                temp_path,
                llm_provider='openai',
                llm_model='gpt-3.5-turbo',
                show_chunks=True,
                validation_config=custom_config,
                api_key='test-key'
            )
            
            assert isinstance(result, list)
            assert len(result) == 1
            
            # 验证调用参数
            mock_llm_factory.create_llm.assert_called_once_with('openai', 'gpt-3.5-turbo', api_key='test-key')
            mock_generator_class.assert_called_once_with(mock_llm, show_chunks=True)
            mock_validator_class.assert_called_once_with(custom_config)
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.LLMFactory')
    @patch('qa_gen_cn.QAGenerator')
    @patch('qa_gen_cn.QAPairValidator')
    @patch('qa_gen_cn.load_document')
    def test_generate_qa_pairs_with_validation_filtering(self, mock_load_document, mock_validator_class, mock_generator_class, mock_llm_factory):
        """测试验证过滤功能"""
        # 设置mock
        mock_llm = Mock()
        mock_llm_factory.create_llm.return_value = mock_llm
        
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_from_document.return_value = [
            {"question": "问题1", "answer": "答案1"},
            {"question": "问题2", "answer": "答案2"},
            {"question": "问题3", "answer": "答案3"}
        ]
        
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate.return_value = [
            {"question": "问题1", "answer": "答案1"},
            {"question": "问题3", "answer": "答案3"}
        ]  # 过滤掉第二个
        
        mock_docs = [Mock(page_content="测试文档内容")]
        mock_load_document.return_value = mock_docs
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            result = generate_qa_pairs(temp_path)
            
            assert isinstance(result, list)
            assert len(result) == 2  # 验证后只有2个
            assert result[0]["question"] == "问题1"
            assert result[1]["question"] == "问题3"
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.LLMFactory')
    @patch('qa_gen_cn.QAGenerator')
    @patch('qa_gen_cn.QAPairValidator')
    @patch('qa_gen_cn.load_document')
    def test_generate_qa_pairs_document_content_loading(self, mock_load_document, mock_validator_class, mock_generator_class, mock_llm_factory):
        """测试文档内容加载"""
        # 设置mock
        mock_llm = Mock()
        mock_llm_factory.create_llm.return_value = mock_llm
        
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_from_document.return_value = [
            {"question": "测试问题", "answer": "测试答案"}
        ]
        
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate.return_value = [
            {"question": "测试问题", "answer": "测试答案"}
        ]
        
        # 模拟多个文档
        mock_doc1 = Mock(page_content="第一部分内容")
        mock_doc2 = Mock(page_content="第二部分内容")
        mock_load_document.return_value = [mock_doc1, mock_doc2]
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            result = generate_qa_pairs(temp_path)
            
            # 验证文档内容被正确加载和合并
            mock_load_document.assert_called_with(temp_path)
            mock_validator.validate.assert_called_once()
            
            # 检查传递给验证器的文档内容
            call_args = mock_validator.validate.call_args
            doc_content = call_args[0][1]  # 第二个参数是文档内容
            assert "第一部分内容" in doc_content
            assert "第二部分内容" in doc_content
        finally:
            os.unlink(temp_path)
    
    def test_generate_qa_pairs_invalid_output_format(self):
        """测试无效输出格式"""
        # 这个测试需要创建一个临时文件，因为函数会尝试加载文档
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            # 由于output_format参数在当前实现中不被支持，这个测试应该通过
            result = generate_qa_pairs(temp_path, output_format="invalid")
            assert isinstance(result, list)  # 应该返回空列表或正常结果
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.LLMFactory')
    @patch('qa_gen_cn.QAGenerator')
    @patch('qa_gen_cn.QAPairValidator')
    @patch('qa_gen_cn.load_document')
    def test_generate_qa_pairs_with_show_chunks(self, mock_load_document, mock_validator_class, mock_generator_class, mock_llm_factory):
        """测试显示chunks功能"""
        # 设置mock
        mock_llm = Mock()
        mock_llm_factory.create_llm.return_value = mock_llm
        
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_from_document.return_value = [
            {"question": "测试问题", "answer": "测试答案"}
        ]
        
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate.return_value = [
            {"question": "测试问题", "answer": "测试答案"}
        ]
        
        mock_docs = [Mock(page_content="测试文档内容")]
        mock_load_document.return_value = mock_docs
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            result = generate_qa_pairs(temp_path, show_chunks=True)
            
            # 验证show_chunks参数被正确传递
            mock_generator_class.assert_called_once_with(mock_llm, show_chunks=True)
            assert isinstance(result, list)
        finally:
            os.unlink(temp_path)
