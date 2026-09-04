# Sapho Bio Growth Intelligence

A lightweight LinkedIn content intelligence and AI-assisted engagement MVP built for the **Sapho Bio Growth Engineer take-home assignment**.

The application identifies relevant voices in the compounding pharmacy ecosystem, maintains a queue of their LinkedIn posts, and uses an LLM to generate context-aware responses for Sapho Bio.

It also provides a human-in-the-loop workflow for copying a generated response, opening the original LinkedIn post, and logging the engagement.

---

## Assignment Requirements

The assignment requested an MVP that could:

1. Build a list of the top 10 influencers from the compounding pharmacy industry on LinkedIn.
2. Collect their latest posts from the last month or latest 10 posts.
3. Create a lightweight HTML viewer for the post queue.
4. Use an LLM API to generate an appropriate response from Sapho Bio.
5. Optionally make the response deployable to LinkedIn with a single-click workflow and log the action.

This repository implements all five areas.

---

## Features

### 1. Top 10 Compounding Pharmacy Influencers

The project contains a curated list of 10 professionals relevant to the compounding pharmacy ecosystem.

Selection focuses on professionals working across:

- Compounding pharmacy leadership
- 503A and 503B operations
- Sterile compounding
- Pharmacy quality and compliance
- Regulatory policy
- Personalized medicine
- Pharmacy advocacy
- Manufacturing and process validation

The influencer dataset is stored in:

`data/influencers.json`

Each influencer record contains:

- Name
- Role
- Company
- LinkedIn profile
- Reason for industry relevance

---

### 2. LinkedIn Post Collection Pipeline

LinkedIn post records are maintained in:

`data/posts.json`

A collection and validation pipeline is provided at:

`scripts/collect_linkedin_posts.py`

The collector:

- Validates influencer IDs
- Validates LinkedIn URLs
- Requires unique individual post URLs
- Rejects generic profile activity URLs
- Normalizes collected records
- Removes duplicate URLs
- Limits collection to a maximum of 10 posts per influencer
- Produces a normalized dataset
- Generates a collection audit report

Run the collection pipeline with:

`python scripts/collect_linkedin_posts.py`

The generated files are:

`data/collected_posts.json`

`data/collection_report.json`

Current collection:

- **10 influencers configured**
- **10 influencers represented**
- **12 unique LinkedIn posts**
- **0 duplicate post URLs**

### LinkedIn Collection Methodology

LinkedIn restricts automated access to portions of its platform.

This MVP therefore uses a transparent public-source collection and validation workflow rather than attempting to bypass authentication, CAPTCHAs, access controls, or private LinkedIn APIs.

Where LinkedIn does not expose a reliable timestamp, `posted_at` is intentionally left null rather than fabricating a date.

The assignment permits either posts from the last month or the latest 10 posts. The dataset uses relevant recent public posts where available and the latest-post interpretation where reliable one-month activity is not publicly accessible.

---

## 3. LinkedIn Engagement Queue

The FastAPI application renders a lightweight HTML dashboard containing the collected LinkedIn posts.

Each queue item displays:

- Influencer name
- Role and company
- LinkedIn profile
- Post content
- Link to the original LinkedIn post
- Sapho Bio AI response
- Response status
- Engagement actions

The dashboard also includes:

- Influencer count
- Post count
- AI response count
- Logged engagement count
- Text search
- Response-status filtering

Available filters include:

- All posts
- Needs response
- Draft generated
- Logged posted

---

## 4. AI-Assisted Sapho Bio Responses

The application integrates **Groq** for LLM-powered response generation.

The AI workflow receives the LinkedIn post context and generates a concise response appropriate for Sapho Bio.

The prompt is designed to encourage responses that are:

- Professional
- Specific to the source post
- Relevant to Sapho Bio
- Concise
- Non-promotional
- Scientifically responsible
- Suitable for professional LinkedIn engagement

The model is instructed not to invent unsupported scientific claims.

AI integration is implemented in:

`app/llm.py`

Responses are generated through:

`POST /api/posts/{post_id}/generate-response`

Generated responses are persisted to SQLite rather than existing only in the browser.

---

## 5. Human-in-the-Loop LinkedIn Workflow

The optional engagement workflow is implemented without claiming unrestricted LinkedIn publishing permissions.

After generating a response, the user can perform the following actions.

### Generate Response

