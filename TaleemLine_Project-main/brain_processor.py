# This file sends the student’s text to Ollama (Llama3) and gets a response.

import requests
import json

# Default instructions (used if no custom prompt is given)
DEFAULT_INSTRUCTIONS = (
    "You are TaleemLine, a friendly tutor for school students. "
    "You MUST try responding in simple Urdu. "
    "Use english for Scientific terminology "
    "give understanding of the topic in easy way "
    "Always give complete sentences. "
    "Dont give english translation "
)

# takes student input as text argument
# Added custom_prompt parameter so FSM can change the AI's behavior
def tutor_brain(student_text, custom_prompt=None):

    # ollama running locally - fully offline AI
    url = "http://localhost:11434/api/generate"
    
    # Use custom prompt if provided, otherwise use default
    system_instructions = custom_prompt if custom_prompt else DEFAULT_INSTRUCTIONS

    payload = {
        "model": "llama3",   # FAST model
        "prompt": f"{system_instructions}\n\nStudent says: {student_text}",
        "stream": False,
    }

    print("--- Brain is thinking... ---")

    # Python → Ollama → Llama3 → response
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json().get("response", "").strip()

            print("\n--- Teacher's Response ---")
            print(result)

            # ✅ SAFETY CHECK
            if not result or len(result) < 5:
                return "معذرت، مجھے سمجھ نہیں آیا۔ دوبارہ بتائیں۔"

            return result

        else:
            return "معذرت، جواب حاصل نہیں ہو سکا۔"

    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return "کنکشن میں مسئلہ ہے۔"

if __name__ == "__main__":
    # Test the brain
    result = tutor_brain("What is 2+2?")
    print("AI Said:", result)