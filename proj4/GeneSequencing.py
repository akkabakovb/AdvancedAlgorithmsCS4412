#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import math
import time

# Used to compute the band2 * MAXINDELS + 1 for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass


# This is the method called by the GUI.  _sequences_ is a list of the ten sequences, _table_ is a
# handle to the GUI so it can be updated as you find results, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you
# how many base pairs to use in computing the alignment

	def align( self, sequences, table, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		results = []

		for i in range(len(sequences)):
			jresults = []
			for j in range(len(sequences)):

				if(j < i):
					s = {}
				else:
###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2
					if banded:
						score, seq1, seq2 = self.NeedlemanWunschBanded(sequences[i][:self.MaxCharactersToAlign], sequences[j][:self.MaxCharactersToAlign])
					else:
						score, seq1, seq2 = self.NeedlemanWunsch(sequences[i][:self.MaxCharactersToAlign], sequences[j][:self.MaxCharactersToAlign])
					alignment1 = '{}  DEBUG:(seq{}, {} chars,align_len={}{})'.format(seq1,i+1,
						len(sequences[i]), align_length, ',BANDED' if banded else '')
					alignment2 = '{}  DEBUG:(seq{}, {} chars,align_len={}{})'.format(seq2,j+1,
						len(sequences[j]), align_length, ',BANDED' if banded else '')
###################################################################################################
					s = {'align_cost':score, 'seqi_first100':alignment1[:100] if score != math.inf else 'No Alignment Possible', 'seqj_first100':alignment2[:100] if score != math.inf else 'No Alignment Possible'}
					table.item(i,j).setText('{}'.format(int(score) if score != math.inf else score))
					table.update()
				jresults.append(s)
			results.append(jresults)
		return results

	def NeedlemanWunsch(self, seq1, seq2):
		# Initialization of DP and backpointers tables
		table = [[0] * (len(seq2) + 1) for i in range(len(seq1) + 1)]
		back = [[None] * (len(seq2) + 1) for i in range(len(seq1) + 1)]
		for j in range(len(seq2)+1):
			table[0][j] = j * INDEL
		for i in range(len(seq1)+1):
			table[i][0] = i * INDEL
	    # Fill-in table
		for i in range(1, len(seq1)+1):
			for j in range(1, len(seq2)+1):
				diag = table[i-1][j-1] + (MATCH if seq1[i-1] == seq2[j-1] else SUB)
				top = table[i-1][j] + INDEL
				left = table[i][j-1] + INDEL
				table[i][j] = min(left, top, diag)
				if table[i][j] == left:
					back[i][j] = "l"
				elif table[i][j] == top:
					back[i][j] = "t"
				else:
					back[i][j] = "d"
	    # Reconstruction using back pointers
		i = len(seq1)
		j = len(seq2)
		alignment1 = ""
		alignment2 = ""
		while i > 0 or j > 0:
			direction = back[i][j]
			if direction == "l":
				alignment1 = "-" + alignment1
				alignment2 = seq2[j-1] + alignment2
				j -= 1
			elif direction == "t":
				alignment1 = seq1[i-1] + alignment1
				alignment2 = "-" + alignment2
				i -= 1
			else:
				alignment1 = seq1[i-1] + alignment1
				alignment2 = seq2[j-1] + alignment2
				i -= 1
				j -= 1
		return table[-1][-1], alignment1, alignment2

	def NeedlemanWunschBanded(self, seq1, seq2):
		# Initialization of DP and backpointers tables
		if abs(len(seq1) - len(seq2)) > MAXINDELS:
			return math.inf, "", ""
		table = [[float('inf')] * (2*MAXINDELS+1) for i in range(len(seq1) + 1)]
		back  = [[None] * (2*MAXINDELS+1) for i in range(len(seq1) + 1)]
		table[0][MAXINDELS] = 0
		# Fill-in table
		for i in range(len(seq1) + 1):
			for banded_j in range(2 * MAXINDELS + 1):
				j = i + (banded_j - MAXINDELS)
				if j < 0 or j > len(seq2):
					continue
				if i == 0 and j == 0:
					continue
				diag = float('inf')
				top = float('inf')
				left = float('inf')
	            # diag
				if i > 0 and j > 0:
					cost = MATCH if seq1[i-1] == seq2[j-1] else SUB
					diag = table[i-1][banded_j] + cost
				# top
				if i > 0 and banded_j + 1 < 2 * MAXINDELS + 1:
					top = table[i-1][banded_j+1] + INDEL
				# left
				if j > 0 and banded_j - 1 >= 0:
					left = table[i][banded_j-1] + INDEL
				table[i][banded_j] = min(left, top, diag)
				if table[i][banded_j] == left:
					back[i][banded_j] = "l"
				elif table[i][banded_j] == top:
					back[i][banded_j] = "t"
				else:
					back[i][banded_j] = "d"
	    # Reconstruction using back pointers
		i = len(seq1)
		j = len(seq2)
		banded_j = MAXINDELS + (j - i)
		alignment1 = ""
		alignment2 = ""
		while i > 0 or j > 0:
			direction = back[i][banded_j]
			if direction == "d":
				alignment1 = seq1[i-1] + alignment1
				alignment2 = seq2[j-1] + alignment2
				i -= 1
				j -= 1
				banded_j = MAXINDELS + (j - i)
			elif direction == "t":
				alignment1 = seq1[i-1] + alignment1
				alignment2 = "-" + alignment2
				i -= 1
				banded_j += 1
			elif direction == "l":
				alignment1 = "-" + alignment1
				alignment2 = seq2[j-1] + alignment2
				j -= 1
				banded_j -= 1
		return table[len(seq1)][MAXINDELS + (len(seq2) - len(seq1))], alignment1, alignment2
