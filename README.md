# Package Dependency Resolver (DFS Topological Sort)

**1st Place Winning Project — Ananthya Python Hackathon (CSI × IEEE) at DSATM**

## Overview
A zero-dependency package manager utility modeled after Python's `pip` installer. This tool ingests raw package dependency configurations, builds a Directed Graph using native Python data structures, and computes a valid installation order or isolates circular dependency deadlocks.

## Key Engineering Features
* **Directed Graph Parser:** Converts unstructured multi-line dependency lists into an adjacency list dictionary without external libraries.
* **3-State DFS Topological Sort:** Uses Depth-First Search with active `visiting` and `done` state tracking to guarantee every dependency is installed before the parent package in linear $O(V + E)$ time.
* **Automated Cycle Detection:** Identifies back-edges in the recursion stack and extracts the exact circular dependency loop (e.g., `Cycle detected: A -> B -> A`).
* **Missing Dependency Validation:** Scans graph edges prior to execution to flag required packages that lack definitions.
* **ASCII Dependency Tree & Live CLI:** Renders a visual hierarchy of package relationships with recursion guards and includes an interactive terminal mode for live testing.

## Sample Input & Output

### Input
```text
A: B, C
B: C
C:
