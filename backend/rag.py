
import re
import requests
from pypdf import PdfReader

OLLAMA_URL = "http://localhost:11434"
CHAT_MODEL = "qwen2.5:1.5b"


def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages).strip()


def split_into_chunks(text, chunk_size=900, overlap=120):
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - overlap

    return chunks


def find_relevant_chunks(question, chunks, top_k=3):
    terms = set(re.findall(r"[a-zA-Z0-9]+", question.lower()))

    stop_words = {
        "what", "is", "the", "a", "an", "if", "does",
        "do", "how", "when", "why", "who", "and",
        "or", "of", "to", "in", "on", "for", "will",
        "happens", "happen", "borrower"
    }

    terms = terms - stop_words

    scored = []

    for chunk in chunks:
        chunk_terms = set(
            re.findall(r"[a-zA-Z0-9]+", chunk.lower())
        )

        score = len(terms.intersection(chunk_terms))

        if score:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [chunk for score, chunk in scored[:top_k]]


def _extract_value(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1).strip(" .,:;")

    return None


def get_direct_answer(question, document_text):
    q = question.lower()

    # 1. Missed EMI / late payment question
    missed_emi_keywords = [
        "misses an emi",
        "missed emi",
        "miss an emi",
        "does not pay the emi",
        "not pay the emi",
        "emi payment",
        "late payment",
        "fails to pay"
    ]

    if any(word in q for word in missed_emi_keywords):
        return None

    # 2. EMI date question
    if any(word in q for word in [
        "first emi date",
        "emi date",
        "first installment date"
    ]):
        value = _extract_value([
            r"(?:first\s+)?emi\s+date\s*(?:is|:|-)?\s*([A-Za-z0-9 ,/-]+)",
            r"first\s+installment\s+date\s*(?:is|:|-)?\s*([A-Za-z0-9 ,/-]+)"
        ], document_text)

        if value:
            return f"முதல் EMI தேதி: {value}"

        return None

    # 3. Monthly EMI amount question
    if any(word in q for word in [
        "monthly emi",
        "emi amount",
        "monthly installment",
        "monthly instalment",
        "மாத தவணை"
    ]) or q.strip() == "what is the emi?":

        value = _extract_value([
            r"(?:monthly\s+)?emi\s*(?:amount)?\s*(?:is|:|-)?\s*(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d+)?)"
        ], document_text)

        if value:
            return f"மாத EMI: ₹{value}"

        return None

    # 4. Loan amount
    if any(word in q for word in [
        "loan amount",
        "approved amount",
        "sanctioned amount",
        "தொகை"
    ]):
        value = _extract_value([
            r"(?:approved|sanctioned|loan)\s+amount\s*(?:is|:|-)?\s*(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d+)?)"
        ], document_text)

        if value:
            return f"கடன் தொகை: ₹{value}"

        return None

    # 5. Interest rate
    if any(word in q for word in [
        "interest rate",
        "rate of interest",
        "வட்டி"
    ]):
        value = _extract_value([
            r"(?:annual\s+)?interest\s+rate\s*(?:is|:|-)?\s*([\d.]+\s*%?)",
            r"([\d.]+\s*%)\s*(?:per annum|p\.a\.)"
        ], document_text)

        if value:
            return f"வட்டி விகிதம்: {value}"

        return None

    # 6. Loan tenure
    if any(word in q for word in [
        "tenure",
        "duration",
        "காலம்"
    ]):
        value = _extract_value([
            r"(?:loan\s+)?tenure\s*(?:is|:|-)?\s*([\w ]+?(?:years?|months?))\b",
            r"repayment\s+period\s*(?:is|:|-)?\s*([\w ]+?(?:years?|months?))\b"
        ], document_text)

        if value:
            return f"கடன் காலம்: {value}"

        return None

    return None


def answer_document_question(question, document_text):
    if not document_text.strip():
        return "PDF-ல் படிக்கக்கூடிய text கிடைக்கவில்லை."

    direct = get_direct_answer(question, document_text)

    if direct:
        return direct

    chunks = split_into_chunks(document_text)
    relevant = find_relevant_chunks(question, chunks)

    if not relevant:
        return "இந்தக் கேள்விக்கான தகவல் PDF-ல் தெளிவாகக் கிடைக்கவில்லை."

    context = "\n\n".join(relevant)

    prompt = f"""
You are a PDF question-answering assistant.

Answer ONLY using the supplied PDF context.

Question: {question}

PDF context:
{context}

Rules:
1. Answer in simple Tamil.
2. Answer only what the question asks.
3. Do not answer a missed-payment question with the EMI amount.
4. If the answer is not present in the context, say:
   "இந்தத் தகவல் PDF-ல் கிடைக்கவில்லை."
5. Never invent facts.
6. Keep the answer short and relevant.
"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": CHAT_MODEL,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "10m",
                "options": {
                    "temperature": 0.1,
                    "num_predict": 180,
                    "num_ctx": 2048
                }
            },
            timeout=180
        )

        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        return answer or "AI response கிடைக்கவில்லை."

    except requests.exceptions.ConnectionError:
        return "Ollama connect ஆகவில்லை. Ollama running-ல் இருக்கிறதா check பண்ணுங்கள்."

    except requests.exceptions.Timeout:
        return "பதில் உருவாக்க நேரம் அதிகமாகிறது. மீண்டும் முயற்சி செய்யுங்கள்."

    except requests.exceptions.RequestException as exc:
        return f"AI Error: {exc}"
