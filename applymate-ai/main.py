import os
import re
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()

# ---------------------------------------------------------------- LLM
llm = ChatGroq(model="openai/gpt-oss-120b", max_retries=6, reasoning_effort="low")

# ---------------------------------------------------------------- Candidate details
# Filled in from the website's setup form (resume upload, LinkedIn, GitHub, Gmail).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

resume_path = ""
resume_filename = "Resume.pdf"
resume_text = ""
linkedin_url = ""
github_url = ""
sender_email = ""
app_password = ""

# ---------------------------------------------------------------- Prompt (same as notebook)
draft_email_prompt = ChatPromptTemplate.from_template("""
You are a professional job application email writer.

Write a personalized, clear, and convincing application email
using the candidate's resume and details given.

use only the mentioned things like email id, job role, company if you are not sure about the details you have then ask first ...dont take these details on your own or dont fake it ...
dont go further untill and unless you dont have the given information...
if one dont know the company name then mention like 'in your company' only when nothing is mentioned...

Candidate Resume:
{resume_text}

LinkedIn Profile:
{linkedin_url}

GitHub Profile:
{github_url}


Recruiter Email:
{recruiter_email}

Job Role:
{job_role}

Company Name:
{company_name}


EMAIL STRUCTURE

1. Opening Paragraph:
- Mention the job role and company name.
- Briefly introduce the candidate.
- Express interest in the position.

2. Relevant Professional Experience:
- This section is MANDATORY.
- Mention relevant companies and job titles.
- Explain actual responsibilities and technologies used.
- Include measurable achievements when available.
- Prioritize experience relevant to the target role.
- Do not skip this section, even if the candidate has projects.

3. Relevant Project Experience:
- This section is MANDATORY and must come after professional experience.
- Select 1-3 projects relevant to the target job.
- Mention each project's name, purpose, technologies, and implementation.
- Include specific results only when supported by the resume.
- Do not combine all projects into one vague sentence.
- Do not describe every project in the resume.

4. Closing Paragraph:
- Explain briefly how the candidate's skills can contribute to the company.
- Mention that the resume is attached.
- Express interest in discussing the opportunity.

5. Signature:
- End with "Regards," followed by the candidate's actual name.
- Include the candidate's email address if available in the resume.
- Include the COMPLETE LinkedIn URL provided above.
- Include the COMPLETE GitHub URL provided above.
- Never write only "LinkedIn" or "GitHub" without their URLs.
- Never invent or modify contact details.

WRITING RULES

- Aim for 180-250 words, excluding the subject and signature.
- Never exceed 300 words.
- Use short paragraphs and clear section headings.
- Mention professional experience FIRST, then projects.
- Use a professional, natural, confident tone.
- Do not reproduce the entire resume.
- Do not invent experience, responsibilities, technologies, skills,
  projects, achievements, metrics, or qualifications.
- Use only information supported by the resume or candidate details.
- Use "Dear Hiring Manager" unless the recruiter's name is reliably known.
- Do not invent the recruiter's name.
- Do not include placeholder information.
- Do not use Markdown formatting markers such as **.
- Keep the subject concise and specific to the role and company.
- Do not invent, guess, or modify any email address or profile URL.
-do not get the recruiters email i d on your own as placeholder until and unless candidate didnt providee ask for it to the candidate.



Return the email in exactly this format:

Subject: <email_subject>

Body:
Dear Hiring Manager,

<opening paragraph>

Relevant Professional Experience:
<relevant experience with specific responsibilities>

Relevant Project Experience:
<1-3 selected projects with specific details>

<closing paragraph>

Regards,
<candidate name>
Email: <candidate email if available>
LinkedIn: <complete LinkedIn URL>
GitHub: <complete GitHub URL>
""")

# ---------------------------------------------------------------- Tools (same logic as notebook)
drafts = {}


