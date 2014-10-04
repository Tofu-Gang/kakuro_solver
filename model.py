# -*- coding: utf-8 -*-
__author__ = "Jakub Franěk"

from xml.etree.ElementTree import parse
from itertools import combinations, product
from collections import defaultdict

################################################################################

class Model(object):
    TAG_KAKURO = 'kakuro'
    TAG_ROW = 'row'
    TAG_FILLER = 'filler'
    TAG_CLUE = 'clue'
    TAG_LETTER = 'letter'

    ATTR_HORIZONTAL = 'horizontal'
    ATTR_VERTICAL = 'vertical'

    ORIENTATION_HORIZONTAL = 'horizontal'
    ORIENTATION_VERTICAL = 'vertical'

################################################################################
############################ model creation methods ############################
################################################################################

    def __init__(self, fileName):
        """
        Creates a model of Kakuro puzzle by parsing a xml file in the given path.
        """

        self.grid = []
        self.width = None
        self.height = None
        self._loadFromXml(fileName)

################################################################################

    def _loadFromXml(self, fileName):
        """
        Loads puzzle model from xml file.
        """

        kakuroFile = open(fileName, 'r')
        tree = parse(fileName)
        kakuro = tree.getroot()

        if kakuro.tag == self.TAG_KAKURO:
            self.height = len(kakuro)

            for row in kakuro:
                if row.tag == self.TAG_ROW:

                    if self.width is None:
                        self.width = len(row)
                    if self.width is not None and self.width != len(row):
                        # TODO: parse error, rows not equally long
                        pass
                    modelRow = []

                    for element in row:
                        if element.tag == self.TAG_FILLER:
                            modelRow.append(None)
                        if element.tag == self.TAG_CLUE:
                            horizontal = element.attrib.get(self.ATTR_HORIZONTAL)
                            vertical = element.attrib.get(self.ATTR_VERTICAL)
                            modelRow.append({self.ATTR_HORIZONTAL: horizontal,
                                             self.ATTR_VERTICAL: vertical})
                        if element.tag == self.TAG_LETTER:
                            modelRow.append([number for number in range(1, 10)])

                    self.grid.append(modelRow)

        kakuroFile.close()

################################################################################
############################## model info methods ##############################
################################################################################

    def _word(self, i, j, orientation, hashable=True):
        """
        Returns all squares that belong to the word (horizontal or vertical,
        depending on the given orientation) which is the square on the i-th row
        and j-th column part of. Returns None if the square is not a letter.
        Return value comes in two possible variants: hashable and not hashable.
        Hashable variant can be used as dictionary key, which is needed in the
        generalized repetiton heuristic. Not hashable variant cannot be used as
        such, but provides direct changes to the grid through the word object
        since it is mutable. Since the hashable variant is used more often and
        it is more optimized for read-only operations, this is used as a default
        value.
        """

        try:
            while isinstance(self.grid[i][j], list) \
              and not isinstance(self.grid[i][j], dict):

                if orientation == self.ORIENTATION_HORIZONTAL:
                    # go to the left in  row until finding a clue
                    j -= 1
                if orientation == self.ORIENTATION_VERTICAL:
                    # go up in the column until finding a clue
                    i -= 1

            word = []
            while True:

                if orientation == self.ORIENTATION_HORIZONTAL:
                    # go to the right in the row until going through the whole word
                    j += 1
                if orientation == self.ORIENTATION_VERTICAL:
                    # go down in the column until going through the whole word
                    i += 1

                if i == self.height or j == self.width \
                  or not isinstance(self.grid[i][j], list):
                    break
                else:
                    if hashable:
                        word.append(tuple(self.grid[i][j]))
                    else:
                        word.append(self.grid[i][j])

            if hashable:
                return tuple(word)
            else:
                return word

        except TypeError:
            return None

################################################################################

    def _wordDuplicateLetters(self, i, j, orientation):
        """
        Returns tuple of duplicate squares of the word (horizontal or vertical,
        depending on the given orientation) which is the square in the i-th row
        and j-th column part of. One duplicate square is also a tuple which
        consists of two tuples. First are possible numbers in the duplicate
        square and second are indexes of the square in the word (not in the
        model grid).
        """

        duplicates = defaultdict(list)

        for index, item in enumerate(self._word(i, j, orientation)):
            duplicates[item].append(index)

        return tuple((key, tuple(indexes)) for key, indexes in duplicates.items())

