import numpy as np
import pandas as pd
import colorsys
import os
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import geoplotlib
from geoplotlib.core import BatchPainter
from geoplotlib.layers import BaseLayer, HotspotManager
from geoplotlib.utils import read_csv, BoundingBox

places_df = pd.read_csv('../data/places.csv')
pop_times_df = pd.concat([pd.read_csv('../data/popular_times_1.csv'), pd.read_csv('../data/popular_times_2.csv')])

def hsv2rgb(h,s,v):
	return list(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

class CustomLayer(BaseLayer):
	def __init__(self, data, color=None, point_size=2, f_tooltip=None):
		"""Create a dot density map
		:param data: data access object
		:param color: color
		:param point_size: point size
		:param f_tooltip: function to return a tooltip string for a point
		"""
		self.data = data
		self.color = color
		self.timer = 0
		if self.color is None:
			self.color = [255,0,0]
		self.point_size = point_size
		self.f_tooltip = f_tooltip
		self.hotspots = HotspotManager()


	def invalidate(self, proj):
		self.painter = BatchPainter()
		x, y = proj.lonlat_to_screen(self.data['lon'], self.data['lat'])
		if self.f_tooltip:
			for i in range(0, len(x)):
				record = {k: self.data[k][i] for k in self.data.keys()}
				self.hotspots.add_rect(x[i] - self.point_size, y[i] - self.point_size,
									   2*self.point_size, 2*self.point_size,
									   self.f_tooltip(record))
		self.painter.set_color(self.color)
		self.painter.points(x, y, 2*self.point_size, True)

	def draw(self, proj, mouse_x, mouse_y, ui_manager):
		self.painter.batch_draw()
		picked = self.hotspots.pick(mouse_x, mouse_y)
		if picked:
			ui_manager.tooltip(picked)
	
	def bbox(self):
		return BoundingBox.from_points(lons=self.data['lon'], lats=self.data['lat'])


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
	data = data.drop(['types', 'vicinity', 'price_level'], axis=1)
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
	
	cheaters = np.where(data['color'] == 'red')
	cheaters = data.iloc[cheaters]

	geoplotlib.add_layer(CustomLayer(geoplotlib.utils.DataAccessObject(data), color=[0, 255, 0, 60], point_size=4))
	geoplotlib.add_layer(CustomLayer(geoplotlib.utils.DataAccessObject(cheaters), color=[255, 0, 0], point_size=4, f_tooltip=lambda r: r['name']))
	
	geoplotlib.show()