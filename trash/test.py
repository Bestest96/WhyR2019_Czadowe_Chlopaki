from ctypes import Structure, c_double
import sys
import os
import geoplotlib
from geoplotlib.core import BatchPainter
from geoplotlib.layers import BaseLayer, HotspotManager
from geoplotlib.utils import read_csv, BoundingBox
from multiprocessing import Process, Value
import pandas as pd 
import colorsys

class CustomLayer(BaseLayer):
    def __init__(self, index, data, color=None, point_size=2, f_tooltip=None):
        """Create a dot density map
        :param data: data access object
        :param color: color
        :param point_size: point size
        :param f_tooltip: function to return a tooltip string for a point
        """
        self.index = index
        self.full_data = data
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
        self.painter.points(x, y, 2*self.point_size, False)

    def on_key_release(self, key, mod):
        print(key)
        if self.timer != 0:
            return
        
        self.timer = 1
        
        if key == self.index:
            if len(self.data) != 0:
                self.data = []
            else:
                self.data = self.full_data
            self.invalidate()


    def draw(self, proj, mouse_x, mouse_y, ui_manager):
        self.painter.batch_draw()
        picked = self.hotspots.pick(mouse_x, mouse_y)
        if picked:
            ui_manager.tooltip(picked)
        
        print(self.timer)
        
        if self.timer != 0:
            self.timer += 1
        if self.timer == 60:
            self.timer = 0
    
    def bbox(self):
        return BoundingBox.from_points(lons=self.data['lon'], lats=self.data['lat'])


def hsv2rgb(h,s,v):
    return list(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

def yolo():
    data = read_csv('bus.csv')
    geoplotlib.dot(data)
    geoplotlib.show()

def cb(fn):
    sys.stdin = os.fdopen(fn)
    while True:
        var = input("Please enter something: ")
        if var == 'list':
            print(levels)

def kappa():
    global levels
    data = pd.read_csv("places.csv", usecols=["name", "lat", "lon", "type"])
    levels = data.type.unique()
    for index, obj_type in enumerate(levels):
        #if index != 0 and index != 1:
        #    continue
        #print("{} {}".format(type, 360 / num_of_types * index))
        #print("{} {}".format(type, hsv2rgb(360 / num_of_types * index / 100, 1, 1)))
        series = data.loc[data.type == obj_type]
        geoplotlib.add_layer(CustomLayer(index + 49, geoplotlib.utils.DataAccessObject(series), color=hsv2rgb(360 / len(levels) * index / 100, 1, 1)))
    geoplotlib.show()


if __name__ == "__main__":
    fn = sys.stdin.fileno()
    #levels = Array('i', None, lock=True)
    t1 = Process(target=kappa)
    t2 = Process(target=cb, args=(fn,))
    
    t1.start()
    #t2.start()
    #kappa()