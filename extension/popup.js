import { icons } from "./icons.js";

// Initialize when popup opens
document.addEventListener("DOMContentLoaded", () => {
  document
    .getElementById("extractButton")
    .addEventListener("click", extractData);
});

async function extractData() {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML =
    '<div class="loading"><div class="loader"></div><p>Extracting page data...</p></div>';

  try {
    // Get the active tab
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });

    // Check if it's a valid webpage
    if (!tab.url.startsWith("http://") && !tab.url.startsWith("https://")) {
      throw new Error(
        "Please navigate to a valid webpage (http:// or https://)",
      );
    }
      if (
      tab.url.includes("youtube.com/watch") ||
      tab.url.includes("youtu.be")
    ) {
      try {
        // Send ONLY the URL to backend transcript endpoint
        const response = await fetch(
          "http://localhost:5000/api/save-youtube-transcript",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ url: tab.url }),
          },
        );

        if (!response.ok) {
          throw new Error("Failed to save YouTube transcript");
        }

        const data = await response.json();

        resultDiv.innerHTML = `
          <div class="success-message">
            ✅ YouTube transcript saved locally<br/>
            <small>${data.filename}</small>
          </div>
        `;
      } catch (err) {
        resultDiv.innerHTML = `<div class="error">Error: ${err.message}</div>`;
      }

      // ⛔ IMPORTANT: stop here so normal page extraction does NOT run
      return;
    }
    
    // Send message to content script
    chrome.tabs.sendMessage(
      tab.id,
      { action: "extractPageData" },
      async (response) => {
        if (chrome.runtime.lastError) {
          resultDiv.innerHTML = `<div class="error">Error: ${chrome.runtime.lastError.message}<br><br>Please make sure you're on a valid webpage and try reloading the page.</div>`;
          return;
        }

        if (response && response.success) {
          console.log("Extracted Data:", response.data);

          // Display the extracted data
          displayExtractedData(response.data);

          // Send to backend
          try {
            await sendToBackend(response.data);
            const statusMsg = document.createElement("div");
            statusMsg.className = "success-message";
            statusMsg.textContent = "Data sent to backend successfully!";
            resultDiv.insertBefore(statusMsg, resultDiv.firstChild);
          } catch (backendError) {
            const errorMsg = document.createElement("div");
            errorMsg.className = "warning-message";
            errorMsg.textContent =
              "Failed to send to backend: " + backendError.message;
            resultDiv.insertBefore(errorMsg, resultDiv.firstChild);
          }
        } else {
          throw new Error(response?.error || "Failed to extract data");
        }
      },
    );
  } catch (error) {
    console.error("Error:", error);
    resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
  }
}

function displayExtractedData(data) {
  const resultDiv = document.getElementById("result");
  document.body.classList.replace("compact", "expanded");

  // Truncate content for display (show first 500 characters)
  const contentPreview =
    data.articleContent && data.articleContent.length > 500
      ? data.articleContent /* .substring(0, 500) + "..." */
      : data.articleContent || "No content available";

  let html = `
    <div class="extracted-data">
      <h3>Extracted Page Data</h3>
      <div class="data-section">
        <div class="info-row">${icons.link}<a href="${data.url}" target="_blank" class="info-link">${data.url}</a></div>

        <div class="info-row">${icons.file}<span class="info-text">${data.title}</span></div>

        <div class="info-row">${icons.calendar}<span class="info-text">${data.date}</span></div>

        <div class="info-row">${icons.clock}<span class="info-text">${data.time}</span></div>
      </div>

      <div class="data-section">
        <div class="content-preview">${contentPreview}</div>
        <div class="data-section-stats">
          <p><strong>Word Count:</strong> ${data.wordCount}</p>
          <p><strong>Paragraph Count:</strong> ${data.paragraphCount}</p>
        </div>
      </div>
  `;

  // Add metadata if available
  if (data.metaDescription || data.metaKeywords || data.author) {
    html += `
      <div class="data-section">`;

    if (data.metaDescription) {
      html += `<div class="meta-block"><div class="meta-label">Description</div><p class="meta-description">${data.metaDescription}</p></div>`;
    }

    if (data.metaKeywords) {
      const keywords = data.metaKeywords
        .split(",")
        .map((k) => k.trim())
        .filter(Boolean);

      html += `<div class="meta-block"><div class="meta-label">Keywords</div><div class="meta-tags">${keywords.map((k) => `<span class="tag">${k}</span>`).join("")}</div></div>`;
    }

    if (data.author) {
      html += `<div class="meta-block"><div class="meta-label">Author</div><p class="meta-author">${data.author}</p></div>`;
    }

    html += `</div>`;
  }

  html += `</div>`;
  resultDiv.innerHTML = html;
}

async function sendToBackend(data) {
  // Get custom backend URL from storage, or use default
  return new Promise((resolve, reject) => {
    chrome.storage.sync.get(["backendUrl"], async (result) => {
      const BACKEND_URL =
        result.backendUrl || "http://localhost:5000/api/save-page-data";

      try {
        const response = await fetch(BACKEND_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          throw new Error(`Backend responded with status: ${response.status}`);
        }

        const resultData = await response.json();
        console.log("Backend response:", resultData);
        resolve(resultData);
      } catch (error) {
        console.error("Backend error:", error);
        reject(error);
      }
    });
  });
}
