import json
import os
from flask import current_app, session

class TranslationManager:
    _translations = {}

    @staticmethod
    def load_translations():
        """អានហ្វាល JSON ទាំងអស់ចូលទៅក្នុង Memory ពេលបើក Server"""
        base_path = os.path.join(current_app.root_path, 'translations')
        
        # Load English
        with open(os.path.join(base_path, 'en.json'), 'r', encoding='utf-8') as f:
            TranslationManager._translations['en'] = json.load(f)
            
        # Load Khmer
        with open(os.path.join(base_path, 'km.json'), 'r', encoding='utf-8') as f:
            TranslationManager._translations['km'] = json.load(f)

    @staticmethod
    def get_text(key_path):
        """
        ទាញយកពាក្យដោយប្រើ Dot Notation (ឧ. 'sidebar.dashboard')
        """
        lang = session.get('language', 'en') # យកភាសាពី Session
        data = TranslationManager._translations.get(lang, TranslationManager._translations['en'])
        
        # បំបែក key (ឧ. "sidebar.dashboard" -> ["sidebar", "dashboard"])
        keys = key_path.split('.')
        
        for k in keys:
            data = data.get(k, {})
            
        # បើរកមិនឃើញ ឱ្យបង្ហាញ Key ដើមវិញ (ដើម្បីកុំឱ្យ Error)
        if isinstance(data, dict): 
            return key_path
            
        return data

# Function ជំនួយសម្រាប់ហៅប្រើក្នុង Template
def t(key):
    # Load ម្ដងដំបូងបើមិនទាន់ Load
    if not TranslationManager._translations:
        TranslationManager.load_translations()
    return TranslationManager.get_text(key)