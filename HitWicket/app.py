from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Game state storage
game_state = {
    "players": {
        "A": {"characters": {}, "turn": True,"pieces_left": 5},
        "B": {"characters": {}, "turn": False,"pieces_left": 5}
    },
    "board": [[None]*5 for _ in range(5)]
}

def initialize_game():
    game_state["players"]["A"]["characters"] = {
        "A-P1": (0, 0), "A-H1": (0, 1), "A-H2": (0, 2), "A-P2": (0, 3), "A-P3": (0, 4)
    }
    game_state["players"]["B"]["characters"] = {
        "B-P1": (4, 0), "B-H1": (4, 1), "B-H2": (4, 2), "B-P2": (4, 3), "B-P3": (4, 4)
    }
    update_board()

def update_board():
    for row in range(5):
        for col in range(5):
            game_state["board"][row][col] = None
    for player, data in game_state["players"].items():
        for char_name, (row, col) in data["characters"].items():
            game_state["board"][row][col] = {"player": player, "name": char_name}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    initialize_game()
    emit('game_state_update', game_state)

@socketio.on('get_available_moves')
def handle_get_available_moves(data):
    char_name = data['char_name']
    available_moves = get_available_moves(char_name)
    emit('available_moves', available_moves)


@socketio.on('player_move')
def handle_player_move(data):
    player_id = data['player_id']
    char_name = data['char_name']
    move = data['move']

    if not validate_move(player_id, char_name, move):
        emit('invalid_move', {'error': 'Invalid move!'})
        return

    move_character(player_id, char_name, move)
    if check_game_over():
        emit('game_over', {'winner': 'A' if len(game_state["players"]["B"]["characters"]) == 0 else 'B'})
    else:
        emit('game_state_update', game_state, broadcast=True)

def get_available_moves(char_name):
    
    player_id = char_name.split('-')[0]
    row, col = game_state["players"][player_id]["characters"][char_name]
    char_type = char_name.split('-')[1]
    available_moves = []

    
    def is_in_bounds(r, c):
        return 0 <= r < 5 and 0 <= c < 5

    
    def is_valid_destination(r, c):
        if not is_in_bounds(r, c):
            return False
        cell_data = game_state["board"][r][c]
        if cell_data is None:
            return True  
        return cell_data["player"] != player_id  

    if char_type[0] == "P":
        
        if col > 0 and is_valid_destination(row, col - 1):  
            available_moves.append("L")
        if col < 4 and is_valid_destination(row, col + 1):  
            available_moves.append("R")
        if row > 0 and is_valid_destination(row - 1, col):  
            available_moves.append("F")
        if row < 4 and is_valid_destination(row + 1, col):  
            available_moves.append("B")
    
    elif char_type == "H1":
        # Hero1 moves
        if col >= 2 and is_valid_destination(row, col - 2):  
            available_moves.append("L")
        if col <= 3 and is_valid_destination(row, col + 2):  
            available_moves.append("R")
        if row >= 2 and is_valid_destination(row - 2, col): 
            available_moves.append("F")
        if row <= 3 and is_valid_destination(row + 2, col):  
            available_moves.append("B")
    
    elif char_type == "H2":
        # Hero2 diagonal moves
        if row >= 2 and col >= 2 and is_valid_destination(row - 2, col - 2):  
            available_moves.append("FL")
        if row >= 2 and col <= 3 and is_valid_destination(row - 2, col + 2):  
            available_moves.append("FR")
        if row <= 3 and col >= 2 and is_valid_destination(row + 2, col - 2): 
            available_moves.append("BL")
        if row <= 3 and col <= 3 and is_valid_destination(row + 2, col + 2): 
            available_moves.append("BR")
    
    return available_moves



def validate_move(player_id, char_name, move):
    if not game_state["players"][player_id]["turn"]:
        return False
    if char_name not in game_state["players"][player_id]["characters"]:
        return False

    row, col = game_state["players"][player_id]["characters"][char_name]
    char_type = char_name.split('-')[1]

    if char_type == "P1" or char_type == "P2" or char_type == "P3":
        return validate_pawn_move(row, col, move)
    elif char_type == "H1":
        return validate_hero1_move(row, col, move)
    elif char_type == "H2":
        return validate_hero2_move(row, col, move)
    return False

