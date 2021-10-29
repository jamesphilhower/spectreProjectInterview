import unittest
import requests
import time
import json
import datetime

weatherAPI_key = "8f436b315b23053092bbb93a346f8da6"
weatherAPI_base = "https://api.openweathermap.org/data/2.5/onecall/timemachine?"
lat = 40.78
lon = -72.94

time.sleep(1)

base = 'http://localhost:8000/'

class TestAllTheThings(unittest.TestCase):

    # No Data Tests
    # No keywords
    def testaGet_noData(self):
        print("Deleting Data...")
        requests.get(base+"deleteDatabase")
        time.sleep(2)
        r = requests.get(base+"load")
        self.assertEqual(r.status_code, 236)
    # Keywords
    def testaGet_noData_withLowTime(self):
        r = requests.get(base+"load?datetime=99")
        self.assertEqual(r.status_code, 236)
    def testaGet_noData_withReasonableValue(self):
        r = requests.get(base+f"load?datetime={int(time.time())}")
        self.assertEqual(r.status_code, 236)
    def testaGet_noData_withHighTime(self):
        r = requests.get(base+"load?datetime=99999999999")
        self.assertEqual(r.status_code, 236)
    # Inc Keywords
    def testaGet_noData_withLowTimeIncKey(self):
        r = requests.get(base+"load?wrongKey=99")
        self.assertEqual(r.status_code, 236)
    def testaGet_noData_withReasonableValueIncKey(self):
        r = requests.get(base+f"load?datetime={int(time.time())}")
        self.assertEqual(r.status_code, 236)
    def testaGet_noData_withHighTimeIncKey(self):
        r = requests.get(base+"load?wrongKey=999999999999")
        self.assertEqual(r.status_code, 236)

    # Test store Endpoint

    def testbStore_noData(self):
        jsonToSend = {}
        jsonSend = json.dumps(jsonToSend)
        r =requests.post(url = base+"store", data = jsonSend)
        self.assertEqual(r.status_code, 413)
    def testbStore_IncKey_1(self):
        jsonToSend = {"wrongKey": "wrongVal"}
        jsonSend = json.dumps(jsonToSend)
        r =requests.post(url = base+"store", data = jsonSend)
        self.assertEqual(r.status_code, 413)
    def testbStore_IncKey_2(self):
        jsonToSend = {"data": {"wrongKey": 1635526800, "temp": 285.02}}
        jsonSend = json.dumps(jsonToSend)
        r =requests.post(url = base+"store", data = jsonSend)
        self.assertEqual(r.status_code, 411)
    def testbStore_IncKey_3(self):
        jsonToSend = {"data": {"time": 1635526800, "wrongKey": 285.02}}
        jsonSend = json.dumps(jsonToSend)
        r =requests.post(url = base+"store", data = jsonSend)
        self.assertEqual(r.status_code, 411)
    def testbStore_IncJSON(self):
        jsonToSend = "not a json"
        r =requests.post(url = base+"store", data = jsonToSend)
        self.assertEqual(r.status_code, 412)
    def testbStore_IncJSON(self):
        jsonToSend = '{"time": 1635526800, "temp": 285.02}'
        r =requests.post(url = base+"store", data = jsonToSend)
        self.assertEqual(r.status_code, 413)
    def testbStore_correctJSON(self):
        weather_data = [{"time": 1635030000, "temp": 280.35}, {"time": 1635033600, "temp": 285.35}, {"time": 1635037200, "temp": 290.35}]
        jsonToSend = {"data": weather_data}
        jsonSend = json.dumps(jsonToSend)
        r =requests.post(url = base+"store", data = jsonSend)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.text, "3")

    # No keywords
    def testcGet_withData(self):
        r = requests.get(base+"load")
        self.assertEqual(r.text, '{"time": 1635037200, "temp": 290.35}')
    # Keywords
    def testcGet_withData_withLowTime(self):
        r = requests.get(base+"load?datetime=99")
        self.assertEqual(r.text, '{"time": 1635030000, "temp": 280.35}')
    def testcGet_withData_withFoundValue(self):
        r = requests.get(base+f"load?datetime=1635030000")
        self.assertEqual(r.text, '{"time": 1635030000, "temp": 280.35}')
    def testcGet_withData_withCloseValueGoLow(self):
        r = requests.get(base+f"load?datetime=1635030001")
        self.assertEqual(r.text, '{"time": 1635030000, "temp": 280.35}')
    def testcGet_withData_withCloseValueGoHigh(self):
        r = requests.get(base+f"load?datetime=1635031850")
        self.assertEqual(r.text, '{"time": 1635033600, "temp": 285.35}')
    def testcGet_withData_withHighTime(self):
        r = requests.get(base+"load?datetime=99999999999")
        self.assertEqual(r.text, '{"time": 1635037200, "temp": 290.35}')
    # Inc Keywords
    def testcGet_withData_withLowTimeIncKey(self):
        r = requests.get(base+"load?wrongKey=99")
        self.assertEqual(r.text, '{"time": 1635037200, "temp": 290.35}')
    def testcGet_withData_withFoundValueIncKey(self):
        r = requests.get(base+f"load?wrongKey=1635037200")
        self.assertEqual(r.text, '{"time": 1635037200, "temp": 290.35}')
    def testcGet_withData_withHighTimeIncKey(self):
        r = requests.get(base+"load?wrongKey=999999999999")
        self.assertEqual(r.text, '{"time": 1635037200, "temp": 290.35}')
    
    # Trigger
    def testd_Trigger(self):
        # Reset DB 
        requests.get(base+"deleteDatabase")
        time.sleep(2)
        # Request to trigger
        r = requests.post(base+"trigger", data={})
        # Request that gets ignored
        extraRequest = requests.post(base+"trigger", data={})
        self.assertEqual(r.status_code, 201)
        time.sleep(10)
        lengthCheck = requests.get(base+"dbLength")
        l1 = lengthCheck.text
        self.assertGreaterEqual(144, int(l1) or self.assertGreaterEqual(int(l1), 120))
        r2 = requests.post(base+"trigger", data={})
        self.assertEqual(r2.status_code, 201)
        lengthCheck2 = requests.get(base+"dbLength")
        l2 = lengthCheck2.text
        self.assertEqual(l1, l2)  
        # Reset DB
        requests.get(base+"deleteDatabase")
        # Add just one day of data to verify that trigger will load all missing data up til now
        # Check the length of these additions compared to the original ones
        start = datetime.datetime.now()
        start = start - datetime.timedelta(days=5)
        start = int(start.timestamp())
        weatherAPI_query = f"lat={lat}&lon={lon}&dt={start}&appid={weatherAPI_key}"
        r3 = requests.get(weatherAPI_base+weatherAPI_query)
        parsed = json.loads(r3.text)
        data = []
        for dataEntry in parsed['hourly']:
            entryTime =  dataEntry['dt']
            entryTemp = dataEntry['temp']
            data.append({"time":entryTime, "temp": entryTemp})
        last_entry = str(data[-1]).replace("'",'"')
        jsonToSend = {"data": data}
        jsonSend = json.dumps(jsonToSend)
        r4 = requests.post(url = base+"store", data = jsonSend)
        # Check inserted Values
        r5 = requests.get(base+"load")
        self.assertEqual(r5.text, str(last_entry))
        # Check number of inserted on first insert
        self.assertEqual(r4.text, "24")
        r6 = requests.post(base+"trigger", data={})
        self.assertEqual(r6.status_code, 201)
        time.sleep(10)
        lengthCheck = requests.get(base+"dbLength")
        l3 = lengthCheck.text
        # Check number of inserted on second insert
        self.assertEqual(l3, l1)




if __name__ == '__main__':
    unittest.main()