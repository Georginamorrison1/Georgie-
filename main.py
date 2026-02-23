#!/usr/bin/env python3
"""HiBob + Claude integration: HR data analysis, reporting, and recruitment."""

import argparse
import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Error: {name} environment variable is not set.", file=sys.stderr)
        print("Copy .env.example to .env and fill in your credentials.", file=sys.stderr)
        sys.exit(1)
    return value


def _build_hibob_client():
    from src.hibob_client import HiBobClient

    return HiBobClient(
        service_user_id=_require_env("HIBOB_SERVICE_USER_ID"),
        service_user_token=_require_env("HIBOB_SERVICE_USER_TOKEN"),
    )


def _check_anthropic_key():
    _require_env("ANTHROPIC_API_KEY")


# ------------------------------------------------------------------
# Command handlers
# ------------------------------------------------------------------


def cmd_headcount(args):
    """Generate a headcount report by department and location."""
    _check_anthropic_key()
    bob = _build_hibob_client()

    from src.reporter import HRReporter

    print("Fetching employees from HiBob...", flush=True)
    try:
        employees = bob.get_employees()
    except Exception as exc:
        print(f"Error fetching employees: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(employees)} employees. Generating report...\n", flush=True)
    summary = bob.aggregate_employees(employees)
    HRReporter().generate_headcount_report(summary)


def cmd_timeoff(args):
    """Generate a time-off summary for the last 30 days."""
    _check_anthropic_key()
    bob = _build_hibob_client()

    from src.reporter import HRReporter

    today = datetime.now().date()
    from_date = (today - timedelta(days=30)).isoformat()
    to_date = today.isoformat()

    print("Fetching time-off data from HiBob...", flush=True)
    try:
        outtoday = bob.get_timeoff_outtoday()
        requests = bob.get_timeoff_requests(from_date, to_date)
    except Exception as exc:
        print(f"Error fetching time-off data: {exc}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Fetched {len(outtoday)} out today, {len(requests)} requests in last 30 days."
        " Generating report...\n",
        flush=True,
    )
    summary = bob.aggregate_timeoff(requests, outtoday)
    HRReporter().generate_timeoff_report(summary)


def cmd_query(args):
    """Answer a custom workforce question using Claude."""
    _check_anthropic_key()
    bob = _build_hibob_client()

    from src.reporter import HRReporter

    print("Fetching employees from HiBob...", flush=True)
    try:
        employees = bob.get_employees()
    except Exception as exc:
        print(f"Error fetching employees: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(employees)} employees. Answering query...\n", flush=True)
    summary = bob.aggregate_employees(employees)
    HRReporter().answer_query(args.question, summary)


# ------------------------------------------------------------------
# CLI definition
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# Recruitment command handlers
# ------------------------------------------------------------------


def cmd_recruit_job_add(args):
    from src.database import init_db
    from src.jobs import create_job

    init_db()
    job_id = create_job(
        title=args.title,
        department=args.department or "",
        location=args.location or "",
        description=args.description or "",
        requirements=args.requirements or "",
    )
    print(f"Job created (id={job_id}): {args.title}")


def cmd_recruit_job_list(args):
    from src.database import init_db
    from src.jobs import list_jobs

    init_db()
    jobs = list_jobs(status=args.status)
    if not jobs:
        print("No jobs found.")
        return
    for j in jobs:
        print(f"  [{j['id']}] {j['title']}  |  {j['status']}  |  {j.get('department') or '-'}  |  {j.get('location') or '-'}")


def cmd_recruit_job_close(args):
    from src.database import init_db
    from src.jobs import close_job

    init_db()
    if close_job(args.id):
        print(f"Job {args.id} closed.")
    else:
        print(f"Job {args.id} not found.", file=sys.stderr)
        sys.exit(1)


