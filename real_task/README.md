# PlaceMux AI Matching Engine

## Overview

PlaceMux is an AI-powered job matching system that connects students with job opportunities based on skills, qualifications, and job requirements.

This project implements:

* Student ↔ Job Feature Space
* Explainable Matching Engine
* Resume Parsing
* Job Description Parsing
* Semantic Matching
* Candidate Ranking
* FastAPI-based Matching API

The system is designed to provide transparent and measurable candidate-job recommendations rather than black-box decisions.

---

## Objectives

The project was developed as part of:

**PlaceMux – Week 2 | Phase 2**

Key goals:

* Define the student-job feature space.
* Build an explainable matching engine.
* Design backend API contracts.
* Generate match scores with reasoning.
* Rank candidates for job opportunities.
* Support real-world resume and job description matching.

---

## Project Structure

```text
real_task/
│
├── app.py
├── requirements.txt
│
├── baseline/
│   ├── matching.py
│   └── metrics.py
│
├── data/
│   ├── students.csv
│   └── jobs.csv
│
├── parsing/
│   ├── skills.py
│   ├── resume_parser.py
│   └── jd_parser.py
│
├── matching/
│   ├── rule_matcher.py
│   ├── semantic_matcher.py
│   └── ranking.py
```

---

## Student ↔ Job Feature Space

### Student Features

* Python Score
* SQL Score
* Machine Learning Score
* CGPA
* Experience
* Projects

### Job Features

* Required Skills
* Minimum CGPA
* Experience Requirements

---

## Matching Methodology

### Rule-Based Matching

Matches candidate skills against required job skills.

Formula:

```text
Skill Match Score =
Matched Skills / Required Skills × 100
```

### Semantic Matching

Uses TF-IDF Vectorization and Cosine Similarity to compare:

* Resume Text
* Job Description Text

Formula:

```text
Semantic Score =
Cosine Similarity × 100
```

### Final Match Score

```text
Final Score =
(0.7 × Rule Match Score)
+
(0.3 × Semantic Score)
```

---

## Explainability

Every recommendation provides:

### Matched Skills

Example:

```json
[
  "python",
  "tensorflow",
  "aws"
]
```

### Missing Skills

Example:

```json
[
  "sql"
]
```

This allows recruiters and candidates to understand why a recommendation was generated.

---

## API Endpoints

### Health Check

```http
GET /
```

Response:

```json
{
  "status": "running"
}
```

---

### Semantic Match

```http
POST /semantic-match
```

Request:

```json
{
  "resume_text": "Python FastAPI TensorFlow Docker AWS",
  "jd_text": "Looking for AI Engineer with Python TensorFlow AWS SQL"
}
```

Response:

```json
{
  "final_score": 82.5,
  "recommendation": "Strong Match",
  "matched_skills": [
    "python",
    "tensorflow",
    "aws"
  ],
  "missing_skills": [
    "sql"
  ],
  "semantic_score": 75.0
}
```

---

## Technologies Used

### Backend

* Python
* FastAPI

### Data Processing

* Pandas
* NumPy

### Machine Learning

* Scikit-Learn
* TF-IDF Vectorizer
* Cosine Similarity

### Development Tools

* VS Code
* Uvicorn
* Git
* GitHub

---

## Installation

Clone the repository:

```bash
git clone <repository_url>
cd real_task
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn app:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Evaluation Metrics

The matching system can be evaluated using:

* Precision
* Recall
* False Positive Rate
* Match Accuracy

Example metrics are calculated using:

```python
precision_score()
recall_score()
confusion_matrix()
```

---


## Conclusion

This project demonstrates an explainable AI-powered candidate-job matching system capable of processing structured candidate data, resumes, and job descriptions. It provides transparent recommendations, measurable evaluation metrics, and a scalable API architecture suitable for recruitment marketplaces such as PlaceMux.