Calls the Groq LLM using the selected LinkedIn post as context and generates a Sapho Bio response.

The generated response initially receives a **Draft** status.

### Regenerate Response

Allows the user to request another AI-generated version before publishing.

### Copy

Copies the generated response directly to the clipboard.

### Copy + Open LinkedIn

Copies the response and opens the original LinkedIn post.

The user can then review and paste the response directly into LinkedIn.

### Mark Posted

After publication, the user can mark the engagement as posted.

The application records:

- Response text
- Draft/posted status
- Creation time
- Posted time

This creates a lightweight engagement audit trail.

---

## Why Not Automatically Post Directly to LinkedIn?

Direct programmatic commenting on LinkedIn requires appropriate LinkedIn API access, authentication, scopes, and platform permissions.

For an MVP, attempting to work around those controls would be inappropriate and brittle.

Instead, this implementation provides a practical assisted workflow:

**Generate → Review → Copy + Open LinkedIn → Publish → Mark Posted**

This keeps a human in the loop while still reducing the amount of manual work required.

With approved LinkedIn API access, the final publication step could later be replaced by an authenticated API integration while preserving the rest of the application architecture.

---

## Architecture

```text
LinkedIn Public Sources
          |
          v
Collection / Validation Pipeline
scripts/collect_linkedin_posts.py
          |
          v
JSON Data Layer
influencers.json + posts.json
          |
          v
Database Seed Pipeline
app/seed.py
          |
          v
SQLite Database
          |
          +--------------------+
          |                    |
          v                    v
      FastAPI              Groq LLM
          |                    |
          +---------+----------+
                    |
                    v
           LinkedIn Queue UI
          HTML / CSS / JS
                    |
                    v
          Human Review Workflow
                    |
                    v
               LinkedIn
```

---

## Technology Stack

### Backend

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

### AI

- Groq API
- Groq Python SDK

### Frontend

- Jinja2
- HTML
- CSS
- Vanilla JavaScript

### Data Collection

- Python
- JSON
- Public LinkedIn source records

---

## Project Structure

```text
sapho-growth-engineer/
│
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── llm.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   │
│   └── templates/
│       └── index.html
│
├── data/
│   ├── influencers.json
│   ├── posts.json
│   ├── collected_posts.json
│   └── collection_report.json
│
├── scripts/
│   └── collect_linkedin_posts.py
│
├── screenshots/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

# Local Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd sapho-growth-engineer
```

## 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```text
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create `.env` from the included example:

```bash
cp .env.example .env
```

Then add a Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The real `.env` file is ignored by Git and should never be committed.

---

# Prepare the Dataset

Run the collection and validation pipeline:

```bash
python scripts/collect_linkedin_posts.py
```

Then seed the application database:

```bash
python -m app.seed
```

Expected database contents:

```text
Influencers in database: 10
Posts in database: 12
```

---

# Run the Application

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

Open the dashboard in a browser:

`http://127.0.0.1:8000`

Health endpoint:

`http://127.0.0.1:8000/health`

Posts API:

`http://127.0.0.1:8000/api/posts`

---

# API Endpoints

## Health Check

`GET /health`

Returns the current application health status.

---

## Retrieve Posts

`GET /api/posts`

Returns the LinkedIn post queue together with influencer information and generated responses.

---

## Generate Sapho Bio Response

`POST /api/posts/{post_id}/generate-response`

Calls the Groq LLM using the selected LinkedIn post and persists the generated response as a draft.

---

## Mark Response Posted

`POST /api/responses/{response_id}/mark-posted`

Updates the response status to posted and records the posting timestamp.

---

## Return Response to Draft

`POST /api/responses/{response_id}/mark-draft`

Returns a previously logged response to draft status.

---

# Database Model

The application uses three primary entities.

## Influencer

Stores:

- Name
- Title
- Company
- LinkedIn URL
- Relevance rationale

## LinkedInPost

Stores:

- Influencer relationship
- Post text
- Original LinkedIn URL
- Published timestamp when reliably available
- Collection timestamp

## GeneratedResponse

Stores:

- LinkedIn post relationship
- AI-generated response
- Draft/posted status
- Creation timestamp
- Posting timestamp

Relationship:

```text
Influencer
    |
    └── LinkedInPost
            |
            └── GeneratedResponse
```

---

# Example Product Workflow

A Growth team member opens the dashboard and sees a relevant post about sterile compounding quality.

They click:

**Generate Response**

