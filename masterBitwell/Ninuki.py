#!/usr/bin/python3
# Set the path to your python3 above

"""
Go0 random Go player
Cmput 455 sample code
Written by Cmput 455 TA and Martin Mueller
"""
from gtp_connection import GtpConnection, format_point, point_to_coord
from board_base import DEFAULT_SIZE, GO_POINT, GO_COLOR
from board import GoBoard
from board_util import GoBoardUtil
from engine import GoEngine
import time
import random
from flat_monte_carlo import SimulationPlayer
from policy_player import PolicyPlayer
from typing import List, Tuple
import traceback

from board_base import (
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    GO_COLOR, GO_POINT,
    PASS,
    MAXSIZE,
    coord_to_point,
    opponent
)


class ABPlayer(GoEngine):
    def __init__(self) -> None:
        """
        Ninuki player which uses basic iterative deepening alpha-beta search.
        Many improvements are possible.
        """
        GoEngine.__init__(self, "Go0", 1.0)
        self.time_limit = 1


    def get_move(self, board: GoBoard, color: str) -> GO_POINT:
        start_time = time.time()
        if board.isGameOver():
            return "resign"
        if board.get_empty_points().size == 0:
            return "pass"
        if color == 'w':
            board.current_player = WHITE
        else:
            board.current_player = BLACK
        
        #can't let opponent make open fours with both ends open - guaranteed win

        strongOpeningMove = self.strongOpening(board, board.current_player)
        if strongOpeningMove != None:
            log_to_file('Strong opening move: '+strongOpeningMove+'\n')
            print('Strong opening move: '+strongOpeningMove)
            assert(board.get_color(move_to_point(strongOpeningMove, board.size)) == EMPTY)
            return strongOpeningMove

        MonteCarloMove = SimulationPlayer().genmove(board, board.current_player)
        timeStamp1 = time.time()
        #log_to_file('MonteCarlo took: '+str(timeStamp1-start_time) + '\n')

        if MonteCarloMove != None:
            print("MonteCarloMove: "+format_point(point_to_coord(MonteCarloMove, board.size)).lower())
            log_to_file("MonteCarloMove: "+format_point(point_to_coord(MonteCarloMove, board.size)).lower()+'\n')
            assert(board.get_color(MonteCarloMove) == EMPTY)
            return format_point(point_to_coord(MonteCarloMove, board.size)).lower()
        else:
            winner, move = self.solve_board(board)
            timeStamp2 = time.time()
            log_to_file("AlphabetaMove\n")
            #log_to_file('Alphabeta took:'+ str(timeStamp2-timeStamp1) + '\n')
            return format_point(point_to_coord(self.best_move, board.size)).lower()

    def alpha_beta(self, alpha, beta, depth):
        if time.time() - self.solve_start_time > (self.time_limit - 0.01):
            return 0, False, True

        is_terminal, winner = self.board.is_terminal()
        if is_terminal:
            if winner == self.board.current_player:
                return 1, True, False
            elif winner == opponent(self.board.current_player):
                return -1, True, False
            else:
                return 0, True, False
        #log_to_file('Depth:'+str(depth)+'\n')
        if depth >= self.max_depth:
            return 0, False, False

        any_unsolved = False
        # implement move ordering with policyMoves
        #moves = GoBoardUtil.generate_legal_moves(self.board, self.board.current_player)

        # can order moves so that moves close to the centre are favored
        moves = list(self.board.get_empty_points())
        
        if depth == 0:
            random.shuffle(moves)
        #log_to_file(str(moves)+'\n')
        policy_moves = PolicyPlayer().get_all_policy_moves(self.board, self.board.current_player)

        if len(policy_moves) > 0:
            moves = policy_moves #+ list(set(moves).difference(set(policy_moves)))
            #log_to_file(str(moves)+'\n')
        
        for move in moves:
            self.board.play_move(move, self.board.current_player)
            
            value, solved, timeout = self.alpha_beta(-beta, -alpha, depth+1)
            self.board.undo()
            value = -value

            if timeout:
                return 0, False, True
            
            if not solved:
                any_unsolved = True

            if value > alpha:
                alpha = value
                if depth == 0:
                    self.best_move = move

            if solved and value == 1:
                return 1, True, False

            if value >= beta:
                return beta, True, False
        
        return alpha, not any_unsolved, False

    def solve_board(self, board):
        self.solve_start_time = time.time()
        self.board = board.copy()
        self.tt = {}
        if self.board.get_empty_points().size == 0:
            self.best_move = PASS
        else:
            self.best_move = self.board.get_empty_points()[0]

        solved = False
        timeout = False
        self.max_depth = 1
        while not solved and not timeout:
            result, solved, timeout = self.alpha_beta(-1, 1, 0)
            self.max_depth += 1
        
        if timeout:
            return "unknown", None
        elif result == 1:
            if self.board.current_player == BLACK:
                return "b", format_point(point_to_coord(self.best_move, self.board.size)).lower()
            else:
                return "w", format_point(point_to_coord(self.best_move, self.board.size)).lower()
        elif result == -1:
            if self.board.current_player == BLACK:
                return "w", None
            else:
                return "b", None
        else:
            return "draw", format_point(point_to_coord(self.best_move, self.board.size)).lower()

    def set_time_limit(self, time_limit):
        self.time_limit = time_limit

    def strongOpening(self, board: GoBoard, color: GO_COLOR):
        strongSquence = ['d4', 'd3', 'd5', 'c4', 'e4', 'c3', 'e5', 'c5', 'e3']
        if PolicyPlayer().urgentMove(board, color):
            return None
        if len(board.get_empty_points()) - board.get_captures(BLACK) - board.get_captures(WHITE)>= 35:
            for i in range(len(strongSquence)):
                if board.get_color(move_to_point(strongSquence[i], board.size)) == EMPTY:
                    if i >= 2:
                        if board.get_color(move_to_point(strongSquence[i-1], board.size)) == color:
                            return strongSquence[i]
                        else:
                            continue
                    else:
                        return strongSquence[i]
        return None
            
def move_to_point(move: str, size: int) -> GO_POINT:
    coord = move_to_coord(move, size)
    return coord_to_point(coord[0], coord[1], size)

def run() -> None:
    """
    start the gtp connection and wait for commands.
    """
    board: GoBoard = GoBoard(DEFAULT_SIZE)
    con: GtpConnection = GtpConnection(ABPlayer(), board)
    con.start_connection()

def log_to_file(content: str) -> None:
    # Open the file in append mode ('a')
    file_path = 'profiling.txt'
    with open(file_path, 'a') as file:
        # Write content to the file
        file.write(content)

def move_to_coord(point_str: str, board_size: int) -> Tuple[int, int]:
    """
    Convert a string point_str representing a point, as specified by GTP,
    to a pair of coordinates (row, col) in range 1 .. board_size.
    Raises ValueError if point_str is invalid
    """
    if not 2 <= board_size <= MAXSIZE:
        raise ValueError("board_size out of range")
    s = point_str.lower()
    if s == "pass":
        return (PASS, PASS)
    try:
        col_c = s[0]
        if (not "a" <= col_c <= "z") or col_c == "i":
            raise ValueError
        col = ord(col_c) - ord("a")
        if col_c < "i":
            col += 1
        row = int(s[1:])
        if row < 1:
            raise ValueError
    except (IndexError, ValueError):
        raise ValueError("wrong coordinate")
    if not (col <= board_size and row <= board_size):
        raise ValueError("wrong coordinate")
    return row, col

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log_to_file(traceback.format_exc())
