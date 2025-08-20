import random
import time

from hostess.station.station import Station
import invoke

#
# for _ in range(100):
#     invoke.run('bash', asynchronous=True)
#
#

host, port = "localhost", random.randint(10000, 20000)
station = Station(host, port)
station.start()
try:
    for i in range(100):
        station.launch_node(
            name=f'kitty{i}',
            elements=(
                ("hostess.station.actors", "SysCaller"),
                ("hostess.station.actors", "FileSystemWatch")
            ),
            update_interval=0.1
        )
    for node in station.nodes:
        station.shutdown_node(node['name'])
    time.sleep(6)
    assert all(n['reported_status'] == 'shutdown' for n in station.nodes)
finally:
    station.shutdown()
