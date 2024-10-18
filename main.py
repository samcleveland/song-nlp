from spotify_data import Spotify_Data
from dotenv import load_dotenv
import pandas as pd

def main():
    sd = Spotify_Data()
    print(pd.DataFrame(sd.get_tracks('wetleg')['tracks']))


#if __name__ == "__main__":
#    main()

# Initialize class
sd = Spotify_Data()

# Get ID for artist
df = sd.get_artist_id('Big Thief')

# Use ID to pull all albums the artist appears on 
albums = sd.get_albums(df.loc[0,'id'])

# Loop through albums to get all songs (regardless of who the artist is)
songs = pd.DataFrame(sd.get_album_tracks(albums[0]))['id'].to_list()


# Loop through songs to get audio analysis
analysis = sd.get_audio_analysis(songs[0])