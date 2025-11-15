#!/usr/bin/env python3
"""
Fake News Detection - Quick Run Script
Uses existing data.csv and model.pkl to demonstrate the project
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import warnings

warnings.filterwarnings('ignore')

# Set working directory
os.chdir(r'C:\Users\Adeeb pasha\OneDrive\Documents\Fake_news_detection\Fake_news_Detection')
print(f"Working Directory: {os.getcwd()}\n")

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("=" * 70)
print("STEP 1: Loading Data...")
print("=" * 70)

try:
    df = pd.read_csv("data.csv")
    print(f"✓ Dataset loaded successfully!")
    print(f"  - Shape: {df.shape}")
    print(f"  - Columns: {df.columns.tolist()}")
    print(f"  - Labels (0=Fake, 1=Real): {df['Label'].value_counts().to_dict()}\n")
except FileNotFoundError:
    print("✗ Error: data.csv not found!")
    sys.exit(1)

# ============================================================================
# STEP 2: DATA PREPROCESSING
# ============================================================================
print("=" * 70)
print("STEP 2: Data Preprocessing...")
print("=" * 70)

# Fill missing values
df['Body'].fillna("", inplace=True)
df['Headline'].fillna("", inplace=True)

# Combine Headline and Body
df['Content'] = df['Headline'] + " " + df['Body']

print(f"✓ Missing values filled")
print(f"  - Sample content (first article):")
print(f"    {df['Content'].iloc[0][:150]}...\n")

# ============================================================================
# STEP 3: FEATURE EXTRACTION
# ============================================================================
print("=" * 70)
print("STEP 3: Feature Extraction (TF-IDF)...")
print("=" * 70)

vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', max_df=0.8, min_df=5)
X = vectorizer.fit_transform(df['Content'])
y = df['Label']

print(f"✓ TF-IDF Vectorizer applied")
print(f"  - Feature matrix shape: {X.shape}")
print(f"  - Number of features: {X.shape[1]}\n")

# ============================================================================
# STEP 4: TRAIN-TEST SPLIT
# ============================================================================
print("=" * 70)
print("STEP 4: Train-Test Split (80-20)...")
print("=" * 70)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"✓ Data split completed")
print(f"  - Training set size: {X_train.shape[0]}")
print(f"  - Testing set size: {X_test.shape[0]}\n")

# ============================================================================
# STEP 5: MODEL TRAINING
# ============================================================================
print("=" * 70)
print("STEP 5: Model Training (Multinomial Naive Bayes)...")
print("=" * 70)

model = MultinomialNB()
model.fit(X_train, y_train)

print(f"✓ Model trained successfully!\n")

# ============================================================================
# STEP 6: MODEL EVALUATION
# ============================================================================
print("=" * 70)
print("STEP 6: Model Evaluation...")
print("=" * 70)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"✓ Model Performance Metrics:")
print(f"  - Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  - Precision: {precision:.4f}")
print(f"  - Recall:    {recall:.4f}")
print(f"  - F1-Score:  {f1:.4f}\n")

print(f"Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Fake (0)', 'Real (1)']))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"                 Predicted")
print(f"              Fake    Real")
print(f"Actual Fake   {cm[0,0]:4d}   {cm[0,1]:4d}")
print(f"       Real   {cm[1,0]:4d}   {cm[1,1]:4d}\n")

# ============================================================================
# STEP 7: SAVE MODEL
# ============================================================================
print("=" * 70)
print("STEP 7: Saving Model...")
print("=" * 70)

joblib.dump(model, "model_trained.pkl")
joblib.dump(vectorizer, "vectorizer_trained.pkl")
print(f"✓ Model saved as: model_trained.pkl")
print(f"✓ Vectorizer saved as: vectorizer_trained.pkl\n")

# ============================================================================
# STEP 8: TEST WITH SAMPLE ARTICLES
# ============================================================================
print("=" * 70)
print("STEP 8: Sample Predictions...")
print("=" * 70)

sample_texts = [
    "Trump wins re-election in historic landslide victory",
    "Scientists discover new treatment for cancer using innovative approach",
    "Aliens spotted over New York - Government cover-up confirmed",
    "Stock market reaches record high amid economic growth"
]

for i, text in enumerate(sample_texts, 1):
    text_vec = vectorizer.transform([text])
    pred = model.predict(text_vec)[0]
    prob = model.predict_proba(text_vec)[0]
    label = "REAL" if pred == 1 else "FAKE"
    
    print(f"\nSample {i}: {label}")
    print(f"  Text: {text[:60]}...")
    print(f"  Confidence: {max(prob)*100:.2f}%")

print("\n" + "=" * 70)
print("✓ FAKE NEWS DETECTION COMPLETE!")
print("=" * 70 + "\n")
