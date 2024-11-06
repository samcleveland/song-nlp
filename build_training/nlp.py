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
            
        self.song_data = self.song_data[~self.song_data['lyric_location'].isna()].reset_index(drop=True).copy()
        
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
        
        sentiment = []
        
        for lyric in lyrics:
            #lyric = lyric.split()
            #lyric = ' '.join(lyric[:350])
            try:
                sentiment.append(classifier(lyric)[0])
            except:
                sentiment.append([{'label':'POSITIVE', 'score':None}, {'label':'NEGATIVE', 'score':None}])
        
        for lyric in lyrics:
            try:
                sentiment.append(classifier(lyric))
            except:
                sentiment.append(None)
        
        return pd.DataFrame([self.clean_emotion_dict(song) if song is not None else None for song in sentiment])
        
    
    def song_emotion_analysis(self, lyrics:list) -> pd.DataFrame:
        classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)
        
        emotion_list = []
        
        for lyric in lyrics:

            #lyric = lyric.split()
            #lyric = ' '.join(lyric[:350])
            try:
                emotion_list.append(classifier(lyric)[0])
            except:
                emotion_list.append([{'label': 'joy', 'score': None}, 
                                     {'label': 'neutral', 'score': None}, 
                                     {'label': 'sadness', 'score': None},
                                     {'label': 'disgust', 'score': None}, 
                                     {'label': 'anger', 'score': None}, 
                                     {'label': 'surprise', 'score': None}, 
                                     {'label': 'fear', 'score': None}])
        
        return pd.DataFrame([self.clean_emotion_dict(song) if song is not None else None for song in emotion_list])
    
    def clean_emotion_dict(self, emotion_dict_list:list) -> dict:
        
        return {emotion['label']:emotion['score'] for emotion in emotion_dict_list}
    
    def token_length_lyrics(self, lyrics:list) -> list:
        classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
        tokenizer = classifier.tokenizer
        
        return [len(tokenizer.tokenize(song)) for song in lyrics]
    
    
    def nlp_songs(self) -> pd.DataFrame:
        song_lyrics = self.load_lyrics(self.song_data['lyric_location']).reset_index().rename({'index':'Lyric Location'},axis=1)
        

        sent_scored_lyrics = song_lyrics.merge(self.song_sentiment_analysis(song_lyrics['lyrics'].to_list()),
                                                            how='left',
                                                            left_index=True,
                                                            right_index=True)

        emotion_scored_lyrics = sent_scored_lyrics.merge(self.song_emotion_analysis(song_lyrics['lyrics'].to_list()),
                                                        how='left',
                                                        left_index=True,
                                                        right_index=True)
        
        return self.song_data.merge(emotion_scored_lyrics,
                                    how='left',
                                    left_on='lyric_location',
                                    right_on='Lyric Location').drop(['Lyric Location','lyrics'], axis=1)