# Checkers probabilities
This is a modified version of the monte carlo tree search code developed by [ImparaAI](https://github.com/ImparaAI/monte-carlo-tree-search). This code kept some of the functions that help to build a tree with random games.

The objetive of this package is to answer the wuestion "Given a current board, which is the probability of win if I perform X move?" (where X can be any of the possible moves).
To solve this question, we build a tree with only one depth level. Where the root node is the current board, and each child is the board after one of the possible movements.

For each posible move, N games , of D moves each game are simulated randomly. During each game, each player will adquire some reward points. The reward points are used to estimate the probability to win for a specific move.

![alt text](https://github.com/gbravoi/checkers_probabilities/blob/master/readme_img/checkers.png?raw=true)


## Computing winning probability
During the simulated random game, both players win points. For example:
```python
default=1,
remove_opponent_piece=50,
become_king=100,
opponent_no_pieces=1000,
opponent_no_valid_move=1000,
```
(These rewards are in *gym/seulai_gym/env/board.py*)

Once the simulation ends, the game score is computed as (*montecarlo/montecarlo.py*):
```python
game_score=player_score-oponent_score*self.oponente_scaler
child.game_points.append(game_score)
```
where **oponente_scaler** is a number bigger than one. A greater number implies playing more defensively
The **game_score** will be saved in the list **child.game_points**

Once all N games are simulated for each possible move the probability of winning is computed as (*montecarlo/montecarlo.py*):
```python
for child in root_node.children:
	winning_score=np.mean(child.game_points)
	child.transition_move.winning_prob=winning_score  #save score here, later will transform it in probability
	sum_scores+=winning_score
	moves.append(child.transition_move)
	if min_score>winning_score: #save min score, used later to leave all scores as positive numbers
		min_score=winning_score

if min_score!=float('inf') :
	min_score=abs(min_score)+1 #(avoid prob=0)
else:
	min_score=1
sum_scores+=min_score*len(moves) #we will add min_score to all scores to ensure positive numbers

#now transform score to probabilities
for move in moves:
	move.winning_prob=(min_score+move.winning_prob)/(sum_scores)
```

In here move is a class that contains information of the move (from position, to position and winning probability)


## Setting number of simulations and game depth
This can be done in *montecarlo/montecarlo.py* modifiying the following lines:
```python
self.number_of_simulations=10
self.number_of_simulations_ending=5 
self.max_depth=10 
self.max_depth_ending=10
self.ending_treshold=4
self.oponente_scaler=1.1
```

In here *self.ending_treshold* is the number of pieces to consider the game near and end (if any of the players has equal or lower quantity). When the game is ending, we may want to increase the depth of the games *self.max_depth_ending* to take into consideration that the pieces can be distanced and that kings have more possible movements. We could also want to reduce *self.number_of_simulations_ending* to reduce the needed total time to simulate and compute the probabilities

## How to test code
To test version with graphical interface
```
python3 integration_test_gym.py
```

or to test version without grapical interface, but compatible with python 2.7 (ROS) 
```
python2 integration_test_terminal.py
```

You have 2 options: 
* watch a game where the computer play against other computer. Probabilities will be printed in the terminal, and the computer will choose the best move.
* Play against the computer. Probabilities will be printed in the terminal. Then, when is user turn, a promp will ask which of the available moves want to choose.


To modify if if a game computer vs computer, or human vs computer change the following line in *integration_test_gym.py* (*integration_test_terminal.py*)
```python
human_agent=a2 #set None if no human, else will take the turn of the agent (a1 or a2)
```
