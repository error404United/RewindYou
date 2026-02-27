// Initialize when popup opens
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById("extractButton").addEventListener("click", extractData);
  document.getElementById("loginButton").addEventListener("click", loginUser);
  hydrateAuthStatus();
});

async function extractData() {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = '<div class="loading"><div class="loader"></div><p>Extracting page data...</p></div>';

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab.url.startsWith('http://') && !tab.url.startsWith('https://')) {
      throw new Error('Please navigate to a valid webpage (http:// or https://)');
    }

    // YouTube transcript handling
    if (tab.url.includes("youtube.com/watch") || tab.url.includes("youtu.be")) {
      try {
        const response = await authFetch('/api/save-youtube-transcript', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: tab.url })
        });

        if (!response.ok) {
          const err = await response.json().catch(() => ({}));
          throw new Error(err.error || 'Failed to save YouTube transcript');
        }

        const data = await response.json();

        // Build a page-like data object so displayExtractedData works
        const pageData = {
          url: data.url,
          title: data.title,
          articleContent: data.content_preview,
          date: new Date().toLocaleDateString(),
          time: new Date().toLocaleTimeString(),
          wordCount: data.word_count,
          paragraphCount: 0,
          metaDescription: data.summary,
          metaKeywords: '',
          author: ''
        };

        displayExtractedData(pageData);

        const statusMsg = document.createElement('div');
        statusMsg.className = 'success-message';
        statusMsg.textContent = 'YouTube transcript saved & processed!';
        resultDiv.insertBefore(statusMsg, resultDiv.firstChild);
      } catch (err) {
        resultDiv.innerHTML = `<div class="error">Error: ${err.message}</div>`;
      }
      return; // Stop here — skip normal page extraction
    }

    chrome.tabs.sendMessage(tab.id, { action: "extractPageData" }, async (response) => {
      if (chrome.runtime.lastError) {
        resultDiv.innerHTML = `<div class="error">Error: ${chrome.runtime.lastError.message}<br><br>Please make sure you're on a valid webpage and try reloading the page.</div>`;
        return;
      }

      if (response && response.success) {
        displayExtractedData(response.data);

        try {
          await sendToBackend(response.data);
          const statusMsg = document.createElement('div');
          statusMsg.className = 'success-message';
          statusMsg.textContent = 'Data sent to backend successfully!';
          resultDiv.insertBefore(statusMsg, resultDiv.firstChild);
        } catch (backendError) {
          const errorMsg = document.createElement('div');
          errorMsg.className = 'warning-message';
          errorMsg.textContent = 'Failed to send to backend: ' + backendError.message;
          resultDiv.insertBefore(errorMsg, resultDiv.firstChild);
        }
      } else {
        throw new Error(response?.error || 'Failed to extract data');
      }
    });
  } catch (error) {
    console.error('Error:', error);
    resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
  }
}

function displayExtractedData(data) {
  const resultDiv = document.getElementById("result");
  
  // 1. Force the content to be a string, and default to empty if undefined
  const safeContent = (data && data.articleContent) ? String(data.articleContent) : "";
  
  // 2. Safely truncate content for display
  const contentPreview = safeContent.length > 500 
    ? safeContent.substring(0, 500) + '...' 
    : safeContent || 'No content available';
  
  let html = `
    <div class="extracted-data">
      <h3>Extracted Page Data</h3>
      
      <div class="data-section">
        <h4>Basic Information</h4>
        <p><strong>URL:</strong> <a href="${data.url || '#'}" target="_blank">${data.url || 'Unknown'}</a></p>
        <p><strong>Title:</strong> ${data.title || 'Unknown Title'}</p>
        <p><strong>Date:</strong> ${data.date || ''}</p>
        <p><strong>Time:</strong> ${data.time || ''}</p>
      </div>

      <div class="data-section">
        <h4>Content Preview</h4>
        <div class="content-preview">${contentPreview}</div>
      </div>

      <div class="data-section">
        <h4>Content Statistics</h4>
        <p><strong>Word Count:</strong> ${data.wordCount || 0}</p>
        <p><strong>Paragraph Count:</strong> ${data.paragraphCount || 0}</p>
      </div>
  `;

  // Add metadata if available
  if (data.metaDescription || data.metaKeywords || data.author) {
    html += `
      <div class="data-section">
        <h4>Metadata</h4>
    `;
    if (data.metaDescription) html += `<p><strong>Description:</strong> ${data.metaDescription}</p>`;
    if (data.metaKeywords) html += `<p><strong>Keywords:</strong> ${data.metaKeywords}</p>`;
    if (data.author) html += `<p><strong>Author:</strong> ${data.author}</p>`;
    html += `</div>`;
  }
  
  html += `</div>`;
  resultDiv.innerHTML = html;
}

