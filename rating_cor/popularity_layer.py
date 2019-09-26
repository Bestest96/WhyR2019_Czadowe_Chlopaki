import colorsys

from geoplotlib.layers import BaseLayer, BatchPainter, BoundingBox

from rating_cor.type_dataframe import *


def hsv2rgb(h, s, v):
    return list(int(round(i * 255)) for i in colorsys.hsv_to_rgb(h, s, v))


class AnimatedLayer(BaseLayer):

    def __init__(self, data_places, data_times, ptype='bakery'):
        self.painter = None
        bk_places, bk_pop_times = get_df_by_type(data_places, data_times, ptype)
        bk_places = bk_places.drop(['point'], axis=1)
        self.bk_places = bk_places.drop_duplicates(['place_id'])
        self.bk_pop_times = bk_pop_times.drop(['name', 'vicinity'], axis=1)
        self.limit = 1
        self.day_idx = 0
        self.hour_idx = 0
        self.hours = self.bk_pop_times.hour.unique()
        self.days = self.bk_pop_times.day.unique()
        self.timer = 0

    def invalidate(self, proj):
        pass

    def draw(self, proj, mouse_x, mouse_y, ui_manager):
        join_data = get_places_pop(self.bk_places, self.bk_pop_times,
                                   self.hours[self.hour_idx], self.days[self.day_idx])
        self.painter = BatchPainter()
        for i in join_data.occupancy_index.unique():
            points = join_data.loc[join_data.occupancy_index == i]
            self.painter.set_color(hsv2rgb(1, 1, i / join_data.occupancy_index.max()))
            self.painter.points(*proj.lonlat_to_screen(points['lng'], points['lat']))
        self.painter.batch_draw()
        if self.timer != 0:
            self.timer += 1
        if self.timer >= 60:
            self.timer = 0

    def on_key_release(self, key, modifiers):
        if self.timer != 0:
            return
        self.timer = 1
        if key == 110:
            self.hour_idx += 1
            if self.hour_idx == len(self.hours):
                self.hour_idx = 0
                self.day_idx += 1
                if self.day_idx == len(self.days):
                    self.day_idx = 0
        elif key == 98:
            self.hour_idx -= 1
            if self.hour_idx == -1:
                self.hour_idx = len(self.hours) - 1
                self.day_idx -= 1
                if self.day_idx == -1:
                    self.day_idx = len(self.days) - 1
        return True

    def bbox(self):
        return BoundingBox.from_points(lons=self.bk_places['lng'], lats=self.bk_places['lat'])
