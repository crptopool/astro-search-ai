export async function fetchNocoData({ category = "", sub_categories = "" }) {
    const baseUrl = 'https://nocodb.admads.com/api/v2/tables/mrm2wil7jtms2wp/records';
    const viewId = 'vwlkfciwoiq7f0a1';
  
    const whereClause = `(category,eq,${category})~and(sub_categories,anyof,${sub_categories})`;
    const fullUrl = `${baseUrl}?viewId=${viewId}&where=${encodeURIComponent(whereClause)}&limit=5&shuffle=0&offset=0`;
  
    const headers = {
      'xc-auth': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImluZm9AYWx0YWlyLmdlIiwiaWQiOiJ1c2puN3A2d2pnajh3bnc3Iiwicm9sZXMiOnsib3JnLWxldmVsLWNyZWF0b3IiOnRydWUsInN1cGVyIjp0cnVlfSwidG9rZW5fdmVyc2lvbiI6IjQxOTAzMDI4NzgxZmY1NGFlYjUxMTVhNmVhMTZhMjFlYTUxMGNjYjM5MmJjODNkYzkwMzQ5YWYyZWI2ZDAxYWZjZTU0Y2FlNTQzMmFjY2NiIiwiaWF0IjoxNzUwNTIyMTQ2LCJleHAiOjE3ODY1MjIxNDZ9.q3V5fNWQEg8cQnUjwrJexnTFPguBmXJ5E8fXJrMTaPk'
    };
  
    try {
      const response = await fetch(fullUrl, { method: 'GET', headers });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
  
      const result = await response.json();
      return Array.isArray(result.records || result.list || result.data)
        ? result.records || result.list || result.data
        : [];
    } catch (error) {
      console.error('Fetch failed:', error);
      return [];
    }
  }
  