import type { AstroGlobal } from 'astro';

// Default translations for aside types
const defaultTranslations = {
  'aside.note': 'Note',
  'aside.tip': 'Tip',
  'aside.caution': 'Caution',
  'aside.danger': 'Danger',
  'aside.quran': 'Quran',
  'aside.hadith': 'Hadith',
  'aside.reference': 'Reference'
};

// Translation function that handles looking up translation strings
export function useTranslations(Astro: AstroGlobal) {
  // Get the current language from Astro.locals if available, or default to 'en'
  const lang = Astro.locals?.lang || 'en';
  
  // This function returns the translation for a given key
  return function translate(key: string): string {
    // First check if we have a translation in the current language
    // You can expand this to use actual translation files as your project grows
    const translation = defaultTranslations[key];
    
    if (!translation) {
      // If no translation is found, return the key for debugging purposes
      console.warn(`Missing translation for key "${key}"`);
      return key;
    }
    
    return translation;
  };
}

// Helper function to get the locale from the URL path
export function getLocaleFromPath(pathname: string): string {
  const segments = pathname.split('/').filter(Boolean);
  // Check if the first segment is a supported locale
  const locales = ['en', 'bn', 'de', 'es', 'ja', 'fr', 'it', 'id', 'zh-CN', 'pt-BR', 'pt-PT', 'ko', 'tr', 'ru', 'hi', 'da', 'uk'];
  
  if (segments.length > 0 && locales.includes(segments[0])) {
    return segments[0];
  }
  
  // Default to English
  return 'en';
}