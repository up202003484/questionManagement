import os
import google.generativeai as genai
from google import genai as google_genai
from google.genai import types
import numpy as np
import time
MIN_DELAY_BETWEEN_EMBEDDINGS = 6 # seconds
# High-level API for generation
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Low-level client for embeddings
client = google_genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def embed_text(text: str) -> list[float]:
    time.sleep(MIN_DELAY_BETWEEN_EMBEDDINGS)
    result = client.models.embed_content(
        model="gemini-embedding-exp-03-07",
        contents=text,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
    )
    return result.embeddings[0].values

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    if not vec1 or not vec2:
        return 0.0
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

def find_similar_questions(new_question: str, db_questions: list[dict], threshold: float = 0.85):
    new_vec = embed_text(new_question)
    similar_questions = []

    for item in db_questions:
        existing_vec = item.get("embedding")
        if existing_vec:
            similarity = cosine_similarity(new_vec, existing_vec)
            if similarity >= threshold:
                similar_questions.append((item["question"], similarity))

    return sorted(similar_questions, key=lambda x: -x[1])
