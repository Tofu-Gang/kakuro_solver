__author__ = "Tofu Gang"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsView, QToolBar, QAction, QFileDialog, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QIcon, QKeySequence
from src.model import Model
import res.resources_rc



################################################################################

class MainWindow(QMainWindow):
    SQUARE_SIZE = 50

################################################################################

    def __init__(self, parent=None):
        """
        It creates main window of the application. Kakuro model isn't initiali-
        zed here, though.
        """

        super(MainWindow, self).__init__(parent)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.model = None

        self.openAction \
            = QAction(QIcon(':/icons/open.png'), 'Open file', self)
        self.openAction.setShortcut(QKeySequence.Open)
        self.openAction.triggered.connect(self._loadFromFile)
        self.solveAction \
            = QAction(QIcon(':/icons/solve.png'), 'Solve automatically', self)
        self.solveAction.triggered.connect(self._solve)
        self.solveAction.setEnabled(False)
        self.rawHeuristicAction \
            = QAction(QIcon(':/icons/1.png'), 'Raw heuristic', self)
        self.rawHeuristicAction.triggered.connect(self._rawHeuristic)
        self.rawHeuristicAction.setEnabled(False)
        self.contextSolutionsHeuristicAction \
            = QAction(QIcon(':/icons/2.png'), 'Context solutions heuristic',
                      self)
        self.contextSolutionsHeuristicAction.triggered.connect(
            self._contextSolutionsHeuristic)
        self.contextSolutionsHeuristicAction.setEnabled(False)
        self.generalizedRepetitionHeuristicAction \
            = QAction(QIcon(':/icons/3.png'),
                      'Generalized repetition heuristic', self)
        self.generalizedRepetitionHeuristicAction.triggered.connect(
            self._generalizedRepetitionHeuristic)
        self.generalizedRepetitionHeuristicAction.setEnabled(False)

        self.toolBar = QToolBar('toolbar', self)
        self.addToolBar(self.toolBar)
        self.toolBar.addAction(self.openAction)
        self.toolBar.addAction(self.solveAction)
        self.toolBar.addAction(self.rawHeuristicAction)
        self.toolBar.addAction(self.contextSolutionsHeuristicAction)
        self.toolBar.addAction(self.generalizedRepetitionHeuristicAction)

################################################################################

    def _loadFromFile(self):
        """
        It opens a dialog to load a xml file, which is then parsed and shown
        in the main window.
        """

        fileName = QFileDialog.getOpenFileName(self, 'Open file', '../puzzles/')[0]
        # continue only if some file was really loaded
        if len(fileName) > 0:
            self.model = Model(fileName)
            self._showModel()
            self.rawHeuristicAction.setEnabled(True)
            self.solveAction.setEnabled(True)

################################################################################

    def _showModel(self):
        """
        Graphical representation of the puzzle model is created here.
        """

        self.scene.clear()

        for i in range(self.model.height):

            for j in range(self.model.width):
                square = self.model.grid[i][j]

                if square is None:
                    self._showFiller(i, j)
                elif isinstance(square, dict):
                    self._showClue(i, j)
                elif isinstance(square, list):
                    self._showLetter(i, j)
                else:
                    #TODO: error
                    pass
        self.resize((self.model.width + 1) * self.SQUARE_SIZE,
                    (self.model.height + 1) * self.SQUARE_SIZE)

################################################################################

    def _showFiller(self, i, j):
        """
        Graphical representation of a filler square is created here.
        """

        self.scene.addRect(j * self.SQUARE_SIZE, i * self.SQUARE_SIZE,
                           self.SQUARE_SIZE, self.SQUARE_SIZE,
                           QPen(Qt.black, 1, Qt.SolidLine),
                           QBrush(Qt.gray, Qt.SolidPattern))

################################################################################

    def _showClue(self, i, j):
        """
        Graphical representation of a summation square is created here.
        """

        x = j * self.SQUARE_SIZE
        y = i * self.SQUARE_SIZE
        self.scene.addRect(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE,
                           QPen(Qt.black, 1, Qt.SolidLine),
                           QBrush(Qt.gray, Qt.SolidPattern))
        self.scene.addLine(x, y, x + self.SQUARE_SIZE,
                           y + self.SQUARE_SIZE,
                           QPen(Qt.black, 1, Qt.SolidLine))

        hTextItem = QGraphicsTextItem('')
        vTextItem = QGraphicsTextItem('')
        horizontal = (self.model.grid[i][j])[self.model.HORIZONTAL]
        vertical = (self.model.grid[i][j])[self.model.VERTICAL]

        if horizontal is not None:
            hTextItem.setPlainText(str(horizontal))
        if vertical is not None:
            vTextItem.setPlainText(str(vertical))

        hTextItem.setPos(x + self.SQUARE_SIZE / 2,
                         y + self.SQUARE_SIZE / 4)
        vTextItem.setPos(x + self.SQUARE_SIZE / 4,
                         y + self.SQUARE_SIZE / 2)
        self.scene.addItem(hTextItem)
        self.scene.addItem(vTextItem)

