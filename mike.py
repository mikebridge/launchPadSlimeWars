#!/usr/bin/python

import random
import launchpad
from pygame import time

class ButtonColor:
    def __init__(self, r, g):
        self.red = r
        self.green = g

    def nextColor(self):
        newr = self.red + 1
        newg = self.green
        if (newr > 3):
            newg = newg + 1
            newr = 0
        if (newg > 3):
            newr = 0
            newg = 0
        return ButtonColor(newr, newg)

    def __eq__(self, other):
        return self.red == other.red and self.green == other.green

    def __str__(self):
        return "RED("+str(self.red)+"), GREEN("+str(self.green)+")"

    def __hash__(self):
        return hash((self.red, self.green))

class VirtualBoard:
    # logically, the board is maxx x maxy, indexed from zero.
    # but the launchpad is indexed from 1 vertically because of
    # the extra horizontal row at the top.
    
    def __init__(self, maxx = 8, maxy = 8):
        self.maxx = maxx
        self.maxy = maxy
        self.matrix = [[ButtonColor(0,0)
                        for i in range(self.maxx)]
                        for j in range(self.maxy)]
        self.emptySquares = self.maxx * self.maxy

    def updateEmptySquareCount(self, x, y, buttonColor):
        if (buttonColor != ButtonColor(0,0) and self.matrix[x][y] == ButtonColor(0,0)):
            self.emptySquares -= 1
        if (buttonColor == ButtonColor(0,0) and self.matrix[x][y] != ButtonColor(0,0)):
            self.emptySquares += 1            
    
    def setColor(self, x, y, buttonColor):
        self.updateEmptySquareCount(x, y, buttonColor)
        self.matrix[x][y] = buttonColor        
    
    def cycleColor(self, x, y):
        self.setColor(x, y, self.matrix[x][y].nextColor())

    def off(self, x, y):
        self.setColor(x, y, ButtonColor(0,0))

    def currentColor(self, x, y):
        return self.matrix[x][y]

    def squaresWithColor(self, buttonColor):
        return [Square(x,y,buttonColor)
                    for x in range(0, self.maxx)
                    for y in range(0, self.maxy)
                    if buttonColor == self.matrix[x][y]]
                        
    def colorsWithCounts(self):
        colors = [self.matrix[x][y]
            for x in range(0, self.maxx)
            for y in range(0, self.maxy)]
        return {color: colors.count(color) for color in colors}

    def colorsThatHaveMaxCount(self):
        colorCounts = self.colorsWithCounts()
        return [k for k,v in colorCounts.iteritems()
                if v == max(colorCounts.values())]        

class HWBoard:
    
    def __init__(self, virtualBoard, LP):
        self.virtualBoard = virtualBoard
        self.LP = LP

    def setColor(self, x, y, buttonColor):
        #self.matrix[x][y] = buttonColor
        self.virtualBoard.setColor(x, y, buttonColor)
        self.LP.LedCtrlXY(x, y + 1, buttonColor.red, buttonColor.green)

    def flashWithColor(self, x, y, offColor, finalColor):
        self.virtualBoard.setColor(x, y, finalColor)
        ms = 100
        for i in range(1,4):
            time.wait(ms)
            self.LP.LedCtrlXY(x, y + 1, finalColor.red, finalColor.green)
            time.wait(ms)
            self.LP.LedCtrlXY(x, y + 1, offColor.red, offColor.green)
        time.wait(ms)
        self.LP.LedCtrlXY(x, y + 1, finalColor.red, finalColor.green)

        
    def __getattr__(self,name):
        return getattr(self.virtualBoard, name)
        
class HWTopRow:
    def __init__(self, LP):
        self.LP = LP

    def setAllToColor(self, buttonColor):
        for x in range(0,8):
            self.LP.LedCtrlXY(x, 0, buttonColor.red, buttonColor.green)

    def flashAllWithColor(self, buttonColors):
        for i in range(1,5):
            for color in buttonColors:
                time.wait(1000)
                self.setAllToColor(ButtonColor(0,0))
                time.wait(1000)
                self.setAllToColor(color)            