async function sendToBackend(data) {
  const response = await authFetch('/api/save-page-data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error(`Backend responded with status: ${response.status}`);
  }

  return response.json();
}

async function loginUser() {
  const email = document.getElementById('emailInput').value.trim();
  const password = document.getElementById('passwordInput').value.trim();
  const statusEl = document.getElementById('auth-status');

  statusEl.textContent = 'Logging in...';
  statusEl.className = 'muted';

  try {
    const response = await authFetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    }, { skipAuth: true, skipRefresh: true });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || err.message || `Login failed (${response.status})`);
    }

    const body = await response.json();
    await storeTokens(body.access_token, body.refresh_token);
    statusEl.textContent = 'Authenticated. Tokens stored.';
    statusEl.className = 'success-message';
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.className = 'warning-message';
  }
}

function hydrateAuthStatus() {
  chrome.storage.local.get(['accessToken', 'refreshToken'], (stored) => {
    const statusEl = document.getElementById('auth-status');
    if (stored.accessToken && stored.refreshToken) {
      statusEl.textContent = 'Ready: tokens found.';
      statusEl.className = 'success-message';
    } else {
      statusEl.textContent = 'Login to store tokens.';
      statusEl.className = 'muted';
    }
  });
}

async function authFetch(path, options, config = {}) {
  const backendBase = await getBackendBase();
  const url = `${backendBase}${path}`;
  const opts = { ...(options || {}) };
  opts.headers = opts.headers || {};

  let tokens = await getTokens();
  if (!config.skipAuth && tokens.accessToken) {
    opts.headers['Authorization'] = `Bearer ${tokens.accessToken}`;
  }

  let response = await fetch(url, opts);

  if (response.status === 401 && tokens.refreshToken && !config.skipRefresh) {
    const refreshed = await refreshTokens(tokens.refreshToken, backendBase);
    if (refreshed) {
      tokens = refreshed;
      opts.headers['Authorization'] = `Bearer ${tokens.accessToken}`;
      response = await fetch(url, opts);
    }
  }

  return response;
}

async function refreshTokens(refreshToken, backendBase) {
  try {
    const res = await fetch(`${backendBase}/api/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    if (!res.ok) return null;

    const body = await res.json();
    await storeTokens(body.access_token, body.refresh_token);
    return { accessToken: body.access_token, refreshToken: body.refresh_token };
  } catch (err) {
    console.error('Refresh failed', err);
    return null;
  }
}

async function getBackendBase() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(['backendUrl'], (result) => {
      const base = (result.backendUrl || 'http://localhost:5000').replace(/\/$/, '');
      resolve(base);
    });
  });
}

async function storeTokens(accessToken, refreshToken) {
  return new Promise((resolve) => {
    chrome.storage.local.set({ accessToken, refreshToken }, () => resolve());
  });
}

async function getTokens() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['accessToken', 'refreshToken'], (stored) => {
      resolve({ accessToken: stored.accessToken, refreshToken: stored.refreshToken });
    });
  });
}