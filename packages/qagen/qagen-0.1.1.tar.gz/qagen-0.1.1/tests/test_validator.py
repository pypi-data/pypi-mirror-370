# -*- coding: utf-8 -*-
"""
测试 validator.py 模块
"""

import pytest
import numpy as np
from unittest.mock import patch, Mock, MagicMock
from qa_gen_cn.validator import QAPairValidator


class TestQAPairValidator:
    """测试QAPairValidator类"""
    
    def test_init(self, validation_config):
        """测试初始化"""
        validator = QAPairValidator(validation_config)
        assert validator.config == validation_config
        assert validator._model is None
    
    def test_extract_keywords_chinese(self, validation_config):
        """测试中文关键词提取"""
        validator = QAPairValidator(validation_config)
        documents = ["人工智能是计算机科学的重要分支", "机器学习是AI的核心技术"]
        
        with patch('qa_gen_cn.validator.jieba.analyse.extract_tags') as mock_extract:
            mock_extract.return_value = [("人工智能", 0.8), ("机器学习", 0.7)]
            keywords = validator._extract_keywords_chinese(documents)
        
        assert isinstance(keywords, list)
        assert len(keywords) == 2  # 两个文档
        assert len(keywords[0]) == 2  # 第一个文档的关键词数量
        assert len(keywords[1]) == 2  # 第二个文档的关键词数量
    
    def test_validate_keywords_success(self, validation_config):
        """测试关键词验证成功"""
        validator = QAPairValidator(validation_config)
        doc_content = "人工智能和机器学习是重要的技术"
        qa_pair = {
            "question": "什么是人工智能？",
            "answer": "人工智能是计算机科学的分支"
        }
        
        with patch.object(validator, '_extract_keywords_chinese') as mock_extract:
            mock_extract.return_value = [[("人工智能", 0.8), ("机器学习", 0.7)]]
            
            with patch('qa_gen_cn.validator.jieba.lcut') as mock_lcut:
                mock_lcut.side_effect = [
                    ["什么", "是", "人工智能"],  # question分词
                    ["人工智能", "是", "计算机科学", "的", "分支"]  # answer分词
                ]
                
                result = validator._validate_keywords(doc_content, qa_pair)
        
        # 修复：检查返回值的结构
        assert result is not None
        assert "question" in result
        assert "answer" in result
        # 检查返回的是集合类型
        assert isinstance(result["question"], set)
        assert isinstance(result["answer"], set)
        assert "人工智能" in result["question"]
    
    def test_validate_keywords_no_match(self, validation_config):
        """测试关键词验证失败"""
        validator = QAPairValidator(validation_config)
        doc_content = "人工智能和机器学习是重要的技术"
        qa_pair = {
            "question": "什么是其他技术？",
            "answer": "其他技术不是AI相关"
        }
        
        with patch.object(validator, '_extract_keywords_chinese') as mock_extract:
            mock_extract.return_value = [[("人工智能", 0.8), ("机器学习", 0.7)]]
            
            with patch('qa_gen_cn.validator.jieba.lcut') as mock_lcut:
                mock_lcut.side_effect = [
                    ["什么", "是", "其他", "技术"],  # question分词
                    ["其他", "技术", "不是", "AI", "相关"]  # answer分词
                ]
                
                result = validator._validate_keywords(doc_content, qa_pair)
        
        assert result is None
    
    def test_validate_length_success(self, validation_config):
        """测试长度验证成功"""
        validator = QAPairValidator(validation_config)
        qa_pair = {
            "question": "什么是人工智能？",
            "answer": "人工智能是计算机科学的一个分支，旨在创建能够模拟人类智能的机器。"
        }
        
        result = validator._validate_length(qa_pair)
        
        assert result is not None
        assert result["question"] == qa_pair["question"]
        assert result["answer"] == qa_pair["answer"]
    
    def test_validate_length_question_too_short(self, validation_config):
        """测试问题太短"""
        validator = QAPairValidator(validation_config)
        qa_pair = {
            "question": "AI?",
            "answer": "人工智能是计算机科学的一个分支。"
        }
        
        result = validator._validate_length(qa_pair)
        
        assert result is None
    
    def test_validate_length_question_too_long(self, validation_config):
        """测试问题太长"""
        validator = QAPairValidator(validation_config)
        qa_pair = {
            "question": "什么是人工智能？" * 20,  # 重复20次使其超过100字符
            "answer": "人工智能是计算机科学的一个分支。"
        }
        
        result = validator._validate_length(qa_pair)
        
        assert result is None
    
    def test_validate_length_answer_too_short(self, validation_config):
        """测试答案太短"""
        validator = QAPairValidator(validation_config)
        qa_pair = {
            "question": "什么是人工智能？",
            "answer": "AI技术"
        }
        
        result = validator._validate_length(qa_pair)
        
        assert result is None
    
    def test_validate_length_answer_too_long(self, validation_config):
        """测试答案太长"""
        validator = QAPairValidator(validation_config)
        qa_pair = {
            "question": "什么是人工智能？",
            "answer": "人工智能是计算机科学的一个分支。" * 50  # 重复50次使其超过500字符
        }
        
        result = validator._validate_length(qa_pair)
        
        assert result is None
    
    @patch('qa_gen_cn.validator.SentenceTransformer')
    @patch('qa_gen_cn.validator.util.cos_sim')
    def test_validate_similarity_success(self, mock_cos_sim, mock_sentence_transformer, validation_config):
        """测试相似度验证成功"""
        validator = QAPairValidator(validation_config)
        doc_content = "人工智能是计算机科学的重要分支"
        qa_pair = {
            "question": "什么是人工智能？",
            "answer": "人工智能是计算机科学的分支"
        }
        
        # 设置mock
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        mock_model.encode.return_value = Mock()  # 模拟tensor
        
        mock_cos_sim.return_value.item.side_effect = [0.8, 0.7]  # 高于阈值
        
        result = validator._validate_similarity(doc_content, qa_pair)
        
        assert result is not None
        assert result["question"] == qa_pair["question"]
        assert result["answer"] == qa_pair["answer"]
    
    @patch('qa_gen_cn.validator.SentenceTransformer')
    @patch('qa_gen_cn.validator.util.cos_sim')
    def test_validate_similarity_failure(self, mock_cos_sim, mock_sentence_transformer, validation_config):
        """测试相似度验证失败"""
        validator = QAPairValidator(validation_config)
        doc_content = "人工智能是计算机科学的重要分支"
        qa_pair = {
            "question": "什么是其他技术？",
            "answer": "其他技术不是AI相关"
        }
        
        # 设置mock
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        mock_model.encode.return_value = Mock()  # 模拟tensor
        
        mock_cos_sim.return_value.item.side_effect = [0.3, 0.2]  # 低于阈值
        
        result = validator._validate_similarity(doc_content, qa_pair)
        
        assert result is None
    
    def test_validate_duplicates(self, validation_config):
        """测试重复检测"""
        validator = QAPairValidator(validation_config)
        qa_pairs = [
            {"question": "什么是AI？", "answer": "AI是人工智能"},
            {"question": "什么是人工智能？", "answer": "人工智能是AI"},
            {"question": "什么是机器学习？", "answer": "机器学习是AI的分支"}
        ]
        
        # 修复：使用正确的属性名
        with patch.object(validator, '_model') as mock_model:
            mock_model.encode.return_value = Mock()
            
            with patch('qa_gen_cn.validator.util.cos_sim') as mock_cos_sim:
                # 模拟相似度矩阵：前两个问题相似，第三个不同
                mock_cos_sim.return_value.cpu.return_value.numpy.return_value = np.array([
                    [1.0, 0.9, 0.3],
                    [0.9, 1.0, 0.3],
                    [0.3, 0.3, 1.0]
                ])
                
                with patch('qa_gen_cn.validator.AgglomerativeClustering') as mock_clustering:
                    mock_clustering_instance = Mock()
                    mock_clustering_instance.labels_ = [0, 0, 1]  # 前两个聚类为0，第三个为1
                    mock_clustering.return_value = mock_clustering_instance
                    
                    result = validator._validate_duplicates(qa_pairs)
        
        # 应该保留第一个和第三个（不同聚类）
        assert len(result) == 2
        assert result[0]["question"] == "什么是AI？"
        assert result[1]["question"] == "什么是机器学习？"
    
    def test_validate_empty_qa_pairs(self, validation_config):
        """测试空QA pairs列表"""
        validator = QAPairValidator(validation_config)
        result = validator.validate([], "some content")
        
        assert result == []
    
    def test_validate_similarity_priority(self, validation_config):
        """测试相似度验证优先级"""
        validator = QAPairValidator(validation_config)
        qa_pairs = [{"question": "test", "answer": "test"}]
        doc_content = "test content"
        
        with patch.object(validator, '_validate_similarity') as mock_similarity:
            mock_similarity.return_value = {"question": "test", "answer": "test"}
            
            result = validator.validate(qa_pairs, doc_content)
        
        mock_similarity.assert_called_once()
        assert len(result) == 1
    
    def test_validate_length_priority(self, validation_config):
        """测试长度验证优先级"""
        # 移除相似度配置，只保留长度配置
        length_config = {
            "question_min_length": 5,
            "question_max_length": 100,
            "answer_min_length": 10,
            "answer_max_length": 500
        }
        
        validator = QAPairValidator(length_config)
        qa_pairs = [{"question": "test question", "answer": "test answer with sufficient length"}]
        doc_content = "test content"
        
        with patch.object(validator, '_validate_length') as mock_length:
            mock_length.return_value = {"question": "test question", "answer": "test answer"}
            
            result = validator.validate(qa_pairs, doc_content)
        
        mock_length.assert_called_once()
        assert len(result) == 1
    
    def test_validate_keywords_priority(self, validation_config):
        """测试关键词验证优先级"""
        # 只保留关键词配置
        keyword_config = {"keyword_top_n": 10}
        
        validator = QAPairValidator(keyword_config)
        qa_pairs = [{"question": "test", "answer": "test"}]
        doc_content = "test content"
        
        with patch.object(validator, '_validate_keywords') as mock_keywords:
            mock_keywords.return_value = {"question": {"test"}, "answer": {"test"}}
            
            result = validator.validate(qa_pairs, doc_content)
        
        mock_keywords.assert_called_once()
        assert len(result) == 1
    
    def test_validate_uniqueness_priority(self, validation_config):
        """测试唯一性验证优先级"""
        # 只保留唯一性配置
        uniqueness_config = {
            "uniqueness_distance_threshold": 0.1,
            "uniqueness_check_enabled": True
        }
        
        validator = QAPairValidator(uniqueness_config)
        qa_pairs = [{"question": "test", "answer": "test"}]
        doc_content = "test content"
        
        with patch.object(validator, '_validate_duplicates') as mock_duplicates:
            mock_duplicates.return_value = [{"question": "test", "answer": "test"}]
            
            result = validator.validate(qa_pairs, doc_content)
        
        mock_duplicates.assert_called_once()
        assert len(result) == 1
    
    def test_validate_no_config(self):
        """测试没有配置时返回原始QA pairs"""
        validator = QAPairValidator({})
        qa_pairs = [{"question": "test", "answer": "test"}]
        doc_content = "test content"
        
        result = validator.validate(qa_pairs, doc_content)
        
        assert result == qa_pairs
