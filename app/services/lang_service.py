import json
from flask import session

def load_language():
    lang = session.get('translations', 'en')
    try:
        with open(f'translations/{lang}.json', encoding='utf-8') as f:
            return json.load(f)
    except:
        with open('translations/en.json', encoding='utf-8') as f:
            return json.load(f)