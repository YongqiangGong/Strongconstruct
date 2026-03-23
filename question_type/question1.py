from enum import Enum
from pydantic import BaseModel, Field
class Options(BaseModel):
    A: str = Field(description="答案中的第1个选项")
    B: str = Field(description="答案中的第2个选项")
    C: str = Field(description="答案中的第3个选项")
    D: str = Field(description="答案中的第4个选项")
    E: str = Field(description="答案中的第5个选项")

class Question(BaseModel):
    question_type: str = "选择题"  
    question: str = Field(description="基于文本生成的问题内容")
    options: Options = Field(description="问题对应的选项")
    answer: str = Field(description="问题对应的正确答案")