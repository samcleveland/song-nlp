from dotenv import load_dotenv
import os

from transformers import pipeline, BertTokenizer


import pandas as pd
import plotly.express as px

load_dotenv()


class NLP():
    def __init__(self, song_data:pd.DataFrame = None, song_data_location:str = None):
        if song_data is None:
            self.song_data = pd.read_csv(song_data_location)
        else:
            self.song_data = song_data
        
    def load_lyrics(self, song_list: list) -> pd.DataFrame:
        lyric_dict = dict.fromkeys(song_list)
        
        for filename in lyric_dict.keys():
            lyrics = self.read_lyrics_from_txt_file(filename)            
            lyric_dict[filename] = ' '.join(lyrics.split())
            
        return pd.DataFrame.from_dict(lyric_dict, orient='index', columns=['lyrics']).rename(index={'Index':'Song'})
        
        
        
    def read_lyrics_from_txt_file(self, file_location:str) -> str:
        with open(f"../lyrics/{file_location.replace(' ','')}", "r", encoding="utf-16") as file:
            lyrics: str = file.read() 
            file.close()
            
        return lyrics
    
    def song_sentiment_analysis(self, lyrics:list) -> pd.DataFrame:
        classifier = pipeline("text-classification", top_k=None)
        
        sentiment = classifier(lyrics)
        
        return pd.DataFrame([self.clean_emotion_dict(song) for song in sentiment])
        
    
    def song_emotion_analysis(self, lyrics:list) -> pd.DataFrame:
        classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)
        
        emotion_list = classifier(lyrics)
        
        return pd.DataFrame([self.clean_emotion_dict(song) for song in emotion_list])
    
    def clean_emotion_dict(self, emtions_dict:dict) -> dict:
        
        return {emotion['label']:emotion['score'] for emotion in emtions_dict}
    
    def token_length_lyrics(self, lyrics:list) -> list:
        classifier = pipeline("text-classification", top_k=None)
        tokenizer = classifier.tokenizer
        
        return [len(tokenizer.tokenize(song)) for song in lyrics]
    
    
    def nlp_songs(self) -> pd.DataFrame:
        song_lyrics = self.load_lyrics(self.song_data['lyric_location'])
        
        song_lyrics['token_count'] = self.token_length_lyrics(song_lyrics['lyrics'].to_list())
        scoreable_song_lyrics = song_lyrics[song_lyrics['token_count'] < 500].copy().reset_index().rename({'index':'song'}, axis=1)
    
        scoreable_song_lyrics = scoreable_song_lyrics.merge(self.song_sentiment_analysis(scoreable_song_lyrics['lyrics'].to_list()),
                                                            how='left',
                                                            left_index=True,
                                                            right_index=True)
        
        scoreable_song_lyrics = scoreable_song_lyrics.merge(self.song_emotion_analysis(scoreable_song_lyrics['lyrics'].to_list()),
                                                            how='left',
                                                            left_index=True,
                                                            right_index=True)
        
        return self.song_data.merge(scoreable_song_lyrics,
                                    how='left',
                                    left_on='lyric_location',
                                    right_on='song').drop(['song',
                                                           'lyrics'],
                                                           axis=1)
