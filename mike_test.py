import unittest

from mike import *

RED = ButtonColor(3,0)
GREEN = ButtonColor(0,3)
YELLOW = ButtonColor(1,2)
ORANGE = ButtonColor(3,3)

class ButtonColorTests(unittest.TestCase):

    def test_equality(self):
        self.assertEqual(ButtonColor(3,3), ButtonColor(3,3))

    def test_inequality(self):
        self.assertNotEqual(ButtonColor(3,3), ButtonColor(3,2))

class SquareTests(unittest.TestCase):
    def setUp(self):
        self.color1= ButtonColor(3,3)
        self.color2 = ButtonColor(3,2)
        
    def test_equality(self):
        self.assertEqual(Square(3,3, self.color1), Square(3,3, self.color1))

    def test_inequality(self):
        self.assertNotEqual(Square(3,3, self.color1), Square(3,3, self.color2))

    def test_inequality(self):
        self.assertNotEqual(Square(3,3, self.color1), Square(3,2, self.color1))


class BoardLogicTests(unittest.TestCase):

    def setUp(self):
        self.virtualBoard = VirtualBoard()
        self.boardLogic = BoardLogic(self.virtualBoard)

    def test_in_bounds(self):
        self.assertTrue(self.boardLogic.inBounds(0,0))
        self.assertTrue(self.boardLogic.inBounds(7,7))
        self.assertFalse(self.boardLogic.inBounds(-1,7))
        self.assertFalse(self.boardLogic.inBounds(1,-1))
        self.assertFalse(self.boardLogic.inBounds(8,7))
        self.assertFalse(self.boardLogic.inBounds(7,8))

    def test_adjacent_squares(self):
        squares = self.boardLogic.squaresAdjacentTo(3,3)
        self.assertEqual(len(squares), 8)
        
    def test_adjacent_squares_to_corner(self):
        squares = self.boardLogic.squaresAdjacentTo(0,0)
        self.assertEqual(len(squares), 3)

    def test_finds_adjacent_color(self):
        # arrange
        color = ButtonColor(1,1)
        self.virtualBoard.setColor(3,3,color)
        # act
        hasColor = self.boardLogic.hasAdjacentColor(3,2, color)
        # assert
        self.assertTrue(hasColor)        

    def test_color_is_not_adjacent_to_itself(self):
        # arrange
        color = ButtonColor(1,1)
        self.virtualBoard.setColor(3,3,color)
        # act
        hasColor = self.boardLogic.hasAdjacentColor(3,3, color)
        # assert
        self.assertFalse(hasColor)        

class SlimeWarsStrategyTests(unittest.TestCase):

    def setUp(self):
        self.virtualBoard = VirtualBoard()
        self.boardLogic = BoardLogic(self.virtualBoard)
        colorList = [RED, GREEN, YELLOW, ORANGE]
        self.strategy = SlimeWarsStrategy(self.virtualBoard, colorList)
        
    def test_init_puts_users_in_corners(self):
        squares = self.strategy.initBoardSetup()
        #print(squares)
        #print[square for square in squares]
        expectedSquare = Square(0,0,RED)
        self.assertTrue(expectedSquare in squares)
        
        
        
if __name__ == '__main__':
        unittest.main(exit=False)
