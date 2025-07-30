import React, { useEffect, useState } from 'react';

type Result = {
  surah_no: number;
  surah_name_en: string;
  surah_name_roman: string;
  ayah_no_surah: number;
  ayah_translation_en: string;
  path: string;
};

export default function CustomSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Result[]>([]);
  const [data, setData] = useState<Result[]>([]);

  useEffect(() => {
    fetch('/search/flexsearch-index.json')
      .then((res) => res.json())
      .then(setData)
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!query) {
      setResults([]);
    } else {
      const lower = query.toLowerCase();
      const filtered = data.filter((item) =>
        item.ayah_translation_en?.toLowerCase().includes(lower)
      );
      setResults(filtered.slice(0, 10)); // Limit results
    }
  }, [query, data]);

  return (
    <div style={{ marginBottom: '2rem' }}>
      <input
        type="text"
        placeholder="Search Quran..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          padding: '0.5rem',
          width: '100%',
          fontSize: '1rem',
          border: '1px solid #ccc',
          borderRadius: '4px',
        }}
      />
      <ul style={{ listStyle: 'none', paddingLeft: 0, marginTop: '1rem' }}>
        {results.map((r, i) => (
          <li key={i} style={{ marginBottom: '0.5rem' }}>
            <a href={r.path} style={{ textDecoration: 'none', color: '#0077cc' }}>
              <strong>Surah {r.surah_no} ({r.surah_name_roman})</strong><br />
              {r.ayah_no_surah}. {r.ayah_translation_en}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
