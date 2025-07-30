
# 📘 README — Custom FlexSearch Search Integration for Astro Starlight Quran

This project integrates a custom search experience using **FlexSearch** instead of the default Algolia-powered Starlight search.

---

## ✅ Features Implemented

- 📄 Converts `.mdx` Surah pages into a searchable JSON index.
- 🔎 Client-side search with live filtering using [FlexSearch](https://github.com/nextapps-de/flexsearch).
- 🔗 Each result links directly to its corresponding Surah page.
- 🧩 Replaces default Starlight header search with a custom component.

---

## 📁 Folder Structure

```
astro-quran/
├── public/
│   └── search/
│       └── flexsearch-index.json       ← 🔍 Search index
├── scripts/
│   └── generate-flexsearch-index.py    ← 🔧 Index builder
├── src/
│   └── components/
│       └── CustomSearch.astro          ← Astro wrapper for client component
│       └── CustomSearchImpl.tsx        ← Client-side React search logic
├── node_modules/@astrojs/starlight/components/
│   └── Header.astro                    ← 🔄 Patched to inject custom search
```

---

## 🧑‍💻 Step-by-Step Setup

### 1. **Generate the Search Index**

You must first generate a `flexsearch-index.json` using a Python script:

```bash
python scripts/generate-flexsearch-index.py
```

This script scans your `src/content/docs/surahs/*.mdx` files and extracts:

- `title`: Surah title
- `body`: Surah content
- `path`: URL path to the page

📦 Output: `public/search/flexsearch-index.json`

---

### 2. **Add the Search Component**

#### `src/components/CustomSearchImpl.tsx`

Handles loading the index and searching on the client using `flexsearch`.

#### `src/components/CustomSearch.astro`

Wraps the React component using `client:load`:

```astro
---
import CustomSearchImpl from './CustomSearchImpl.tsx';
---

<div>
  <CustomSearchImpl client:load />
</div>
```

---

### 3. **Patch the Starlight Header**

Replace the original search component in:

```diff
node_modules/@astrojs/starlight/components/Header.astro
```

Insert your component like this:

```astro
---
import CustomSearch from '../../../src/components/CustomSearch.astro';
---

<header class="sl-header">
  <CustomSearch />
  <!-- Other header content -->
</header>
```

📝 Alternatively: create a custom `Header.astro` and register it in `astro.config.mjs` under `components`.

---

## 🧪 Testing

- Start Astro:
  ```bash
  npm run dev
  ```

- Type any term (e.g. *Samad*, *Ikhlas*, *mercy*) in the header search bar.
- You should see matching Surahs with clickable links.

---

## 🚧 Known Issues

- Results may not appear if the index is malformed. Always regenerate after changing `.mdx`.
- This approach does **not** support fuzzy or typo-tolerant search out of the box.

---

## 📌 To Do

- [ ] Add search term highlighting
- [ ] Add keyboard navigation for results
- [ ] Switch to `client:visible` for lazy-loading the component
