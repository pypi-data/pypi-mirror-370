# -*- coding: utf-8 -*-

from pathlib import Path
from tuxsuite.requests import get
from tuxsuite.cli.requests import headers, get_storage

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def download(build, output):
    output = Path(output)
    output.mkdir(exist_ok=True)
    build_dir = output / build.uid
    build_dir.mkdir(exist_ok=True)
    url = build.status["download_url"] + "?export=json"
    # for private builds
    headers = {"Authorization": build.headers["Authorization"]}
    files = get(url, headers=headers).json()
    # TODO parallelize?
    for f in files["files"]:
        url = f["Url"]
        dest = build_dir / Path(url).name
        download_file(url, dest, headers)


def progress_bar(completed, total, length=40):
    fraction = completed / total
    pattern = int(fraction * length) * "="
    padding = int(length - len(pattern)) * "-"
    end = "\r" if completed < total else "\n"
    sys.stdout.write(
        f"Progress: [{pattern}{padding}] {int(fraction*100)}% ({completed}/{total} files){end}"
    )
    sys.stdout.flush()


def download_artifacts(config, build, output, url_path=True, files={}):
    print("* Downloading artifacts, Please wait...")
    output = Path(output)
    output.mkdir(exist_ok=True)
    build_dir = output / build.uid
    build_dir.mkdir(exist_ok=True)
    if not files:
        url = (
            f"{build.download_url}{url_path}/"
            if url_path is not True
            else build.download_url
        ) + "?export=json"

        files = get_storage(config, url).json()
    total_files = len(files.get("files", []))
    completed_files = 0

    with ThreadPoolExecutor() as executor:
        futures = []
        for f in files.get("files", []):
            url = f["Url"]
            dest = build_dir / Path(url).name
            futures.append(executor.submit(download_file, url, dest, headers(config)))

        for future in as_completed(futures):
            future.result()
            completed_files += 1
            progress_bar(completed_files, total_files)


def download_file(url, dest, headers=""):
    r = get(url, stream=True, headers=headers)
    with dest.open("wb") as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