@tool
def write_email(
    company_name: str,
    job_role: str,
    recruiter_email: str,
    instructions: str = ""
):
    """Write a job application email.
    Call only when company, role and recruiter email are known.
    """

    res = (draft_email_prompt | llm).invoke({
        "resume_text": resume_text,
        "details": instructions,
        "recruiter_email": recruiter_email,
        "job_role": job_role,
        "company_name": company_name,
        "linkedin_url": linkedin_url,
        "github_url": github_url,
    })

    text = res.content.replace("**", "").strip()

    subject = f"Application for {job_role} at {company_name}"
    body = text

    if "Body:" in text:
        head, body = text.split("Body:", 1)
        subject = head.replace("Subject:", "").strip()

    drafts["subject"] = subject
    drafts["body"] = body.strip()
    drafts["recruiter_email"] = recruiter_email

    return (
        f"Draft ready.\n"
        f"Recruiter: {drafts['recruiter_email']}\n"
        f"Subject: {drafts['subject']}\n\n"
        f"{drafts['body']}"
    )


@tool
def send_email():
    """Send the currently approved draft to its saved recruiter email."""

    if not drafts.get("recruiter_email"):
        return "FAILED: Recruiter email is missing."

    if not drafts.get("subject") or not drafts.get("body"):
        return "FAILED: Email draft is missing."

    recipient = drafts["recruiter_email"]

    msg = EmailMessage()
    msg["Subject"] = drafts["subject"]
    msg["From"] = sender_email
    msg["To"] = recipient

    msg.set_content(drafts["body"])

    with open(resume_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=resume_filename
        )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)

    except Exception as e:
        return f"FAILED to send email: {e}"

    return f"Email sent successfully to {recipient}"


def rewrite_email(instruction: str):
    # Check whether the user provided a new email address
    emails = re.findall(
        r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
        instruction
    )

    if emails:
        drafts["recruiter_email"] = emails[-1]

    # Rewrite the email body using the user's instructions
    res = llm.invoke(
        f"""
        Rewrite the job application email below.

        User instructions: {instruction}

        Keep the same facts, greeting and signature.
        Preserve the applicant's name, email, LinkedIn and GitHub URLs.
        Do not invent information.
        Do not include ** markers.
        Return only the email body, without a subject.

        EMAIL:
        {drafts["body"]}
        """
    )

    drafts["body"] = res.content.replace("**", "").strip()

    return (
        f"Updated recruiter: {drafts['recruiter_email']}\n"
        f"Subject: {drafts['subject']}\n\n"
        f"{drafts['body']}"
    )


# ---------------------------------------------------------------- Agent (same as notebook)
agent = create_agent(
    model=llm,
    tools=[write_email, send_email],
    system_prompt=(
        "You are ApplyMate AI, a friendly assistant that helps users "
        "apply for jobs by email. Greet the user and chat naturally. "

        "Ask one question at a time to collect the company name, "
        "job role and recruiter email. Never guess these details. "

        "Once all details are known, call write_email to create a draft. "
        "Do not send the email automatically. The send_email tool is "
        "subject to a human approval step. "

        "If the user requests changes to the draft, use write_email "
        "with the same company, role and the latest recruiter email, "
        "including the requested changes in instructions, when appropriate. "

        "If the user changes the recruiter email, use the new address "
        "and ensure the latest address is saved before sending. "

        "After approval and execution of send_email, clearly report "
        "whether sending succeeded or failed. "
        "Then ask whether the user wants to apply somewhere else."
    ),
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "write_email": False
            }
        )
    ]
)

# ---------------------------------------------------------------- Web layer
app = Flask(__name__)


def build_reply(response):
    """Turn an agent response into JSON for the browser."""
    if "__interrupt__" in response:
        return {
            "pending": True,
            "reply": "Your draft is ready. Please review it before sending.",
            "draft": {
                "recruiter_email": drafts.get("recruiter_email", ""),
                "subject": drafts.get("subject", ""),
                "body": drafts.get("body", ""),
            },
        }
    return {"pending": False, "reply": response["messages"][-1].content}


