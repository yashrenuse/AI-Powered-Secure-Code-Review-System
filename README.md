# AI-Powered Secure Code Review System

## Project Overview

The AI-Powered Secure Code Review System is an intelligent platform designed to automate the code review process for GitHub Pull Requests. The system combines Artificial Intelligence, Static Code Analysis, and Machine Learning techniques to identify security vulnerabilities, coding issues, and performance problems in source code before deployment.

The platform automatically monitors GitHub Pull Requests, analyzes modified code files, performs static analysis using industry-standard tools, generates AI-powered review reports, classifies vulnerability severity levels, and displays results through an interactive dashboard.

---

## Problem Statement

Manual code reviews are time-consuming, inconsistent, and highly dependent on reviewer expertise. Critical security vulnerabilities such as SQL Injection, Cross-Site Scripting (XSS), API Key Exposure, Hardcoded Credentials, and Command Injection may remain undetected.

This project aims to automate the review process using AI and machine learning to improve software security, code quality, and development efficiency.

---

## Objectives

* Automate GitHub Pull Request Reviews
* Detect Security Vulnerabilities
* Improve Code Quality Assessment
* Generate AI-Based Review Suggestions
* Classify Severity Levels
* Provide Centralized Security Dashboard
* Reduce Manual Review Effort

---

## Technologies Used

### Backend

* Python
* FastAPI

### AI Model

* Groq API
* Llama 3.3 70B Versatile

### Static Analysis Tools

* Pylint
* Flake8
* Bandit

### Database

* SQLite

### Frontend

* HTML
* CSS
* Jinja2 Templates

### Version Control

* Git
* GitHub Webhooks

### Machine Learning

* TF-IDF Vectorization
* Logistic Regression
* Random Forest
* Naive Bayes
* Support Vector Machine (SVM)

---

## System Workflow

1. Developer creates Pull Request on GitHub
2. GitHub Webhook sends event to FastAPI server
3. Modified code is extracted
4. Static analysis is performed
5. AI model reviews the code
6. Security vulnerabilities are detected
7. Severity level is assigned
8. Results are stored in SQLite database
9. Review report is posted back to GitHub
10. Dashboard displays review history

---

## Dataset Information

Dataset Name:
Security Vulnerabilities Dataset

Features:

* Title
* Date
* Severity
* Summary
* Link

Total Records:
3350+

Severity Classes:

* Critical
* High
* Moderate
* Low

---

## Machine Learning Results

| Model               | Accuracy |
| ------------------- | -------- |
| Logistic Regression | 54.23%   |
| Random Forest       | 53.43%   |
| Naive Bayes         | 56.92%   |
| SVM                 | 56.31%   |

Best Performing Model:
Support Vector Machine (SVM)

---

## Key Features

* Automated Code Review
* Security Vulnerability Detection
* Severity Classification
* AI Generated Recommendations
* GitHub Integration
* Interactive Dashboard
* Static Analysis Integration
* Machine Learning Evaluation

---

## Limitations

* Currently optimized for Python code
* AI responses depend on LLM output quality
* Dataset imbalance affects classification accuracy
* Requires internet connection for AI analysis

---

## Future Enhancements

* Multi-language Support
* Deep Learning Models
* Real-Time Monitoring
* Advanced Vulnerability Prediction
* CI/CD Integration
* Cloud Deployment

---

## Author

Yash Renuse

Final Year B.E. Project

Artificial Intelligence & Machine Learning
