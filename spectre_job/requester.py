import time
import requests
from datetime import datetime, timedelta
import json 

weatherAPI_key = "8f436b315b23053092bbb93a346f8da6"
weatherAPI_base = "https://api.openweathermap.org/data/2.5/onecall/timemachine?"

db_base = 'http://localhost:8000/'
db_GET_suffix = 'lastEntry'
db_POST_suffix = 'store'
lat = 40.78
lon = -72.94

def getLastEntry():
    r = None
    url = db_base + db_GET_suffix
    r = requests.get(url)
    print("get last", r, r.status_code, r.text)
    try:
        print('abotut to load entrydata')
        entryData = r.text.replace("'", '"')
        
        print("step1", entryData, len(entryData), type(entryData))
        entryData = json.loads(entryData)
        print("step2", entryData, len(entryData), type(entryData))
        return (entryData['time'], entryData['temp'])
    except:
        print('something wrong')
    return None

def manageWeatherApiQuery():
    weatherApiQueryData = []
    lastEntry =  getLastEntry()
    now = datetime.now()
    if lastEntry:
        entryTime, _ = lastEntry
        nextTime = entryTime + 3600
        print(nextTime)
        print('now', now.timestamp())
        if now.timestamp() < nextTime:
            return weatherApiQueryData
        secondsDifference = int(now.timestamp()) - nextTime
        print(secondsDifference)
        days = secondsDifference // (3600*24)
        print(days)
        if days > 5:
            print(days)
            print("Oh no we have a problem")
        else:
            while days >= 0:
                weatherApiQueryData += queryweatherAPI(nextTime)
                nextTime += (24*3600)
                days -= 1
    else:
        for day in reversed(range(6)):
            time_before = now - timedelta(days=day)
            start = int(time_before.timestamp())
            weatherApiQueryData += queryweatherAPI(start)
    return weatherApiQueryData

def queryweatherAPI(start):
    # Query Database to see if we have any information

    data = []
    weatherAPI_query = f"lat={lat}&lon={lon}&dt={start}&appid={weatherAPI_key}"
    r = requests.get(weatherAPI_base+weatherAPI_query)
    parsed = json.loads(r.text)
    
    for dataEntry in parsed['hourly']:
        entryTime =  dataEntry['dt']
        entryTemp = dataEntry['temp']
        data.append({"time":entryTime, "temp": entryTemp})
    return data

weather_data = manageWeatherApiQuery()
if weather_data:
    jsonToSend = {"data": weather_data}
    print(jsonToSend)
    jsonSend = json.dumps(jsonToSend)
    r2 =requests.post(url = db_base+db_POST_suffix, data = jsonSend)
    print(r2.status_code)
else:
    print("no data to add")