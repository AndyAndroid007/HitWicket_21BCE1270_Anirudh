const socket = io();


socket.on('game_state_update', function(gameState) {
    updateBoard(gameState.board);
    updateTurnStatus(gameState.players);
});


function updateBoard(board) {
    const boardElement = document.getElementById('board');
    boardElement.innerHTML = ''; 

    for (let row = 0; row < 5; row++) {
        for (let col = 0; col < 5; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell'; 
            const cellData = board[row][col];

            if (cellData) {
                cell.classList.add(`player${cellData.player}`);
                cell.textContent = cellData.name;
                cell.dataset.player = cellData.player;
                cell.dataset.charName = cellData.name;
                cell.dataset.row = row;
                cell.dataset.col = col;
                cell.addEventListener('click', handleCellClick);
            }

            boardElement.appendChild(cell);
        }
    }
}


function handleCellClick(event) {
    const cell = event.target;
    const cellData = cell.dataset;

    if (cellData.player) {
        
        document.querySelectorAll('.cell').forEach(c => c.classList.remove('selected'));
        
        
        cell.classList.add('selected');

        
        socket.emit('get_available_moves', {
            char_name: cellData.charName
        });
    }
}


socket.on('available_moves', function(availableMoves) {
    const moveButtonsElement = document.getElementById('move-buttons');
    moveButtonsElement.innerHTML = ''; 

    availableMoves.forEach(move => {
        const button = document.createElement('button');
        button.className = 'move-button';
        button.textContent = move;
        button.dataset.move = move;
        button.addEventListener('click', function() {
            const selectedCell = document.querySelector('.cell.selected');
            if (selectedCell) {
                const charName = selectedCell.dataset.charName;
                
                
                socket.emit('player_move', {
                    player_id: selectedCell.dataset.player,
                    char_name: charName,
                    move: button.dataset.move
                });

               
                button.disabled = true; 
                selectedCell.classList.add('moving');
                setTimeout(() => selectedCell.classList.remove('moving'), 500);
                
               
                selectedCell.classList.remove('selected');
            }
        });
        moveButtonsElement.appendChild(button);
    });
});


socket.on('invalid_move', function() {
    addGameMessage('Invalid move.');
});


socket.on('capture_message', function(data) {
    addGameMessage(data.message);
});


socket.on('game_over', function(data) {
    document.getElementById('game-status').innerText = `Game Over! Player ${data.winner} wins!`;
    document.getElementById('turn-status').innerText = ''; 
    addGameMessage(`Game Over! Player ${data.winner} wins!`);
});


function updateTurnStatus(players) {
    const currentPlayer = Object.keys(players).find(player => players[player].turn);
    document.getElementById('turn-status').innerText = `It's ${currentPlayer}'s turn.`;
}


function addGameMessage(message) {
    const gameMessagesDiv = document.getElementById('game-messages');
    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    gameMessagesDiv.appendChild(messageElement);

  
    gameMessagesDiv.scrollTop = gameMessagesDiv.scrollHeight;
}