def validate_pawn_move(row, col, move):
    if move == "L" and col > 0:
        return True
    elif move == "R" and col < 4:
        return True
    elif move == "F" and row > 0:
        return True
    elif move == "B" and row < 4:
        return True
    return False

def validate_hero1_move(row, col, move):
    if move == "L" and col >= 2:
        if game_state["board"][row][col - 1] is None: 
            return True
    elif move == "R" and col <= 2:
        if game_state["board"][row][col + 1] is None: 
            return True
    elif move == "F" and row >= 2:
        if game_state["board"][row - 1][col] is None:  
            return True
    elif move == "B" and row <= 2:
        if game_state["board"][row + 1][col] is None:  
            return True
    return False

def validate_hero2_move(row, col, move):
    if move == "FL" and row >= 2 and col >= 2:
        if game_state["board"][row - 1][col - 1] is None:  
            return True
    elif move == "FR" and row >= 2 and col <= 2:
        if game_state["board"][row - 1][col + 1] is None: 
            return True
    elif move == "BL" and row <= 2 and col >= 2:
        if game_state["board"][row + 1][col - 1] is None: 
            return True
    elif move == "BR" and row <= 2 and col <= 2:
        if game_state["board"][row + 1][col + 1] is None: 
            return True
    return False


from flask_socketio import emit

def move_character(player_id, char_name, move):
    row, col = game_state["players"][player_id]["characters"][char_name]
    char_type = char_name.split('-')[1]
    new_row, new_col = row, col

   
    if char_type == "P1" or char_type == "P2" or char_type == "P3":
        if move == "L":
            new_col -= 1
        elif move == "R":
            new_col += 1
        elif move == "F":
            new_row -= 1
        elif move == "B":
            new_row += 1

    elif char_type == "H1":
        if move == "L":
            new_col -= 2
        elif move == "R":
            new_col += 2
        elif move == "F":
            new_row -= 2
        elif move == "B":
            new_row += 2

    elif char_type == "H2":
        if move == "FL":
            new_row -= 2
            new_col -= 2
        elif move == "FR":
            new_row -= 2
            new_col += 2
        elif move == "BL":
            new_row += 2
            new_col -= 2
        elif move == "BR":
            new_row += 2
            new_col += 2

   
    if 0 <= new_row < 5 and 0 <= new_col < 5:
        
        other_player = "A" if player_id == "B" else "B"
        if game_state["board"][new_row][new_col] is not None:
            if game_state["board"][new_row][new_col]["player"] == other_player:
                game_state["players"][other_player]["pieces_left"] -= 1
                emit('capture_message', {'message': f"{other_player} loses a piece! Pieces left for {other_player} : {game_state['players'][other_player]['pieces_left']}"},
                     broadcast=True)

        
        game_state["board"][row][col] = None
        game_state["board"][new_row][new_col] = {"player": player_id, "name": char_name}
        game_state["players"][player_id]["characters"][char_name] = (new_row, new_col)
        
        
        game_state["players"][player_id]["turn"] = False
        game_state["players"][other_player]["turn"] = True
        
        
        if game_state["players"][other_player]["pieces_left"] == 0:
            emit('game_over', {'winner': player_id}, broadcast=True)
        else:
            emit('game_state_update', game_state, broadcast=True)
            emit('game_message', {'message': f"It's {other_player}'s turn."}, broadcast=True)
        
        
        emit('game_message', {'message': f"{char_name} moved to position ({new_row}, {new_col})"}, broadcast=True)
    else:
        emit('invalid_move', broadcast=True)




def check_game_over():
    for player in game_state["players"]:
        if len(game_state["players"][player]["characters"]) == 0:
            return True
    return False

if __name__ == '__main__':
    socketio.run(app, debug=True)
