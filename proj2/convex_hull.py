from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time
import math
# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)

	def rightmostP(self, points):
		p_i = 0
		p = points[p_i]
		for ind, i in enumerate(points):
			if i.x() > p.x():
				p = i
				p_i = ind
		return p_i

	def leftmostP(self, points):
		p_i = 0
		p = points[p_i]
		for ind, i in enumerate(points):
			if i.x() < p.x():
				p = i
				p_i = ind
		return p_i

	def slope(self, a, b):
		return (a.y()-b.y())/(a.x()-b.x())

	def convexHullDC(self, points):
		if(len(points)<=1): return points
		# print(len(points)//2)
		leftSH = self.convexHullDC(points[:len(points)//2]) #left convex hull
		# print(len(points)//2+1)
		rightSH = self.convexHullDC(points[len(points)//2:]) #right convex hull

		rightmostL = self.rightmostP(leftSH)
		leftmostR = self.leftmostP(rightSH)
		vertexL_ui = rightmostL
		vertexR_ui = leftmostR
		vertexL_li = rightmostL
		vertexR_li = leftmostR

		# Finding upper tangent
		while self.slope(leftSH[vertexL_ui],rightSH[vertexR_ui])>self.slope(leftSH[len(leftSH)-1 if vertexL_ui==0 else vertexL_ui-1],rightSH[vertexR_ui]) \
			or self.slope(leftSH[vertexL_ui],rightSH[vertexR_ui])<self.slope(leftSH[vertexL_ui],rightSH[(vertexR_ui+1)%len(rightSH)]):
			while self.slope(leftSH[vertexL_ui],rightSH[vertexR_ui])>self.slope(leftSH[len(leftSH)-1 if vertexL_ui==0 else vertexL_ui-1],rightSH[vertexR_ui]):
				vertexL_ui = len(leftSH)-1 if vertexL_ui == 0 else vertexL_ui-1
			while self.slope(leftSH[vertexL_ui],rightSH[vertexR_ui])<self.slope(leftSH[vertexL_ui],rightSH[(vertexR_ui+1)%len(rightSH)]):
				vertexR_ui = (vertexR_ui + 1) % len(rightSH)

		# Finding lower tangent
		while self.slope(rightSH[vertexR_li],leftSH[vertexL_li])<self.slope(rightSH[vertexR_li],leftSH[(vertexL_li+1)%len(leftSH)]) \
			or self.slope(rightSH[vertexR_li],leftSH[vertexL_li])>self.slope(rightSH[len(rightSH)-1 if vertexR_li==0 else vertexR_li-1],leftSH[vertexL_li]):
			while self.slope(rightSH[vertexR_li],leftSH[vertexL_li])<self.slope(rightSH[vertexR_li],leftSH[(vertexL_li+1)%len(leftSH)]) :
				vertexL_li = (vertexL_li+1)%len(leftSH)
			while self.slope(rightSH[vertexR_li],leftSH[vertexL_li])>self.slope(rightSH[len(rightSH)-1 if vertexR_li==0 else vertexR_li-1],leftSH[vertexL_li]):
				vertexR_li = len(rightSH)-1 if vertexR_li==0 else vertexR_li-1

		# array of vertices of merged hull
		mergedHull = []

		# include vertices in a clockwise direction of the right sub hull
		v_i = vertexR_ui
		while v_i!=vertexR_li:
			mergedHull.append(rightSH[v_i])
			v_i = (v_i+1)%len(rightSH)
		mergedHull.append(rightSH[vertexR_li])

		# include vertices in a clockwise direction of the left sub hull
		v_i = vertexL_li
		while v_i!=vertexL_ui:
			mergedHull.append(leftSH[v_i])
			v_i = (v_i+1)%len(leftSH)
		mergedHull.append(leftSH[vertexL_ui])

		return mergedHull

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		points = sorted(points, key = lambda s: s.x())
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		hull_pts = self.convexHullDC(points)

		polygon = [QLineF(hull_pts[i],hull_pts[(i+1)%len(hull_pts)]) for i in range(len(hull_pts))]

		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.5f} sec'.format(t4-t3))
