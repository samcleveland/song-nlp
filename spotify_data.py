from dotenv import load_dotenv
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd


load_dotenv()

class Spotify_Data():
    '''
    Class to load in spotify song data  
    
    '''
    def __init__(self):
        CLIENT_ID: Final[str] = os.getenv('CLIENT_ID')
        CLIENT_SECRET: Final[str] = os.getenv('CLIENT_SECRET')
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))
        
        
    def get_artist_id(self, artist: str, start_idx:int = 0) -> pd.DataFrame:
        '''Returns the dataframe with artist ID, popularity, and genre for input artist name'''       
        # Return top search results for artist
        search_df: pd.DataFrame = pd.DataFrame(self.sp.search(artist, offset=start_idx, type='artist'))
        
        # Filter dataframe down to only artist info
        artist_df: pd.DataFrame = pd.DataFrame(search_df.loc['items',:][0])
        artist_df['name'] = artist_df['name'].apply(lambda row: row.lower())
        
        if len(artist_df[artist_df.name == artist.lower()]) == 1:
            return artist_df[artist_df.name == artist.lower()]
        elif start_idx >= 90:
            return None
        else:
            return self.get_artist_id(artist, start_idx = start_idx + 10)
        
    def get_albums(self, artist_id:str = None) -> pd.DataFrame:
        ''' Returns something '''
        return self.sp.artist_albums(artist_id)
