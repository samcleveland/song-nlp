import pandas as pd

feature_map = {'NEGATIVE': 'continuous - numeric',
                 'POSITIVE': 'continuous - numeric',
                 'acousticness': 'continuous - numeric',
                 'anger': 'continuous - numeric',
                 'danceability': 'continuous - numeric',
                 'disgust': 'continuous - numeric',
                 'duration_ms_x': 'continuous - numeric',
                 'energy': 'continuous - numeric',
                 'fear': 'continuous - numeric',
                 #'genres': None,
                 'instrumentalness': 'continuous - numeric',
                 'joy': 'continuous - numeric',
                 'key': 'ordinal - numeric',
                 'liveness': 'continuous - numeric',
                 'loudness': 'continuous - numeric',
                 'lyric_location': 'id',
                 'mode': 'binary - categorical',
                 'neutral': 'continuous - numeric',
                 'popularity': 'discrete - numeric',

                 #'release_date': 'discrete - numeric',
                 'sadness': 'continuous - numeric',
                 'speechiness': 'continuous - numeric',
                 'surprise': 'continuous - numeric',
                 'tempo': 'continuous - numeric',
                 'time_signature': 'discrete - numeric',
                 'valence': 'continuous - numeric'}

        
def generate_model_dataframe(df: pd.DataFrame, features: list = list(feature_map.keys())) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df[features]
    
    model_features = pd.DataFrame.from_dict(feature_map, orient='index').reset_index().rename({'index':'feature',
                                                                                                0:'stat_data_type'},
                                                                                              axis=1)
    
    model_features['in_model'] = model_features['stat_data_type'].apply(lambda row: 0 if row is None else 1)
    
    return df, model_features

def convert_genre_str_to_dict(artist_genre: str) -> list:
    genre_list = eval(artist_genre)
    return dict.fromkeys(genre_list,1)
        
def clean_genres(df: pd.DataFrame, model_features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    genre_df = pd.DataFrame([convert_genre_str_to_dict(song) for song in df.genres]).fillna(0)
    
    df = df.merge(genre_df,
                  how='left',
                  left_index=True,
                  right_index=True)
    
    genre_features = pd.DataFrame(genre_df.columns).rename({0:'feature'}, axis=1)
    genre_features['stat_data_type'] = 'binary - categorical'
    genre_features['in_model'] = 1
    
    model_features = pd.concat([model_features, genre_features]).reset_index(drop=True)
    
    return df, model_features

def release_year(df: pd.DataFrame, model_features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df['release_date'] = pd.to_datetime(df.release_date).dt.year
    return df, model_features
        
        