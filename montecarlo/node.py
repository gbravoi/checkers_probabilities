import random
from math import log, sqrt

class Node:

	def __init__(self, state,player_number=None,transition_action={}):
		self.state = state
		self.transition_action=transition_action #save information of the action from the parent to bring to current status
		self.win_value = 0
		self.policy_value = None
		self.visits = 0
		self.parent = None
		self.children = []
		self.expanded = False
		self.player_number = player_number
		self.discovery_factor = 0.35

	def update_win_value(self, value):
		self.win_value += value
		self.visits += 1

		if self.parent:
			#check if different color, because win from one color is loss for the other
			win_multiplier = 1 if self.parent.player_number == self.player_number else -1
			self.parent.update_win_value(value*win_multiplier)

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
		discovery_operand = self.discovery_factor * (self.policy_value or 1) * sqrt(log(self.parent.visits) / (self.visits or 1))

		win_multiplier = 1 if self.parent.player_number == root_node.player_number else -1
		win_operand = win_multiplier * self.win_value / (self.visits or 1)

		self.score = win_operand + discovery_operand

		return self.score

	def is_scorable(self):
		return self.visits or self.policy_value != None