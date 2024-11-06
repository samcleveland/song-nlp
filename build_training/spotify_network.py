from dotenv import load_dotenv
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd

import time


load_dotenv()

class Spotify_Network():
    '''
    Class to load in spotify song data  
    
    '''
    
    def __init__(self):
        CLIENT_ID: Final[str] = os.getenv('CLIENT_ID')
        CLIENT_SECRET: Final[str] = os.getenv('CLIENT_SECRET')
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))
        
        self.visited_artists = set()
        
        
    def get_artist_id(self, artist: str) -> pd.DataFrame:
        '''Returns the dataframe with artist ID, popularity, and genre for input artist name'''       
        # Return top search results for artist
        search_df: pd.DataFrame = pd.DataFrame(self.sp.search(artist, type='artist'))
        
        # Filter dataframe down to only artist info
        artist_df: pd.DataFrame = pd.DataFrame(search_df.loc['items',:].iloc[0])
        return artist_df[['id',
                          'name',
                          'popularity',
                          'genres',
                          'followers',
                          ]].rename({'id':'artist_id',
                                     'name':'artist_name'},
                                      axis=1).iloc[:1]
                                     
                                     
    def get_top_tracks(self, artist_id:str) -> pd.DataFrame:
        
        top_tracks_df: pd.DataFrame = pd.DataFrame(self.sp.artist_top_tracks(artist_id)['tracks'])
        top_tracks_df['artist_id'] = artist_id
        top_tracks_df = top_tracks_df[['id',
                                       'duration_ms',
                                       'explicit',
                                       'name',
                                       'popularity',
                                       'artist_id',
                                       'artists'
                                       ]].rename({'id':'track_id',
                                                  'name':'track_name'},
                                                   axis=1).set_index('track_id')
    
        return top_tracks_df
    
    def spotify_related_artists(self, artist_id:str):
        artist_df: pd.DataFrame =  pd.DataFrame(self.sp.artist_related_artists(artist_id)['artists'])
        
        return artist_df[['id',
                          'name',
                          'popularity',
                          'genres',
                          'followers',
                          ]].rename({'id':'artist_id',
                                     'name':'artist_name'},
                                      axis=1)
                                     
    def crawler_main(self, artist_name:str, webcrawler_cap:int = 100) -> pd.DataFrame:
        artist_id = self.get_artist_id(artist_name).loc[0,'artist_id']
        
        self.visited_artists.add(artist_id)
        
        self.top_tracks_df = self.get_top_tracks(artist_id)
        
        top_related_artists = self.spotify_related_artists(artist_id).artist_id.tolist()
        for artist in top_related_artists:
            self.crawler(artist, webcrawler_cap = webcrawler_cap)
            
        self.top_tracks_df = self.clean_song_artists(self.top_tracks_df)
        
        
        feature_df_list = []
        for chunk in range(0, len(self.top_tracks_df), 100):
            print(f'{chunk}')

            audio_features = pd.DataFrame(self.sp.audio_features(self.top_tracks_df.index.to_list()[chunk:chunk+100]))
            feature_df_list.append(audio_features)

        
        self.top_tracks_df = self.top_tracks_df.merge(pd.concat(feature_df_list),
                                                      how='left',
                                                      left_on='track_id',
                                                      right_on='id')
                
        return self.top_tracks_df
            
                                     
    def crawler(self, artist_id:str, webcrawler_cap: int = 100):
        time.sleep(.5)
       
        if len(self.visited_artists) % 10 == 0:
            print(f'{len(self.visited_artists)} / {webcrawler_cap}')
        
        self.visited_artists.add(artist_id)
        
        try:
            self.top_tracks_df = pd.concat([self.top_tracks_df, self.get_top_tracks(artist_id)])  # this is not efficient
        except:
            pass
        
        try:
            top_related_artists = self.spotify_related_artists(artist_id).artist_id.tolist()
        except:
            top_related_artists = None

        if top_related_artists is not None:
            for artist in top_related_artists:
                if artist not in self.visited_artists and len(self.visited_artists) < webcrawler_cap:
                    self.crawler(artist, webcrawler_cap = webcrawler_cap)
                else:
                    pass
            
    def clean_song_artists(self, song_df: pd.DataFrame) -> pd.DataFrame:
        song_df['artist_list'] = song_df['artists'].apply(lambda row: [r['name'] for r in row])
        return song_df
    
    def get_audio_analysis(self, track_id: str) -> pd.DataFrame:
        return self.sp.audio_analysis(track_id)
    
    def get_audio_feat(self, track_id: list) -> pd.DataFrame:
        return self.sp.audio_features(track_id)
