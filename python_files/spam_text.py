
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# --- Load and preprocess data ---
import os

# Always resolve path relative to project root
csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "mail_data.csv")
df = pd.read_csv(csv_path, encoding="latin1")
data = df.where((pd.notnull(df)), "")
data.loc[data['Category'] == 'spam', 'Category'] = 0
data.loc[data['Category'] == 'ham', 'Category'] = 1
X = data["Message"]
Y = data["Category"]
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=3)

# --- Feature extraction and model training ---
feature_extraction = TfidfVectorizer(min_df=1, stop_words='english', lowercase=True)
X_train_features = feature_extraction.fit_transform(X_train)
X_test_features = feature_extraction.transform(X_test)
Y_train = Y_train.astype('int')
Y_test = Y_test.astype('int')
Model = LogisticRegression()
Model.fit(X_train_features, Y_train)

# --- Accuracy (optional, for debugging) ---
# prediction_on_training_data = Model.predict(X_train_features)
# accuracy_on_training_data = accuracy_score(Y_train, prediction_on_training_data)
# prediction_on_test_data = Model.predict(X_test_features)
# accuracy_on_test_data = accuracy_score(Y_test, prediction_on_test_data)

# --- Prediction function for Flask ---
def spam_text(text):
    input_data_features = feature_extraction.transform([text])
    prediction = Model.predict(input_data_features)
    score = Model.predict_proba(input_data_features)[0][prediction[0]]
    if prediction[0] == 1:
        result = 'Ham mail'
    else:
        result = 'Spam mail'
    return result, round(score * 100, 2)
