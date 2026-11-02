# MCP and FastAPI Tool Agent

A small, working demo of an agent that completes a task by calling a
real tool, not by answering from memory.

## How it works

1. The agent reads the task text.
2. It picks one tool from its registry (`tools.json`).
3. It runs that tool with the arguments it can extract.
4. It returns the tool's actual result, with the tool name stated.

## Tools

| Tool | What it does |
|---|---|
| `score_lead` | Scores a lead 0-100 (email, phone, website, industry fit, location) |
| `search_docs` | Finds sections in sample documents that match a query |
| `draft_email` | Drafts a short first email for a company and city, no price, no guessed contact |
| `add_numbers` | Adds a list of numbers and returns the total |

## Honest limits

- The tool registry follows an MCP-style manifest: each tool has a
  name, a description, and an input schema in `tools.json`.
- This demo calls the tools as local Python functions and also
  exposes them over FastAPI. It is **not** a full MCP server
  transport; wrapping the same registry in an MCP server is a stated
  next step, not something already claimed.
- Sample data is fictional. For a real client, replace
  `sample_docs/` with that client's documents.

## Run it

```bash
python3 agent.py --task "score lead Bright Homes Realty, Real Estate, Austin TX, hello@brighthomes.example, 512-555-0100, https://brighthomes.example"
python3 agent.py --task "search docs for refund policy"
python3 agent.py --task "draft email for Bright Homes Realty in Austin"
python3 agent.py --task "add 12 30 8"
```

## Optional API demo

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then send `POST /run` with `{"task": "..."}`, or open `GET /tools`
for the tool manifest.

## Files

- `agent.py` — tool registry, tool picking, and command-line tool
- `app.py` — optional FastAPI demo
- `tools.json` — MCP-style tool manifest
- `sample_docs/` — 1 fictional sample document
- `requirements.txt` — FastAPI and Uvicorn, only needed for the API demo

## Docker and CI

Run the FastAPI demo in Docker (Docker is not needed to run the
plain Python tool, which works without it):

```bash
docker build -t mcp-tool-agent .
docker run -p 8000:8000 mcp-tool-agent
```

Then open http://localhost:8000/health

GitHub Actions runs on every push and pull request: it installs
requirements, compiles the Python files, runs the smoke test above,
and builds the Docker image. A failing check means the code or the
Dockerfile needs fixing before it is shared.
