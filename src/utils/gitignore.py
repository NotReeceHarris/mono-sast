"""Workspace preparation: copy target dir and strip .gitignore'd paths."""

import logging
import os
import shutil
import subprocess

logger = logging.getLogger(__name__)

WORKSPACE = "/tmp/sast_workspace"


def prepare_workspace(source_dir: str) -> str:
    """Copy *source_dir* to a fresh workspace and delete .gitignore'd paths.

    Uses ``git ls-files --others --ignored --exclude-standard`` to resolve
    ignored paths so we don't have to parse .gitignore ourselves.
    Returns the workspace path.
    """
    if os.path.exists(WORKSPACE):
        shutil.rmtree(WORKSPACE)

    logger.info(f"Copying target directory to workspace: {WORKSPACE}")
    shutil.copytree(source_dir, WORKSPACE, symlinks=True)

    result = subprocess.run(
        ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.info("git ls-files failed (not a git repo or no .gitignore) — skipping ignore filter.")
        return WORKSPACE

    ignored = [p for p in result.stdout.split("\0") if p]
    logger.info(f"Removing {len(ignored)} ignored path(s) from workspace.")

    for rel_path in ignored:
        full_path = os.path.join(WORKSPACE, rel_path)
        if os.path.isfile(full_path) or os.path.islink(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)

    return WORKSPACE
