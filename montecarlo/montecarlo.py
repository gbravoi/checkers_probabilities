"""
This is a modified version of the MCTS by https://github.com/ImparaAI/monte-carlo-tree-search
The objective of this code is to provide a probability over the next move given a board and a player.
For this, first compute all posibles movements from that board.
Play N random games that start with one posible move. Games has a maximum depth. Assign a score to each game.
Using the scores, compute a probability of win for the current player when performing that movement.

All game functions are from repo https://github.com/gbravoi/gym
"""
import random
import numpy as np
import copy

#import gym
from seoulai_gym.envs.checkers.rules import Rules
import seoulai_gym.envs.checkers.utils as checkers_utils

#import montecarlo
from mcts.montecarlo.node import Node

#other imports
import game.checkers_move as cmove

class MonteCarlo:

	def __init__(self, root_node):
		self.root_node = root_node
		self.moves_prob=None

	#functions child finder adapter to gym
	def child_finder(self, node):
		"""
		add any child nodes to the parent node passed into the function
		"""
		#current player and oponent type
		current_player=node.player_number
		oponent_type=Rules.get_opponent_type(current_player)

		#get all possibles moves from this board
		parent_board=copy.deepcopy(node.state)
		valid_moves=Rules.generate_valid_moves(parent_board.board_list, current_player, len(parent_board.board_list))

		#for each valid move, create board. create a node with that board and with next agent.
		for from_move in valid_moves.keys(): #select a piece
			all_moves=valid_moves[from_move]

			for to_move in all_moves:#select a move from that piece
				child_board=copy.deepcopy(parent_board) #save board object
				transition_move=cmove.Move(from_move,to_move,current_player)
				obs, rew, done, info=child_board.move(current_player, transition_move.from_row(), transition_move.from_col(), transition_move.to_row(), transition_move.to_col())
				new_node=Node(child_board,oponent_type,transition_move)#new board after player type, next move: oponent
				new_node.action_reward=rew #reward asociated to certain movements
				node.add_child(new_node)#add child

			# print("\n\r old board")
			# checkers_utils.print_board(node.state.board_list)
			# print("\n\r new board")
			# checkers_utils.print_board(child_board.board_list)
			# print("\n\r")


	def node_evaluator(self, node):
		"""
		Return value different from None if lose or win to indicate game ended.
		Consider end if a player has only one piece (can scape infinitly)
		or if a player can't move
		"""
		board_object=node.state
		board_list=board_object.board_list
		current_type=node.player_number #the one that will try to move
		opponent_ptype=Rules.get_opponent_type(current_type) #the one that already move
		board_size=len(board_list)
		# checkers_utils.print_board(board)

		#check if lose
		if len(Rules.get_positions(board_list, current_type, board_size) )== 1:#check current player doesn't have any pieces
			# print("{} lose".format(current_type))
			rew_opponent_no_pieces = board_object.rewards["opponent_no_pieces"]
			return {opponent_ptype: rew_opponent_no_pieces}
		elif len(Rules.generate_valid_moves(board_list, current_type, board_size)) == 0:#check if current player can't move
			# print("{} lose".format(current_type))
			rew_opponent_cant_move = board_object.rewards["opponent_no_valid_move"]
			return {opponent_ptype: rew_opponent_cant_move}

		#check if wins (current player with current board)
		if len(Rules.get_positions(board_list, opponent_ptype, board_size)) == 1: #check other player doesn't have any pieces
			# print("{} lose".format(opponent_ptype))
			rew_opponent_no_pieces = board_object.rewards["opponent_no_pieces"]
			return {current_type: rew_opponent_no_pieces}
		elif len(Rules.generate_valid_moves(board_list, opponent_ptype, board_size)) == 0:#check if other player can't move
			# print("{} lose".format(opponent_ptype))
			rew_opponent_cant_move = board_object.rewards["opponent_no_valid_move"]
			return {current_type: rew_opponent_cant_move}

		return None





	def estimate_probabilities(self,print_prob=True):
		"""
		Estimate winning probabilities of the board
		average points in game in the movement
		Then devide the points/sum_all (averages) of all possible movements
		"""
		root_node=self.root_node
		player_number=root_node.player_number
		sum_scores=0
		min_score=float('inf') #needed to leave all probabilities positive. 

		moves=[]
		for child in root_node.children:
			winning_score=np.mean(child.game_points)
			child.transition_move.winning_prob=winning_score#save score here, later will transform it in probability
			sum_scores+=winning_score
			moves.append(child.transition_move)
			if min_score>winning_score: #save min score, used later to leave all scores as positive numbers
				min_score=winning_score

		if min_score!=float('inf') :
			min_score=abs(min_score)+1 #(avoid prob=0)
		else:
			min_score=1
		sum_scores+=min_score*len(moves) #we will add min_score to all scores
		#now transform score to probabilities
		if print_prob:
			print("\n\r possible moves:")
		for move in moves:
			move.winning_prob=(min_score+move.winning_prob)/(sum_scores)
			#for debug
			if move.winning_prob is None:
				print("error")
			if print_prob:
					move.print_move()

		self.moves_prob=moves

		# return moves

	def get_best_move(self):
		"""
		return best move
		This should be called after a montecalo simulation
		"""
		#if move weren't previously computed
		if self.moves_prob is None:
			self.estimate_probabilities()

		#select best
		best_move=[]
		prob=0
		for move in self.moves_prob:
			if move.winning_prob>prob:
				best_move=[move]
				prob=move.winning_prob
			elif move.winning_prob==prob:
				best_move.append(move)
		
		self.moves_prob=None #reset

		return random.choice(best_move)



	def simulate(self, expansion_count = 1,max_depth=6):
		"""
		simulate N branches (N=expansion_count)
		max_depth: max depth of the branches
		In difference of MTCS, where you keep expanding more promisiong nodes in the tree,
		we will expand always one level below root devel, simulating a random game. the result of all the random games will help
		ro decide the probability to win performing that move.
		"""
		for i in range(expansion_count):
			current_node = self.root_node

			self.expand(current_node,max_depth)#expand de unexplored leaft
			

	def expand(self, node,max_depth):
		"""
		expand all child of the selected node
		performing random simulations on each branch
		until the have a win or lose value
		"""
		if node.children == []: #added since we will expand several times the same childs. Need to look for child only the first time
			self.child_finder(node)

		for child in node.children:
			child_win_value = self.node_evaluator(child)

			if child_win_value != None:#run intil child is a win/lose
				child.update_win_value(child_win_value)
			else: #else, continue expanding the random simulation
				current_depth=1
				# print("depth: {}".format(current_depth))
				self.random_rollout(child,max_depth,current_depth)
				child.children = []

			#once it finished expanding (i.e sinulation in branch ended), save game points (PARENT SCORE)
			player_score=child.win_value[child.parent.player_number]
			oponent_score=child.win_value[Rules.get_opponent_type(child.parent.player_number)]
			oponente_scaler=1.4 #number greater than 1, if 1 points are the same for player or oponente. if greater, any ventage of the oponent is being avoided
			game_score=player_score-oponent_score*oponente_scaler
			child.game_points.append(game_score)


		if len(node.children):
			node.expanded = True

	def random_rollout(self, node,max_depth,current_depth):
		"""
		continue expanding branch, in random nodes intil win value is returned
		limit to a max_depth of the branch
		"""
		self.child_finder(node)
		child = random.choice(node.children)#expand current branch to a random child
		node.children = []
		node.add_child(child)
		child_win_value = self.node_evaluator(child)

		if child_win_value != None or max_depth<current_depth:#if is a win/lose stop. Can also stop because reached simulation max depth
			node.update_win_value(child_win_value)
		else:
			current_depth+=1
			# print("depth: {}".format(current_depth))
			# print("next child")
			# checkers_utils.print_board(child.state.board_list)
			# print("\n\r")
			self.random_rollout(child,max_depth,current_depth)#if not, continue expanding branch