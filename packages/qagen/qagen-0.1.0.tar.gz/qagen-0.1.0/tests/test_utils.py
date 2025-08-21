# -*- coding: utf-8 -*-
"""
测试 utils.py 模块
"""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock
from qa_gen_cn.utils import load_document


class TestLoadDocument:
    """测试文档加载功能"""
    
    def test_load_document_success(self, temp_document_file):
        """测试成功加载文档"""
        docs = load_document(temp_document_file)
        
        assert isinstance(docs, list)
        assert len(docs) > 0
        assert hasattr(docs[0], 'page_content')
        assert "人工智能" in docs[0].page_content
    
    def test_load_document_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(RuntimeError, match="Error loading nonexistent_file.txt"):
            load_document("nonexistent_file.txt")
    
    def test_load_document_empty_file(self):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        
        try:
            docs = load_document(temp_path)
            assert isinstance(docs, list)
            assert len(docs) > 0
            assert docs[0].page_content == ""
        finally:
            os.unlink(temp_path)
    
    def test_load_document_encoding_utf8(self):
        """测试UTF-8编码的文档"""
        content = "测试中文内容：人工智能、机器学习、深度学习"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            docs = load_document(temp_path)
            assert isinstance(docs, list)
            assert len(docs) > 0
            assert "人工智能" in docs[0].page_content
            assert "机器学习" in docs[0].page_content
        finally:
            os.unlink(temp_path)
    
    @patch('qa_gen_cn.utils.TextLoader')
    def test_load_document_with_mock_loader(self, mock_loader):
        """使用mock测试文档加载"""
        # 设置mock
        mock_doc = Mock()
        mock_doc.page_content = "模拟的文档内容"
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        # 测试
        docs = load_document("test.txt")
        
        # 验证
        mock_loader.assert_called_once_with("test.txt", encoding='utf-8')
        mock_loader_instance.load.assert_called_once()
        assert len(docs) == 1
        assert docs[0].page_content == "模拟的文档内容"
