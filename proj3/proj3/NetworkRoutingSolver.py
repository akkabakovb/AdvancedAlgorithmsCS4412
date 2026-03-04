#!/usr/bin/python3


from CS4412Graph import *
import time


class NetworkRoutingSolver:
    def __init__( self):
        dist = []
        prev = []
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS4412Graph )
        self.network = network

    def deleteminArr(self, H):
        ind = 0
        min = H[ind]
        n = len(H)
        for i in range(n):
            if min>H[i]:
                min = H[i]
                ind = i
        H[ind] = float('inf')         # mark node visited
        return ind

    def arrayDijkstra(self, srcIndex):
        # intialization of return data structures
        dist = []
        prev = []
        INF = float('inf')
        # initialization of the dist, prev and array priority queue
        priority_queue = []
        for i in range(len(self.network.nodes)):
            if i == srcIndex:
                dist.append(0)
            else: dist.append(INF)
            priority_queue.append(dist[i])
            prev.append(None)
        len_queue = len(self.network.nodes)
        #
        while len_queue!=0:
            # O(n) - traverse entire queue
            u = self.network.nodes[self.deleteminArr(priority_queue)]
            len_queue -= 1
            for e in u.neighbors:
                if dist[e.dest.node_id] > dist[e.src.node_id] + e.length:
                    dist[e.dest.node_id] = dist[e.src.node_id] + e.length
                    prev[e.dest.node_id] = u
                    priority_queue[e.dest.node_id] = dist[e.dest.node_id]
        self.dist = dist
        self.prev = prev

    def percolateDown(self, H, root_ind, pointer_arr, size):
        min = root_ind

        if (2*root_ind + 1) < size and H[2*root_ind + 1][1] < H[min][1]:
            min = 2*root_ind + 1

        if (2*root_ind + 2) < size and H[2*root_ind + 2][1] < H[min][1]:
            min = 2*root_ind + 2

        if min != root_ind:
            temp = H[root_ind]
            H[root_ind] = H[min]
            H[min] = temp
            pointer_arr[H[root_ind][0]] = root_ind
            pointer_arr[H[min][0]] = min
            self.percolateDown(H, min, pointer_arr, size)

    def bubbleUp(self, H, pointer_arr, h_ind):
        if(h_ind<=0): return
        swap_ind = (h_ind-1) // 2
        if H[swap_ind][1] > H[h_ind][1]:

            temp = H[swap_ind]
            H[swap_ind] = H[h_ind]
            H[h_ind] = temp

            pointer_arr[H[h_ind][0]] = h_ind
            pointer_arr[H[swap_ind][0]] = swap_ind

        else: return

        return self.bubbleUp(H, pointer_arr, swap_ind)

    def insertHeap(self, H, pointer_arr):
        return self.bubbleUp(H, pointer_arr, len(pointer_arr)-1)

    def deleteminHeap(self, H, pointer_arr):
        if not H:
            return None

        min_node = H[0][0]
        pointer_arr[min_node] = -1  # Mark as removed

        if len(H) == 1:
            H.pop()
            return min_node

        # Move last element to root
        H[0] = H.pop()
        pointer_arr[H[0][0]] = 0
        # Restore heap property
        self.percolateDown(H, 0, pointer_arr, len(H))

        return min_node


    def heapDijkstra(self, srcIndex):
        # intialization of return data structures
        dist = []
        prev = []

        # initialization of the dist, prev and array priority queue
        priority_queue = []
        pointer_arr = []
        for i in range(len(self.network.nodes)):
            if i == srcIndex:
                dist.append(0)
            else: dist.append(float('inf'))
            priority_queue.append([i,dist[i]])
            pointer_arr.append(i)
            self.insertHeap(priority_queue, pointer_arr)
            prev.append(None)
        #
        while len(priority_queue)!=0:
            # O(n) - traverse entire queue
            u = self.network.nodes[self.deleteminHeap(priority_queue, pointer_arr)]
            for e in u.neighbors:
                if pointer_arr[e.dest.node_id] != -1 and dist[e.dest.node_id] > dist[e.src.node_id] + e.length:
                    dist[e.dest.node_id] = dist[e.src.node_id] + e.length
                    prev[e.dest.node_id] = u
                    priority_queue[pointer_arr[e.dest.node_id]][1] = dist[e.dest.node_id]
                    self.bubbleUp(priority_queue, pointer_arr, pointer_arr[e.dest.node_id])
        self.dist = dist
        self.prev = prev
        return None

    def getShortestPath( self, destIndex ):
        self.dest = destIndex
        # TODO: RETURN THE SHORTEST PATH FOR destIndex
        #       INSTEAD OF THE DUMMY SET OF EDGES BELOW
        #       IT'S JUST AN EXAMPLE OF THE FORMAT YOU'LL
        #       NEED TO USE
        path_edges = []
        total_length = 0
        node = self.network.nodes[self.dest]
         # Check if path exists
        if self.prev[node.node_id] is None:
            return {'cost': float('inf'), 'path': []}
        while node.node_id != self.source:
            prev_node = self.prev[node.node_id]
            for i in prev_node.neighbors:
                if i.dest == node: length = i.length
            edge = CS4412GraphEdge(prev_node, node, length)
            path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
            total_length += edge.length
            node = prev_node
        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()
        # TODO: RUN DIJKSTRA'S TO DETERMINE SHORTEST PATHS.
        #       ALSO, STORE THE RESULTS FOR THE SUBSEQUENT
        #       CALL TO getShortestPath(dest_index)
        if(use_heap): self.heapDijkstra(srcIndex)
        else: self.arrayDijkstra(srcIndex)
        t2 = time.time()
        return (t2-t1)
