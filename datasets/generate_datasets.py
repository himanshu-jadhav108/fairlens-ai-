import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 1000

# 1. Hiring Bias Dataset
# Bias against 'Female' gender
gender = np.random.choice(['Male', 'Female'], size=n_samples, p=[0.55, 0.45])
experience = np.random.randint(0, 15, size=n_samples)
education = np.random.choice(['Bachelors', 'Masters', 'PhD'], size=n_samples, p=[0.6, 0.3, 0.1])
tech_score = np.random.randint(40, 100, size=n_samples)

# Give a slight boost to tech score for Masters/PhD to make it realistic
tech_score = np.where(education == 'Masters', tech_score + 5, tech_score)
tech_score = np.where(education == 'PhD', tech_score + 10, tech_score)
tech_score = np.clip(tech_score, 40, 100)

# Base probability
prob = (experience / 15) * 0.3 + (tech_score / 100) * 0.5

# Bias term: deduct from females
bias_penalty = np.where(gender == 'Female', 0.25, 0.0)
prob = prob - bias_penalty

# Add some noise
prob += np.random.normal(0, 0.1, size=n_samples)
hired = (prob > 0.5).astype(int)

df_hiring = pd.DataFrame({
    'Gender': gender,
    'Experience_Years': experience,
    'Education_Level': education,
    'Technical_Score': tech_score,
    'Hired': hired
})
df_hiring.to_csv('hiring_bias.csv', index=False)
print("Generated hiring_bias.csv")

# 2. Loan Approval Bias Dataset
# Bias against 'Young' age group
age_group = np.random.choice(['Young', 'Adult', 'Senior'], size=n_samples, p=[0.3, 0.5, 0.2])
income = np.random.randint(30000, 150000, size=n_samples)
credit_score = np.random.randint(500, 850, size=n_samples)
loan_amount = np.random.randint(5000, 50000, size=n_samples)

# Normalize features
norm_income = income / 150000
norm_credit = credit_score / 850
norm_loan = loan_amount / 50000

# Base probability
prob_loan = (norm_income * 0.4) + (norm_credit * 0.5) - (norm_loan * 0.2)

# Bias term: penalize 'Young' group significantly
bias_penalty_loan = np.where(age_group == 'Young', 0.2, 0.0)
prob_loan = prob_loan - bias_penalty_loan

prob_loan += np.random.normal(0, 0.05, size=n_samples)
approved = (prob_loan > 0.4).astype(int)

df_loan = pd.DataFrame({
    'Age_Group': age_group,
    'Income': income,
    'Credit_Score': credit_score,
    'Loan_Amount': loan_amount,
    'Approved': approved
})
df_loan.to_csv('loan_approval_bias.csv', index=False)
print("Generated loan_approval_bias.csv")
