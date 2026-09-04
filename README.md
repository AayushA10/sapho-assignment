# Sapho Bio Growth Intelligence

**LinkedIn Content Intelligence + AI-Assisted Growth Engagement MVP**

A lightweight end-to-end Growth Engineering application built for the **Sapho Bio Growth Engineer take-home assignment**.

The system identifies relevant voices in the compounding pharmacy ecosystem, organizes their LinkedIn content into an engagement queue, generates contextual Sapho Bio responses using an LLM, and provides a human-in-the-loop workflow for reviewing, deploying, and logging engagement.

---

## 🚀 Live Demo

### https://sapho-assignment.onrender.com

The application is publicly deployed on **Render** and connected to the **Groq API** for live AI response generation.

> **Demo availability note:** This application is hosted on Render's free compute tier for demonstration purposes. Free instances may spin down after periods of inactivity. As a result, the first request after inactivity can take approximately 30–60 seconds to wake the service. Subsequent requests should load normally.

---

## Assignment

The take-home assignment requested an MVP capable of:

1. Building a list of the top 10 influencers from the compounding pharmacy industry on LinkedIn.
2. Collecting a list of their latest posts from the last month or latest 10 posts.
3. Creating a lightweight HTML viewer for the post queue.
4. Using an LLM API to generate an appropriate response from Sapho Bio.
5. Optionally making the response deployable to LinkedIn with a single-click workflow and logging the action.

This implementation covers all five areas through a functional end-to-end prototype.

---

# Assignment → Implementation

| Requirement | Implementation |
|---|---|
| Top 10 industry influencers | Curated dataset of 10 compounding-pharmacy professionals |
| LinkedIn post collection | Public-source collection, normalization, validation and deduplication pipeline |
| Lightweight HTML viewer | FastAPI + Jinja2 responsive engagement dashboard |
| LLM response generation | Groq-powered contextual Sapho Bio response generation |
| Single-click-assisted deployment | Copy + Open LinkedIn workflow |
| Engagement logging | Persistent draft/posted response tracking |
| Public demonstration | Deployed application on Render |

---

# Product Overview

The application turns LinkedIn industry monitoring into a structured Growth workflow:

```text
Discover relevant industry voices
              ↓
Collect relevant LinkedIn content
              ↓
Validate and normalize source records
              ↓
Store content in a structured database
              ↓
Prioritize content in an engagement queue
              ↓
Generate contextual Sapho Bio responses
              ↓
Human review / regenerate if necessary
              ↓
Copy response + open original LinkedIn post
              ↓
Publish manually
              ↓
Log engagement status
```

The goal is not simply to call an LLM.

The MVP demonstrates how an AI-assisted system could help a Growth team systematically discover, review, engage with, and track relevant industry conversations.

---

# Core Features

## 1. Compounding Pharmacy Influencer Dataset

The project contains a curated list of **10 professionals** relevant to the compounding pharmacy ecosystem.

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

Each record contains:

- Name
- Role
- Company
- LinkedIn profile
- Industry relevance rationale

---

## 2. LinkedIn Content Collection

Source post records are maintained in:

`data/posts.json`

A reproducible collection and validation pipeline is implemented in:

`scripts/collect_linkedin_posts.py`

The pipeline:

- Loads configured influencers
- Loads public-source post records
- Validates influencer references
- Validates LinkedIn URLs
- Requires individual LinkedIn post URLs
- Rejects generic profile/activity URLs
- Normalizes records
- Deduplicates post URLs
- Caps collection at 10 posts per influencer
- Produces a normalized output dataset
- Produces an auditable collection report

Run the pipeline with:

```bash
python scripts/collect_linkedin_posts.py
```

Generated artifacts:

```text
data/collected_posts.json
data/collection_report.json
```

Current dataset:

```text
Influencers configured:     10
Influencers represented:    10
Unique posts collected:     12
Duplicate URLs removed:      0
```

