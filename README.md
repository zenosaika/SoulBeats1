# FakeRoV

## Start The Server

- Run Server in Container
```
docker build --tag 'fakerov' .
docker run --rm -it -p 8080:8080 fakerov
```

- Forward Port using ngrok
```
ngrok tcp 8080
```

## Join The Server
- Change `SERVER_IP` and `SERVER_PORT` in client.py
- run client.py to join the server

## Project Overview
<img src="https://github.com/zenosaika/FakeRoV/blob/main/project_overview.png">