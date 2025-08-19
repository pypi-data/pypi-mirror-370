"""
IP Audio is a website that hosts audio for goldenaudiobooks.club, sharedaudiobooks.net,hdaudiobooks.net
"""

import os
from os import mkdir, path
from urllib import parse

import requests
from bs4 import BeautifulSoup
# from pypdl import Pypdl
from requests import get
from rich import print

website_lists = [
    "goldenaudiobook",  # https://goldenaudiobooks.club/
    "sharedaudiobooks",  # https://sharedaudiobooks.net/
    "hdaudiobooks",  # https://hdaudiobooks.ne
    "findaudiobook",  # https://findaudiobook.club/
    "bagofaudio",  # https://bagofaudio.com/
    "bigaudiobooks",  # https://bigaudiobooks.club/
    "fulllengthaudiobooks",  # https://fulllengthaudiobooks.net/
    "primeaudiobooks",  # https://primeaudiobooks.club/
]


def gererate_list(url: str):
    response = get(url)
    soup = BeautifulSoup(response.text, "lxml")

    title = soup.head.title.text.strip()
    audios = soup.find_all("audio", class_="wp-audio-shortcode")
    audios = list(map(lambda audio: audio.source.get("src"), audios))

    return {"title": title, "audios": audios}


# def download_now(title, audios, basepath):
#     print(f"Downloading [bold]{title}[/bold]")
#     dl = Pypdl(allow_reuse=True)
#     for audio in audios:
#         bookpath = path.join(basepath, parse.unquote(audio.split("/")[-2]))
#         print(f"\tFile: {bookpath}/{audio.split('/')[-1].split('?')[0]}")
#         if not path.exists(bookpath):
#             mkdir(bookpath)

#         dl.start(url=audio, file_path=bookpath, overwrite=False)

#     dl.shutdown()
#     print("Completed")


def download_now(title, audios, basepath):
    print(f"Downloading [bold]{title}[/bold]")

    for audio in audios:
        bookpath = os.path.join(basepath, parse.unquote(audio.split("/")[-2]))
        filename = audio.split("/")[-1].split("?")[0]
        filepath = os.path.join(bookpath, filename)

        print(f"\tFile: {filepath}")

        if not os.path.exists(bookpath):
            os.makedirs(bookpath, exist_ok=True)

        if os.path.exists(filepath):
            print("\t\tAlready exists, skipping...")
            continue

        try:
            with requests.get(audio, stream=True) as r:
                r.raise_for_status()
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
        except Exception as e:
            print(f"\t\tError downloading {filename}: {e}")

    print("Completed")
