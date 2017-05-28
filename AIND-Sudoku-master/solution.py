import itertools

assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'
rcols = cols[::-1]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

#create diagonal units
diag1 = list(zip(rows,cols))
diag2 = list(zip(rows,rcols))
diagonal_units = [[i[0]+i[1] for i in diag1],[i[0]+i[1] for i in diag2]]

yes_diag = 1 #set to 1 for diagonal sudoku and 0 otherwise
if yes_diag == 1:
    unitlist = row_units + column_units + square_units + diagonal_units
else:
    unitlist = row_units + column_units + square_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Naked twins: two boxes in same unit that have a pair of identical digits
    # remaining as their only possibilities
    for unit in unitlist:
        # Find all boxes with two digits remaining as possibilities
        pairs = [box for box in unit if len(values[box]) == 2]
        # Pairwise combinations
        poss_twins = [list(pair) for pair in itertools.combinations(pairs, 2)]
        for pair in poss_twins:
            box1 = pair[0]
            box2 = pair[1]
            # Find the naked twins
            if values[box1] == values[box2]:
                for box in unit:
                    # Eliminate the naked twins as possibilities for peers
                    if box != box1 and box != box2:
                        for digit in values[box1]:
                            assign_value(values, box, values[box].replace(digit,''))
    return values                
                    

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    #convert the input string to a list then a dictionary
    values = []
    all_digits = '123456789'
    for g in grid:
        #replace '.' in the input string with '123456789' in the list 
        if g == '.':
            values.append(all_digits)
        #replace each number in the input string with the same number in the list
        elif g in all_digits:
            values.append(g)
    #ensure there are 81 values in the string
    assert len(values) == 81
    #create a dictionary with the values in the string matches to the corresponding box
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    #find the boxes with only one possibility
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            #remove the digit in the solved value from all peer boxes
            values = assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789': #iterate through each digit check if it is in a unit
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                #if the digit appears only in once in a unit, it becomes the solved value
                values = assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    #cycle through all the all tactics unless there is no progress
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        #if there are any empty boxes, return False
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    values = reduce_puzzle(values)
    #if the reduce_puzzle() returns False, return for but if all boxes have only one value in them, return the sudoku puzzle
    if values is False:
        return False 
    if all(len(values[s]) == 1 for s in boxes): 
        return values
    #choose a square with one of the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    #use recursion to solve each of the sudokus using those possibilities
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    
    answer = grid_values(grid) #convert grid into dictionary
    answer = search(answer) #solve sudoku in dictionary form
    return answer
    
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
