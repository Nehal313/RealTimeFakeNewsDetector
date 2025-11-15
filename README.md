# 🔍 Fake News Detection & Verification System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Production-ready AI system combining ML classification, multi-source verification, RAG-powered evidence retrieval, and an intelligent AI assistant for comprehensive fake news detection.**

**Author:** Mohammed Nehal

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Chrome Extension](#chrome-extension)
- [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This system provides real-time fake news detection through multiple layers of analysis:

1. **ML Classification** - Machine learning model (98.2% accuracy) for instant fake/real prediction
2. **Multi-Source Verification** - Cross-checks claims against 6+ trusted news outlets in real-time
3. **RAG Evidence Retrieval** - Vector similarity search for relevant evidence from knowledge base
4. **AI Assistant** - 8 specialized AI endpoints for claim extraction, summarization, explanations, and more
5. **Browser Integration** - Chrome extension with color-coded verification UI

### Key Capabilities:
- ⚡ Sub-2-second response time
- 🌐 Multi-source verification (Reuters, AP News, BBC, The Hindu, TOI, NDTV)
- 🤖 AI-powered claim extraction and evidence retrieval
- 📝 Advanced summarization (HuggingFace + TF-IDF)
- 🎨 Real-time browser extension with intuitive UI
- 🐳 Fully containerized with Docker

---

## ✨ Features

### Core Features

#### 1. **Fake News Classification**
- Machine learning model trained on 10,000+ articles
- TF-IDF + Logistic Regression pipeline
- 98.2% test accuracy
- Confidence scoring for predictions

#### 2. **Real-Time Multi-Source Verification**
Automatically verifies claims across trusted sources:
- **Global:** Reuters, AP News, BBC
- **India:** The Hindu, Times of India, NDTV
- **Government:** Official .gov domain verification

**Verification Process:**
```
User Article → Extract Keywords → Search Sources → 
Calculate Similarity → Aggregate Results → 
Return: Verified | Unverified | Contradictory | Breaking News
```

#### 3. **Advanced Summarization**
- **Primary:** HuggingFace DistilBART (abstractive)
- **Fallback:** TF-IDF extractive summarization
- Key sentence extraction
- Configurable summary length

#### 4. **RAG (Retrieval-Augmented Generation)**
- FAISS vector store for similarity search
- SentenceTransformer embeddings (384-dim)
- OpenAI embeddings support (optional)
- Evidence retrieval for fact-checking

#### 5. **AI Assistant Module**
8 specialized endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/ai/ask` | Natural language Q&A about articles |
| `/ai/extract-claims` | Extract verifiable claims |
| `/ai/rag-query` | Retrieve evidence via vector search |
| `/ai/draft` | Generate rebuttals, tweets, summaries |
| `/ai/explain` | Explain model reasoning |
| `/ai/feedback` | Log user corrections |
| `/ai/admin/health` | System health check |
| `/ai/admin/stats` | Usage statistics |

#### 6. **Chrome Extension**
- Real-time webpage analysis
- Color-coded verification status:
  - 🟢 **Green** - Verified by multiple sources
  - 🔴 **Red** - Likely fake news
  - 🟡 **Yellow** - Unverified
  - 🟣 **Purple** - Contradictory information
- Analyze full page or selected text
- Configurable API endpoint

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CHROME EXTENSION                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Content.js  │  │   Popup.js   │  │ Background.js│      │
│  │ (Extract Text)│  │ (UI Logic)   │  │ (Service)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                  │                                 │
└─────────┼──────────────────┼─────────────────────────────────┘
          │                  │
          └─────────┬────────┘
                    │ HTTP/JSON
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Core Endpoints                      │  │
│  ├──────────────┬──────────────┬──────────────┐         │  │
│  │  /predict    │   /verify    │ /full-check  │         │  │
│  │  (ML Model)  │ (Multi-Source)│ (Complete)  │         │  │
│  └──────┬───────┴──────┬───────┴──────┬───────┘         │  │
│         │              │              │                  │  │
│         ▼              ▼              ▼                  │  │
│  ┌──────────────────────────────────────────────────┐   │  │
│  │         AI Assistant Module (8 Endpoints)        │   │  │
│  │  /ai/ask | /ai/extract-claims | /ai/rag-query   │   │  │
│  │  /ai/draft | /ai/explain | /ai/feedback         │   │  │
│  └──────┬───────────────┬───────────────┬──────────┘   │  │
│         │               │               │              │  │
└─────────┼───────────────┼───────────────┼──────────────┘
          │               │               │
          ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  ML MODEL    │  │ VECTOR STORE │  │   SCRAPER    │
│              │  │              │  │              │
│ TF-IDF +     │  │ FAISS Index  │  │ BeautifulSoup│
│ Logistic     │  │ Embeddings   │  │ Aiohttp      │
│ Regression   │  │ (384-dim)    │  │              │
│              │  │              │  │ 6 Sources    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Data Flow

1. **User Action** → Extension extracts text from webpage
2. **API Request** → POST to `/full-check` endpoint
3. **ML Prediction** → Model classifies as FAKE/REAL with confidence
4. **Verification** → Scrapes Reuters, AP, BBC, etc. for similar articles
5. **Similarity Scoring** → Cosine similarity using TF-IDF
6. **Summarization** → HuggingFace model generates summary
7. **Claims Extraction** → NLP extracts verifiable claims
8. **RAG Query** → Vector search for supporting evidence
9. **Response** → JSON with prediction, verification, summary, sources
10. **Display** → Extension shows color-coded results

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.115+
- **ML:** scikit-learn 1.7.2, joblib
- **NLP:** NLTK, sentence-transformers
- **Summarization:** HuggingFace Transformers (DistilBART)
- **Vector Store:** FAISS
- **Web Scraping:** aiohttp, BeautifulSoup4
- **Embeddings:** SentenceTransformer (all-MiniLM-L6-v2)

### Chrome Extension
- **Manifest:** V3
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **API Communication:** Fetch API

### Infrastructure
- **Containerization:** Docker, Docker Compose
- **Cache:** Redis (optional)
- **Deployment:** Render / Railway / Heroku compatible

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional)
- Chrome/Edge browser

### Local Setup (Without Docker)

```bash
# 1. Clone repository
git clone https://github.com/AdeebPasha123/Fake-news-detection.git
cd Fake-news-detection

# 2. Setup backend
cd backend
pip install -r requirements.txt

# 3. Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

# 4. Run server
uvicorn main:app --reload --port 8000
```

Server runs at: `http://localhost:8000`

### Docker Setup (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/AdeebPasha123/Fake-news-detection.git
cd Fake-news-detection

# 2. Build and run
docker-compose up --build

# Server runs at http://localhost:8000
```

### Install Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `extension/` folder
5. Extension icon appears in toolbar
6. Click icon → Configure API URL (default: `http://localhost:8000`)

---

## 📚 API Documentation

### Core Endpoints

#### 1. **Predict** - ML Classification Only
```bash
POST /predict
Content-Type: application/json

{
  "text": "Article content here..."
}

Response:
{
  "prediction": "FAKE",
  "confidence": 0.89,
  "label": 0
}
```

#### 2. **Verify** - Multi-Source Verification
```bash
POST /verify
Content-Type: application/json

{
  "text": "Article content",
  "headline": "Optional headline"
}

Response:
{
  "verification_status": "Verified",
  "matching_sources": ["reuters", "bbc", "apnews"],
  "similarity_scores": {
    "reuters": 0.85,
    "bbc": 0.78,
    "apnews": 0.92
  },
  "keywords": ["election", "results", "2024"],
  "timestamp": 1700000000.0
}
```

#### 3. **Full Check** - Complete Analysis
```bash
POST /full-check
Content-Type: application/json

{
  "text": "Full article text...",
  "headline": "Article headline"
}

Response:
{
  "model_prediction": "REAL",
  "model_confidence": 0.94,
  "verification_status": "Verified",
  "matching_sources": ["reuters", "thehindu"],
  "similarity_scores": {...},
  "keywords": [...],
  "summary": "AI-generated summary...",
  "key_sentences": ["Most important sentence 1", ...],
  "timestamp": 1700000000.0
}
```

### AI Assistant Endpoints

#### 4. **Ask** - Q&A with RAG
```bash
POST /ai/ask

{
  "question": "What are the main claims in this article?",
  "context": "Optional article text"
}
```

#### 5. **Extract Claims**
```bash
POST /ai/extract-claims

{
  "text": "Article with multiple claims..."
}

Response:
{
  "claims": [
    {
      "claim": "President signed new climate law",
      "type": "policy",
      "entities": ["President", "Climate Law"],
      "verification_query": "President climate law signed",
      "priority": 4
    }
  ]
}
```

#### 6. **RAG Query** - Evidence Retrieval
```bash
POST /ai/rag-query

{
  "query": "climate change policy 2024",
  "k": 5
}
```

#### 7. **Draft Generator**
```bash
POST /ai/draft

{
  "text": "Article content...",
  "draft_type": "rebuttal"  // Options: rebuttal, summary, tweet, bullets, press_release
}
```

#### 8. **Explain Prediction**
```bash
POST /ai/explain

{
  "text": "Article...",
  "prediction": "FAKE",
  "confidence": 0.87
}
```

#### 9. **User Feedback**
```bash
POST /ai/feedback

{
  "article_text": "...",
  "model_prediction": "FAKE",
  "user_verdict": "REAL",
  "user_comment": "Model was wrong"
}
```

#### 10. **Admin Endpoints**
```bash
GET /ai/admin/health   # System health
GET /ai/admin/stats    # Usage statistics
GET /sources           # List trusted sources
```

### Interactive API Docs
Access Swagger UI at: `http://localhost:8000/docs`

---

## 🧩 Chrome Extension

### Features
- **Analyze Full Page** - Extracts all text from current webpage
- **Analyze Selected Text** - Checks only highlighted text
- **Color-Coded Results:**
  - Green badge = Verified by multiple sources
  - Red badge = Likely fake
  - Yellow badge = Unverified
  - Purple badge = Contradictory information
- **Detailed Breakdown:**
  - ML prediction + confidence
  - Verification status
  - Matching sources with similarity scores
  - Article summary
  - Key insights
  - Important keywords

### Configuration
Click extension icon → Set API URL → Save

Default: `http://localhost:8000`  
Production: `https://your-api.onrender.com`

---

## 🐳 Docker Deployment

### Full Stack with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services
- **backend:** FastAPI server (port 8000)
- **redis:** Redis cache (port 6379)

### Persistent Data
Volumes mounted:
- `.vectordb/` - FAISS index
- `logs/` - Application logs
- `model/` - ML model files

---

## ⚙️ Environment Variables

Create `backend/.env` from `.env.example`:

```bash
# API Keys (optional)
OPENAI_API_KEY=sk-...                    # For OpenAI embeddings
BING_API_KEY=your-bing-key              # For Bing Search API

# Server
PORT=8000

# Paths
VECTORDB_PATH=.vectordb
MODEL_PATH=model/model.pkl

# Redis
REDIS_URL=redis://redis:6379

# Logging
LOG_LEVEL=INFO
```

**Note:** System works without API keys using local models

---

## 📁 Project Structure

```
Fake-news-detection/
├── backend/
│   ├── main.py                 # FastAPI app + core endpoints
│   ├── ai_tasks.py             # AI assistant module
│   ├── search.py               # Multi-source scraping
│   ├── claims.py               # Claim extraction
│   ├── summarize.py            # HuggingFace summarization
│   ├── embeddings.py           # Vector embeddings
│   ├── vectorstore.py          # FAISS vector store
│   ├── utils.py                # NLP utilities
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Container definition
│   ├── .env.example            # Environment template
│   ├── model/
│   │   └── model.pkl           # Trained ML model
│   ├── .vectordb/              # FAISS index (persistent)
│   └── logs/                   # Application logs
│
├── extension/
│   ├── manifest.json           # Extension config (MV3)
│   ├── popup.html              # Extension UI
│   ├── popup.js                # UI logic + API calls
│   ├── content.js              # Page text extraction
│   ├── background.js           # Service worker
│   ├── styles.css              # Styling
│   └── icons/                  # Extension icons
│
├── docker-compose.yaml         # Multi-service orchestration
├── .dockerignore               # Docker ignore rules
└── README.md                   # This file
```

---

## 💻 Development

### Running Tests
```bash
cd backend
pytest tests/
```

### Adding New Sources
Edit `backend/search.py`:
```python
TRUSTED_SOURCES = {
    "newsource": "https://newsource.com/search?q=",
}

# Add extraction logic in extract_headlines()
```

### Updating ML Model
```bash
cd backend
python train_model_fast.py
```

### Populating Vector Store
```python
from vectorstore import get_vector_store

store = get_vector_store()
store.add(
    texts=["Evidence text 1", "Evidence text 2"],
    metadata=[{"source": "reuters"}, {"source": "bbc"}]
)
store.save()
```

---

## 🧪 Testing

### Backend API Test
```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Breaking news about major event"}'
```

### Extension Test
1. Load extension in Chrome
2. Navigate to any news article
3. Click extension icon
4. Click "Analyze Current Page"
5. Verify results display correctly

### Docker Test
```bash
docker-compose up --build
# Wait for services to start
curl http://localhost:8000/ai/admin/health
```

---

## 🚀 Deployment

### Deploy to Render

1. **Create Web Service:**
   - Connect GitHub repository
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables:**
   ```
   PYTHON_VERSION=3.10.0
   PORT=8000
   ```

3. **Deploy** - Render auto-builds on push

### Deploy to Railway

```bash
cd backend
railway init
railway up
```

### Deploy to Heroku

```bash
cd backend
heroku create fake-news-api
git push heroku main
```

### Update Extension API URL
After deployment, update extension:
1. Click extension icon
2. Set API URL to: `https://your-api.onrender.com`
3. Save

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Author

**Mohammed Nehal**

- GitHub: [@AdeebPasha123](https://github.com/AdeebPasha123)
- Project: [Fake News Detection](https://github.com/AdeebPasha123/Fake-news-detection)

---

## 🙏 Acknowledgments

- Scikit-learn for ML pipeline
- HuggingFace for transformer models
- FastAPI for modern Python API framework
- FAISS for efficient similarity search
- All open-source contributors

---

## 📞 Support

For issues, questions, or feature requests:
- Open an [Issue](https://github.com/AdeebPasha123/Fake-news-detection/issues)
- Check [Documentation](https://github.com/AdeebPasha123/Fake-news-detection/wiki)

---

**⭐ Star this repository if you find it helpful!**