def make_config(thread_id):
    return {"configurable": {"thread_id": thread_id or "chat1"}}


@app.route("/")
def index():
    return render_template("index.html")


def is_configured():
    return all([resume_path, resume_text, linkedin_url, github_url,
                sender_email, app_password])


@app.route("/api/status")
def status():
    return jsonify({
        "configured": is_configured(),
        "linkedin_url": linkedin_url,
        "github_url": github_url,
        "sender_email": sender_email,
        "resume_filename": resume_filename if resume_path else "",
    })


@app.route("/api/setup", methods=["POST"])
def setup():
    global resume_path, resume_filename, resume_text
    global linkedin_url, github_url, sender_email, app_password

    new_linkedin = (request.form.get("linkedin_url") or "").strip()
    new_github = (request.form.get("github_url") or "").strip()
    new_sender = (request.form.get("sender_email") or "").strip()
    new_password = (request.form.get("app_password") or "").replace(" ", "").strip()
    file = request.files.get("resume")

    if not (new_linkedin and new_github and new_sender and new_password):
        return jsonify({"error": "Please fill in all the fields."}), 400
    if not re.fullmatch(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', new_sender):
        return jsonify({"error": "Enter a valid Gmail address."}), 400

    new_path = resume_path
    new_name = resume_filename
    if file and file.filename:
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Resume must be a PDF file."}), 400
        new_name = secure_filename(file.filename) or "Resume.pdf"
        new_path = os.path.join(UPLOAD_DIR, new_name)
        file.save(new_path)
    elif not resume_path:
        return jsonify({"error": "Please upload your resume (PDF)."}), 400

    try:
        loader = PyPDFLoader(new_path)
        new_text = "\n".join(p.page_content for p in loader.load())
    except Exception as e:
        return jsonify({"error": f"Could not read the resume PDF: {e}"}), 400
    if not new_text.strip():
        return jsonify({"error": "No text found in the PDF."}), 400

    resume_path, resume_filename, resume_text = new_path, new_name, new_text
    linkedin_url, github_url = new_linkedin, new_github
    sender_email, app_password = new_sender, new_password
    return jsonify({"ok": True})


@app.route("/api/chat", methods=["POST"])
def chat():
    if not is_configured():
        return jsonify({"error": "Please complete the setup first."}), 400
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400
    try:
        response = agent.invoke(
            {"messages": HumanMessage(content=message)},
            config=make_config(data.get("thread_id")),
        )
        return jsonify(build_reply(response))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/decision", methods=["POST"])
def decision():
    if not is_configured():
        return jsonify({"error": "Please complete the setup first."}), 400
    data = request.get_json(force=True)
    action = data.get("action")
    config = make_config(data.get("thread_id"))

    try:
        # yes -> approve
        if action == "approve":
            response = agent.invoke(
                Command(resume={"decisions": [{"type": "approve"}]}),
                config=config,
            )
            return jsonify(build_reply(response))

        # no -> reject
        if action == "reject":
            response = agent.invoke(
                Command(resume={"decisions": [{
                    "type": "reject",
                    "message": "User cancelled. Do not send.",
                }]}),
                config=config,
            )
            return jsonify(build_reply(response))

        # anything else -> user's requested changes (rewrite_email)
        if action == "rewrite":
            instruction = (data.get("instruction") or "").strip()
            if not instruction:
                return jsonify({"error": "Enter your changes first"}), 400
            rewrite_email(instruction)
            return jsonify({
                "pending": True,
                "reply": "Draft updated. Review it before sending.",
                "draft": {
                    "recruiter_email": drafts.get("recruiter_email", ""),
                    "subject": drafts.get("subject", ""),
                    "body": drafts.get("body", ""),
                },
            })

        return jsonify({"error": "Unknown action"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)