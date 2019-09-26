import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

places_df = pd.read_csv('../data/places.csv')
pop_times_df = pd.concat([pd.read_csv('../data/popular_times_1.csv'), pd.read_csv('../data/popular_times_2.csv')])

def get_df_by_type(places_df, pop_times_df, place_types):
    places_by_type = places_df[places_df.type.isin(place_types)]
    pop_times_by_type = pop_times_df[pop_times_df.place_id.isin(places_by_type.place_id)]
    return places_by_type, pop_times_by_type

def get_places_pop(places_df, pop_times_df):
    pop_times_df = pop_times_df[['place_id', 'occupancy_index']].groupby(['place_id']).mean()
    return pop_times_df.join(places_df.set_index('place_id'))

if __name__ == "__main__":
	pd.set_option('display.max_columns', 200, 'display.max_columns', 20)
	bk_places, bk_pop_times = get_df_by_type(places_df, pop_times_df, ['restaurant', 'bar', 'cafe', 'bakery'])
	bk_places = bk_places.drop(['point'], axis=1)
	bk_places = bk_places.drop_duplicates(['place_id'])
	bk_pop_times = bk_pop_times.drop(['name', 'vicinity'], axis=1)
	data = get_places_pop(bk_places, bk_pop_times)
	data = data.drop(['types', 'vicinity', 'price_level', 'lat', 'lng'], axis=1)
	data = data.sort_values(by=['user_ratings_total', 'occupancy_index'], ascending=False)
	data = data.loc[(data['occupancy_index'] >= 1) & (data['user_ratings_total'] < 4000) & (data['rating'] >= 3)]
	#ax1 = data.plot.scatter(x='user_ratings_total', y='rating', c='DarkBlue')
	
	cmap = cm.get_cmap('Spectral')

	threedee = plt.figure().gca(projection='3d')
	data['color'] = np.where((data['user_ratings_total'] > data['user_ratings_total'].mean()) & (data['rating'] > data['rating'].mean()) & (data['occupancy_index'] < data['occupancy_index'].mean()), 'red', 'green')
	threedee.scatter(data['user_ratings_total'], data['rating'], data['occupancy_index'], c=data['color'] ,cmap=cmap)
	threedee.set_xlabel('user_ratings_total')
	threedee.set_ylabel('rating')
	threedee.set_zlabel('occupancy_index')
	plt.show()