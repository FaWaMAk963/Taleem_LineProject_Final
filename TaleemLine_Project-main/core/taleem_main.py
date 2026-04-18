
# ─────────────────────────────────────────────────────────────────────────────
# taleem_main.py
# ─────────────────────────────────────────────────────────────────────────────
# TaleemLine – FSM Session Agent
#
# Purpose:
#   Implements the complete learning session as a Finite State Machine.
#   Handles language/grade/subject/mode selection and drives the
#   Learning, Test, and Game conversation loops.
#
# FSM states:
#   IDLE → LANG_SELECT → GRADE_SELECT → SUBJECT_SELECT → MODE_SELECT
#        → LEARNING_SESSION | TEST_SESSION | GAME_SESSION
#        → END_SESSION → IDLE
#
# Dual-mode design:
#   GUI mode    – speak_fn and input_fn are injected by AgentThread so all
#                 I/O goes through Qt signals (no blocking the event loop).
#   Console mode – speak_fn / input_fn are None; falls back to voice_generator
#                  and stt_test directly. start_session() drives the full flow.
#
# Key methods:
#   speak()               – output text (injected fn or voice_generator)
#   get_student_input()   – capture voice or keyboard input
#   process_with_ollama() – send student text to brain_processor → Llama3
#   get_system_prompt()   – build mode-aware prompt for the LLM
#   start_session()       – full console session (not used in GUI mode)
#
# Imported by: dial_screen.AgentThread, main_app.run_console
#
# ─────────────────────────────────────────────────────────────────────────────


from transitions import Machine
from io import stt_test
import brain_processor
from io import voice_generator
import os


