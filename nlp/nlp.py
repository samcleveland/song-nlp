from dotenv import load_dotenv
import os

from transformers import pipeline


import pandas as pd
import plotly.express as px

load_dotenv()


class NLP():
    def __init__(self, song_data_location: str):
        self.song_data = pd.read_csv(song_data_location)
        
    def load_lyrics(self, song_list: list) -> pd.DataFrame:
        lyric_dict = dict.fromkeys(song_list)
        
        for filename in lyric_dict.keys():
            lyrics = self.read_lyrics_from_txt_file(filename)            
            lyric_dict[filename] = ' '.join(lyrics.split())
            
        return pd.DataFrame.from_dict(lyric_dict, orient='index', columns=['lyrics']).rename(index={'Index':'Song'})
        
        
        
    def read_lyrics_from_txt_file(self, file_location) -> str:
        with open(f"../lyrics/{file_location.replace(' ','')}", "r", encoding="utf-16") as file:
            lyrics: str = file.read() 
            file.close()
            
        return lyrics
    
    def song_sentiment_analysis(self, lyrics) -> list:
        
        classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
        return classifier(lyrics)
        


n = NLP('../build_training/spotify_artist_info.csv')
df = n.load_lyrics(n.song_data['lyric_location'])

results = []
failed_songs = []
#classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
classifier = pipeline("text-classification", return_all_scores=True)

for idx, row in df.iterrows():
    try:
        results.append(classifier(row['lyrics']))
    except:
        failed_songs.append(idx)
        results.append(None)
        
df['word_count'] = df.lyrics.apply(lambda row: len(row.split()))
df['char_count'] = df.lyrics.apply(lambda row: len(row))
df['failed'] = df.index.isin(failed_songs)

df_failed = df[df.index.isin(failed_songs)]
        
    
