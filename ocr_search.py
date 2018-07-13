import sys
import re
from LocationMatrix import LocationMatrix as location


def get_bools(matrix, context, test):
    context = re.compile(context)
    if matrix.search(context):
        terms = matrix.get_index(context)
        if test == "":
            bef = matrix.check_context(terms, 0)
            aft = matrix.check_context(terms, 1)
            tog = matrix.check_together(terms)
        elif test == 0:
            bef = True
            aft = False
            tog = matrix.check_together_frac(terms, 0)
        elif test == 1:
            bef = False
            aft = True
            tog = matrix.check_together_frac(terms, 1)
        return [bef, aft, tog]
    else:
        return [False, False, False]


def word_windows(anchor, context, n, matrix):
    #  get the index of the anchor                  |
    #  check for proper indices (pull up chunks)    | The tricky part - may
    #  run proper indices                           | add in later
    matrix.refresh_matrix()
    if matrix.search(anchor) and matrix.search(context):
        anchors = matrix.get_index(anchor)
        matrix.get_n_range(n, anchors[0])
        results = get_bools(matrix, context, "")
        print_results("Word Window", results)
        return results
    else:
        results = [False, False, False]
        print_results("Word Window", results)
        return results


def character_windows(anchor, context, n, matrix):
    matrix.refresh_matrix()
    if matrix.search(anchor) and matrix.search(context):
        anchors = matrix.get_index(anchor)
        sym = matrix.get_chars(anchors[0])
        matrix.trim_matrix_full(sym - n, 2 * n)
        matrix.re_split()
        sym = matrix.get_index("\\^")
        matrix.split(sym[0])
        results = get_bools(matrix, context, "")
        print_results("Character Window: ", results)
        return results
    else:
        results = [False, False, False]
        print_results("Character Window: ", results)
        return results


def line_windows(anchor, context, n, matrix):
    matrix.refresh_matrix()
    if matrix.search(anchor) and matrix.search(context):
        anchors = matrix.get_index(anchor)
        matrix.get_lines(anchors[0], n)
        results = get_bools(matrix, context, "")
        print_results("Line Window", results)
        return results
    else:
        results = [False, False, False]
        print_results("Line Window", results)
        return results


def playbill_windows(anchor, context, matrix):
    matrix.refresh_matrix()
    if matrix.search(anchor) and matrix.search(context):
        anchors = matrix.get_index(anchor)
        matrix.split(anchors[0])
        results = get_bools(matrix, context, "")
        print_results("Playbill Window", results)
        return results
    else:
        results = [False, False, False]
        print_results("Playbill Window", results)
        return results


def location_search(anchor, index, context, percent, matrix):
    matrix.refresh_matrix()
    if matrix.search(anchor) and matrix.search(context):
        if index == "":
            index = matrix.get_index(anchor)
            words = matrix.calc_frac_percent(percent)
            matrix.trim_matrix(index[0], words)
            if percent > 0:
                results = get_bools(matrix, context, 1)
            else:
                results = get_bools(matrix, context, 0)
        else:
            words = matrix.calc_frac_percent(percent)
            matrix.trim_matrix_full(index, words)
            if matrix.search(anchor):
                anchors = matrix.get_index(anchor)
                matrix.split(anchors[0])
                results = get_bools(matrix, context, "")
            else:
                results = [False, False, False]
        print_results("Location Search", results)
        return results
    else:
        results = [False, False, False]
        print_results("Location Search", results)
        return results


def print_results(test, results):
    print ("{} Results:".format(test))
    print("\tBefore:   {}".format(results[0]))
    print("\tAfter:    {}".format(results[1]))
    print("\tTogether: {}".format(results[2]))


# To be used for final - probably need to change for command line?
# file = input("Please input filename here: ")
# anchor = input("Please enter anchor term: ")
# context = input("Please enter search term(s): ")
# n = input("Please input the window size for before and after the anchor term"
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
    results_1 = word_windows(anchor, context, n, matrix)
    results_2 = character_windows(anchor, context, n, matrix)
    results_3 = line_windows(anchor, context, n, matrix)
    results_4 = playbill_windows(anchor, context, matrix)
    results_5 = location_search(anchor, index, context, percent, matrix)
    results = [results_1, results_2, results_3, results_4, results_5]
    return results


if __name__ == "__main__":
    main()