################################################################################

    def _wordClue(self, i, j, orientation):
        """
        Returns clue for the word (horizontal or vertical, depending on the
        given orientation) which is the square in the i-th row and the j-th
        column part of. Returns None if the square is not a letter.
        """

        try:
            while isinstance(self.grid[i][j], list) \
              and not isinstance(self.grid[i][j], dict):

                if orientation == self.ORIENTATION_HORIZONTAL:
                    # go to the left in the row until finding a clue
                    j -= 1
                if orientation == self.ORIENTATION_VERTICAL:
                    # go up in the column until finding a clue
                    i -= 1

            if orientation == self.ORIENTATION_HORIZONTAL:
                return int((self.grid[i][j])[self.ATTR_HORIZONTAL])
            if orientation == self.ORIENTATION_VERTICAL:
                return int((self.grid[i][j])[self.ATTR_VERTICAL])

        except TypeError:
            return None

################################################################################

    def _isWordSolved(self, i, j, orientation):
        """
        Returns True if the word (horizontal or vertical, depending on the given
        orientation) which is the square in the i-th row and the j-th column
        part of is already solved. Returns False otherwise.
        """

        return all(len(square) == 1 for square in self._word(i, j, orientation))

################################################################################

    def _cheatSheet(self, length, clue):
        """
        Returns list of all possible solutions for a word with given length and
        clue. It is computed with simple combinations rather than hard-coding
        the cheat sheet.
        """

        return tuple(combination for combination in combinations([number for number in range(1, 10)], length)
                     if sum(combination) == clue)

################################################################################

    def _wordSolutions(self, i, j, orientation):
        """
        It returns all possible combinations that are solutions for the word
        (horizontal or vertical, depending on the given orientation) which is
        the square in the i-th row and the j-th column part of.
        """

        clue = self._wordClue(i, j, orientation)
        word = self._word(i, j, orientation)
        # get all combinations of possible numbers from letters, including those
        # with repeating numbers; exclude the ones where some numbers are more
        # than once or the ones which summation is not equal to the clue of the
        # word
        return tuple(combination for combination in tuple(product(*word))
                     if len(set(combination)) == len(combination) \
                       and sum(combination) == clue)

################################################################################

    def isSolved(self):
        """
        Returns True if the puzzle is solved, False otherwise.
        """

        for i in range(self.height):

            for j in range(self.width):
                square = self.grid[i][j]

                if isinstance(square, list) and len(square) > 1:
                    return False

        return True

################################################################################
######################## heuristic applications methods ########################
################################################################################

    def _applyRawHeuristicRule(self, i, j, orientation):
        """
        It applies raw heuristic rule for possible numbers exclusion on the
        square in the i-th row and j-th column.
        It excludes those possible numbers which are not part of any solution
        taken from the cheat sheet.
        """

        # get params of the word which is the square in the i-th row and j-th
        # column part of
        wordLength = len(self._word(i, j, orientation))
        wordClue = self._wordClue(i, j, orientation)
        # now we can peek to cheat sheet to see every possible solution of the
        # word with given lengths and clues
        solutions = self._cheatSheet(wordLength, wordClue)
        # get all numbers which appear in at least one possible solution for
        # the word
        possibleNumbers = set().union(*solutions)
        # now we can exclude numbers which does not appear in any of all the
        # possible solutions
        self.grid[i][j] = [number for number in self.grid[i][j]
                           if number in possibleNumbers]

################################################################################

    def _applySolutionsRule(self, i, j, orientation):
        """
        It applies possible solutions rule for possible numbers exclusion on the
        whole word (horizontal or vertical, depending on the given orientation)
        which is the square in the i-th row and j-th column part of.
        It gets all possible combinations of numbers which are solutions for the
        word and excludes numbers which are not part of it.
        It returns True if any changes were made. If running this method leaves
        the model unchanged, it returns False.
        """

        word = self._word(i, j, orientation, hashable=False)
        combs = self._wordSolutions(i, j, orientation)
        modelChanged = False

        for i in range(len(word)):
            square = word[i]

            for number in range(1, 10):

                if number in square and number not in tuple(comb[i] for comb in combs):
                    square.remove(number)
                    modelChanged = True

        return modelChanged

