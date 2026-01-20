// Function to extract comprehensive page data
function extractPageData(){
  // Get main content (try different selectors for article content)
  let articleContent = '';
  
  // Try to find article content using common selectors
  const contentSelectors = [
    'article',
    'main',
    '[role="main"]',
    '.post-content',
    '.article-content',
    '.entry-content',
    '.content'
  ];
  
  let contentElement = null;
  for (const selector of contentSelectors) {
    contentElement = document.querySelector(selector);
    if (contentElement && contentElement.innerText.trim().length > 100) {
      articleContent = contentElement.innerText;
      break;
    }
  }
  
  // If no article element found, use body text
  if (!articleContent) {
    articleContent = document.body.innerText;
  }

  const pageData = {
    url: window.location.href,
    title: document.title,
    content: document.body.innerText, // Full page content (backup)
    articleContent: articleContent, // Main content
    date: new Date().toLocaleDateString(),
    time: new Date().toLocaleTimeString(),
    metaDescription: document.querySelector('meta[name="description"]')?.content || '',
    metaKeywords: document.querySelector('meta[name="keywords"]')?.content || '',
    author: document.querySelector('meta[name="author"]')?.content || '',
    wordCount: articleContent.split(/\s+/).filter(word => word.length > 0).length,
    paragraphCount: articleContent.split(/\n\n+/).filter(p => p.trim().length > 0).length
  };

  return pageData;
}

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  if (req.action === "extractPageData") {
    try {
      const data = extractPageData();
      sendResponse({ success: true, data: data });
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }
  return true; // Keep the message channel open for async response
});