---

## LinkedIn Collection Methodology

LinkedIn does not guarantee unrestricted anonymous or automated access to all profile and post content.

For that reason, this MVP intentionally uses a **public-source collection and validation approach** rather than attempting to circumvent platform controls.

The implementation does **not** use:

- Login automation
- CAPTCHA bypass
- Access-control bypass
- Private LinkedIn APIs
- Scraped credentials
- Undocumented publishing mechanisms

Publicly discoverable post records were curated and then passed through a reproducible validation, normalization, and deduplication pipeline.

Where a reliable publication timestamp is unavailable from the public source, `posted_at` is intentionally left null rather than fabricating a timestamp.

The assignment allows content from the **last month or latest 10 posts**. The MVP uses relevant recent/latest publicly accessible content across the selected influencers and maintains a maximum of 10 records per influencer in the collection pipeline.

For some records, `post_text` represents a concise content snapshot or summary rather than claiming to reproduce the complete original LinkedIn post verbatim.

Every queue item retains its original LinkedIn source URL for traceability.

---

# 3. LinkedIn Engagement Queue

The collected content is presented through a lightweight responsive HTML dashboard.

Each queue card displays:

- Influencer name
- Role
- Company
- LinkedIn context
- Post content snapshot
- Original LinkedIn source
- Sapho Bio AI response
- Response status
- Engagement controls

The dashboard also provides:

- Number of tracked influencers
- Number of collected posts
- Number of AI-generated responses
- Number of logged engagements
- Search
- Status filtering

Available filters:

```text
All posts
Needs response
Draft generated
Logged posted
```

This allows a Growth user to quickly distinguish between untouched content, AI-assisted drafts, and completed engagements.

---

# 4. Groq-Powered Response Generation

The application integrates the **Groq API** for LLM-powered response generation.

The current implementation uses:

`openai/gpt-oss-20b`

through the Groq Python SDK.

AI integration is implemented in:

`app/llm.py`

The generation workflow receives the source LinkedIn content and creates a concise professional response suitable for Sapho Bio.

The prompt is designed to encourage responses that are:

- Contextual
- Professional
- Concise
- Relevant to the source discussion
- Appropriate for LinkedIn
- Non-spammy
- Non-promotional
- Scientifically responsible

The model is instructed not to fabricate unsupported scientific claims.

Responses are generated through:

`POST /api/posts/{post_id}/generate-response`

The generated result is persisted to the database rather than existing only in browser state.

---

# 5. Human-in-the-Loop AI Workflow

The system intentionally does not automatically publish an LLM-generated biotechnology-company response without review.

Instead, each generated response enters a **Draft** state.

The user can then:

### Generate Response

Generate a contextual Sapho Bio response from the selected LinkedIn content.

### Regenerate Response

Request a new response when the initial generation is not ideal.

### Copy

Copy the response directly to the clipboard.

### Copy + Open LinkedIn

Copy the response and attempt to open the exact original LinkedIn post in a new browser tab.

This minimizes the steps required to move from AI generation to human-approved engagement.

Browser popup settings may occasionally prevent the LinkedIn tab from opening automatically. In that situation, the response is still copied and the UI reports that the browser blocked the new tab.

### Mark Posted

Once the user has published the response, the engagement can be marked as posted.

The database records:

- Response text
- Response status
- Creation timestamp
- Posting timestamp

This creates a lightweight engagement audit trail.

---

# Why Human Review Instead of Fully Autonomous Publishing?

Direct LinkedIn publishing requires approved authentication, scopes, and platform permissions.

More importantly, an AI-generated response representing a biotechnology company should have human oversight before external publication.

The MVP therefore uses:

```text
AI generation
      ↓
Human review
      ↓
Optional regeneration
      ↓
Copy + Open LinkedIn
      ↓
Human publication
      ↓
Engagement logging
```

This approach provides most of the workflow efficiency without pretending to have unrestricted LinkedIn publishing permissions.

