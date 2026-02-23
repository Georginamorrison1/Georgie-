"""Claude-powered CV screening for the recruitment tool."""

import anthropic

from src.pipeline import get_application
from src.candidates import get_candidate
from src.jobs import get_job

MODEL = "claude-opus-4-6"


def screen_candidate(application_id: int) -> None:
    """Use Claude to assess a candidate's resume against the job requirements.

    Streams the assessment to stdout. The application, candidate, and job must
    all exist and the candidate must have a resume_text set.
    """
    application = get_application(application_id)
    if not application:
        raise ValueError(f"Application {application_id} not found.")

    candidate = get_candidate(application["candidate_id"])
    job = get_job(application["job_id"])

    if not candidate.get("resume_text"):
        raise ValueError(
            f"Candidate {candidate['name']} has no resume text. "
            "Add one with: recruit candidate add --resume <text>"
        )

    prompt = f"""You are an expert technical recruiter. Assess the following candidate against the job requirements and provide a structured screening report.

Job Title: {job['title']}
Department: {job.get('department') or 'Not specified'}
Location: {job.get('location') or 'Not specified'}

Job Description:
{job.get('description') or 'Not provided'}

Requirements:
{job.get('requirements') or 'Not provided'}

---

Candidate: {candidate['name']}
Email: {candidate['email']}

Resume / Profile:
{candidate['resume_text']}

---

Provide a structured report with these sections:
1. Overall Recommendation (Strong Yes / Yes / Maybe / No)
2. Strengths (bullet points — where the candidate clearly meets or exceeds requirements)
3. Gaps (bullet points — requirements the candidate does not appear to meet)
4. Key Questions (2–4 interview questions tailored to probe any gaps or verify strengths)
5. Summary (2–3 sentences)

Be specific, grounded in the resume text above, and concise."""

    client = anthropic.Anthropic()
    with client.messages.stream(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()
