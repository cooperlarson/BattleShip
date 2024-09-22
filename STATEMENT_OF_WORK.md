# Statement of Work (SOW) for Socket Programming Project

## Project Title:
### BattleShip

## Team:
* Cooper Larson

## Project Objective:
The goal of this project is to enhance my working knowledge of sockets and build a functional 2-player remote battleship game complete with sockets for asynchronous communication. If time permits, adding additional game functionality and graphic capabilities is a bonus goal.

## Scope:

### Inclusions:
* A web server that supports socket communication between 2 clients supported by a shared server.
* A functional game of battleship.

### Exclusions:
* Graphical User Input or display.
* Global matchmaking.
* Other general that would make battlefield more engaging but are expensive to implement.

## Deliverables:
* Python game + web socket server script.
* Python client script for initiating game with another player on the server.
* Robust documentation to assist the end user in hosting their own battleship server with sockets.

## Timeline:

### Key Milestones:
* Testable server code (10/01/24)
* Working game logic (10/7/24)
* Working client communication with server (10/14/24)
* Working client communication with server + game logic (11/1/24)
* Thorough testing, debugging, optimization, and product delivery (12/1/24)

### Task Breakdown:
* Write the server code to facilitate client communication with a shared host (10/1/24)
* Write initial game logic (10/7/24)
* Integrate the game logic into the server (10/14/24)
* Write the client game socket scripts (10/21/24)
* Test the server client socket integration (11/1/24)

## Technical Requirements:

### Hardware:
* 2 client devices with properly configured LAN or WAN network communication link
* Optional: a dedicated host device / server

### Software:
* Languages
  * Python
* Libraries
  * Socket
  * Threading
* OS
  * Supports all major operating systems that support Python

## Assumptions:
* There is a routable link via some network trace which supports TCP protocol between the 2 devices and the server.
* There are no firewall rules in place preventing TCP communication from completing on the configured port(s).

## Roles and Responsibilities
* **Cooper Larson**:
  * Roles:
    * Project Manager
    * Software Architect
    * Lead Engineer
    * Junior Network Engineer
    * System Administrator
    * Senior Test Engineer
  * Responsibilities:
    * Coordinate team efforts on the project.
    * Design the software according to project specifications using industry-standard design processes.
    * Write the code.
    * Apply knowledge of sockets and networking to create a seamless connection interface between client devices and a game server using TCP.
    * Write thorough tests, applying the principles of Test Driven Development in key areas to deliver robust, self-documented code.
   
## Communication Plan (solo team)
* I will check in with myself on a regular basis to ensure the project makes regular progress.

## Additional Notes:
* If I finish early enough I have some cool ideas planned for potentially expanded gameplay capabilities.