class TaleemAgent:
    """Main AI Agent with Complete FSM"""
    
    # Complete FSM states from the presentation diagram
    states = [
        'IDLE', 
        'LANG_SELECT', 
        'GRADE_SELECT', 
        'SUBJECT_SELECT', 
        'MODE_SELECT',
        'LEARNING_SESSION',
        'TEST_SESSION',
        'GAME_SESSION',
        'END_SESSION'
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=TaleemAgent.states, initial='IDLE')
        
        # Session data
        self.language = None
        self.grade = None
        self.subject = None
        self.mode = None
        self.score = 0
        self.total_questions = 0
        self.use_keyboard = False  # Fallback if mic fails
        
        # Mappings
        self.languages = {'1': 'English', '2': 'Urdu', '3': 'Pashto'}
        self.grades = {
            '1': 'Grade 1', '2': 'Grade 2', '3': 'Grade 3',
            '4': 'Grade 4', '5': 'Grade 5', '6': 'Grade 6',
            '7': 'Grade 7', '8': 'Grade 8', '9': 'Grade 9',
            '10': 'Grade 10', '11': 'Grade 11', '12': 'Grade 12'
        }
        self.subjects = {
            '1': 'Math', '2': 'English', '3': 'Science', 
            '4': 'Urdu', '5': 'Physics', '6': 'Chemistry'
        }
        
        # All FSM transitions
        self.machine.add_transition('start', 'IDLE', 'LANG_SELECT')
        self.machine.add_transition('select_language', 'LANG_SELECT', 'GRADE_SELECT')
        self.machine.add_transition('select_grade', 'GRADE_SELECT', 'SUBJECT_SELECT')
        self.machine.add_transition('select_subject', 'SUBJECT_SELECT', 'MODE_SELECT')
        self.machine.add_transition('select_learning', 'MODE_SELECT', 'LEARNING_SESSION')
        self.machine.add_transition('select_test', 'MODE_SELECT', 'TEST_SESSION')
        self.machine.add_transition('select_game', 'MODE_SELECT', 'GAME_SESSION')
        self.machine.add_transition('end_session', ['LEARNING_SESSION', 'TEST_SESSION', 'GAME_SESSION'], 'END_SESSION')
        self.machine.add_transition('reset', 'END_SESSION', 'IDLE')
        
    def get_greeting(self):
        """Greeting based on selected language"""
        greetings = {
            'Urdu': "Assalam-o-Alaikum! TaleemLine mein khush aamdeed. Main aapki ustad hoon. Poochna shuru karein.",
            'English': "Hello! Welcome to TaleemLine. I am your teacher. Start asking questions.",
            'Pashto': "Salam! TaleemLine ta kha de yam. Za sta ustaz yam."
        }
        return greetings.get(self.language, "Welcome to TaleemLine!")
    
    def get_language_prompt(self):
        return "Press 1 for English and 2 for Urdu"
    
    def get_grade_prompt(self):
        if self.language == 'Urdu':
            return "Apna grade select karein. 1 se 12 tak dabayein."
        return "Select your grade from 1 to 12"
    
    def get_subject_prompt(self):
        return "1:Math 2:English 3:Science 4:Urdu 5:Physics 6:Chemistry"
    
    def get_mode_prompt(self):
        if self.language == 'Urdu':
            return "4: Sabaq, 5: Test, 6: Game"
        return "4: Learning, 5: Test, 6: Game"
    
    def get_system_prompt(self):
        """Generate prompt based on current mode - THIS USES OLLAMA"""
        if self.state == 'LEARNING_SESSION':
            return (
                f"You are TaleemLine, a friendly tutor for {self.grade} students. "
                f"Subject: {self.subject}. Language: {self.language}. "
                f"Explain topics simply with examples. "
                f"If language is Urdu, respond in Urdu but keep scientific terms in English."
            )
        elif self.state == 'TEST_SESSION':
            return (
                f"You are TaleemLine, conducting a test for {self.grade}. "
                f"Subject: {self.subject}. Language: {self.language}. "
                f"Ask ONE multiple choice question with 4 options (A, B, C, D). "
                f"Wait for answer. Tell if correct with explanation."
            )
        elif self.state == 'GAME_SESSION':
            return (
                f"You are TaleemLine, playing educational game with {self.grade}. "
                f"Subject: {self.subject}. Language: {self.language}. "
                f"Use riddles and fun questions. Give hints if stuck. Celebrate correct answers!"
            )
        return "You are TaleemLine tutor."
    
    def get_student_input(self):
        """Get input from student (voice or keyboard fallback)"""
        if self.use_keyboard:
            return stt_test.recognize_speech_text_input()
        else:
            text = stt_test.recognize_speech()
            if not text.strip():
                print(" Microphone failed. Switching to keyboard input.")
                self.use_keyboard = True
                return stt_test.recognize_speech_text_input()
            return text
    
    def process_with_ollama(self, student_text):
        """Send to Ollama (Llama3) and get response"""
        # Get the correct prompt based on Learning/Test/Game mode
        mode_prompt = self.get_system_prompt()
        
        # Pass it directly to the brain
        response = brain_processor.tutor_brain(student_text, custom_prompt=mode_prompt)
        
        return response
    
    def get_summary(self):
        """Performance summary"""
        if self.mode == 'Test':
            return f"Test complete! Score: {self.score}/{self.total_questions}"
        return f"Session ended! Questions: {self.total_questions}"

    def start_session(self):
        """Main session flow - matches workflow diagram"""
        print("\n" + "="*50)
        print("   TALEEMLINE - Voice Based Learning Agent")
        print("   (Powered by Ollama Llama3)")
        print("="*50 + "\n")
        
        # Check Ollama connection first
        print("Checking Ollama connection...")
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            print("Ollama is running!")
        except:
            print("ERROR: Ollama is not running!")
            print("Please start Ollama first, then run this again.")
            return
        
        # STATE 1: IDLE → LANG_SELECT
        self.start()
        print(f"\n[State: {self.state}]")
        voice_generator.speak_response(self.get_language_prompt())
        
        lang_input = input("Enter language (1-3): ")
        self.language = self.languages.get(lang_input, 'Urdu')
        print(f"✓ Language: {self.language}")
        
        # STATE 2: LANG_SELECT → GRADE_SELECT
        self.select_language()
        print(f"[State: {self.state}]")
        voice_generator.speak_response(self.get_grade_prompt())
        
        grade_input = input("Enter grade (1-12): ")
        self.grade = self.grades.get(grade_input, 'Grade 5')
        print(f"✓ Grade: {self.grade}")
        
        # STATE 3: GRADE_SELECT → SUBJECT_SELECT
        self.select_grade()
        print(f"[State: {self.state}]")
        voice_generator.speak_response(self.get_subject_prompt())
        
        subj_input = input("Enter subject (1-6): ")
        self.subject = self.subjects.get(subj_input, 'Math')
        print(f"✓ Subject: {self.subject}")
        
        # STATE 4: SUBJECT_SELECT → MODE_SELECT
        self.select_subject()
        print(f"[State: {self.state}]")
        voice_generator.speak_response(self.get_mode_prompt())
        
        mode_input = input("Enter mode (4-6): ")
        if mode_input == '5':
            self.select_test()
            self.mode = 'Test'
        elif mode_input == '6':
            self.select_game()
            self.mode = 'Game'
        else:
            self.select_learning()
            self.mode = 'Learning'
        print(f"✓ Mode: {self.mode}")
        
        # STATE 5: Active Session
        print(f"\n[State: {self.state}]")
        greeting = self.get_greeting()
        voice_generator.speak_response(greeting)
        print(f"AI: {greeting}\n")
        
        # Conversation loop
        session_active = True
        while session_active:
            self.total_questions += 1
            
            # Get voice/text input
            student_text = self.get_student_input()
            
            if not student_text.strip():
                continue
            
            # Check for end keywords
            end_words = ['bye', 'allah', 'khuda', 'end', 'stop', 'bas', 'theek hai', 'quit']
            if any(w in student_text.lower() for w in end_words):
                session_active = False
                break
            
            # Send to Ollama for response
            response = self.process_with_ollama(student_text)
            print(f"\nAI: {response}\n")
            
            # Speak response
            voice_generator.speak_response(response)
            
            # Track score for test mode
            if self.mode == 'Test':
                if any(w in response.lower() for w in ['correct', 'sahi', 'theek', 'right']):
                    self.score += 1
        
        # STATE 6: END_SESSION
        self.end_session()
        print(f"\n[State: {self.state}]")
        summary = self.get_summary()
        voice_generator.speak_response(summary)
        print(f"AI: {summary}")
        
        # Back to IDLE
        self.reset()
        print(f"[State: {self.state}]")
        print("\n=== Session Ended ===\n")


if __name__ == "__main__":
    agent = TaleemAgent()
    agent.start_session()