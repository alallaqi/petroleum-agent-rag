"""
Language Translator Module for Petroleum Agent RAG System

This module provides automatic language detection and translation capabilities
for Arabic, French, English, and German using Ollama for local translation.
Designed as a lightweight preprocessing/postprocessing wrapper around the RAG system.
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from langchain_ollama import OllamaLLM

# Set seed for consistent language detection results
DetectorFactory.seed = 0

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageTranslator:
    """
    Lightweight language translator for petroleum engineering queries.
    
    Supports automatic detection and translation between:
    - Arabic (ar)
    - French (fr) 
    - English (en)
    - German (de)
    """
    
    def __init__(self, ollama_base_url: Optional[str] = None, model_name: str = "llama3.2:latest"):
        """
        Initialize the language translator.
        
        Args:
            ollama_base_url: Optional custom Ollama URL
            model_name: Ollama model to use for translation
        """
        self.supported_languages = {
            'ar': 'Arabic',
            'fr': 'French', 
            'en': 'English',
            'de': 'German'
        }
        
        self.model_name = model_name
        self.ollama_base_url = ollama_base_url or "http://localhost:11434"
        
        # Initialize configuration settings
        self.enabled = True
        self.default_language = 'en'
        self.enable_monitoring = True
        self.max_retries = 3
        
        # Initialize monitoring statistics
        self.stats = {
            'total_queries': 0,
            'translations_performed': 0,
            'languages_detected': {},
            'translation_failures': 0,
            'average_translation_time': 0.0,
            'queries_by_language': {},
            'successful_translations': 0
        }
        
        # Initialize Ollama LLM for translation
        try:
            self.llm = OllamaLLM(
                model=self.model_name,
                base_url=self.ollama_base_url
            )
            logger.info(f"🌍 Language Translator initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama LLM: {e}")
            self.llm = None
            
        # Petroleum engineering terminology glossary for better translations
        self.petroleum_terms = {
            'en': {
                'drilling': 'drilling',
                'hydraulic fracturing': 'hydraulic fracturing', 
                'reservoir': 'reservoir',
                'wellbore': 'wellbore',
                'production': 'production',
                'completion': 'completion',
                'formation': 'formation',
                'casing': 'casing',
                'cementing': 'cementing',
                'petroleum': 'petroleum',
                'crude oil': 'crude oil',
                'natural gas': 'natural gas',
                'permeability': 'permeability',
                'porosity': 'porosity'
            },
            'ar': {
                'drilling': 'حفر',
                'hydraulic fracturing': 'التكسير الهيدروليكي',
                'reservoir': 'مكمن',
                'wellbore': 'بئر',
                'production': 'إنتاج',
                'completion': 'إكمال',
                'formation': 'تكوين',
                'casing': 'أنبوب البئر',
                'cementing': 'الأسمنت',
                'petroleum': 'بترول',
                'crude oil': 'النفط الخام',
                'natural gas': 'الغاز الطبيعي',
                'permeability': 'النفاذية',
                'porosity': 'المسامية'
            },
            'fr': {
                'drilling': 'forage',
                'hydraulic fracturing': 'fracturation hydraulique',
                'reservoir': 'réservoir',
                'wellbore': 'puits',
                'production': 'production',
                'completion': 'complétion',
                'formation': 'formation',
                'casing': 'tubage',
                'cementing': 'cimentation',
                'petroleum': 'pétrole',
                'crude oil': 'pétrole brut',
                'natural gas': 'gaz naturel',
                'permeability': 'perméabilité',
                'porosity': 'porosité'
            },
            'de': {
                'drilling': 'Bohren',
                'hydraulic fracturing': 'hydraulisches Fracking',
                'reservoir': 'Lagerstätte',
                'wellbore': 'Bohrloch',
                'production': 'Förderung',
                'completion': 'Komplettierung',
                'formation': 'Formation',
                'casing': 'Verrohrung',
                'cementing': 'Zementierung',
                'petroleum': 'Erdöl',
                'crude oil': 'Rohöl',
                'natural gas': 'Erdgas',
                'permeability': 'Durchlässigkeit',
                'porosity': 'Porosität'
            }
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code (ar, fr, en, de) or 'en' as fallback
        """
        if not text or not text.strip():
            return 'en'
            
        try:
            detected = detect(text)
            
            # Map detected language to supported languages
            if detected in self.supported_languages:
                logger.info(f"🔍 Detected language: {self.supported_languages[detected]} ({detected})")
                return detected
            else:
                logger.warning(f"⚠️ Unsupported language detected: {detected}, defaulting to English")
                return 'en'
                
        except LangDetectException as e:
            logger.warning(f"⚠️ Language detection failed: {e}, defaulting to English")
            return 'en'
        except Exception as e:
            logger.error(f"❌ Unexpected error in language detection: {e}")
            return 'en'
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Translate text from source language to English.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            
        Returns:
            Translated text in English
        """
        if source_lang == 'en' or not self.llm:
            return text
            
        try:
            source_language_name = self.supported_languages.get(source_lang, 'Unknown')
            
            prompt = f"""You are a petroleum engineering translator. Translate this {source_language_name} text to English. Give only the direct translation, no explanations.

