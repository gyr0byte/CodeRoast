"""
CodeRoast — GitHub Code Scraper
Scrapes Python, Java, and JavaScript code from GitHub repositories
to build a labeled training dataset.

Strategy:
    - High-star repos (500+ stars)  → quality 0 (Pristine) or 1 (Acceptable)
    - Low-star abandoned repos      → quality 2 (Concerning) or 3 (Disaster)

Usage:
    python data/scrape_github.py

Requirements:
    - GitHub personal access token in environment variable GITHUB_TOKEN
    - Or: set token in the script below (not recommended for public repos)

Output:
    data/raw/scraped_code.csv
"""

import os
import re
import sys
import time
import csv
import random
import requests
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


# ─── Configuration ───────────────────────────────────────────────────────────

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

BASE_URL = "https://api.github.com"

# Target: ~600 samples across 3 languages
SAMPLES_PER_LANGUAGE = 200
LANGUAGES = ["python", "java", "javascript"]

# File extensions to look for
EXTENSIONS = {
    "python": [".py"],
    "java": [".java"],
    "javascript": [".js"],
}

# Query parameters for high vs low quality repos
HIGH_QUALITY_QUERY = {
    "python": "language:python stars:>500 pushed:>2024-01-01",
    "java": "language:java stars:>500 pushed:>2024-01-01",
    "javascript": "language:javascript stars:>500 pushed:>2024-01-01",
}

LOW_QUALITY_QUERY = {
    "python": "language:python stars:<5 pushed:<2022-01-01",
    "java": "language:java stars:<5 pushed:<2022-01-01",
    "javascript": "language:javascript stars:<5 pushed:<2022-01-01",
}


# ─── API Helpers ─────────────────────────────────────────────────────────────

def github_request(url: str, params: dict = None) -> dict:
    """Make a rate-limited GitHub API request."""
    response = requests.get(url, headers=HEADERS, params=params)

    # Handle rate limiting
    if response.status_code == 403:
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
        wait_seconds = max(reset_time - int(time.time()), 60)
        print(f"[RATE LIMIT] Waiting {wait_seconds}s for rate limit reset...")
        time.sleep(wait_seconds + 1)
        return github_request(url, params)  # Retry

    if response.status_code != 200:
        print(f"[WARNING] API returned {response.status_code}: {response.text[:200]}")
        return {}

    return response.json()


def search_repos(query: str, per_page: int = 30, page: int = 1) -> list:
    """Search GitHub repositories."""
    data = github_request(
        f"{BASE_URL}/search/repositories",
        params={"q": query, "per_page": per_page, "page": page, "sort": "stars"},
    )
    return data.get("items", [])


def get_repo_contents(owner: str, repo: str, path: str = "") -> list:
    """Get the file tree of a repository (top-level or specific path)."""
    data = github_request(f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}")
    if isinstance(data, list):
        return data
    return []


