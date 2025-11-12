import os
import re
import pandas as pd
import google.generativeai as genai
from prompts import SYSTEM_INSTRUCTIONS

# ============================================================
# 🔐 1️⃣ Direct Gemini API Key Configuration (local use only)
# ============================================================
# WARNING: This method is not secure for public repos or shared systems.
# Use it only on your personal/local machine.
# ============================================================


genai.configure(api_key="GEMINI_API_KEY")  # ← Replace with your actual Gemini API key


# ============================================================
# 🚀 2️⃣ Initialize Gemini Model
# ============================================================

MODEL_NAME = "models/gemini-2.0-flash"
model = genai.GenerativeModel(model_name=MODEL_NAME)

# ============================================================
# 🧠 3️⃣ Function to Call Gemini
# ============================================================

def _call_gemini(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the generated text.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini Error] {e}"

# ============================================================
# 💬 4️⃣ Convert Natural Language → SQL
# ============================================================

def nl_to_sql(question: str, schema_hint: str, provider: str = "Gemini", model_name: str = MODEL_NAME) -> str:
    """
    Converts a natural language question into SQL using Gemini.
    """
    prompt = f"""{SYSTEM_INSTRUCTIONS}

Schema:
{schema_hint}

Question: {question}
Return only the SQL query inside triple backticks like ```sql```."""
    
    print("🧠 Sending query to Gemini...")
    res = _call_gemini(prompt)

    # Extract SQL code from LLM response
    match = re.search(r"```sql\s*(.*?)```", res, re.DOTALL)
    if match:
        sql_query = match.group(1).strip()
    else:
        sql_query = res.strip()
    
    print("✅ SQL generated successfully.")
    return sql_query

# ============================================================
# 📊 5️⃣ Post-Processing: Generate a Summary of the Result
# ============================================================

def post_answer_enrichment(question: str, df: pd.DataFrame, provider: str = "Gemini", model_name: str = MODEL_NAME) -> str:
    """
    Generates a short summary or observation about the query result.
    """
    if df.empty:
        return f"No results found for: '{question}'."

    num_rows, num_cols = df.shape
    preview_cols = ", ".join(df.columns[:3])
    summary = f"✅ Query returned {num_rows} rows and {num_cols} columns. (Preview columns: {preview_cols})"

    # Optional: Ask Gemini to summarize the table insight
    insight_prompt = f"Question: {question}\nData summary:\n{df.head(5).to_string()}\nProvide a 1-line insight."
    try:
        insight = _call_gemini(insight_prompt)
        summary += f"\n💡 Insight: {insight}"
    except Exception as e:
        summary += f"\n⚠️ Insight generation failed: {e}"

    return summary
