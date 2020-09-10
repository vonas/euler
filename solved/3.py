#!/usr/bin/env python3
# https://projecteuler.net/problem=3


"""

if n is not a prime number, then it must have a prime factor
less than or equal to the square root of n.[citation needed]

to find the prime factors of n, we can check all prime numbers
until the square root of n and pick the largest that divides n evenly.

this is the solution to the problem.

to find those prime numbers we can utilize the sieve of eratosthenes.

"""


from math import sqrt

from util import sieve


def solve(n):

    limit = int(sqrt(n))
    primes = sieve(limit)

    for p in reversed(primes):
        if n % p == 0:
            return p

    return None


n = 600851475143

if __name__ == '__main__':
    print(solve(n))  # 6857
