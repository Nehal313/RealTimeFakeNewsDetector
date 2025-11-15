// Content script - extracts text from webpage

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractPageText') {
    extractPageText(sendResponse);
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'extractSelectedText') {
    extractSelectedText(sendResponse);
    return true;
  }
});

/**
 * Extract main text content from page
 */
function extractPageText(sendResponse) {
  try {
    let text = '';
    let headline = '';
    
    // Try to get headline
    const h1 = document.querySelector('h1');
    const title = document.querySelector('title');
    
    if (h1) {
      headline = h1.innerText.trim();
    } else if (title) {
      headline = title.innerText.trim();
    }
    
    // Extract main content
    // Priority: article tag, main tag, body
    const article = document.querySelector('article');
    const main = document.querySelector('main');
    const body = document.body;
    
    if (article) {
      text = article.innerText;
    } else if (main) {
      text = main.innerText;
    } else {
      text = body.innerText;
    }
    
    // Clean text
    text = cleanText(text);
    headline = cleanText(headline);
    
    // Limit text length (API constraint)
    const maxLength = 5000;
    if (text.length > maxLength) {
      text = text.substring(0, maxLength);
    }
    
    sendResponse({
      success: true,
      text: text,
      headline: headline,
      url: window.location.href
    });
    
  } catch (error) {
    sendResponse({
      success: false,
      error: error.message
    });
  }
}

/**
 * Extract selected text from page
 */
function extractSelectedText(sendResponse) {
  try {
    const selection = window.getSelection().toString().trim();
    
    if (!selection || selection.length < 10) {
      sendResponse({
        success: false,
        error: 'Please select at least 10 characters of text'
      });
      return;
    }
    
    const text = cleanText(selection);
    
    sendResponse({
      success: true,
      text: text,
      headline: text.substring(0, 100),
      url: window.location.href
    });
    
  } catch (error) {
    sendResponse({
      success: false,
      error: error.message
    });
  }
}

/**
 * Clean and normalize text
 */
function cleanText(text) {
  return text
    .replace(/\s+/g, ' ')           // Multiple spaces to single space
    .replace(/\n+/g, ' ')           // Newlines to space
    .replace(/\t+/g, ' ')           // Tabs to space
    .trim();
}

console.log('Fake News Detector: Content script loaded');
