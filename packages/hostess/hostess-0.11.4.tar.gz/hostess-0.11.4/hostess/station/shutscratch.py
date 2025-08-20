import datetime as dt
import random
import time

from hostess.station.bases import Sensor
from hostess.station.station import Station


class PrintSensor(Sensor):
    def checker(self, _):
        print(dt.datetime.now().isoformat())
        return None, []


station = Station("localhost", random.randint(11111,22222))
station.start()
station.save_port_to_shared_memory()
# delegate = station.launch_delegate(
#     name='null', context='local', update_interval=0.2
# )
time.sleep(3)
station.shutdown()