def cmd_recruit_candidate_add(args):
    from src.database import init_db
    from src.candidates import add_candidate

    init_db()
    resume_text = args.resume or ""
    if args.resume_file:
        try:
            with open(args.resume_file) as f:
                resume_text = f.read()
        except OSError as e:
            print(f"Cannot read resume file: {e}", file=sys.stderr)
            sys.exit(1)
    candidate_id = add_candidate(
        name=args.name,
        email=args.email,
        phone=args.phone or "",
        resume_text=resume_text,
    )
    print(f"Candidate created (id={candidate_id}): {args.name} <{args.email}>")


def cmd_recruit_candidate_list(args):
    from src.database import init_db
    from src.candidates import list_candidates

    init_db()
    candidates = list_candidates()
    if not candidates:
        print("No candidates found.")
        return
    for c in candidates:
        has_resume = "resume" if c.get("resume_text") else "no resume"
        print(f"  [{c['id']}] {c['name']}  |  {c['email']}  |  {has_resume}")


def cmd_recruit_apply(args):
    from src.database import init_db
    from src.pipeline import apply

    init_db()
    try:
        app_id = apply(job_id=args.job, candidate_id=args.candidate)
        print(f"Application created (id={app_id}): candidate {args.candidate} -> job {args.job}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_recruit_stage(args):
    from src.database import init_db
    from src.pipeline import advance_stage

    init_db()
    try:
        if advance_stage(args.application, args.stage):
            print(f"Application {args.application} moved to stage '{args.stage}'.")
        else:
            print(f"Application {args.application} not found.", file=sys.stderr)
            sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_recruit_applications(args):
    from src.database import init_db
    from src.pipeline import list_applications

    init_db()
    applications = list_applications(job_id=args.job, stage=args.stage)
    if not applications:
        print("No applications found.")
        return
    for a in applications:
        print(
            f"  [{a['id']}] {a['candidate_name']} -> {a['job_title']}"
            f"  |  stage: {a['stage']}  |  updated: {a['updated_at'][:10]}"
        )


def cmd_recruit_interview_schedule(args):
    from src.database import init_db
    from src.interviews import schedule_interview

    init_db()
    try:
        interview_id = schedule_interview(
            application_id=args.application,
            interviewer=args.interviewer,
            scheduled_at=args.at,
            stage_name=args.stage or "",
        )
        print(f"Interview scheduled (id={interview_id}) for application {args.application} at {args.at}.")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_recruit_interview_list(args):
    from src.database import init_db
    from src.interviews import list_interviews

    init_db()
    interviews = list_interviews(args.application)
    if not interviews:
        print("No interviews found.")
        return
    for i in interviews:
        print(
            f"  [{i['id']}] {i['scheduled_at']}  |  interviewer: {i['interviewer']}"
            f"  |  stage: {i.get('stage_name') or '-'}"
        )
        if i.get("notes"):
            print(f"          notes: {i['notes']}")


def cmd_recruit_screen(args):
    _check_anthropic_key()
    from src.database import init_db
    from src.screener import screen_candidate

    init_db()
    try:
        screen_candidate(args.application)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


# ------------------------------------------------------------------
# CLI definition
# ------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="hibob-claude",
        description="HiBob + Claude: AI-powered HR data analysis, reporting, and recruitment",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # headcount
    headcount = subparsers.add_parser(
        "headcount",
        help="Generate a headcount report by department and location",
    )
    headcount.set_defaults(func=cmd_headcount)

    # timeoff
    timeoff = subparsers.add_parser(
        "timeoff",
        help="Generate a time-off summary for the last 30 days",
    )
    timeoff.set_defaults(func=cmd_timeoff)

    # query
    query = subparsers.add_parser(
        "query",
        help="Ask a custom question about your workforce",
    )
    query.add_argument("question", help='e.g. "Which department grew the most this quarter?"')
    query.set_defaults(func=cmd_query)

    # ------------------------------------------------------------------
    # recruit — top-level recruitment command
    # ------------------------------------------------------------------
    recruit = subparsers.add_parser("recruit", help="Recruitment pipeline management")
    recruit_sub = recruit.add_subparsers(dest="recruit_command", required=True)

    # recruit job
    recruit_job = recruit_sub.add_parser("job", help="Manage job postings")
    recruit_job_sub = recruit_job.add_subparsers(dest="job_command", required=True)

    rj_add = recruit_job_sub.add_parser("add", help="Create a new job posting")
    rj_add.add_argument("--title", required=True)
    rj_add.add_argument("--department")
    rj_add.add_argument("--location")
    rj_add.add_argument("--description")
    rj_add.add_argument("--requirements")
    rj_add.set_defaults(func=cmd_recruit_job_add)

    rj_list = recruit_job_sub.add_parser("list", help="List job postings")
    rj_list.add_argument("--status", choices=["open", "closed", "draft"], help="Filter by status")
    rj_list.set_defaults(func=cmd_recruit_job_list)

    rj_close = recruit_job_sub.add_parser("close", help="Close a job posting")
    rj_close.add_argument("id", type=int, help="Job id")
    rj_close.set_defaults(func=cmd_recruit_job_close)

    # recruit candidate
    recruit_cand = recruit_sub.add_parser("candidate", help="Manage candidates")
    recruit_cand_sub = recruit_cand.add_subparsers(dest="candidate_command", required=True)

    rc_add = recruit_cand_sub.add_parser("add", help="Add a candidate")
    rc_add.add_argument("--name", required=True)
    rc_add.add_argument("--email", required=True)
    rc_add.add_argument("--phone")
    rc_add.add_argument("--resume", help="Resume text (inline)")
    rc_add.add_argument("--resume-file", dest="resume_file", help="Path to a plain-text resume file")
    rc_add.set_defaults(func=cmd_recruit_candidate_add)

    rc_list = recruit_cand_sub.add_parser("list", help="List all candidates")
    rc_list.set_defaults(func=cmd_recruit_candidate_list)

    # recruit apply
    r_apply = recruit_sub.add_parser("apply", help="Apply a candidate to a job")
    r_apply.add_argument("--job", required=True, type=int, help="Job id")
    r_apply.add_argument("--candidate", required=True, type=int, help="Candidate id")
    r_apply.set_defaults(func=cmd_recruit_apply)

    # recruit stage
    r_stage = recruit_sub.add_parser("stage", help="Advance an application to a new stage")
    r_stage.add_argument("--application", required=True, type=int, help="Application id")
    r_stage.add_argument(
        "--stage",
        required=True,
        choices=["applied", "screening", "interview", "offer", "hired", "rejected"],
    )
    r_stage.set_defaults(func=cmd_recruit_stage)

    # recruit applications
    r_apps = recruit_sub.add_parser("applications", help="List applications")
    r_apps.add_argument("--job", type=int, help="Filter by job id")
    r_apps.add_argument(
        "--stage",
        choices=["applied", "screening", "interview", "offer", "hired", "rejected"],
        help="Filter by stage",
    )
    r_apps.set_defaults(func=cmd_recruit_applications)

    # recruit interview
    recruit_iv = recruit_sub.add_parser("interview", help="Manage interviews")
    recruit_iv_sub = recruit_iv.add_subparsers(dest="interview_command", required=True)

    ri_sched = recruit_iv_sub.add_parser("schedule", help="Schedule an interview")
    ri_sched.add_argument("--application", required=True, type=int, help="Application id")
    ri_sched.add_argument("--interviewer", required=True)
    ri_sched.add_argument("--at", required=True, help="ISO 8601 datetime, e.g. 2026-03-10T14:00")
    ri_sched.add_argument("--stage", help='e.g. "phone screen", "technical", "final"')
    ri_sched.set_defaults(func=cmd_recruit_interview_schedule)

    ri_list = recruit_iv_sub.add_parser("list", help="List interviews for an application")
    ri_list.add_argument("--application", required=True, type=int, help="Application id")
    ri_list.set_defaults(func=cmd_recruit_interview_list)

    # recruit screen
    r_screen = recruit_sub.add_parser(
        "screen", help="AI-powered CV screening using Claude"
    )
    r_screen.add_argument("--application", required=True, type=int, help="Application id")
    r_screen.set_defaults(func=cmd_recruit_screen)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