With approved LinkedIn API access, the publication step could later be replaced with an authenticated integration while preserving the rest of the architecture.

---

# System Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                  PUBLIC INDUSTRY SOURCES                     │
│                                                              │
│     Compounding Pharmacy Professionals + LinkedIn Posts      │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ Public-source research
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                 SOURCE DATA LAYER                            │
│                                                              │
│  data/influencers.json              data/posts.json          │
│                                                              │
│  • Industry professionals           • Post snapshots         │
│  • Roles / companies                • Source URLs            │
│  • LinkedIn profiles                • Post metadata          │
│  • Relevance rationale                                      │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│             COLLECTION + VALIDATION PIPELINE                 │
│                                                              │
│          scripts/collect_linkedin_posts.py                   │
│                                                              │
│  Validate URLs → Normalize → Deduplicate → Audit             │
└─────────────────────┬─────────────────────┬──────────────────┘
                      │                     │
                      ▼                     ▼
        ┌──────────────────────┐   ┌────────────────────────┐
        │ collected_posts.json │   │ collection_report.json │
        └──────────┬───────────┘   └────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                    DATABASE SEEDING                          │
│                                                              │
│                        app/seed.py                           │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                      SQLITE DATABASE                         │
│                                                              │
│   Influencer ──────► LinkedInPost ──────► GeneratedResponse │
│                                                              │
│   Profiles            Content             Draft / Posted     │
│   Metadata            Source URLs         Timestamps         │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION                       │
│                                                              │
│                        app/main.py                           │
│                                                              │
│        REST API + Business Logic + Jinja Rendering           │
└───────────────┬──────────────────────────────┬───────────────┘
                │                              │
                │                              │
                ▼                              ▼
┌────────────────────────────┐    ┌────────────────────────────┐
│       WEB INTERFACE        │    │         GROQ API           │
│                            │    │                            │
│ Jinja2                     │    │ openai/gpt-oss-20b         │
│ HTML                       │◄──►│                            │
│ CSS                        │    │ Contextual response        │
│ JavaScript                 │    │ generation                │
└──────────────┬─────────────┘    └────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                 HUMAN-IN-THE-LOOP WORKFLOW                   │
│                                                              │
│ Generate → Review → Regenerate → Copy → Open LinkedIn        │
│                              ↓                               │
│                         Mark Posted                          │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                       LINKEDIN                               │
│                                                              │
│          Human-approved external engagement                  │
└──────────────────────────────────────────────────────────────┘
```

---

# Architecture Principles

The MVP was designed around several principles.

### Separation of Concerns

Collection, persistence, AI generation, API behavior, and presentation are separated into independent application layers.

### Source Traceability

Every content item retains its original LinkedIn URL.

### Persistent State

Generated responses and engagement statuses are stored in SQLite instead of being maintained only in frontend memory.

### Human Oversight

The LLM assists with engagement but does not independently represent Sapho Bio externally.

### Replaceable Components

The architecture allows SQLite to be replaced by PostgreSQL, Groq models to be changed, or authorized LinkedIn APIs to be integrated without redesigning the entire product.

### MVP Simplicity

FastAPI, Jinja2, vanilla JavaScript, and SQLite keep the prototype easy to run and inspect while still demonstrating a complete application architecture.

---

# Technology Stack

## Backend

- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

## Database

- SQLite

## AI

- Groq API
- Groq Python SDK
- `openai/gpt-oss-20b`

## Frontend

- Jinja2
- HTML
- CSS
- Vanilla JavaScript

## Data Pipeline

- Python
- JSON
- Public-source LinkedIn records

## Deployment

- Render Web Service
- GitHub-connected deployment
- Environment-based secret management

---

# Repository Structure

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
│   │   │
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

# Local Development

## 1. Clone the Repository

```bash
git clone https://github.com/AayushA10/sapho-assignment.git
cd sapho-assignment
```

---

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

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure the Groq API Key

Create a local environment file:

```bash
cp .env.example .env
```

Then configure:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The real `.env` file is excluded through `.gitignore`.

API keys should never be committed to the repository.

---

# Prepare the Data

Run the collection and validation pipeline:

```bash
python scripts/collect_linkedin_posts.py
```

Then seed the database:

```bash
python -m app.seed
```

Expected dataset:

```text
Influencers in database: 10
Posts in database: 12
```

---

# Run Locally

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Then open:

`http://127.0.0.1:8000`

