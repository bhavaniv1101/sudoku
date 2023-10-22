# -*- coding: utf-8 -*-
"""
Created on Mon May 17 16:56:16 2021

@author: bhava
"""


import copy
import pprint


# ORDER = n means n^2 by n^2 grid.
ORDER = 3


def puzzles_from_file(file_name="sudoku.txt"):
    """
    Returns list of puzzles from file_name.

    Each puzzle is assumed to be 9 x 9 and is represented as a list of 9 lists,
    each having 9 elements in range(10).
    """

    puzzle_list = []
    with open(file_name, "r") as f_hand:
        for line in f_hand:
            if line.startswith("Grid 01"):
                new_grid = []
                continue
            elif line.startswith("G"):
                puzzle_list.append(new_grid)
                new_grid = []
                continue
            row = [int(num) for num in line[: 9]]
            new_grid.append(row)
        # To append last grid to puzzle list.
        puzzle_list.append(new_grid)
    print(f"{len(puzzle_list)} puzzles found")
    return puzzle_list


def update_cand_lists(cand_lists, loc, num):
    """
    Updates candidate lists based on location loc being num.
    """

    i_row, i_col = loc

    # Remove num from row i_row.
    for cand_list in cand_lists[i_row]:
        if num in cand_list:
            cand_list.remove(num)

    # Remove num from column i_col.
    for row in cand_lists:
        cand_list = row[i_col]
        if num in cand_list:
            cand_list.remove(num)

    # Find sub-grid row and sub-grid column corresponding to (i_row, i_col).
    i_sgrow = i_row // ORDER
    i_sgcol = i_col // ORDER

    # Remove num from sub-grid.
    for j_row in range(i_sgrow * ORDER, (i_sgrow + 1) * ORDER):
        for j_col in range(i_sgcol * ORDER, (i_sgcol + 1) * ORDER):
            cand_list = cand_lists[j_row][j_col]
            if num in cand_list:
                cand_list.remove(num)

    # Add back num to location (i_row, i_col).
    cand_lists[i_row][i_col] = [num]


def init_cand_lists(puzzle):
    """
    Returns initial candidate lists for a given puzzle.
    """

    size = ORDER ** 2
    cand_lists = [[[num for num in range(1, 1 + size)]
                   for _ in range(size)] for _ in range(size)]

    for i_row in range(size):
        for i_col in range(size):
            num = puzzle[i_row][i_col]
            if num == 0:
                continue
            update_cand_lists(cand_lists, (i_row, i_col), num)

    return cand_lists


def location_of_next_guess(cand_lists):
    """
    Returns minimum candidate list length and location of next guess.

    Returns 0, (None, None) if empty candidate list is found.
    Returns 1, (None, None) if all candidate lists are length 1.
    Returns n_cand_min, (i_row, i_col) otherwise. Here n_cand_min is the
    minimum candidate list length > 1 and (i_row, i_col) is the first location
    with a candidate list of this length.
    """

    i_row = None
    i_col = None
    n_cand_min = ORDER ** 2 + 1

    for j_row, row in enumerate(cand_lists):
        for j_col, cand_list in enumerate(row):
            len_cand_list = len(cand_list)
            # Update only if we have new shortest candidate list of length > 1.
            if 1 < len_cand_list < n_cand_min:
                n_cand_min = len_cand_list
                i_row = j_row
                i_col = j_col
            elif len_cand_list == 0:
                return 0, (None, None)

    # i_row and i_col are not updated if all cand_lists are of length 1.
    # This means the puzzle has been solved.
    if i_row is None:
        return 1, (None, None)

    return n_cand_min, (i_row, i_col)


def update_state_and_guess_lists(state_list, guess_list, loc):
    """
    Updates state_list and guess_list based on location of next guess.
    """

    i_row, i_col = loc
    # Creating new state by copying last state to update it in place.
    cand_lists = copy.deepcopy(state_list[-1])
    # Pick first number in candidate list of loc for next guess.
    num = cand_lists[i_row][i_col][0]
    update_cand_lists(cand_lists, loc, num)
    state_list.append(cand_lists)
    guess_list.append((loc, num))
    print(f"Guessing {num} at location {loc}")


def solver(puzzle):
    """
    Returns solution to a sudoku puzzle.
    """

    # state_list tracks sequence of candidate lists after successive guesses.
    state_list = [init_cand_lists(puzzle)]
    # guess_list tracks the locations of guesses and the numbers guessed.
    guess_list = []

    while True:

        # Get minimum candidate list length and location of next guess.
        # We get 0, (None, None) if empty candidate list is found.
        # We get 1, (None, None) if all candidate lists are length 1.
        # Otherwise, we get n_cand_min, (i_row, i_col). Here n_cand_min is the
        # minimum candidate list length > 1 and (i_row, i_col) is the first
        # location with a candidate list of this length.
        n_cand_min, loc = location_of_next_guess(state_list[-1])

        if n_cand_min == 0:
            # Delete last state and last guess and remove number which
            # was guessed from cand_list of location of last guess.
            _ = state_list.pop()
            last_loc, last_num = guess_list.pop()
            last_cand_list = state_list[-1][last_loc[0]][last_loc[1]]
            print(f"Removing {last_num} from location {last_loc}")
            last_cand_list.remove(last_num)
            # After removing last guess, we pick another number from the same
            # candidate list if it is non-empty.
            if len(last_cand_list) > 0:
                update_state_and_guess_lists(state_list, guess_list, last_loc)
            continue

        if n_cand_min == 1:
            # Puzzle solved!
            solved = [[cand_list[0] for cand_list in row]
                      for row in state_list[-1]]
            pprint.pprint(puzzle)
            print("Puzzle solved!")
            return solved

        # Make next guess and update state_list and guess_list.
        update_state_and_guess_lists(state_list, guess_list, loc)


def main():
    """
    Main function
    """

    puzzle_list = puzzles_from_file()

    puzzle = [[0, 7, 0, 0, 0, 0, 6, 0, 8],
              [0, 5, 0, 0, 4, 0, 0, 0, 0],
              [3, 0, 0, 0, 0, 6, 0, 0, 0],
              [0, 0, 4, 0, 0, 5, 0, 2, 0],
              [0, 0, 0, 0, 0, 0, 0, 9, 0],
              [9, 0, 2, 0, 0, 0, 3, 0, 0],
              [0, 0, 0, 3, 0, 0, 0, 0, 1],
              [0, 0, 0, 5, 0, 0, 0, 7, 3],
              [0, 0, 0, 2, 9, 4, 0, 0, 0]]

    pprint.pprint(solver(puzzle))
    # pprint.pprint(solver(puzzle_list[0]))


if __name__ == "__main__":
    main()
