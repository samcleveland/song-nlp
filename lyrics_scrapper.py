import requests
from bs4 import BeautifulSoup



page = requests.get('https://genius.com/Big-thief-change-lyrics')

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="lyrics-root")
t = results.text


class Lyric_Crawler():
    def __init__(self, artist: str, song: str):
        self.artist = artist.lower().replace(' ','-')
        self.song = song.lower().replace(' ','-')
        
    def lyric_call(self) -> str:
        page = requests.get(f'https://genius.com/{self.artist}-{self.song}-lyrics')
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="lyrics-root")
        self.lyrics = results.text