Health check:

`http://127.0.0.1:8000/health`

Posts API:

`http://127.0.0.1:8000/api/posts`

---

# API

## Health Check

```text
GET /health
```

Returns the current application health status.

---

## Retrieve Engagement Queue

```text
GET /api/posts
```

Returns the post queue together with influencer information and generated-response state.

---

## Generate Sapho Bio Response

```text
POST /api/posts/{post_id}/generate-response
```

Generates a contextual response through Groq and persists it as a draft.

---

## Mark Response Posted

```text
POST /api/responses/{response_id}/mark-posted
```

Marks an engagement as posted and records the posting timestamp.

---

## Return Response to Draft

```text
POST /api/responses/{response_id}/mark-draft
```

Returns a previously logged engagement to draft state.

---

# Data Model

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
- Post content
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
    │
    │ 1:N
    ▼
LinkedInPost
    │
    │ 1:N
    ▼
GeneratedResponse
```

---

# Example Demo Flow

A Growth team member opens the application.

### Step 1 — Discover

The dashboard presents relevant posts from tracked compounding pharmacy professionals.

### Step 2 — Prioritize

The user can search the queue or filter posts by engagement state.

### Step 3 — Generate

The user selects:

**Generate Response**

The backend sends the relevant post context to Groq.

### Step 4 — Review

The generated response appears as a **Draft**.

The user can edit their intended workflow by regenerating if necessary.

### Step 5 — Deploy

The user selects:

**Copy + Open LinkedIn**

The response is copied and the original LinkedIn post is opened.

### Step 6 — Log

After publishing the approved comment, the user selects:

**Mark Posted**

The engagement is persisted with its status and timestamp.

---

# Deployment

The live MVP is deployed as a Render Web Service connected to the GitHub repository.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The database is initialized and seeded when the service starts.

The Groq API key is supplied through Render environment variables and is never stored in source control.

---

# Deployment Persistence Note

The public demo uses the **Render free tier** and a local SQLite database.

This is appropriate for a take-home MVP, but the free service does not provide a persistent disk.

Therefore, application state should be treated as **demo state rather than durable production storage**. A service restart or redeployment can recreate the SQLite database from the repository's seed data.

For production, I would use a managed PostgreSQL database so generated responses and engagement history persist independently of application instances.

This deployment choice keeps the take-home demo simple and free while keeping the production migration path clear.

---

# Responsible AI and Safety

The system is intentionally designed as **AI-assisted engagement**, not autonomous corporate communication.

Safeguards include:

- Human review before publication
- Draft state for generated responses
- Ability to regenerate responses
- Original source traceability
- No automatic LinkedIn publication without authorization
- No authentication bypass
- No CAPTCHA bypass
- No private LinkedIn API usage
- Conservative timestamp handling
- Prompt instructions against unsupported scientific claims
- Engagement status logging
- API secrets excluded from source control

These controls are especially relevant when AI-generated communication may represent a biotechnology company.

---

# Key Product Decisions

## Human Review Before Publishing

LLM output should not automatically represent a biotechnology company externally.

Human approval is therefore a deliberate part of the product architecture rather than an implementation limitation.

## Source Traceability

Every queue item retains the original LinkedIn post URL.

## Persistent Application Model

AI responses are represented as database entities rather than temporary frontend text.

## Lightweight Frontend

The assignment requested a lightweight HTML viewer.

Jinja2 and vanilla JavaScript provide the required interactivity without unnecessary frontend framework complexity.

## SQLite for MVP

SQLite provides zero-configuration relational persistence for local development and demonstration.

A production system would use PostgreSQL.

## Transparent LinkedIn Integration

The MVP does not claim permissions it does not have.

Instead, it demonstrates the workflow through a human-in-the-loop deployment path that could later be upgraded to an official authenticated LinkedIn integration.

---

# Current MVP Limitations

This project is intentionally scoped as an MVP.

Key limitations:

1. LinkedIn public availability varies by profile and post.
2. Some reliable publication timestamps are unavailable from public sources.
3. Direct LinkedIn publishing is not performed without approved API access.
4. Influencer selection is curated rather than generated from a large-scale social graph.
5. The current dataset is a representative public-source snapshot rather than a continuously running crawler.
6. AI responses require human review before external use.
7. SQLite is appropriate for the MVP but not the intended production database.
8. The free Render deployment can sleep after inactivity and may take approximately 30–60 seconds to wake.
9. Free Render storage is ephemeral, so demo database state may reset following a restart or redeployment.

These constraints are documented rather than hidden behind fabricated data or unsupported platform automation.

---

# Production Evolution

With additional time and appropriate platform access, I would evolve the MVP toward:

### Data Acquisition

- Scheduled ingestion
- Approved LinkedIn API integrations
- Incremental post discovery
- Semantic deduplication
- Influencer discovery and ranking

### AI

- Response style controls
- Multiple Sapho Bio personas
- Prompt versioning
- Retrieval-augmented company context
- Scientific claim validation
- Response quality evaluation

### Growth Intelligence

- Post relevance scoring
- Engagement opportunity ranking
- Topic clustering
- Influencer relationship history
- Engagement analytics
- Conversion attribution

### Platform

- PostgreSQL
- Background workers
- Authentication
- Team accounts
- Role-based permissions
- Full audit logging
- Rate limiting
- Automated tests
- CI/CD
- Monitoring and observability

### LinkedIn

With approved platform access:

```text
LinkedIn OAuth
      ↓
