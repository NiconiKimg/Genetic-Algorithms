[English](README.md) | [Español](README.es.md)

# Practical Assignment No. 1

Develop a program using a **Canonical Genetic Algorithm** to find a maximum of the objective function:

$$
f(x) = \left(\frac{x}{\text{coef}}\right)^2
$$

within the domain $[0, 2^{30} - 1]$

where $\text{coef} = 2^{30} - 1$

Considering the following input parameters:

- **Crossover Probability:** 0.75
- **Mutation Probability:** 0.05
- **Initial Population:** 10 individuals
- **Program Cycles (Generations):** 20
- **Selection Method:** Roulette Wheel
- **Crossover Method:** 1-Point
- **Mutation Method:** Bit-inversion (bit-flip)

---

## Option A

The program must display, upon termination:

- The chromosome corresponding to the maximum value found.
- The maximum, minimum, and average values obtained for each population generation.
- The standard deviation of fitness per generation (visually demonstrating population convergence - low deviation - or ongoing diversity - high deviation).
- Analytical explanations of observed behavior in the conclusions.
- Computation time measurement.
- A table reporting average execution time for each iteration variant (20, 100, and 200 cycles) and each method (Roulette Wheel, Tournament, Elitism). Analyze the trade-off between solution quality and computational cost.
- Printout of tables showing minimum, average, and maximum fitness values for 20, 100, and 200 cycles.
- Comparative plots of Maximum, Minimum, and Average objective function values per generation across 20, 100, and 200 iterations (one graph per iteration count).
- Comparative analysis running the program across different iteration counts, introducing appropriate adjustments to input parameters to enrich the experimental conclusions.

---

## Option B

Apply the requirements specified in Option A using the **Tournament Selection** method.

---

## Option C

An **elite** is understood as a small group that, due to specific characteristics, fitness, or privileges, is superior compared to the bulk of a given population.

From an optimization perspective, a genetic algorithm is a population-based directed search method governed by probability. Under the mild condition that the algorithm maintains elitism - preserving the best element in the population unchanged across generations - it can be formally proven that the algorithm converges in probability to the global optimum. In other words, as the number of iterations increases, the probability of containing the optimal solution within the population approaches one.

Consequently, **elitism** is the most widely adopted technique to improve genetic algorithm convergence.

In this assignment, elitism is implemented during selection as follows:

- Sampling is performed over an elite of members: for this exercise, the two chromosomes exhibiting the highest fitness in the current population are selected and transferred directly into the subsequent generation, bypassing intermediate population sampling.
- This process repeats for each generation until the designated number of iterations is completed. Execution of 100 iterations is requested.

For this third part, implement elitism and output the console results and plots requested in Parts A and B under elitist preservation. Solve the problem executing 100 algorithm iterations.

Compare all three methods (Roulette Wheel, Tournament, Elitism) across:

- Best fitness achieved
- Generation in which the best fitness was reached
- Stability (standard deviation across runs)
- Execution time

Additionally, adjust selected input parameters to extract meaningful conclusions based on experimental findings.

---

## Final Report Format

- **Theoretical Introduction** (Canonical GA, Elitism)
- **Problem Description and Objective Function**
- **Fixed and Variable Parameters** (summary table)
- **Encoding and Results for Option A** (Roulette Wheel)
- **Encoding and Results for Option B** (Tournament)
- **Encoding and Results for Option C** (Elitism)
- **Additional Experiments** (parameter sensitivity analysis)
- **Comparative Plots** (maximum, minimum, average fitness)
- **Summary Table of Stability and Execution Times**
- **Conclusions and Final Recommendations**
