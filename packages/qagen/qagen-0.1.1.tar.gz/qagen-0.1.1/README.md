# QA Generation CN - 中文问答对生成工具

一个强大的中文文档问答对（QA pairs）自动生成和验证工具，支持多种LLM提供商，具备完善的质量验证机制。

## ✨ 功能特性

- 🤖 **多LLM支持**: 支持Ollama（本地）和OpenAI（云端）模型
- 📄 **智能文档处理**: 自动分块、中文优化处理
- ✅ **多维度验证**: 语义相似度、关键词匹配、长度控制、唯一性检测
- 📊 **详细统计**: 生成质量报告和数据分析
- 🎯 **中文优化**: 专门针对中文内容优化
- 🔧 **灵活配置**: 丰富的参数配置选项

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd qa_gen_cn

# 安装依赖
pip install -r requirements.txt

# 激活conda环境（如果使用）
conda activate LLM
```

### 2. 配置LLM

#### 使用Ollama（推荐，本地运行）

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve

# 下载模型
ollama pull llama3.1:8b
# 或下载其他模型
ollama pull qwen3:8b
ollama pull gemma2:9b
```

#### 使用OpenAI（云端）

```bash
# 设置API密钥
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 基础使用

#### 方法一：使用完整脚本（推荐）

```bash
# 运行完整的生成和验证流程
python examples/generate_and_validate_qa.py
```

#### 方法二：使用简化脚本

```bash
# 仅生成QA pairs，不进行验证
python examples/generator_and_no_validate_qa.py
```

#### 方法三：编程方式使用

```python
from qa_gen_cn import generate_qa_pairs

# 基础使用
qa_pairs = generate_qa_pairs(
    doc_path="your_document.txt",
    llm_provider="ollama",
    llm_model="llama3.1:8b"
)

# 自定义配置
qa_pairs = generate_qa_pairs(
    doc_path="your_document.txt",
    llm_provider="openai",
    llm_model="gpt-3.5-turbo",
    show_chunks=True,
    validation_config={
        "keyword_top_n": 10
    },
    api_key="your-openai-api-key"
)
```

## 📖 详细使用指南

### 1. 文档格式要求

支持纯文本文件（.txt），内容示例：

```text
大有唐王降敕封，钦差玄奘问禅宗。坚心磨琢寻龙穴，着意修持上鹫峰。
边界远游多少国，云山前度万千重。自今别驾投西去，秉教迦持悟大空。

却说三藏自贞观十三年九月望前三日，蒙唐王与多官送出长安关外。
一二日马不停蹄，早至法门寺。本寺住持上房长老，带领众僧有五百余人，
两边罗列，接至里面，相见献茶。茶罢进斋。斋后不觉天晚。
```

### 2. 配置参数详解

#### LLM配置

```python
# Ollama配置
llm_config = {
    "llm_provider": "ollama",
    "llm_model": "llama3.1:8b",  # 或其他可用模型
    "show_chunks": True,  # 显示文档分块过程
    "chunk_size": 500,   # 文档块大小
    "chunk_overlap": 50  # 块重叠大小
}

# OpenAI配置
openai_config = {
    "llm_provider": "openai",
    "llm_model": "gpt-3.5-turbo",  # 或 "gpt-4"
    "api_key": "your-api-key"
}
```

#### 验证配置

```python
validation_config = {
    # 语义相似度验证
    "similarity_threshold": 0.3,  # 相似度阈值（0-1）
    "similarity_model": "paraphrase-multilingual-MiniLM-L12-v2",
    
}
```

### 3. 高级使用示例

#### 自定义生成流程

```python
from qa_gen_cn.generator import QAGenerator
from qa_gen_cn.llm_factory import LLMFactory
from qa_gen_cn.validator import QAPairValidator
from qa_gen_cn.utils import load_document

# 1. 初始化LLM
llm = LLMFactory.create_llm(
    provider='ollama', 
    model='llama3.1:8b',
    temperature=0.7
)

# 2. 创建生成器
generator = QAGenerator(llm=llm, show_chunks=True)

# 3. 生成QA pairs
qa_pairs = generator.generate_from_document(
    doc_path="your_document.txt",
    chunk_size=3000,
    chunk_overlap=100
)

# 4. 配置验证器
validator = QAPairValidator({
   "similarity_threshold": 0.4,
   'similarity_model':'paraphrase-multilingual-MiniLM-L12-v2'
})

# 5. 验证QA pairs
doc_content = " ".join([doc.page_content for doc in load_document("your_document.txt")])
validated_pairs = validator.validate(qa_pairs, doc_content)

print(f"生成 {len(qa_pairs)} 个QA pairs，验证通过 {len(validated_pairs)} 个")
```



## 📊 输出结果

### 文件结构

运行完成后，会在`output`目录生成以下文件：

```
output/
├── qa_generation_result.json  # 完整结果（包含配置、统计等）
├── qa_pairs.json             # 纯QA pairs数据
└── statistics.txt            # 统计报告
```

### 输出格式示例

#### QA Pairs JSON格式

```json
[
  {
    "question": "什么是人工智能？",
    "answer": "人工智能是计算机科学的一个分支，旨在创建能够模拟人类智能的机器。"
  },
  {
    "question": "机器学习和深度学习的关系是什么？",
    "answer": "机器学习是人工智能的分支，深度学习是机器学习的子集，使用神经网络进行学习。"
  }
]
```

#### 统计报告示例

```
=== QA Pairs 生成和验证统计报告 ===

