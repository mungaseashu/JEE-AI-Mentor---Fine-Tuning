# ==============================================================================
# JEE MENTOR AI - FASTAPI MAIN SERVER APPLICATION
# ==============================================================================
import time
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any

# Import internal services
from backend.config import settings
from backend.database import get_db, _engine, Base
from backend.models import User, ChatSession, ChatMessage, TestAttempt, QuestionHistory, AnalyticsMetric
from backend.auth import hash_password, verify_password, create_access_token, get_current_user
from backend.schemas import (
    UserCreate, UserOut, UserLogin, Token,
    ChatRequest, ChatResponse,
    SolveRequest, SolveResponse,
    TestConfig, TestQuestionOut, TestAttemptSubmit,
    AnalyticsSummary
)
from backend.cache import jee_cache
from backend.orchestrator import JEEOrchestrator
from backend.adaptive import JEEAdaptiveLearningEngine

# 1. Boot up FastAPI with detailed metadata
app = FastAPI(
    title="JEE Mentor AI API",
    description="Advanced production-grade AI tutoring platform for IIT-JEE Main & Advanced preparation.",
    version="1.0.0"
)

# 2. Configure CORS for smooth React Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local Vite servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Dynamic Database Creation on Boot
@app.on_event("startup")
def startup_event():
    print("[INFO] Server starting up. Performing database schema migrations...")
    try:
        Base.metadata.create_all(bind=_engine)
        print("[SUCCESS] Database tables verified and created successfully.")
    except Exception as e:
        print(f"[ERROR] Database migration failed: {e}")

    # Pre-load AI inference engine singleton to prevent request thread timeouts
    print("[INFO] Server starting up. Pre-loading AI inference engine...")
    try:
        from training.inference import JEEInferenceEngine
        _ = JEEInferenceEngine()
        print("[SUCCESS] AI inference engine loaded and cached in memory.")
    except Exception as e:
        print(f"[WARNING] Failed to pre-load AI inference engine: {e}")

# 4. Custom Rate Limiting Middleware using cache layer
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    client_ip = request.client.host
    endpoint = request.url.path
    
    # Apply rate limiting to critical API boundaries only
    if endpoint.startswith(("/chat", "/solve", "/generate-test")):
        rate_key = f"rate_limit:{client_ip}:{endpoint}"
        current_hits = jee_cache.get(rate_key)
        
        if current_hits is not None and int(current_hits) >= 30: # Limit to 30 requests per minute
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. You can only perform 30 operations per minute."
            )
            
        new_hits = 1 if current_hits is None else int(current_hits) + 1
        # Set sliding window expiry of 60 seconds
        jee_cache.set(rate_key, new_hits, expire_seconds=60)
        
    return await call_next(request)

# ==============================================================================
# ENDPOINTS: AUTHENTICATION
# ==============================================================================

@app.post("/register", response_model=UserOut, status_code=status.HTTP_210_REGISTRATION_SUCCESS if hasattr(status, 'HTTP_210_REGISTRATION_SUCCESS') else 201)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registers a new student profile and saves secure hashed credentials."""
    # Check for duplicates
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="A user with this email address already exists.")
        
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username is already taken.")
        
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/login", response_model=Token)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Validates login credentials and returns a secure signed JWT Access Token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# ==============================================================================
# ENDPOINTS: CORE TUTORING & SOLVER
# ==============================================================================

@app.post("/chat")
def chat_with_tutor(payload: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """RAG-infused streaming chat endpoint yielding tokens in SSE format."""
    orchestrator = JEEOrchestrator(db)
    
    # 1. Establish or retrieve session_id
    session_id = payload.session_id
    if not session_id:
        # Create a new active session for the user
        session = ChatSession(user_id=current_user.id, title=f"Doubts Session: {payload.message[:30]}...")
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id

    # 2. Define streaming generator
    def token_generator():
        # Inject custom SSE headers
        yield f"SESSION_ID:{session_id}\n\n"
        
        for token in orchestrator.orchestrate_chat_stream(session_id, payload.message):
            yield token
            
    return StreamingResponse(token_generator(), media_type="text/event-stream")

@app.post("/solve", response_model=SolveResponse)
def solve_question(payload: SolveRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """OCR Solver: Solves dynamic questions, parses mathematical graphs, and returns steps."""
    orchestrator = JEEOrchestrator(db)
    result = orchestrator.orchestrate_question_solve(
        question_text=payload.question_text,
        image_base64=payload.image_base64,
        subject=payload.subject
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

# ==============================================================================
# ENDPOINTS: ADAPTIVE PRACTICE & QUIZZES
# ==============================================================================

@app.post("/generate-test", response_model=List[TestQuestionOut])
def generate_adaptive_quiz(payload: TestConfig, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generates a personalized, difficulty-adjusted micro practice quiz."""
    engine = JEEAdaptiveLearningEngine(db)
    quiz = engine.generate_personalized_test(
        user_id=current_user.id,
        subject=payload.subject,
        topics=payload.topics,
        num_qs=payload.num_questions
    )
    
    if not quiz:
        raise HTTPException(status_code=404, detail="No high-quality questions matching selection found.")
        
    return quiz

