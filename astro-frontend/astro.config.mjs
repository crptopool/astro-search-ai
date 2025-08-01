// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';

// import surahSidebar from './src/config/sidebar-surahs.js';
export const locales = {
	root: { label: 'English', lang: 'en' },
	bn: { label: 'Bangla', lang: 'bn' },
	de: { label: 'Deutsch', lang: 'de' },
	es: { label: 'Español', lang: 'es' },
	ja: { label: '日本語', lang: 'ja' },
	fa: { label: 'Persian', lang: 'fa' },
	fr: { label: 'Français', lang: 'fr' },
	it: { label: 'Italiano', lang: 'it' },
	id: { label: 'Bahasa Indonesia', lang: 'id' },
	'zh-cn': { label: '简体中文', lang: 'zh-CN' },
	'pt-br': { label: 'Português do Brasil', lang: 'pt-BR' },
	'pt-pt': { label: 'Português', lang: 'pt-PT' },
	ko: { label: '한국어', lang: 'ko' },
	ml: { label: 'Malayalam', lang: 'ml' },
	no: { label: 'Norwegian', lang: 'no' },
	tr: { label: 'Türkçe', lang: 'tr' },
	ru: { label: 'Русский', lang: 'ru' },
	hi: { label: 'हिंदी', lang: 'hi' },
	da: { label: 'Dansk', lang: 'da' },
	uk: { label: 'Українська', lang: 'uk' },
	ur: { label: 'Urdu', lang: 'ur' },
	uz: { label: 'Uzbek', lang: 'uz' },
};

// https://astro.build/config
export default defineConfig({
	integrations: [
		react(),
		starlight({
			title: 'The Noble Quran',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/withastro/starlight' }],
			defaultLocale: 'root',
			locales,
			sidebar: [
				 
				{
					label: 'Table of Contents',
					items: [
					  {
						label: 'Index',
						link: '/tableofcontents'
					  }
					]
				  },
				{
					label: 'The Noble Quran',
					autogenerate: { directory: 'surahs' },
				},
 

			],
		 
			customCss: ['./src/styles/global.css'],
			components: {
		//		Footer: './src/components/CustomFooter.astro',
				Search: './src/components/CustomSearch.astro',
			  },
			
		}),
	],
	vite: {
		plugins: [tailwindcss()],
		preview: {
			allowedHosts: 'all',
		},
		define: {
			'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL),
		},
	},
});
