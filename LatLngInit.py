# -*- coding: utf-8 -*-
__author__ = 'vic'

from LatLngUtil import PointOnEarth
from crud import MongoCRUD
import decimal
import time


class map_location:
    '''
    border_location_top = {
        "lat": 25.210,
        "lng": 121.560
    }

    border_location_right = {
        "lat": 24.970,
        "lng": 121.666
    }

   border_location_base = {
        "lat": 24.970,
        "lng": 121.456
    }
    '''
    border_location_top_all = [{
        # "lat" : 25.216,  #1
        # "lng" : 121.453  #1
        # "lat" : 25.041,  #3
        # "lng" : 121.453     #3
        # "lat" : 25.137,  # 2
        # "lng" : 121.453  # 2
        "lat" : 25.216 , "lng" : 121.453
    },{"lat" : 25.101 ,"lng" :121.481 },{"lat" : 25.008 ,"lng" : 121.529}]

    border_location_right_all =[ {
        # "lat" : 25.137,  #right 1
        # "lng" : 121.665  #right 1
        # "lat" : 24.957,        #1
        # "lng" : 121.665        #1
        # "lat" : 24.957,   #3
        # "lng" : 121.665  #3
        # "lat" : 25.041, #2
        # "lng" : 121.665 #2
        "lat" : 25.101 , "lng" : 121.624
    },{"lat" : 25.008, "lng" : 121.634},{"lat" : 24.960 ,"lng" : 121.621 }]
    border_location_base_all = [{
        # "lat" : 25.137,  #1
        # "lng" : 121.453  #1
        # "lat" : 25.957, #1
        # "lng" :121.435 #1
        # "lat" : 24.957,  #3
        # "lng" : 121.453  #3
        # "lat" : 25.041, #2
        # "lng" : 121.453 #2
        "lat" : 25.101 ,"lng" : 121.453
    },{"lat" : 25.008 ,"lng" : 121.481}, {"lat" : 24.960 ,"lng" :121.529}]
    def init_location(self, location, degree):
        location['province'] = 'Taiwan'
        location['city'] = 'Taipei'
        location['status'] = '0'
        location['degree'] = degree
        return location

    # def get_location_x(self, direction=90, radius=0.5):

    # def get_location_x(self, border_location_base, border_location_right ,  direction=90, radius=0.25):
    def get_location_x(self, border_location_base, border_location_right ,  direction=90, radius=0.5):
        """
        东经
        lng change
        """
        # loc = self.border_location_base
        loc = border_location_base
        locations = []
        location = loc
        locations.append(self.init_location(loc, direction))
        # while location['lng'] <= self.border_location_right['lng']:
        while location['lng'] <= border_location_right['lng']:
            location = self.get_direction_base(location, direction, radius)
            # print location['lng'],location['lat']
            locations.append(self.init_location(location, direction))
            # radius += 1h
        print '\n\n'
        print 'x_locations==', locations ,'\n', "length:" ,len(locations)
        print '\n\n\n\n'
        return locations

    # def get_location_y(self):
    # def get_location_y(self,border_location):
    def get_location_y(self,border_location_top,border_location):
        """
        北纬
        lat change
        @return:
        """
        direction = 0
        # radius = 1
        radius = 0.5

        locations = []
        # location = self.border_location_base
        location=border_location
        print location , ":"
        # while location['lat'] <= self.border_location_top['lat']:
        while location['lat'] <= border_location_top['lat']:
            location = self.get_direction_base(location, direction, radius)
            locations.append(self.init_location(location, direction))
            # radius += 1
            # print locations.lat
        print 'y_locations==', locations,'\n', "length:" , len(locations)
        self.save(locations)

    # def get_direction_base(self, location_base, direction=0, radius=0.25):
    def get_direction_base(self, location_base, direction=0, radius=0.5):

        """
        """
        p = PointOnEarth(location_base['lng'], location_base['lat'])
        location = p.get_location(direction, radius)
        if location:
            return location

    def save(self, results):
        mcrud = MongoCRUD()
        mcrud.save_circle_centers(results)

    def get_location_border(self):
        """
            location，其中包含此地方的经过地址解析的纬度(lat)、经度(lng)值
        """
        length_i=len(self.border_location_top_all)
        for i in range(0,length_i):
            border_location_base = self.border_location_base_all[i]
            border_location_right = self.border_location_right_all[i]
            locations = self.get_location_x(border_location_base, border_location_right, direction=90, radius=0.5)
            self.save(locations)
            for location in locations:
                border_location_top = self.border_location_top_all[i]
                self.get_location_y(border_location_top,location)

if __name__ == "__main__":
    start = time.clock()
    loc = map_location()
    loc.get_location_border()
    elapsed = (time.clock() - start)
    print("Time used:",elapsed)
