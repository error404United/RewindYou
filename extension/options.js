document.addEventListener("DOMContentLoaded", () => {
  // Load saved backend URL if it exists
  chrome.storage.sync.get(["backendUrl"], (result) => {
    if (result.backendUrl) {
      document.getElementById("backend-url").value = result.backendUrl;
    } else {
      document.getElementById("backend-url").value = "http://localhost:5000";
    }
  });

  // Save backend URL when button is clicked
  document.getElementById("save-button").addEventListener("click", () => {
    const backendUrl = document.getElementById("backend-url").value.trim().replace(/\/$/, "");

    chrome.storage.sync.set({ backendUrl: backendUrl }, () => {
      const successMessage = document.getElementById("success-message");
      successMessage.style.display = "block";

      // Hide success message after 2 seconds
      setTimeout(() => {
        successMessage.style.display = "none";
      }, 2000);
    });
  });
});