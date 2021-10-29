from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
import docker
from docker.types import Mount
from requests.sessions import HTTPAdapter
from .models import WeatherPoint
from json import loads
import time

model_fields = [f.name for f in WeatherPoint._meta.fields]

@transaction.atomic
@csrf_exempt
def trigger(request) -> HttpResponse:   
    try:
        client = docker.from_env()
        imageToRun = client.images.get("spectredockerjob")
        client.containers.run(imageToRun, network="host", detach=True)
        print("Triggered Job")
        return HttpResponse("Job Triggered", status=201)
    except:
        return HttpResponse(status = 500)

@transaction.atomic
@csrf_exempt
def store(request) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse(status=404)
    data = None
    try:
        data = loads(request.body.decode('utf-8'))
    except:
        return HttpResponse(status=412)
    if 'data' not in data:
        print('No Data in Database')
        return HttpResponse(status=413)
    
    items = data['data']
    print(f"Post received with {len(items)}")

    items_to_add = []
    for item in items:
        if 'time' in item and 'temp' in item:
            validTime = validateDate(item['time'])
            validTemp = validateTemp(item['temp'])
        else:
            return HttpResponse(status=411)
        if not validTime or not validTemp or WeatherPoint.objects.filter(time=validTime).exists():
            print("skipping item", item)
            continue
        items_to_add.append(WeatherPoint(time = validTime, temp = validTemp))
    print("Adding this many items -> ", len(items_to_add))
    try:
        WeatherPoint.objects.bulk_create(items_to_add)
    except:
        print("Didn't add data to DB")
        return HttpResponse(status=416)
    time.sleep(1)
    opts = WeatherPoint.objects.all()
    print("len of database", len(opts))
    return HttpResponse(str(len(opts)), status=201)

def getClosestTime(timedate) -> int:
    now = time.time()
    if not timedate or timedate > now:
        offset = now % 3600
        return int(now - offset)
    offset = timedate % 3600
    if offset <= 1800:
        return int(timedate - offset)
    offset_corrector = 3600 - offset
    return int(timedate + offset_corrector)

def validateDate(timedate) -> int: 
    try:
        timedate = int(timedate)
    except:
        return None
    if timedate < 0:
        return None
    return timedate

def validateTemp(temp) -> float:
    try:
        temp = float(temp)
    except:
        return None
    if temp < 179 or temp > 331:
        return None
    return temp

def firstEntry() -> dict:
    first = WeatherPoint.objects.first()
    if not first:
        return None
    first = {field:getattr(first,field) for field in model_fields}
    return first

def lastEntry(request = None)->HttpResponse:
    if request and request.method != "GET":
        return HttpResponse(status = 404)
    entry = WeatherPoint.objects.last()
    if not entry:
        return HttpResponse("No Entries")
    entry = {field:getattr(entry,field) for field in model_fields}
    print('Last entry is ', entry)
    return HttpResponse(str(entry).replace("'", '"'))
    
def load(request) -> HttpResponse:
    if request.method != "GET":
        return HttpResponse(status=404)
    earliest = firstEntry()
    if not earliest:
        print("no data loaded yet")
        return HttpResponse(status=236)
    validTime = None
    if "datetime" in request.GET:
        timedate = request.GET["datetime"]
        validTime = validateDate(timedate)
        if not validTime:
            return HttpResponse("Not a valid Time", status=400)
    query_time = getClosestTime(validTime)
    print("Closest query time", query_time)
    
    if query_time < earliest['time']:
        print("returning earliest")
        return HttpResponse(str(earliest).replace("'", '"'))
    queryResult = WeatherPoint.objects.filter(time = query_time).first()
    print(queryResult)
    if not queryResult:
        return lastEntry()
    queryResult = {field:getattr(queryResult,field) for field in model_fields}
    print(queryResult)
    return HttpResponse(str(queryResult).replace("'", '"'))

@transaction.atomic
def deleteDatabase(request) -> None:
    try:
        WeatherPoint.objects.all().delete()
    except:
        print("failed to delete")
        return HttpResponse(status=500)
    return HttpResponse("Database Deleted", status=200)

@transaction.atomic
def dbLength(request) -> None:
    try:
        return HttpResponse(str(len(WeatherPoint.objects.all())))
    except:
        return HttpResponse(status = 500)