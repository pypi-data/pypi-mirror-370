#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QA Pair Validator to filter and ensure the quality of generated QA pairs.
"""

import jieba
import jieba.analyse
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import AgglomerativeClustering
from typing import List, Dict, Any, Tuple, Set

class QAPairValidator:
    """
    Validates a list of QA pairs based on a set of configurable rules.
    Validation 1,2,3,4 validation是互斥的，只能选择一个验证
    验证优先级：1>2>3>4，在self.config中配置了：
        1 similarity_threshold和similarity_model，后面其他验证的配置可以不配置，如果配置了也不起作用。
        2 question_min_length和question_max_length，answer_min_length和answer_max_length，后面其他验证的配置可以不配置，如果配置了也不起作用。
        3 keyword_top_n，后面其他验证的配置可以不配置，如果配置了也不起作用。
        4 similarity_model、uniqueness_distance_threshold和uniqueness_check_enabled，其他验证的配置可以不配置，如果配置了也不起作用。
    qa_pair: A dictionary containing the QA pair.
            - similarity_threshold: The threshold for the similarity between the question and the answer.recommended value  is 0.5.
            - similarity_model: The model name for the similarity calculation. recommended value is  'paraphrase-multilingual-MiniLM-L12-v2'.
            - question_min_length: The minimum length of the question. recommended value is 5.
            - question_max_length: The maximum length of the question. recommended value is100.
            - answer_min_length: The minimum length of the answer. recommended value is 10.
            - answer_max_length: The maximum length of the answer. recommended value is500.
            - uniqueness_distance_threshold: The threshold for the distance between the questions.recommended value is 0.1.
            - keyword_top_n: The number of keywords to extract from the document. recommended value is 10.
            - uniqueness_check_enabled: A boolean indicating whether to check for uniqueness. recommended value is True.
    
    """
    def __init__(self, validation_config: Dict[str, Any]):
        """
        Initializes the validator with a configuration.

        Args:
            validation_config: A dictionary containing settings for each validation step,
                               e.g., thresholds, min/max lengths.
        """
        self.config = validation_config
        # Lazy load model only when needed
        self._model = None


    # Validation 1: Semantic Similarity
    def _validate_similarity(self, doc_content: str, qa_pair: Dict[str, str]) -> bool:
        """
        Args:
            doc_content: The original document content for context-based validation.
            qa_pair: A dictionary containing the QA pair.
            - similarity_threshold: The threshold for the similarity between the question and the answer.recommended value is 0.5.
            - similarity_model: The model name for the similarity calculation. recommended value is is 'paraphrase-multilingual-MiniLM-L12-v2'.
        Returns:
            A boolean indicating whether the QA pair is valid.
        """
        # if 'similarity_threshold' in qa_pair:
        threshold = self.config['similarity_threshold']
        # else:
        #     threshold = self.config.get("similarity_threshold", 0.5)
        # if 'similarity_model' in self.config:
        model_name = self.config['similarity_model']
        # else:
        # model_name = self.config.get("similarity_model", 'paraphrase-multilingual-MiniLM-L12-v2')
        self._model = SentenceTransformer(model_name)
        doc_embedding = self._model.encode(doc_content, convert_to_tensor=True)
        q_embedding = self._model.encode(qa_pair['question'], convert_to_tensor=True)
        a_embedding = self._model.encode(qa_pair['answer'], convert_to_tensor=True)

        q_sim = util.cos_sim(doc_embedding, q_embedding).item()
        a_sim = util.cos_sim(doc_embedding, a_embedding).item()

        if q_sim > threshold and a_sim > threshold:
            return {
            'question': qa_pair['question'],
            'answer': qa_pair['answer']}
        # else:
        #     return {
        #         'question_matched_keywords': qa_pair['question'],
        #         'answer_matched_keywords': qa_pair['answer'],
        #         'is_valid': False}
    # Validation 2: Keyword Match
    def _extract_keywords_chinese(self,documents)->list:
       
        """
        使用 jieba 提取中文文档中的关键词
        Args:
            documents: 文档列表（每个文档是一个字符串）
            top_n: 返回前 N 个关键词
        Returns:
            关键词列表
        """
        keywords = []
        # if 'keyword_top_n' in self.config:
        top_n_keywords = self.config['keyword_top_n']
        # else:
        #     top_n_keywords = self.config.get("keyword_top_n", 10)
        
        for doc in documents:
            # 使用 jieba.analyse.extract_tags 提取关键词
            # 使用 TF-IDF 算法，返回 (word, weight) 元组
            doc_keywords = jieba.analyse.extract_tags(doc, topK=top_n_keywords, withWeight=True)
            keywords.extend(doc_keywords)
        
        return keywords

    def _validate_keywords(self, doc_content: str, qa_pair: Dict[str, str]) -> bool:
        """
        检查中文 QA 对是否包含关键词
        Args:
            doc_content: The original document content for context-based validation.
            qa_pair: A dictionary containing the QA pair.
            - question: 问题字符串
            - answer: 答案字符串
        Returns:
            包含的关键词列表和是否有效
        """
        keywords = self._extract_keywords_chinese([doc_content])
        keyword_set = {word for word, _ in keywords}
    
        # 对问题和答案进行分词
        question_words = set(jieba.lcut(qa_pair['question']))
        answer_words = set(jieba.lcut(qa_pair['answer']))
        
        # 检查问题和答案中包含的关键词
        question_matched = question_words.intersection(keyword_set)
        answer_matched = answer_words.intersection(keyword_set)
        
        # 判断有效性：问题和答案都必须包含至少一个关键词
        if  len(question_matched) > 0 and len(answer_matched) > 0:
            return {
                'question': question_matched,
                'answer': answer_matched
            }
        # else: 
        #      return {
        #         'question_matched_keywords': question_matched,
        #         'answer_matched_keywords': answer_matched,
        #         'is_valid': False
        #     }
    # Validation 3: Length Checks
    def _validate_length(self, qa_pair: Dict[str, str]) -> bool:
        """

        Args:
            qa_pair: A dictionary containing the QA pair.
            - question_min_length: The minimum length of the question. if not in qa_pair, default is 5.
            - question_max_length: The maximum length of the question. if not in qa_pair, default is 100.
            - answer_min_length: The minimum length of the answer. if not in qa_pair, default is 10.
            - answer_max_length: The maximum length of the answer. if not in qa_pair, default is 500.

        Returns:
            A boolean indicating whether the QA pair is valid.
        """
        q_len = len(qa_pair['question'])
        a_len = len(qa_pair['answer'])
        q_min = self.config['question_min_length']
        q_max = self.config['question_max_length']
        a_min = self.config['answer_min_length']
        a_max = self.config['answer_max_length']
        
        if (q_min <= q_len <= q_max) and (a_min <= a_len <= a_max):
            return {
                'question': qa_pair['question'],
                'answer': qa_pair['answer']}
       
    # Validation 4: Uniqueness/Duplication Check
    def _validate_duplicates(self, qa_pairs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Args:
            qa_pairs: The list of generated QA pairs.
            - uniqueness_distance_threshold: The threshold for the distance between the questions. if not in qa_pair, default is 0.1.
        Returns:
            A list of validated and filtered QA pairs.
        """
        threshold = self.config['uniqueness_distance_threshold']
        model_name = self.config['similarity_model']
        # else:
        # model_name = self.config.get("similarity_model", 'paraphrase-multilingual-MiniLM-L12-v2')
        self._model = SentenceTransformer(model_name)
        questions = [p['question'] for p in qa_pairs]
        embeddings = self._model.encode(questions, convert_to_tensor=True, normalize_embeddings=True)
        
        distance_matrix = 1 - util.cos_sim(embeddings, embeddings).cpu().numpy()
        distance_matrix = np.clip(distance_matrix, 0, None)

        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=threshold,
            metric='precomputed',
            linkage='average'
        ).fit(distance_matrix)

        # Keep only the first item from each cluster
        unique_indices = []
        seen_labels = set()
        for i, label in enumerate(clustering.labels_):
            if label not in seen_labels:
                unique_indices.append(i)
                seen_labels.add(label)
        
        return [qa_pairs[i] for i in sorted(unique_indices)]
    def validate(self, qa_pairs: List[Dict[str, str]], doc_content: str) -> List[Dict[str, str]]:
        """
        Applies a pipeline of validations to filter QA pairs.

        Args:
            qa_pairs: The list of generated QA pairs.
            doc_content: The original document content for context-based validation.

        Returns:
            A list of validated and filtered QA pairs.
        """
        if not qa_pairs:
            return []

        # Validation 1,2,3,4 validation是互斥的，只能选择一个验证
        # 验证优先级：1>2>3>4，在self.config中配置了：
        #       1 similarity_threshold和similarity_model，后面其他验证的配置可以不配置，如果配置了也不起作用。
        #       2 question_min_length和question_max_length，answer_min_length和answer_max_length，后面其他验证的配置可以不配置，如果配置了也不起作用。
        #       3 keyword_top_n，后面其他验证的配置可以不配置，如果配置了也不起作用。
        #       4 uniqueness_distance_threshold和uniqueness_check_enabled，其他验证的配置可以不配置，如果配置了也不起作用。

        qa_pairs_result = []
        if 'similarity_threshold' in self.config and 'similarity_model' in self.config:
            for pair in qa_pairs:
                qa_pairs_result.append(self._validate_similarity(doc_content, pair))
        elif 'question_min_length' in self.config and 'question_max_length' in self.config and 'answer_min_length' in self.config and 'answer_max_length' in self.config:
            for pair in qa_pairs:
                qa_pairs_result.append(self._validate_length(pair))
        elif 'keyword_top_n' in self.config:
            for pair in qa_pairs:
                qa_pairs_result.append(self._validate_keywords(doc_content, pair))
        elif 'uniqueness_distance_threshold' in self.config and 'uniqueness_check_enabled' in self.config:
            qa_pairs_result=self._validate_duplicates(qa_pairs)
        else:
            qa_pairs_result=qa_pairs
            

        return qa_pairs_result

    
