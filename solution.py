import random

# <editor-fold desc="Encode the board.">
def cross(A, B):
    """Compute cross product of elements in A and elements in B.

    Args:
        A: an iterable
        B: an iterable
    Returns:
        The cross product of A an B in the form of a list
    """
    return [a + b for a in A for b in B]


rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diag_unit_1 = [rows[int(i) - 1] + i for i in cols]
diag_unit_2 = [rows[int(i) - 1] + cols[::-1][int(i) - 1] for i in cols]
diag_units = [diag_unit_1, diag_unit_2]

# These are better handled from `solve`, to allow for diagonal option.
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)
# </editor-fold>


# <editor-fold desc="Encode the game and and display a particular state.">
def grid_values(grid):
    """Convert a grid into a dictionary of {box: char} with '123456789' for empties.

    Args:
        grid(string): a grid in string form
    Returns:
        A grid in dictionary form
            Keys: the boxes, e.g., 'A1'
            Values: the value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    return {box: '123456789' if value == '.' else value for box in boxes for box, value in zip(boxes, grid)}


def display(values):
    """Display a sudoku as a 2-D grid. If the state is False (no solution found), display a message instead.

    Args:
        values(dict): a sudoku in dictionary form
    Returns:
        None
    """
    if values:
        width = 1 + max(len(values[b]) for b in boxes)
        line = '+'.join(['-' * (width * 3)] * 3)
        for r in rows:
            print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                          for c in cols))
            if r in 'CF': print(line)
    else:
        print('Sorry, no solution could be found, so there is nothing to display.')
    return
# </editor-fold>


# <editor-fold desc="Keep track of intermediate states of the game.">
assignments = []


def assign_value(values, box, value):
    """Assign a value to a given box. If it updates the board record it.

    Args:
        values(dict): a sudoku in dictionary form
        box(string): the box whose value is to be updated
        value(string): the new value
    Returns:
        The resulting sudoku in dictionary form
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values
# </editor-fold>


# <editor-fold desc="Implement strategy techniques.">
def eliminate(values):
    """Eliminate a box's value from the possible values of all its peers.

    Args:
        values(dict): a sudoku in dictionary form
    Returns:
        The resulting sudoku in dictionary form
    """
    for box, value in values.items():
        if len(value) == 1:
            for peer in peers[box]:
                values = assign_value(values, peer, values[peer].replace(value, ''))
    return values


def only_choice(values):
    """In every unit with a value that only fits in one box, assign that value to that box.

    Args:
        values(dict): a sudoku in dictionary form
    Returns:
        The resulting sudoku in dictionary form
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values


def naked_tuplets(values, n):
    """Find tuplets and eliminate their value from their peers in that unit.

    In every unit where a value consisting of n digits is only possible in n boxes, eliminate those digits
    from the possible values of the remaining boxes in that unit. The set of n boxes sharing the n-digit value
    is a tuplet.

    Args:
        values(dict): a sudoku in dictionary form
        n(int): the length of the tuplet
    Returns:
        The resulting sudoku in dictionary form
    """
    assert n <= 8, "The tuplet cannot exceed the length of a unit (9), and 'nonuplets' are useless!"
    # In each unit
    for unit in unitlist:
        # get all boxes with a value of length n.
        potential_tuplets = [box for box in unit if len(values[box]) == n]
        # If there are at least n such boxes
        if len(potential_tuplets) >= n:
            # for each one
            for i in range(len(potential_tuplets)):
                box_1, box_value_1 = potential_tuplets[i], values[potential_tuplets[i]]
                same_value = [box_1] # store boxes with same value
                # compare it with the other boxes with a value of length n in the unit.
                for j in range(i + 1, len(potential_tuplets)):
                    box_2, box_value_2 = potential_tuplets[j], values[potential_tuplets[j]]
                    if box_value_1 == box_value_2:
                        same_value.append(box_2)
                # If there are as many boxes with the same value as there are digits in that value
                if len(same_value) == n:
                    # eliminate the digits of the shared value as possibilities for their unit peers.
                    for peer in [peer for peer in unit if peer not in same_value]:
                        for digit in box_value_1:
                            values = assign_value(values, peer, values[peer].replace(digit, ''))
    return values


def naked_twins(values):
    """Implement a specific case of a naked tuplet, where n is 2.

    Args:
        values(dict): a sudoku in dictionary form
    Returns:
        The resulting sudoku in dictionary form
    """
    return naked_tuplets(values, 2)
# </editor-fold>


# <editor-fold desc="Implement constraint propagation and search.">
def reduce_puzzle(values):
    """Implement constraint propagation.

    Apply repeatedly three constraints: eliminate, only choice, and naked twins, to an unsolved puzzle.

    Args:
        values(dict): a sudoku in dictionary form
    Returns:
        The solved sudoku in dictionary form, or False if no solution is found
    """
    stalled = False # Have we stopped making progress?
    while not stalled:
        # Check how many boxes have a determined value.
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the eliminate strategy.
        values = eliminate(values)
        # Use the only choice strategy.
        values = only_choice(values)
        # Use the naked twins strategy.
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare.
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, create a search tree and solve the sudoku.

    Args:
        values(dict): a sudoku in dictionary form
    Returns:
        The solved sudoku in dictionary form, or False if no solution is found
    """
    # Reduce the puzzle.
    values = reduce_puzzle(values)
    if values is False:
        return False # Failed earlier
    if all(len(values[box]) == 1 for box in boxes):
        return values # Solved!
    # Choose one of the unfilled boxes with the fewest possibilities. Break ties with random choice.
    n = min(len(values[box]) for box in boxes if len(values[box]) > 1)
    b = random.choice([box for box in boxes if len(values[box]) == n])

    # Alternatively, simply choose the first such box.
    # n, b = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)

    # Use recursion to solve each one of the resulting sudokus. If one returns a value (not False), return it.
    for value in values[b]:
        new_sudoku = values.copy()
        new_sudoku[b] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt
# </editor-fold>


# <editor-fold desc="Generate a Sudoku grid.">
def generate_full_grid(diagonal=False):
    """Generate a full Sudoku grid, with all values shown."""
    grid = '.' * len(boxes)
    return ''.join(solve(grid, diagonal=diagonal).values())


def generate_puzzle_grid(full_grid, proportion_hidden=0.5):
    """Generate a grid with hidden values from ones with all the values observable."""
    n_hidden = int(len(grid) * proportion_hidden)
    puzzle_grid = grid_values(full_grid)
    for i in range(n_hidden):
        box = random.choice([box for box in boxes if puzzle_grid[box] != '.'])
        puzzle_grid[box] = '.'
    return ''.join(puzzle_grid.values())
# </editor-fold>


# <editor-fold desc="Solve the game.">
def solve(grid, diagonal=True):
    """Find the solution to a Sudoku grid.

    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid, or False if no solution exists
    """
    global unitlist, units, peers
    if diagonal:
        unitlist = row_units + column_units + square_units + diag_units
        units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
        peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)
    else:
        unitlist = row_units + column_units + square_units
        units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
        peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)
    return search(grid_values(grid))
# </editor-fold>


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
