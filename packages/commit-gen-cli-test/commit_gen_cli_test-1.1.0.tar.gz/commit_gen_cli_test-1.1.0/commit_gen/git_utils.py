"""
Git utilities for Commit-Gen.
"""

import subprocess
import sys
from typing import List, Dict, Optional


def run_command(command: str, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(command, shell=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        sys.exit(1)


def get_git_changes() -> str:
    """Get staged changes for commit message generation."""
    result = run_command("git diff --cached --name-status", capture_output=True)
    return result.stdout.strip()


def get_git_diff() -> str:
    """Get the diff content for commit message generation."""
    result = run_command("git diff --cached", capture_output=True)
    return result.stdout.strip()


def stage_all_changes() -> None:
    """Stage all changes in the repository."""
    run_command("git add .")


def create_git_commit(message: str) -> None:
    """Create a git commit with the given message."""
    run_command(f'git commit -m "{message}"')


def push_to_origin() -> None:
    """Push changes to the origin remote."""
    try:
        # Get current branch name
        current_branch = get_current_branch()
        # Push to origin with specific branch
        run_command(f"git push origin {current_branch}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Push failed: {e}")
        # Fallback to simple git push if branch-specific push fails
        try:
            run_command("git push")
        except subprocess.CalledProcessError as e2:
            print(f"❌ Fallback push also failed: {e2}")
            raise


def get_current_branch() -> str:
    """Get the current git branch name."""
    result = run_command("git rev-parse --abbrev-ref HEAD", capture_output=True)
    return result.stdout.strip()


def get_last_branch_commit(branch: str) -> str:
    """Get the last commit hash of a branch."""
    result = run_command(f"git rev-parse {branch}", capture_output=True)
    return result.stdout.strip()


def get_diff_between_branches(base_commit: str, current_branch: str) -> str:
    """Get diff between two branches."""
    result = run_command(f"git diff {base_commit}..{current_branch}", capture_output=True)
    return result.stdout.strip()


def get_commits_between(base_commit: str, current_branch: str) -> str:
    """Get commits between two branches."""
    result = run_command(f"git log {base_commit}..{current_branch} --pretty=format:'%H|%an|%s'", capture_output=True)
    return result.stdout.strip()


def get_repo_url() -> Optional[str]:
    """Get the repository URL."""
    try:
        result = run_command("git config --get remote.origin.url", capture_output=True)
        url = result.stdout.strip()
        # Convert SSH URL to HTTPS if needed
        if url.startswith("git@"):
            url = url.replace("git@", "https://").replace(":", "/")
        return url
    except subprocess.CalledProcessError:
        return None


def get_commit_time(commit_hash: str) -> str:
    """Get the commit time in a readable format."""
    result = run_command(f"git show -s --format=%ci {commit_hash}", capture_output=True)
    return result.stdout.strip()


def resolve_file_path(filename: str) -> str:
    """Resolve file path, handling symlinks and ensuring correct path."""
    import os

    # Try to resolve symlinks and get real path
    try:
        real_path = os.path.realpath(filename)
        # If the real path is different and exists, use the real path
        if real_path != filename and os.path.exists(real_path):
            # Check if the real path is within the current directory
            current_dir = os.getcwd()
            if real_path.startswith(current_dir):
                # Return relative path from current directory
                return os.path.relpath(real_path, current_dir)
            else:
                # If real path is outside current directory, check if it's accessible
                if os.path.exists(real_path):
                    return real_path
    except (OSError, ValueError):
        pass

    # If symlink resolution fails, check if the original path exists
    if os.path.exists(filename):
        return filename

    # If neither exists, return the original filename
    return filename


def get_modified_files() -> List[Dict[str, str]]:
    """Get list of modified and untracked files with their status."""
    files = []

    # Get modified files
    try:
        result = run_command("git status --porcelain", capture_output=True)
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                status = line[:2].strip()
                filename = line[2:].lstrip()

                # Resolve file path to handle symlinks
                resolved_filename = resolve_file_path(filename)

                # Check if file exists (only for untracked files, deleted files are expected to not exist)
                if status == '??':
                    import os
                    if not os.path.exists(resolved_filename):
                        continue

                # Parse status (handle combined XY codes from porcelain)
                if status == '??':
                    file_status = "untracked"
                elif 'D' in status:
                    file_status = "deleted"
                elif 'M' in status:
                    file_status = "modified"
                elif 'A' in status:
                    file_status = "added"
                elif 'R' in status:
                    file_status = "renamed"
                elif 'C' in status:
                    file_status = "copied"
                elif 'U' in status:
                    file_status = "unmerged"
                else:
                    file_status = "unknown"

                files.append({
                    "filename": resolved_filename,
                    "status": file_status,
                    "full_status": status
                })
    except subprocess.CalledProcessError:
        pass

    return files


def get_file_info(filename: str) -> Dict[str, str]:
    """Get detailed information about a file."""
    from pathlib import Path

    file_path = Path(filename)
    info = {
        "filename": filename,
        "exists": file_path.exists(),
        "size": "0B",
        "last_modified": "unknown"
    }

    if file_path.exists():
        # Get file size
        size_bytes = file_path.stat().st_size
        if size_bytes < 1024:
            info["size"] = f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            info["size"] = f"{size_bytes // 1024}KB"
        else:
            info["size"] = f"{size_bytes // (1024 * 1024)}MB"

        # Get last modified time
        mtime = file_path.stat().st_mtime
        from datetime import datetime
        info["last_modified"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    else:
        # For deleted files, try to get info from git
        try:
            result = run_command(f"git log -1 --format=%ci -- \"{filename}\"", capture_output=True)
            if result.stdout.strip():
                info["last_modified"] = "deleted"
                info["size"] = "deleted"
        except subprocess.CalledProcessError:
            pass

    return info


def stage_specific_files(filenames: List[str]) -> None:
    """Stage specific files including deleted files reliably.

    - Existing files are staged with `git add`.
    - Deleted files are staged with `git add -u -- <path>` to record removals.
    """
    if not filenames:
        return

    # Get current git status to identify deleted files
    git_status = {}
    try:
        result = run_command("git status --porcelain", capture_output=True)
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                status = line[:2].strip()
                filename = line[2:].lstrip()
                git_status[filename] = status
    except subprocess.CalledProcessError:
        pass

    # Separate files based on existence and git status
    existing_files: List[str] = []
    deleted_files: List[str] = []
    missing_files: List[str] = []

    for filename in filenames:
        import os
        resolved_filename = resolve_file_path(filename)

        # Determine deletion state from porcelain (handles ' D' or 'D ' → 'D')
        is_deleted = git_status.get(filename) == 'D' or git_status.get(resolved_filename) == 'D'

        if is_deleted:
            # Use the original filename for better matching with porcelain output
            deleted_files.append(filename)
            continue

        if os.path.exists(resolved_filename):
            existing_files.append(resolved_filename)
        else:
            missing_files.append(filename)

    # Show warnings for missing files (not tracked as deleted)
    if missing_files:
        print(f"⚠️  Warning: The following files don't exist and are not tracked as deleted:")
        for file in missing_files:
            print(f"   - {file}")

    # Stage existing files
    if existing_files:
        files_str = " ".join(f'"{f}"' for f in existing_files)
        run_command(f"git add {files_str}")

    # Stage deleted files using git rm --cached --ignore-unmatch
    # If the exact path no longer matches, stage from the nearest existing ancestor directory
    for deleted_file in deleted_files:
        try:
            # Ignore unmatched to avoid hard failure when pathspec no longer matches
            run_command(f"git rm -r --cached --ignore-unmatch -- \"{deleted_file}\"")
        except subprocess.CalledProcessError:
            import os
            # Find nearest existing ancestor directory
            ancestor = deleted_file
            while ancestor and not os.path.isdir(ancestor):
                new_ancestor = os.path.dirname(ancestor)
                if new_ancestor == ancestor:
                    break
                ancestor = new_ancestor
            if not ancestor:
                ancestor = '.'
            if ancestor and not os.path.isdir(ancestor):
                ancestor = '.'
            # Stage updates (including deletions) from ancestor directory
            run_command(f"git add -u -- \"{ancestor}\"")

    total_staged = len(existing_files) + len(deleted_files)
    if total_staged:
        print(f"✅ Successfully staged {total_staged} files ({len(existing_files)} added/modified, {len(deleted_files)} deleted)")
    else:
        print("❌ No valid files to stage")


def get_staged_files() -> List[str]:
    """Get list of currently staged files."""
    try:
        result = run_command("git diff --cached --name-only", capture_output=True)
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []


def clear_staging_area() -> None:
    """Clear the git staging area."""
    run_command("git reset")


def is_git_repository() -> bool:
    """Check if current directory is a git repository."""
    try:
        run_command("git rev-parse --git-dir", capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_file_category(filename: str) -> str:
    """Categorize file based on extension and path."""
    filename_lower = filename.lower()

    # Code files
    if any(filename_lower.endswith(ext) for ext in
           ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']):
        return "code"

    # Config files
    if any(filename_lower.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']):
        return "config"

    # Documentation
    if any(filename_lower.endswith(ext) for ext in ['.md', '.txt', '.rst', '.adoc']):
        return "docs"

    # Tests
    if 'test' in filename_lower or 'spec' in filename_lower:
        return "tests"

    # Assets
    if any(filename_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']):
        return "assets"

    # Build/Dependencies
    if any(filename_lower.endswith(ext) for ext in ['.lock', '.log', '.tmp', '.cache']):
        return "build"

    return "other"
