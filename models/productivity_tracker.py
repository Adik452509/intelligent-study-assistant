import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import StudySession, get_db
from datetime import datetime, timedelta
from typing import List, Dict

class ProductivityTracker:
  """Track and analyze study productivity"""

  def __init__(self):
    self.db = get_db()
  def log_session(
      self, 
      subject:str,
      topic:str,
      duration_minutes: int,
      difficulty_rating: int = None,
      focus_level: int = None,
      notes: str =""
  ) -> Dict:
      """Log a study session"""
      session = StudySession(
         subject = subject,
         topic=topic,
         duration_minutes=duration_minutes,
         difficulty_rating=difficulty_rating,
         focus_level=focus_level,
         notes=notes,
         completed=True
      )
      self.db.add(session)
      self.db.commit()

      return {
         "status" : "success",
         "message" : f"✅ Logged {duration_minutes} min session on {topic}!"
      }
  def get_today_stats(self) -> Dict:
     """Get today's study statistics"""
     today_start = datetime.now().replace(hour=0, minute=0, second=0)
     sessions = self.db.query(StudySession).filter(StudySession.date >= today_start).all()

     if not sessions:
         return {
             "total_hours": 0,
                "sessions": 0,
                "subjects": []
         }
     total_minutes = sum(s.duration_minutes for s in sessions)
     subjects = list(set(s.subject for s in sessions))

     return {
        "total_hours": round(total_minutes / 60, 2),
        "sessions": len(sessions),
        "subjects": subjects
     }
  def get_study_streak(self) -> int:
     """Calculate current study streak"""
     current_date = datetime.now().replace(hour=0, minute=0, second=0)
     streak = 0
     check_date = current_date

     for _ in range(365):
        day_start = check_date
        day_end = check_date + timedelta(days=1)

        count = self.db.query(StudySession).filter(
            StudySession.date >= day_start,
            StudySession.date < day_end
        ).count()

        if count>0:
           streak +=1
           check_date -= timedelta(days=1)
        else:
           break
     return streak

#test
if __name__ == "__main__":
   tracker = ProductivityTracker()

   #log session
   result = tracker.log_session(
      "Machine Learning",
      "Linear Regression",
      60,
      difficulty_rating=4,
      focus_level=8,
   )  
   print(result["message"])

   #get stats
   stats = tracker.get_today_stats()
   print(f"Today: {stats['total_hours']}h, {stats['sessions']} sessions")

   #get streak
   streak = tracker.get_study_streak()
   print(f"Streak: {streak} days")

