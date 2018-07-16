import sys
import re
from LocationMatrix import LocationMatrix as location


# Check to see if the context word(s) are even there before checking where
# they are. Returns list of 3 booleans - is the word before the anchor,
# after the anchor, and / or right next to the anchor? Has special option for
# location search, as before or after may be rendered moot. Takes in the
# matrix, the context search term, and a private indicator of if the matrix
# is from a location search, and whether to test the matrix for before or
# after.
def get_bools(matrix, context, test):
    # compile the context term
    # For list of regex characters, see https://github.com/tartley/python-regex
    # -cheatsheet/blob/master/cheatsheet.rst
    context = re.compile(context)
    # Is the term even there? Should we even bother?
    if matrix.search(context):
        # Yes, let's get the locations for all the times the term shows up
        terms = matrix.get_index(context)
        # Any other test
        if test == "":
            # Search before the anchor
            bef = matrix.check_context(terms, 0)
            # Search after the anchor
            aft = matrix.check_context(terms, 1)
            # Search with the anchor
            tog = matrix.check_together(terms)
        # Location test option - search only before the anchor
        elif test == 0:
            bef = True
            aft = False
            tog = matrix.check_together_frac(terms, 0)
        # Location test option - search only after the anchor
        elif test == 1:
            bef = False
            aft = True
            tog = matrix.check_together_frac(terms, 1)
        # Return the results
        return [bef, aft, tog]
    else:
        #  Context not present - return False
        return [False, False, False]


# Search for the context term within n words of the anchor term
# Currently only searches for first instance of anchor term.
def word_windows(anchor, context, n, matrix):
    #  get the index of the anchor                  |
    #  check for proper indices (pull up chunks)    | The tricky part - may
    #  run proper indices                           | add in later
    # Restart the matrix
    matrix.refresh_matrix()
    # Are the anchor term and the context term even there?
    if matrix.search(anchor) and matrix.search(context):
        # Get index for the anchor
        anchors = matrix.get_index(anchor)
        for index in anchors:
            # Cuts the matrix down to n words before and n words after anchor
            matrix.refresh_matrix()
            matrix.print_line(index)
            test = input("Search this instance Y/N?: ")
            if test == "Y" or test == "y":
                matrix.get_n_range(n, index)
                results = get_bools(matrix, context, "")
                print_results("Word Window", results)
    else:
        # Not Here, set / print  False
        results = [False, False, False]
        print_results("Word Window", results)


# Search for context term n chars before and n chars after anchor term
def character_windows(anchor, context, n, matrix):
    # Restart the matrix
    matrix.refresh_matrix()
    # Is the term there?
    if matrix.search(anchor) and matrix.search(context):
        # Get anchor index
        anchors = matrix.get_index(anchor)
        for index in anchors:
            matrix.refresh_matrix()
            matrix.print_line(index)
            test = input("Search this instance Y/N?: ")
            if test == "Y" or test == "y":
                # Translate the matrix lines to strings, replace anchor with ^
                sym = matrix.get_chars(index)
                # Trim the matrix into chunk consisting of n characters before
                # and n characters after ^
                matrix.trim_matrix_full(sym - n, 2 * n)
                # resplit the lines into lists of words
                matrix.re_split()
                # Get the new index of ^
                sym = matrix.get_index("\\^")
                # Split the matrix into before ^ and after ^, removing ^
                matrix.split(sym[0])
                # Get / print results
                results = get_bools(matrix, context, "")
                print_results("Character Window: ", results)
    else:
        # Not here, get / print results
        results = [False, False, False]
        print_results("Character Window: ", results)


# Search for term within n lines before and after anchor
def line_windows(anchor, context, n, matrix):
    # Restart matrix
    matrix.refresh_matrix()
    # Is it there?
    if matrix.search(anchor) and matrix.search(context):
        # Get index of anchor
        anchors = matrix.get_index(anchor)
        for index in anchors:
            matrix.refresh_matrix()
            matrix.print_line(index)
            test = input("Search this instance Y/N?: ")
            if test == "Y" or test == "y":
                #  Split the matrix into lines before and after anchor
                matrix.get_lines(index, n)
                # Get / print  results
                results = get_bools(matrix, context, "")
                print_results("Line Window", results)
    else:
        # Not here - Get / print / return results
        results = [False, False, False]
        print_results("Line Window", results)
        return results


