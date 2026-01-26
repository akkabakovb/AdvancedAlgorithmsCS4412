import random


def prime_test(N, k):
	# This is main function, that is connected to the Test button. You don't need to touch it.
	return fermat(N,k), miller_rabin(N,k)


def mod_exp(x, y, N):
    # Function: modexp
	# Time Complexity: O(n^3)
	# Space Complexity: O(n)

	#base case
	if y==0:
		return 1
	#recursive call with halved exponent
	z = mod_exp(x, y//2, N) # n-number of recursive calls (right bitshift)
	#check whether y is even or not
	if y % 2 == 0:
		return z**2 % N # z**2 = z*z that requres 2*n*2 time to multiply two n-bit numbers and take mod
	else:
		return x*z**2 % N


def fprobability(k):
    # For the Fermat primality test, if N is composite,
    # at most one half of the possible bases a in [1, N−1]
    # will fail to reveal this fact.
    # Thus, a single test falsely reports "prime" with
    # probability at most 1/2. For k independent tests,
    # the probability that all tests fail is 1/2^k.
    # Therefore, the probability that the algorithm is correct is:
    return 1-1/2**k


def mprobability(k):
    # ----------------------------------------------------- #
	# It turns out that if we combine this square-root check with
    # our earlier Fermat test, then at least three-fourths of the possible values of a between 1 and
    # N − 1 will reveal a composite N, even if it is a Carmichael number. (textbook)
	# ----------------------------------------------------- #
    # Hence, a single test falsely reports "prime" with
    # probability at most 1/4. With k independent tests,
    # the probability that all tests fail is (1/4)^k.
    # Therefore, the probability that the algorithm is correct is:
    return 1-1/4**k


def fermat(N,k):
    # Function: modexp
	# Time Complexity: O(k*n^3)
	# Space Complexity: O(k*n)

	r = [] # to store k n-bit integers -> k*n space required
	#populate list of k elements with random integers in range [1, N)
	for i in range(k+1):
		# reffering to the textbook those are a_1, a_2, a_3, ... a_k
		r.append(random.randint(1, N-1))
	for i in r: # there will be k number of iterations and each will take n^3 time
		#iterate over a_1, a_2,... a_k < N and
		if mod_exp(i,N-1,N)!=1: #modexp fucntion will execute n recursive calls with constant size variables-> n space
			#check whether a_i^(N-1) mod N equals 1 or not. If not -> composite
			return 'composite'
	return 'prime'


def miller_rabin(N,k):
	# Function: miller_rabin
	# Time Complexity: O(k*n^4)
	# Space Complexity: O(k*n)
	
	r = []						  # stores k n-bit integers → O(k*n) space
	for i in range(k+1):
		r.append(random.randint(1, N-1))  # k iterations → O(k) time
	#iterate over a_1, a_2,... a_k < N
	for i in r:        					  # k iterations
		#first, check whether a_i passes first test, i.e. Fermat Little Theorem
		if mod_exp(i, N-1, N)!=1:		  # O(n^3) time, O(n) stack space
			return 'composite'
		new_exp = N-1
		while new_exp % 2 != 1:			  # exponent halved → O(n) iterations
			#if exponent is even halve it, i.e. take the root
			new_exp = new_exp // 2
			res = mod_exp(i, new_exp, N)  # O(n^3) time, O(n) stack space
			if res != 1:
				#if the a_i^(...) mod N = -1 -> a_i passed and move to a_i+1
				if res == N-1:
					break
				else:
					#if the a_i^(...) mod N is neither -1 or 1 -> N is composite
					return 'composite'
	return 'prime'
