import random
import seoulai_gym.envs.checkers.utils as checkers_utils

class MonteCarlo:

	def __init__(self, root_node):
		self.root_node = root_node
		self.child_finder = None
		self.node_evaluator = lambda child, montecarlo: None

	def make_choice(self):
		"""
		choose the best chilndres from root.
		"""
		best_children = []
		most_visits = float('-inf')

		for child in self.root_node.children:
			if child.visits > most_visits:
				most_visits = child.visits
				best_children = [child]
			elif child.visits == most_visits:
				best_children.append(child)

		return random.choice(best_children)

	def make_exploratory_choice(self):
		children_visits = map(lambda child: child.visits, self.root_node.children)
		children_visit_probabilities = [visit / self.root_node.visits for visit in children_visits]
		random_probability = random.uniform(0, 1)
		probabilities_already_counted = 0.

		for i, probability in enumerate(children_visit_probabilities):
			if probabilities_already_counted + probability >= random_probability:
				return self.root_node.children[i]

			probabilities_already_counted += probability

	def simulate(self, expansion_count = 1,max_depth=50):
		"""
		simulate N branches (N=expansion_count)
		max_depth: max depth of the branches
		In difference of MTCS, where you keep expanding more promisiong nodes in the tree,
		we will expand always one level below root devel, simulating a random game. the result of all the random games will help
		ro decide the probability to win performing that move.
		"""
		for i in range(expansion_count):
			current_node = self.root_node


			# while current_node.expanded:#search the prefered child with best probabilities to win. if is not expanded, continue expanding it
			# 	current_node = current_node.get_preferred_child(self.root_node)
			# 	current_depth+=1
			# 	print("depth: {}".format(current_depth))

			self.expand(current_node,max_depth)#expand de unexplored leaft
			

	def expand(self, node,max_depth):
		"""
		expand all child of the selected node
		performing random simulations on each branch
		until the have a win or lose value
		"""
		if node.children == []: #added since we will expand several times the same childs. Need to look for child only the first time
			self.child_finder(node, self)

		for child in node.children:
			child_win_value = self.node_evaluator(child, self)

			if child_win_value != None:#run intil child is a win/lose
				child.update_win_value(child_win_value)
			else: #else, continue expanding the random simulation
				current_depth=1
				# print("depth: {}".format(current_depth))
				self.random_rollout(child,max_depth,current_depth)
				child.children = []
				#once it finished expanding (i.e sinulation in branch ended), save game points
				game_score=2*child.win_value[child.parent.player_number]-sum(child.win_value.values())
				child.game_points.append(game_score)


		if len(node.children):
			node.expanded = True

	def random_rollout(self, node,max_depth,current_depth):
		"""
		continue expanding branch, in random nodes intil win value is returned
		limit to a max_depth of the branch
		"""
		self.child_finder(node, self)
		child = random.choice(node.children)#expand current branch to a random child
		node.children = []
		node.add_child(child)
		child_win_value = self.node_evaluator(child, self)

		if child_win_value != None or max_depth<current_depth:#if is a win/lose stop. Can also stop because reached simulation max depth
			node.update_win_value(child_win_value)
		else:
			current_depth+=1
			# print("depth: {}".format(current_depth))
			# print("next child")
			# checkers_utils.print_board(child.state.board_list)
			# print("\n\r")
			self.random_rollout(child,max_depth,current_depth)#if not, continue expanding branch