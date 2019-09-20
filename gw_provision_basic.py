#
# This is a basic test for GW provisioning test.
#

import time
from pyHS100 import (SmartPlug)
from test_config import smart_plug_ip

print("GW provisioning test starts...\n")

print("Step 1: power off DUT")
p = SmartPlug(smart_plug_ip)
p.state = "OFF"
time.sleep(3)
print("Step 2: power on DUT")
p.state = "ON"



