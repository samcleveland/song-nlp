
from dotenv import load_dotenv
import os
from pathlib import Path

import pandas as pd

from spotify_network import Spotify_Network
from lyrics_scrapper import Lyric_Scrapper
from nlp import NLP




artist = 'rolling stones'



def main():
    # Initialize spotify class and download spotify data
    sn = Spotify_Network()
    print(f'{artist}')
    df_songs = sn.crawler_main(artist, webcrawler_cap = 50)
    
    # write data to sql

    
    # Get song lyrics for each song
    lyrics_list = []
    
    for idx, row in df_songs.iterrows():
        song_lyrics = Lyric_Scrapper(row['artist_list'][0], row['track_name'])
        lyrics_list.append(song_lyrics.get_lyrics())
        
    df_songs['lyric_location'] = lyrics_list
    
    # remove songs that don't have lyrics
    df_songs_with_lyrics = df_songs[~df_songs['lyric_location'].isna()].copy()
    
    song_nlp = NLP(song_data = df_songs_with_lyrics)
    df_songs_with_lyrics = song_nlp.nlp_songs()
    
    # Save spotify data
    output_path = 'spotify_artist_info_nlp.csv'
    
    if Path(output_path).is_file():
        df_songs_with_lyrics.to_csv(output_path, mode='a', header=False, index=False)
    else:
        df_songs_with_lyrics.to_csv(output_path, index=False)
    
if __name__ == "__main__":
    main()





