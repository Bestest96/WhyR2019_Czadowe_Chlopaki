from rating_cor.type_dataframe import get_df_by_type
import pandas as pd
import os

os.chdir('WhyR2019_Czadowe_Chlopaki')
places_df = pd.read_csv('data/places.csv')
pop_times_df = pd.concat([pd.read_csv('data/popular_times_1.csv'), pd.read_csv('data/popular_times_2.csv')])

