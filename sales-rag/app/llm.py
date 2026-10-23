import os
from typing import List, Dict, Any
from groq import Groq

MODELS_TO_TRY = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "groq/compound",
    "groq/compound-mini",
    "openai/gpt-oss-20b"
]

def generate_rag_answer(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Generates a natural, accurate, and grounded answer using Groq LLMs
    based strictly on retrieved technical document chunks.
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    context_blocks = []
    for idx, c in enumerate(retrieved_chunks):
        doc = c.get("document", "Document")
        page = c.get("page", 1)
        prod = c.get("product_family", "Lighting Product")
        ctype = c.get("type", "Specification")
        text = c.get("text", "")
        context_blocks.append(
            f"--- Context Source {idx+1}: [{prod}] (File: {doc}, Page {page}, Section: {ctype}) ---\n{text}"
        )

    context_text = "\n\n".join(context_blocks)
    fallback_answer = retrieved_chunks[0]["text"] if retrieved_chunks else "Specification details not found in approved catalog."

    if not api_key:
        return fallback_answer

    try:
        client = Groq(api_key=api_key, timeout=8.0)
    except Exception:
        return fallback_answer

    prompt = f"""You are an expert technical sales engineer for commercial and architectural lighting products.
Answer the customer's question directly, accurately, and concisely using ONLY the provided document context below.

Customer Question:
{query}

Approved Technical Document Context:
{context_text}

Guidelines:
1. Provide a direct, factual answer with exact numerical values and proper units:
   - Beam Angles: in degrees (e.g., 15°, 24°, 36°, 50°, 90°, 120°).
   - CCT (Color Temperature): in Kelvin (e.g., 2700K, 3000K, 4000K, 5700K, 6500K).
   - Wattage / Power: in Watts (e.g., 3W, 5W, 7W, 10W, 12W, 18W, 20W, 24W, 30W, 36W).
   - Luminous Flux: in lumens (e.g., 400 lm, 800 lm, 1,600 lm).
   - Voltage: in Volts (e.g., AC100-277V, AC220-240V, AC85-265V).
   - Ingress / Impact: IP rating (e.g., IP20, IP40) & IK rating (e.g., IK02).
   - Lifespan & Warranty: (e.g., 50,000 hours @ L70, Lifetime*, 3 Year, 5 Year).
   - Dimming / Controls: (e.g., TRIAC, DALI, 0-10V).
2. For questions asking for descriptions, applications, features, or product comparisons, summarize the details accurately from the context.
3. If the context does not contain the answer, respond: "The requested specification is not mentioned in the provided product documentation."
"""

    for model_id in MODELS_TO_TRY:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise technical lighting specialist. You only state facts directly supported by the context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.0,
                max_tokens=300
            )
            answer = response.choices[0].message.content.strip()
            if answer:
                return answer
        except Exception:
            continue

    return fallback_answer