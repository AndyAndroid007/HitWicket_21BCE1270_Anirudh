  

Game README

 Overview

This game is a turn-based strategy game implemented using Flask and Flask-SocketIO. It features two players with different types of characters moving on a 5x5 board. The game updates in real-time using WebSockets, and the game state is synchronized between the clients.

 Features

- Real-Time Updates: The game uses WebSockets to provide real-time updates to all connected clients.
- Two Players: Each player controls a set of characters with different movement capabilities.
- Turn-Based Mechanics: The game alternates turns between players.
- Character Movement: Different characters have unique movement patterns.
- Capture Mechanics: Characters can capture opponent's pieces.
- Game Over Detection: The game detects when a player has no pieces left and announces the winner.

 Requirements

- Python 3.7 or higher
- Flask
- Flask-SocketIO

 Installation

1. Clone the repository:
   `git clone <repository-url>`
   `cd <repository-directory>`

2. Create a virtual environment:
   `python -m venv venv`
   `source venv/bin/activate`  (On Windows, use `venv\Scripts\activate`)

3. Install the dependencies:
   `pip install flask flask-socketio`

 Running the Game

1. Start the Flask application:
   `python app.py`

2. Open your web browser and navigate to `http://localhost:5000` to start playing.

 Game Mechanics

 Initialization

- The game is initialized with two players, "A" and "B".
- Player "A" starts with characters at positions `(0,0)` to `(0,4)` and Player "B" starts with characters at positions `(4,0)` to `(4,4)`.

 Available Moves

- Pawns (P1, P2, P3): Can move left (L), right (R), forward (F), or backward (B).
- Hero1 (H1): Can move two squares left (L), right (R), forward (F), or backward (B).
- Hero2 (H2): Can move diagonally in all four directions.

 Move Validation

- Moves are validated based on the character's type and current position.
- Moves that go out of bounds or land on occupied cells by the same player are invalid.

 Game State

- The board state and player turns are managed in the `game_state` dictionary.
- The game ends when a player has no pieces left.



 Development

- Debugging: The Flask application is run with `debug=True` for development purposes.
- Configuration: The `SECRET_KEY` is set to `'your_secret_key'` and should be updated for production environments.

 
