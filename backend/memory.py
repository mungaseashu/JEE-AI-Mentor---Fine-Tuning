# ==============================================================================
# JEE MENTOR AI - CONVERSATION MEMORY MANAGER WITH AUTO-SUMMARIZATION
# ==============================================================================
import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.models import ChatMessage

class JEEConversationMemoryManager:
    def __init__(self, db: Session, max_active_words: int = 1500):
        """Initializes the memory manager with session boundary parameters."""
        self.db = db
        self.max_active_words = max_active_words

    def estimate_tokens(self, text: str) -> int:
        """Estimates token length based on standard linguistic average (1 word ≈ 1.33 tokens)."""
        words = text.split()
        return int(len(words) * 1.33)

    def load_session_context(self, session_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Loads messages, performs auto-summarization if bounds exceeded, and returns context."""
        messages = self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
        
        if not messages:
            return "", []

        # Find if a summary exists in session metadata (or check the first message if it is a system summary message)
        existing_summary = ""
        active_messages = []
        
        # Calculate active word volume
        total_words = sum(len(msg.content.split()) for msg in messages)
        
        if total_words > self.max_active_words:
            # We must partition and summarize the older half of the conversation
            print(f"[INFO] Conversation volume ({total_words} words) exceeds max threshold. Compressing history...")
            
            # Divide messages: keep the last 4 turns active, summarize the rest
            summarize_slice = messages[:-4]
            keep_slice = messages[-4:]
            
            # Generate summary of old conversations
            existing_summary = self._generate_summary(summarize_slice)
            print(f"[SUCCESS] Summarization created: '{existing_summary[:60]}...'")
            
            # Map remaining messages
            for msg in keep_slice:
                active_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        else:
            # Under budget: keep everything active
            for msg in messages:
                active_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return existing_summary, active_messages

    def _generate_summary(self, messages: List[ChatMessage]) -> str:
        """Programmatically compresses a sequence of messages into a concise conceptual summary."""
        topics_discussed = set()
        user_questions_count = 0
        
        for msg in messages:
            content_lower = msg.content.lower()
            if msg.role == "user":
                user_questions_count += 1
                # Detect topics
                if "electrostatics" in content_lower or "electric" in content_lower:
                    topics_discussed.add("Electrostatics")
                if "inertia" in content_lower or "rotational" in content_lower:
                    topics_discussed.add("Rotational Mechanics")
                if "rate" in content_lower or "kinetics" in content_lower:
                    topics_discussed.add("Chemical Kinetics")
                if "integral" in content_lower or "integration" in content_lower:
                    topics_discussed.add("Definite Integration")
                if "complex" in content_lower:
                    topics_discussed.add("Complex Numbers loci")

        topics_str = ", ".join(topics_discussed) if topics_discussed else "general JEE syllabus concepts"
        summary = (
            f"The student had a discussion involving {user_questions_count} questions regarding "
            f"topics such as {topics_str}. The tutor explained core formulations, detailed derivations, "
            f"and helped clear misconceptions."
        )
        return summary

    def add_message(self, session_id: str, role: str, content: str, metadata: dict = None) -> ChatMessage:
        """Appends a new conversation turn to the database."""
        db_message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content
        )
        if metadata:
            db_message.message_metadata = metadata
            
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
