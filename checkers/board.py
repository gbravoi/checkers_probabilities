"""
Martin Kersner, m.kersner@gmail.com
seoulai.com
2018
Adapted by Gabriela B. to work with python 2.7 and ROS
"""
 
import random
import rospy

from base import Constants
from base import DarkPiece
from base import LightPiece
from rules import Rules
from utils import generate_random_move


class Rewards(object):
    def __init__(self):
        self.default=1
        self.invalid_move=0.0
        self.move_opponent_piece=0.0
        self.remove_opponent_piece=50
        self.become_king=100
        self.opponent_no_pieces=1000
        self.opponent_no_valid_move=1000
        

    def __getitem__(self, name):
        return self._get_reward(name)

    def __setitem__(self, name, value):
        # tests if reward exists, exception is not catched on purpose
        self._get_reward(name)
        return setattr(self, name, value)

    def _get_reward(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            raise AttributeError(str(name)+" reward does not exists")


class Board(Constants, Rules):
    def __init__(
        self, size=8, initial_board=None):
        """Board constructor.

        Args:
            size: Board size.
        """
        self.size = size
        self.init(initial_board)
        self.rewards = Rewards()

    def init(self,initial_board=None):
        """Initialize board and setup pieces on board.

        Note: Dark pieces should be ALWAYS on the top of the board.
        """
        def interpret_initial_board(initial_board):
            self.board_list=[ #start with empty
                sum([[None] for _ in range(self.size)], []),
                sum([[None] for _ in range(self.size)], []),
                sum([[None] for _ in range(self.size)], []),
                sum([[None] for _ in range(self.size)], []),
                sum([[None] for _ in range(self.size)], []),
                sum([[None] for _ in range(self.size)], []),
                sum([[None] for _ in range(self.size)], []),
                sum([[None] for _ in range(self.size)], []),
            ]
            for i in range(self.size):
                for j in range(self.size):
                    if initial_board[i][j]==self.DARK:
                        self.board_list[i][j]=DarkPiece()
                    elif initial_board[i][j]==self.LIGHT:
                        self.board_list[i][j]=LightPiece()
                    elif initial_board[i][j]==self.DARK_KING:
                        piece=DarkPiece()
                        piece.make_king()
                        self.board_list[i][j]=piece
                    elif initial_board[i][j]==self.LIGHT_KING:
                        piece=LightPiece()
                        piece.make_king()
                        self.board_list[i][j]=piece
                    else:
                        rospy.logerr("Initial board not valid")
                        rospy.signal_shutdown("Initial board not valid")


        half_size = self.size//2
        self.board_list=None
        if initial_board is None:
            self.board_list = [
                sum([[None, DarkPiece()] for _ in range(half_size)], []),
                sum([[DarkPiece(), None] for _ in range(half_size)], []),
                sum([[None, DarkPiece()] for _ in range(half_size)], []),
                sum([[None] for _ in range(self.size)], []),
                sum([[None] for _ in range(self.size)], []),
                sum([[LightPiece(), None] for _ in range(half_size)], []),
                sum([[None, LightPiece()] for _ in range(half_size)], []),
                sum([[LightPiece(), None] for _ in range(half_size)], []),
            ]
        else:
            self.board_list=interpret_initial_board(initial_board)

    def update_rewards(
        self,
        rewards_map):
        """Update rewards. Adding new reward is not allowed.

        If `rewards_map` contains reward that wasn't defined in `Rewards`,
        AttributeError will be raised.

        Args:
            rewards_map: (Dict)

        Returns:
            None

        Raises:
            AttributeError: If attempts to add new reward.
        """
        for key, value in rewards_map.items():
            self.rewards[key] = value

    def move(
        self,
        ptype,
        from_row,
        from_col,
        to_row,
        to_col) :
        """Move piece across board and check validity of movement.
        It will automatically perform any jumps and kings transformations

        Args:
            ptype: Type of piece making a move.
            from_row: Row of board of original piece location.
            from_col: Column of board of original piece location.
            to_row: Row of board of desired piece location.
            to_col: Column of board of desired piece location.

        Returns:
            obs: information about positions of pieces.
            rew: reward for perfomed step.
            done: information about end of game.
            info: additional information about current step.
        """
        rew = self.rewards["default"]
        info = {}
        done = False

        if not self._can_opponent_move(self.board_list, self.get_opponent_type(ptype), self.size):
            return self._opponent_cant_move(self.board_list, self.rewards, info)

        # general invalid move
        if not self.validate_move(self.board_list, from_row, from_col, to_row, to_col):
            rew = self.rewards["invalid_move"]
            info.update({"invalid_move": (from_row, from_col, to_row, to_col)})

            from_row, from_col, to_row, to_col = generate_random_move(
                self.board_list,
                ptype,
                self.size,
            )

        # don't move with opponent's piece
        if ptype != self.board_list[from_row][from_col].ptype:
            rew = self.rewards["move_opponent_piece"]
            info.update({"move_opponenstept_piece": (from_row, from_col)})

            from_row, from_col, to_row, to_col = generate_random_move(
                self.board_list,
                ptype,
                self.size,
            )

        # move piece
        info_update = self.execute_move(from_row, from_col, to_row, to_col)
        info.update(info_update)

        # remove opponent's piece. by rule: if other jump is possible, jump again
        between_row, between_col = self.get_between_position(from_row, from_col, to_row, to_col)
        if between_row is not None and between_col is not None:
            p_between = self.board_list[between_row][between_col]
            if p_between is not None:
                i=1
                self.board_list[between_row][between_col] = None
                info.update({"removed_{}".format(i): ((between_row, between_col), p_between)})
                rew = self.rewards["remove_opponent_piece"]
                #check if other jump is possible
                jumps_list=Rules.get_valid_moves_jump(self.board_list, to_row, to_col)#valid jumps where it landed
                while len(jumps_list)>0:
                    i+=1
                    temp_from_row=to_row
                    temp_from_col=to_col
                    jump=random.choice(jumps_list)
                    to_row=jump[0]
                    to_col=jump[1]
                    between_row, between_col = self.get_between_position(temp_from_row, temp_from_col, to_row, to_col)
                    self.board_list[between_row][between_col] = None
                    info.update({"removed_{i}": ((between_row, between_col), p_between)})
                    rew += self.rewards["remove_opponent_piece"]
                    #update board
                    info_update = self.execute_move(temp_from_row, temp_from_col, to_row, to_col)
                    info.update(info_update)
                    jumps_list=Rules.get_valid_moves_jump(self.board_list, to_row, to_col)#valid jumps where it landed
        



        # become king
        p = self.board_list[to_row][to_col]
        if (to_row == 0 and p.direction == self.UP) or (to_row == self.size-1 and p.direction == self.DOWN):
            p.make_king()
            info.update({"king": (to_row, to_col)})
            rew = self.rewards["become_king"]

        # end of game?
        if len(self.get_positions(self.board_list, self.get_opponent_type(p.ptype), self.size)) == 0:
            # opponent lost all his pieces
            done = True
            rew = self.rewards["opponent_no_pieces"]
            info.update({"opponent_no_pieces": True})

        if not self._can_opponent_move(self.board_list, self.get_opponent_type(ptype), self.size):
            return self._opponent_cant_move(self.board_list, self.rewards, info)

        obs = self.board_list

        return obs, rew, done, info

    def execute_move(
        self,
        from_row,
        from_col,
        to_row,
        to_col) :
        """
        fuction only moves a piece form one position to other. Does not check rules
        """
        self.board_list[to_row][to_col] = self.board_list[from_row][from_col]
        self.board_list[from_row][from_col] = None
        return {"moved": ((from_row, from_col), (to_row, to_col))}


    def remove_piece(self,row, col):
        """
        Remove a piece of the board. Does not chekc for rules
        (used when manually performing a jump)
        """
        self.board_list[row][col] = None

    def transform_king(self,row,col):
        """
        Transform piece in that row,col to king
        Does not check for rules
        """
        p = self.board_list[row][col]
        p.make_king()





    @staticmethod
    def _can_opponent_move(
        board_list,
        opponent_ptype,
        board_size):
        if len(Rules.generate_valid_moves(board_list, opponent_ptype, board_size)) == 0:
            return False
        else:
            return True

    @staticmethod
    def _opponent_cant_move(
        board_list,
        rewards,
        info ) :
        obs = board_list
        rew = rewards["opponent_no_valid_move"]
        info.update({"opponent_invalid_move": True})
        done = True
        return obs, rew, done, info