class HWSideColumn:
    def __init__(self, LP):
        self.LP = LP

    def setAllToColor(self, buttonColor):
        for x in range(1,9):
            self.LP.LedCtrlXY(8, x, buttonColor.red, buttonColor.green)


class BoardLogic:

    def __init__(self, board):
        self.board = board

    def inBounds(self, x, y):
        return (x >= 0 and y >= 0
            and x < self.board.maxx and y < self.board.maxy)

    def squaresAdjacentTo(self, x, y):
        return self.squaresWithinSpaces(x,y,1)

    def squaresWithinSpaces(self, x, y, distance):
        return [Square(x1, y1, self.board.currentColor(x1, y1))
                for x1 in range(x - distance, x + distance + 1)
                for y1 in range(y - distance, y + distance + 1)
                if(not(x1 == x and y1 == y)
                     and self.inBounds(x1, y1))]                    
            
    def hasAdjacentColor(self, x, y, color):
        return [square
                for square in self.squaresAdjacentTo(x, y)
                if square.color == color]

    def hasColorWithinDistance(self, x, y, color, distance):
        return [square
                for square in self.squaresWithinSpaces(x, y, distance)
                if square.color == color]

    def squareIsColor(self, x, y, color):
        return self.board.currentColor(x,y) == color

class Square:
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.color == other.color

    def __str__(self):
        return "X,Y="+str(self.x)+","+str(self.y)+" "+str(self.color)


class Mover:
    def __init__(self, board):
        self.board = board
        
    def apply(self, square):
        self.board.setColor(square.x, square.y, square.color)
        

class SlimeWarsStrategy:
    emptyColor = ButtonColor(0,0)
    
    def __init__(self, board, playerColorList):
        self.board = board
        self.playerColorList = playerColorList
        self.boardLogic = BoardLogic(board)

    def fillInitCorner(self, x, y, playerColor):
        moves = []
        moves.append(Square(x, y, playerColor))
        moves.append(Square(x, 1 if y==0 else self.board.maxy - 2, playerColor))
        moves.append(Square(1 if x==0 else self.board.maxx - 2, y, playerColor))
        return moves
                     
    def initBoardSetup(self):
        moves = []
        maxx=self.board.maxx-1
        maxy=self.board.maxy-1
        moves+=self.fillInitCorner(0, 0, self.playerColorList[0])
        if (len(self.playerColorList) == 4):
            moves += self.fillInitCorner(maxx, 0, self.playerColorList[1])
            moves += self.fillInitCorner(maxx, maxy, self.playerColorList[2])
            moves += self.fillInitCorner(0, maxy, self.playerColorList[3])
        return moves

    def distance(self, x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))        

    def isValidMove(self, player, requestedx, requestedy, preselectedxy):
        if not(self.boardLogic.squareIsColor(requestedx, requestedy, self.emptyColor)):
            return False
        
        if (preselectedxy == None):        
            return self.boardLogic.hasAdjacentColor(requestedx, requestedy, \
                                                          self.playerColorList[player])
        else:            
            return self.boardLogic.squareIsColor(preselectedxy[0], preselectedxy[1], self.playerColorList[player])\
                and self.distance(requestedx, requestedy, preselectedxy[0], preselectedxy[1]) < 3
        

    def hasAValidMove(self, player):
        playerColor = self.playerColorList[player]
        for playerSquare in self.board.squaresWithColor(playerColor):
            for emptySquare in self.board.squaresWithColor(self.emptyColor):
                if (abs(emptySquare.x - playerSquare.x) < 3 and \
                    abs(emptySquare.y - playerSquare.y) < 3):
                    return True
        return False


    def captures(self, requestedx, requestedy, playerColor):
        return [Square(square.x, square.y, playerColor)        
                for square in
                    self.boardLogic.squaresAdjacentTo(requestedx, requestedy)
                if not(square.color.red == 0 and square.color.green == 0) and\
                    square.color != playerColor]
        
    def calculateBoardUpdates(self, player, requestedx, requestedy, preselectedxy=None):
        result = []
        currentColor = self.playerColorList[player]        
        if(self.isValidMove(player, requestedx, requestedy, preselectedxy)):
            result = [Square(requestedx,requestedy, currentColor)] +\
                self.captures(requestedx, requestedy, currentColor)
            if preselectedxy!=None and self.distance(requestedx, requestedy,
                                                     preselectedxy[0], preselectedxy[1]) == 2:
                result.append(Square(preselectedxy[0], preselectedxy[1], self.emptyColor))
        return result
    
    def isComplete(self):
        return self.board.emptySquares == 0

