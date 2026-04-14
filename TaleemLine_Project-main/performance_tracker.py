# Performance Tracking Module
# Tracks student progress across sessions

import json
import os
from datetime import datetime


class PerformanceTracker:
    def __init__(self, student_id="default_student"):
        self.student_id = student_id
        self.data_file = f"performance_{student_id}.json"
        self.current_session = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'language': None,
            'grade': None,
            'subject': None,
            'mode': None,
            'questions_asked': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'topics_covered': [],
            'duration_seconds': 0
        }
        self.history = self.load_history()

    def start_session(self, language, grade, subject, mode):
        """Initialize a new session"""
        self.current_session['language'] = language
        self.current_session['grade'] = grade
        self.current_session['subject'] = subject
        self.current_session['mode'] = mode

    def record_question(self, question, is_correct=False):
        """Record a question asked and whether answered correctly"""
        self.current_session['questions_asked'] += 1
        if is_correct:
            self.current_session['correct_answers'] += 1
        else:
            self.current_session['wrong_answers'] += 1

    def add_topic(self, topic):
        """Add a topic covered in this session"""
        if topic not in self.current_session['topics_covered']:
            self.current_session['topics_covered'].append(topic)

    def set_duration(self, seconds):
        """Set session duration"""
        self.current_session['duration_seconds'] = seconds

    def end_session(self):
        """Save current session to history"""
        self.history.append(self.current_session)
        self.save_history()
        return self.get_session_summary()

    def get_session_summary(self):
        """Get summary of current session"""
        total = self.current_session['questions_asked']
        correct = self.current_session['correct_answers']
        
        if total > 0:
            accuracy = (correct / total) * 100
        else:
            accuracy = 0

        summary = {
            'total_questions': total,
            'correct': correct,
            'wrong': self.current_session['wrong_answers'],
            'accuracy': round(accuracy, 1),
            'topics': self.current_session['topics_covered'],
            'duration': self.current_session['duration_seconds']
        }
        return summary

    def get_overall_stats(self):
        """Get overall statistics across all sessions"""
        if not self.history:
            return {"total_sessions": 0}
        
        total_sessions = len(self.history)
        total_questions = sum(s['questions_asked'] for s in self.history)
        total_correct = sum(s['correct_answers'] for s in self.history)
        
        # Most studied subject
        subjects = [s['subject'] for s in self.history if s['subject']]
        favorite_subject = max(set(subjects), key=subjects.count) if subjects else None
        
        return {
            'total_sessions': total_sessions,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'overall_accuracy': round((total_correct/total_questions)*100, 1) if total_questions > 0 else 0,
            'favorite_subject': favorite_subject,
            'last_session': self.history[-1]['date'] if self.history else None
        }

    def get_progress_report(self):
        """Generate a text progress report"""
        session_summary = self.get_session_summary()
        overall_stats = self.get_overall_stats()
        
        report = f"""
═══════════════════════════════════════
        TALEEMLINE PROGRESS REPORT
═══════════════════════════════════════

📊 Current Session:
   • Questions: {session_summary['total_questions']}
   • Correct: {session_summary['correct']}
   • Accuracy: {session_summary['accuracy']}%
   • Topics: {', '.join(session_summary['topics']) if session_summary['topics'] else 'None'}
   • Duration: {session_summary['duration']} seconds

📈 Overall Statistics:
   • Total Sessions: {overall_stats['total_sessions']}
   • Total Questions: {overall_stats['total_questions']}
   • Overall Accuracy: {overall_stats['overall_accuracy']}%
   • Favorite Subject: {overall_stats['favorite_subject'] or 'N/A'}

═══════════════════════════════════════
"""
        return report

    def load_history(self):
        """Load session history from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        """Save session history to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Test the tracker
    tracker = PerformanceTracker("student_001")
    tracker.start_session("Urdu", "Grade 5", "Math", "Test")
    tracker.record_question("What is 2+2?", is_correct=True)
    tracker.record_question("What is 5x5?", is_correct=True)
    tracker.record_question("What is 10/2?", is_correct=False)
    tracker.add_topic("Addition")
    tracker.add_topic("Multiplication")
    tracker.set_duration(300)
    
    summary = tracker.end_session()
    print(tracker.get_progress_report())