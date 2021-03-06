#!/usr/bin/env python2
"""
same as integration_test_gym 
but does not use gym (and is able to play the game)
"""
import copy
import numpy as np
import random

#import montecarlo
from montecarlo.node import Node
from montecarlo.montecarlo import MonteCarlo


#import checkers rules
from checkers.checkers import Checkers 
from checkers.agents import RandomAgentLight
from checkers.agents import RandomAgentDark



def main():
	#start gym
	env = Checkers()

	a1 = RandomAgentLight() #computer players
	a2 = RandomAgentDark() 
	human_agent=a2 #set None if no human, else will take the turn of the agent

	obs = env.reset()
	# checkers_utils.print_board(obs)

	current_agent = a1
	next_agent = a2



	while True:
		#we have 2 agents. human and computer. If is computer we can move rabdom or using probabilities
		#pending implement choose that based on probability

		#start montecarlo
		board=copy.deepcopy(env.board)#copy current board to process montecarlo
		Node_0=Node(board,current_agent.ptype) #start node
		montecarlo = MonteCarlo(Node_0)
		#run montecarlo simulation
		montecarlo.simulate()

		#if human, show probabibilities and let them choose, else machine choose best
		chosen_move=None
		if human_agent==current_agent:
			montecarlo.estimate_probabilities()
			index= int((input("type number from 0 to N to access the action and press enter. Invalid numbers create a random movement:")))#if number  outside dictionary choose random
			moves_dic=montecarlo.moves_prob
			if index<len(moves_dic):
				print("user move")
				chosen_move=moves_dic[index]
			else:
				print("user move random")
				chosen_move=random.choice(moves_dic)
		else: #computer plays
			chosen_move = montecarlo.get_best_move()#get best move based on probabilities
			print("best move")

		chosen_move.print_move()
		from_row=chosen_move.from_row()
		from_col=chosen_move.from_col()
		to_row=chosen_move.to_row()
		to_col=chosen_move.to_col()

		#Execute move on gym enviroment
		obs, rew, done, info = env.step(current_agent, from_row, from_col, to_row, to_col)


		if done:
			print("Game over!"+str( current_agent)+" agent wins.")
			obs = env.reset()
			break

		# switch agents
		temporary_agent = current_agent
		current_agent = next_agent
		next_agent = temporary_agent




if __name__ == "__main__":
    main()