import { useEffect, useState } from 'react';
import FlexSearch, { Document } from 'flexsearch';

interface SearchResult {
  id: string;
  title: string;
  path: string;
}

// Define the expected structure of your index data
interface IndexItem {
  id: number;
  title: string;
  slug: string;
  content: string;
}

export default function CustomSearchImpl() {
  const [query, setQuery] = useState('');
  const [index, setIndex] = useState<Document | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);

  // Load the FlexSearch index on mount
  useEffect(() => {
    const loadIndex = async () => {
      try {
        // First, fetch the raw data
        const res = await fetch('/search/flexsearch-index.json');
        const rawData: IndexItem[] = await res.json();

        // Initialize FlexSearch
        const flex = new FlexSearch.Document({
          tokenize: 'forward',
          cache: 100,
          document: {
            id: 'id',
            index: ['title', 'content'],
            store: ['title', 'slug']
          }
        });

        // Add each document to the index manually
        for (const item of rawData) {
          await flex.add({
            id: item.id,
            title: item.title,
            content: item.content,
            slug: item.slug
          });
        }

        setIndex(flex);
      } catch (error) {
        console.error("Error loading search index:", error);
      }
    };

    loadIndex();
  }, []);

  // Update results when query changes
  useEffect(() => {
    if (!query || !index) {
      setResults([]);
      return;
    }

    const runSearch = async () => {
      try {
        // Search in both title and content fields
        const titleResults = await index.search(query, { 
          index: 'title',
          limit: 5,
          enrich: true 
        });
        
        const contentResults = await index.search(query, { 
          index: 'content',
          limit: 10,
          enrich: true 
        });

        // Combine and format results
        const combined = [...titleResults, ...contentResults];
        const formatted = combined.flatMap(result => 
          result.result.map(item => ({
            id: item.id.toString(),
            title: item.doc.title,
            path: item.doc.slug
          }))
        );

        // Remove duplicates based on id
        const uniqueResults = Array.from(
          formatted.reduce((map, item) => map.set(item.id, item), new Map()).values()
        );

        setResults(uniqueResults.slice(0, 10));
      } catch (error) {
        console.error("Error during search:", error);
        setResults([]);
      }
    };

    runSearch();
  }, [query, index]);

  return (
    <div style={{ position: 'relative', maxWidth: 400 }}>
      <input
        type="search"
        placeholder="Search Quran..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          width: '100%',
          padding: '0.5rem',
          fontSize: '1rem',
          borderRadius: '4px',
          border: '1px solid #ccc',
        }}
      />
      {results.length > 0 && (
        <ul
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            width: '100%',
            background: 'white',
            border: '1px solid #ccc',
            zIndex: 1000,
            maxHeight: '300px',
            overflowY: 'auto',
            padding: 0,
            margin: '0.5rem 0 0 0',
            listStyle: 'none',
          }}
        >
          {results.map((r, idx) => (
            <li key={idx}>
              <a
                href={r.path}
                style={{
                  display: 'block',
                  padding: '0.5rem',
                  textDecoration: 'none',
                  color: '#0077cc',
                }}
              >
                <strong>{r.title}</strong>
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}