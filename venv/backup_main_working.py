from fastapi import FastAPI, Request
from github import Github
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os

# Load environment variables
load_dotenv()

# Get tokens from .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Connect GitHub API
github_client = Github(GITHUB_TOKEN)

# Connect Groq AI model
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile"
)

# Create FastAPI app
app = FastAPI()


# Home Route
@app.get("/")
def home():
    return {
        "message": "AI Code Review System Running"
    }


# GitHub Webhook Route
@app.post("/webhook")
async def github_webhook(request: Request):

    # Convert webhook payload into dictionary
    payload = await request.json()

    # Get GitHub event type
    event_type = request.headers.get("X-GitHub-Event")

    print("\n===== WEBHOOK RECEIVED =====")
    print(f"GitHub Event: {event_type}")

    # Ignore non-pull-request events
    if event_type != "pull_request":
        return {"message": "Ignored non-PR event"}

    # Get PR action
    action = payload.get("action")

    # Only process opened PRs
    if action != "opened":
        return {"message": "Ignored non-opened PR"}

    # Extract PR information
    pull_request = payload["pull_request"]

    repo_name = payload["repository"]["full_name"]

    pr_number = pull_request["number"]

    print("\n===== PULL REQUEST INFO =====")
    print(f"Repository: {repo_name}")
    print(f"PR Number: {pr_number}")

    try:

        # Connect to repository
        repo = github_client.get_repo(repo_name)

        # Get pull request object
        pr = repo.get_pull(pr_number)

        # Get changed files
        files = pr.get_files()

        # Loop through changed files
        for file in files:

            print("\n==============================")
            print(f"File: {file.filename}")
            print("==============================")

            # Skip if no patch exists
            if not file.patch:
                continue

            print("\nChanged Code:")
            print(file.patch)

            # AI Prompt
            prompt = f"""
You are a senior security engineer.

Analyze this code change carefully.

Find:
1. Security vulnerabilities
2. Hardcoded secrets
3. Bad coding practices
4. Sensitive information exposure

Code:
{file.patch}

Give response in clean bullet points.
"""

            print("\n===== AI SECURITY REVIEW =====")

            # Send code to AI
            response = llm.invoke([
                HumanMessage(content=prompt)
            ])

            # Print AI response in terminal
            print(response.content)

            # Post AI review comment on GitHub PR
            pr.create_issue_comment(
                f"## 🤖 AI Security Review\n\n{response.content}"
            )

            print("\n===== COMMENT POSTED TO GITHUB =====")

    except Exception as e:
        print(f"\nERROR: {e}")

    return {
        "status": "success",
        "message": "Webhook processed successfully"
    }