# ==============================================================================
# JEE MENTOR AI - ADAPTIVE LEARNING & INDIVIDUAL PERSONALIZATION ENGINE
# ==============================================================================
import json
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models import AnalyticsMetric, QuestionHistory
from backend.schemas import WeakTopicInfo

class JEEAdaptiveLearningEngine:
    def __init__(self, db: Session):
        self.db = db

    def update_proficiency(self, user_id: str, subject: str, topic: str, is_correct: bool):
        """Updates the running student proficiency of a JEE topic using moving averages."""
        metric = self.db.query(AnalyticsMetric).filter(
            AnalyticsMetric.user_id == user_id,
            AnalyticsMetric.subject == subject,
            AnalyticsMetric.topic == topic
        ).first()
        
        if not metric:
            # Seed a new topic metrics record starting at a 0.5 baseline
            metric = AnalyticsMetric(
                user_id=user_id,
                subject=subject,
                topic=topic,
                questions_attempted=0,
                questions_correct=0,
                running_proficiency=0.5
            )
            self.db.add(metric)
            
        metric.questions_attempted += 1
        if is_correct:
            metric.questions_correct += 1
            
        # Exponential moving average to quickly adapt to learning curves
        # alpha = 0.15 gives high weight to recent attempts while preserving history
        alpha = 0.15
        target = 1.0 if is_correct else 0.0
        metric.running_proficiency = (alpha * target) + ((1.0 - alpha) * metric.running_proficiency)
        
        self.db.commit()
        self.db.refresh(metric)
        print(f"[INFO] Updated {topic} proficiency for User {user_id[-6:]}: {metric.running_proficiency:.2f}")

    def get_weak_topics(self, user_id: str) -> List[WeakTopicInfo]:
        """Scans student records to compile a prioritized list of weak topics and recommendations."""
        metrics = self.db.query(AnalyticsMetric).filter(
            AnalyticsMetric.user_id == user_id
        ).all()
        
        weak_topics_list = []
        for m in metrics:
            accuracy = m.questions_correct / m.questions_attempted if m.questions_attempted > 0 else 0.0
            
            # Highlight topics with low proficiency (below 65% accuracy or running score < 0.6)
            if m.questions_attempted >= 2 and m.running_proficiency < 0.65:
                # Formulate a smart target recommendation linking back to concepts
                rec = self._generate_recommendation(m.subject, m.topic)
                
                weak_topics_list.append(WeakTopicInfo(
                    topic=m.topic,
                    subject=m.subject,
                    accuracy=accuracy,
                    questions_attempted=m.questions_attempted,
                    recommendation=rec
                ))
                
        # Sort by worst proficiency first
        weak_topics_list.sort(key=lambda x: x.accuracy)
        return weak_topics_list

    def _generate_recommendation(self, subject: str, topic: str) -> str:
        """Dynamic text seeder matching target topics with specific textbooks and formulas."""
        if topic == "Electrostatics":
            return "Review Gauss's Law derivations and revise Coulomb's vector notation in NCERT Physics Chapter 1."
        elif topic == "Rotational Mechanics":
            return "Re-derive parallel/perpendicular axis theorem and practice moment of inertia calculations of composite bodies."
        elif topic == "Chemical Kinetics":
            return "Revise integrated first-order rate laws and memorize temperature dependencies in the Arrhenius equation."
        elif topic == "Complex Numbers":
            return "Practice complex loci geometries and Euler conversion formulae in Trigonometry guides."
        elif topic == "Definite Integration":
            return "Revise standard trigonometric symmetry limits and practice King's rule transformations."
        else:
            return f"Revise core formulas for {topic} in your syllabus and practice additional mock questions."

    def determine_difficulty_profile(self, user_id: str, subject: str, topics: List[str]) -> str:
        """Determines the correct target difficulty based on student average proficiency across topics."""
        if not topics:
            return "Medium"
            
        metrics = self.db.query(AnalyticsMetric).filter(
            AnalyticsMetric.user_id == user_id,
            AnalyticsMetric.subject == subject,
            AnalyticsMetric.topic.in_(topics)
        ).all()
        
        if not metrics:
            return "Medium" # Default baseline
            
        avg_prof = sum(m.running_proficiency for m in metrics) / len(metrics)
        
        # Difficulty Progression Curve
        if avg_prof < 0.45:
            return "Easy"     # Seed easier questions to rebuild foundational confidence
        elif avg_prof > 0.75:
            return "Hard"     # Challenge advanced students with IIT JEE Advanced level problems
        else:
            return "Medium"   # Maintain steady standard JEE Main curve

    def generate_personalized_test(self, user_id: str, subject: str, topics: List[str], num_qs: int = 5) -> List[Dict[str, Any]]:
        """Loads and filters high-quality questions matching the student's adaptive difficulty profile."""
        # 1. Determine student difficulty progression target
        target_diff = self.determine_difficulty_profile(user_id, subject, topics)
        print(f"[INFO] Adaptive Engine selected quiz difficulty '{target_diff}' for student based on proficiency.")
        
        # 2. Load matching questions from our synthetic cleaned dataset
        cleaned_dataset_path = "dataset/cleaned_jee_dataset.json"
        try:
            with open(cleaned_dataset_path, "r", encoding="utf-8") as f:
                questions = json.load(f)
        except Exception:
            return [] # Fail gracefully
            
        # 3. Filter list
        filtered_qs = []
        for q in questions:
            if q["subject"].lower() != subject.lower():
                continue
            if topics and q["topic"] not in topics:
                continue
            filtered_qs.append(q)
            
        if not filtered_qs:
            # Fallback to general subjects if strict topic list returns empty
            filtered_qs = [q for q in questions if q["subject"].lower() == subject.lower()]

        # 4. Sort and prioritize target difficulty
        primary_pool = [q for q in filtered_qs if q["difficulty"].lower() == target_diff.lower()]
        secondary_pool = [q for q in filtered_qs if q["difficulty"].lower() != target_diff.lower()]
        
        # Make a combined selection: 70% primary difficulty, 30% other levels for variety
        selected_qs = []
        random.shuffle(primary_pool)
        random.shuffle(secondary_pool)
        
        selected_qs.extend(primary_pool[:int(num_qs * 0.8)])
        remaining = num_qs - len(selected_qs)
        selected_qs.extend(secondary_pool[:remaining])
        
        # In case we still need more questions
        if len(selected_qs) < num_qs:
            extra = [q for q in filtered_qs if q not in selected_qs]
            random.shuffle(extra)
            selected_qs.extend(extra[:num_qs - len(selected_qs)])
            
        # 5. Format output
        output_list = []
        for idx, q in enumerate(selected_qs[:num_qs]):
            output_list.append({
                "id": f"q_{idx+1}_{random.randint(100, 999)}",
                "subject": q["subject"],
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "input": q["input"],
                "tags": q["tags"]
            })
            
        return output_list
