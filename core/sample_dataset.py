# ─────────────────────────────────────────────────────────────────────────────
# FILE: sample_dataset.py
# ─────────────────────────────────────────────────────────────────────────────
# TaleemLine – Curated Educational Dataset
#
# Purpose:
#   Provides a hand-crafted dictionary of questions, explanations, and game
#   prompts organised by Subject → Grade → Mode. Used as a supplementary
#   content bank alongside the live Ollama responses.
#
# Structure:
#   SAMPLE_DATASET[subject][grade][mode] → list of content dicts
#   Subjects: Math, Science, English
#   Grades:   Grade 1, Grade 5  (expandable)
#   Modes:    Learning, Test, Game
#
# Key functions:
#   get_question(grade, subject, mode)      – random question from dataset
#   get_learning_content(grade, subject)    – all learning items for a topic
#   evaluate_answer(question, student_ans)  – True/False correctness check
#
# Imported by: taleem_main.TaleemAgent (optional — for seeded questions)
#
# Part of: TaleemLine Voice Learning Agent
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_DATASET = {
    "Math": {
        "Grade 1": {
            "Learning": [
                {
                    "topic": "Counting",
                    "explanation": "Counting means saying numbers in order. 1, 2, 3, 4, 5...",
                    "example": "Agar aapke paas 3 seb hain, toh aap 1, 2, 3 gin sakte hain."
                },
                {
                    "topic": "Addition",
                    "explanation": "Addition means putting things together. 2 + 3 = 5",
                    "example": "Agar 2 seb aur 3 seb mila dein, toh total 5 seb honge."
                }
            ],
            "Test": [
                {
                    "question": "2 + 3 = ?",
                    "options": ["A) 4", "B) 5", "C) 6", "D) 3"],
                    "answer": "B",
                    "explanation": "2 aur 3 ko jama karne par 5 aata hai."
                },
                {
                    "question": "5 - 2 = ?",
                    "options": ["A) 2", "B) 4", "C) 3", "D) 1"],
                    "answer": "C",
                    "explanation": "5 mein se 2 nikalne par 3 bache."
                }
            ],
            "Game": [
                {
                    "type": "riddle",
                    "question": "Main hoon number 2 aur mera double 4 hai. Main kaun hoon?",
                    "answer": "2",
                    "hint": "Yeh sab se chhota even number hai."
                }
            ]
        },
        "Grade 5": {
            "Learning": [
                {
                    "topic": "Fractions",
                    "explanation": "Fraction means a part of a whole. 1/2 means half.",
                    "example": "Agar pizza ko 2 hisson mein kaato, toh ek hissa 1/2 hoga."
                },
                {
                    "topic": "Multiplication",
                    "explanation": "Multiplication is repeated addition. 3 x 4 means 3+3+3+3 = 12",
                    "example": "3 tables: 3, 6, 9, 12, 15, 18..."
                }
            ],
            "Test": [
                {
                    "question": "1/2 + 1/2 = ?",
                    "options": ["A) 1/4", "B) 1", "C) 2/2", "D) B and C dono"],
                    "answer": "D",
                    "explanation": "1/2 + 1/2 = 2/2 = 1"
                },
                {
                    "question": "7 x 8 = ?",
                    "options": ["A) 54", "B) 56", "C) 58", "D) 48"],
                    "answer": "B",
                    "explanation": "7 x 8 = 56"
                }
            ],
            "Game": [
                {
                    "type": "quick_fire",
                    "question": "5 x 5?",
                    "answer": "25",
                    "hint": "Yeh perfect square hai."
                }
            ]
        }
    },
    "Science": {
        "Grade 5": {
            "Learning": [
                {
                    "topic": "Photosynthesis",
                    "explanation": "Plants make their food using sunlight, water, and CO2. This is called photosynthesis.",
                    "example": "Paudhe dhoop se energy le kar apna khana banate hain."
                },
                {
                    "topic": "Solar System",
                    "explanation": "Our solar system has 8 planets. Earth is the 3rd planet from the Sun.",
                    "example": "Suraj, Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune"
                }
            ],
            "Test": [
                {
                    "question": "Photosynthesis mein kya chahiye?",
                    "options": ["A) Dhoop", "B) Pani", "C) CO2", "D) Sab upar"],
                    "answer": "D",
                    "explanation": "Photosynthesis ke liye dhoop, pani, aur CO2 sab chahiye."
                }
            ],
            "Game": [
                {
                    "type": "riddle",
                    "question": "Main solar system ka sab se bada planet hoon. Main kaun hoon?",
                    "answer": "Jupiter",
                    "hint": "Mere paas 79 moons hain."
                }
            ]
        }
    },
    "English": {
        "Grade 5": {
            "Learning": [
                {
                    "topic": "Nouns",
                    "explanation": "A noun is a word that names a person, place, or thing.",
                    "example": "Ali (person), Karachi (place), book (thing) - sab nouns hain."
                }
            ],
            "Test": [
                {
                    "question": "Which is a noun?",
                    "options": ["A) Run", "B) Happy", "C) School", "D) Quickly"],
                    "answer": "C",
                    "explanation": "School is a place, so it is a noun."
                }
            ],
            "Game": [
                {
                    "type": "word_game",
                    "question": "Name 3 nouns you can see in a classroom.",
                    "answer": "chair, table, board",
                    "hint": "Think of things you can touch."
                }
            ]
        }
    }
}


def get_question(grade, subject, mode):
    """Get a random question from the dataset"""
    try:
        import random
        
        subject_found = SAMPLE_DATASET.get(subject)
        if subject_found is None:
            return None
            
        grade_found = subject_found.get(grade)
        if grade_found is None:
            return None
            
        mode_found = grade_found.get(mode)
        if mode_found is None:
            return None
            
        if len(mode_found) > 0:
            return random.choice(mode_found)
        return None
        
    except Exception as e:
        print(f"Error getting question: {e}")
        return None


def get_learning_content(grade, subject, topic=None):
    """Get learning content for a topic"""
    try:
        subject_found = SAMPLE_DATASET.get(subject)
        if subject_found is None:
            return []
            
        grade_found = subject_found.get(grade)
        if grade_found is None:
            return []
            
        content = grade_found.get("Learning", [])
        
        if topic and content:
            content = [c for c in content if c.get("topic", "").lower() == topic.lower()]
        
        return content
        
    except Exception as e:
        print(f"Error getting content: {e}")
        return []


def evaluate_answer(question, student_answer):
    """Evaluate if student's answer is correct"""
    try:
        if question is None:
            return False
            
        correct_answer = question.get("answer", "")
        
        if not correct_answer:
            return False
        
        # Handle multiple choice
        if correct_answer in ["A", "B", "C", "D"]:
            return student_answer.upper().strip() == correct_answer
        
        # Handle text answers (check if correct answer is in student answer)
        return correct_answer.lower() in student_answer.lower()
        
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return False


# Simple test when run directly
if __name__ == "__main__":
    print("Testing Sample Dataset...")
    print("-" * 30)
    
    q = get_question("Grade 5", "Math", "Test")
    if q:
        print("Question:", q.get("question", ""))
        print("Options:", q.get("options", []))
        print("Answer:", q.get("answer", ""))
    else:
        print("No question found")
    
    print("-" * 30)
    
    content = get_learning_content("Grade 5", "Science")
    for c in content:
        print("Topic:", c.get("topic", ""))
        print("Explanation:", c.get("explanation", ""))
        print()