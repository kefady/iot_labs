import csv
import random
from datetime import datetime
from typing import Optional, TextIO

from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
from domain.parking import Parking


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str) -> None:
        self._filenames = {
            'accelerometer': accelerometer_filename,
            'gps': gps_filename,
            'parking': parking_filename,
        }

        self._files: dict[str, Optional[TextIO]] = {'accelerometer': None, 'gps': None, 'parking': None}
        self._readers: dict[str, Optional[csv.DictReader]] = {'accelerometer': None, 'gps': None, 'parking': None}

        self.is_reading: bool = False

    def start_reading(self, *args, **kwargs):
        for key in self._filenames:
            self._files[key] = open(self._filenames[key], 'r')
            self._reset_reader(key)

        self.is_reading = True

    def read(self) -> dict[str, Parking | AggregatedData]:
        if not self.is_reading:
            raise RuntimeError('FileDatasource.start_reading() must be called before reading')

        acc_row = self._next_row('accelerometer')
        gps_row = self._next_row('gps')
        park_row = self._next_row('parking')

        acc_data = Accelerometer(
            x=int(acc_row["x"]),
            y=int(acc_row["y"]),
            z=int(acc_row["z"])
        )

        gps_data = Gps(
            longitude=float(gps_row["longitude"]),
            latitude=float(gps_row["latitude"])
        )

        park_data = Parking(
            empty_count=int(park_row["empty_count"]),
            gps=Gps(
                longitude=float(park_row["longitude"]),
                latitude=float(park_row["latitude"])
            )
        )

        return {
            'aggregated': AggregatedData(user_id=random.randint(0, 1000), accelerometer=acc_data, gps=gps_data,
                                         timestamp=datetime.now()),
            'parking': park_data,
        }

    def stop_reading(self, *args, **kwargs):
        for key in self._files:
            if self._files[key]:
                self._files[key].close()
                self._files[key] = None
            self._readers[key] = None

        self.is_reading = False

    def _reset_reader(self, key: str):
        file = self._files[key]
        if not file:
            raise RuntimeError(f"Failed to open {key} data file")
        file.seek(0)
        reader = csv.DictReader(file)
        next(reader)  # skip header
        self._readers[key] = reader

    def _next_row(self, key: str) -> dict:
        reader = self._readers[key]
        if not reader:
            raise RuntimeError(f"{key} reader is not initialized")

        row = next(reader, None)
        if row is None:
            self._reset_reader(key)
            row = next(self._readers[key], None)
            if row is None:
                raise RuntimeError(f"No data found in {key} file after reset")
        return row

    def __del__(self):
        self.stop_reading()
