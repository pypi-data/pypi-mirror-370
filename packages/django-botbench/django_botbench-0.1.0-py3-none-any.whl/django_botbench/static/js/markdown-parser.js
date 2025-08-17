function parseMarkdown(text) {
  // Track open tags to handle partial fragments
  const openTags = [];
  
  // Split text into lines for processing
  const lines = text.split('\n');
  const result = [];
  let inList = false;
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    
    // Handle unordered lists (lines starting with dash)
    if (line.trim().startsWith('- ')) {
      // Start list if not already in one
      if (!inList) {
        // Close any open formatting tags before starting list
        while (openTags.length > 0) {
          const tag = openTags.pop();
          result.push(`</${tag.tag}>`);
        }
        result.push('<ul>');
        inList = true;
      }
      
      const listContent = line.trim().substring(2); // Remove "- "
      const processedContent = processInlineFormatting(listContent, openTags);
      result.push(`<li>${processedContent}</li>`);
    } else {
      // Close list if we were in one
      if (inList) {
        // Close any open formatting tags before closing list
        while (openTags.length > 0) {
          const tag = openTags.pop();
          result.push(`</${tag.tag}>`);
        }
        result.push('</ul>');
        inList = false;
      }
      
      // Process regular lines with inline formatting - preserve all whitespace
      const processedLine = processInlineFormatting(line, openTags);
      result.push(processedLine);
    }
    
    // Add newline back (except for last line)
    if (i < lines.length - 1) {
      result.push('\n');
    }
  }
  
  // Close list if still open at the end
  if (inList) {
    // Close any open formatting tags before closing list
    while (openTags.length > 0) {
      const tag = openTags.pop();
      result.push(`</${tag.tag}>`);
    }
    result.push('</ul>');
  }
  
  // Close any remaining open tags at the end
  while (openTags.length > 0) {
    const tag = openTags.pop();
    result.push(`</${tag.tag}>`);
  }
  
  return result.join('');
}

function processInlineFormatting(text, openTags) {
  let result = '';
  let i = 0;
  
  while (i < text.length) {
    const char = text[i];
    
    if (char === '*' || char === '_') {
      const formatChar = char;
      let count = 0;
      let j = i;
      
      // Count consecutive formatting characters
      while (j < text.length && text[j] === formatChar) {
        count++;
        j++;
      }
      
      // Handle bold formatting (2 or more consecutive chars)
      if (count >= 2) {
        const tagType = 'strong';
        const openTagIndex = findOpenTag(openTags, tagType, formatChar);
        
        if (openTagIndex !== -1) {
          // Close the tag
          result += `</strong>`;
          openTags.splice(openTagIndex, 1);
        } else {
          // Open the tag
          result += `<strong>`;
          openTags.push({ tag: tagType, char: formatChar });
        }
        
        i = j; // Skip the formatting characters
      } else if (count === 1) {
        // Handle italic formatting (single char)
        const tagType = 'em';
        const openTagIndex = findOpenTag(openTags, tagType, formatChar);
        
        if (openTagIndex !== -1) {
          // Close the tag
          result += `</em>`;
          openTags.splice(openTagIndex, 1);
        } else {
          // Open the tag
          result += `<em>`;
          openTags.push({ tag: tagType, char: formatChar });
        }
        
        i = j; // Skip the formatting character
      } else {
        // Should not reach here, but handle gracefully
        result += escapeHtml(char);
        i++;
      }
    } else {
      // Regular character
      result += escapeHtml(char);
      i++;
    }
  }
  
  return result;
}

function findOpenTag(openTags, tagType, formatChar) {
  // Find the most recent open tag of the same type and format character
  for (let i = openTags.length - 1; i >= 0; i--) {
    if (openTags[i].tag === tagType && openTags[i].char === formatChar) {
      return i;
    }
  }
  return -1;
}

function escapeHtml(text) {
  // const div = document.createElement('div');
  // div.textContent = text;
  // return div.innerHTML;
  return text;
}

// Export the function for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = parseMarkdown;
}