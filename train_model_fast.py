import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Load dataset
print("Loading dataset...")
fake = pd.read_csv('Dataset/Fake.csv')
true = pd.read_csv('Dataset/True.csv')

# Sample for faster training - 10K samples
fake_sample = fake.sample(n=5000, random_state=42)
true_sample = true.sample(n=5000, random_state=42)

fake_sample['label'] = 0
true_sample['label'] = 1

df = pd.concat([fake_sample, true_sample], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Total samples: {len(df)}")

# Prepare
df['combined'] = df['title'].fillna('') + ' ' + df['text'].fillna('')

# Split
X_train, X_test, y_train, y_test = train_test_split(
    df['combined'], df['label'], test_size=0.2, random_state=42
)

print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# Train
print("\nTraining...")
pipe = Pipeline([
    ('vect', CountVectorizer(max_features=5000)),
    ('tfidf', TfidfTransformer()),
    ('clf', LogisticRegression(max_iter=500))
])

pipe.fit(X_train, y_train)

# Evaluate
train_score = pipe.score(X_train, y_train)
test_score = pipe.score(X_test, y_test)

print(f"\n✓ Training accuracy: {train_score*100:.2f}%")
print(f"✓ Test accuracy: {test_score*100:.2f}%")

# Save
joblib.dump(pipe, 'model/model.pkl')
print(f"\n✓ Model saved to model/model.pkl")

# Test
print("\n--- Quick Test ---")
tests = [
    "President announces new economic policy",
    "SHOCKING secret revealed! Click NOW!",
    "Study shows climate change effects"
]

for text in tests:
    pred = pipe.predict([text])[0]
    prob = pipe.predict_proba([text])[0]
    label = "FAKE" if pred == 0 else "REAL"
    conf = max(prob) * 100
    print(f"{label} ({conf:.0f}%): {text}")
