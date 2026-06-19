# Student <-> Job Feature Space

Overview
- Purpose: Define the signals used by the matching layer to score and explain candidate-job suitability.

Core feature groups
- Verified skill scores: numeric verified scores per skill (e.g., `python`, `sql`, `machine_learning`).
- JD required skill thresholds: per-skill required minimums (e.g., `python_req`).
- Academic signal: `cgpa` (numeric).
- Experience signal: `experience_months` (numeric).
- Project signal: `projects` (count).
- Textual signals: resume text and job description for semantic matching.

Engineered features
- Skill ratio per required skill: min(student_skill / job_req, 1.0).
- Aggregate skill score: mean of skill ratios scaled to 0-100.
- Experience normalized: min(experience_months / 6, 1.0) * 100.
- Project normalized: min(projects / 5, 1.0) * 100.

Why these features
- Measurable and explainable: each contribution (skill, cgpa, experience) can be shown in plain English.
- Minimal leakage: features are derived from student and job attributes only.

Usage
- Baseline score: weighted sum (skill:70%, cgpa:10%, experience:10%, projects:10%).
- Rule match: exact skill overlap ratio for the JD-required set.
- Semantic match: TF-IDF cosine similarity on full texts used as a complementary signal.

Next steps
- Extend verified skill vector to include confidence and provenance.
- Add calibrated thresholds per role family.
