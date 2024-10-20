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

# Sprint 2

## Deliverables:

* **Designed and Implemented Protocol in Client and Server**: Developed a communication protocol for message exchange between the server and clients.
* **Defined the Structure and Format of Messages**: Established the format for messages exchanged between the server and clients, including message types, data fields, and expected responses.
* **Receive, Parse, and Process Messages**: Handles incoming messages from clients and parses different message types such as join requests, move commands, and chat messages.
* **Send Messages to Server**: Implement the ability to send detailed messages to the server, parse server responses, and provide feedback to the user about any errors.
* **Handle Client Connections and Disconnections**: Implemented mechanisms to manage client connections and disconnections, keep track of connected clients, and inform other clients when a player joins or leaves the game.

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