# Search the entire playbill for the context term in regard to the anchor term
def playbill_windows(anchor, context, matrix):
    # Restart matrix
    matrix.refresh_matrix()
    # Are they there?
    if matrix.search(anchor) and matrix.search(context):
        # Get anchor index
        anchors = matrix.get_index(anchor)
        for index in anchors:
            matrix.print_line(index)
            test = input("Search this instance Y/N?: ")
            if test == "Y" or test == "y":
                # Split matrix into before anchor and after anchor
                matrix.split(index)
                # get / print / return results
                results = get_bools(matrix, context, "")
                print_results("Playbill Window", results)
    else:
        # Not there - get / print / return results
        results = [False, False, False]
        print_results("Playbill Window", results)
        return results


# Takes in index and percent - index = where to start, percent = how much to
# use. Index - enter number of words, Percent - number between 0 and 1. If no
# index entered, runs the program using the anchor as the starting / ending
# point.
def location_search(anchor, index, context, percent, matrix):
    # Restart matrix
    matrix.refresh_matrix()
    # Are they there?
    if matrix.search(anchor) and matrix.search(context):
        # No index - use anchor as start / end point
        # get words
        words = matrix.calc_frac_percent(percent)
        if index == "":
            # get anchor index
            anchors = matrix.get_index(anchor)
            for index in anchors:
                matrix.print_line(index)
                test = input("Search this instance Y/N?: ")
                if test == "Y" or test == "y":
                    # trim matrix to before or after anchor (+ percent = aft,
                    # - = bef)
                    matrix.trim_matrix(index, words)
                    # Get results for after ancher
                    if percent > 0:
                        results = get_bools(matrix, context, 1)
                    # Get results for before anchor
                    else:
                        results = get_bools(matrix, context, 0)
                    print_results("Location Search", results)
        # Index present
        else:
            # trim matrix to number of words before / after index point
            matrix.trim_matrix_full(index, words)
            # Is anchor present here?
            if matrix.search(anchor):
                # Get anchor index
                anchors = matrix.get_index(anchor)
                for index in anchors:
                    matrix.print_line(index)
                    test = input("Search here Y/N?: ")
                    if test == "Y" or test == "y":
                        # Split to before anchor and after anchor
                        matrix.split(anchors[0])
                        # Get results
                        results = get_bools(matrix, context, "")
                        print_results("Location Search", results)
            # Anchor not present - results = False
            else:
                results = [False, False, False]
                # Print results
                print_results("Location Search", results)
    else:
        # Not present - get / print / results
        results = [False, False, False]
        print_results("Location Search", results)
        return results


# Print the results in an orderly fashion. Takes in which test, and the results
def print_results(test, results):
    print ("{} Results:".format(test))
    print("\tBefore:   {}".format(results[0]))
    print("\tAfter:    {}".format(results[1]))
    print("\tTogether: {}".format(results[2]))


# Get the variables and run the tests!
def main():
    file = sys.argv[1]
    anchor = input("Please enter anchor term: ")
    context = input("Please enter context term: ")
    n = int(input("Please enter the character / word window (Or enter 0 to \
    ignore these tests): "))
    index = input("Please enter where you would like to start your \
    location search (enter 0 to start from the beginning or leave blank \
    to use the anchor word as an index): ")
    if index != "":
        index = int(index)
    percent = float(input("Please enter what percentage of the playbill you \
    would like to search (only affects location search): "))
    matrix = location(file)
    word_windows(anchor, context, n, matrix)
    character_windows(anchor, context, n, matrix)
    line_windows(anchor, context, n, matrix)
    playbill_windows(anchor, context, matrix)
    location_search(anchor, index, context, percent, matrix)


if __name__ == "__main__":
    main()
