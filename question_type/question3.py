from enum import Enum
from pydantic import BaseModel, Field
class Answer(str, Enum):
    answer1="正确"
    answer2="错误"

class Question(BaseModel):
    question_type: str = "判断题"  
    question: str = Field(description="基于文本生成的问题内容")
    answer: Answer=Field(description="正确或错误")