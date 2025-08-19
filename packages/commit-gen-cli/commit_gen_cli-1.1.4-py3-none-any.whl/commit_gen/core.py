"""
Core functionality for Commit-Gen.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Optional

from .config import (
    get_provider,
    get_api_key,
    get_model,
    get_default_model_for_provider,
)
from .git_utils import (
    run_command,
    get_git_changes,
    get_git_diff,
    create_git_commit,
    push_to_origin,
    get_current_branch,
    get_last_branch_commit,
    get_diff_between_branches,
    get_commits_between,
    get_repo_url,
    get_commit_time,
)
from .providers import generate_commit_message

# Debug mode flag
DEBUG = False


def debug_log(message: str, content: Optional[str] = None) -> None:
    """Log debug messages if debug mode is enabled."""
    if DEBUG:
        print(f"DEBUG: {message}")
        if content:
            print("DEBUG: Content >>>")
            print(content)
            print("DEBUG: <<<")


def check_ollama() -> None:
    """Check if Ollama is running and the model exists."""
    # Check if Ollama is running
    if not shutil.which("ollama"):
        print("Error: Ollama not found. Please install Ollama first.")
        sys.exit(1)

    # Check if ollama serve is running
    result = run_command("pgrep ollama", capture_output=True)
    if result.returncode != 0:
        print("Error: Ollama server not running. Please start Ollama first:")
        print("ollama serve")
        sys.exit(1)

    # Get the model
    model = get_model() or get_default_model_for_provider("ollama")

    # Check if model exists using ollama ls
    result = run_command("ollama ls")
    if result.returncode != 0:
        print("Error running 'ollama ls'. Make sure Ollama is installed correctly.")
        sys.exit(1)

    models = [line.split()[0] for line in result.stdout.splitlines() if line.strip()]
    if model not in models:
        print(f"Error: Model '{model}' not found in Ollama. Please pull it first:")
        print(f"ollama pull {model}")
        sys.exit(1)


def format_commit_data(commits_raw: str, repo_url: Optional[str]) -> str:
    """Format commit data into a structured format for the AI prompt."""
    if not commits_raw.strip() or not repo_url:
        return "No commits found or repository URL not available."

    commits = []
    commit_links = {}
    author_commits = {}

    for line in commits_raw.strip().split('\n'):
        if not line.strip():
            continue

        parts = line.split('|', 2)
        if len(parts) < 3:
            continue

        commit_hash, author, message = parts
        # Determine if it's GitLab or GitHub to format the URL correctly
        if "gitlab" in repo_url:
            commit_url = f"{repo_url}/-/commit/{commit_hash}"
        else:  # GitHub and others
            commit_url = f"{repo_url}/commit/{commit_hash}"

        # Store commit data for formatted output
        commits.append({
            "hash": commit_hash,
            "author": author,
            "message": message,
            "url": commit_url
        })

        # Store commit links for easy reference
        commit_links[commit_hash] = commit_url

        # Group commits by author
        if author not in author_commits:
            author_commits[author] = []
        author_commits[author].append(commit_hash)

    # Check if we have any commits
    if not commits:
        return "No commits found or repository URL not available."

    # Format commits for display
    formatted_commits = "\n".join([f"{c['hash']} - {c['author']}: {c['message']}" for c in commits])

    # Create a JSON structure with all the data
    commit_data = {
        "formatted_commits": formatted_commits,
        "commit_links": commit_links,
        "author_commits": author_commits,
        "commits": commits
    }

    return json.dumps(commit_data)


def generate_changelog_between_tags(from_tag: str, to_tag: str, changelog_filename: str = "CHANGELOG.md") -> None:
    """Generate a changelog between two specific tags."""
    import os
    cwd = Path(os.getcwd())
    changelog_file = cwd / changelog_filename
    
    # Verify tags exist
    from_tag_result = run_command(f"git tag -l {from_tag}", capture_output=True)
    to_tag_result = run_command(f"git tag -l {to_tag}", capture_output=True)
    
    if not from_tag_result.stdout.strip():
        print(f"❌ Tag '{from_tag}' not found")
        sys.exit(1)
    if not to_tag_result.stdout.strip():
        print(f"❌ Tag '{to_tag}' not found")
        sys.exit(1)

    # Get commit information between tags
    commits_raw = get_commits_between(from_tag, to_tag)
    if not commits_raw.strip():
        print(f"❌ No commits found between tags {from_tag} and {to_tag}")
        sys.exit(1)

    # Get diff content between tags
    diff_content = get_diff_between_branches(from_tag, to_tag)
    if "No changes detected" in diff_content:
        commit_count = len(commits_raw.strip().split('\n'))
        print(f"⚠️  No file changes detected between tags {from_tag} and {to_tag}, but found {commit_count} commits.")

    # Get repository URL for creating commit links
    repo_url = get_repo_url()
    if not repo_url:
        print("⚠️  Could not determine repository URL. Commit links may not work correctly.")
        repo_url = "https://example.com/repo"  # Fallback URL

    # Format commit data with detailed information
    commit_data = format_commit_data(commits_raw, repo_url)
    if "No commits found" in commit_data:
        print(f"❌ Could not format commit data properly.")
        sys.exit(1)

    # Escape { and } to avoid format errors in diff_content only
    diff_content = diff_content.replace("{", "{{").replace("}", "}}")

    # Get commit times for tags
    from_tag_time = get_commit_time(run_command(f"git rev-list -n 1 {from_tag}").stdout.strip())
    to_tag_time = get_commit_time(run_command(f"git rev-list -n 1 {to_tag}").stdout.strip())

    # Changelog prompt template for tags
    CHGLOG_PROMPT_TEMPLATE = """
    Write a concise changelog of code changes in Markdown format for changes between tags `{from_tag}` and `{to_tag}`.

    Commits (JSON format with commit details):
    {commit_list}

    Diff:
    {diff_content}

    Requirements:
    - Write in Vietnamese
    - Follow this structure exactly:

    # Changelog

    ## {to_tag} - {from_tag} ({to_tag_time} - {from_tag_time})

    ### Added or Changed
    - [Summarize what changed in business logic or code, first line is breaking changes if exists] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Removed
    - [Summarize anything that was removed, if any] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Fixed
    - [Summarize any bug fixes or error corrections] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Under the hood
    - [Summarize any internal changes] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Dependencies
    - [List dependency updates] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Contributors
    - @[username](https://gitlab.mobio.vn/username) ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    Guidelines:
    - The commit_list is a JSON object containing:
      - formatted_commits: A text list of all commits
      - commit_links: A dictionary mapping commit hashes to their URLs
      - author_commits: A dictionary mapping authors to their commits
      - commits: An array of detailed commit objects
    - Use the commit_links to create proper hyperlinks
    - Only include sections that have actual changes
    - Skip empty sections entirely
    - Group related commits logically
    - Extract commit hashes from the commit data and link them properly
    - Use Vietnamese language for all descriptions
    """

    prompt = CHGLOG_PROMPT_TEMPLATE.format(
        from_tag=from_tag,
        to_tag=to_tag,
        from_tag_time=from_tag_time,
        to_tag_time=to_tag_time,
        commit_list=commit_data,
        diff_content=diff_content
    )

    provider = get_provider()
    api_key = get_api_key()
    model = get_model() or get_default_model_for_provider(provider)

    print(f"🤖 Generating changelog between tags {from_tag} and {to_tag}...")
    changelog = generate_commit_message(provider, api_key, model, None, prompt)
    
    if not changelog:
        print("❌ Failed to generate changelog.")
        sys.exit(1)

    # Write changelog to file
    with open(changelog_file, 'w', encoding='utf-8') as f:
        f.write(changelog)

    print(f"✅ Changelog generated and saved to {changelog_file}")


def generate_changelog_by_commit_sha(compare_branch: str = "master", changelog_filename: str = "CHANGELOG.md") -> None:
    """Generate a changelog between two branches."""
    import os
    cwd = Path(os.getcwd())
    changelog_file = cwd / changelog_filename
    branch = get_current_branch()
    base_commit = get_last_branch_commit(compare_branch)

    # Check if branches are the same
    if branch == compare_branch:
        print(f"Warning: Current branch '{branch}' is the same as compare branch. This may result in empty changelog.")

    # Get commit information
    commits_raw = get_commits_between(base_commit, branch)
    if not commits_raw.strip():
        print(f"Error: No commits found between {compare_branch} and {branch}.")
        sys.exit(1)

    # Get diff content with improved handling
    diff_content = get_diff_between_branches(base_commit, branch)
    if "No changes detected" in diff_content:
        # Count the number of commits by counting newlines plus 1
        commit_count = len(commits_raw.strip().split('\n'))
        print(
            f"Warning: No file changes detected between {compare_branch} and {branch}, but found {commit_count} commits.")

    # Get repository URL for creating commit links
    repo_url = get_repo_url()
    if not repo_url:
        print("Warning: Could not determine repository URL. Commit links may not work correctly.")
        repo_url = "https://example.com/repo"  # Fallback URL

    # Format commit data with detailed information
    commit_data = format_commit_data(commits_raw, repo_url)
    if "No commits found" in commit_data:
        print(f"Error: Could not format commit data properly.")
        sys.exit(1)

    # Escape { and } to avoid format errors in diff_content only
    # We don't escape commit_data because it's already properly formatted JSON
    diff_content = diff_content.replace("{", "{{").replace("}", "}}")

    # Get commit times
    branch_time = get_commit_time(run_command(f"git rev-parse {branch}").stdout.strip())
    compare_branch_time = get_commit_time(run_command(f"git rev-parse {compare_branch}").stdout.strip())

    # Changelog prompt template
    CHGLOG_PROMPT_TEMPLATE = """
    Write a concise changelog of code changes in Markdown format for changes between the `{compare_branch}` and `{branch}` branches.

    Commits (JSON format with commit details):
    {commit_list}

    Diff:
    {diff_content}

    Requirements:
    - Write in Vietnamese
    - Follow this structure exactly:

    # Changelog

    ## {branch} - {compare_branch} ({branch_time} - {compare_branch_time})

    ### Added or Changed
    - [Summarize what changed in business logic or code, first line is breaking changes if exists] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Removed
    - [Summarize anything that was removed, if any] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Fixed
    - [Summarize any bug fixes or error corrections] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Under the hood
    - [Summarize any internal changes] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Dependencies
    - [List dependency updates] ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    ### Contributors
    - @[username](https://gitlab.mobio.vn/username) ([#commit_hash](commit_url), [#commit_hash](commit_url)...)

    Guidelines:
    - The commit_list is a JSON object containing:
      - formatted_commits: A text list of all commits
      - commit_links: A dictionary mapping commit hashes to their URLs
      - author_commits: A dictionary mapping authors to their commit hashes
      - commits: A list of commit objects with hash, author, message, and URL
    - Each changelog entry MUST end with relevant commit links in the format [#hash](url)
    - For multiple commits related to one change, separate the commit links with commas
    - Group related changes under one list item if appropriate
    - Only describe what changed in the **code** and the **business logic**
    - Use `-` for each bullet point
    - Include commit links at the end of each changelog line
    - For Contributors section, list each contributor with their relevant commits
    - No explanation outside the `.md` content
    - Must render cleanly on GitHub and GitLab
    - Dont use "```md" or "```markdown" at the start and end of the output.

    Output only the `.md` file content — no extra comments or metadata.
    """

    # Create the prompt with all the data
    prompt = CHGLOG_PROMPT_TEMPLATE.format(
        branch=branch,
        compare_branch=compare_branch,
        commit_list=commit_data,
        diff_content=diff_content,
        branch_time=branch_time,
        compare_branch_time=compare_branch_time
    )

    print("\nPrompt gửi cho AI:\n", prompt)

    # Generate the changelog using the appropriate AI provider
    provider = get_provider()
    api_key = get_api_key()
    model = get_model()

    print(f"\nGenerating changelog using {provider} with model {model}...")
    changelog_entry = generate_commit_message(provider, api_key, model, commit_data, diff_content, prompt)

    # Write the changelog to file
    if changelog_file.exists():
        with open(changelog_file, "a") as f:
            f.write("\n\n" + changelog_entry)  # Add extra newlines for separation
        print(f"Đã cập nhật {changelog_filename} với nội dung mới tại {cwd}.")
    else:
        with open(changelog_file, "w") as f:
            f.write(changelog_entry)
        print(f"Đã tạo {changelog_filename} với nội dung đầu tiên tại {cwd}.")

    print(f"\nChangelog generation complete. File saved to {changelog_file}")


def process_commit_generation(
        provider: str,
        api_key: str,
        model: str,
        custom_prompt: Optional[str] = None,
        push_changes: bool = False,
) -> None:
    """Process commit message generation and commit creation."""
    # Note: Files should already be staged by CLI before calling this function
    # We don't auto-stage files here anymore

    # Get git changes
    changes = get_git_changes()
    diff_content = get_git_diff()

    debug_log("Git changes detected", changes)

    if not changes:
        print("No staged changes found. Please stage your changes first.")
        print("💡 Use one of these options:")
        print("   commit-gen                    # Interactive file selection")
        print("   commit-gen --all             # Stage all files")
        print("   commit-gen --files file1 file2  # Stage specific files")
        sys.exit(1)

    # Generate commit message
    commit_message = generate_commit_message(
        provider, api_key, model, changes, diff_content, custom_prompt
    )

    # Create git commit
    create_git_commit(commit_message)

    # Push to origin if flag is set
    if push_changes:
        push_to_origin()

    print("Successfully committed changes with message:")
    print(commit_message)
    debug_log("Script completed successfully")
