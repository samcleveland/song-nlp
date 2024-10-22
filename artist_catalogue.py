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
    sd = Spotify_Data()
    print(pd.DataFrame(sd.get_tracks('wetleg')['tracks']))


#if __name__ == "__main__":
#    main()

# Initialize class
sd = Spotify_Data()

df_full = pd.concat([sd.build_artist_dataset(artist) for artist in full_artist_list])

for idx, row in df_full.iterrows():
    song_lyrics = Lyric_Scrapper(row['artist_name'], row['track_name'])
    song_lyrics.get_lyrics()