################################################################################

    def _showLetter(self, i, j):
        """
        Graphical representation of a square to fill is created here.
        """

        x = j * self.SQUARE_SIZE
        y = i * self.SQUARE_SIZE
        self.scene.addRect(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE,
                           QPen(Qt.black, 1, Qt.SolidLine), QBrush(Qt.NoBrush))

        square = self.model.grid[i][j]

        if len(square) == 1:
            numberTextItem = QGraphicsTextItem(str(square[0]))
            numberTextItem.setDefaultTextColor(Qt.darkGreen)
            numberTextItem.setPos(x + self.SQUARE_SIZE / 3,
                                  y + self.SQUARE_SIZE / 3)
            self.scene.addItem(numberTextItem)
        else:

            for number in square:
                numberTextItem = QGraphicsTextItem(str(number))
                xPos = x + ((number - 1) % 3) * self.SQUARE_SIZE / 3
                yPos = y + ((number - 1) / 3) * self.SQUARE_SIZE / 3
                numberTextItem.setPos(xPos, yPos)
                self.scene.addItem(numberTextItem)

################################################################################

    def _solve(self):
        """
        It solves the puzzle automatically.
        """

        self.model.solve()
        self._showModel()
        # the puzzle is solved, disable everything so we can just load another
        # puzzle
        self.solveAction.setEnabled(False)
        self.rawHeuristicAction.setEnabled(False)
        self.contextSolutionsHeuristicAction.setEnabled(False)
        self.generalizedRepetitionHeuristicAction.setEnabled(False)

################################################################################

    def _rawHeuristic(self):
        """
        It applies raw heuristic on the puzzle.
        """

        self.model.rawHeuristic()
        self._showModel()
        if self.model.isSolved():
            # the puzzle is solved, disable everything so we can just load
            # another puzzle
            self.solveAction.setEnabled(False)
            self.rawHeuristicAction.setEnabled(False)
            self.contextSolutionsHeuristicAction.setEnabled(False)
            self.generalizedRepetitionHeuristicAction.setEnabled(False)
        else:
            # raw heuristic can be run only once (at least it has effect only on
            # the first run)
            self.rawHeuristicAction.setEnabled(False)
            # now we can enable two more precise heuristics
            self.contextSolutionsHeuristicAction.setEnabled(True)
            self.generalizedRepetitionHeuristicAction.setEnabled(True)

################################################################################

    def _contextSolutionsHeuristic(self):
        """
        It applies context solutions heuristic on the puzzle.
        """

        modelChanged = self.model.contextSolutionsHeuristic()
        self._showModel()
        if self.model.isSolved():
            # the puzzle is solved, disable everything so we can just load
            # another puzzle
            self.solveAction.setEnabled(False)
            self.rawHeuristicAction.setEnabled(False)
            self.contextSolutionsHeuristicAction.setEnabled(False)
            self.generalizedRepetitionHeuristicAction.setEnabled(False)
        else:
            # if any changes were made, leave the action enabled, disable it otherwise
            self.contextSolutionsHeuristicAction.setEnabled(modelChanged)
            # if any changes were made, enable the repetition heuristic, leave it as
            # it is otherwise (it may have not be used at all and in this case we
            # want to have it enabled)
            if modelChanged:
                self.generalizedRepetitionHeuristicAction.setEnabled(True)

################################################################################

    def _generalizedRepetitionHeuristic(self):
        """
        It applies generalized repetition heuristic on the puzzle.
        """

        modelChanged = self.model.generalizedRepetitionHeuristic()
        self._showModel()
        if self.model.isSolved():
            # the puzzle is solved, disable everything so we can just load
            # another puzzle
            self.solveAction.setEnabled(False)
            self.rawHeuristicAction.setEnabled(False)
            self.contextSolutionsHeuristicAction.setEnabled(False)
            self.generalizedRepetitionHeuristicAction.setEnabled(False)
        else:
            # if any changes were made, leave the action enabled, disable it otherwise
            self.generalizedRepetitionHeuristicAction.setEnabled(modelChanged)
            # if any changes were made, enable the context solutions heuristic,
            # leave it as it is otherwise (it may have not be used at all and in
            # this case we want to have it enabled)
            if modelChanged:
                self.contextSolutionsHeuristicAction.setEnabled(True)

################################################################################