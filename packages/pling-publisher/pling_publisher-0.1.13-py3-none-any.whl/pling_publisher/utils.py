import os
import zipfile
from typing import Optional

import requests
import typer

import re
import sys
import base64
from urllib import parse
from pprint import pprint


def create_zip_file(file_path, target_dir):
    directories_to_ignore = [
        ".git",
        ".github",
        "dist",
        ".gitignore",
        "Makefile",
        "setup.py",
    ]
    zipobj = zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1

    for base, dirs, files in os.walk(target_dir):
        if any(ignore_directory in base for ignore_directory in directories_to_ignore):
            continue

        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])


def upload(
    username: Optional[str], password: Optional[str], project_id: str, zipfile: str
):
    authority = "www.pling.com"
    baseUrl = "https://" + authority + "/"
    the_file = base64.b64encode(open(zipfile, "rb").read())

    headers = {
        "authority": authority,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "dnt": "1",
        "pragma": "no-cache",
        "referer": baseUrl,
        "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    login_data = {
        "csrf": "",
        "email": username,
        "password": password,
        "next": "/",
        "remember_me": "1",
    }

    client = requests.Session()
    client.get(baseUrl, headers=headers)
    login_page = client.get(baseUrl + "login/", headers=headers)
    result = re.search(
        r"name=\"csrf\" value=\"(.*?)\"", login_page.content.decode("UTF-8")
    )
    login_data["csrf"] = result.group(1)

    headers["referer"] = baseUrl + "login/"
    login_response = client.post(baseUrl + "login/", login_data, headers=headers)

    if b"Incorrect login and/or password" in login_response.content:
        typer.echo("failed login")
        sys.exit(1)

    edit_page = client.get(baseUrl + "p/" + project_id + "/edit", headers=headers)
    result = re.search(r"var fileUri = '(.*?)'", edit_page.content.decode("UTF-8"))
    upload_url = result.group(1)
    result = re.search(r"\"owner_id\", '(.*?)'", edit_page.content.decode("UTF-8"))
    owner_id = result.group(1)
    result = re.search(r"client_id = '(.*?)'", edit_page.content.decode("UTF-8"))
    client_id = result.group(1)
    result = re.search(
        r"data-ppload-collection-id=\"(.*?)\"", edit_page.content.decode("UTF-8")
    )
    collection_id = result.group(1)

    headers["acccept"] = "application/json, text/javascript, */*; q=0.01"
    headers["origin"] = baseUrl
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-site"
    del headers["sec-fetch-user"]
    del headers["upgrade-insecure-requests"]

    params = dict(parse.parse_qsl(parse.urlsplit(upload_url).query))

    post_data = {
        "collection_id": collection_id,
        "id": "1676575635",
        "owner_id": owner_id,
        "format": "json",
        "client_id": client_id,
        "name": "file",
        "filename": "archive.tgz",
    }

    files = {"file": (zipfile, the_file, "application/zip")}
    response = client.post(
        upload_url, params=params, headers=headers, data=post_data, files=files
    )

    if '"status":"success"' in response.content.decode("UTF-8"):
        return True
    else:
        typer.echo("Failed publishing: " + zipfile)
        typer.echo("\n")
        typer.echo(response.content.decode("UTF-8"))
        return False
