import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx


BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_INFLUENCERS_FILE = (
    BASE_DIR / "data" / "influencers.json"
)

DEFAULT_POSTS_FILE = (
    BASE_DIR / "data" / "posts.json"
)

DEFAULT_OUTPUT_FILE = (
    BASE_DIR / "data" / "collected_posts.json"
)

DEFAULT_REPORT_FILE = (
    BASE_DIR / "data" / "collection_report.json"
)


LINKEDIN_HOSTS = {
    "linkedin.com",
    "www.linkedin.com",
}


BLOCKED_URL_FRAGMENTS = (
    "/recent-activity/",
    "/in/",
    "/company/",
)


def load_json(
    file_path: Path,
) -> list[dict[str, Any]]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected JSON list in {file_path}"
        )

    return data


def save_json(
    file_path: Path,
    data: Any,
) -> None:
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

        file.write("\n")


def normalize_url(
    url: str,
) -> str:
    return url.strip()


def is_linkedin_url(
    url: str,
) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in {
        "http",
        "https",
    }:
        return False

    return parsed.netloc.lower() in (
        LINKEDIN_HOSTS
    )


def is_individual_post_url(
    url: str,
) -> bool:
    if not is_linkedin_url(url):
        return False

    lowered = url.lower()

    if any(
        fragment in lowered
        for fragment in BLOCKED_URL_FRAGMENTS
    ):
        return False

    valid_patterns = (
        "/posts/",
        "/feed/update/urn:li:activity:",
    )

    return any(
        pattern in lowered
        for pattern in valid_patterns
    )


