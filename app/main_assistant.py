import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.chatbot import StudyChatbot
from models.study_planner import IntelligentStudyPlanner
from models.productivity_tracker import ProductivityTracker
from typing import Dict, List

class StudyAssistant:
    """Main assistant class integrating all study-related components."""

    def __init__(self):
        print("Initializing Study Assistant...")
        self.chatbot = StudyChatbot()
        self.planner = IntelligentStudyPlanner()
        self.tracker = ProductivityTracker()
        print("✅ Study Assistant ready!")
    
    # === CHATBOT ===
    def ask_question(self, question: str) -> str:
        """Ask a question to the chatbot."""
        return self.chatbot.ask(question)
    # === STUDY PLANNER ===
    def create_personalized_plan(self, student_profile:Dict,
                                 subject:str,
                                 topics:List[str],
                                 deadline_days:int,
                                 difficulty_levels: Dict = None) -> Dict:
        """Create a personalized study plan."""
        plan = self.planner.generate_personalized_plan(
            student_profile = student_profile,
            subject = subject,
            topics = topics,
            deadline_days = deadline_days,
            difficulty_levels = difficulty_levels
        )
        return plan
    def get_plan_summary(self, plan: Dict) -> str:
        """Get a summary of the study plan."""
        return self.planner.get_plan_summary(plan)
    
    # === PRODUCTIVITY TRACKER ===
    def log_session(
        self, 
        subject: str, 
        topic: str, 
        duration: int,
        difficulty: int = None,
        focus: int = None
    ) -> str:
        """Session log karo"""
        result = self.tracker.log_session(
            subject, topic, duration, difficulty, focus
        )
        return result["message"]
    def get_today_stats(self) -> Dict:
        """Get today's study statistics."""
        return self.tracker.get_today_stats()
    def get_study_streak(self) -> int:
        """Get current study streak."""
        return self.tracker.get_study_streak()


#test
if __name__ == "__main__":
    print("="*70)
    print("TESTING INTEGRATED STUDY ASSISTANT")
    print("="*70)
    
    assistant = StudyAssistant()
    
    # Test 1: Chatbot
    print("\n=== Test 1: Chatbot ===")
    answer = assistant.ask_question("What is machine learning?")
    print(f"Answer: {answer[:100]}...")


    # Test 2: Planner
    print("\n=== Test 2: Study Planner ===")
    student_profile = {
        "learning_pace": "moderate",
        "study_pattern": "pomodoro",
        "daily_available_hours": 3,
        "preferred_times": ["morning", "evening"],
        "weak_areas": ["Neural Networks"]
    }
    plan = assistant.create_personalized_plan(
        student_profile=student_profile,
        subject="Machine Learning",
        topics=["Linear Regression", "Neural Networks", "Decision Trees"],
        deadline_days=5,
        difficulty_levels={
            "Linear Regression": "easy",
            "Neural Networks": "hard",
            "Decision Trees": "medium"
        }
    )
    print(assistant.get_plan_summary(plan))

    # Test 3: Tracker
    print("\n=== Test 3: Productivity Tracker ===")
    msg = assistant.log_session("ML", "Linear Regression", 45, 3, 7)
    print(msg)
    
    stats = assistant.get_today_stats()
    print(f"Today's Stats: {stats}")
    
    streak = assistant.get_study_streak()
    print(f"Study Streak: {streak} days")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)