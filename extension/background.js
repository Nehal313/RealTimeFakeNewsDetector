// Background service worker for Chrome Extension

// Handle installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Fake News Detector extension installed');
  
  // Set default configuration
  chrome.storage.sync.get(['apiUrl'], (result) => {
    if (!result.apiUrl) {
      chrome.storage.sync.set({ 
        apiUrl: 'http://localhost:8000' 
      });
    }
  });
});

// Handle extension icon click (optional custom behavior)
chrome.action.onClicked.addListener((tab) => {
  console.log('Extension icon clicked on tab:', tab.id);
});

console.log('Background service worker loaded');
