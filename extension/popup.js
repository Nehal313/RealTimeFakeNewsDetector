// Popup script - handles UI logic and API communication

// Configuration
let API_URL = 'http://localhost:8000';

// DOM Elements
const analyzeBtn = document.getElementById('analyze-btn');
const analyzeSelectionBtn = document.getElementById('analyze-selection-btn');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const errorDiv = document.getElementById('error');
const apiUrlInput = document.getElementById('api-url');
const saveConfigBtn = document.getElementById('save-config');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadConfig();
  attachEventListeners();
});

/**
 * Load saved configuration
 */
function loadConfig() {
  chrome.storage.sync.get(['apiUrl'], (result) => {
    if (result.apiUrl) {
      API_URL = result.apiUrl;
      apiUrlInput.value = API_URL;
    }
  });
}

/**
 * Save configuration
 */
function saveConfig() {
  const url = apiUrlInput.value.trim();
  if (!url) {
    showError('Please enter a valid API URL');
    return;
  }
  
  API_URL = url;
  chrome.storage.sync.set({ apiUrl: url }, () => {
    showTemporaryMessage('Configuration saved!');
  });
}

/**
 * Attach event listeners
 */
function attachEventListeners() {
  analyzeBtn.addEventListener('click', analyzePage);
  analyzeSelectionBtn.addEventListener('click', analyzeSelection);
  saveConfigBtn.addEventListener('click', saveConfig);
}

/**
 * Analyze entire page
 */
async function analyzePage() {
  try {
    showLoading();
    
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Extract text from page
    const response = await chrome.tabs.sendMessage(tab.id, { 
      action: 'extractPageText' 
    });
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to extract text');
    }
    
    // Analyze with API
    await analyzeText(response.text, response.headline);
    
  } catch (error) {
    showError(error.message);
  }
}

/**
 * Analyze selected text
 */
async function analyzeSelection() {
  try {
    showLoading();
    
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Extract selected text
    const response = await chrome.tabs.sendMessage(tab.id, { 
      action: 'extractSelectedText' 
    });
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to extract selection');
    }
    
    // Analyze with API
    await analyzeText(response.text, response.headline);
    
  } catch (error) {
    showError(error.message);
  }
}

/**
 * Call API to analyze text
 */
