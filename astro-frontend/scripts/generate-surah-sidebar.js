// scripts/generate-surah-sidebar.js
import fs from 'fs/promises';
import fetch from 'node-fetch';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Directus API endpoint
const API_URL = 'http://localhost:8055/items/TheNobleQuran?limit=-1';

try {
  const response = await fetch(API_URL);
  const { data } = await response.json();

  const uniqueSurahs = [...new Set(data.map((r) => r.sura_no).filter(Boolean))].sort((a, b) => a - b);

  const sidebarItems = uniqueSurahs.map((no) => ({
    label: `Surah ${no}`,
    link: `/surah/${no}`,
  }));

  const output = `export default ${JSON.stringify([
    {
      label: 'The Noble Quran',
      items: sidebarItems,
    },
  ], null, 2)};\n`;

  const outputPath = path.join(__dirname, '../src/config/sidebar-surahs.js');
  await fs.writeFile(outputPath, output);
  console.log(`✅ Sidebar items written to ${outputPath}`);
} catch (err) {
  console.error('❌ Failed to generate sidebar:', err);
}