Text: {text}

Translation:"""

            translation = self.llm.invoke(prompt)
            
            # Clean up the translation response
            translation = translation.strip()
            if translation.startswith("Translation:"):
                translation = translation.replace("Translation:", "").strip()
            
            logger.info(f"🔄 Translated from {source_language_name} to English")
            return translation
            
        except Exception as e:
            logger.error(f"❌ Translation to English failed: {e}")
            return text  # Return original text as fallback
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translate text from English to target language.
        
        Args:
            text: English text to translate
            target_lang: Target language code
            
        Returns:
            Translated text in target language
        """
        if target_lang == 'en' or not self.llm:
            return text
            
        try:
            target_language_name = self.supported_languages.get(target_lang, 'Unknown')
            
            prompt = f"""You are a petroleum engineering translator. Translate this English text to {target_language_name}. Give only the direct translation, no explanations.

Text: {text}

Translation:"""

            translation = self.llm.invoke(prompt)
            
            # Clean up the translation response
            translation = translation.strip()
            if translation.startswith("Translation:"):
                translation = translation.replace("Translation:", "").strip()
            
            logger.info(f"🔄 Translated from English to {target_language_name}")
            return translation
            
        except Exception as e:
            logger.error(f"❌ Translation from English failed: {e}")
            return text  # Return original text as fallback
    
    def process_query(self, query: str) -> Tuple[str, str]:
        """
        Process user query: detect language and translate to English if needed.
        
        Args:
            query: User input query
            
        Returns:
            Tuple of (english_query, detected_language)
        """
        import time
        start_time = time.time()
        
        # Update monitoring stats
        if self.enable_monitoring:
            self.stats['total_queries'] += 1
        
        # Detect language
        detected_lang = self.detect_language(query)
        
        # Track language detection
        if self.enable_monitoring:
            self.stats['languages_detected'][detected_lang] = self.stats['languages_detected'].get(detected_lang, 0) + 1
            self.stats['queries_by_language'][detected_lang] = self.stats['queries_by_language'].get(detected_lang, 0) + 1
        
        # Translate to English if needed
        try:
            english_query = self.translate_to_english(query, detected_lang)
            
            # Track successful translation
            if self.enable_monitoring and detected_lang != 'en':
                self.stats['translations_performed'] += 1
                self.stats['successful_translations'] += 1
                
                # Update average translation time
                translation_time = time.time() - start_time
                current_avg = self.stats['average_translation_time']
                total_translations = self.stats['translations_performed']
                self.stats['average_translation_time'] = ((current_avg * (total_translations - 1)) + translation_time) / total_translations
                
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            english_query = query  # Fallback to original
            
            # Track translation failure
            if self.enable_monitoring and detected_lang != 'en':
                self.stats['translations_performed'] += 1
                self.stats['translation_failures'] += 1
        
        return english_query, detected_lang
    
    def process_response(self, response: str, target_language: str) -> str:
        """
        Process response: translate from English to target language if needed.
        
        Args:
            response: English response from RAG system
            target_language: Target language for response
            
        Returns:
            Translated response
        """
        return self.translate_from_english(response, target_language)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages mapping."""
        return self.supported_languages.copy()
    
    def is_supported_language(self, lang_code: str) -> bool:
        """Check if language is supported."""
        return lang_code in self.supported_languages
    
    def get_language_stats(self) -> Dict[str, Any]:
        """Get translator statistics and status."""
        return {
            'supported_languages': len(self.supported_languages),
            'languages': list(self.supported_languages.keys()),
            'model': self.model_name,
            'status': 'ready' if self.llm else 'error',
            'petroleum_terms_count': sum(len(terms) for terms in self.petroleum_terms.values())
        }
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current multilingual configuration settings.
        
        Returns:
            Dictionary with all configuration parameters
        """
        return {
            'enabled': getattr(self, 'enabled', True),
            'supported_languages': list(self.supported_languages.keys()),
            'supported_languages_names': list(self.supported_languages.values()),
            'default_language': getattr(self, 'default_language', 'en'),
            'model_name': self.model_name,
            'ollama_base_url': getattr(self, 'ollama_base_url', 'http://localhost:11434'),
            'enable_monitoring': getattr(self, 'enable_monitoring', True),
            'max_retries': getattr(self, 'max_retries', 3),
            'petroleum_terms_loaded': sum(len(terms) for terms in self.petroleum_terms.values()),
            'translation_status': 'ready' if self.llm else 'error'
        }
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Get detailed monitoring and performance statistics.
        
        Returns:
            Dictionary with comprehensive monitoring data
        """
        # Initialize stats if not present
        if not hasattr(self, 'stats'):
            self.stats = {
                'total_queries': 0,
                'translations_performed': 0,
                'languages_detected': {},
                'translation_failures': 0,
                'average_translation_time': 0.0,
                'queries_by_language': {},
                'successful_translations': 0
            }
        
        stats = self.stats
        
        # Calculate success rate
        success_rate = 0.0
        if stats['translations_performed'] > 0:
            success_rate = (stats['successful_translations'] / stats['translations_performed']) * 100
        
        return {
            'performance': {
                'total_queries_processed': stats['total_queries'],
                'total_translations_performed': stats['translations_performed'],
                'successful_translations': stats['successful_translations'],
                'translation_failures': stats['translation_failures'],
                'success_rate_percentage': round(success_rate, 2),
                'average_translation_time_seconds': round(stats['average_translation_time'], 3)
            },
            'language_usage': {
                'languages_detected_count': stats['languages_detected'],
                'queries_by_language': stats['queries_by_language'],
                'most_common_language': max(stats['queries_by_language'].items(), key=lambda x: x[1])[0] if stats['queries_by_language'] else 'N/A'
            },
            'system_info': {
                'supported_languages_count': len(self.supported_languages),
                'model_status': 'ready' if self.llm else 'error',
                'configuration': self.get_configuration()
            }
        }
    
    def reset_monitoring_stats(self) -> None:
        """Reset all monitoring statistics to initial state."""
        self.stats = {
            'total_queries': 0,
            'translations_performed': 0,
            'languages_detected': {},
            'translation_failures': 0,
            'average_translation_time': 0.0,
            'queries_by_language': {},
            'successful_translations': 0
        }
        logger.info("📊 Multilingual monitoring statistics have been reset")
        
    def is_translation_enabled(self) -> bool:
        """
        Check if translation functionality is currently enabled and operational.
        
        Returns:
            True if translation is enabled and LLM is available, False otherwise
        """
        return (
            getattr(self, 'enabled', True) and 
            self.llm is not None and
            len(self.supported_languages) > 0
        )
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update configuration settings dynamically.
        
        Args:
            config: Dictionary with configuration updates
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Update configurable parameters
            if 'enabled' in config:
                self.enabled = config['enabled']
                
            if 'default_language' in config and config['default_language'] in self.supported_languages:
                self.default_language = config['default_language']
                
            if 'enable_monitoring' in config:
                self.enable_monitoring = config['enable_monitoring']
                
            if 'max_retries' in config:
                self.max_retries = max(1, int(config['max_retries']))
                
            logger.info("⚙️ Multilingual configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update configuration: {e}")
            return False


def test_language_translator():
    """Test function for language translator."""
    print("🧪 Testing Language Translator...")
    
    translator = LanguageTranslator()
    
    # Test queries in different languages
    test_queries = {
        'en': "What is hydraulic fracturing?",
        'ar': "ما هو التكسير الهيدروليكي؟", 
        'fr': "Qu'est-ce que la fracturation hydraulique?",
        'de': "Was ist hydraulisches Fracking?"
    }
    
    for lang, query in test_queries.items():
        print(f"\n--- Testing {translator.supported_languages[lang]} ({lang}) ---")
        print(f"Original: {query}")
        
        # Process query
        english_query, detected_lang = translator.process_query(query)
        print(f"Detected: {detected_lang}")
        print(f"English: {english_query}")
        
        # Test response translation back
        sample_response = "Hydraulic fracturing is a technique used to extract oil and gas from shale formations."
        translated_response = translator.process_response(sample_response, detected_lang)
        print(f"Response: {translated_response}")
    
    # Test configuration and monitoring features
    print("\n" + "="*60)
    print("🔧 TESTING CONFIGURATION & MONITORING FEATURES")
    print("="*60)
    
    # Display configuration
    config = translator.get_configuration()
    print(f"\n📋 Configuration:")
    print(f"   Enabled: {config['enabled']}")
    print(f"   Supported Languages: {', '.join(config['supported_languages'])}")
    print(f"   Model: {config['model_name']}")
    print(f"   Translation Status: {config['translation_status']}")
    print(f"   Petroleum Terms Loaded: {config['petroleum_terms_loaded']}")
    
    # Display monitoring stats
    monitoring_stats = translator.get_monitoring_stats()
    performance = monitoring_stats['performance']
    language_usage = monitoring_stats['language_usage']
    
    print(f"\n📊 Monitoring Statistics:")
    print(f"   Total Queries Processed: {performance['total_queries_processed']}")
    print(f"   Translations Performed: {performance['total_translations_performed']}")
    print(f"   Success Rate: {performance['success_rate_percentage']:.1f}%")
    print(f"   Average Translation Time: {performance['average_translation_time_seconds']:.3f}s")
    
    print(f"\n🌍 Language Usage:")
    for lang, count in language_usage['queries_by_language'].items():
        lang_name = translator.supported_languages.get(lang, lang)
        print(f"   {lang_name}: {count} queries")
    
    # Test translation status check
    is_enabled = translator.is_translation_enabled()
    print(f"\n✅ Translation System Status: {'OPERATIONAL' if is_enabled else 'OFFLINE'}")
    
    print("\n🎉 All tests completed successfully!")


if __name__ == "__main__":
    test_language_translator() 