Authorized API
      ↓
Human-approved response
      ↓
Direct publishing
      ↓
Automatic engagement logging
```

The current architecture allows these capabilities to be added incrementally.

---

# Demo Checklist

For a quick evaluation of the MVP:

1. Open the live application.
2. Review the tracked industry professionals.
3. Review the 12-post engagement queue.
4. Search for an influencer or topic.
5. Filter by response status.
6. Select a post.
7. Click **Generate Response**.
8. Review the Groq-generated Sapho Bio response.
9. Click **Regenerate Response**.
10. Click **Copy**.
11. Click **Copy + Open LinkedIn**.
12. Return to the application.
13. Click **Mark Posted**.
14. Filter by **Logged posted** to verify the engagement workflow.

---

# Live Demo

### https://sapho-assignment.onrender.com

> Hosted on Render's free tier. If the service has been inactive, please allow approximately 30–60 seconds for the initial request while the instance wakes.

---

# Repository

### https://github.com/AayushA10/sapho-assignment

---

# Summary

**Sapho Bio Growth Intelligence** demonstrates an end-to-end AI-assisted Growth Engineering workflow:

```text
Industry Discovery
        ↓
LinkedIn Content Collection
        ↓
Validation + Normalization
        ↓
Structured Persistence
        ↓
Engagement Queue
        ↓
Groq LLM Generation
        ↓
Human Review
        ↓
LinkedIn-Assisted Deployment
        ↓
Engagement Logging
```

Rather than treating the assignment as only an LLM demo, the implementation focuses on the complete operational workflow around AI-assisted industry engagement.

The result is a lightweight but extensible prototype showing how Sapho Bio could systematically identify relevant conversations, generate contextual responses, preserve human oversight, and track engagement from a single interface.