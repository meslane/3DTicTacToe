import pygame
from math import *
import struct
import sys
import time
import random
import copy

import pg3d

def getAllCombinations(l, n, r, index, data, i, output):
    if (index == r):
        temp = []
    
        for j in range(r):
            temp.append(data[j])
        output.append(temp)
        return 
    
    if (i >= n):
        return
        
    data[index] = l[i]
    getAllCombinations(l, n, r, index + 1, data, i + 1, output)
    getAllCombinations(l, n, r, index, data, i + 1, output)

class cell(pg3d.cube):
    def __init__(self, center, sidelength, color, number):
        super().__init__(center, sidelength, color)
        
        self.defaultColor = color 
        self.selected = False #if user clicks but hasn't locked in yet
        self.occupied = False #if occuped by user
        
        self.number = number #cell number from 0-63 based on order in array
        
    def numToBin(self):
        return (1 << self.number)

class player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.type = 0 #0 if player, 1 if bot
        self.boardstate = 0x0 #number denoting where the player has placed their pieces on the board
        self.parentBoard = None
        
    def copy(self):
        copyplayer = player(self.name, self.color)
        copyplayer.type = self.type
        copyplayer.boardstate = self.boardstate
        
        return copyplayer
        
    def testState(self, teststate):
        return teststate & self.boardstate == teststate #if bit pattern is in board state
        
    def testWin(self):
        diags3D = [0x1000020000400008, 0x8000040000200001, 0x1002004008000, 0x8004002001000]
        diagsHoriz = [0x1000200040008, 0x8000400020001]
        diagsVert = [0x1248, 0x8421]
        diagsDepth = [0x1001001001000, 0x1000010000100001]
        
        for d in diags3D:
            if self.testState(d):
                return True
        
        for n in range(4):
            for d in diagsHoriz: #flat diagonals
                if self.testState(d << (4 * n)):
                    return True
                    
            for d in diagsVert: #vertical diagonals
                if self.testState(d << (16 * n)):
                    return True
                    
            for d in diagsDepth: #'z' diagonals
                if self.testState(d << n):
                    return True
                
            for m in range(4):
                if self.testState((0x1111 << m) << (16 * n)): #verticals
                    return True
                    
                if self.testState((0x1000100010001 << m) << (4 * n)): #'z' horizontals
                    return True
                
        for n in range(16):
            if self.testState((0xf << (4 * n))): #horizontals
                return True
                
        return False
        
    def makeMove(self, cellNum): #cellnum must be in 64-bit format
        if not self.parentBoard.testState(cellNum): #if desired move is not occupied
            self.boardstate |= cellNum
            self.parentBoard.boardstate |= cellNum
            return True
            
        return False
        
    def getWinningMoves(self): #return number of possbile winning moves this player can make this turn
        moves = []
        
        for n in range(64):
            if not self.parentBoard.testState(1 << n): #if not already occupied
                newplayer = copy.deepcopy(self)
                newplayer.boardstate |= (1 << n)
                if newplayer.testWin():
                    moves.append((1 << n))
                    
        return tuple(moves)
        
    def getWinningSequences(self, depth): #get all sequences of n length that will result in a win
        moves = []
        winningMoves = []
        
        validmoves = list(self.parentBoard.getValidMoves())
        
        getAllCombinations(validmoves, len(validmoves), depth, 0, [0] * depth, 0, moves)
        
        for sequence in moves:
            movebits = 0
            for move in sequence:
                movebits |= move
            
            newplayer = copy.deepcopy(self)
            newplayer.boardstate |= movebits
            
            if newplayer.testWin():
                winningMoves.append(sequence)
        
        return winningMoves
                
class bot(player):
    def __init__(self, name, color, difficulty):
        super().__init__(name, color)
        self.type = 1
        self.difficulty = difficulty #0 = random, 1-3 = n move look ahead
        
    def doRandomMove(self):
        attemptCell = random.randint(0,63)
        while not self.makeMove(1 << attemptCell):
            attemptCell = random.randint(0,63)
            
        return attemptCell
        
    def doBlockingMove(self):
        possibleDefMoves = []
        possibleOffMoves = []
        cell = -1
        
        for p in self.parentBoard.playerlist: #defensive move
            for d in range(1, self.difficulty + 1):
                for m in p.getWinningSequences(d):
                    if m not in possibleDefMoves:
                        possibleDefMoves.append(m)
                        print(m)
                        
                if possibleDefMoves: #break so we address more pressing defensive moves first
                    break
                    
        for d in range(1, self.difficulty + 1):
            for m in self.getWinningSequences(d):
                if m not in possibleOffMoves:
                    possibleOffMoves.append(m)
                        
            if possibleOffMoves:
                break
                
        if possibleDefMoves and possibleOffMoves:
            if (len(possibleDefMoves[0]) < len(possibleOffMoves[0])): #make defensive move if opponent is closer to winning
                cell = possibleDefMoves[random.randint(0, len(possibleDefMoves) -1)][0]
            else:
                cell = possibleOffMoves[random.randint(0, len(possibleOffMoves) -1)][0]
        elif possibleDefMoves:
            cell = possibleDefMoves[random.randint(0, len(possibleDefMoves) -1)][0]
        elif possibleOffMoves:
            cell = possibleOffMoves[random.randint(0, len(possibleOffMoves) -1)][0]
        else: #random move
            validMoves = self.parentBoard.getValidMoves()
            cell = validMoves[random.randint(0, len(validMoves) - 1)]
            
        self.makeMove(cell)

        return int(log(cell, 2))
        
        
        
class board:
    def __init__(self, playerlist, currPlayerNum):
        self.playerlist = playerlist #list of player objects
        self.currentPlayer = playerlist[currPlayerNum]
        self.boardstate = 0x0
        self.children = [] #list of child boards for bot tree search
        
        for p in self.playerlist:
            p.parentBoard = self
            
    def copy(self):
        copyplayerlist = []
        
        for p in self.playerlist:
            copyplayerlist.append(p.copy())
    
        copyObject = board(copyplayerlist, self.playerlist.index(self.currentPlayer))
        copyObject.boardstate = self.boardstate
        
        return copyObject
            
    def gotoNextPlayer(self):
        if self.currentPlayer == self.playerlist[-1]:
            self.currentPlayer = self.playerlist[0]
        else:
            self.currentPlayer = self.playerlist[self.playerlist.index(self.currentPlayer) + 1]
            
    '''
    def createChildTree(self, depth): #create a tree of all possible moves out to n depth
        if depth > 0:
            for n in range(64):
                if not self.testState(1 << n): #if move is valid
                    #print("depth: {}, cell: {}, player: {}".format(depth, n, self.currentPlayer.name))
                    self.children.append(self.copy())
                    self.children[-1].currentPlayer.makeMove(1 << n) #copy current board state but make the move, thereby advancing the game by 1
                    self.children[-1].gotoNextPlayer() #advance to the next player
                    self.children[-1].createChildTree(depth - 1) #recur
                    #print("depth: {}, cell: {}, player: {}".format(depth, n, self.currentPlayer.name))
    '''    
    
    def testState(self, teststate):
        return teststate & self.boardstate == teststate #if bit pattern is in board state
    
    def testWin(self):
        return self.currentPlayer.testWin() #true if given player has won
        
    def getValidMoves(self): #get all moves that any player could make
        validmoves = []
        
        for n in range(64):
            if not self.testState(1 << n):
                validmoves.append(1 << n)
                
        return tuple(validmoves)