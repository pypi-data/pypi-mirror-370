import os
import subprocess
import tempfile

from pygit2.repository import Repository

from exponent.core.remote_execution.types import (
    CreateCheckpointRequest,
    CreateCheckpointResponse,
    GitCommitMetadata,
    GitDiff,
    GitFileChange,
    RollbackToCheckpointResponse,
)


async def create_checkpoint(
    request: CreateCheckpointRequest,
) -> CreateCheckpointResponse:
    repo = Repository(".")
    head_commit = str(repo.head.target)
    uncommitted_changes_commit = None
    diff_versus_last_checkpoint = None

    # Get metadata for head commit - fetch each field separately
    author_name = (
        subprocess.run(
            ["git", "log", "--format=%aN", "-1", head_commit],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        or "unknown"
    )

    author_email = (
        subprocess.run(
            ["git", "log", "--format=%aE", "-1", head_commit],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        or "unknown@unknown"
    )

    author_date = subprocess.run(
        ["git", "log", "--format=%ai", "-1", head_commit],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    commit_date = subprocess.run(
        ["git", "log", "--format=%ci", "-1", head_commit],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    commit_message = subprocess.run(
        ["git", "log", "--format=%B", "-1", head_commit],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    # Get current branch
    branch_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    branch = branch_result.stdout.strip()

    head_metadata = GitCommitMetadata(
        author_name=author_name,
        author_email=author_email,
        author_date=author_date,
        commit_date=commit_date,
        branch=branch,
        commit_message=commit_message,
    )

    if repo.status():  # working dir is dirty
        with tempfile.NamedTemporaryFile(prefix="git_index_") as tmp:
            tmp_index_path = tmp.name

            # Set up environment with temporary index
            env = os.environ.copy()
            env["GIT_INDEX_FILE"] = tmp_index_path

            # Initialize temporary index from HEAD
            subprocess.run(["git", "read-tree", head_commit], env=env, check=True)

            # Add all files (including untracked) to temporary index
            subprocess.run(["git", "add", "-A"], env=env, check=True)

            # Write tree object from our temporary index
            result = subprocess.run(
                ["git", "write-tree"],
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            tree_hash = result.stdout.strip()

            if not tree_hash:
                raise ValueError("Failed to create tree object")

            # Create commit object from the tree with HEAD as parent
            result = subprocess.run(
                [
                    "git",
                    "commit-tree",
                    tree_hash,
                    "-p",
                    str(head_commit),
                    "-m",
                    "Checkpoint commit",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            uncommitted_changes_commit = result.stdout.strip()

            if not uncommitted_changes_commit:
                raise ValueError("Failed to create checkpoint commit")

    if request.last_checkpoint_head_commit:
        last_checkpoint_commit = (
            request.last_checkpoint_uncommitted_changes_commit
            or request.last_checkpoint_head_commit
        )
        current_commit = uncommitted_changes_commit or head_commit

        diff_versus_last_checkpoint = _parse_git_diff_tree(
            last_checkpoint_commit,
            current_commit,
        )

    return CreateCheckpointResponse(
        correlation_id=request.correlation_id,
        head_commit_hash=head_commit,
        head_commit_metadata=head_metadata,
        uncommitted_changes_commit_hash=uncommitted_changes_commit,
        diff_versus_last_checkpoint=diff_versus_last_checkpoint,
    )


async def rollback_to_checkpoint(
    correlation_id: str,
    head_commit: str,
    checkpoint_commit: str | None,
) -> RollbackToCheckpointResponse:
    # Clean working directory (including untracked files) before any operations
    subprocess.run(
        ["git", "clean", "-fd"], check=True
    )  # Remove untracked files and directories
    subprocess.run(
        ["git", "reset", "--hard"], check=True
    )  # Remove staged/unstaged changes

    # Now reset HEAD to the original commit state
    subprocess.run(["git", "reset", "--hard", head_commit], check=True)

    if checkpoint_commit:
        # Cherry-pick the checkpoint commit to restore all changes
        subprocess.run(
            ["git", "cherry-pick", "--no-commit", checkpoint_commit], check=True
        )
        subprocess.run(["git", "reset"], check=True)

    return RollbackToCheckpointResponse(
        correlation_id=correlation_id,
    )


def _parse_git_diff_tree(
    from_commit: str, to_commit: str, max_files: int = 50
) -> GitDiff:
    """Parse git diff-tree output into a GitDiff object.

    Args:
        from_commit: Starting commit hash
        to_commit: Ending commit hash
        max_files: Maximum number of files to include in the diff
    """
    result = subprocess.run(
        ["git", "diff-tree", "--numstat", from_commit, to_commit],
        capture_output=True,
        text=True,
        check=True,
    )

    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        added, deleted, path = line.split("\t")
        files.append(
            GitFileChange(path=path, lines_added=int(added), lines_deleted=int(deleted))
        )

    total_files = len(files)
    truncated = total_files > max_files
    if truncated:
        files = files[:max_files]

    return GitDiff(files=files, truncated=truncated, total_files=total_files)
