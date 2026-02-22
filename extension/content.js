// Function to extract comprehensive page data
// Function to extract comprehensive page data using Readability.js
function extractPageData() {
  const MAX_CONTENT = 50000; // Truncate to 50k chars to avoid backend limits
  
  let articleContent = '';
  let title = document.title;
  let byline = document.querySelector('meta[name="author"]')?.content || '';
  let excerpt = document.querySelector('meta[name="description"]')?.content || '';

  try {
    const documentClone = document.cloneNode(true);
    const reader = new Readability(documentClone);
    const article = reader.parse();

    if (article && article.textContent) {
      articleContent = article.textContent.trim();
      title = article.title || title;
      byline = article.byline || byline;
      excerpt = article.excerpt || excerpt;
    } else {
      // Safe fallback if Readability returns null
      articleContent = (document.body && document.body.innerText) ? document.body.innerText.trim() : "No readable text found on this page.";
    }
  } catch (error) {
    console.error("Readability parsing error:", error);
    // Safe fallback if cloning or parsing throws a fatal error
    articleContent = (document.body && document.body.innerText) ? document.body.innerText.trim() : "No readable text found on this page.";
  }

  // Safe truncation check
  if (articleContent && articleContent.length > MAX_CONTENT) {
    articleContent = articleContent.substring(0, MAX_CONTENT) + '...';
  }

  // Build the exact payload your popup/backend expects
  const pageData = {
    url: window.location.href,
    title: title,
    content: document.body.innerText, // Full page content (backup)
    articleContent: articleContent,   // Cleaned main content from Readability
    date: new Date().toLocaleDateString(),
    time: new Date().toLocaleTimeString(),
    metaDescription: excerpt,
    metaKeywords: document.querySelector('meta[name="keywords"]')?.content || '',
    author: byline,
    wordCount: articleContent.split(/\s+/).filter(word => word.length > 0).length,
    paragraphCount: articleContent.split(/\n\n+/).filter(p => p.trim().length > 0).length
  };

  return pageData;
}

// Listen for messages from the popup (Unchanged)
chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  if (req.action === "extractPageData") {
    try {
      const data = extractPageData();
      sendResponse({ success: true, data: data });
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }
  if (req.action === "getAuthTokens") {
    chrome.storage.local.get(["accessToken", "refreshToken"], (stored) => {
      sendResponse({
        success: true,
        accessToken: stored.accessToken,
        refreshToken: stored.refreshToken
      });
    });
  }
  return true; // Keep the message channel open for async response
});
