import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import os

np.random.seed(42)
n_samples = 1000

data = pd.DataFrame({
    'age': np.random.randint(18, 65, n_samples),
    'income': np.random.normal(50000, 15000, n_samples),
    'loan_amount': np.random.normal(10000, 3000, n_samples),
    'credit_score': np.random.randint(300, 850, n_samples),
    'employment_years': np.random.randint(0, 20, n_samples),
    'education_level': np.random.choice(['high_school', 'bachelor', 'master', 'phd'], n_samples)
})

le = LabelEncoder()
data['education_level'] = le.fit_transform(data['education_level'])

data['will_default'] = (
    (data['loan_amount'] > 15000) |
    (data['credit_score'] < 600) |
    (data['income'] < 30000)
).astype(int)

X = data.drop(columns=['will_default'])
y = data['will_default']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

joblib.dump(model, os.path.join('src', 'models', 'loan_model.pkl'))

print("Replaced model with XGBoost and saved.")
