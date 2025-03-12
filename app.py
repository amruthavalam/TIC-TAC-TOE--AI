from flask import Flask, request, jsonify, render_template
import numpy as np

app = Flask(__name__)

# Constants
HUMAN = 'X'
AI = 'O'
EMPTY = ' '

# Initialize board
def create_board():
    return [[EMPTY] * 3 for _ in range(3)]

board = create_board()

# Check if there is a winner
def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != EMPTY:
            return row[0]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]

    return None

# Check if board is full
def is_full(board):
    return all(cell != EMPTY for row in board for cell in row)

# Get available moves
def available_moves(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == EMPTY]

# Minimax Algorithm with Alpha-Beta Pruning
def minimax(board, depth, is_maximizing, alpha, beta):
    winner = check_winner(board)
    if winner == AI:
        return 10 - depth
    elif winner == HUMAN:
        return depth - 10
    elif is_full(board):
        return 0

    if is_maximizing:
        max_eval = -float('inf')
        for r, c in available_moves(board):
            board[r][c] = AI
            eval_score = minimax(board, depth + 1, False, alpha, beta)
            board[r][c] = EMPTY
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for r, c in available_moves(board):
            board[r][c] = HUMAN
            eval_score = minimax(board, depth + 1, True, alpha, beta)
            board[r][c] = EMPTY
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

# AI Move
def best_move():
    best_score = -float('inf')
    move = None
    for r, c in available_moves(board):
        board[r][c] = AI
        move_score = minimax(board, 0, False, -float('inf'), float('inf'))
        board[r][c] = EMPTY
        if move_score > best_score:
            best_score = move_score
            move = (r, c)
    return move

# API Routes
@app.route('/')
def index():
    return render_template('index.html')  # Load the HTML file

@app.route('/move', methods=['POST'])
def make_move():
    global board
    data = request.get_json()
    row, col = data['row'], data['col']

    if board[row][col] == EMPTY:
        board[row][col] = HUMAN
        if check_winner(board):
            return jsonify({"board": board, "winner": HUMAN})
        elif is_full(board):
            return jsonify({"board": board, "winner": "Draw"})

        ai_row, ai_col = best_move()
        board[ai_row][ai_col] = AI
        if check_winner(board):
            return jsonify({"board": board, "winner": AI})
        elif is_full(board):
            return jsonify({"board": board, "winner": "Draw"})

        return jsonify({"board": board, "winner": None})
    else:
        return jsonify({"error": "Invalid move!"})

@app.route('/reset', methods=['GET'])
def reset_board():
    global board
    board = create_board()
    return jsonify({"message": "Board reset!"})

if __name__ == '__main__':
    app.run(debug=True)

