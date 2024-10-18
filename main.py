from spotify_data import Spotify_Data
from dotenv import load_dotenv
import pandas as pd

def main():
    sd = Spotify_Data()
    print(pd.DataFrame(sd.get_tracks('wetleg')['tracks']))


#if __name__ == "__main__":
#    main()

sd = Spotify_Data()
df = sd.get_artist_id('Big Thief')
new_df = sd.get_albums(df.loc[0,'id'])