# BattleShip
Python implementation of BattleShip for 2 players using sockets.

<img src="https://t3.ftcdn.net/jpg/05/92/31/70/360_F_592317043_rOOpTliZqnmqLi3YwWxGIgVyyfk5nMaM.jpg" width=100% />

# Sprint 1

## Deliverables:

* **TCP BattleshipServer**: Manages player connections, game state, and turn-based gameplay over TCP.
* **TCP BattleshipClient**: Connects to the server, handles player interactions and game commands via the command line.
* **Message Protocol Class**: Serializes and deserializes game data in JSON format for communication between server and clients.
* **ErrorHandler Wrapper Class**: Provides error handling and recovery mechanisms for server and client methods.
* **Unit Tests for Client-Server Communication**: Validates client-server communication, message integrity, and server reliability (work in progress).



## How to play (note this is in active dev):

### Start the server:
```bash
python3 server.py
```

### Connect clients:
```bash
python3 client.py
```

### Play the game:
* Each player positions their battleships using the command line.
* The game starts.
* Players take turns targeting chosen coordinates, attempting to sink each others ships.
* The first player to eliminate all their opponents ships wins the game!

## Technologies Used:
* Python
* Sockets

## Additional Resources:
* [Getting started with Python](https://www.python.org/about/gettingstarted/)

***Additional documentation coming soon***
