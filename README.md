# AI Resume Profile Onboarder

A Streamlit app that turns a PDF resume into a structured candidate profile. It extracts the resume text, uses GPT-4o-mini to convert it into a fixed JSON structure, scores the profile for completeness (0-100), stores it in a 6-table MySQL database and creates a login for the candidate. Candidates can then log in to view and edit their profile.

## Demo
Add 2 or 3 screenshots here: the upload page, the profile dashboard and the edit page. Do not include real personal data.

## How it works

```
PDF resume
   -> PyMuPDF extracts the text
   -> GPT-4o-mini parses it into JSON (rule-based prompt, JSON mode, temperature 0)
   -> code validates the JSON and normalizes skill levels
   -> profile completeness score (0-100) and status
   -> saved to MySQL (6 tables, one transaction)
   -> login credentials generated and emailed via Gmail SMTP
   -> candidate logs in, views and edits the profile
```

## Features
- Upload a PDF resume and get a structured profile in a few seconds
- Extracts personal details, skills (with level when stated), projects, certifications and awards
- Prompt rules: return only valid JSON, use null for anything missing, never guess Aadhar or PAN numbers
- Output checks: missing top-level keys are filled in, skill levels are limited to Beginner, Intermediate, Advanced or null
- Token usage is logged for each request to track API cost
- Profile completeness score and a lifecycle status
- Login page and a profile dashboard with view mode, edit mode and a status update
- The score and status are recalculated after every edit

## Profile score
The score measures how **complete** a profile is. It does not measure how good the candidate is.

| Section | Points | Rule |
|---|---|---|
| Personal info | 30 | Share of 7 fields filled: first name, last name, email, mobile, job role, company, date of birth |
| Skills | 20 | 5 or more = 20, 3-4 = 15, 1-2 = 10 |
| Projects | 20 | 3 or more = 20, 2 = 15, 1 = 10 |
| Certifications | 15 | 2 or more = 15, 1 = 10 |
| Experience | 15 | 5+ years = 15, 2-4 = 10, 1 = 5 |

| Score | Status |
|---|---|
| 0-40 | Created |
| 41-70 | Reviewed |
| 71-100 | Open to Work |

The user can also set the status to Not Interested.

## Database
MySQL database `profile_details` with 6 tables. Each resume is saved in one transaction, so if any insert fails, everything is rolled back. All queries are parameterized.

| Table | Main columns |
|---|---|
| `users` | user_id, first_name, last_name, date_of_birth, mobile_number, email_id, aadhar_number, pan_number, job_role, current_company, years_of_experience, profile_status |
| `auth_users` | user_id, email_id, user_password |
| `skillset` | user_id, skill_name, experence_level_in_skills |
| `project_history` | user_id, project_title, project_description, project_start_month, project_start_year, project_end_month, project_end_year, activites |
| `certification` | user_id, cerification_name, year_of_certification |
| `awards` | user_id, award_name, year_of_award, company_name |

Some column names contain typos (for example `experence_level_in_skills`, `cerification_name`, `activites`). They match the database and the code, so they are kept as they are. A `schema.sql` file with the full table definitions is in the repository: [add after you export it].

## Tech stack
Python, Streamlit, OpenAI API (GPT-4o-mini), PyMuPDF, MySQL (mysql-connector-python), Gmail SMTP

## Project files
| File | Purpose |
|---|---|
| `app.py` | Streamlit app with 3 pages: upload, login, profile dashboard |
| `pdf_extract.py` | Reads text from the uploaded PDF with PyMuPDF |
| `openai_parser.py` | Prompt, GPT-4o-mini call and output validation |
| `score_utils.py` | Completeness score, status and score label |
| `Database.py` | MySQL connection, save, fetch, update and login functions |
| `email_server.py` | Sends the login credentials by Gmail SMTP |
| `requirements.txt` | Python packages |

## Setup

1. Install the packages:
```
pip install -r requirements.txt
```
2. Create the MySQL database `profile_details` and its 6 tables (see `schema.sql`).
3. Set these environment variables. Never put keys or passwords in the code:

| Variable | What it is |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `DB_PASSWORD` | MySQL password (optional `DB_HOST`, `DB_USER`, `DB_NAME`) |
| `EMAIL_PASSWORD` | Gmail **app password** for the sender account |

On Windows (Command Prompt), for the current session:
```
set OPENAI_API_KEY=your_key
set DB_PASSWORD=your_password
set EMAIL_PASSWORD=your_app_password
```
4. Set `SENDER_EMAIL` in `email_server.py` to your sending Gmail address.
5. Run the app:
```
streamlit run app.py
```
It opens at http://localhost:8501.

## Testing
I tested the parser on 25 resumes of varied layouts and checked the extracted fields against the PDFs.

## Limitations
- Passwords are generated with Python's `random` module and stored in plain text. They should be generated with the `secrets` module and stored as bcrypt hashes.
- Scanned (image-only) PDFs fail, because no text can be extracted. OCR would be needed.
- The score measures completeness, not candidate quality. Awards are not scored.
- Edit mode changes personal details only, not skills, projects or certifications.
- Extraction depends on the model, so results can vary with resume layout and wording.
