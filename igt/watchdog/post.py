import requests
data = {
"RaspberryNumber":"",
"PowerSwitchNumber":"",
"Status":"connection lost, dut in PM test wait for (11 minutes) before restart the DUT",
}
try:
  r = requests.post("http://bifrost.intel.com:2020/watchdog",data)
except:
  print "--> Could not connect to database"
