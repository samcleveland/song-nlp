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
        
        
    def get_artist_id(self, artist: str, start_idx: int = 0) -> pd.DataFrame:
        '''Returns the dataframe with artist ID, popularity, and genre for input artist name'''       
        # Return top search results for artist
        search_df: pd.DataFrame = pd.DataFrame(self.sp.search(artist, offset=start_idx, type='artist'))
        
        # Filter dataframe down to only artist info
        artist_df: pd.DataFrame = pd.DataFrame(search_df.loc['items',:].iloc[0])
        artist_df['name'] = artist_df['name'].apply(lambda row: row.lower())
        
        if len(artist_df[artist_df.name == artist.lower()]) == 1:
            return artist_df[artist_df.name == artist.lower()]
        elif start_idx >= 90:
            return None
        else:
            return self.get_artist_id(artist, start_idx = start_idx + 10)
        
    def get_albums(self, artist_id: str = None) -> list:
        ''' Returns something '''
        album_df = self.sp.artist_albums(artist_id, include_groups='album,single', limit=50)
        return pd.DataFrame([i for i in album_df['items']])

    def get_album_tracks(self, album_ids: str) -> pd.DataFrame:
        return pd.DataFrame(self.sp.album_tracks(album_ids)['items'])
    
    def get_audio_analysis(self, track_id: str) -> pd.DataFrame:
        return self.sp.audio_analysis(track_id)
    
    def get_audio_feat(self, track_id: list) -> pd.DataFrame:
        return self.sp.audio_features(track_id)
    
    
    def build_artist_dataset(self, artist: str) -> pd.DataFrame:
        '''
        Builds full artist dataset 

        Parameters
        ----------
        artist : str
            Artist Name

        Returns
        -------
        pd.DataFrame
            Spotify song analysis by track for Artist's catalogue.

        '''
        
        # Get artist ID
        self.full_artist_df = self.get_artist_id(artist)[['id',
                                                          'name',
                                                          'popularity',
                                                          'genres',
                                                          'followers',
                                                          ]].rename({'id':'artist_id',
                                                                     'name':'artist_name'},
                                                                     axis=1)
        
        if self.full_artist_df is None:
            return pd.DataFrame()
        
        artist_list = self.full_artist_df.artist_id.unique()
        
        # Get all albums by looping through IDs
        for art_id in artist_list:
            album_df = self.get_albums(art_id)[['id',
                                                'name',
                                                'release_date',
                                                'album_group',
                                                'album_type'
                                                ]].rename({'id':'album_id',
                                                           'name':'album_name'},
                                                           axis=1)
            album_df['artist_id'] = art_id   

            self.full_artist_df = self.full_artist_df.merge(album_df,
                                                            how='left',
                                                            left_on='artist_id',
                                                            right_on='artist_id')
            
            # Get all songs on each album
            album_list = album_df.album_id.unique()
            
            track_df_list = []
            
            for alb_id in album_list:
                track_df = self.get_album_tracks(alb_id)[['id',
                                                          'name',
                                                          ]].rename({'id':'track_id',
                                                                     'name':'track_name'},
                                                                     axis=1)
                                                                     
                track_df['album_id'] = alb_id
                
                track_df_list.append(track_df)
            
            track_df = pd.concat(track_df_list)
            
            feature_df_list = []
            for chunk in range(0, len(track_df), 100):
                feature_df_list.append(pd.DataFrame(self.sp.audio_features(track_df.track_id.to_list()[chunk:chunk+100])))
                
            
            track_df = track_df.merge(pd.concat(feature_df_list),
                                      how='left',
                                      left_on='track_id',
                                      right_on='id')
            
            self.full_artist_df = self.full_artist_df.merge(track_df,
                                                            how='left',
                                                            left_on='album_id',
                                                            right_on='album_id')
            
             
    
        return self.full_artist_df
        
        