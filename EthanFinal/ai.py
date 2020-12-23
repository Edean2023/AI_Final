import json
import chess
import random
from typing import List


# chess AI class
class ChessAI:
    def __init__(self, side_color: chess.Color, board: chess.Board, minimax_depth: int = 3):
        # the side color the AI is playing ass
        self.color = side_color

        # the board the AI is playing on
        self.board = board

        # minimax depth
        self.depth = minimax_depth

        # loads piece values
        with open("weights/fast_piece_values.json", "r") as piece_values_file:
            self.piece_values = json.load(piece_values_file)

            # fix some formatting
            self.piece_values[True] = self.piece_values["true"]
            self.piece_values[False] = self.piece_values["false"]

    # accesses a list of valid moves
    @property
    def valid_moves(self) -> List[chess.Move]:
        return list(self.board.legal_moves)

    # returns the # of pieces on the board
    @property
    def total_pieces(self) -> int:
        # get a list of pieces on the squares
        squares = [self.board.piece_at(square) for square in range(0, 64)]

        # filter out all None values and get the total # of pieces
        return len(list(filter(None, squares)))

    # calculates the score of a piece given the side color, piece, and board square
    def get_piece_score(self, side: chess.Color, piece: chess.Piece, square: int):
        # get the value from the modifier lookup table + the value of the piece
        value = self.piece_values[piece.color][piece.piece_type][square] + self.piece_values["values"][piece.piece_type]

        # return the value as a positive value if its color is the same as the side color
        if side == piece.color:
            return value
        # else return it as a negative value
        else:
            return value * -1

    # calculates the score advantage for a given side
    def calculate_score(self, side: chess.Color) -> int:
        # score tally
        score = 0

        # calculate the # of pieces on the board
        piece_count = self.total_pieces

        for square in range(0, 64):
            # get piece at square
            piece = self.board.piece_at(square)

            # if there is no piece skip
            if piece is None:
                continue

            # if there is more than 10 pieces on the board
            if piece_count > 12:
                score += self.get_piece_score(side, piece, square)

        return score

    # return the move the ai will make given the current board state
    def get_move(self) -> chess.Move:
        return self.minimax_root(self.depth)

    # root of minimax
    def minimax_root(self, depth: int = 3, is_maximizing: bool = True) -> chess.Move:
        # keep track of the best move and best core
        b_move = None
        b_score = -9999

        # keep track of a neutral score and move pool in case no good move is found
        n_score = self.calculate_score(self.color)
        n_moves = []

        # for each move in the legal move list perform minimax
        for move in self.board.legal_moves:
            # make the move
            self.board.push(move)

            # perform minimax
            score = self.minimax(depth - 1, not is_maximizing)

            # undo move
            self.board.pop()

            # if score is better than the best make it the new best
            if b_score <= score:
                b_move = move
                b_score = score
            elif score == n_score:
                n_moves.append(move)

        # if no best move was found then choose from one of the neutral moves
        if b_score == n_score:
            try:
                b_move = random.choice(n_moves)
            except IndexError:
                b_move = random.choice(self.valid_moves)

        # return the best move found
        return b_move

    # recursive minimax using alpha beta pruning
    def minimax(self, depth: int, is_maximizing: bool, alpha: int = -10000, beta: int = 10000) -> int:
        if depth == 0:
            return self.calculate_score(self.color)

        # if the move results in checkmate give lots of points
        if self.board.is_checkmate() and self.board.turn != self.color:
            return 10000 + self.calculate_score(self.color)

        # if the move results in draw add 50 points, draws are good
        if self.board.is_stalemate() and self.board.turn != self.color:
            return 50 + self.calculate_score(self.color)

        # if the move results in you getting checkmated take away lots of points
        if self.board.is_checkmate() and self.board.turn == self.color:
            return -10000 + self.calculate_score(self.color)

        # if it is maximizing for AI
        if is_maximizing:
            # keep track of the best score
            b_score = -9999

            for move in self.valid_moves:
                # make a move
                self.board.push(move)

                # check if the calculated score is higher than the current best score
                b_score = max(b_score, self.minimax(depth - 1, not is_maximizing, alpha, beta))

                # reverse the move
                self.board.pop()

                # beta pruning
                if b_score >= beta:
                    return b_score

                # calculate the new alpha
                alpha = max(alpha, b_score)

            # fallback return if no pruning occurs
            return b_score
        # minimizing for opponents
        else:
            # keep track of the best score
            b_score = 9999

            for move in self.valid_moves:
                # make a move
                self.board.push(move)

                # check if the calculated score is higher than the current best score
                b_score = min(b_score, self.minimax(depth - 1, not is_maximizing, alpha, beta))

                # reverse the move
                self.board.pop()

                # alpha pruning
                if b_score <= alpha:
                    return b_score
                beta = min(beta, b_score)

            # fallback return if no pruning occurs
            return b_score
