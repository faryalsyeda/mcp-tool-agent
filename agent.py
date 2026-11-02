"""Tool Agent (demo).

An agent that completes a task by calling a real tool, not by
answering from memory. It reads a task, picks one tool from its
registry, runs it with the arguments it can extract, and returns the
tool's actual result.

Tools in this demo (see tools.json for the full manifest):
- score_lead: score a lead 0-100, same rules as the Lead
  Qualification Agent (email, phone, website, industry fit, location).
- search_docs: find sections in sample documents that match a query.
- draft_email: draft a short first email for a company and city.
  No price, no guessed contact.
- add_numbers: add a list of numbers, for a simple calculation check.

Run:
    python3 agent.py --task "score lead Bright Homes Realty, Real Estate, Austin TX, hello@brighthomes.example, 512-555-0100, https://brighthomes.example"
    python3 agent.py --task "search docs for refund policy"
    python3 agent.py --task "draft email for Bright Homes Realty in Austin"
    python3 agent.py --task "add 12 30 8"

The tool registry follows an MCP-style manifest: each tool has a
name, a description, and an input schema in tools.json. This demo
calls the tools as local Python functions and also exposes them over
FastAPI in app.py. It is not a full MCP server transport; that step
would wrap the same registry in an MCP server, and is not claimed here.
"""

import argparse
import json
import os
import re

HERE = os.path.dirname(__file__)
_DOCS_DIR = os.path.join(HERE, "sample_docs")


def score_lead(company="", industry="", city="", state="", email="",
               phone="", website=""):
    score = 0
    reasons = []
    if email:
        score += 30
        reasons.append("business email present (+30)")
    if phone:
        score += 20
        reasons.append("phone present (+20)")
    if website:
        score += 20
        reasons.append("website present (+20)")
    if industry.lower() in ("real estate", "mortgage", "marketing"):
        score += 20
        reasons.append("target industry fit (+20)")
    if city and state:
        score += 10
        reasons.append("complete city and state (+10)")
    grade = "A" if score >= 80 else "B" if score >= 60 else "C"
    return {"company": company, "score": score, "grade": grade, "reasons": reasons}


def search_docs(query):
    results = []
    query_words = set(re.findall(r"[a-z0-9]+", query.lower()))
    for filename in sorted(os.listdir(_DOCS_DIR)):
        if not filename.endswith(".txt"):
            continue
        with open(os.path.join(_DOCS_DIR, filename), encoding="utf-8") as f:
            text = f.read()
        for paragraph in [p.strip() for p in text.split("\n\n") if p.strip()]:
            words = set(re.findall(r"[a-z0-9]+", paragraph.lower()))
            if query_words & words:
                results.append({"source": filename, "text": paragraph})
    return results[:3]


def draft_email(company, city):
    return (
        f"Hi {company} team,\n\n"
        f"I help businesses in {city} turn a long lead list into a short, "
        "prioritised action list. Would a small demo help? Reply with "
        "your main problem and I will show an example, with no obligation."
    )


def add_numbers(numbers):
    return {"numbers": numbers, "total": sum(numbers)}


def run_task(task):
    """Pick a tool from the task text, run it, and return the result."""
    low = task.lower()
    if low.startswith("score lead"):
        # Format: score lead <company>, <industry>, <city> <state>, <email>, <phone>, <website>
        rest = task[len("score lead"):].strip()
        parts = [p.strip() for p in rest.split(",")]
        company = parts[0] if len(parts) > 0 else ""
        industry = parts[1] if len(parts) > 1 else ""
        city_state = parts[2].split() if len(parts) > 2 else []
        city = city_state[0] if city_state else ""
        state = city_state[1] if len(city_state) > 1 else ""
        email = parts[3] if len(parts) > 3 else ""
        phone = parts[4] if len(parts) > 4 else ""
        website = parts[5] if len(parts) > 5 else ""
        return {"tool": "score_lead",
                "result": score_lead(company, industry, city, state, email, phone, website)}
    if low.startswith("search docs for"):
        query = task[len("search docs for"):].strip()
        return {"tool": "search_docs", "result": search_docs(query)}
    if low.startswith("draft email for"):
        rest = task[len("draft email for"):].strip()
        parts = [p.strip() for p in rest.split(" in ")]
        company = parts[0] if parts else ""
        city = parts[1] if len(parts) > 1 else ""
        return {"tool": "draft_email", "result": draft_email(company, city)}
    if low.startswith("add "):
        numbers = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", task[4:])]
        return {"tool": "add_numbers", "result": add_numbers(numbers)}
    return {"tool": None,
            "result": "No tool matched this task. Try: score lead ..., "
                      "search docs for ..., draft email for ..., or add ... "}


def main():
    parser = argparse.ArgumentParser(description="Run the Tool Agent on a task.")
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    print(json.dumps(run_task(args.task), indent=2))


if __name__ == "__main__":
    main()
