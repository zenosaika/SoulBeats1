# Soul Beats 1

## Start The Server

- Run Server in Container
```
docker build --tag 'soulbeats1' .
docker run --rm -it -p 8080:8080 soulbeats1
```

- Forward Port using ngrok
```
ngrok tcp 8080
```

## Join The Server
- Change `SERVER_IP` and `SERVER_PORT` in client.py
- run client.py to join the server

## Credits
- [Character Sprite Generator](https://sanderfrenken.github.io/Universal-LPC-Spritesheet-Character-Generator)
- [Procedural Orb Generator](https://itch.io/queue/c/1866035/pixel-art-generators?game_id=1495273)
- [RPG Map Maker](https://deepnight.net/tools/rpg-map/)

## Presentation
<img src="https://github.com/zenosaika/SoulBeats1/blob/main/presentation/1.jpg"><br>
<img src="https://github.com/zenosaika/SoulBeats1/blob/main/presentation/2.jpg"><br>
<img src="https://github.com/zenosaika/SoulBeats1/blob/main/presentation/3.jpg"><br>
<img src="https://github.com/zenosaika/SoulBeats1/blob/main/presentation/4.jpg"><br>
<img src="https://github.com/zenosaika/SoulBeats1/blob/main/presentation/5.jpg"><br>
<img src="https://github.com/zenosaika/SoulBeats1/blob/main/presentation/6.jpg"><br>
<img src="https://github.com/zenosaika/SoulBeats1/blob/main/presentation/7.jpg"><br>
<img src="https://github.com/zenosaika/SoulBeats1/blob/main/presentation/8.jpg"><br>