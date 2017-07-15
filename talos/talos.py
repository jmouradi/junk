#!/usr/bin/python
# 
# talos.py 
# 
# ./talos.py <input file>
#
# Outputs a solution to the input file, if found.
# 
# The input file is of the form: 
# 1. Rows: N
# 2. Columns: M
# 3.           <-- BLANK LINE BETWEEN COLUMNS AND PIECE DEFINITION
# 4. Piece Line
# 5. Piece Line 
# ...
# N. Piece Line
# N+1.          <-- BLANK LINE AFTER PIECE DEFINITION 
# N+2 Piece Line
# ...
# M. Piece Line
# 
# ... and so on and so forth.
# 

# Piece lines have any number of 'X' (square occupied) or '.' (square
# unoccupied), AND ALL LINES MUST BE THE SAME WIDTH. A continguous group of 
# piece lines represents a single piece of the puzzle, i.e.: 
# XXX
# .X. 
# Represents a tetris "T".
#
#
# NOTE: This is a hacky script I wrote to play a video game. It does not do 
# a lot of validation. It's ugly. Deal with it. Don't do anything stupid.

from copy import deepcopy
from string import ascii_uppercase
import sys
from itertools import takewhile

# We mask each piece with a unique printable character so as to differentiate 
# it in the final output. 
charmask = ascii_uppercase

# Reads an input file. 
# Input: Name of the file.
# Output: (Rows, Cols, Pieces)
def readFile(name): 
  with open(name, "r") as infile: 
    lines = infile.readlines()
  lines = map(lambda x: x.strip(' \t\n\r'), lines)
  rows = int(lines[0].split(' ')[1])
  cols = int(lines[1].split(' ')[1])

  lines = lines[3:] # Trim the header.
  pieces = []
  numPieces = 0
  while len(lines) > 0: 
    pieceStrs = list(takewhile(lambda x: len(x) > 0, lines))
    if len(pieceStrs) == 0: 
      break
    piece = []
    for string in pieceStrs: 
      piecePiece = []
      piecePiece.extend(string)
      piece.append(piecePiece)
    lines = lines[len(piece)+1:]
    # piece = pieceToTuple(mask(piece, numPieces))
    piece = mask(piece, numPieces)
    pieces.append(piece)
    numPieces += 1
  return rows, cols, pieces

def sanity(rows, cols, pieces, grid): 
  print "Rows: " + str(rows)
  print "Cols: " + str(cols)
  print ""
  for piece in pieces: 
    printGrid(piece)
    print ""

def printGrid(grid):
  for line in grid: 
    for char in line: 
      print char,
    print ""

def getGrid(rows, cols): 
  return [["." for x in range(cols)] for y in range(rows)] 

# X X X 
# . . X
# to
# . X  (0, 0) = (1, 0); (0, 1) = (0, 0)
# . X  (1, 0) = (1, 1); (1, 1) = (0, 1)
# X X  (2, 0) = (1, 2); (2, 1) = (0, 2)
# 
# ...so new(j, len-i-1) = original(i, j)

# Returns a new piece: the supplied piece rotated 90 degrees. 
def rot(piece): 
  retpiece = [["." for x in range(len(piece))] for y in range(len(piece[0]))] 
  for i in range(0, len(piece)):
    for j in range(0, len(piece[0])):
      newrow = j
      newcol = len(piece)-i-1
      retpiece[j][len(piece)-i-1] = piece[i][j]
  return retpiece
  # return pieceToTuple(retpiece)

# Mask a piece with a unique character.
# Operates on pieces that are still lists! Not yet tuples!
def mask(piece, depth): 
  newPiece = [["." for x in range(len(piece[0]))] for y in range(len(piece))] 
  for i in range(0, len(piece)): 
    for j in range(0, len(piece[0])): 
      if piece[i][j] == 'X':
        newPiece[i][j] = charmask[depth]
  return newPiece

# Determine whether the pieces lie "flush" from top-to-bottom. We are populating
# the grid in row-major order, so we scan from top down. 
def flush(grid): 
  for col in range(0, len(grid[0])):
    seenDot = False
    for row in range(0, len(grid)):
      if grid[row][col] == '.':
        seenDot = True
      else: 
        if seenDot: 
          return False
  return True

# If a piece can be placed on the grid, place it. If you succeed, ensure all 
# squares on the grid lie flush from the top down. If they are, return True. 
# Otherwise, remove the piece if it has been placed, and return False.
def placeIfPossiblePrune(grid, piece, startRow, startCol, remPieces): 
  if canPlace(grid, piece, startRow, startCol): 
    place(grid, piece, startRow, startCol)
    if flush(grid):
      return True
    else:
      remove(grid, piece, startRow, startCol)
  return False

# Ensure the piece in the current position overlaps with no other pieces.
def canPlace(grid, piece, startRow, startCol): 
  for row in range(len(piece)):
    for col in range(len(piece[0])): 
      if piece[row][col] != '.':
        if grid[row + startRow][col + startCol] != '.':
          return False
  return True

# Place a piece on the grid.
def place(grid, piece, startRow, startCol): 
  for row in range(len(piece)):
    for col in range(len(piece[0])): 
      if piece[row][col] != '.':
        newRow = row + startRow
        newCol = col + startCol
        grid[row + startRow][col + startCol] = piece[row][col]

# Remove a piece from the grid.
def remove(grid, piece, startRow, startCol): 
  for row in range(len(piece)):
    for col in range(len(piece[0])): 
      if piece[row][col] != '.':
        grid[row + startRow][col + startCol] = '.'

# Makes immutable pieces.
def pieceToTuple(piece): 
  newPiece = deepcopy(piece)
  tupleList = map(lambda x: tuple(x), newPiece)
  return tuple(tupleList)

count = 0

def dfs(depth, grid, pieces): 
  if len(pieces) == 0: 
    global count
    print count
    print("Solution: ")
    printGrid(grid)
    sys.exit(1)
  usedPieces = set()
  for i in range(0, len(pieces)): 
    piece = pieces[i]
    # Aggressive pruning: this piece is like a piece we've examined at depth.
    if pieceToTuple(piece) in usedPieces:
      continue
    del pieces[i]
    for rotation in range(0, 4):
      piece = rot(piece)
      if pieceToTuple(piece) in usedPieces: 
        continue
      usedPieces.add(pieceToTuple(piece))
      seenDot = False
      for startRow in range(0, len(grid) - len(piece) + 1):
        for startCol in range(0, len(grid[0]) - len(piece[0]) + 1):
          if grid[startRow][startCol] == '.':
            seenDot = True
          res = placeIfPossiblePrune(grid, piece, startRow, startCol, pieces)
          if res:
            # printGrid(grid)
            dfs(depth+1, grid, pieces)
            remove(grid, piece, startRow, startCol)
          if seenDot == True:
            break
        if seenDot == True: 
          break
    pieces.insert(i, piece)
    global count
    count += 1
    
def main():
  input = sys.argv[1]
  rows, cols, pieces = readFile(input)
  grid = getGrid(rows, cols)
  dfs(0, grid, pieces)

if __name__ == "__main__": 
  main()
