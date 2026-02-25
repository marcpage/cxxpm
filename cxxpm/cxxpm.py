#!/usr/bin/env python3


"""manage dependencies"""

from os.path import join, isfile
from os import makedirs
from shutil import copyfile
from tempfile import gettempdir

from yaml import safe_load
from requests import get, HTTPError
from requests.exceptions import MissingSchema


def load_yaml(path: str) -> dict:
    """Loads a yaml file

    Args:
        path (str): The path to the yaml file

    Returns:
        dict[str, dict]: The data loaded from the yaml file
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            return safe_load(file)

    except FileNotFoundError:
        return {}


def download_file(base_url: str, filename: str, save_dir: str) -> None:
    """
    Downloads a file from base_url + filename and saves it to save_dir/filename

    Returns the full path of the saved file
    """
    full_url = base_url.rstrip("/") + "/" + filename.lstrip("/")
    local_path = join(save_dir, filename)

    with get(full_url, stream=True, timeout=30) as response:
        response.raise_for_status()  # raise exception for 4xx/5xx errors
        print(f"Downloading: {full_url}")

        with open(local_path, "wb") as f:
            downloaded = 0

            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)

    print(f"      Saved: {local_path}")


def fill_cache(dependency: str, cache_dir: str, repos: list[str]) -> bool:
    """Ensures the archive is in the cache, returns False if it cannot be found"""
    target = join(cache_dir, dependency)

    if isfile(target):
        return True

    for repo in repos:
        local_file = join(repo, dependency)

        if isfile(local_file):
            copyfile(local_file, target)
            return True

        try:
            download_file(repo, dependency, cache_dir)
            return True

        except HTTPError as error:
            print(f"⚠️⚠️⚠️ Unable to download {dependency} from {repo}: {error}")
            continue

        except MissingSchema:
            print(f"⚠️⚠️⚠️ Missing local repo path: {repo}")
            continue

    return False


def main() -> None:
    """Main command"""
    settings = load_yaml("cxxpm.yml")
    default_cache_dir = join(gettempdir(), "cxxpm")
    makedirs(default_cache_dir, exist_ok=True)
    cache_dir = settings.get("cache", default_cache_dir)
    repos = settings.get("repositories", [])
    dependencies = settings.get("dependencies", [])
    expand_dir = settings.get("location", "build/cxxpm/dependencies")
    makedirs(expand_dir, exist_ok=True)
    success = True

    for dependency in dependencies:
        succeeded = fill_cache(dependency, cache_dir, repos)
        success = success and succeeded

        if not succeeded:
            print(f"❌❌❌ failed to find: {dependency}")

    if not success:
        print("❌❌❌ Dependency fetch failed ❌❌❌")


if __name__ == "__main__":
    main()
