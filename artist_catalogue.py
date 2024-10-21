from spotify_data import Spotify_Data
from dotenv import load_dotenv
import pandas as pd

full_artist_list = ['Big Thief',
                    'Wet Leg',
                    ]

def main():
    sd = Spotify_Data()
    print(pd.DataFrame(sd.get_tracks('wetleg')['tracks']))


#if __name__ == "__main__":
#    main()

# Initialize class
sd = Spotify_Data()

df_full = pd.concat([sd.build_artist_dataset(artist) for artist in full_artist_list])
