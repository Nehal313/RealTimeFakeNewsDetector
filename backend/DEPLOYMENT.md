# Fake News Verification Backend - Deployment Guide

## Local Development

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Server
```bash
uvicorn main:app --reload --port 8000
```

### 3. Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Predict
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Breaking news about political scandal"}'

# Full check
curl -X POST http://localhost:8000/full-check \
  -H "Content-Type: application/json" \
  -d '{"text": "Celebrity death news", "headline": "Famous actor dies"}'
```

---

## Deploy to Render

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub

### 2. Create Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Configure:
  - **Name**: fake-news-verification-api
  - **Environment**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - **Root Directory**: `backend`

### 3. Environment Variables
Add in Render dashboard:
- `PYTHON_VERSION`: 3.11.0
- `PORT`: (auto-set by Render)

### 4. Deploy
- Click "Create Web Service"
- Wait 3-5 minutes for deployment
- Your API URL: `https://fake-news-verification-api.onrender.com`

---

## Deploy to Railway

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login
```bash
railway login
```

### 3. Initialize Project
```bash
cd backend
railway init
```

### 4. Deploy
```bash
railway up
```

### 5. Set Start Command
In Railway dashboard:
- Settings → Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Deploy to Heroku

### 1. Create Procfile
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 2. Deploy
```bash
heroku login
heroku create fake-news-verification
git push heroku main
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 8000 |
| PYTHON_VERSION | Python version | 3.11 |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/predict` | POST | ML prediction only |
| `/verify` | POST | Multi-source verification |
| `/full-check` | POST | Complete analysis |
| `/sources` | GET | List trusted sources |

---

## Testing Production

```bash
# Replace with your deployment URL
API_URL="https://your-api.onrender.com"

# Test
curl $API_URL/health
```

---

## Troubleshooting

### Model not loading
- Ensure `model/model.pkl` exists in backend folder
- Check file size (should be ~9-10 MB)

### CORS errors
- CORS is enabled for all origins in main.py
- If issues persist, check browser console

### Slow response
- First request may take 10-15s (cold start on free tier)
- Subsequent requests: < 2 seconds
