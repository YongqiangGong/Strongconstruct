# 🧠 StrongConstruct

[**English**](./README_EN.md) | [**中文**](./README.md)

StrongConstruct is a fine-tuning dataset generation framework based on Large Language Models (LLMs). It generates Supervised Fine-Tuning (SFT) and Preference Datasets (PD) from provided PDF texts. By utilizing a human-in-the-loop workflow, StrongConstruct effectively enhances dataset quality and annotation efficiency. Additionally, StrongConstruct includes the StrongUI front-end module, providing a visual interface for users to correct and annotate data conveniently. The framework has been tested on medical texts, demonstrating high-quality results. All files in StrongConstruct are customizable, and domain-specific labels can be configured to optimize generation performance.

## 📚 Table of Contents
- 📖 Introduction
- ✨ Features
- 📁 Project Structure
- ⚙️ Installation and Usage
- 🔧 Code Usage Tutorial
- ⚠️ Precautions
- 🌍 Application Scenarios
- 👥 Team Members
- 🏛️ Affiliations


## 📖 Introduction

In the field of Large Language Models, constructing high-quality data is often the most time-consuming phase. StrongConstruct automates the process—from PDF parsing and text chunking to quality scoring and question generation—through a "human-in-the-loop" workflow:

- High Automation: Integrates MinerU for deep PDF parsing while preserving layout logic.

- Controllable Quality: Introduces an LLM scoring mechanism to easily filter out low-quality text chunks and questions.

- Annotation Labeling: Annotates datasets based on domain labels, facilitating various use cases.

- Visualization: Provides the StrongUI interface for intuitive data correction and annotation.

## ✨ Features
- Full Pipeline: Covers PDF to Markdown conversion, text cleaning, semantic segmentation, question generation, and auto-scoring.

- Intelligent Cleaning Strategy: Uses chonkie for semantic chunking combined with LLM-based value scoring for each chunk.

- Dual Dataset Support: Simultaneously generates SFT (Instruction-Answer) and PD (Preference/Comparison) datasets.

- Multi-dimensional Labeling: Supports user-defined domain labels.

- Interactive Correction: Reduces the barrier for manual auditing via an HTML front-end interface.

## 📁 Project Structure

