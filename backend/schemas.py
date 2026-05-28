# ==============================================================================
# JEE MENTOR AI - DATA BOUNDARY SCHEMAS (Pydantic API Models)
# ==============================================================================
import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field

# --- User & Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# --- Chat & RAG Schemas ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: List[Dict[str, Any]] = []

# --- OCR & Question Solver Schemas ---
class SolveRequest(BaseModel):
    question_text: Optional[str] = None
    image_base64: Optional[str] = None # Base64 encoded string of question image
    subject: Optional[str] = None

class SolveResponse(BaseModel):
    extracted_text: Optional[str] = None
    solution: str
    formulas_used: List[str] = []
    graph_base64: Optional[str] = None # Base64 encoded plotted chart if triggered
    latency_ms: float

# --- Quiz & Mock Test Schemas ---
class TestConfig(BaseModel):
    subject: str
    topics: List[str] = []
    difficulty: str = "Medium"
    num_questions: int = 5

class TestQuestionOut(BaseModel):
    id: str
    subject: str
    topic: str
    difficulty: str
    input: str
    tags: List[str] = []

class QuestionAttempt(BaseModel):
    question_text: str
    subject: str
    topic: str
    difficulty: str
    student_answer: Optional[str] = None
    is_correct: bool
    confidence_score: float = 1.0

class TestAttemptSubmit(BaseModel):
    subject: str
    topics: List[str]
    difficulty: str
    score: float
    total_questions: int
    correct_answers: int
    time_taken_seconds: int
    question_attempts: List[QuestionAttempt]

# --- Analytics Schemas ---
class WeakTopicInfo(BaseModel):
    topic: str
    subject: str
    accuracy: float
    questions_attempted: int
    recommendation: str

class AnalyticsSummary(BaseModel):
    overall_accuracy: float
    total_solved: int
    subjects_proficiency: Dict[str, float] # e.g. {"Physics": 0.72, "Chemistry": 0.85}
    weak_topics: List[WeakTopicInfo]
