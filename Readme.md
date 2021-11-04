# Greetings!
The majority of the code logic is in spectre/spectre_main/views.py
The setup of the database is in spectre/spectre_main/models.py
The tests are located in spectre/tests.py

# Purpose:
The purpose of this project is to get historic by the hour weather from OpenWeatherMap for Manhattan (up to 5 days)
and then be able to update the records when a job is triggered. The project runs in a docker container, and 
launches a second docker container to trigger the API GET requests from OpenWeatherMap. 

## To run inside of a container:
```
cd spectre_job
docker build -t spectredockerjob .
cd ../spectre
docker build -t coolproject . 
docker run --mount type=bind,source=//var/run/docker.sock,target=/var/run/docker.sock --publish 8000:8000 coolproject 
```
## To run tests:
```
cd spectre
python tests.py
```
### To close:
#### From another terminal:
```
docker container kill $(docker ps -q)
```

### Notes:
The application can be found at http://localhost:8000/{path}
path options include:

-'trigger'-> POST endpoint that triggers docker job that adds data to database from external API
-'store' -> POST endpoint that accepts json body to add data to database
-'load' -> GET endpoint can accept argument datetime with an int in unix time
-'lastEntry' -> GET endpoint that returns last item in database
-'deleteDatabase' -> GET endpoint thtat removes all items from database
-'dbLength'  -> GET endpoint returns length of items in the database# spectreProject
