import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()

        self.datasource = Datasource(user_id=1)
        self.car_marker = None
        self.line_layer = LineMapLayer(coordinates=[], color=[1, 0, 0, 1], width=2)

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """

        self.mapview.add_layer(self.line_layer)  # Add the line layer to the map
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """

        new_points = self.datasource.get_new_points()

        if not new_points:
            return

        for latitude, longitude, road_state in new_points:
            if self.car_marker is None:
                self.car_marker = MapMarker(lat=latitude, lon=longitude, source="images/car.png")
                self.mapview.add_marker(self.car_marker)
                self.mapview.center_on(latitude, longitude)

            self.update_car_marker((latitude, longitude))

            if self.line_layer.coordinates is None:
                self.line_layer.coordinates = [(latitude, longitude)]
            else:
                self.line_layer.add_point((latitude, longitude))

            if road_state == "pothole":
                self.set_pothole_marker((latitude, longitude))
            elif road_state == "bump":
                self.set_bump_marker((latitude, longitude))

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """

        self.car_marker.lat, self.car_marker.lon = point
        self.mapview.center_on(point[0], point[1])

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """

        pothole_marker = MapMarker(lat=point[0], lon=point[1], source="images/pothole.png")
        self.mapview.add_marker(pothole_marker)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """

        bump_marker = MapMarker(lat=point[0], lon=point[1], source="images/bump.png")
        self.mapview.add_marker(bump_marker)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView(zoom=20)
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
