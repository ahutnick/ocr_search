# File manipulation - remove duplicates
# Creates nested list from a playbill text file, with each word an entry in a
# line list, and each line an entry in the matrix list. Also includes helper
# functions for search.

import os
import re


class LocationMatrix(object):
    def __init__(self, file):
        # Text, parsed into lines
        self.text = self.file_opener(file)
        # Lines parsed into words
        self.matrix = self.matrix_maker(self.text)
        # Assigns each word its number, and stores its location
        self.values = self.get_values()
        # number of words
        self.words = len(self.values)

    # Calculates number of words from percent
    def calc_frac_percent(self, percent):
        return int(self.words * percent)

    # Checks to see if word[s] fall[s] before or after anchor
    def check_context(self, index, loc):
        # Loop through context locations
        for num in index:
            # Check to see if the row numbers match
            val = self.values[num]
            if val[0] == loc:
                return True
        return False

    # Check to see if anchor and context are together
    def check_together(self, index):
        matrix = self.matrix
        for num in index:
            val = self.values[num]
            # is the context found in the last entry of the first row
            # Or the first entry of the last row?
            if matrix[val[0]][val[1]] == matrix[0][len(matrix[0]) - 1]\
                    or matrix[val[0]][val[1]] == matrix[1][0]:
                return True
        return False

    # Check together when you only have before or after anchor
    def check_together_frac(self, index, test):
        matrix = self.matrix
        for num in index:
            val = self.values[num]
            if test == 0:
                i = len(matrix) - 1
                if matrix[val[0]][val[1]] == matrix[i][len(matrix[i]) - 1]:
                    return True
                return False
            elif test == 1:
                if matrix[val[0]][val[1]] == matrix[0][0]:
                    return True
                return False

    def file_opener(self, file):
        file = os.path.expanduser(file)
        text = ""
        with open(file, "r") as filename:
            text = filename.readlines()
            text = [line.rstrip('\n') for line in text]
            text = [x for x in text if x != ""]
            for line in range(len(text)):
                patt = re.compile("\.\.\.*")
                text[line] = re.split(patt, text[line])
                text[line] = " ".join(text[line])
        return text

    # Returns matrix as consisting of strings, replacing anchor word with a ^.
    def get_chars(self, index):
        matrix = self.matrix
        val = self.values[index]
        matrix[val[0]][val[1]] = "^"
        for i in range(len(matrix)):
            matrix[i] = " ".join(matrix[i])
            filter(lambda x: x.isalnum() or x == " " or x == "^", matrix[i])
        self.update_matrix()
        sym = self.get_index("\\^")
        return sym[0]

    def get_index(self, pattern):
        key = []
        for line in self.matrix:
            key += re.findall(pattern, " ".join(line))
        indices = []
        v = self.values
        if key != []:
            for word in range(len(key)):
                for i in range(len(v)):
                    term = self.matrix[v[i][0]][v[i][1]]
                    if key[word] in term \
                            and i not in indices:
                        indices.append(i)
            return indices

    def get_lines(self, index, n):
        val = self.values[index]
        if val[0] - n < 0:
            low = 0
        else:
            low = val[0] - n
        if val[0] + n >= len(self.matrix):
            high = len(self.matrix) - 1
        else:
            high = val[0] + n
        bef_line = self.matrix[low: val[0] + 1]
        bef_line[len(bef_line) - 1] = bef_line[len(bef_line) - 1][:val[1]]
        aft_line = self.matrix[val[0]: high + 1]
        aft_line[0] = aft_line[0][val[1] + 1:]
        bef_line = [item for sublist in bef_line for item in sublist]
        aft_line = [item for sublist in aft_line for item in sublist]
        self.matrix = [bef_line, aft_line]
        self.update_matrix()

    def get_n_range(self, n, index):
        if index + n >= self.words:
            higher_end = self.values[self.words - 1]
        else:
            higher_end = self.values[index + n]
        if index - n < 0:
            lower_end = self.values[0]
        else:
            lower_end = self.values[index - n]
        check = self.values[index]
        self.matrix[lower_end[0]] = self.matrix[lower_end[0]][lower_end[1]:]
        self.matrix[higher_end[0]] = \
            self.matrix[higher_end[0]][:higher_end[1] + 1]
        if check[0] == lower_end[0]:
            low = self.matrix[lower_end[0]]
            low = low[:check[1]]
        else:
            low = self.matrix[lower_end[0]: check[0] + 1]
            low[len(low) - 1] = low[len(low) - 1][:check[1]]
        if check[0] == higher_end[0]:
            high = self.matrix[higher_end[0]]
            high = high[check[1] + 1:]
        else:
            high = self.matrix[check[0]: higher_end[0] + 1]
            high[0] = high[0][check[1] + 1:]
        if type(high[0]) == list:
            high = [item for sublist in high for item in sublist]
        if type(low[0]) == list:
            low = [item for sublist in low for item in sublist]
        self.matrix = [low, high]
        self.update_matrix()

    def get_values(self):
        values = {}
        count = 0
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                # if self.matrix[i][j] != "":
                values[count] = [i, j]
                count += 1
        return values

    def matrix_maker(self, text):
        matrix = []
        for line in text:
            line = line.split()
            matrix.append(line)
        return matrix

    def nested_list_cracker(self, nest):
        sum = []
        for list in nest:
            for i in range(len(list)):
                sum.append(list[i])
        return sum

    def print_matrix(self):
        for line in self.matrix:
            print (" ".join(line))
        print ("Total words: {}".format(self.words))

    def print_line(self, index):
        val = self.values[index]
        print (self.matrix[val[0]])

    def refresh_matrix(self):
        self.matrix = self.matrix_maker(self.text)
        self.update_matrix()

    def re_split(self):
        matrix = self.matrix
        for line in range(len(matrix)):
                matrix[line] = matrix[line].split()
        self.update_matrix()

    def search(self, pattern):
        for line in self.matrix:
            if type(self.matrix[0]) == list:
                if re.search(pattern, " ".join(line)):
                    return True
            else:
                if re.search(pattern, line):
                    return True
        return False

    def split(self, index):
        val = self.values[index]
        last_low = self.matrix[val[0]]
        last_low = [last_low[:val[1]]]
        low = self.matrix[:val[0]] + last_low
        low = self.nested_list_cracker(low)
        first_high = self.matrix[val[0]]
        first_high = [first_high[val[1] + 1:]]
        high = first_high + self.matrix[val[0] + 1:]
        high = self.nested_list_cracker(high)
        self.matrix = [low, high]
        self.update_matrix()

    def trim_matrix(self, index, words):
        if index + words > self.words:
            lim = self.words - 1
        elif index + words < 0:
            lim = 0
        else:
            lim = index + words
        val = self.values[index]
        val_lim = self.values[lim]
        if lim < index:
            self.matrix = self.matrix[val_lim[0]: val[0] + 1]
            self.matrix[0] = self.matrix[0][val_lim[1]:]
            self.matrix[len(self.matrix) - 1] = \
                self.matrix[len(self.matrix) - 1][:val[1]]
            if self.matrix[len(self.matrix) - 1] == []:
                self.matrix.remove(self.matrix[len(self.matrix) - 1])
        else:
            self.matrix = self.matrix[val[0]: val_lim[0] + 1]
            self.matrix[0] = self.matrix[0][val[1] + 1:]
            self.matrix[len(self.matrix) - 1] = \
                self.matrix[len(self.matrix) - 1][:val_lim[1] + 1]
        self.update_matrix()

    def trim_matrix_full(self, index, words):
        if index + words > self.words:
            lim = self.words - 1
        elif index + words < 0:
            lim = 0
        else:
            lim = index + words
        val = self.values[index]
        val_lim = self.values[lim]
        if lim < index:
            self.matrix = self.matrix[val_lim[0]: val[0] + 1]
            self.matrix[0] = self.matrix[0][val_lim[1]:]
            self.matrix[len(self.matrix) - 1] = \
                self.matrix[len(self.matrix) - 1][:val[1]]
            if self.matrix[len(self.matrix) - 1] == []:
                self.matrix.remove(self.matrix[len(self.matrix) - 1])
        else:
            self.matrix = self.matrix[val[0]: val_lim[0] + 1]
            self.matrix[0] = self.matrix[0][val[1]:]
            self.matrix[len(self.matrix) - 1] = \
                self.matrix[len(self.matrix) - 1][:val_lim[1] + 1]
        self.update_matrix()

    def update_matrix(self):
        self.num_rows = len(self.matrix)
        self.values = self.get_values()
        self.words = len(self.values)
