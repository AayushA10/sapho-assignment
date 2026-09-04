from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.database import Base, engine, get_db
from app.llm import generate_sapho_response
from app.models import GeneratedResponse, LinkedInPost


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sapho Bio Growth Intelligence",
    description=(
        "LinkedIn content intelligence and "
        "AI-assisted engagement MVP."
    ),
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(
    directory="app/templates"
)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    posts = (
        db.query(LinkedInPost)
        .options(
            joinedload(
                LinkedInPost.influencer
            ),
            joinedload(
                LinkedInPost.responses
            ),
        )
        .order_by(
            LinkedInPost.id.desc()
        )
        .all()
    )

    total_posts = len(posts)

    unique_influencer_ids = {
        post.influencer_id
        for post in posts
    }

    total_influencers = len(
        unique_influencer_ids
    )

    total_responses = sum(
        len(post.responses)
        for post in posts
    )

    posted_responses = sum(
        1
        for post in posts
        for response in post.responses
        if response.status == "posted"
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "posts": posts,
            "total_posts": total_posts,
            "total_influencers": (
                total_influencers
            ),
            "total_responses": (
                total_responses
            ),
            "posted_responses": (
                posted_responses
            ),
        },
    )


@app.get("/api/posts")
def get_posts(
    db: Session = Depends(get_db),
):
    posts = (
        db.query(LinkedInPost)
        .options(
            joinedload(
                LinkedInPost.influencer
            ),
            joinedload(
                LinkedInPost.responses
            ),
        )
        .order_by(
            LinkedInPost.id.desc()
        )
        .all()
    )

    return [
        {
            "id": post.id,
            "influencer_id": (
                post.influencer_id
            ),
            "influencer_name": (
                post.influencer.name
                if post.influencer
                else None
            ),
            "influencer_title": (
                post.influencer.title
                if post.influencer
                else None
            ),
            "company": (
                post.influencer.company
                if post.influencer
                else None
            ),
            "linkedin_profile_url": (
                post.influencer.linkedin_url
                if post.influencer
                else None
            ),
            "post_text": (
                post.post_text
            ),
            "post_url": (
                post.post_url
            ),
            "posted_at": (
                post.posted_at
            ),
            "created_at": (
                post.created_at
            ),
            "responses": [
                {
                    "id": response.id,
                    "response_text": (
                        response.response_text
                    ),
                    "status": (
                        response.status
                    ),
                    "created_at": (
                        response.created_at
                    ),
                    "posted_at": (
                        response.posted_at
                    ),
                }
                for response
                in sorted(
                    post.responses,
                    key=lambda item: item.id,
                    reverse=True,
                )
            ],
        }
        for post in posts
    ]


@app.post(
    "/api/posts/{post_id}/generate-response"
)
def generate_response(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = (
        db.query(LinkedInPost)
        .filter(
            LinkedInPost.id == post_id
        )
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail=(
                "LinkedIn post not found."
            ),
        )

    try:
        response_text = (
            generate_sapho_response(
                post.post_text
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate "
                "Sapho Bio response."
            ),
        ) from exc

    generated_response = (
        GeneratedResponse(
            post_id=post.id,
            response_text=response_text,
            status="draft",
        )
    )

    db.add(
        generated_response
    )
    db.commit()
    db.refresh(
        generated_response
    )

    return {
        "id": (
            generated_response.id
        ),
        "post_id": (
            generated_response.post_id
        ),
        "response_text": (
            generated_response.response_text
        ),
        "status": (
            generated_response.status
        ),
        "created_at": (
            generated_response.created_at
        ),
        "posted_at": (
            generated_response.posted_at
        ),
    }


@app.post(
    "/api/responses/{response_id}/mark-posted"
)
def mark_response_posted(
    response_id: int,
    db: Session = Depends(get_db),
):
    response = (
        db.query(GeneratedResponse)
        .filter(
            GeneratedResponse.id
            == response_id
        )
        .first()
    )

    if not response:
        raise HTTPException(
            status_code=404,
            detail=(
                "Generated response "
                "not found."
            ),
        )

    response.status = "posted"
    response.posted_at = (
        datetime.utcnow()
    )

    db.commit()
    db.refresh(
        response
    )

    return {
        "id": response.id,
        "post_id": (
            response.post_id
        ),
        "status": (
            response.status
        ),
        "posted_at": (
            response.posted_at
        ),
    }


@app.post(
    "/api/responses/{response_id}/mark-draft"
)
def mark_response_draft(
    response_id: int,
    db: Session = Depends(get_db),
):
    response = (
        db.query(GeneratedResponse)
        .filter(
            GeneratedResponse.id
            == response_id
        )
        .first()
    )

    if not response:
        raise HTTPException(
            status_code=404,
            detail=(
                "Generated response "
                "not found."
            ),
        )

    response.status = "draft"
    response.posted_at = None

    db.commit()
    db.refresh(
        response
    )

    return {
        "id": response.id,
        "post_id": (
            response.post_id
        ),
        "status": (
            response.status
        ),
        "posted_at": (
            response.posted_at
        ),
    }