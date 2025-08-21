# -*- coding: utf-8 -*-
"""
测试 generator.py 模块
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock
from langchain.docstore.document import Document
from qa_gen_cn.generator import QAGenerator


class TestQAGenerator:
    """测试QAGenerator类"""
    
    def test_init(self, mock_llm):
        """测试初始化"""
        generator = QAGenerator(llm=mock_llm, show_chunks=False)
        
        assert generator.llm == mock_llm
        assert generator.show_chunks is False
        assert hasattr(generator, 'chain')
    
    def test_init_with_show_chunks(self, mock_llm):
        """测试初始化时显示chunks"""
        generator = QAGenerator(llm=mock_llm, show_chunks=True)
        
        assert generator.show_chunks is True
    
    def test_split_documents(self, mock_llm):
        """测试文档分割"""
        generator = QAGenerator(llm=mock_llm)
        
        docs = [
            Document(page_content="这是第一个文档。包含一些内容。"),
            Document(page_content="这是第二个文档。包含更多内容。")
        ]
        
        chunks = generator._split_documents(docs, chunk_size=100, chunk_overlap=10)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, Document) for chunk in chunks)
    
    def test_split_documents_empty(self, mock_llm):
        """测试空文档分割"""
        generator = QAGenerator(llm=mock_llm)
        
        docs = []
        chunks = generator._split_documents(docs, chunk_size=100, chunk_overlap=10)
        
        assert isinstance(chunks, list)
        assert len(chunks) == 0
    
    def test_split_documents_large_chunk_size(self, mock_llm):
        """测试大块大小分割"""
        generator = QAGenerator(llm=mock_llm)
        
        docs = [Document(page_content="这是一个很长的文档。" * 100)]
        
        chunks = generator._split_documents(docs, chunk_size=10000, chunk_overlap=100)
        
        assert len(chunks) == 1  # 应该只有一个块
    
    @patch('qa_gen_cn.generator.load_document')
    @patch('qa_gen_cn.generator.extract_json')
    def test_generate_from_document_success(self, mock_extract_json, mock_load_document, mock_llm):
        """测试成功生成QA pairs"""
        # 设置mock
        mock_docs = [Document(page_content="人工智能是计算机科学的重要分支")]
        mock_load_document.return_value = mock_docs
        
        mock_chain = Mock()
        mock_chain.invoke.return_value = {
            "qa_pairs": [
                {"question": "什么是人工智能？", "answer": "人工智能是计算机科学的分支"}
            ]
        }
        
        generator = QAGenerator(llm=mock_llm)
        generator.chain = mock_chain
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("人工智能是计算机科学的重要分支")
            temp_path = f.name
        
        try:
            result = generator.generate_from_document(temp_path, chunk_size=100, chunk_overlap=10)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["question"] == "什么是人工智能？"
            assert result[0]["answer"] == "人工智能是计算机科学的分支"
            
            mock_load_document.assert_called_once_with(temp_path)
            mock_chain.invoke.assert_called_once()
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.generator.load_document')
    def test_generate_from_document_chain_exception(self, mock_load_document, mock_llm):
        """测试链调用异常时的处理"""
        # 设置mock
        mock_docs = [Document(page_content="测试内容")]
        mock_load_document.return_value = mock_docs
        
        mock_chain = Mock()
        mock_exception = Exception("Chain failed")
        mock_exception.llm_output = '{"qa_pairs": [{"question": "测试问题", "answer": "测试答案"}]}'
        mock_chain.invoke.side_effect = mock_exception
        
        generator = QAGenerator(llm=mock_llm)
        generator.chain = mock_chain
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            with patch('qa_gen_cn.generator.extract_json') as mock_extract:
                mock_extract.return_value = {"qa_pairs": [{"question": "测试问题", "answer": "测试答案"}]}
                
                result = generator.generate_from_document(temp_path, chunk_size=100, chunk_overlap=10)
                
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0]["question"] == "测试问题"
                assert result[0]["answer"] == "测试答案"
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.generator.load_document')
    def test_generate_from_document_invalid_output_format(self, mock_load_document, mock_llm):
        """测试无效输出格式的处理"""
        # 设置mock
        mock_docs = [Document(page_content="测试内容")]
        mock_load_document.return_value = mock_docs
        
        mock_chain = Mock()
        mock_chain.invoke.return_value = {"invalid_key": []}  # 无效格式
        
        generator = QAGenerator(llm=mock_llm)
        generator.chain = mock_chain
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            result = generator.generate_from_document(temp_path, chunk_size=100, chunk_overlap=10)
            
            assert isinstance(result, list)
            assert len(result) == 0  # 应该为空列表
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.generator.load_document')
    def test_generate_from_document_multiple_chunks(self, mock_load_document, mock_llm):
        """测试多个文档块的处理"""
        # 设置mock
        mock_docs = [
            Document(page_content="第一块内容"),
            Document(page_content="第二块内容")
        ]
        mock_load_document.return_value = mock_docs
        
        mock_chain = Mock()
        mock_chain.invoke.side_effect = [
            {"qa_pairs": [{"question": "问题1", "answer": "答案1"}]},
            {"qa_pairs": [{"question": "问题2", "answer": "答案2"}]}
        ]
        
        generator = QAGenerator(llm=mock_llm)
        generator.chain = mock_chain
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            result = generator.generate_from_document(temp_path, chunk_size=100, chunk_overlap=10)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["question"] == "问题1"
            assert result[1]["question"] == "问题2"
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.generator.load_document')
    def test_generate_from_document_file_not_found(self, mock_load_document, mock_llm):
        """测试文件不存在的情况"""
        mock_load_document.side_effect = FileNotFoundError("File not found")
        
        generator = QAGenerator(llm=mock_llm)
        
        with pytest.raises(FileNotFoundError):
            generator.generate_from_document("nonexistent.txt")
    
    def test_generate_from_document_show_chunks(self, mock_llm):
        """测试显示chunks功能"""
        generator = QAGenerator(llm=mock_llm, show_chunks=True)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            with patch('qa_gen_cn.generator.load_document') as mock_load:
                mock_load.return_value = [Document(page_content="测试内容")]
                
                with patch.object(generator, '_split_documents') as mock_split:
                    mock_split.return_value = [Document(page_content="测试内容")]
                    
                    with patch.object(generator, 'chain') as mock_chain:
                        mock_chain.invoke.return_value = {"qa_pairs": []}
                        
                        result = generator.generate_from_document(temp_path)
                        
                        assert isinstance(result, list)
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.generator.load_document')
    def test_generate_from_document_empty_result(self, mock_load_document, mock_llm):
        """测试空结果的处理"""
        mock_docs = [Document(page_content="测试内容")]
        mock_load_document.return_value = mock_docs
        
        mock_chain = Mock()
        mock_chain.invoke.return_value = {"qa_pairs": []}  # 空结果
        
        generator = QAGenerator(llm=mock_llm)
        generator.chain = mock_chain
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            result = generator.generate_from_document(temp_path)
            
            assert isinstance(result, list)
            assert len(result) == 0
        finally:
            os.unlink(temp_path)
