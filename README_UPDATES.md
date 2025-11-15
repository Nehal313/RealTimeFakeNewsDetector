# Fake News Detection - Production Updates

## 📊 Project Overview

This repository contains a **production-ready fake news detection system** with 93.52% accuracy. The model uses machine learning to classify news articles as real or fake using TF-IDF vectorization and Multinomial Naive Bayes classification.

### Latest Updates (November 2025)

**Developed comprehensive data pipeline with 4,009 articles (53% fake, 47% real) achieving 93.52% accuracy**
- Enhanced dataset preprocessing with comprehensive missing value handling
- Cross-platform compatible file path resolution
- Full data exploration and statistical analysis

**Implemented TF-IDF feature extraction and Multinomial Naive Bayes classifier with 96.83% recall rate**
- 5,000 feature TF-IDF vectorization with stop word removal
- Optimized Naive Bayes classifier achieving industry-leading recall
- Comprehensive feature analysis and importance tracking

**Created standalone Python script (run_fake_news_detection.py) for batch processing and real-time predictions**
- End-to-end pipeline from data loading to model evaluation
- Real-time prediction capability on custom text inputs
- 8-step comprehensive workflow with detailed logging

**Added pre-trained model (model_trained.pkl) and vectorizer for immediate deployment without retraining**
- Serialized trained models for instant inference
- Vectorizer snapshot for consistent feature extraction
- Production-ready deployment configuration

**Fixed hardcoded file paths in notebook for cross-platform compatibility and improved usability**
- Dynamic working directory detection
- Relative path resolution for all data files
- Windows/Linux/Mac compatible path handling

**Includes precision (89.12%), recall (96.83%), and F1-score (92.82%) metrics for production deployment**
- Confusion matrix analysis with detailed breakdown
- Classification report with per-class metrics
- Model validation on 802 test samples

---

## 🎯 Model Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | 93.52% |
| **Precision** | 89.12% |
| **Recall** | 96.83% |
| **F1-Score** | 92.82% |
| **Test Set Size** | 802 articles |
| **Training Set Size** | 3,207 articles |

### Confusion Matrix
```
                 Predicted
              Fake    Real
Actual Fake    414     41
       Real     11    336
```

---

## 📁 Files & Structure

### Core Files
- **`run_fake_news_detection.py`** - Complete production pipeline with real-time predictions
- **`Fakenewsdetection.ipynb`** - Updated Jupyter notebook with fixed file paths
- **`data.csv`** - 4,009 news articles with labels (1=Real, 0=Fake)
- **`model.pkl`** - Original pre-trained model

### Generated Files
- **`model_trained.pkl`** - Newly trained Naive Bayes classifier
- **`vectorizer_trained.pkl`** - TF-IDF vectorizer for feature extraction
- **`.gitignore`** - Excludes large binary model files from version control

---

## 🚀 Quick Start

### Prerequisites
```bash
# Create conda environment
conda create -n fake-news python=3.11 -y
conda activate fake-news

# Install dependencies
pip install -r requirements.txt
```

### Run the Model

**Option 1: Standalone Python Script**
```bash
python run_fake_news_detection.py
```

**Option 2: Jupyter Notebook**
```bash
jupyter notebook Fakenewsdetection.ipynb
```

**Option 3: Live Predictions**
```python
import joblib

# Load model and vectorizer
model = joblib.load('model_trained.pkl')
vectorizer = joblib.load('vectorizer_trained.pkl')

# Make prediction
text = "Breaking news about latest scientific discovery"
prediction = model.predict(vectorizer.transform([text]))[0]
confidence = model.predict_proba(vectorizer.transform([text]))[0]

print(f"Classification: {'REAL' if prediction == 1 else 'FAKE'}")
print(f"Confidence: {max(confidence)*100:.2f}%")
```

---

## 📊 Data Insights

- **Total Articles**: 4,009
- **Fake News**: 2,137 (53.3%)
- **Real News**: 1,872 (46.7%)
- **Features**: URL, Headline, Body, Label
- **Train-Test Split**: 80-20 (3,207 / 802)

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.11 |
| **ML Library** | scikit-learn |
| **Data Processing** | pandas, numpy |
| **Feature Extraction** | TF-IDF Vectorizer |
| **Classification** | Multinomial Naive Bayes |
| **Serialization** | joblib |
| **NLP** | NLTK, WordCloud |
| **Deployment** | Flask (optional) |

---

## 📈 Workflow

```
1. Load Data (4,009 articles)
   ↓
2. Preprocess (handle missing values, combine text)
   ↓
3. Feature Extraction (TF-IDF: 5,000 features)
   ↓
4. Train-Test Split (80-20)
   ↓
5. Model Training (Multinomial Naive Bayes)
   ↓
6. Evaluation (accuracy, precision, recall, F1)
   ↓
7. Save Models (pickle serialization)
   ↓
8. Real-Time Predictions (on custom text)
```

---

## 🎓 Key Features

✅ **93.52% Accuracy** - Industry-leading classification performance  
✅ **Real-Time Predictions** - Instant article classification  
✅ **Cross-Platform Compatible** - Works on Windows, Linux, macOS  
✅ **Production Ready** - Pre-trained models included  
✅ **Comprehensive Metrics** - Precision, recall, F1-score, confusion matrix  
✅ **Easy Integration** - Simple Python API for predictions  
✅ **Well-Documented** - Clear code comments and docstrings  
✅ **Scalable** - Can handle batch processing  

---

## 📝 Usage Examples

### Single Article Prediction
```python
from run_fake_news_detection import predict_article

result = predict_article("Your news headline here")
print(f"Result: {result['label']} (Confidence: {result['confidence']:.2f}%)")
```

### Batch Processing
```python
articles = [
    "Trump wins re-election in historic landslide victory",
    "Scientists discover new treatment for cancer",
    "Aliens spotted over New York - Government cover-up confirmed"
]

for article in articles:
    prediction = model.predict(vectorizer.transform([article]))
    print(f"Article: {article[:50]}... -> {'REAL' if prediction[0] == 1 else 'FAKE'}")
```

---

## 🔮 Future Improvements

- [ ] Implement deep learning models (LSTM, BERT)
- [ ] Add multi-language support
- [ ] Create REST API endpoint
- [ ] Develop web UI for predictions
- [ ] Implement model versioning and A/B testing
- [ ] Add explainability features (SHAP, LIME)
- [ ] Expand dataset with recent news articles
- [ ] Implement automated model retraining pipeline

---

## 📞 Support

For issues, feature requests, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Contact: adeebpasha123@gmail.com

---

## 📄 License

This project is open source and available under the MIT License.

---

**Last Updated**: November 15, 2025  
**Status**: ✅ Production Ready  
**Accuracy**: 93.52%  
**Model Version**: 1.0
