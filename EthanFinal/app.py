# <> Steps to Run Program <>
# 1: install requirements.txt
# 2: run app.py
# 3: open "localhost:5000" in your browser
# 4: play against the chess AI!

from flask import Flask, render_template, redirect
from flask_socketio import SocketIO, emit
from ai import ChessAI
import random
import chess

# flask and socketIO objects
app = Flask("Basic Chess UI")
socket_io = SocketIO(app)


# current chess game and ai
board = chess.Board()
ai = ChessAI(chess.WHITE, board)


# return the state of the board
def get_sate():
    if board.is_stalemate():
        return "stalemate"
    elif board.is_insufficient_material():
        return "insufficient_material"
    elif board.can_claim_threefold_repetition():
        return "threefold"
    elif board.can_claim_fifty_moves():
        return "fifty_moves"
    elif board.is_fivefold_repetition():
        return "fivefold"
    elif board.is_seventyfive_moves():
        return "seventyfive_moves"
    elif board.is_checkmate():
        return "checkmate"
    else:
        return "none"


@app.route("/")
def index():
    return redirect("/random")


@app.route("/<color>")
def play(color: str):
    global ai

    # reset the board
    board.set_board_fen(chess.STARTING_BOARD_FEN)

    # randomly pick a color if none was specified
    if color not in ["white", "black"]:
        color = random.choice(["white", "black"])

    # reset AI
    if color.lower() == "white":
        ai = ChessAI(chess.BLACK, board)
    elif color.lower() == "black":
        ai = ChessAI(chess.WHITE, board)

    return render_template("player-ai.html", data={
        "fen": board.fen(),
        "player": {
            "color": "b" if ai.color == chess.WHITE else "w"
        },
        "ai": {
            "color": "w" if ai.color == chess.WHITE else "b"
        }
    })


# make a move as the player
@socket_io.on('move')
def player_move(data):
    # create a move object from the source and destination information
    move = chess.Move.from_uci(data["move"]["source"] + data["move"]["target"])
    move.promotion = chess.QUEEN

    # try move with promotion
    if move in board.legal_moves:
        board.push(move)
    else:
        # remove promotion
        move.promotion = None

        # make move
        board.push(move)

    # emit the new fen
    emit("fen", board.fen())

    # emit sate
    emit("state", get_sate())


# return the fen
@socket_io.on('get')
def get_fen():
    # emit the fen
    emit("fen", board.fen())

    # emit sate
    emit("state", get_sate())


# have the ai make a move
@socket_io.on('ai_move')
def ai_move():
    if board.is_game_over():
        # emit the new fen
        emit("fen", board.fen())

        # emit sate
        emit("state", get_sate())
        return

    # if it is not the AI's turn to move skip and ignore the move command
    if board.turn != ai.color:
        return

    # get the ai move
    move = ai.get_move()

    try:
        # make the move
        board.push(move)
    # if the move the AI made is illegal then make a dummy move to prevent crashing
    except AttributeError:
        board.push(list(board.legal_moves)[0])

    # emit the new fen
    emit("fen", board.fen())

    # emit sate
    emit("state", get_sate())


# run if main
if __name__ == "__main__":
    socket_io.run(app, "0.0.0.0", 5000)
