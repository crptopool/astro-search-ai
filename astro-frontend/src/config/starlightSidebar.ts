import type { Sidebar } from '@astrojs/starlight';

// Correct use of `dir`: 'ltr' or 'rtl'
export const locales = {
  root: { label: 'English', lang: 'en', dir: 'ltr' },
  bn: { label: 'বাংলা', lang: 'bn', dir: 'ltr' },
  ur: { label: 'اردو', lang: 'ur', dir: 'rtl' },
  hi: { label: 'हिंदी', lang: 'hi', dir: 'ltr' },
  fa: { label: 'فارسی', lang: 'fa', dir: 'rtl' },
  id: { label: 'Al‑Qur’an', lang: 'id', dir: 'ltr' },
  tr: { label: 'Kur’an‑ı Kerim', lang: 'tr', dir: 'ltr' },
  de: { label: 'Der edle Koran', lang: 'de', dir: 'ltr' },
  fr: { label: 'Le Noble Coran', lang: 'fr', dir: 'ltr' },
  es: { label: 'El Noble Corán', lang: 'es', dir: 'ltr' },
  ru: { label: 'Священный Коран', lang: 'ru', dir: 'ltr' },
  'zh-cn': { label: '古兰经', lang: 'zh-CN', dir: 'ltr' },
  'pt-pt': { label: 'O Alcorão Sagrado', lang: 'pt-PT', dir: 'ltr' },
  ko: { label: '성 꾸란', lang: 'ko', dir: 'ltr' },
  ja: { label: '聖クルアーン', lang: 'ja', dir: 'ltr' },
};

// Sidebar generator function
export function generateSidebar(): Record<string, Sidebar> {
  const sidebar: Record<string, Sidebar> = {};

  for (const [localeKey, locale] of Object.entries(locales)) {
    const directory = localeKey === 'root' ? 'en' : localeKey;

    sidebar[localeKey] = [
      {
        label: locale.label,
        autogenerate: {
          directory,
        },
      },
    ];
  }

  return sidebar;
}
