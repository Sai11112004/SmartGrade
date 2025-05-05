import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import random

# Generate sample data for 50 students per year in each department
departments = ['CSE', 'ECE', 'EEE', 'IT']
years = [1, 2, 3, 4]
data = []

for dept in departments:
    for year in years:
        for i in range(50):
            student_id = f"{dept}{year}{i+1:03d}"
            subject1 = random.uniform(60, 100)
            subject2 = random.uniform(60, 100)
            subject3 = random.uniform(60, 100)
            subject4 = random.uniform(60, 100)
            subject5 = random.uniform(60, 100)
            attendance = random.uniform(75, 100)
            assignment_score = random.uniform(70, 100)
            
            # Calculate average score
            avg_score = (subject1 + subject2 + subject3 + subject4 + subject5) / 5
            
            # Determine grade based on performance
            if avg_score >= 90 and attendance >= 90 and assignment_score >= 90:
                grade = 'A'
            elif avg_score >= 80 and attendance >= 85 and assignment_score >= 85:
                grade = 'B'
            elif avg_score >= 70 and attendance >= 80 and assignment_score >= 80:
                grade = 'C'
            elif avg_score >= 60 and attendance >= 75 and assignment_score >= 75:
                grade = 'D'
            else:
                grade = 'F'
            
            # Generate parent phone number (10% chance of no phone number)
            parent_phone = None
            if random.random() > 0.1:
                parent_phone = f"+91{random.randint(7000000000, 9999999999)}"
            
            data.append({
                'student_id': student_id,
                'department': dept,
                'year': year,
                'subject1': round(subject1, 2),
                'subject2': round(subject2, 2),
                'subject3': round(subject3, 2),
                'subject4': round(subject4, 2),
                'subject5': round(subject5, 2),
                'attendance': round(attendance, 2),
                'assignment_score': round(assignment_score, 2),
                'predicted_grade': grade,
                'parent_phone': parent_phone
            })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('student_data.csv', index=False)

# Prepare data for ML model
X = df[['subject1', 'subject2', 'subject3', 'subject4', 'subject5', 'attendance', 'assignment_score']]
y = df['predicted_grade']

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
import joblib
joblib.dump(model, 'grade_predictor_model.joblib')

print("Data generation and model training completed successfully!") 