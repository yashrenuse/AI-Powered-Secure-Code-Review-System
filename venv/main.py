from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from github import Github
from dotenv import load_dotenv
from groq import Groq

import sqlite3
import os
from datetime import datetime

import subprocess
import tempfile


# ============================================
# LOAD ENV VARIABLES
# ============================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================
# CONNECT SERVICES
# ============================================

github_client = Github(GITHUB_TOKEN)

groq_client = Groq(api_key=GROQ_API_KEY)


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# ============================================
# DATABASE SETUP
# ============================================

conn = sqlite3.connect("reviews.db")

cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS reviews (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository TEXT,
    pr_number INTEGER,
    file_name TEXT,
    severity TEXT,
    review TEXT,
    created_at TEXT

)

""")

conn.commit()

conn.close()


# ============================================
# HOME ROUTE
# ============================================

@app.get("/")
def home():

    return {
        "message": "AI Code Review System Running"
    }


# ============================================
# DASHBOARD ROUTE
# ============================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    conn = sqlite3.connect("reviews.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reviews ORDER BY id DESC")

    reviews = cursor.fetchall()

    total_reviews = len(reviews)

    high_count = 0
    medium_count = 0
    low_count = 0

    for review in reviews:

        severity = review[4]

        if severity == "HIGH":
            high_count += 1

        elif severity == "MEDIUM":
            medium_count += 1

        else:
            low_count += 1

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "reviews": reviews,
            "total_reviews": total_reviews,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count
        }
    )


# ============================================
# GITHUB WEBHOOK
# ============================================

@app.post("/webhook")
async def github_webhook(request: Request):

    payload = await request.json()

    event_type = request.headers.get("X-GitHub-Event")

    print("\n===== WEBHOOK RECEIVED =====")
    print(f"GitHub Event: {event_type}")

    # Ignore non PR events
    if event_type != "pull_request":

        return {
            "message": "Ignored non pull request event"
        }

    action = payload.get("action")

    # Only review newly opened PRs
    if action != "opened":

        return {
            "message": "Ignored non-opened PR"
        }

    pull_request = payload["pull_request"]

    repo_name = payload["repository"]["full_name"]

    pr_number = pull_request["number"]

    print("\n===== PULL REQUEST INFO =====")
    print(f"Repository: {repo_name}")
    print(f"PR Number: {pr_number}")

    try:

        # ============================================
        # GET REPOSITORY
        # ============================================

        repo = github_client.get_repo(repo_name)

        pr = repo.get_pull(pr_number)

        files = pr.get_files()

        final_review = "# 🤖 Advanced AI Code Review\n\n"

        # ============================================
        # PROCESS EACH FILE
        # ============================================

        for file in files:

            print("\n==============================")
            print(f"File: {file.filename}")
            print("==============================")

            patch_content = file.patch

            print("\nChanged Code:\n")
            print(patch_content)

            # ============================================
            # STATIC ANALYSIS
            # ============================================

            static_analysis_result = ""

            try:

                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".py",
                    delete=False
                ) as temp_file:

                    temp_file.write(patch_content)

                    temp_file_path = temp_file.name

                # PYLINT

                pylint_result = subprocess.run(

                    ["pylint", temp_file_path],

                    capture_output=True,
                    text=True

                )

                # FLAKE8

                flake8_result = subprocess.run(

                    ["flake8", temp_file_path],

                    capture_output=True,
                    text=True

                )

                # BANDIT

                bandit_result = subprocess.run(

                    ["bandit", "-r", temp_file_path],

                    capture_output=True,
                    text=True

                )

                static_analysis_result += "\nPYLINT RESULTS:\n"
                static_analysis_result += pylint_result.stdout

                static_analysis_result += "\nFLAKE8 RESULTS:\n"
                static_analysis_result += flake8_result.stdout

                static_analysis_result += "\nBANDIT RESULTS:\n"
                static_analysis_result += bandit_result.stdout

            except Exception as analysis_error:

                static_analysis_result = str(analysis_error)

            print("\n===== STATIC ANALYSIS =====\n")

            print(static_analysis_result)

            # ============================================
            # AI PROMPT
            # ============================================

            prompt = f'''
You are a Senior AI Security Engineer and Professional Code Reviewer.

Analyze the following GitHub Pull Request code changes very carefully.

Your responsibilities:

================ SECURITY ANALYSIS ================

1. Detect SQL Injection vulnerabilities
2. Detect Cross Site Scripting (XSS)
3. Detect hardcoded passwords
4. Detect exposed API keys
5. Detect JWT token exposure
6. Detect insecure authentication
7. Detect shell injection vulnerabilities
8. Detect dangerous subprocess/system commands
9. Detect unsafe eval() usage
10. Detect insecure file handling
11. Detect sensitive information leakage
12. Detect insecure imports

================ CODE QUALITY ANALYSIS ================

13. Detect bad coding practices
14. Detect poor readability
15. Detect duplicate logic
16. Detect poor naming conventions
17. Detect missing error handling
18. Detect bad project structure

================ PERFORMANCE ANALYSIS ================

19. Detect inefficient loops
20. Detect unnecessary database calls
21. Detect memory inefficient code
22. Detect slow operations

================ SEVERITY RULES ================

HIGH:
- passwords
- api keys
- shell execution
- SQL injection
- eval()
- authentication vulnerabilities

MEDIUM:
- bad practices
- poor readability
- missing validation

LOW:
- formatting
- naming improvements

======================================================

Code Changes:
{patch_content}

======================================================

Static Analysis Results:
{static_analysis_result}

======================================================

Give response EXACTLY in this format:

AI CODE REVIEW REPORT

Severity:
HIGH / MEDIUM / LOW

Security Issues:
- issue here

Code Quality Issues:
- quality issue here

Performance Issues:
- performance issue here

Why It Is Dangerous:
- explanation

Recommended Fix:
- fix recommendation

Improved Secure Code Example:
# secure improved code here

Overall Summary:
- final review summary
'''

            print("\n===== AI REVIEW STARTED =====\n")

            # ============================================
            # SEND TO AI
            # ============================================

            ai_response = groq_client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.3
            )

            review_text = ai_response.choices[0].message.content

            print(review_text)

            # ============================================
            # DETECT SEVERITY
            # ============================================

            severity = "LOW"

            if "HIGH" in review_text:
                severity = "HIGH"

            elif "MEDIUM" in review_text:
                severity = "MEDIUM"

            # ============================================
            # SAVE TO DATABASE
            # ============================================

            conn = sqlite3.connect("reviews.db")

            cursor = conn.cursor()

            cursor.execute("""

            INSERT INTO reviews (

                repository,
                pr_number,
                file_name,
                severity,
                review,
                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?)

            """, (

                repo_name,
                pr_number,
                file.filename,
                severity,
                review_text,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            ))

            conn.commit()

            conn.close()

            print("\n===== REVIEW SAVED TO DATABASE =====")

            # ============================================
            # ADD TO FINAL COMMENT
            # ============================================

            final_review += f"## 📄 File: `{file.filename}`\n\n"

            final_review += review_text + "\n\n---\n\n"

        # ============================================
        # POST COMMENT TO GITHUB
        # ============================================

        pr.create_issue_comment(final_review)

        print("\n===== COMMENT POSTED SUCCESSFULLY =====")

    except Exception as e:

        print(f"\nERROR: {e}")

    return {

        "status": "success",
        "message": "Webhook processed successfully"

    }