#!/usr/bin/env python3


"""Test the main command"""

from contextlib import chdir
from os.path import isfile, join
from os import makedirs
from tempfile import TemporaryDirectory

from cxxpm.cxxpm import main

TEST_YAML = """
cache: "%(cache)s"

repositories:
  - "https://file-examples.com/storage/fe796f9a72699f68e92e313/2017/02"
  - "%(repo_path)s"

dependencies:
  - file.zip
  - zip_2MB.zip
"""


def test_main() -> None:
    """test timestamps"""
    with TemporaryDirectory("test_download") as cache_dir, chdir(cache_dir):
        main()

    with TemporaryDirectory("test_download") as cache_dir, chdir(cache_dir):
        repo_path = join(cache_dir, "repo")
        makedirs(repo_path, exist_ok=False)

        with open(join(repo_path, "file.zip"), "w", encoding="utf-8") as dep_file:
            dep_file.write("Not really a zip")

        with open("cxxpm.yml", "w", encoding="utf-8") as settings:
            settings.write(
                TEST_YAML % {"cache": cache_dir, "repo_path": join(cache_dir, "repo")}
            )

        main()
        assert isfile(join(cache_dir, "zip_2MB.zip"))
        assert isfile(join(cache_dir, "file.zip"))
        main()
        assert isfile(join(cache_dir, "zip_2MB.zip"))
        assert isfile(join(cache_dir, "file.zip"))

    with TemporaryDirectory("test_download") as cache_dir, chdir(cache_dir):
        repo_path = join(cache_dir, "repo")
        makedirs(repo_path, exist_ok=False)

        with open("cxxpm.yml", "w", encoding="utf-8") as settings:
            settings.write(
                TEST_YAML % {"cache": cache_dir, "repo_path": join(cache_dir, "repo")}
            )

        main()
        assert isfile(join(cache_dir, "zip_2MB.zip"))
        assert not isfile(join(cache_dir, "file.zip"))


if __name__ == "__main__":
    test_main()
