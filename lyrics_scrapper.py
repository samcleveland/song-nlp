import requests
from bs4 import BeautifulSoup

import re


class Lyric_Scrapper():
    def __init__(self, artist: str, song: str):
        self.artist = artist.lower()
        self.song = song.lower()
        
    def clean_title(self, title_part:str) -> str:
        '''
        Removes punctuation from artist name or song name

        Parameters
        ----------
        title_part : str
            Artist's name or song name

        Returns
        -------
        str
            Artist's name or song name without punctuation

        '''
        title_part = re.sub(r"[,!.\{}\[\]\\\()|@#$%^&*+=:;?/<>_'—\"]", "", title_part) #remove any symbols in the name
        title_part = title_part.replace(' ','-') # replace spaces with dashes
        
        return title_part
        
    def lyric_call(self) -> None:
        '''
        Requests genius lyrics for specified song. 

        Returns
        -------
        None
            DESCRIPTION.

        '''
        self.artist_clean = self.clean_title(self.artist)
        self.song_clean = self.clean_title(self.song)
        
        page = requests.get(f"https://genius.com/{self.artist_clean}-{self.song_clean}-lyrics")
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="lyrics-root")
        self.lyrics = results.text
        
    def separate_conjoined_words(self, lyrics: str, split_idx: int) -> str:
        '''
        Recursive function that searches for and separates conjoined words in the song lyrics. 
        Identifies conjoined words by looking for words where there is a lowercase letter or symbol
        immeidately before a capital letter.
        
        Parameters
        ----------
        lyrics : str
            Song lyrics with words that are not properly separated.
            
        split_idx: int
            Index value of needed space

        Returns
            str
        '''
        lyrics = ' '.join([lyrics[:split_idx], lyrics[split_idx:]])
        try:
            return self.separate_conjoined_words(lyrics, 
                                                 re.search(r"[a-z0-9'?,\)][A-Z]", 
                                                           lyrics).start()+1)
        except:
            return lyrics
        
        
    def cleaning_lyrics(self) -> None:
        '''
        Function to clean lyrics in preparation for tokenization. Cleaning includes removing any headers/footers from 
        Genius.com, removing the song part, adding spaces between words, and removing any mid lyric ads.
        
        Uses lyric object already included in class.

        Returns
        -------
        None
            DESCRIPTION.

        '''
        # Remove pre-lyric headings
        self.lyrics = self.lyrics.split('Lyrics')
        self.lyrics = ' '.join(self.lyrics[1:])
        
        # Remove post-lyric footers
        self.lyrics = re.sub(r"[0-9]Embed", '', self.lyrics)
        
        # replace everything between [] with a space
        self.lyrics = re.sub(r"\[.{1,15}]", ' ', self.lyrics)
        
        # add space between words on different lines
        ## webscrapper combines word at the end of the line with the first word on the next line        
        self.lyrics = self.separate_conjoined_words(self.lyrics, 
                                                    re.search(r"[a-z0-9'?,\)][A-Z]", 
                                                              self.lyrics).start()+1)
        
        # remove tour ads
        self.lyrics = re.sub(fr"(?i)see {self.artist} live get tickets as low as \$\d+ you might also like", "", self.lyrics)
        
        
    def write_lyrics(self) -> None:
        with open(f"lyrics/{self.artist_clean}-{self.song_clean}.txt", "w", encoding="utf-16") as file:
            file.write(self.lyrics)
            
    def get_lyrics(self) -> None:
        '''
        Main function that cleans artist name, downloads the songs lyrics, cleans the song lyrics and saves the lyrics into a txt file for processing later. 

        Returns
        -------
        None
            DESCRIPTION.

        '''
        try:
            self.lyric_call()
            self.cleaning_lyrics()
            self.write_lyrics()
        except:
            print(f'{self.artist} - {self.song} failed')
