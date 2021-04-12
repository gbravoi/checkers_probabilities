"""
Checkers
https://en.wikipedia.org/wiki/Draughts

Martin Kersner, m.kersner@gmail.com
seoulai.com
2018

Adapted by Gabriela B. to work with python 2.7 and ROS
"""
import copy



from base import Piece
from base import Constants
from board import Board
from rules import Rules


class Checkers(Constants, Rules):
    def __init__(self,initial_board=None):
        """Initialize checkers board and its visualization.

        Returns:
            None
        """
        self.possible_moves = None
        self.piece_location = None

        self.board = Board(initial_board=initial_board)

    def update_rewards(self,rewards_map):
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
        self.board.update_rewards(rewards_map)

    def step(
        self,
        agent,
        from_row,
        from_col,
        to_row,
        to_col) :
        """Make a step (= move) within board.

        Args:
            agent: Agent making a move.
            from_row: Row of board of original piece location.
            from_col: Col of board of original piece location.
            to_row: Row of board of desired piece location.
            to_col: Col of board of desired piece location.

        Returns:
            obs: Information about positions of pieces.
            rew: Reward for perfomed step.
            done: Information about end of game.
            info: Additional information about current step.
        """
        #get podible moves for highlight. First check for jumtps
        possible_jumps=self.get_valid_moves_jump(self.board.board_list, from_row, from_col)
        if len(possible_jumps)>0:
            self.possible_moves = possible_jumps
        else:
            self.possible_moves = self.get_valid_moves_simple(self.board.board_list, from_row, from_col)

        self.piece_location = (from_row, from_col)
        obs, rew, done, info = self.board.move(agent.ptype, from_row, from_col, to_row, to_col)
        return copy.deepcopy(obs), rew, done, info

    def reset(self):
        """Reset all variables and initialize new game.

        Returns:
            obs: Information about positions of pieces.
        """
        self.board = Board()
        obs = self.board.board_list
        return obs



