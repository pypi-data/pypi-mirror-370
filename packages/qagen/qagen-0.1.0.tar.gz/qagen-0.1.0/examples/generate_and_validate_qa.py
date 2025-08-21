#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于1.txt文件生成QA pairs并进行验证的完整脚本
"""

import sys
import os
import json
from typing import List, Dict, Any

# 添加项目根目录到Python路径（examples 的上一级）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qa_gen_cn.generator import QAGenerator
from qa_gen_cn.llm_factory import LLMFactory
from qa_gen_cn.validator import QAPairValidator
from qa_gen_cn.utils import load_document

def load_document_content(doc_path: str) -> str:
    """加载文档内容"""
    docs = load_document(doc_path)
    return "\n".join([doc.page_content for doc in docs])

def generate_qa_pairs_with_validation(
    doc_path: str,
    llm_provider: str,
    llm_model: str ,
    show_chunks: bool ,
    chunk_size: int,
    chunk_overlap: int,
    validation_config: dict
) -> Dict[str, Any]:
    """
    生成QA pairs并进行验证
    
    Args:
        doc_path: 文档路径
        llm_provider: LLM provider('ollama' 或 'openai')
        llm_model: 模型名称
        show_chunks: 是否显示文档块
        chunk_size: 文档块大小
        chunk_overlap: 文档块重叠大小
    
    Returns:
        包含生成结果和验证结果的字典
    """
    
    print(f"=== 开始处理文档: {doc_path} ===")
    
    # 1. 初始化LLM
    print("1. 初始化语言模型...")
    try:
        llm = LLMFactory.create_llm(provider=llm_provider, model=llm_model)
        print(f"   ✓ 成功初始化 {llm_provider} 模型: {llm_model}")
    except Exception as e:
        print(f"   ✗ 初始化LLM失败: {e}")
        return {"error": f"LLM初始化失败: {e}"}
    
    # 2. 初始化QA生成器
    print("2. 初始化QA生成器...")
    generator = QAGenerator(llm=llm, show_chunks=show_chunks)
    print("   ✓ QA生成器初始化完成")
    
    # 3. 生成QA pairs
    print("3. 生成QA pairs...")
    # try:
    qa_pairs = generator.generate_from_document(
        doc_path=doc_path,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    # 生成后进行一次结构清洗，确保每项都包含 question/answer
    qa_pairs = [
        p for p in qa_pairs
        if isinstance(p, dict) and ('question' in p) and ('answer' in p)
    ]
    print(f"   ✓ 成功生成 {len(qa_pairs)} 个QA pairs")
    
    # 4. 加载原始文档内容用于验证
    print("4. 加载原始文档内容...")
    try:
        doc_content = load_document_content(doc_path)
        print(f"   ✓ 文档内容加载完成，长度: {len(doc_content)} 字符")
    except Exception as e:
        print(f"   ✗ 加载文档内容失败: {e}")
        return {"error": f"文档内容加载失败: {e}"}
    
    # 5. 配置验证器
    print("5. 配置验证器...")
    validation_config = validation_config
    
    validator = QAPairValidator(validation_config)
    print("   ✓ 验证器配置完成")
    
    # 6. 验证QA pairs
    print("6. 验证QA pairs...")
    try:
        validated_pairs = validator.validate(qa_pairs, doc_content)
        # 验证后再做一次安全过滤，避免统计阶段KeyError
        validated_pairs = [
            p for p in validated_pairs
            if isinstance(p, dict) and ('question' in p) and ('answer' in p)
        ]
        print(f"   ✓ 验证完成，通过验证的QA pairs: {len(validated_pairs)}/{len(qa_pairs)}")
    except Exception as e:
        print(f"   ✗ 验证失败: {e}")
        return {"error": f"验证失败: {e}"}
    
    # 7. 生成详细报告
    print("7. 生成详细报告...")
    
    # 统计信息
    stats = {
        "total_generated": len(qa_pairs),
        "total_validated": len(validated_pairs),
        "validation_rate": (len(validated_pairs) / len(qa_pairs)) if qa_pairs else 0,
        "average_question_length": (
            sum(len(pair.get('question', '')) for pair in validated_pairs) / len(validated_pairs)
        ) if validated_pairs else 0,
        "average_answer_length": (
            sum(len(pair.get('answer', '')) for pair in validated_pairs) / len(validated_pairs)
        ) if validated_pairs else 0
    }
    
    # 质量分析
    quality_analysis = []
    for i, pair in enumerate(validated_pairs):
        analysis = {
            "id": i + 1,
            "question_length": len(pair.get('question', '')),
            "answer_length": len(pair.get('answer', '')),
            "question": pair.get('question', ''),
            "answer": pair.get('answer', '')
        }
        quality_analysis.append(analysis)
    
    result = {
        "document_path": doc_path,
        "llm_config": {
            "provider": llm_provider,
            "model": llm_model
        },
        "generation_config": {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "show_chunks": show_chunks
        },
        "validation_config": validation_config,
        "statistics": stats,
        "qa_pairs": validated_pairs,
        "quality_analysis": quality_analysis
    }
    
    print("   ✓ 报告生成完成")
    return result

def save_results(result: Dict[str, Any], output_dir: str = "output"):
    """保存结果到文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存完整结果
    full_result_path = os.path.join(output_dir, "qa_generation_result.json")
    with open(full_result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 保存纯QA pairs
    qa_pairs_path = os.path.join(output_dir, "qa_pairs.json")
    with open(qa_pairs_path, 'w', encoding='utf-8') as f:
        json.dump(result.get("qa_pairs", []), f, ensure_ascii=False, indent=2)
    
    # 保存统计报告
    stats_path = os.path.join(output_dir, "statistics.txt")
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write("=== QA Pairs 生成和验证统计报告 ===\n\n")
        f.write(f"文档路径: {result.get('document_path', 'N/A')}\n")
        f.write(f"LLM配置: {result.get('llm_config', {})}\n\n")
        
        stats = result.get("statistics", {})
        f.write("统计信息:\n")
        f.write(f"- 总生成数量: {stats.get('total_generated', 0)}\n")
        f.write(f"- 验证通过数量: {stats.get('total_validated', 0)}\n")
        f.write(f"- 验证通过率: {stats.get('validation_rate', 0):.2%}\n")
        f.write(f"- 平均问题长度: {stats.get('average_question_length', 0):.1f} 字符\n")
        f.write(f"- 平均答案长度: {stats.get('average_answer_length', 0):.1f} 字符\n\n")
        
        f.write("验证配置:\n")
        for key, value in result.get("validation_config", {}).items():
            f.write(f"- {key}: {value}\n")
    
    print(f"结果已保存到 {output_dir} 目录:")
    print(f"  - 完整结果: {full_result_path}")
    print(f"  - QA pairs: {qa_pairs_path}")
    print(f"  - 统计报告: {stats_path}")

def print_summary(result: Dict[str, Any]):
    """打印结果摘要"""
    if "error" in result:
        print(f"\n❌ 处理失败: {result['error']}")
        return
    
    stats = result.get("statistics", {})
    print(f"\n=== 处理完成摘要 ===")
    print(f"📄 文档: {result.get('document_path', 'N/A')}")
    print(f"🤖 LLM: {result.get('llm_config', {}).get('model', 'N/A')}")
    print(f"📊 生成统计:")
    print(f"   - 总生成: {stats.get('total_generated', 0)} 个QA pairs")
    print(f"   - 验证通过: {stats.get('total_validated', 0)} 个QA pairs")
    print(f"   - 通过率: {stats.get('validation_rate', 0):.2%}")
    print(f"   - 平均问题长度: {stats.get('average_question_length', 0):.1f} 字符")
    print(f"   - 平均答案长度: {stats.get('average_answer_length', 0):.1f} 字符")
    
    # 显示前几个QA pairs作为示例
    qa_pairs = result.get("qa_pairs", [])
    if qa_pairs:
        print(f"\n📝 示例QA pairs (前3个):")
        for i, pair in enumerate(qa_pairs[:3]):
            print(f"   {i+1}. Q: {pair['question']}")
            print(f"      A: {pair['answer'][:100]}{'...' if len(pair['answer']) > 100 else ''}")

def main():
    """主函数"""
    # 文档路径
    doc_path = "examples/1.txt"
    
    # 检查文档是否存在
    if not os.path.exists(doc_path):
        print(f"❌ 文档不存在: {doc_path}")
        return
    # 配置 validation_config
    validation_config = {
        "uniqueness_distance_threshold": 0.1,
        "uniqueness_check_enabled":True,
        'similarity_model':'paraphrase-multilingual-MiniLM-L12-v2'
      
    }
    # 配置参数
    config = {
        "llm_provider": "ollama",  # 或者 "openai"
        "llm_model": "llama3.1:8b",  # 使用更稳定的模型
        "show_chunks": True,  # 设置为True可以看到文档分块
        "chunk_size": 4000,
        "chunk_overlap": 20,
        "validation_config": validation_config
    }
    


    
    print("🚀 开始QA pairs生成和验证流程...")
    
    # 生成和验证QA pairs
    result = generate_qa_pairs_with_validation(
        doc_path=doc_path,
        **config
    )
    
    # 打印摘要
    print_summary(result)
    
    # 保存结果
    if "error" not in result:
        save_results(result)
        print(f"\n✅ 所有结果已保存到 output 目录")

if __name__ == "__main__":
    main()