def get_file_content(download_url: str) -> str:
    """Download raw file content from GitHub."""
    try:
        response = requests.get(download_url, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return ""


# ─── Function Extraction ────────────────────────────────────────────────────

def extract_functions_python(code: str) -> list:
    """Extract individual function definitions from Python code."""
    import ast
    functions = []
    try:
        tree = ast.parse(code)
        lines = code.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno - 1
                end = getattr(node, "end_lineno", start + 1)
                func_code = "\n".join(lines[start:end])
                if 5 <= len(func_code.splitlines()) <= 100:
                    functions.append(func_code)
    except SyntaxError:
        pass
    return functions


def extract_functions_java(code: str) -> list:
    """Extract method definitions from Java code using regex."""
    pattern = re.compile(
        r"((?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{)",
        re.MULTILINE,
    )
    functions = []
    for match in pattern.finditer(code):
        start = match.start()
        # Find matching closing brace
        brace_count = 0
        end = start
        for i in range(start, len(code)):
            if code[i] == "{":
                brace_count += 1
            elif code[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        func_code = code[start:end]
        lines = func_code.splitlines()
        if 5 <= len(lines) <= 100:
            functions.append(func_code)
    return functions


def extract_functions_js(code: str) -> list:
    """Extract function definitions from JavaScript code using regex."""
    functions = []

    # Match: function name(...) { ... }
    pattern1 = re.compile(
        r"(function\s+\w+\s*\([^)]*\)\s*\{)",
        re.MULTILINE,
    )

    # Match: const/let/var name = function(...) { ... }
    pattern2 = re.compile(
        r"((?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?function\s*\([^)]*\)\s*\{)",
        re.MULTILINE,
    )

    for pattern in [pattern1, pattern2]:
        for match in pattern.finditer(code):
            start = match.start()
            brace_count = 0
            end = start
            for i in range(start, len(code)):
                if code[i] == "{":
                    brace_count += 1
                elif code[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            func_code = code[start:end]
            lines = func_code.splitlines()
            if 5 <= len(lines) <= 100:
                functions.append(func_code)

    return functions


EXTRACTORS = {
    "python": extract_functions_python,
    "java": extract_functions_java,
    "javascript": extract_functions_js,
}


# ─── Scraping Pipeline ──────────────────────────────────────────────────────

def scrape_language(language: str, target_count: int) -> list:
    """
    Scrape code samples for a single language.

    Returns:
        List of dicts with keys: code, language, quality_label, severity_score, repo_stars
    """
    print(f"\n{'='*60}")
    print(f"Scraping {language.upper()} samples (target: {target_count})")
    print(f"{'='*60}")

    samples = []
    extractor = EXTRACTORS[language]
    extensions = EXTENSIONS[language]

    # Scrape high-quality repos (quality 0-1)
    high_quality_count = target_count // 2
    print(f"\n[Phase 1] Scraping high-quality repos...")
    samples.extend(
        _scrape_repos(
            query=HIGH_QUALITY_QUERY[language],
            language=language,
            extractor=extractor,
            extensions=extensions,
            target=high_quality_count,
            quality_range=(0, 1),
            severity_range=(0.0, 0.3),
        )
    )

    # Scrape low-quality repos (quality 2-3)
    low_quality_count = target_count - len(samples)
    print(f"\n[Phase 2] Scraping low-quality repos...")
    samples.extend(
        _scrape_repos(
            query=LOW_QUALITY_QUERY[language],
            language=language,
            extractor=extractor,
            extensions=extensions,
            target=low_quality_count,
            quality_range=(2, 3),
            severity_range=(0.5, 1.0),
        )
    )

    print(f"\n[DONE] Collected {len(samples)} {language} samples")
    return samples


def _scrape_repos(query: str, language: str, extractor, extensions: list,
                  target: int, quality_range: tuple,
                  severity_range: tuple) -> list:
    """Scrape functions from repos matching the query."""
    samples = []
    page = 1

    while len(samples) < target and page <= 5:
        repos = search_repos(query, per_page=10, page=page)
        if not repos:
            break

        for repo in repos:
            if len(samples) >= target:
                break

            owner = repo["owner"]["login"]
            name = repo["name"]
            stars = repo.get("stargazers_count", 0)
            print(f"  Scanning: {owner}/{name} (⭐ {stars})")

            # Get repo file tree
            contents = get_repo_contents(owner, name)
            source_files = [
                f for f in contents
                if f.get("type") == "file"
                and any(f["name"].endswith(ext) for ext in extensions)
            ]

            # Also check common source directories
            for dir_name in ["src", "lib", "app", "main", "core"]:
                dir_contents = get_repo_contents(owner, name, dir_name)
                source_files.extend([
                    f for f in dir_contents
                    if f.get("type") == "file"
                    and any(f["name"].endswith(ext) for ext in extensions)
                ])

            # Limit files per repo to avoid over-representing one repo
            random.shuffle(source_files)
            source_files = source_files[:5]

            for file_info in source_files:
                if len(samples) >= target:
                    break

                download_url = file_info.get("download_url")
                if not download_url:
                    continue

                content = get_file_content(download_url)
                if not content:
                    continue

                # Extract functions from the file
                functions = extractor(content)
                for func in functions[:3]:  # Max 3 functions per file
                    if len(samples) >= target:
                        break

                    quality = random.randint(*quality_range)
                    severity = round(
                        random.uniform(*severity_range), 2
                    )

                    samples.append({
                        "code": func,
                        "language": language,
                        "quality_label": quality,
                        "severity_score": severity,
                        "repo_stars": stars,
                    })

            # Rate limiting: pause between repos
            time.sleep(1)

        page += 1

    return samples


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("🔥 CodeRoast — GitHub Code Scraper")
    print("=" * 60)

    if not GITHUB_TOKEN:
        print("[WARNING] No GITHUB_TOKEN set. API rate limit will be very low (60 req/hr).")
        print("          Set your token: $env:GITHUB_TOKEN = 'ghp_your_token_here'")
        print("          Or export GITHUB_TOKEN=ghp_your_token_here")
        print()

    all_samples = []
    for lang in LANGUAGES:
        samples = scrape_language(lang, SAMPLES_PER_LANGUAGE)
        all_samples.extend(samples)

    # Save to raw CSV
    os.makedirs(config.DATA_RAW_DIR, exist_ok=True)
    output_path = config.DATA_RAW_DIR / "scraped_code.csv"

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["code", "language", "quality_label",
                           "severity_score", "repo_stars"]
        )
        writer.writeheader()
        writer.writerows(all_samples)

    print(f"\n{'='*60}")
    print(f"✅ Scraped {len(all_samples)} total samples")
    print(f"   Saved to: {output_path}")
    print(f"{'='*60}")
    print(f"\nNext step: run preprocessing:")
    print(f"  python data/preprocess_dataset.py")


if __name__ == "__main__":
    main()
