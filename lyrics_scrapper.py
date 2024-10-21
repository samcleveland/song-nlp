import requests
from bs4 import BeautifulSoup

import re

import warnings





class Lyric_Scrapper():
    def __init__(self, artist: str, song: str):
        self.artist = artist.lower()
        self.song = song.lower()
        
    def lyric_call(self) -> None:
        page = requests.get(f"https://genius.com/{self.artist.replace(' ','-')}-{self.song.replace(' ','-')}-lyrics")
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
        
    
    
l1 = Lyric_Scrapper('big thief', 'change')
l1.lyric_call()
l1_span = l1.cleaning_lyrics()
l1_text = l1.lyrics

l2 = Lyric_Scrapper('olivia rodrigo', 'pretty isnt pretty')
l2.lyric_call()
l2.cleaning_lyrics()
l2_text = l2.lyrics

l3 = Lyric_Scrapper('chappell roan', 'pink pony club')
l3.lyric_call()
l3.cleaning_lyrics()
l3_text = l3.lyrics

l4 = Lyric_Scrapper('charli xcx', '365')
l4.lyric_call()
l4.cleaning_lyrics()
l4_text = l4.lyrics
        