@app.post("/submit-test", status_code=200)
def submit_quiz_attempt(payload: TestAttemptSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Registers quiz results, updates student exponential moving proficiency scores."""
    engine = JEEAdaptiveLearningEngine(db)
    
    # 1. Log master quiz attempt
    attempt = TestAttempt(
        user_id=current_user.id,
        subject=payload.subject,
        score=payload.score,
        total_questions=payload.total_questions,
        correct_answers=payload.correct_answers,
        time_taken_seconds=payload.time_taken_seconds
    )
    attempt.topics = payload.topics
    db.add(attempt)
    
    # 2. Iterate question logs and update proficiencies
    for q in payload.question_attempts:
        history_item = QuestionHistory(
            user_id=current_user.id,
            subject=q.subject,
            topic=q.topic,
            difficulty=q.difficulty,
            question_text=q.question_text,
            student_answer=q.student_answer,
            is_correct=q.is_correct,
            confidence_score=q.confidence_score
        )
        db.add(history_item)
        
        # Trigger adaptive score recalculation
        engine.update_proficiency(
            user_id=current_user.id,
            subject=q.subject,
            topic=q.topic,
            is_correct=q.is_correct
        )
        
    db.commit()
    return {"message": "Quiz scores and proficiency tracks saved successfully!"}

# ==============================================================================
# ENDPOINTS: ANALYTICS & WEAK TOPICS
# ==============================================================================

@app.get("/analyze", response_model=AnalyticsSummary)
def get_analytics_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Compiles learning proficiency metrics and highlights weak chapters."""
    engine = JEEAdaptiveLearningEngine(db)
    
    # 1. Calculate overall accuracy
    history = db.query(QuestionHistory).filter(QuestionHistory.user_id == current_user.id).all()
    total_solved = len(history)
    correct_count = sum(1 for h in history if h.is_correct)
    
    overall_acc = (correct_count / total_solved) if total_solved > 0 else 0.0
    
    # 2. Subject-wise aggregation
    metrics = db.query(AnalyticsMetric).filter(AnalyticsMetric.user_id == current_user.id).all()
    subjects_prof = {"Physics": 0.5, "Chemistry": 0.5, "Mathematics": 0.5} # mid-point default seed
    
    subjects_groups = {}
    for m in metrics:
        if m.subject not in subjects_groups:
            subjects_groups[m.subject] = []
        subjects_groups[m.subject].append(m.running_proficiency)
        
    for subj, vals in subjects_groups.items():
        if vals:
            subjects_prof[subj] = round(sum(vals) / len(vals), 2)
            
    # 3. Pull weak topics lists
    weak_list = engine.get_weak_topics(current_user.id)
    
    return {
        "overall_accuracy": round(overall_acc, 2),
        "total_solved": total_solved,
        "subjects_proficiency": subjects_prof,
        "weak_topics": weak_list
    }

@app.get("/weak-topics", response_model=List[Dict[str, Any]])
def get_weak_topics_only(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Specific helper returning weak topics list and dynamic recommendations."""
    engine = JEEAdaptiveLearningEngine(db)
    weak_topics = engine.get_weak_topics(current_user.id)
    
    return [w.dict() for w in weak_topics]
