# task_extractor_core.py

import spacy
import dateparser
from datetime import datetime
import re
from dateparser.search import search_dates

nlp = spacy.load("en_core_web_sm")

ACTION_VERBS = {
    "submit", "complete", "finish", "send", "deliver", "review", "prepare",
    "create", "update", "call", "email", "schedule", "book", "reserve",
    "order", "buy", "purchase", "pay", "attend", "meet", "discuss", "plan",
    "organize", "arrange", "confirm", "follow up", "check", "verify", "test"
}
TASK_INDICATORS = {
    "task", "assignment", "project", "deadline", "due", "reminder",
    "appointment", "meeting", "report", "presentation", "document",
    "proposal", "invoice", "quote", "contract"
}
PRIORITY_WORDS = {
    "high": {"urgent", "asap", "immediately", "critical"},
    "medium": {"soon", "priority", "should", "need to"},
    "low": {"maybe", "eventually", "when possible"}
}
CATEGORY_MAP = {
    "work": {"report", "meeting", "presentation", "project", "client", "business"},
    "personal": {"doctor", "dentist", "family", "friend", "home", "car"},
    "deadline": {"due", "deadline", "submit", "deliver", "finish"},
    "meeting": {"meeting", "call", "conference", "discuss", "attend", "appointment"}
}

def extract_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def contains_task_keywords(sentence):
    words = set(word.lower() for word in re.findall(r"\w+", sentence))
    return bool(words & (ACTION_VERBS | TASK_INDICATORS))

def extract_date(sentence):
    results = search_dates(sentence, settings={'PREFER_DATES_FROM': 'future'})
    if results:
        return results[0][1].date().isoformat()
    return None

def assign_priority(sentence):
    words = set(sentence.lower().split())
    for level, keywords in PRIORITY_WORDS.items():
        if words & keywords:
            return level
    return "low"

def classify_category(sentence):
    words = set(sentence.lower().split())
    for cat, keywords in CATEGORY_MAP.items():
        if words & keywords:
            return cat
    return "uncategorized"

def clean_sentence(sentence, date_str):
    if date_str:
        sentence = re.sub(r"\b" + re.escape(date_str) + r"\b", "", sentence, flags=re.IGNORECASE)
    sentence = re.sub(r'\b(today|tomorrow|yesterday|next \w+|this \w+|in \d+ days)\b', '', sentence, flags=re.IGNORECASE)
    return ' '.join(sentence.split())

def extract_tasks(text):
    tasks = []
    for sent in extract_sentences(text):
        if contains_task_keywords(sent):
            date = extract_date(sent)
            if date:
                task = {
                    "original": sent,
                    "task": clean_sentence(sent, date),
                    "due_date": date,
                    "priority": assign_priority(sent),
                    "category": classify_category(sent)
                }
                tasks.append(task)
    return tasks
