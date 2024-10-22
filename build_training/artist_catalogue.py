from spotify_data import Spotify_Data
from dotenv import load_dotenv
import pandas as pd

from lyrics_scrapper import Lyric_Scrapper

full_artist_list = ['Big Thief',
                    'Wet Leg',
                    'Chappell Roan',
                    'Charli xcx',
                    'Frankie Cosmos',
                    'Julia Jacklin',
                    'Whitney',
                    'Alvvays',
                    'Snail Mail',
                    ]


def main():
    # Initialize spotify class and download spotify data
    sd = Spotify_Data()
    df_full = pd.concat([sd.build_artist_dataset(artist) for artist in full_artist_list])
    
    # Get song lyrics for each song
    lyrics_list = []
    
    for idx, row in df_full.iterrows():
        song_lyrics = Lyric_Scrapper(row['artist_name'], row['track_name'])
        lyrics_list.append(song_lyrics.get_lyrics())
        
    df_full['lyric_location'] = lyrics_list
    
    # Save spotify data
    df_full[~df_full['lyric_location'].isna()].to_csv('spotify_artist_info.csv', index=False)
    
if __name__ == "__main__":
    main()

