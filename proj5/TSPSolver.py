#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
import copy


class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	
	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	def greedy(self, time_allowance=60.0):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)

		start_time = time.time()

		best_cost = float('inf')
		best_route = None
		count = 0

		for i in range(ncities):
			candidate_city = cities[i]
			unvisited_cities = cities.copy()
			route = []

			route.append(unvisited_cities.pop(i))
			bssf = 0

			while len(unvisited_cities) != 0:
				min_path, min_index = candidate_city.costTo(unvisited_cities[0]), 0

				for j in range(1, len(unvisited_cities)):
					cost = candidate_city.costTo(unvisited_cities[j])
					if min_path > cost:
						min_path, min_index = cost, j

				if min_path != float('inf'):
					bssf += min_path
					candidate_city = unvisited_cities[min_index]   
					route.append(unvisited_cities.pop(min_index))
				else:
					break

			if len(route) == ncities:
				return_cost = route[-1].costTo(route[0])
				if return_cost != float('inf'):
					total_cost = bssf + return_cost
					count += 1

					if total_cost < best_cost:
						best_cost = total_cost
						best_route = route

		end_time = time.time()

		results['cost'] = best_cost if best_route else float('inf')
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = TSPSolution(best_route) if best_route else None
		results['max'] = None
		results['total'] = None
		results['pruned'] = None

		return results

	
	
	
	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''

	def initCostMatrix(self, cities):
		cost_matrix = [[0]*len(cities) for _ in range(len(cities))]
		for i in range(len(cities)):
			for j in range(len(cities)):
				cost_matrix[i][j] = cities[i].costTo(cities[j])
		return cost_matrix

	def branchAndBound( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)

		start_time = time.time()

		bssf = self.greedy(60.0)['soln']
		count = 0
		pruned = 0
		total_states = 0
		max_q_size = 0
		priority_q = PriorityQueue()
		root_state = State(self.initCostMatrix(cities), 0, [cities[0]])
		root_state.reduceMatrix()
		priority = root_state.lower_bound / len(root_state.route)
		priority_q.insert(root_state,priority)
		total_states += 1
		while priority_q.getSize() > 0:
			if time.time() - start_time > time_allowance:
				break
			max_q_size = max(max_q_size, priority_q.getSize())
			subproblem = priority_q.deleteMin()
			if subproblem.lower_bound >= bssf.cost:
				pruned += 1
				continue
			last_city = subproblem.route[-1]
			i = last_city._index
			visited = set(city._index for city in subproblem.route)
			for j in range(ncities):
				if j in visited:
					continue
				residual_cost = subproblem.c_matrix[i][j]
				if residual_cost == float('inf'):
					continue
				new_cmat = copy.deepcopy(subproblem.c_matrix)
				new_cmat[i] = [float('inf')] * ncities
				for row in range(ncities):
					new_cmat[row][j] = float('inf')
				new_cmat[j][i] = float('inf')
				new_route = subproblem.route.copy()
				new_route.append(cities[j])
				new_lower_bound = subproblem.lower_bound + residual_cost
				new_state = State(new_cmat, new_lower_bound, new_route)
				new_state.reduceMatrix()
				total_states += 1
				if len(new_route) == ncities:
					return_cost = cities[j].costTo(new_route[0])
					if return_cost != float('inf'):
						candidate = TSPSolution(new_route)
						if candidate.cost < bssf.cost:
							bssf = candidate
							count += 1
					continue
				if new_state.lower_bound < bssf.cost:
					new_priority = new_state.lower_bound/len(new_state.route)
					priority_q.insert(new_state, new_priority)
				else:
					pruned += 1
		end_time = time.time()
		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = max_q_size
		results['total'] = total_states
		results['pruned'] = pruned
		return results







	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''
		
	def fancy( self,time_allowance=60.0 ):
		pass
		



