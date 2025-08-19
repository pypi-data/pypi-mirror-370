"""
IP Audio is a website that hosts audio for goldenaudiobooks.club, sharedaudiobooks.net,hdaudiobooks.net
"""

from os import mkdir, path
from urllib import parse

from bs4 import BeautifulSoup
from pypdl import Pypdl
from requests import get
from rich import print

website_lists = [
    "goldenaudiobook",  # https://goldenaudiobook.net/
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


def download_now(title, audios, basepath):
    try:
        print(f"Downloading [bold]{title}[/bold]")
        dl = Pypdl(allow_reuse=True)
        for audio in audios:
            try:
                bookpath = path.join(basepath, parse.unquote(audio.split("/")[-2]))
                print(f"\tFile: {bookpath}/{audio.split('/')[-1].split('?')[0]}")
                if not path.exists(bookpath):
                    mkdir(bookpath)

                dl.start(
                    url=audio,
                    file_path=bookpath,
                    overwrite=False,
                    multisegment=False,
                    retries=5,
                )
            except Exception as e:
                print(f"Error downloading {audio}: {str(e)}")
                continue

        dl.shutdown()
        print("Completed")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        if "dl" in locals():
            dl.shutdown()
