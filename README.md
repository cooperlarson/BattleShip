# BattleShip
Python implementation of BattleShip for 2 players using sockets.

<img src="https://t3.ftcdn.net/jpg/05/92/31/70/360_F_592317043_rOOpTliZqnmqLi3YwWxGIgVyyfk5nMaM.jpg" width=100% />

# How to play:

## Ensure you are using Python 3.10 or later.
```bash
python3 --version
```

## On the school systems, Python 3.10 can be loaded with the following command:
```bash
module load python/anaconda
```

## Install the required packages:
```bash
pip install -r requirements.txt
```

## Start the server:
```bash
python3 server.py  # Default port is 29999, default host is localhost

# To specify a port:
python3 server.py -p 30000  # Port 30000

# To specify a host:
python3 server.py -i 0.0.0.0  # Host
```

## Connect clients:
##### Client port argument must match the server port argument. Clients are dynamically assigned a port by the server.
```bash
python3 client.py  # Default port is 29999

# To specify a port:
python3 client.py -p 30000  # Port 30000
```

## Enter your name when prompted:
`Welcome to Battleship! Please enter your name:`

## The game will begin once both players have connected.
`Position your ships!`

## Commands:
```bash
Available Commands:
  move [x] [y] - Make a move at the specified coordinates (e.g., move 3 5)
  chat [message] - Send a chat message to your opponent
  view - View the current state of the game board
  quit - Quit the current game

```

### Play the game:
* Each player positions their battleships using the command line.
  * Position with coordinates (row, column) and orientation (horizontal or vertical).
  * Position randomly by typing `random`.
  * Position for demo by typing `demo`. This will advance the board to a late game three-hits to win scenario.
* The game starts.
* Players take turns targeting chosen coordinates, attempting to sink each others ships.
* The first player to eliminate all their opponents ships wins the game!

## Technologies Used:
* Python
* Sockets

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

# Sprint 3
* **Refactor Codebase**: Refactored the codebase to improve readability, maintainability, and scalability.
* **Simplified Message Handling**: Simplified message handling by using action based messages.

# Sprint 4

## Deliverables:
* **Winning Condition**: Implement the winning condition for the game.
* **Command Line Arguments**: Add command line arguments to the server and client for specifying the host and port.
* **User Interface**: Expand the user interface to include more detailed information about the game state and player actions.

# Sprint 5

## Deliverables:
* **Error Handling**: Improved error handling and error messages for better user experience. Balanced use of decorators and try-except blocks.
* **Integration Testing**: Conducted integration testing to ensure the server and client work together as expected.
* **Security / Risk Evaluation**:
  * **Man-in-the-Middle Attack**: This game does not have the requisite handshake protocols safeguard against MITM attacks. This can be addressed by implementing a secure certificate based handshake protocol.
  * **Source Spoofing**: The game does not have any source spoofing protection. This can be addressed by implementing a secure handshake protocol.
  * **Denial of Service (DoS) Attack**: The game is vulnerable to DoS attacks. This can be addressed by implementing rate limiting and connection throttling.
  * **Code Injection**: The game is vulnerable to code injection attacks. This can be addressed by validating user input and using secure serialization methods.

  
# Project Roadmap
##### I could foresee further development of this project in the following directions:
* **GUI Implementation**: Develop a graphical user interface for the game to enhance the user experience.
* **Refine Existing Features**: Improve the existing features and functionalities of the game, such as adding a rematch option or re-entering the match queue.
* **Add More Game Modes**: Implement additional game modes, such as a single-player mode against AI or a tournament mode.
* **Enhance Security**: Improve the security of the game by implementing secure communication protocols and input validation.
* **Potential ML Tournament**: Organize a machine learning tournament where AI agents play against each other in the game of Battleship, with boards of 1000x1000 or larger and fleets of 15-20 ships with variant munition calibers.

# Retrospective:
* **What went well?**:
  * Successfully implemented the core functionality of the game.
  * Developed a robust communication protocol for client-server interactions.
  * Learned a lot about socket programming and message serialization.
* **What could have gone better?**:
  * A GUI could have been implemented to enhance the user experience.
  * More comprehensive error handling, testing, and logging could have been implemented.
  * Additional features such as rematch or re-enter match queue could have been added.

###

## Additional Resources:
* [Getting started with Python](https://www.python.org/about/gettingstarted/)

***Additional documentation coming soon***
