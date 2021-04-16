import pygame
from math import *
import struct
import sys
import time
import random
import copy

import pg3d

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
        
    def numWinningMoves(self, board): #return number of possbile winning moves this player can make this turn
        moves = 0
        
        for n in range(64):
            if not board.testState(1 << n): #if not already occupied
                newplayer = copy.deepcopy(self)
                newplayer.boardstate |= (1 << n)
                if newplayer.testWin():
                    moves += 1
                    
        return moves
                
class bot(player):
    def __init__(self, name, color):
        super().__init__(name, color)
        self.type = 1
        
    def doMove(self):
        attemptCell = random.randint(0,63)
        while not self.makeMove(1 << attemptCell):
            attemptCell = random.randint(0,63)
            
        return attemptCell
        
class board:
    def __init__(self, playerlist):
        self.playerlist = playerlist #list of player objects
        self.boardstate = 0x0
        
        for p in self.playerlist:
            p.parentBoard = self
        
    def testState(self, teststate):
        return teststate & self.boardstate == teststate #if bit pattern is in board state
    
    '''
    def makeMove(self, playerNum, cellNum): #make move and return true if move is valid
        occupied = False
        for p in self.playerlist:
            if p.testState(cellNum): #cellNum must be in 64-bit format
                occupied = True
                break
                
        if not occupied:
            self.playerlist[playerNum].boardstate |= cellNum
            self.boardstate |= cellNum
            return True
            
        return False
    '''
    
    def testWin(self, playerNum):
        return self.playerlist[playerNum].testWin() #true if given player has won