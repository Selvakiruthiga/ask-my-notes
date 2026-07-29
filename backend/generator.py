import json
import google.generativeai as genai
from backend.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")


def build_prompt(context_chunks: list, question: str) -> str:
    context = "\n\n".join(context_chunks)

    prompt = f"""You are a helpful study assistant. Answer the question using ONLY the context below. 
If the answer is not present in the context, say "This is not covered in the uploaded notes."

Context:
{context}

Question: {question}

Answer:"""

    return prompt


def generate_answer(context_chunks: list, question: str) -> str:
    if not context_chunks:
        return "No relevant content found in your notes for this question."

    prompt = build_prompt(context_chunks, question)
    response = model.generate_content(prompt)

    return response.text


def generate_quiz(context_text: str, num_questions: int = 5) -> list:
    prompt = f"""Based on the following notes, create exactly {num_questions} multiple-choice questions to test understanding.

Return ONLY valid JSON with no markdown formatting, no backticks, no extra text. Use this exact structure:
[
  {{"question": "question text", "options": ["option A", "option B", "option C", "option D"], "answer": "the correct option text exactly as written in options"}}
]

Notes:
{context_text}
"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except Exception:
        return []