[English](README.md) | [Español](README.es.md)

# Knapsack Problem

The 0/1 knapsack problem consists of selecting, from a given set of **$n$ items** (each with an associated value $V_i$ and volume $V_i$), a subset that fits within a knapsack of total capacity **$V$** such that the **total accumulated value is maximized**.

Using computational methods, solve the following problem:

> **Determine which items from the list below should be loaded into a knapsack of capacity 4200 cm³ to maximize the total value in $.**

| Item | Volume (cm³) | Value ($) |
|:---:|:---:|:---:|
| 1 | 150 | 20 |
| 2 | 325 | 40 |
| 3 | 600 | 50 |
| 4 | 805 | 36 |
| 5 | 430 | 25 |
| 6 | 1200 | 64 |
| 7 | 770 | 54 |
| 8 | 60 | 18 |
| 9 | 930 | 46 |
| 10 | 353 | 28 |

> **Maximum capacity supported by the knapsack:** **4200 cm³.**

---

To find the solution, implement an **exhaustive procedure** that evaluates every possible candidate subset, computes its corresponding value and feasibility, sorts all valid subsets in descending order of value, and identifies the optimal solution subset.

## Exercises

1. Solve the **Knapsack problem using exhaustive search**.
2. Solve the previous problem using the **greedy algorithm**, comparing its behavior, speed, and optimality with the exhaustive approach.
3. Reformulate the knapsack problem considering **weight** instead of volume. Given **3 items** with the following weights:
   - 1800 g,
   - 600 g,
   - and 1200 g,

   and corresponding values:
   - $72,
   - $36,
   - and $60 respectively,

   with a knapsack capacity supporting up to **3000 g**, complete the following tasks:

   A) Find a solution using both **greedy and exhaustive algorithms**.

   B) Analyze each solution regarding its **degree of optimality** and formulate appropriate analytical conclusions.