async function analyzeText(text, headline) {
  try {
    if (!text || text.length < 10) {
      throw new Error('Text is too short to analyze');
    }
    
    // Call full-check endpoint
    const response = await fetch(`${API_URL}/full-check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        headline: headline || text.substring(0, 200)
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    
    const data = await response.json();
    displayResults(data);
    
  } catch (error) {
    throw error;
  }
}

/**
 * Display analysis results
 */
function displayResults(data) {
  hideLoading();
  hideError();
  resultsDiv.classList.remove('hidden');
  
  // ML Prediction
  const mlLabel = document.getElementById('ml-label');
  const mlPrediction = document.getElementById('ml-prediction');
  const confidenceFill = document.getElementById('confidence-fill');
  const confidenceValue = document.getElementById('confidence-value');
  
  mlLabel.textContent = data.model_prediction;
  mlPrediction.className = 'prediction-badge';
  
  if (data.model_prediction === 'REAL') {
    mlPrediction.classList.add('real');
  } else {
    mlPrediction.classList.add('fake');
  }
  
  const confidence = Math.round(data.model_confidence * 100);
  confidenceFill.style.width = `${confidence}%`;
  confidenceValue.textContent = `${confidence}%`;
  
  // Verification Status
  const verificationLabel = document.getElementById('verification-label');
  const verificationStatus = document.getElementById('verification-status');
  
  verificationLabel.textContent = data.verification_status;
  verificationStatus.className = 'verification-badge';
  
  if (data.verification_status.toLowerCase().includes('verified')) {
    verificationStatus.classList.add('verified');
  } else if (data.verification_status.toLowerCase().includes('unverified')) {
    verificationStatus.classList.add('unverified');
  } else if (data.verification_status.toLowerCase().includes('contradictory')) {
    verificationStatus.classList.add('contradictory');
  } else {
    verificationStatus.classList.add('breaking');
  }
  
  // Sources Count
  const sourcesCount = document.getElementById('sources-count');
  sourcesCount.textContent = data.matching_sources.length;
  
  // Sources List
  const sourcesList = document.getElementById('sources-list');
  sourcesList.innerHTML = '';
  
  if (data.matching_sources.length > 0) {
    data.matching_sources.forEach(source => {
      const score = data.similarity_scores[source];
      const scorePercent = Math.round(score * 100);
      
      const sourceDiv = document.createElement('div');
      sourceDiv.className = 'source-item';
      sourceDiv.innerHTML = `
        <span class="source-name">${capitalizeSource(source)}</span>
        <span class="source-score">${scorePercent}%</span>
      `;
      sourcesList.appendChild(sourceDiv);
    });
  } else {
    sourcesList.innerHTML = '<p class="no-sources">No matching sources found</p>';
  }
  
  // Keywords
  const keywordsList = document.getElementById('keywords-list');
  keywordsList.innerHTML = '';
  
  if (data.keywords && data.keywords.length > 0) {
    data.keywords.forEach(keyword => {
      const keywordSpan = document.createElement('span');
      keywordSpan.className = 'keyword-tag';
      keywordSpan.textContent = keyword;
      keywordsList.appendChild(keywordSpan);
    });
  } else {
    keywordsList.innerHTML = '<span class="keyword-tag">No keywords</span>';
  }
  
  // Summary
  const summaryText = document.getElementById('summary-text');
  if (data.summary && data.summary.length > 0) {
    summaryText.innerHTML = `<p>${data.summary}</p>`;
  } else {
    summaryText.innerHTML = '<p class="no-data">No summary available</p>';
  }
  
  // Key Sentences
  const keySentencesList = document.getElementById('key-sentences-list');
  keySentencesList.innerHTML = '';
  
  if (data.key_sentences && data.key_sentences.length > 0) {
    data.key_sentences.forEach((sentence, index) => {
      const sentenceDiv = document.createElement('div');
      sentenceDiv.className = 'key-sentence-item';
      sentenceDiv.innerHTML = `
        <span class="sentence-number">${index + 1}</span>${sentence}
      `;
      keySentencesList.appendChild(sentenceDiv);
    });
  } else {
    keySentencesList.innerHTML = '<p class="no-data">No key insights available</p>';
  }
  
  // Similarity Scores
  const scoresList = document.getElementById('scores-list');
  scoresList.innerHTML = '';
  
  const scores = data.similarity_scores;
  if (scores && Object.keys(scores).length > 0) {
    Object.entries(scores)
      .sort((a, b) => b[1] - a[1])
      .forEach(([source, score]) => {
        const scorePercent = Math.round(score * 100);
        
        const scoreDiv = document.createElement('div');
        scoreDiv.className = 'score-item';
        scoreDiv.innerHTML = `
          <span class="score-source">${capitalizeSource(source)}</span>
          <div class="score-bar-container">
            <div class="score-bar-fill" style="width: ${scorePercent}%"></div>
          </div>
          <span class="score-value">${scorePercent}%</span>
        `;
        scoresList.appendChild(scoreDiv);
      });
  } else {
    scoresList.innerHTML = '<p class="no-data">No similarity data</p>';
  }
}

/**
 * UI State Management
 */
function showLoading() {
  loadingDiv.classList.remove('hidden');
  resultsDiv.classList.add('hidden');
  errorDiv.classList.add('hidden');
}

function hideLoading() {
  loadingDiv.classList.add('hidden');
}

function showError(message) {
  hideLoading();
  resultsDiv.classList.add('hidden');
  errorDiv.classList.remove('hidden');
  document.getElementById('error-message').textContent = message;
}

function hideError() {
  errorDiv.classList.add('hidden');
}

function showTemporaryMessage(message) {
  const originalText = saveConfigBtn.textContent;
  saveConfigBtn.textContent = message;
  saveConfigBtn.style.background = '#28a745';
  
  setTimeout(() => {
    saveConfigBtn.textContent = originalText;
    saveConfigBtn.style.background = '';
  }, 2000);
}

/**
 * Utility functions
 */
function capitalizeSource(source) {
  const sourceNames = {
    'reuters': 'Reuters',
    'apnews': 'AP News',
    'bbc': 'BBC',
    'thehindu': 'The Hindu',
    'timesofindia': 'Times of India',
    'ndtv': 'NDTV'
  };
  
  return sourceNames[source] || source.toUpperCase();
}
