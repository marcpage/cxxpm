#!/usr/bin/env python3


"""Ensure code coverage ratchets up

README.md is source of truth for minimum coverage
cxxpm/__init__.py is source of truth for version

"""

from sys import argv, exit as return_code
from re import compile as regex, MULTILINE

from cxxpm import __version__ as cxxpm_version

EXPECTED_COVERAGE = regex(r"label=test\+coverage&message=([0-9]+)%&")
COVERAGE = regex(r"^TOTAL\s+[0-9]+\s+[0-9]+\s+([0-9]+)%", MULTILINE)
VERSION = regex(
    r"label=released&message=v([0-9.]+)&.*https://pypi.org/project/cxxpm/([0-9.]+)/"
)


def load(path: str) -> str:
    """loads a file"""
    with open(path, "r", encoding="utf-8") as the_file:
        return the_file.read()


def patch_coverage(path: str | None, readme_contents: str) -> str:
    """reads coverage file and updates readme contents"""
    if not path:
        return readme_contents

    existing_coverage = EXPECTED_COVERAGE.search(readme_contents)
    assert existing_coverage, readme_contents
    minimum_coverage = int(existing_coverage.group(1))
    report_contents = load(path)
    actual_coverage = COVERAGE.search(report_contents)
    assert actual_coverage, report_contents
    coverage = int(actual_coverage.group(1))

    if coverage < minimum_coverage:
        print(f"❌❌❌ Coverage: {coverage}% (below {minimum_coverage}%) ❌❌❌")
        return_code(1)

    search_pattern = existing_coverage.group(0)
    replace_pattern = search_pattern.replace(str(minimum_coverage), str(coverage))
    return readme_contents.replace(search_pattern, replace_pattern)


def patch_version(readme_contents: str) -> str:
    """updates the version from cxxpm module"""
    readme_version = VERSION.search(readme_contents)
    assert readme_version, readme_contents
    assert readme_version.group(1) == readme_version.group(2), (
        readme_version.group(1),
        readme_version.group(2),
    )

    search_pattern = readme_version.group(0)
    replace_pattern = search_pattern.replace(readme_version.group(1), cxxpm_version)
    return readme_contents.replace(search_pattern, replace_pattern)


def main() -> None:
    """Checks code coverage"""
    report_path = argv[2] if len(argv) > 1 else None
    readme_path = argv[1]
    readme_contents = load(readme_path)
    new_readme_contents = patch_version(patch_coverage(report_path, readme_contents))

    if new_readme_contents == readme_contents:
        return  # no need to write it if it hasn't changed

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(new_readme_contents)


if __name__ == "__main__":
    main()
