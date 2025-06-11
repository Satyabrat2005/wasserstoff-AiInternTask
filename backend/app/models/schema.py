from pydantic import BaseModel
from typing import List, Optional


class PageText(BaseModel):
    page: int
    text: str


class UploadResponse(BaseModel):
    filename: str
    total_pages: int
    sample: List[PageText]


class ThemeItem(BaseModel):
    label: str
    count: int


class ThemeResponse(BaseModel):
    themes: List[ThemeItem]


class AskRequest(BaseModel):
    question: str
    chat_history: Optional[List[str]] = []  # or whatever you're using


class AskResponse(BaseModel):
    answer: str
    matched_context: Optional[str] = None  # optional, if you want to show source context