def main():
    print("starting...")
    
    RED = ButtonColor(3,0)
    GREEN = ButtonColor(0,3)
    YELLOW = ButtonColor(1,2)
    ORANGE = ButtonColor(3,3)
    playerColor = [RED, GREEN, YELLOW, ORANGE]
    playerCount = len(playerColor)
    LP = launchpad.Launchpad()  # creates a Launchpad instance (first Launchpad found)
    print("Opening Launchpad...")
     
    LP.Open()                   # start it
    LP.Reset()
    virtualBoard = VirtualBoard(maxx=6, maxy=6)
    board = HWBoard(virtualBoard, LP);
    topRow = HWTopRow(LP);
    
    boardMover = Mover(board)
    game =SlimeWarsStrategy(board, playerColor)                         
    [boardMover.apply(move) for move in game.initBoardSetup()]
                     
    currentPlayer = 0
    topRow.setAllToColor(playerColor[currentPlayer])
    print("READY!")

    preselectedButton = None    
    while True:
        time.wait(30)
        buttonxy = LP.ButtonStateXY()

        if buttonxy != []:
            #print(buttonxy)
            if buttonxy == [ 8, 8, True ]: # Lower right btn
                break
            
            if buttonxy[0] == 8 or buttonxy[1] == 0:   # ignore the side rows
                continue

            if buttonxy[0] >= board.maxx or buttonxy[1] > board.maxy:   # ignore the unused rows
                continue
            
            if buttonxy[2] == True: # True == push down
                # set a start button (optional)
                if board.currentColor(buttonxy[0], buttonxy[1] - 1) == playerColor[currentPlayer]:
                    preselectedButton = (buttonxy[0], buttonxy[1] - 1)
                    board.flashWithColor(buttonxy[0],
                                         buttonxy[1] - 1,
                                         ButtonColor(0,0),
                                         playerColor[currentPlayer])
                    continue

                #print("using preselected "+str(preselectedButton))            
                moves = game.calculateBoardUpdates(currentPlayer, buttonxy[0], buttonxy[1] - 1, preselectedButton) 
                [boardMover.apply(move) for move in moves]
                
                if len(moves)> 0:
                    preselectedButton = None
                    lookForNextPlayer = not(game.isComplete())
                    while lookForNextPlayer:
                        currentPlayer = (currentPlayer + 1) % playerCount
                        lookForNextPlayer = not(game.hasAValidMove(currentPlayer))
                    
                    topRow.setAllToColor(playerColor[currentPlayer]) 
                
                if game.isComplete():
                    #todo: make this flash with the winner's color
                    winnerColors = board.colorsThatHaveMaxCount()
                    topRow.flashAllWithColor(winnerColors)
                    break;

    
    

    print("DONE")

    #LP.Reset()
    LP.Close()
            
#	LP.LedCtrlString( 'HELLO   ', 0, 3, -1 )  # scroll "HELLO" from right to left

if __name__ == "__main__":
        main()
