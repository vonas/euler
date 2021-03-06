#!/usr/bin/env python3
# https://projecteuler.net/problem=3


"""

if n is not a prime number, then it must have a prime factor
less than or equal to the square root of n.[citation needed]

to find the prime factors of n, we can check all prime numbers
until the square root of n and pick the largest that divides n evenly.

this is the solution to the problem.

"""


from math import sqrt

from helper.prime import primes


def solve(n):

    limit = int(sqrt(n))
    numbers = list(primes(end=limit))

    for p in reversed(numbers):
        if n % p == 0:
            return p

    return None


args = (600851475143,)
solution = 6857
