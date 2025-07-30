// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';

// import surahSidebar from './src/config/sidebar-surahs.js';

// https://astro.build/config
export default defineConfig({
	integrations: [
		react(),
		starlight({
			title: 'Docs with Tailwind',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/withastro/starlight' }],
			sidebar: [
				 
				{
					label: 'Guides',
					items: [
						// Each item here is one entry in the navigation menu.
						{ label: 'Example Guide', slug: 'guides/example' },
					],
				},
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
				{
					label: 'The Noble Quran',
					autogenerate: { directory: 'surahs' },
				},
				{
					label: 'Chatbot',
					link: '/chat'
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
			'process.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL),
		},
	},
});
