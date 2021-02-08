import random
from math import log, sqrt
from seoulai_gym.envs.checkers.rules import Rules

class Node:

	def __init__(self, state,player_number=None,transition_move=None):
		self.state = state
		self.transition_move=transition_move #save information of the action from the parent to bring to current status. {(from_row, from_col):(to_row, to_col)}
		self.action_reward=0 #reward for certain actions like capturing a checker or becoming a king (action to move from parent to child)
		#note this reward is of the oponent player that left the board in current state
		self.win_value = {} #store rewards for both player when doing backpropagation of the simulted game
		self.game_points=[]#store final points of that game. computed as rewanr_payer- reward_opponent
		self.policy_value = None
		self.visits = 0
		self.parent = None
		self.children = []
		self.expanded = False
		self.player_number = player_number#who needs to move
		self.discovery_factor =35.0

	def update_win_value(self, value):
		"""
		we pass final value for each player. 
		(At the end we should extrat the corresponding reward for the root node
		"""
		opponent_ptype=Rules.get_opponent_type(self.player_number) #the one that already move
		#recover rewards below on the tree
		if not isinstance(value,dict): #if not a dictionary (case when stop before winning/lossing)
			value={}
		if self.player_number not in value:#make sure player is in the dictionary
			value[self.player_number]=0
		if opponent_ptype  not in value:#make sure player is in the dictionary
			value[opponent_ptype]=0
		
		self.win_value=value

		#add win value in a dictionary with player number. reward of board asociated to movement of previos player.
		self.win_value[opponent_ptype]+=self.action_reward		
		self.visits += 1

		if self.parent:#pass current rewards to the parent on the branch
			self.parent.update_win_value(self.win_value)

	def update_policy_value(self, value):
		self.policy_value = value

	def add_child(self, child):
		self.children.append(child)
		child.parent = self

	def add_children(self, children):
		for child in children:
			self.add_child(child)



	def is_scorable(self):
		return self.visits or self.policy_value != None