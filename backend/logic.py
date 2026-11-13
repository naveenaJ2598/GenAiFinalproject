
import re
import requests

OLLAMA_URL = "http://localhost:11434"
CHAT_MODEL = "qwen2.5:1.5b"


# --------------------------------------------------
# VOCABULARY
# --------------------------------------------------

VOCABULARY = {
    "go": ("போ / செல்", "ஒரு இடத்திற்குச் செல்வது"),
    "going": ("போகிறேன்", "செல்லும் செயல்"),
    "went": ("சென்றேன்", "கடந்த காலத்தில் சென்ற செயல்"),
    "school": ("பள்ளி", "மாணவர்கள் படிக்கும் இடம்"),
    "college": ("கல்லூரி", "உயர்கல்வி படிக்கும் இடம்"),
    "work": ("வேலை", "ஒரு பணியைச் செய்வது"),
    "eat": ("சாப்பிடு", "உணவை உட்கொள்வது"),
    "happy": ("மகிழ்ச்சியாக", "சந்தோஷமாக இருப்பது"),
    "learn": ("கற்றுக்கொள்", "புதிய அறிவைப் பெறுவது"),
    "beautiful": ("அழகான", "பார்ப்பதற்கு அழகாக இருப்பது"),
    "important": ("முக்கியமான", "அவசியமான"),
    "friend": ("நண்பர்", "நம்முடன் பழகும் நபர்"),
    "improve": ("மேம்படுத்து", "ஒரு விஷயத்தை இன்னும் சிறப்பாக்குவது"),
    "english": ("ஆங்கிலம்", "ஒரு மொழி"),
    "food": ("உணவு", "சாப்பிடும் பொருள்"),
    "rice": ("அரிசி / சாதம்", "உணவாக சாப்பிடப்படும் பொருள்"),
}


# --------------------------------------------------
# TEXT HELPERS
# --------------------------------------------------

def _normalise(sentence):
    text = sentence.strip().lower()
    text = re.sub(r"[.!?]+$", "", text)
    return re.sub(r"\s+", " ", text).strip()


def get_vocabulary(sentence):
    words = re.findall(r"[a-zA-Z']+", sentence.lower())

    for word in words:
        if word in VOCABULARY:
            tamil_word, meaning = VOCABULARY[word]

            return (
                f"{word} — {tamil_word}\n"
                f"தமிழ் விளக்கம்: {meaning}"
            )

    return "இந்த sentence-க்கு vocabulary meaning dictionary-ல் இல்லை."


def _format_result(correct, explanation, natural, word):

    tamil_word, meaning = VOCABULARY.get(
        word,
        ("அர்த்தம் கிடைக்கவில்லை", "")
    )

    return (
        f"1. Correct English:\n{correct}\n\n"
        f"2. Tamil Explanation:\n{explanation}\n\n"
        f"3. Natural English:\n{natural}\n\n"
        f"4. Vocabulary:\n"
        f"{word} — {tamil_word}\n"
        f"தமிழ் விளக்கம்: {meaning}"
    )


# --------------------------------------------------
# ALREADY CORRECT SENTENCES
# --------------------------------------------------

def check_already_correct_sentence(sentence):

    text = _normalise(sentence)

    known = {

        "i am very happy today": (
            "I am very happy today.",
            "இந்த வாக்கியம் சரியாக உள்ளது. "
            "Grammar correction தேவையில்லை.\n"
            "- I am = நான் இருக்கிறேன்\n"
            "- very happy = மிகவும் மகிழ்ச்சியாக\n"
            "- today = இன்று",
            "I feel really happy today.",
            "happy",
        ),

        "i want to improve my english": (
            "I want to improve my English.",
            "இந்த வாக்கியம் சரியாக உள்ளது.\n"
            "- I want = நான் விரும்புகிறேன்\n"
            "- to improve = மேம்படுத்த\n"
            "- my English = என்னுடைய ஆங்கிலத்தை",
            "I would like to get better at English.",
            "improve",
        ),

        "i eat food every day": (
            "I eat food every day.",
            "இந்த வாக்கியம் சரியாக உள்ளது.\n"
            "- I eat = நான் சாப்பிடுகிறேன்\n"
            "- food = உணவு\n"
            "- every day = ஒவ்வொரு நாளும்",
            "I have meals every day.",
            "food",
        ),
    }

    item = known.get(text)

    if not item:
        return None

    return _format_result(*item)


# --------------------------------------------------
# RULE BASED GRAMMAR CORRECTION
# --------------------------------------------------

