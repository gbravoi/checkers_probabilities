"""
Martin Kersner, m.kersner@gmail.com
seoulai.com
2018
Adapted by Gabriela B. to work with python 2.7 and ROS
"""


from base import Constants
from base import Piece
import rospy #to print debug info


class Rules(object):
    @staticmethod
    def get_opponent_type(ptype) :
        """Get a type of opponent agent.

        Note: In checkers there is only one pair of agents competing with each other.

        Args:
            ptype: Type of piece.

        Returns:
            opponent_type: Type of opponent agent.
        """
        if ptype == Constants().DARK:
            opponent_type = Constants().LIGHT
        else:
            opponent_type = Constants().DARK

        return opponent_type

    @staticmethod
    def get_positions(
        board_list,
        ptype,
        board_size) :
        """Get positions of all pices of given type in given board.

        Args:
            board_list: Information about positions of pieces.
            ptype: Type of piece.
            board_size:

        Returns:
            positions: Positions of pieces for given agent type in given board.
        """
        positions = []

        for row in range(board_size):
            for col in range(board_size):
                pos = board_list[row][col]
                if pos is not None and pos.ptype == ptype:
                    positions.append((row, col))

        return positions

    @staticmethod
    def get_valid_moves_simple(
        board_list,
        from_row,
        from_col) :
        """Generate valid moves for given position with respect to the current state of game.
        simple: move one square

        Args:
            board_list: Information about positions of pieces.
            from_row: Row of board of piece location.
            from_col: Column of board of piece location.

        Returns:
            List of (row, column) tuples representing valid moves for given piece location at current
            state of board.
        """
        def validate_move_wrapper(to_row_col):
            return Rules.validate_move(board_list, from_row, from_col, *to_row_col)

        return list(filter(validate_move_wrapper, Rules.generate_all_moves_simple(from_row, from_col)))

    @staticmethod
    def get_valid_moves_jump(
        board_list,
        from_row,
        from_col) :
        """Generate valid moves for given position with respect to the current state of game.
        simple: move one square

        Args:
            board_list: Information about positions of pieces.
            from_row: Row of board of piece location.
            from_col: Column of board of piece location.

        Returns:
            List of (row, column) tuples representing valid moves for given piece location at current
            state of board.
        """
        def validate_move_wrapper(to_row_col):
            return Rules.validate_move(board_list, from_row, from_col, *to_row_col)

        return list(filter(validate_move_wrapper, Rules.generate_all_moves_jump(from_row, from_col)))

    @staticmethod
    def generate_valid_moves(
        board_list,
        ptype,
        board_size) :
        """Get all possible valid moves for agent of given type.

        Args:
            board_list: Information about positions of pieces.
            ptype: Type of piece.
            board_size:

        Returns:
            moves: Dictionary with keys tuple(row, col) of pieces with at least one valid move. Values
                of dictionary are represented as a list of tuples as a new valid piece coordinates.
        """
        moves = {}
        double_moves={}
        positions = Rules.get_positions(board_list, ptype, board_size)

        for row, col in positions:
            temp_moves_jump = Rules.get_valid_moves_jump(board_list, row, col)
            if len(temp_moves_jump) > 0:#first find jumps, if there are jumps, do not look for simple moves
                double_moves[(row, col)] = temp_moves_jump
            elif len(double_moves)==0:
                temp_moves = Rules.get_valid_moves_simple(board_list, row, col)
                if len(temp_moves) > 0:
                    moves[(row, col)] = temp_moves

        #add rule: when you can jump a piece, you must do it
        if len(double_moves)>0:
            return double_moves
        return moves

    @staticmethod
    def validate_move(
        board_list,
        from_row,
        from_col,
        to_row,
        to_col) :
        """Validate move given by current and desired piece coordinates.

        Args:
            board_list: Information about positions of pieces.
            from_row: Row of board of original piece location.
            from_col: Column of board of original piece location.
            to_row: Cow of board of desired piece location.
            to_col: Column of board of desired piece location.

        Returns:
            True if given move is valid, otherwise false.
        """
        # not among available moves
        if( (to_row, to_col) not in Rules.generate_all_moves_simple(from_row, from_col)) and ((to_row, to_col) not in Rules.generate_all_moves_jump(from_row, from_col)):
            return False

        # can't move piece from outside of board
        if from_row < 0 or from_col < 0 or from_row > 7 or from_col > 7:
            return False

        # cant move out of board
        if to_row < 0 or to_col < 0 or to_row > 7 or to_col > 7:
            return False

        # target square must be empty
        if board_list[to_row][to_col] is not None:
            return False

        # can't move empty square
        p = board_list[from_row][from_col]
        if p is None:
            return False

        # cant move in opposite direction, except king
        if p.direction == Constants().UP and from_row < to_row and not p.king:
            return False

        if p.direction == Constants().DOWN and from_row > to_row and not p.king:
            return False

        # cant jump over itself or empty square
        between_row, between_col = Rules.get_between_position(from_row, from_col, to_row, to_col)
        if between_row is not None and between_col is not None:
            pp = board_list[between_row][between_col]
            if pp is None or pp.ptype == p.ptype:
                return False

        return True
    
    @staticmethod
    def check_was_jump(board_list, from_row, from_col, to_row, to_col):
        """
        Check if the movement is jump over an enemy piece
        (asuming from is a piece of the current player)
        return boolean
        """
        # rospy.loginfo('from (%s ,%s), to: (%s , %s)',from_row,from_col,to_row,to_col)
        #current player
        p = board_list[from_row][from_col]
        between_row, between_col = Rules.get_between_position(from_row, from_col, to_row, to_col)
        if between_row is not None and between_col is not None:
            pp = board_list[between_row][between_col]
            if pp is not None and pp.ptype != p.ptype:
                return True

        return False

    @staticmethod
    def check_jump_is_possible(board_list, to_row, to_col):
        """
        check if more jump movements are  posible from where the piece landed
        """
        new_from_row=to_row
        new_from_col=to_col
        #check if there are valis jumps
        jumps_list=Rules.get_valid_moves_jump(board_list, new_from_row, new_from_col)#valid jumps where it landed
        return len(jumps_list)>0



    @staticmethod 
    def check_valid_move(board_list, ptype,from_row, from_col, to_row,to_col):
        """
        Check if movement is valid, and is being performed with current user checker
        """
        # don't move with opponent's piece
        if ptype != board_list[from_row][from_col].ptype:
            return False

        #check if movement is valid
        return Rules.validate_move(board_list, from_row, from_col, to_row, to_col)
    
    @staticmethod
    def check_become_king(board_list, to_row,to_col,UP=Constants().UP,DOWN=Constants().DOWN,size=8):
        """
        Check if the new position of the checker is to be a king
        size: how many cell has the board
        UP, DOWN. Numerical representation to up and down directions.
        """
        p = board_list[to_row][to_col]
        return (to_row == 0 and p.direction == UP) or (to_row == size-1 and p.direction == DOWN)

    @staticmethod
    def check_end_game(board_list,ptype, board_size):
        """
        check if end of game
        ptype= type of current player
        """
        opponent_ptype=Rules.get_opponent_type(ptype)
        #openent lost all his pieces?
        oponent_no_pieces= len(Rules.get_positions(board_list, opponent_ptype, board_size)) == 0
        if oponent_no_pieces:
            return True
        
        #check if oponent can move
        oponent_cant_move=len(Rules.generate_valid_moves(board_list, opponent_ptype, board_size)) == 0
        if oponent_cant_move:
            return True

        return False
        




    @staticmethod
    def get_between_position(
        from_row,
        from_col,
        to_row,
        to_col) :
        """Get position of square over which was move performed.

        Args:
            board_list: Information about positions of pieces.
            from_row: Row of board of original piece location.
            from_col: Column of board of original piece location.
            to_row: Row of board of desired piece location.
            to_col: Column of board of desired piece location.

        Returns:
            Position of sqaure expressed by tuple(row, col) if length of move was 2, otherwise
            tuple(None, None).
        """
        if abs(from_row-to_row) == 2 and abs(from_col-to_col) == 2:
            if from_row-to_row > 0:  # UP
                if from_col-to_col > 0:  # LEFT
                    return from_row-1, from_col-1
                else:  # RIGHT
                    return from_row-1, from_col+1
            else:  # DOWN
                if from_col-to_col > 0:  # LEFT
                    return from_row+1, from_col-1
                else:  # RIGHT
                    return from_row+1, from_col+1
        else:
            return None, None

    @staticmethod
    def generate_all_moves_simple(
        from_row,
        from_col) :
        """Generate all moves for given board position. Some moves can be invalid.

        Args:
            from_row: Row of board of piece location.
            from_col: Column of board of piece location.

        Returns:
            moves: Generated moves for given position.
        """
        moves = [
            (from_row-1, from_col-1),
            (from_row+1, from_col-1),
            (from_row-1, from_col+1),
            (from_row+1, from_col+1),
        ]

        return moves


    @staticmethod
    def generate_all_moves_jump(
        from_row,
        from_col ) :
        """Generate all moves for given board position. Some moves can be invalid.

        Args:
            from_row: Row of board of piece location.
            from_col: Column of board of piece location.

        Returns:
            moves: Generated moves for given position.
        """
        moves = [
            (from_row-2, from_col-2),
            (from_row+2, from_col-2),
            (from_row-2, from_col+2),
            (from_row+2, from_col+2),
        ]

        return moves
