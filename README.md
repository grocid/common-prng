# Inversion of Some Common PRNGs

The aim of this project is to provide some efficient methods to attack non-cryptographic random-number generators.

## `System.Random`

The implementation of the `Random` class in C# is based on Donald E. Knuth's subtractive random-number generator algorithm. It has a state which is 31 bits and is seeded by `Environment.TickCount`. This repository provides a CUDA implementation for bruteforcing the seed for a special case when `0 < MAX - MIN < INT_MAX`.

## `Seedrandom.Alea`

Alea is a Marsaglia-type random-number generator originally created by Baagøe. The state is very large and it operates on floating-point numbers. A Z3 implementation is provided.