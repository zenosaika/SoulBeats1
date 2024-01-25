# FakeRoV

## Start The Server

- Run Server in Container
```
docker build --tag 'nenefight' .
docker run --rm -it -p 8080:8080 nenefight
```

- Forward Port using ngrok
```
ngrok tcp 8080
```

## Join The Server
- Change `SERVER_IP` and `SERVER_PORT` in client.py
- run client.py to join the server