################################################################################

    def _applyDuplicatesRule(self, i, j, orientation):
        """
        It applies generalized duplicates rule for possible numbers exclusion on
        the whole word (horizontal or vertical, depending on the given
        orientation) which is the square in the i-th row and j-th column part
        of.
        The rule states that if there are N same letters in the word with N
        possible numbers (N >= 1), we can exclude those numbers from other
        letters in the word.
        It returns True if any changes were made. If running this method leaves
        the model unchanged, it returns False.
        """

        duplicates = self._wordDuplicateLetters(i, j, orientation)
        word = self._word(i, j, orientation, hashable=False)
        modelChanged = False

        for i in range(len(word)):
            square = word[i]

            # go through every duplicate letter in the word
            for duplicate in duplicates:

                # if the numbers exclusion rule can be applied
                if len(duplicate[0]) == len(duplicate[1]) and i not in duplicate[1]:

                    # apply the rule
                    for number in duplicate[0]:

                        if number in square:
                            square.remove(number)
                            modelChanged = True

        return modelChanged

################################################################################
########################### solving wrapper methods ############################
################################################################################

    def rawHeuristic(self):
        """
        Applies the most raw heuristic. It excludes numbers from letters which
        are not part of any possible word solution. All possible solutions for
        each word are obtained from cheat sheet. It takes effect only on the
        first run since it works only with individual squares in no context.
        """

        for i in range(self.height):

            for j in range(self.width):

                if isinstance(self.grid[i][j], list):
                    self._applyRawHeuristicRule(i, j, self.ORIENTATION_HORIZONTAL)
                    self._applyRawHeuristicRule(i, j, self.ORIENTATION_VERTICAL)

################################################################################

    def contextSolutionsHeuristic(self):
        """
        Applies more precise heuristic. It determines all possible solutions for
        the whole word excluding the ones which are not possible for each letter
        in the word. It works in a context of the whole word and since the
        heuristic changes this context, it should be run for several times until
        no changes are made.

        It returns True if any changes were made. If running this heuristic
        leaves the model unchanged, it returns False.
        """

        modelChanged = False

        for i in range(self.height):

            for j in range(self.width):

                if isinstance(self.grid[i][j], list):

                    if not self._isWordSolved(i, j, self.ORIENTATION_HORIZONTAL):
                        result = self._applySolutionsRule(i, j, self.ORIENTATION_HORIZONTAL)
                        if result == True: modelChanged = True

                    if not self._isWordSolved(i, j, self.ORIENTATION_VERTICAL):
                        result = self._applySolutionsRule(i, j, self.ORIENTATION_VERTICAL)
                        if result == True: modelChanged = True

        return modelChanged

################################################################################

    def generalizedRepetitionHeuristic(self):
        """
        It applies more precise heuristic which covers letters duplicates.
        If there are N same letters in the word with N possible numbers
        (N >= 1), we can exclude those numbers from other letters in the word.
        It returns True if any changes were made. If running this heuristic
        leaves the model unchanged, it returns False.
        """

        modelChanged = False

        for i in range(self.height):

            for j in range(self.width):

                if isinstance(self.grid[i][j], list):

                    if not self._isWordSolved(i, j, self.ORIENTATION_HORIZONTAL):
                        result = self._applyDuplicatesRule(i, j, self.ORIENTATION_HORIZONTAL)
                        if result == True: modelChanged = True

                    if not self._isWordSolved(i, j, self.ORIENTATION_VERTICAL):
                        result = self._applyDuplicatesRule(i, j, self.ORIENTATION_VERTICAL)
                        if result == True: modelChanged = True

        return modelChanged

################################################################################

    def solve(self):
        """
        It uses all three known heuristics to solve the puzzle automatically.
        """

        self.rawHeuristic()

        while self.contextSolutionsHeuristic() or self.generalizedRepetitionHeuristic():
            pass

################################################################################