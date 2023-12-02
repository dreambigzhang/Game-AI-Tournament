from board import GoBoard
from board_util import GoBoardUtil
from typing import List, Tuple
from engine import GoEngine
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
"""
policy_moves
This command prints the set of moves considered by the simulation policy for the current player in the current position, in the format

= MoveType movelist 
Where MoveType is one of: {Win, BlockWin, OpenFour, Capture, Random}. Movelist is an alphabetically sorted list of moves (same sorting order as implemented in gogui-rules_legal_moves).
"""
class PolicyPlayer(object):
    def __init__(self):
        pass
    def get_policy_moves(self, board: GoBoard, color: GO_COLOR, policy):
        board_size = board.size
        if policy == 'random':
            return 'Random', scanRandom(board, color, board_size)
        winMoves = scanWin(board, color, board_size)
        if len(winMoves) > 0:
            return 'Win', winMoves
        blockWinMoves = scanBlockWin(board, color, board_size)
        if len(blockWinMoves) > 0:
            return 'BlockWin',blockWinMoves
        openFourMoves = scanOpenFour(board, color, board_size)
        if len(openFourMoves) > 0:
            return 'OpenFour', openFourMoves
        captureMoves = scanCapture(board, color, board_size)
        if len(captureMoves) > 0:
            return 'Capture', captureMoves
        return 'Random', scanRandom(board, color, board_size)

def scanWin(board: GoBoard, color, board_size):
    # scan for win moves
    winMoves = set()
    for point in board.get_empty_points():
        for noc in board.neighbors_of_color(point, color):
            direction = noc - point
            pos_direction_count = 1
            try:
                for i in range(2, 5):
                    if board.get_color(point+direction*i) == color:
                        pos_direction_count += 1
                    else:
                        raise Exception
            except:
                pass
            neg_direction_count = 1
            try:
                for i in range(1, 5):
                    if board.get_color(point-direction*i) == color:

                        neg_direction_count += 1
                    else:
                        raise Exception
            except:
                pass
            if pos_direction_count + neg_direction_count >= 5:
                isWinMove = True
            else:
                isWinMove = False
            if isWinMove:
                winMoves.add(format_point(point_to_coord(point,board_size)).lower())
    if board.get_captures(color)>=8:
        captureMoves = scanCapture(board, color, board_size)
        winMoves = winMoves.union(captureMoves)
    return sorted(winMoves)

def scanBlockWin(board: GoBoard, color, board_size):
    # scan for block win moves
    blockWinMoves = set()
    for point in board.get_empty_points():
        for noc in board.neighbors_of_color(point, opponent(color)):
            direction = noc - point
            pos_direction_count = 1
            try:
                for i in range(2, 5):
                    if board.get_color(point+direction*i) == opponent(color):
                        pos_direction_count += 1
                    else:
                        raise Exception
            except:
                pass
            neg_direction_count = 1
            try:
                for i in range(1, 5):
                    if board.get_color(point-direction*i) == opponent(color):
                        neg_direction_count += 1
                    else:
                        raise Exception
            except:
                pass
            if pos_direction_count + neg_direction_count >= 5:
                isBlockWinMove = True
            else:    
                isBlockWinMove = False

            if isBlockWinMove:
                blockWinMoves.add(format_point(point_to_coord(point,board_size)).lower())
    #print(blockWinMoves)
    # now scan open fours for the oppoenent and look for moves that capture them
    # make sure the fours are open fours not just any fours
    opponentOpenFour = board.getConsecutiveFours(opponent(color))
    #print(opponentOpenFour)
    captureOpenFourMoves = set()
    for point in board.get_empty_points():
        for noc in board.neighbors_of_color(point, opponent(color)):
            isCaptureOpenFourMove = True
            direction = noc - point
            try:
                if not (board.get_color(point+direction*2) == opponent(color) and board.get_color(point+direction*3) == color):
                    raise Exception
                #print("Black Capture Count", board.get_captures(color))
                #print("White Capture Count", board.get_captures(WHITE))
                #print("current player", color)
                if not (noc in opponentOpenFour or noc + direction in opponentOpenFour):
                    raise Exception
            except:
                isCaptureOpenFourMove = False

            if isCaptureOpenFourMove:
                captureOpenFourMoves.add(format_point(point_to_coord(point,board_size)).lower())
    if board.get_captures(opponent(color))>=8:
        captureMoves = scanCapture(board, opponent(color), board_size)
        blockWinMoves = blockWinMoves.union(captureMoves)
    return sorted(blockWinMoves.union(captureOpenFourMoves))

def scanOpenFour(board: GoBoard, color, board_size):
    # scan for open four moves
    openFourMoves = set()
    for point in board.get_empty_points():
        for noc in board.neighbors_of_color(point, color):
            direction = noc - point
            pos_direction_count = 1
            try:
                for i in range(2, 5):
                    if board.get_color(point+direction*i) == color:
                        pos_direction_count += 1
                    else:
                        raise Exception
            except:
                pass
            neg_direction_count = 1
            try:
                for i in range(1, 5):
                    if board.get_color(point-direction*i) == color:

                        neg_direction_count += 1
                    else:
                        raise Exception
            except:
                pass
            try:
                if pos_direction_count + neg_direction_count == 4 and (board.get_color(point+direction*pos_direction_count) == EMPTY or board.get_color(point-direction*neg_direction_count) == EMPTY):
                    isOpenFourMove = True
                else:
                    isOpenFourMove = False
            except:
                isOpenFourMove = False

            if isOpenFourMove:
                openFourMoves.add(format_point(point_to_coord(point,board_size)).lower() )
    return sorted(openFourMoves)

def scanCapture(board: GoBoard, color, board_size):
    captureMoves = set()
    for point in board.get_empty_points():
        for noc in board.neighbors_of_color(point, opponent(color)):
            isCaptureMove = True
            direction = noc - point
            try:
                if not (board.get_color(point+direction*2) == opponent(color) and board.get_color(point+direction*3) == color):
                    raise Exception
            except:
                isCaptureMove = False

            if isCaptureMove:
                captureMoves.add(format_point(point_to_coord(point,board_size)).lower() )
    return sorted(captureMoves)

def scanRandom(board: GoBoard, color, board_size):
    return sorted(format_point(point_to_coord(point,board_size)).lower() for point in board.get_empty_points())





def point_to_coord(point: GO_POINT, boardsize: int) -> Tuple[int, int]:
    """
    Transform point given as board array index 
    to (row, col) coordinate representation.
    Special case: PASS is transformed to (PASS,PASS)
    """
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

