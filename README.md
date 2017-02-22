# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A: The sudoku constraint is that every unit (row, column, or square) be a permutation of the digits 1-9.
Therefore, the fact that two boxes that belong to a particular unit have the same two digits as their only possible
values forbids those two values from being valid options for the remaining boxes of that unit. Indeed, the
constraint that each digit (1-9) only appear once in a unit requires that, since the two digits are certain to be
found in the two 'twin' boxes (even if we don't know yet which digit goes in which 'twin' box), they are certain not
to be found in the other boxes of that unit.

# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: We include an additional type of unit in our unit list. Concretely, this amounts to adding two new units to our list,
namely the two main diagonals of the board. We then apply constraint propagation and search as before, only this time
they apply to the two diagonals as well.

### Install

This project requires **Python 3**.

We recommend students install [Anaconda](https://www.continuum.io/downloads), a pre-packaged Python distribution that contains all of the necessary libraries and software for this project. 
Please try using the environment we provided in the Anaconda lesson of the Nanodegree.

##### Optional: Pygame

Optionally, you can also install pygame if you want to see your visualization. If you've followed our instructions for setting up our conda environment, you should be all set.

If not, please see how to download pygame [here](http://www.pygame.org/download.shtml).

### Code

* `solutions.py` - You'll fill this in as part of your solution.
* `solution_test.py` - Do not modify this. You can test your solution by running `python solution_test.py`.
* `PySudoku.py` - Do not modify this. This is code for visualizing your solution.
* `visualize.py` - Do not modify this. This is code for visualizing your solution.

### Visualizing

To visualize your solution, please only assign values to the values_dict using the ```assign_values``` function provided in solution.py

### Data

The data consists of a text file of diagonal sudokus for you to solve.
