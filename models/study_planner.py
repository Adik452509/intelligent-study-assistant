from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class IntelligentStudyPlanner:
    """AI-powered study planner that adapts to individual students"""
    
    def __init__(self):
        # Different learning paces
        self.learning_pace = {
            "slow": {"hours_per_topic": 4, "revision_ratio": 0.4},
            "moderate": {"hours_per_topic": 2.5, "revision_ratio": 0.3},
            "fast": {"hours_per_topic": 1.5, "revision_ratio": 0.2}
        }
        
        # Study session patterns
        self.session_patterns = {
            "pomodoro": {"session_length": 25, "break_length": 5, "long_break": 15},
            "deep_work": {"session_length": 90, "break_length": 20, "long_break": 30},
            "short_burst": {"session_length": 15, "break_length": 5, "long_break": 10}
        }
    
    def generate_personalized_plan(
        self,
        student_profile: Dict,
        subject: str,
        topics: List[str],
        deadline_days: int,
        difficulty_levels: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Generate a study plan personalized to the student
        
        Args:
            student_profile: Student's learning preferences
            subject: Subject name
            topics: List of topics to cover
            deadline_days: Days until deadline
            difficulty_levels: Optional dict like {"topic1": "hard", "topic2": "easy"}
        """
        
        # Extract student preferences
        pace = student_profile.get("learning_pace", "moderate")
        pattern = student_profile.get("study_pattern", "pomodoro")
        daily_hours = student_profile.get("daily_available_hours", 3)
        preferred_times = student_profile.get("preferred_times", ["evening"])
        weak_areas = student_profile.get("weak_areas", [])
        
        # Calculate time needed for each topic
        topic_time_allocation = self._calculate_topic_times(
            topics, 
            pace, 
            weak_areas, 
            difficulty_levels
        )
        
        # Total hours needed
        total_hours_needed = sum(topic_time_allocation.values())
        total_hours_available = deadline_days * daily_hours
        
        # Add revision time
        revision_ratio = self.learning_pace[pace]["revision_ratio"]
        total_with_revision = total_hours_needed * (1 + revision_ratio)
        
        # Check feasibility
        if total_with_revision > total_hours_available:
            return self._generate_infeasible_response(
                total_with_revision,
                total_hours_available,
                deadline_days,
                daily_hours
            )
        
        # Generate day-by-day plan
        daily_plan = self._create_daily_schedule(
            topics,
            topic_time_allocation,
            deadline_days,
            daily_hours,
            preferred_times,
            pattern,
            weak_areas,
            subject
        )
        
        return {
            "feasible": True,
            "subject": subject,
            "student_profile": student_profile,
            "total_topics": len(topics),
            "deadline": (datetime.now() + timedelta(days=deadline_days)).strftime("%Y-%m-%d"),
            "total_hours_needed": round(total_with_revision, 1),
            "total_hours_available": total_hours_available,
            "buffer_hours": round(total_hours_available - total_with_revision, 1),
            "daily_plan": daily_plan,
            "study_tips": self._generate_personalized_tips(student_profile, topics)
        }
    
    def _calculate_topic_times(
        self,
        topics: List[str],
        pace: str,
        weak_areas: List[str],
        difficulty_levels: Optional[Dict] = None
    ) -> Dict[str, float]:
        """Calculate time needed for each topic based on student's pace and weak areas"""
        
        base_hours = self.learning_pace[pace]["hours_per_topic"]
        topic_times = {}
        
        for topic in topics:
            hours = base_hours
            
            # Add extra time for weak areas
            if topic in weak_areas:
                hours *= 1.5
            
            # Adjust based on difficulty
            if difficulty_levels and topic in difficulty_levels:
                diff = difficulty_levels[topic]
                if diff == "hard":
                    hours *= 1.3
                elif diff == "easy":
                    hours *= 0.7
            
            topic_times[topic] = round(hours, 1)
        
        return topic_times
    
    def _create_daily_schedule(
        self,
        topics: List[str],
        topic_times: Dict[str, float],
        deadline_days: int,
        daily_hours: int,
        preferred_times: List[str],
        pattern: str,
        weak_areas: List[str],
        subject: str
    ) -> List[Dict]:
        """Create detailed daily schedule with study sessions"""
        
        daily_plan = []
        current_date = datetime.now()
        
        # Get session pattern
        session_info = self.session_patterns[pattern]
        
        # Distribute topics across days
        topics_queue = list(topics)
        revision_days = max(2, int(deadline_days * 0.2))
        study_days = deadline_days - revision_days
        
        day_num = 0
        topic_progress = {topic: 0 for topic in topics}
        
        # Study phase
        for day in range(study_days):
            day_num += 1
            date = (current_date + timedelta(days=day)).strftime("%Y-%m-%d")
            
            day_schedule = {
                "day": day_num,
                "date": date,
                "phase": "Learning",
                "preferred_time": preferred_times[day % len(preferred_times)],
                "sessions": [],
                "total_hours": 0
            }
            
            hours_remaining = daily_hours
            
            # Schedule study sessions for the day
            while hours_remaining > 0 and topics_queue:
                current_topic = topics_queue[0]
                time_needed = topic_times[current_topic] - topic_progress[current_topic]
                
                # Determine session length
                session_hours = min(
                    session_info["session_length"] / 60,
                    hours_remaining,
                    time_needed
                )
                
                if session_hours > 0.1:
                    # Create session
                    session = {
                        "topic": current_topic,
                        "duration_minutes": int(session_hours * 60),
                        "activities": self._generate_activities(
                            current_topic,
                            session_hours,
                            current_topic in weak_areas
                        ),
                        "is_weak_area": current_topic in weak_areas
                    }
                    
                    day_schedule["sessions"].append(session)
                    day_schedule["total_hours"] += session_hours
                    
                    topic_progress[current_topic] += session_hours
                    hours_remaining -= session_hours
                    
                    # Add break
                    if hours_remaining > 0:
                        hours_remaining -= session_info["break_length"] / 60
                    
                    # If topic complete, move to next
                    if topic_progress[current_topic] >= topic_times[current_topic]:
                        topics_queue.pop(0)
                else:
                    topics_queue.pop(0)
            
            daily_plan.append(day_schedule)
        
        # Revision phase
        for day in range(revision_days):
            day_num += 1
            date = (current_date + timedelta(days=study_days + day)).strftime("%Y-%m-%d")
            
            if day == revision_days - 1:
                phase = "Final Review & Mock Test"
            elif day == revision_days - 2:
                phase = "Intensive Revision"
            else:
                phase = "Revision"
            
            day_schedule = {
                "day": day_num,
                "date": date,
                "phase": phase,
                "preferred_time": preferred_times[day % len(preferred_times)],
                "sessions": self._generate_revision_sessions(
                    topics, weak_areas, daily_hours, phase
                ),
                "total_hours": daily_hours
            }
            
            daily_plan.append(day_schedule)
        
        return daily_plan
    
    def _generate_activities(
        self,
        topic: str,
        duration_hours: float,
        is_weak: bool
    ) -> List[str]:
        """Generate specific activities for a study session"""
        
        activities = []
        
        if duration_hours >= 1.5:
            activities = [
                f"Watch tutorial/lecture on {topic} (30 min)",
                f"Read textbook chapter on {topic} (25 min)",
                f"Take notes and summarize key concepts (20 min)",
                f"Practice problems/examples (25 min)",
                f"Create flashcards for {topic} (10 min)"
            ]
        elif duration_hours >= 1:
            activities = [
                f"Study {topic} theory (30 min)",
                f"Practice 3-5 problems on {topic} (20 min)",
                f"Review and summarize (10 min)"
            ]
        else:
            activities = [
                f"Quick review of {topic} concepts",
                f"Practice 2-3 problems"
            ]
        
        if is_weak:
            activities.append(f"Extra focus needed - spend more time on examples")
        
        return activities
    
    def _generate_revision_sessions(
        self,
        topics: List[str],
        weak_areas: List[str],
        daily_hours: int,
        phase: str
    ) -> List[Dict]:
        """Generate revision sessions"""
        
        if phase == "Final Review & Mock Test":
            return [
                {
                    "topic": "All Topics",
                    "duration_minutes": int(daily_hours * 30),
                    "activities": [
                        "Quick review of all topics (1 hour)",
                        "Take full mock test (1.5 hours)",
                        "Review mistakes and weak areas (30 min)"
                    ]
                }
            ]
        elif phase == "Intensive Revision":
            sessions = []
            time_per_topic = (daily_hours * 60) // max(len(weak_areas), 1)
            
            for topic in weak_areas:
                sessions.append({
                    "topic": topic,
                    "duration_minutes": time_per_topic,
                    "activities": [
                        f"Intensive review of {topic}",
                        f"Practice difficult problems on {topic}",
                        "Clarify doubts"
                    ],
                    "is_weak_area": True
                })
            
            return sessions
        else:
            sessions = []
            time_per_topic = (daily_hours * 60) // len(topics)
            
            for topic in topics:
                sessions.append({
                    "topic": topic,
                    "duration_minutes": time_per_topic,
                    "activities": [
                        f"Review {topic} notes",
                        f"Practice mixed problems"
                    ]
                })
            
            return sessions
    
    def _generate_infeasible_response(
        self,
        needed: float,
        available: float,
        days: int,
        daily_hours: int
    ) -> Dict:
        """Generate response when plan is not feasible"""
        
        hours_short = needed - available
        suggestions = []
        
        # Option 1: Increase daily hours
        new_daily_hours = needed / days
        if new_daily_hours <= 12:
            suggestions.append(
                f"Study {new_daily_hours:.1f} hours per day instead of {daily_hours}"
            )
        
        # Option 2: Extend deadline
        new_deadline = int(needed / daily_hours) + 1
        suggestions.append(
            f"Extend deadline by {new_deadline - days} days"
        )
        
        # Option 3: Increase learning pace
        suggestions.append(
            "Consider switching to 'fast' learning pace if you're confident"
        )
        
        return {
            "feasible": False,
            "message": f"Not enough time! Need {needed:.1f} hours but only have {available:.1f} hours.",
            "hours_short": round(hours_short, 1),
            "suggestions": suggestions
        }
    
    def _generate_personalized_tips(
        self,
        profile: Dict,
        topics: List[str]
    ) -> List[str]:
        """Generate personalized study tips"""
        
        tips = []
        
        pace = profile.get("learning_pace", "moderate")
        pattern = profile.get("study_pattern", "pomodoro")
        weak_areas = profile.get("weak_areas", [])
        
        if pace == "slow":
            tips.append("Take your time - deep understanding beats speed")
            tips.append("Make detailed notes and revisit them daily")
        elif pace == "fast":
            tips.append("You learn quickly - but don't skip revision!")
            tips.append("Challenge yourself with advanced problems")
        
        if pattern == "pomodoro":
            tips.append("Use a Pomodoro timer app to stay on track")
        elif pattern == "deep_work":
            tips.append("Eliminate all distractions during 90-min sessions")
        
        if weak_areas:
            tips.append(f"Extra focus on: {', '.join(weak_areas[:3])}")
            tips.append("Consider finding a study partner for weak topics")
        
        tips.append("Stay hydrated and take regular breaks")
        tips.append("Get 7-8 hours of sleep for better retention")
        
        return tips
    
    def get_plan_summary(self, plan: Dict) -> str:
        """Convert plan to readable summary"""
        
        if not plan.get("feasible"):
            summary = f"{plan['message']}\n\n"
            summary += "Suggestions:\n"
            for i, suggestion in enumerate(plan['suggestions'], 1):
                summary += f"  {i}. {suggestion}\n"
            return summary
        
        summary = f"""
PERSONALIZED STUDY PLAN FOR {plan['subject'].upper()}

OVERVIEW:
  Total Topics: {plan['total_topics']}
  Deadline: {plan['deadline']}
  Total Hours Needed: {plan['total_hours_needed']}h
  Buffer Time: {plan['buffer_hours']}h
  Learning Pace: {plan['student_profile'].get('learning_pace', 'moderate').title()}
  Study Pattern: {plan['student_profile'].get('study_pattern', 'pomodoro').title()}

DAILY SCHEDULE:
"""
        
        for day in plan['daily_plan']:
            summary += f"\nDay {day['day']} ({day['date']}) - {day['phase']}\n"
            summary += f"  Preferred Time: {day['preferred_time'].title()}\n"
            summary += f"  Total Hours: {day['total_hours']:.1f}h\n"
            
            if day['sessions']:
                summary += "  Sessions:\n"
                for i, session in enumerate(day['sessions'][:3], 1):
                    weak_flag = " (Weak Area)" if session.get('is_weak_area') else ""
                    summary += f"    {i}. {session['topic']}{weak_flag} ({session['duration_minutes']} min)\n"
                        
                if len(day['sessions']) > 3:
                    summary += f"    ... and {len(day['sessions']) - 3} more sessions\n"
        
        summary += "\n\nPERSONALIZED TIPS:\n"
        for tip in plan['study_tips']:
            summary += f"  - {tip}\n"
        
        return summary


# Example usage and testing
if __name__ == "__main__":
    planner = IntelligentStudyPlanner()
    
    # Student profile
    student = {
        "learning_pace": "moderate",
        "study_pattern": "pomodoro",
        "daily_available_hours": 4,
        "preferred_times": ["morning", "evening"],
        "weak_areas": ["Neural Networks", "Backpropagation"],
        "break_preference": "frequent"
    }
    
    # Topic difficulty levels
    difficulties = {
        "Linear Regression": "easy",
        "Logistic Regression": "easy",
        "Decision Trees": "medium",
        "Neural Networks": "hard",
        "Backpropagation": "hard",
        "CNN": "hard"
    }
    
    # Generate plan
    print("Generating personalized study plan...")
    plan = planner.generate_personalized_plan(
        student_profile=student,
        subject="Deep Learning",
        topics=["Linear Regression", "Logistic Regression", "Decision Trees", 
                "Neural Networks", "Backpropagation", "CNN"],
        deadline_days=10,
        difficulty_levels=difficulties
    )
    
    print("\n" + "="*70)
    print(planner.get_plan_summary(plan))
    print("="*70)