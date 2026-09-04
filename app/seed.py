import json
from datetime import datetime
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.models import Influencer, LinkedInPost


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INFLUENCERS_FILE = DATA_DIR / "influencers.json"
POSTS_FILE = DATA_DIR / "posts.json"


def load_json(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_datetime(value):
    if not value:
        return None

    return datetime.fromisoformat(value)


def seed_database():
    Base.metadata.create_all(bind=engine)

    influencers_data = load_json(INFLUENCERS_FILE)
    posts_data = load_json(POSTS_FILE)

    db = SessionLocal()

    try:
        influencer_map = {}

        print()
        print("========================================")
        print("SEEDING INFLUENCERS")
        print("========================================")

        for item in influencers_data:
            influencer = (
                db.query(Influencer)
                .filter(
                    Influencer.linkedin_url == item["linkedin_url"]
                )
                .first()
            )

            if influencer is None:
                influencer = Influencer(
                    name=item["name"],
                    title=item.get("title"),
                    company=item.get("company"),
                    linkedin_url=item["linkedin_url"],
                    relevance_reason=item.get(
                        "relevance_reason"
                    ),
                )

                db.add(influencer)

                # Flush immediately so the influencer gets
                # a database ID without committing yet.
                db.flush()

                print(
                    f"Added influencer: {influencer.name}"
                )

            else:
                print(
                    f"Influencer already exists: "
                    f"{influencer.name}"
                )

            influencer_map[item["id"]] = influencer.id

        print()
        print("========================================")
        print("SEEDING LINKEDIN POSTS")
        print("========================================")

        seen_post_urls = set()

        added_posts = 0
        skipped_duplicate_source_posts = 0
        skipped_existing_posts = 0
        skipped_missing_influencer_posts = 0

        for item in posts_data:
            post_url = item["post_url"]

            # -----------------------------------------------------
            # Prevent duplicate URLs inside posts.json itself.
            # -----------------------------------------------------
            if post_url in seen_post_urls:
                skipped_duplicate_source_posts += 1

                print(
                    "Skipped duplicate source URL for post "
                    f"{item['id']}: {post_url}"
                )

                continue

            seen_post_urls.add(post_url)

            original_influencer_id = item[
                "influencer_id"
            ]

            database_influencer_id = influencer_map.get(
                original_influencer_id
            )

            if database_influencer_id is None:
                skipped_missing_influencer_posts += 1

                print(
                    "Skipped post because influencer "
                    "was not found: "
                    f"{original_influencer_id}"
                )

                continue

            existing_post = (
                db.query(LinkedInPost)
                .filter(
                    LinkedInPost.post_url == post_url
                )
                .first()
            )

            if existing_post is not None:
                skipped_existing_posts += 1

                print(
                    f"Post already exists: {post_url}"
                )

                continue

            post = LinkedInPost(
                influencer_id=database_influencer_id,
                post_text=item["post_text"],
                post_url=post_url,
                posted_at=parse_datetime(
                    item.get("posted_at")
                ),
            )

            db.add(post)

            # Flush each post individually so database-level
            # uniqueness problems are caught during processing.
            db.flush()

            added_posts += 1

            print(
                f"Added post {item['id']} for "
                f"{item.get('influencer_name', 'Unknown')}"
            )

        db.commit()

        influencer_count = db.query(
            Influencer
        ).count()

        post_count = db.query(
            LinkedInPost
        ).count()

        print()
        print("========================================")
        print("SEED COMPLETE")
        print("========================================")
        print(
            f"Influencers in database: "
            f"{influencer_count}"
        )
        print(
            f"Posts in database: {post_count}"
        )
        print(
            f"Posts added this run: {added_posts}"
        )
        print(
            "Duplicate source posts skipped: "
            f"{skipped_duplicate_source_posts}"
        )
        print(
            "Existing database posts skipped: "
            f"{skipped_existing_posts}"
        )
        print(
            "Posts with missing influencer skipped: "
            f"{skipped_missing_influencer_posts}"
        )

    except Exception:
        db.rollback()

        print()
        print("Seed failed. Transaction rolled back.")

        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()