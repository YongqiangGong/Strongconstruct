from enum import Enum
from pydantic import BaseModel, Field
class Question(BaseModel):
    question_type: str = "填空题"  
    question: str = Field(description="基于文本生成的问题内容")
    answer: str = Field(description="问题对应的答案")