# ==============================================================================
# JEE MENTOR AI - TRANSACTIONAL DATABASE SCHEMAS (SQLAlchemy Models)
# ==============================================================================
import datetime
import uuid
import json
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    test_attempts = relationship("TestAttempt", back_populates="user", cascade="all, delete-orphan")
    question_history = relationship("QuestionHistory", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("AnalyticsMetric", back_populates="user", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New JEE Doubts Session")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False) # system, user, assistant
    content = Column(Text, nullable=False)
    
    # RAG sources, tool triggers, image OCR text are serialized as a JSON string
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    @property
    def message_metadata(self) -> dict:
        try:
            return json.loads(self.metadata_json or "{}")
        except Exception:
            return {}

    @message_metadata.setter
    def message_metadata(self, val: dict):
        self.metadata_json = json.dumps(val or {})

class TestAttempt(Base):
    __tablename__ = "test_attempts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(100), nullable=False)
    topics_serialized = Column(Text, nullable=False) # JSON array of topics
    difficulty = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    time_taken_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="test_attempts")

    @property
    def topics(self) -> list:
        try:
            return json.loads(self.topics_serialized or "[]")
        except Exception:
            return []

    @topics.setter
    def topics(self, val: list):
        self.topics_serialized = json.dumps(val or [])

class QuestionHistory(Base):
    __tablename__ = "question_history"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(255), nullable=False)
    difficulty = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    student_answer = Column(String(255), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    confidence_score = Column(Float, default=1.0) # confidence multiplier of response
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="question_history")

class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(255), nullable=False)
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    running_proficiency = Column(Float, default=0.5) # Scale 0.0 to 1.0 (starts at 50% midpoint)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analytics")
