import random
from math import log, sqrt

class Node:

	def __init__(self, state,player_number=None,transition_action={}):
		self.state = state
		self.transition_action=transition_action #save information of the action from the parent to bring to current status. {(from_row, from_col):(to_row, to_col)}
		self.action_reward=0 #reward for certain actions like capturing a checker or becoming a king (action to move from parent to child)
		self.win_value = {} #store rewards for both player when doing backpropagation of the simulted game
		self.game_points=[]#store final points of that game. computed as rewanr_payer- reward_opponent
		self.policy_value = None
		self.visits = 0
		self.parent = None
		self.children = []
		self.expanded = False
		self.player_number = player_number
		self.discovery_factor =35.0

	def update_win_value(self, value):
		"""
		we pass final value for each player. 
		(At the end we should extrat the corresponding reward for the root node
		"""
		#recover rewards below on the tree
		if not isinstance(value,dict): #if not a dictionary (case when stop before winning/lossing)
			value={}
		if self.player_number not in value:#make sure player is in the dictionary
			value[self.player_number]=0
		
		self.win_value=value

		#add win value in a dictionary with player number
		self.win_value[self.player_number]+=self.action_reward		
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

	def get_preferred_child(self, root_node):
		best_children = []
		best_score = float('-inf')

		for child in self.children:
			score = child.get_score(root_node)

			if score > best_score:
				best_score = score
				best_children = [child]
			elif score == best_score:
				best_children.append(child)

		return random.choice(best_children)

	def get_score(self, root_node):
		"""
		get score, higher if root_node will win
		"""
		discovery_operand = self.discovery_factor * (self.policy_value or 1) * sqrt(log(self.parent.visits) / (self.visits or 1))

		player_reward =  self.win_value[root_node.player_number]
		sum_reward=sum(self.win_value.values())
		winning_points=2*player_reward-sum_reward#player-oponentet reward
		win_operand = winning_points / (self.visits or 1)#maye add factor here?

		self.score = win_operand + discovery_operand

		return self.score

	def is_scorable(self):
		return self.visits or self.policy_value != None