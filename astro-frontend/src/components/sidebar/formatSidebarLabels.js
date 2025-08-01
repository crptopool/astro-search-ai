/**
 * Format a directory name to Title Case with spaces instead of hyphens
 * @param {string} text - The text to format (e.g. "blessings-rewards")
 * @returns {string} - The formatted text (e.g. "Blessings Rewards")
 */
export function formatDirectoryName(text) {
  return text
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Recursively formats all directory labels in the sidebar entries
 * @param {Array} entries - The sidebar entries array
 * @returns {Array} - The formatted sidebar entries
 */
export function formatSidebarLabels(entries) {
  if (!entries || !Array.isArray(entries)) return entries;
  
  return entries.map(entry => {
    // Skip formatting if this is a link/page (not a directory)
    if (entry.type !== 'group') return entry;
    
    // Create a new entry with formatted label (only for directory names)
    const newEntry = { ...entry, label: formatDirectoryName(entry.label) };
    
    // Recursively format any nested entries (subdirectories)
    if (newEntry.entries && Array.isArray(newEntry.entries)) {
      newEntry.entries = formatSidebarLabels(newEntry.entries);
    }
    
    return newEntry;
  });
}