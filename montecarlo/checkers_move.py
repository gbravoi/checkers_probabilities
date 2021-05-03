"""
code contain move class, with info of the move
"""
class Move:
	def __init__(self, from_move,to_move,player_number,winning_prob=None):
		self.from_move=from_move #(row,column)
		self.to_move=to_move
		self.player_number=player_number #player who perform the action
		self.winning_prob=winning_prob

		self.from_row=self.from_move[0]
		self.from_col=self.from_move[1]
		self.to_row=self.to_move[0]
		self.to_col=self.to_move[1]

	def print_move(self):
		print("from ({},{}) to ({},{})  prob:{}".format(self.from_move[0],self.from_move[1],self.to_move[0],self.to_move[1],self.winning_prob))

	def from_row(self):
		return self.from_move[0]
	
	def from_col(self):
		return self.from_move[1]

	def to_row(self):
		return self.to_move[0]
	
	def to_col(self):
		return self.to_move[1]