[English](README.md) | [Español](README.es.md)

# Traveling Salesperson Problem (TSP)

The Traveling Salesperson Problem (also known as the Traveling Salesman Problem or **TSP**) is one of the most famous and extensively researched challenges in computational combinatorial optimization.

Despite the apparent simplicity of its formulation, the TSP is one of the most computationally complex problems to solve to optimality.

**Formal Definition:** Given $N$ cities within a geographical territory, the pairwise distances are defined by a matrix $D: N \times N$, where $d[x, y]$ represents the distance between city $X$ and city $Y$.

The objective is to discover a closed tour that, beginning and ending at a designated city, visits each of the remaining cities exactly once while minimizing the total path distance traversed.

---

## Exercises

1. Determine the minimum distance route connecting all provincial capitals of the Argentine Republic using an **exhaustive search method**. Can this method solve the problem in practice? Provide a rigorous theoretical justification.
2. Develop an application with a **menu providing the following options**:
   - **a)** Allow the user to input a provincial capital and compute the minimum route connecting all Argentine provincial capitals starting from that city using the following heuristic: *"From each city, proceed to the nearest unvisited city."* Always return to the starting city upon visiting all nodes. Present an interactive map of the Argentine Republic illustrating the computed route, displaying the origin city, the full sequence of visited capitals, and the total path distance.
   - **b)** Compute the best overall route to visit all provincial capitals by evaluating the nearest neighbor heuristic from every possible starting capital. Output the optimal trajectory and total journey length.
   - **c)** Find the minimum distance route visiting all Argentine provincial capitals using a **Genetic Algorithm**.

---

## Algorithm Specifications and Recommendations

- **$N = 50$:** Chromosome population size.
- **$M = 200$:** Total generational cycle count.
- **Chromosome Representation:** Permutations of 23 natural numbers from 1 to 23, where each gene encodes a unique provincial capital index.
- Crossover and mutation probabilities are left to the team's experimental discretion.
- **Cycle Crossover (CX)** must be implemented to preserve valid city permutations without duplication.

---

## Final Report Requirements

- Compare experimental findings between heuristic approaches and Genetic Algorithms, providing analytical conclusions appended to the report.
- Include a concluding chapter titled **"Practical Applications of the TSP"**, detailing real-world engineering and logistics scenarios where the Traveling Salesperson Problem is actively utilized today (analyze and explain at least two distinct practical use cases).
