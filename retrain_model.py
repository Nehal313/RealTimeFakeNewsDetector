import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv('data.csv')

# Prepare data - combine Headline and Body
df['text'] = df['Headline'].fillna('') + ' ' + df['Body'].fillna('')
X = df['text']
y = df['Label']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create pipeline
pipe = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', LogisticRegression(max_iter=1000))
])

# Train
print("Training model...")
pipe.fit(X_train, y_train)

# Save
joblib.dump(pipe, 'model/model.pkl')

# Test
score = pipe.score(X_test, y_test)
print(f"Model trained and saved to model/model.pkl")
print(f"Test accuracy: {score*100:.2f}%")

# Quick prediction test
test_text = ["Breaking news: major political scandal uncovered"]
pred = pipe.predict(test_text)
prob = pipe.predict_proba(test_text)
print(f"\nTest prediction: {pred[0]}")
print(f"Confidence: {prob[0]}")