The backend sends the post context to Groq.

Groq generates a professional response for Sapho Bio.

The response is stored as a draft.

The user reviews the response.

If they want another version, they click:

**Regenerate Response**

Once satisfied, they click:

**Copy + Open LinkedIn**

The response is copied and the original LinkedIn post is opened.

After publishing the comment, they return to the dashboard and click:

**Mark Posted**

The engagement is then logged in the database.

---

# Product Decisions

## Human Review Before Publishing

LLM-generated content should not automatically represent a biotechnology company without review.

The MVP therefore intentionally keeps a human approval step before publication.

## Persistent Responses

Generated responses are stored in SQLite so engagement history survives browser refreshes.

## Source Traceability

Every queue item links back to its original LinkedIn post.

## Conservative Timestamps

Dates are not fabricated when LinkedIn does not expose a reliable public timestamp.

## Lightweight Frontend

The assignment requested a lightweight HTML viewer, so the frontend intentionally avoids introducing a large JavaScript framework.

## Simple MVP Database

SQLite keeps local setup simple while still demonstrating a persistent relational data model.

A production deployment could replace SQLite with PostgreSQL without requiring a major application redesign.

---

# Safety and Responsible AI

The application is designed as an **AI-assisted**, rather than fully autonomous, engagement system.

Several safeguards are intentionally included:

- Human review before publication
- No automatic LinkedIn publishing without authorized API access
- No LinkedIn authentication bypass
- No CAPTCHA bypass
- No private API usage
- No fabricated post timestamps
- Original LinkedIn source links retained
- AI instructed to avoid unsupported scientific claims
- Engagement status stored for traceability

This is particularly important when generating external communications for a biotechnology company.

---

# Production Evolution

Given additional time and approved platform access, I would extend the system with:

- Official LinkedIn OAuth integration
- Authorized LinkedIn publishing
- PostgreSQL
- Scheduled post ingestion
- Background workers
- Engagement analytics
- Response approval workflows
- Multiple Sapho Bio response personas
- Prompt version tracking
- Semantic duplicate detection
- Influencer relevance scoring
- Post relevance ranking
- Automated engagement prioritization
- Authentication and team accounts
- Full audit logging
- Rate limiting
- Automated test coverage
- CI/CD
- Cloud deployment
- Monitoring and observability

---

# Current MVP Limitations

This project is intentionally scoped as an MVP.

Key limitations include:

1. LinkedIn public availability varies by profile and post.
2. Some reliable publication timestamps are unavailable from public sources.
3. Direct LinkedIn publishing is not performed without authorized API access.
4. Influencer selection is curated rather than generated from a large-scale social graph.
5. SQLite is suitable for the MVP but would be replaced by a production database at scale.
6. Generated AI responses should always be reviewed before external publication.

These limitations are intentionally handled transparently rather than hidden through fabricated data or unsupported automation.

---

# Key Engineering Choices

The goal of this implementation was not simply to generate an LLM response.

The MVP demonstrates an end-to-end workflow:

**Industry discovery → content collection → validation → persistence → AI generation → human review → engagement workflow → logging**

This architecture keeps the prototype lightweight while leaving clear paths for production expansion.

---

# Demo Checklist

For a quick demonstration:

1. Start the FastAPI server.
2. Open the LinkedIn Engagement Queue.
3. Review the 10 tracked industry influencers.
4. Search or filter the queue.
5. Select a relevant LinkedIn post.
6. Click **Generate Response**.
7. Review the Groq-generated Sapho Bio response.
8. Click **Regenerate Response** to demonstrate iterative generation.
9. Click **Copy** to demonstrate clipboard integration.
10. Click **Copy + Open LinkedIn** to demonstrate the assisted deployment workflow.
11. Click **Mark Posted** to demonstrate engagement logging.
12. Refresh the page to demonstrate persistence.

---

# Summary

This MVP satisfies the core assignment by combining:

- 10 relevant compounding pharmacy industry influencers
- Public LinkedIn post collection and validation
- A lightweight LinkedIn post queue
- Groq-powered Sapho Bio response generation
- Search and status filtering
- Persistent response storage
- Human-in-the-loop LinkedIn engagement
- Engagement logging
- A transparent and extensible architecture

The result is a functional prototype of how Sapho Bio could use AI to systematically identify relevant industry conversations and help its Growth team engage with them efficiently while maintaining human oversight.