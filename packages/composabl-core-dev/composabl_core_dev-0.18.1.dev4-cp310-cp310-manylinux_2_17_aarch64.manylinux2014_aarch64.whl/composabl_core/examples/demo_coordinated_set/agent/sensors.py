# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core import Sensor

s1 = Sensor("state1", "the counter", lambda sensors: sensors["state1"])
s2 = Sensor("time_ticks", "the time counter", lambda sensors: sensors["time_ticks"])

sensors = [s1, s2]
