from board import GoBoard
from board_util import GoBoardUtil
from typing import List, Tuple
from engine import GoEngine
import random
from policy_player import PolicyPlayer
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

class SimulationPlayer(object):
    def __init__(self):
        self.numSimulations = 10

    def genmove(self, board: GoBoard, player, policy):
        '''
            1. Generate a list of all legal moves
            2. Simulate 10 games for each legal move
            3. Pick highest winrate
            4. Player resigns or passes when the game is over
            5. Returns the best move
        '''
        # Get all legal moves and put it into a list 
        if policy == 'random':
            legal_moves = board.get_empty_points()
        else:
            _, policy_moves =  PolicyPlayer().get_policy_moves(board, player, policy)
            legal_moves = [coord_to_point(move_to_coord(move, board.size)[0], move_to_coord(move, board.size)[1], board.size) for move in policy_moves]
        if len(legal_moves) == 0:
            print('No legal moves left. Yield')
            return 'Yield'
        
        # Simulate each legal move and assign a value
        score = [0] * len(legal_moves)
        for i in range(len(legal_moves)):
            move = legal_moves[i]
            #print(format_point(point_to_coord(move, board.size)))
            score[i] = self.simulate(board, move, player, policy)
            #print(score[i])
        
        # Get the best score
        bestIndex = score.index(max(score))
        best = legal_moves[bestIndex]
        return best

    def simulate(self, board: GoBoard, move, player, policy):
        '''
            Runs the number of simulations specified in numSimulations
            Returns the evaluation of the results
            Utilizes helper function simulate1 for each simulation
        '''
        stats = [0] * 3
        
        board_copy1 = board.copy()
        board_copy1.play_move(move, player)
        for _ in range(self.numSimulations):
            board_copy2 = board_copy1.copy()
            winner = self.simulate1(board_copy2, policy)
            stats[winner] += 1
            #board = board_copy2

        #board = board_copy1
        assert sum(stats) == self.numSimulations
        #print(stats)
        eval = (stats[player] + 0.5 * stats[EMPTY]) / self.numSimulations
        #print(eval)
        return eval
    
    def simulate1(self, board: GoBoard, policy):
        '''
            Completes 1 simulation until end state using random rules
        '''
        if policy == 'random':
            while not board.isGameOver():
                move = random.choice(board.get_empty_points())
                #print(move)
                board.play_move(move, board.current_player)
        else:
            
            while not board.isGameOver():
                _, policy_moves =  PolicyPlayer().get_policy_moves(board, board.current_player, policy)
                #print(policy_moves)
                moves = [coord_to_point(move_to_coord(move, board.size)[0], move_to_coord(move, board.size)[1], board.size) for move in policy_moves]
                move = random.choice(moves)
                #print(move)
                board.play_move(move, board.current_player)
        #print(board.current_player)
        #print(GoBoardUtil.get_twoD_board(board))
        return board.evalEndState()
    
#==============================================================================================
# Copied here for easy use
#==============================================================================================

def point_to_coord(point: GO_POINT, boardsize: int) -> Tuple[int, int]:
    if point == PASS:
        return (PASS, PASS)
    else:
        NS = boardsize + 1
        return divmod(point, NS)

def format_point(move: Tuple[int, int]) -> str:
    """
    Return move coordinates as a string such as 'A1', or 'PASS'.
    """
    assert MAXSIZE <= 25
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    if move[0] == PASS:
        return "PASS"
    row, col = move
    if not 0 <= row < MAXSIZE or not 0 <= col < MAXSIZE:
        raise ValueError
    return column_letters[col - 1] + str(row)

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