def rule_based_correction(sentence):

    text = _normalise(sentence)

    # Rule 1:
    # I am go to school yesterday.

    match = re.fullmatch(
        r"i am go(?:ing)? to (school|college|work) yesterday",
        text
    )

    if match:

        destination = match.group(1)

        explanation = (
            "இந்த வாக்கியத்தில் 'yesterday' என்பது "
            "நேற்று நடந்த செயலைக் குறிக்கிறது.\n\n"
            "அதனால் Present Tense ஆன 'am going' "
            "பயன்படுத்தாமல் Past Tense ஆன 'went' "
            "பயன்படுத்த வேண்டும்.\n\n"
            "'I went' = நான் சென்றேன்."
        )

        return _format_result(
            f"I went to {destination} yesterday.",
            explanation,
            f"Yesterday, I attended {destination}."
            if destination == "school"
            else f"Yesterday, I went to {destination}.",
            "go"
        )

    # Rule 2:
    # I go to school yesterday.

    match = re.fullmatch(
        r"i go to (school|college|work) yesterday",
        text
    )

    if match:

        destination = match.group(1)

        explanation = (
            "'Yesterday' என்பது கடந்த காலத்தைக் குறிக்கிறது.\n"
            "எனவே 'go' என்பதற்குப் பதிலாக "
            "அதன் Past Tense வடிவமான 'went' பயன்படுத்த வேண்டும்."
        )

        return _format_result(
            f"I went to {destination} yesterday.",
            explanation,
            f"Yesterday, I attended {destination}."
            if destination == "school"
            else f"Yesterday, I went to {destination}.",
            "go"
        )

    # Rule 3:
    # I am go to school.

    match = re.fullmatch(
        r"i am go to (school|college|work)",
        text
    )

    if match:

        destination = match.group(1)

        explanation = (
            "'I am'க்குப் பிறகு இந்த sentence-ல் "
            "'going' பயன்படுத்த வேண்டும்.\n\n"
            "Present Continuous Tense அமைப்பு:\n"
            "am / is / are + verb-ing."
        )

        return _format_result(
            f"I am going to {destination}.",
            explanation,
            f"I'm on my way to {destination}.",
            "going"
        )

    # Rule 4:
    # He go to school every day.

    match = re.fullmatch(
        r"(he|she) go(?:es)? to school every day",
        text
    )

    if match:

        subject = match.group(1).capitalize()

        explanation = (
            "Present Simple Tense-ல் He அல்லது She "
            "போன்ற subject வந்தால் verb-க்கு பொதுவாக "
            "'s' அல்லது 'es' சேர்க்க வேண்டும்.\n\n"
            "அதனால் 'go' என்பதற்குப் பதிலாக 'goes' பயன்படுத்த வேண்டும்."
        )

        return _format_result(
            f"{subject} goes to school every day.",
            explanation,
            f"{subject} attends school every day.",
            "school"
        )

    # Rule 5:
    # He eat rice every day.
    # She eat rice every day.
    # He eats rice every day.

    match = re.fullmatch(
        r"(he|she|it) (eat|play|work|read|drink|watch|study|like|go)"
        r"(?:s|es)? (.+) every day",
        text
    )

    if match:

        subject = match.group(1).capitalize()
        verb = match.group(2)
        object_text = match.group(3)

        # Simple Present verb forms
        verb_forms = {
            "eat": "eats",
            "play": "plays",
            "work": "works",
            "read": "reads",
            "drink": "drinks",
            "watch": "watches",
            "study": "studies",
            "like": "likes",
            "go": "goes",
        }

        correct_verb = verb_forms[verb]

        correct = (
            f"{subject} {correct_verb} "
            f"{object_text} every day."
        )

        explanation = (
            f"'{subject}' என்பது singular subject.\n\n"
            "Simple Present Tense-ல் He, She, It "
            "போன்ற subjects வந்தால் verb-ன் வடிவத்தை "
            "மாற்ற வேண்டும்.\n\n"
            f"அதனால் '{verb}' என்பதற்குப் பதிலாக "
            f"'{correct_verb}' பயன்படுத்த வேண்டும்.\n\n"
            f"{subject} + {correct_verb} = சரியான அமைப்பு."
        )

        if verb == "eat":
            natural = (
                f"{subject} has {object_text} every day."
            )
        elif verb == "go":
            natural = (
                f"{subject} attends {object_text.replace('to ', '')} every day."
            )
        else:
            natural = correct

        return _format_result(
            correct,
            explanation,
            natural,
            verb
        )

    return None


# --------------------------------------------------
# OLLAMA AI
# --------------------------------------------------

def ask_ollama(user_text):

    prompt = f"""
You are an English grammar teacher for a Tamil-speaking beginner.

Student sentence: {user_text}

Return exactly these four sections:

1. Correct English:
2. Tamil Explanation:
3. Natural English:
4. Vocabulary:

Strict instructions:

- Correct the student's grammar accurately.
- Tamil Explanation MUST be written in simple,
  grammatically correct Tamil.
- Explain why the original sentence is wrong.
- Explain the relevant grammar rule in Tamil.
- Never generate unrelated Tamil sentences.
- Natural English MUST be a valid English sentence.
- Natural English must preserve the original meaning.
- Do not write Tamil inside Natural English.
- Vocabulary must contain one English word
  from the student's original sentence and its Tamil meaning.
- If the sentence is already correct, clearly say so.
- Do not invent information.
- Keep the answer short and accurate.

Return only the four sections.
"""

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
                "num_ctx": 2048,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json().get("response", "").strip()


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def ask_lingua_mate(user_text):

    if not user_text or not user_text.strip():
        return "Please enter an English sentence."

    try:

        # First check known correct sentences
        known = check_already_correct_sentence(user_text)

        if known:
            return known

        # Next use deterministic grammar rules
        rule_result = rule_based_correction(user_text)

        if rule_result:
            return rule_result

        # Other sentences go to Ollama
        answer = ask_ollama(user_text)

        if not answer:
            return "AI response கிடைக்கவில்லை. Please try again."

        # Remove model-generated vocabulary section
        if "4. Vocabulary:" in answer:
            answer = answer.split("4. Vocabulary:")[0].strip()

        vocabulary = get_vocabulary(user_text)

        return (
            f"{answer}\n\n"
            f"4. Vocabulary:\n{vocabulary}"
        )

    except requests.exceptions.Timeout:

        return (
            "AI response generate ஆக நேரம் எடுக்கிறது. "
            "Please try again."
        )

    except requests.exceptions.ConnectionError:

        return (
            "Ollama connect ஆகவில்லை. "
            "Ollama running-ல் இருக்கிறதா check பண்ணுங்கள்."
        )

    except requests.exceptions.RequestException as exc:

        return f"AI Error: {exc}"