def validate_influencers(
    influencers: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    influencer_map = {}

    required_fields = {
        "id",
        "name",
        "linkedin_url",
    }

    for influencer in influencers:
        missing = (
            required_fields
            - influencer.keys()
        )

        if missing:
            raise ValueError(
                "Influencer missing required "
                f"fields: {sorted(missing)}"
            )

        influencer_id = influencer["id"]

        if influencer_id in influencer_map:
            raise ValueError(
                "Duplicate influencer id: "
                f"{influencer_id}"
            )

        if not is_linkedin_url(
            influencer["linkedin_url"]
        ):
            raise ValueError(
                "Invalid LinkedIn profile URL "
                f"for {influencer['name']}: "
                f"{influencer['linkedin_url']}"
            )

        influencer_map[
            influencer_id
        ] = influencer

    return influencer_map


def normalize_post(
    post: dict[str, Any],
    influencer_map: dict[
        int,
        dict[str, Any],
    ],
) -> dict[str, Any]:
    required_fields = {
        "id",
        "influencer_id",
        "post_text",
        "post_url",
    }

    missing = (
        required_fields
        - post.keys()
    )

    if missing:
        raise ValueError(
            "Post missing required fields: "
            f"{sorted(missing)}"
        )

    influencer_id = post[
        "influencer_id"
    ]

    if influencer_id not in influencer_map:
        raise ValueError(
            "Unknown influencer id "
            f"{influencer_id} "
            f"for post {post['id']}"
        )

    post_url = normalize_url(
        post["post_url"]
    )

    if not is_individual_post_url(
        post_url
    ):
        raise ValueError(
            "Post does not use a unique "
            "LinkedIn post URL: "
            f"{post_url}"
        )

    post_text = (
        post["post_text"]
        .strip()
    )

    if not post_text:
        raise ValueError(
            "Empty post text for "
            f"post {post['id']}"
        )

    influencer = influencer_map[
        influencer_id
    ]

    return {
        "id": post["id"],
        "influencer_id": influencer_id,
        "influencer_name": (
            post.get(
                "influencer_name"
            )
            or influencer["name"]
        ),
        "post_text": post_text,
        "post_url": post_url,
        "posted_at": post.get(
            "posted_at"
        ),
        "source": post.get(
            "source",
            "LinkedIn",
        ),
        "status": post.get(
            "status",
            "collected",
        ),
    }


def deduplicate_posts(
    posts: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[str],
]:
    seen_urls = set()

    unique_posts = []
    duplicate_urls = []

    for post in posts:
        url = post["post_url"]

        if url in seen_urls:
            duplicate_urls.append(
                url
            )

            continue

        seen_urls.add(url)
        unique_posts.append(post)

    return (
        unique_posts,
        duplicate_urls,
    )


def cap_posts_per_influencer(
    posts: list[dict[str, Any]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    grouped = defaultdict(list)

    for post in posts:
        grouped[
            post["influencer_id"]
        ].append(post)

    selected = []

    for influencer_id in sorted(
        grouped
    ):
        influencer_posts = (
            grouped[influencer_id]
        )

        influencer_posts.sort(
            key=lambda item: item["id"]
        )

        selected.extend(
            influencer_posts[:limit]
        )

    return selected


def probe_public_url(
    client: httpx.Client,
    url: str,
) -> dict[str, Any]:
    try:
        response = client.get(
            url,
            follow_redirects=True,
        )

        return {
            "reachable": (
                200
                <= response.status_code
                < 400
            ),
            "status_code": (
                response.status_code
            ),
            "final_url": str(
                response.url
            ),
        }

    except httpx.HTTPError as exc:
        return {
            "reachable": False,
            "status_code": None,
            "final_url": None,
            "error": str(exc),
        }


def build_collection_report(
    influencers: list[
        dict[str, Any]
    ],
    posts: list[
        dict[str, Any]
    ],
    duplicates: list[str],
    probe_results: dict[
        str,
        dict[str, Any],
    ],
) -> dict[str, Any]:
    represented = {
        post["influencer_id"]
        for post in posts
    }

    per_influencer = defaultdict(
        int
    )

    for post in posts:
        per_influencer[
            str(
                post["influencer_id"]
            )
        ] += 1

    reachable_count = sum(
        1
        for result
        in probe_results.values()
        if result.get(
            "reachable"
        )
    )

    return {
        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "collection_method": (
            "Public LinkedIn URL "
            "collection and validation"
        ),
        "authentication_bypassed": (
            False
        ),
        "influencers_total": (
            len(influencers)
        ),
        "influencers_represented": (
            len(represented)
        ),
        "posts_total": (
            len(posts)
        ),
        "duplicate_urls_removed": (
            len(duplicates)
        ),
        "posts_per_influencer": dict(
            per_influencer
        ),
        "public_probe_enabled": (
            bool(probe_results)
        ),
        "public_urls_reachable": (
            reachable_count
        ),
        "probe_results": (
            probe_results
        ),
    }


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Validate, deduplicate, "
            "and normalize public "
            "LinkedIn post records."
        )
    )

    parser.add_argument(
        "--influencers",
        type=Path,
        default=(
            DEFAULT_INFLUENCERS_FILE
        ),
        help=(
            "Path to influencers JSON."
        ),
    )

    parser.add_argument(
        "--posts",
        type=Path,
        default=DEFAULT_POSTS_FILE,
        help=(
            "Path to collected posts JSON."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=(
            "Path for normalized output."
        ),
    )

    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_FILE,
        help=(
            "Path for collection report."
        ),
    )

    parser.add_argument(
        "--probe",
        action="store_true",
        help=(
            "Attempt to reach each public "
            "LinkedIn post URL."
        ),
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        influencers = load_json(
            args.influencers
        )

        posts = load_json(
            args.posts
        )

        influencer_map = (
            validate_influencers(
                influencers
            )
        )

        normalized_posts = []

        for post in posts:
            normalized_posts.append(
                normalize_post(
                    post,
                    influencer_map,
                )
            )

        (
            normalized_posts,
            duplicate_urls,
        ) = deduplicate_posts(
            normalized_posts
        )

        normalized_posts = (
            cap_posts_per_influencer(
                normalized_posts,
                limit=10,
            )
        )

        probe_results = {}

        if args.probe:
            print()
            print(
                "Checking public "
                "LinkedIn URLs..."
            )

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; "
                    "SaphoGrowthResearch/1.0)"
                )
            }

            with httpx.Client(
                headers=headers,
                timeout=10.0,
            ) as client:
                for post in (
                    normalized_posts
                ):
                    url = post[
                        "post_url"
                    ]

                    result = (
                        probe_public_url(
                            client,
                            url,
                        )
                    )

                    probe_results[
                        url
                    ] = result

                    print(
                        f"{post['id']}: "
                        f"{result.get('status_code')}"
                    )

        report = (
            build_collection_report(
                influencers,
                normalized_posts,
                duplicate_urls,
                probe_results,
            )
        )

        save_json(
            args.output,
            normalized_posts,
        )

        save_json(
            args.report,
            report,
        )

        represented = {
            post["influencer_id"]
            for post
            in normalized_posts
        }

        print()
        print(
            "========================================"
        )
        print(
            "LINKEDIN COLLECTION COMPLETE"
        )
        print(
            "========================================"
        )
        print(
            "Influencers configured:",
            len(influencers),
        )
        print(
            "Influencers represented:",
            len(represented),
        )
        print(
            "Unique posts collected:",
            len(normalized_posts),
        )
        print(
            "Duplicate URLs removed:",
            len(duplicate_urls),
        )
        print(
            "Output:",
            args.output,
        )
        print(
            "Audit report:",
            args.report,
        )
        print()
        print(
            "No LinkedIn authentication, "
            "private API, CAPTCHA bypass, "
            "or access-control bypass was used."
        )

    except Exception as exc:
        print(
            f"\nCOLLECTION FAILED: {exc}",
            file=sys.stderr,
        )

        raise


if __name__ == "__main__":
    main()