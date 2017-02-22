# <editor-fold desc="Encode the board.">
def cross(A, B):
    """Cross product of elements in A and elements in B."""
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

unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)
# </editor-fold>


# <editor-fold desc="Encode the game and and display a particular state.">
def grid_values(grid):
    """
    Convert grid into a dict of {box: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Return:
        A grid in dictionary form.
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    return {box: '123456789' if value == '.' else value for box in boxes for box, value in zip(boxes, grid)}


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
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
        print('Sorry, no solution could be found.')
    return
# </editor-fold>


# <editor-fold desc="Keep track of intermediate states of the game.">
assignments = []


def assign_value(values, box, value):
    """Assign a value to a given box. If it updates the board record it."""
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values
# </editor-fold>


# <editor-fold desc="Implement strategy techniques.">
def eliminate(values):
    """Eliminate a box's value from the possible values of all its peers.

    Args:
        values(dict): The sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    for box, value in values.items():
        if len(value) == 1:
            for peer in peers[box]:
                values = assign_value(values, peer, values[peer].replace(value, ''))
    return values


def only_choice(values):
    """In every unit with a value that only fits in one box, assign the value to that box.

    Args:
        values(dict): The sudoku in dictionary form
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values


def naked_twins(values):
    """In every unit where two values are only possible in two boxes, eliminate those values from the remaining boxes.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        The values dictionary with the naked twins eliminated from peers.
    """
    # In each unit
    for unit in unitlist:
        # get all boxes with a value of length two.
        potential_twins = [box for box in unit if len(values[box]) == 2]
        # If there are at least two such boxes
        if len(potential_twins) >= 2:
            # for each one
            for i in range(len(potential_twins)):
                box_1, box_value_1 = potential_twins[i], values[potential_twins[i]]
                # compare it with the other boxes with a value of length two in the unit.
                for j in range(i + 1, len(potential_twins)):
                    box_2, box_value_2 = potential_twins[j], values[potential_twins[j]]
                    # If we find two boxes with the same value, we've found a pair of naked twins.
                    if box_value_1 == box_value_2:
                        # print("Found naked twins:", box_1, box_2, box_value_1)
                        # Eliminate the values of the naked twins as possibilities for their peers.
                        # Remove the twin from the peers.
                        for peer in [peer for peer in unit if peer != box_1 and peer != box_2]:
                            for digit in box_value_1:
                                values = assign_value(values, peer, values[peer].replace(digit, ''))
    return values
# </editor-fold>


# <editor-fold desc="Implement constraint propagation and search.">
def reduce_puzzle(values):
    stalled = False
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
    """Using depth-first search and propagation, create a search tree and solve the sudoku."""
    # Reduce the puzzle.
    values = reduce_puzzle(values)
    if values is False:
        return False # Failed earlier
    if all(len(values[box]) == 1 for box in boxes):
        return values # Solved!
    # Choose one of the unfilled squares with the fewest possibilities.
    n, b = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)
    # Use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer.
    for value in values[b]:
        new_sudoku = values.copy()
        new_sudoku[b] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt
# </editor-fold>


# <editor-fold desc="Solve the game.">
def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
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
