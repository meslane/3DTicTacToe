import pygame
from math import *
import struct
import sys
import time
import random
import copy
from collections import Counter

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

def getShortest(l):
    min = l[0]
    for i in range(1, len(l)):
        if len(l[i]) < len(min):
            min = l[i]
            
    return min

def getAllShortest(l):
    minlist = []
    minlist.append(l[0])
    
    for i in range(1, len(l)):
        if len(l[i]) < len(minlist[0]):
            minlist.clear()
            minlist.append(l[i])
        elif len(l[i]) == len(minlist[0]):
            minlist.append(l[i])
            
    return minlist
    
def randomInList(l):
    return l[random.randint(0, len(l) - 1)]
    
def getMostCommon(l): #sorts the list by number of occurances and returns a random of the most common
    singlelist = sum(l, [])
    validMoves = []
    
    c = Counter(singlelist)
    
    if c:
        count = max(list(c.values()))
        
        for key in c:
            if c[key] == count:
                validMoves.append(key)
    
    return validMoves

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
        
        print(self.name)
        print("defensive moves")
        for p in self.parentBoard.playerlist: #defensive move
            if p != self:
                for d in range(1, self.difficulty + 1):
                    for m in p.getWinningSequences(d):
                        if m not in possibleDefMoves:
                            possibleDefMoves.append(m)
                            print(m)
                            
                    if possibleDefMoves: #break so we address more pressing defensive moves first
                        break
        
        print("offensive moves")
        for d in range(1, self.difficulty + 1):
            for m in self.getWinningSequences(d):
                if m not in possibleOffMoves:
                    possibleOffMoves.append(m)
                    print(m)
                    
            if possibleOffMoves:
                break      
        
        if possibleDefMoves and possibleOffMoves:
            if (len(getShortest(possibleDefMoves)) < len(getShortest(possibleOffMoves))): #make defensive move if opponent is closer to winning
                '''
                clist = getAllShortest(possibleDefMoves)
                cell = clist[random.randint(0, len(clist) - 1)][random.randint(0, len(getShortest(possibleDefMoves)) - 1)]#take the shortest defensive move sequence
                '''
                cell = randomInList(getMostCommon(getAllShortest(possibleDefMoves)))
            else:
                #cell = possibleOffMoves[random.randint(0, len(possibleOffMoves) -1)][random.randint(0, len(getShortest(possibleOffMoves)) - 1)]
                cell = randomInList(getMostCommon(getAllShortest(possibleOffMoves)))
        elif possibleDefMoves:
            '''
            clist = getAllShortest(possibleDefMoves)
            cell = clist[random.randint(0, len(clist) - 1)][random.randint(0, len(getShortest(possibleDefMoves)) - 1)]
            '''
            cell = randomInList(getMostCommon(getAllShortest(possibleDefMoves)))
        elif possibleOffMoves:
            #cell = possibleOffMoves[random.randint(0, len(possibleOffMoves) -1)][random.randint(0, len(getShortest(possibleOffMoves)) - 1)]
            cell = randomInList(getMostCommon(getAllShortest(possibleOffMoves)))
        else: #random move
            validMoves = self.parentBoard.getValidMoves()
            cell = validMoves[random.randint(0, len(validMoves) - 1)]
            
        self.makeMove(cell)
        print("Chosen move: {}\n".format(cell))
        return int(log(cell, 2))
        
        
        
class board:
    def __init__(self, playerlist, currPlayerNum):
        self.playerlist = playerlist #list of player objects
        self.currentPlayer = playerlist[currPlayerNum]
        self.boardstate = 0x0
        
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