文档路径: examples/1.txt
LLM配置: {'provider': 'ollama', 'model': 'llama3.1:8b'}

统计信息:
- 总生成数量: 25
- 验证通过数量: 18
- 验证通过率: 72.00%
- 平均问题长度: 23.4 字符
- 平均答案长度: 156.7 字符

验证配置:
- keyword_top_n: 15
```

## 🔧 验证机制详解

### 1. 语义相似度验证
- **原理**: 使用多语言语义模型计算问题、答案与原文的相似度
- **作用**: 确保生成的QA pairs与原文内容相关
- **配置**: `similarity_threshold` (0-1，越高越严格),`similarity_model`

### 2. 关键词匹配验证
- **原理**: 提取原文关键词，验证问题和答案是否包含相关关键词
- **作用**: 保证QA pairs涵盖文档核心内容
- **配置**: `keyword_top_n` (提取关键词数量)

### 3. 长度验证
- **原理**: 检查问题和答案的长度是否在合理范围内
- **作用**: 避免过短或过长的QA pairs
- **配置**: `question_min_length`,`question_max_length`,`answer_min_length`, `answer_max_length`

### 4. 唯一性验证
- **原理**: 使用聚类算法检测重复的QA pairs
- **作用**: 确保生成结果的多样性
- **配置**: `similarity_model`,`uniqueness_check_enabled`,`uniqueness_distance_threshold` (聚类距离阈值)，越小越好（更严格去重），但需要根据你的具体需求来平衡数量和质量。
   - 0.0: 理论上不允许任何重复，但实际中很少使用
   - 1.0: 允许所有内容，相当于关闭去重功能
   - 建议范围: 0.05-0.3 之间，根据具体需求调整


### 5. 特别注意
Validation 1,2,3,4 validation是互斥的，只能选择一个验证
验证优先级：**1>2>3>4**，在self.config中配置了：
   1 similarity_threshold和similarity_model，后面其他验证的配置可以不配置，如果配置了也不起作用。
   2 question_min_length和question_max_length，answer_min_length和answer_max_length，后面其他验证的配置可以不配置，如果配置了也不起作用。
   3 keyword_top_n，后面其他验证的配置可以不配置，如果配置了也不起作用。
   4 similarity_model、uniqueness_distance_threshold和uniqueness_check_enabled，其他验证的配置可以不配置，如果配置了也不起作用。
## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. Ollama连接问题

```bash
# 检查Ollama服务状态
ollama list

# 重启Ollama服务
ollama serve

# 检查模型是否已下载
ollama show llama3.1:8b
```

#### 2. OpenAI API问题

```bash
# 检查API密钥
echo $OPENAI_API_KEY

# 测试API连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

#### 3. 验证失败率高

```python
# 降低验证标准
validation_config = {
    "similarity_threshold": 0.1,  # 降低相似度要求
}
```

#### 4. 内存不足

```python
# 减小处理块大小
config = {
    "chunk_size": 2000,      # 减小块大小
    "chunk_overlap": 100     # 减小重叠
}
```

### 调试模式

启用详细输出查看处理过程：

```python
# 显示文档分块
"show_chunks": True

# 查看验证详情
validator = QAPairValidator(config)
# 可以单独测试各个验证方法
```

## 🧪 测试

运行单元测试确保功能正常：

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_generator.py -v

# 运行覆盖率测试
python -m pytest tests/ --cov=qa_gen_cn --cov-report=html
```

## 📁 项目结构

```
qa_gen_cn/
├── qa_gen_cn/                    # 核心模块
│   ├── __init__.py              # 主入口
│   ├── generator.py             # QA生成器
│   ├── llm_factory.py           # LLM工厂
│   ├── validator.py             # 验证器
│   ├── super_json.py            # JSON处理工具
│   └── utils.py                 # 工具函数
├── examples/                    # 示例代码
│   ├── generate_and_validate_qa.py    # 完整生成脚本
│   ├── generator_and_no_validate_qa.py # 简化生成脚本
│   └── 1.txt                   # 示例文档
├── tests/                       # 单元测试
│   ├── test_generator.py
│   ├── test_validator.py
│   └── ...
├── output/                      # 输出目录
├── requirements.txt             # 依赖列表
├── pyproject.toml              # 项目配置
└── README.md                   # 本文档
```

## 🛠️ 技术栈

- **LangChain**: LLM集成和链式处理
- **Sentence Transformers**: 语义相似度计算
- **jieba**: 中文分词和关键词提取
- **scikit-learn**: 聚类和去重算法
- **Ollama**: 本地LLM服务
- **OpenAI**: 云端LLM API
- **pytest**: 单元测试框架

## 📄 许可证

本项目基于MIT许可证开源。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 支持

如果遇到问题，请：
1. 查看本文档的故障排除部分
2. 检查项目的Issues页面
3. 提交新的Issue描述问题
