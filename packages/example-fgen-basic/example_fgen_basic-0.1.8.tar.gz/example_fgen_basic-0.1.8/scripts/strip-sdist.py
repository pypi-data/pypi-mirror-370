"""
Script file to strip unwanted files from dist tarball
"""

import os
import shutil
from pathlib import Path


def main():
    """
    Strip the files we don't want in the tarball
    """
    dist_root = os.environ.get("MESON_DIST_ROOT")

    # Files/Folders to strip from the *.tar.gz
    exclude = [
        ".github",
        "docs",
        "tests",
        "changelog",
        "stubs",
        Path("scripts") / "add-locked-targets-to-pyproject-toml.py",
        Path("scripts") / "inject-srcs-into-meson-build.py",
        Path("scripts") / "propogate-pyproject-metadata.py",
        Path("scripts") / "test-install.py",
        Path("scripts") / "changelog-to-release-template.py",
        Path("scripts") / "print-conda-recipe-pins.py",
        # Keep this one
        # Path("scripts") / "strip-sdist.py",
        ".pre-commit-config.yaml",
        ".gitignore",
        ".readthedocs.yaml",
        "Makefile",
        "environment-docs-conda-base.yml",
        "mkdocs.yml",
        "uv.lock",
        "requirements-docs-locked.txt",
        "requirements-incl-optional-locked.txt",
        "requirements-locked.txt",
        "requirements-only-tests-locked.txt",
        "requirements-only-tests-min-locked.txt",
        "requirements-upstream-dev.txt",
        ".copier-answers.yml",
        ".fprettify.rc",
    ]

    # Strip
    for path in exclude:
        abs_path = os.path.join(dist_root, path)
        if not os.path.exists(abs_path):
            msg = f"File not found: {abs_path}"
            raise FileNotFoundError(msg)

        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)

        elif os.path.isfile(abs_path):
            os.remove(abs_path)


if __name__ == "__main__":
    main()
