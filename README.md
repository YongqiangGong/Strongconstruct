# 🧠 StrongConstruct

[**English**](./README_EN.md) | [**中文**](./README.md)

StrongConstruct是一个基于大模型的微调数据集生成框架，能够基于给定的PDF文本生成监督微调数据集和偏好数据集。StrongConstruct通过人机交互流程，能够有效提升数据集的质量和标注效率。此外StrongConstruct包含了StrongUI前端模块，能够为用户提供可视化的操作界面，方便用户进行数据集的校正和标注。目前此框架已经使用医学文本进行了测试，经过评估后发现可以得到较好的效果。StrongConstruct中的所有文件均可自由修改并且可以设置领域标签以提升生成效果。

## 📚 目录

- [📖 引言]
- [✨ 功能特点]
- [📁 项目结构]
- [⚙️ 安装与使用]
  - [1. 创建新环境并激活](#1-创建新环境并激活)
  - [2. 安装依赖](#2-安装依赖)
  - [3. 下载项目至工作路径](#3-下载项目至工作路径)
  - [4. 开始运行](#4-开始运行)
  - [5. 工作流程及人机交互](#5-工作流程及人机交互以医学文本为例)
  - [6. 输出结果](#6-输出结果)
  - [7. Strong UI](#7-strong-ui)
- [🔧 codes代码使用教程]
- [⚠️ 注意事项]
- [🌍 应用场景]
- [👥 团队成员]
- [🏛️ 单位]


## 📖 引言 

在大模型领域中，高质量数据的构建往往是最耗时的一环。StrongConstruct 通过“人机交互”流程，实现了从 PDF 解析、文本分块、质量评分到题目生成的自动化：

- 高自动化：集成 MinerU 深度解析 PDF，保留版面逻辑。

- 质量可控：引入 LLM 评分机制，易于剔除低质量文本块与题目。

- 注释标注：根据领域标签为数据集进行注释标签，方便多种用途。

- 可视化：提供 StrongUI 界面，支持对生成数据进行直观的校正与标注。

## ✨ 功能特点

- 全流程：覆盖 PDF 转 Markdown、文本清洗、语义分割、题目生成及自动评分。

- 智能清洗策略：利用 chonkie 进行语义分块，并结合 LLM 对分块进行价值评分。

- 双数据集支持：同步生成 SFT（指令-回答）数据集与 PD（偏好对比）数据集。

- 多维度标签体系：支持用户自定义领域标签。

- 交互式校正：通过 HTML 前端界面，降低人工审核数据的操作门槛。

## 📁 项目结构

```
StrongConstruct/
├── README.md                           # 项目说明文档（中文）
├── README_EN.md                        # 项目说明文档（英文）
├── my_code.py                          # 主程序入口
├── Strong_UI                            # 可视化前端
├── codes/                              # 核心代码目录
│   ├── 1.mineru.py                     # PDF转Markdown转换
│   ├── 2.extract_md.py                 # 从Markdown文件中提取文本
│   ├── 3.chunksseparate.py             # 文本分割
│   ├── 4.chunksseparatetxt.py          # TXT文件分割
│   ├── 5.chunksmerge.py                # 文本块合并
│   ├── 6.chunksnumber.py               # 计算文本块字符数量
│   ├── 7.chunksscore.py                # 文本块评分
│   ├── 8.textUI.py                     # 文本处理UI界面
│   ├── 9.generationSFTquestion.py      # 生成SFT问题
│   ├── 10.SFTquestionscore.py          # SFT问题评分
│   ├── 11.generationPDquestion.py      # 生成PD问题
│   ├── 12.PDquestionscore.py           # PD问题评分
│   ├── 13.PDquestionrecommendation.py   # PD问题推荐
│   ├── 14.questionUI.py                # 问题处理UI界面
│   ├── 15.contentlabel.py              # 内容标签
│   ├── 16.systemlabel.py               # 系统标签
│   ├── 17.diseaselabel.py              # 疾病标签
│   └── 18.labelUI.py                   # 标签处理UI界面
├── prompts/                            # 提示词模板目录
│   ├── prompt1.txt                    
│   ├── prompt2.txt                     
│   ├── prompt3.txt                    
│   ├── prompt4.txt                    
│   ├── prompt5.txt                    
│   ├── prompt6.txt                     
│   ├── prompt7.txt                     
│   ├── prompt8.txt                     
│   ├── prompt9.txt                    
│   ├── prompt10.txt                   
│   ├── prompt11.txt                    
│   └── prompt12.txt                    
├── question_type/                      # 问题类型定义目录
│   ├── question1.py                    
│   ├── question2.py                  
│   ├── question3.py                    
│   └── question4.py                    
├── disease/                            # 疾病分类目录
│   ├── 传染病、性病.py                 
│   ├── 产科学.py                       
│   ├── 儿科疾病.py                    
│   ├── 妇科学.py                       
│   ├── 呼吸系统.py                     
│   ├── 消化系统.py                     
│   ├── 神经内外科疾病.py               
│   ├── 精神病.py                       
│   ├── 内分泌系统.py                   
│   ├── 泌尿系统.py                     
│   ├── 心血管系统.py                   
│   ├── 血液系统.py                     
│   ├── 运动系统.py                    
│   ├── 风湿性疾病.py                   
│   └── 其他.py                         
└── demo/                               # 示例和输出目录
    ├── pdfs/                           # 示例PDF文件
    │   └── 黄家驷外科学解剖生理.pdf
    └── output/                         # 输出结果目录
        ├── diseaselabel.json           # 疾病标签结果
        ├── systemlabel.json           # 系统标签结果
        ├── contentlabel.json          # 内容标签结果
        ├── PDquestionrecommendation.json # PD问题推荐结果
        ├── PDquestionscore.json       # PD问题评分结果
        ├── PDquestion.json            # PD问题结果
        ├── SFTquestionscore.json      # SFT问题评分结果
        ├── SFTquestion.json           # SFT问题结果
        ├── chunksscore.json           # 文本块评分结果
        ├── chunksnumber.json          # 文本块数量结果
        ├── chunksmerge.json           # 文本块合并结果
        ├── chunks/                    # 文本块目录
        │   └── 黄家驷外科学解剖生理__黄家驷外科学解剖生理.json
        ├── mineru/                    # MinerU转换结果
        │   └── 黄家驷外科学解剖生理/
        │       ├── auto/
        │       │   ├── 黄家驷外科学解剖生理_model.json
        │       │   ├── 黄家驷外科学解剖生理_middle.json
        │       │   ├── 黄家驷外科学解剖生理_content_list.json
        │       │   ├── 黄家驷外科学解剖生理.md
        │       │   ├── 黄家驷外科学解剖生理_origin.pdf
        │       │   ├── 黄家驷外科学解剖生理_span.pdf
        │       │   ├── 黄家驷外科学解剖生理_layout.pdf
        │       │   └── images/        # 提取的图片
        │       │       ├── 7ef23ab61cc9bd2fb6d9034bb0ffa78495a8ff2cd108cee785ccfefa2e5fd8df.jpg
        │       │       └── efde30aad6c2d4f3b77290bc152e8cbb5b0541df5e24646127b18528c1ddf701.jpg
        └── md/                        # Markdown文件
            └── 黄家驷外科学解剖生理__黄家驷外科学解剖生理.md
```

## 安装与使用

### 1. 创建新环境并激活

```bash
conda create -n StrongConstruct python=3.12
conda activate StrongConstruct
```

### 2. 安装依赖

mineru安装与使用请参考：https://github.com/opendatalab/MinerU

其余依赖：

```bash
pip install pydantic instructor openai chonkie fastapi "uvicorn[standard]"
# 速度较慢可使用镜像，推荐阿里云镜像
```

### 3. 下载项目至工作路径

```bash
git clone https://github.com/YongqiangGong/StrongConstruct.git
cd StrongConstruct
```

### 4.开始运行

```bash
python my_code.py
```

### 5. 工作流程及人机交互（以医学文本为例）

#### 🔧 5.1 初始配置输入
运行框架主程序后，需依次手动输入核心配置信息：
- 📄 PDF 源文件路径（示例：/home/user/pdfs）
- 📂 结构化数据输出目录（示例：/home/user/output）
- 🌐 大模型服务 API 地址（示例：https://dashscope.aliyuncs.com/compatible-mode/v1）
- 🤖 调用的模型名称（示例：qwen3-max）
- 🔑 模型访问密钥（示例：sk-2d7c12272772）
- 🔄 特有领域（示例：肝胆疾病）

#### 🌐 5.2 PDF文档转换为Markdown文件

#### 🔑 5.3 文本块处理

- 🔄 文本块分割：根据LLM的能力对Markdown文件进行分割，生成多个文本块。
- 🔍 文本块合并：将所有分割后的文本块合并为一个文件，方便后续处理。
- 🔢 文本块字符数：计算每个文本块的字符数，用于后续确定题目数量。
- 🔍 文本块评分：基于LLM对每个文本块进行质量评估，生成评分结果。

#### 🔑 5.4 题目生成与评分

- 🔧 题目生成：基于LLM对文本块内容生成符合要求的题目（监督微调数据和偏好数据）。
- 🔍 题目评分：基于LLM对生成的题目进行质量评估，生成评分结果。
- 🔄 偏好推荐：基于LLM对PD数据集中的答案进行推荐，生成推荐结果。

#### 🔑 5.5 标签注释（可自行更改）

- 🔧 内容标签：基于LLM对文本块内容进行注释，生成内容标签（病因病理、诊断治疗、临床表现、文献指南和其他）。
- 🔧 系统标签：基于LLM对文本块内容进行注释，生成系统标签（肝脏、肝脏组织、肝脏功能、肝脏疾病、肝脏治疗和其他）。
- 🔧 疾病标签：基于LLM对文本块内容进行注释，生成疾病标签（肝胆疾病、肝脏疾病、肝病和其他）。

### 6. 输出结果

运行完成后，Strongminer 将生成以下文件：

- `mineru`：包含pdf文档对应转换后的mineru结果
- `md`：包含pdf文档对应的markdown格式
- `chunks`：基于LLM进行分割后的文本块
- `chunksmerge`：合并所有markdown文件后的文本块
- `chunksnumber.json`：计算每一个文本块的字符数
- `chunksscore.json`：对文本块的质量进行评分（Strong UI）
- `SFTquestion.json`：生成的SFT题目和答案
- `SFTquestionscore.json`：对监督微调数据集进行评分（Strong UI）
- `PDquestion.json`：生成的PD题目和答案
- `PDquestionscore.json`：对PD数据集进行评分
- `PDquestionrecommendation.json`：基于LLM对PD数据集中的答案进行推荐（Strong UI）
- `contentlabel.json`：包含所有题目所属内容的结构化数据（病因病理、诊断治疗、临床表现、文献指南和其他）
- `systemlabel.json`：包含所有题目所属人体系统的结构化数据
- `diseaselabel.json`：包含所有题目所属疾病的结构化数据（Strong UI）

这些文件将存储在指定的输出目录中，用户可以根据需要进行后续处理和分析。

### 7. Strong UI

Strong UI是一个可视化前端，能够对生成的不同类型文件进行校正和完善。主程序运行时会自动在6969端口开放，用户可以轻松的使用Strong UI对生成的文件进行处理，大大提升工作效率。

## codes代码使用教程（示例）

### pdf转换markdown

```bash
python codes/1.mineru.py demo/pdfs demo/output/mineru
```

### 从mineru输出提取markdown

查看`2.extract_md.py`文件，运行后会在`demo/output/md`目录下生成对应的markdown文件。


### 文本分割
注意此处必须输入的是包含.md文件的目录，否则无法运行文件。
```bash
python codes/3.chunksseparate.py demo/output/mineru/黄家驷外科学解剖生理/auto demo/output/md
```
运行`4.chunksseparatetxt.py`文件能够对txt文件进行分割，不需要运行前两个文件。

### 文本块合并
```bash
python codes/5.chunksmerge.py demo/output/md demo/output
```

### 其余文件单独打开后在python中运行即可。


## ⚠️ 注意事项

- 🚀 尽量选用超大参数的大模型以提升提取效果，避免使用小参数模型
- 🔗 使用mineru时请注意pdf文件存储路径必须为pdfs目录下，否则无法运行文件。
- ⏱️ 前期pdf文档转换为markdown格式速度较慢，没有报错则无需担心
- 🔧 目前主程序仅支持pdf文件，txt文件需单独使用codes文件里面的`4.chunksseparatetxt.py`文件进行分割
- 🔓 本框架为开源项目，用户可以根据需要进行修改和定制。



## 🌍 应用场景

- 大模型训练：将专业教材、临床指南、法律条文快速转为训练集。

- RAG 知识库构建：通过高质量的分块和标签化处理，提升检索增强生成的准确度。

- 企业内训数据生成：将企业内部手册转化为可交互的问答对。

- 基准测试构建：为大模型评估提供标准数据集，确保模型在不同任务上的性能对比。

## 👥 团队成员

- 龚永强
- 李睿熙
- 董瀚
- 薛宸宇
- 马瑞琪
- 刘艺锦
- 龚浦贺
- 张鸣洋

## 👥 指导老师

- 白易
- 刘寅
- 张雅敏

## 🏛️ 单位

- 南开大学医学院
- 天津市第一中心医院肝胆外科