```
StrongConstruct/
├── README.md                           # 项目说明文档（中文）
├── README_EN.md                        # 项目说明文档（英文）
├── my_code.py                          # 主程序入口
├── StrongUI.html                        # 校正前端UI
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
│   ├── 10.SFTquestionscore.py           # SFT问题评分
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

## Installation and Usage

### 1. Create and Activate Environment

```bash
conda create -n StrongConstruct python=3.12
conda activate StrongConstruct
```

### 2. Install Dependencies

For MinerU installation, please refer to：https://github.com/opendatalab/MinerU

Other dependencies:

```bash
pip install pydantic instructor openai chonkie fastapi "uvicorn[standard]"
```

### 3. Download Project

```bash
git clone https://github.com/YongqiangGong/StrongConstruct.git
cd StrongConstruct
```

### 4.Run the Program

```bash
python my_code.py
```

### 5. Workflow and Human-Interaction (Medical Example)

#### 🔑 5.1 Initial Configuration

After starting the main program, manually input the following:
- 📄 PDF Source Path (e.g., /home/user/pdfs)
- 📂 Output Directory (e.g., /home/user/output)
- 🌐 LLM API Endpoint (e.g., https://dashscope.aliyuncs.com/compatible-mode/v1)
- 🤖 Model Name (e.g., qwen-max)
- 🔑 API Key (e.g., sk-xxxxxx)
- 🔄 Specific Domain (e.g., Hepatobiliary Diseases)

#### 🔑 5.2 PDF to Markdown Conversion
#### 🔑 5.3 Text Chunk Processing

- Segmentation: Splits Markdown into chunks based on LLM context windows.
- Merging: Combines split chunks into a single file for processing.
- Character Count: Calculates length to determine the appropriate number of questions.
- Scoring: Evaluates chunk quality using the LLM.

#### 🔑 5.4 Question Generation and Scoring
- Generation: Creates SFT and PD data based on chunk content.
- Scoring: Evaluates the quality of generated questions.
- PD Recommendation: LLM recommends the preferred answer within the PD dataset.

#### 🔑 5.5 Label Annotation (Customizable)

- Content Labels: Annotates content (e.g., Etiology, Diagnosis, Clinical Manifestation).
- System Labels: Annotates biological systems (e.g., Liver, Tissue, Function).
- Disease Labels: Annotates specific diseases.

### 6. Output Results

After completion, StrongConstruct will generate the following files:

- `mineru`: Contains the MinerU conversion results corresponding to the PDF documents.
- `md`: Contains the Markdown format corresponding to the PDF documents.
- `chunks`: Text chunks segmented based on the LLM.
- `chunksmerge.json`: Merged text chunks from all Markdown files.
- `chunksnumber.json`: Character counts for each text chunk.
- `chunksscore.json`: Quality scores for the text chunks.
- `SFTquestion.json`: Generated SFT (Supervised Fine-Tuning) questions and answers.
- `SFTquestionscore.json`: Quality scores for the SFT dataset.
- `PDquestion.json`: Generated PD (Preference Dataset) questions and answers.
- `PDquestionscore.json`: Quality scores for the PD dataset.
- `PDquestionrecommendation.json`: Answer recommendations for the PD dataset based on the LLM.
- `contentlabel.json`: Structured data of content categories for all questions.
- `systemlabel.json`: Structured data of human body systems for all questions.
- `diseaselabel.json`: Structured data of disease categories for all questions.

These files will be stored in the specified output directory, allowing users to perform subsequent processing and analysis as needed.

### 7. Strong UI

Strong UI is a visual front-end that can correct and complete different types of files generated by StrongConstruct. The main program will automatically open port 6969 when running, and users can easily use Strong UI to process the generated files, greatly improving work efficiency.

## `codes` Usage Tutorial (Examples)

### PDF to Markdown conversion

```bash
python codes/1.mineru.py demo/pdfs demo/output/mineru

### Extract Markdown from MinerU output

### Text segmentation
Note: You must input the directory containing the .md files; otherwise, the file cannot be executed.
```bash
python codes/3.chunksseparate.py demo/output/mineru/黄家驷外科学解剖生理/auto demo/output/md
```

The `3.chunksseparatetxt.py` script supports txt file splitting, independent of the execution of the first two scripts.

### Text chunk merging
```bash
python codes/5.chunksmerge.py demo/output/md demo/output
```

### Others
The remaining files can be run in Python after opening them individually.


## ⚠️ Precautions
- 🚀 Model Selection: Try to choose large-scale models with massive parameters to improve extraction results; avoid using small-parameter models.

- 🔗 Path Requirement: When using MinerU, please note that the PDF file storage path must be under the pdfs directory; otherwise, the file cannot be executed.

- ⏱️ Processing Time: The initial conversion of PDF documents to Markdown format is slow; if no error is reported, there is no need to worry.

- 🔧 File Support: Currently, the main program only supports PDF files. TXT files must be segmented separately using the 2.chunksseparatetxt.py file in the codes directory.

- 🔓 Open Source: This framework is an open-source project; users can modify and customize it according to their needs.



## 🌍 Application Scenarios

- LLM Training: Rapidly convert professional textbooks, clinical guidelines, and legal statutes into high-quality training datasets.
- RAG Knowledge Base Construction: Improve the accuracy of Retrieval-Augmented Generation by utilizing high-quality chunking and structured labeling.
- Enterprise Internal Training: Transform internal corporate manuals and handbooks into interactive Q&A pairs for employee training.
- Benchmark Construction: Provide standardized datasets for LLM evaluation, ensuring consistent performance comparisons across different tasks and domains.

## 👥 Team Members

- Yongqiang Gong
- Ruixi Li
- Han Dong
- Chenyu Xue
- Ruiqi Ma
- Yijin Liu
- Puhe Gong
- Mingyang Zhang

## 👥 Research Supervisor

- Yi Bai 
- Yin Liu
- Yamin Zhang


## 🏛️ Institution

- School of Medicine, Nankai University
- Department of Hepatobiliary Surgery, Tianjin First Central Hospital
