# O(1) Dynamics - Package Dependency Resolver
# 100% Native Python - With Live Judge Input Mode

def print_tree(graph, pkg, indent="", seen=None):
    """BONUS: Prints a visual ASCII dependency tree."""
    if seen is None:
        seen = []
    print(indent + "└── " + pkg)
    if pkg in seen:
        return  # Stops infinite recursion if a circular loop exists
    for dep in graph.get(pkg, []):
        print_tree(graph, dep, indent + "    ", seen + [pkg])


def resolve_dependencies(raw_text):
    graph = {}

    # STEP 1: Read the package list and build the dictionary
    lines = raw_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line == "" or ":" not in line:
            continue

        parts = line.split(":")
        pkg = parts[0].strip()       # Package name on the left of ':'
        deps_str = parts[1].strip()  # Dependencies on the right of ':'

        # Handle a package with no dependencies (e.g., "C:")
        if deps_str == "":
            graph[pkg] = []
        else:
            dep_list = []
            for d in deps_str.split(","):
                if d.strip() != "":
                    dep_list.append(d.strip())
            graph[pkg] = dep_list

    if len(graph) == 0:
        return "-> Error: Please enter valid package lines containing ':'"

    # Print the Bonus Dependency Tree
    print("\nDependency Tree:")
    for pkg in graph:
        print_tree(graph, pkg)

    # STEP 2: Report a package that is needed but not defined
    for pkg in graph:
        for dep in graph[pkg]:
            if dep not in graph:
                return f"\n-> Error: Package '{dep}' is needed by '{pkg}', but '{dep}' is not defined."

    # STEP 3: DFS using 'visiting' and 'done' lists
    visiting = []  # Tracks active path to detect circular dependencies
    done = []      # Tracks completed packages in valid install order

    def dfs(pkg):
        # If already installed, skip it
        if pkg in done:
            return

        # If currently in 'visiting', we found a circular loop!
        if pkg in visiting:
            loop_start = visiting.index(pkg)
            cycle_loop = visiting[loop_start:] + [pkg]
            raise ValueError(" -> ".join(cycle_loop))

        # Mark package as currently visiting
        visiting.append(pkg)

        # Recursively visit all dependencies first
        for dep in graph[pkg]:
            dfs(dep)

        # Unmark from visiting and add to done (install order)
        visiting.pop()
        done.append(pkg)

    # Run DFS across all packages in the graph
    try:
        for pkg in graph:
            dfs(pkg)
        return "\n-> Install order: " + ", ".join(done)
    except ValueError as cycle_path:
        return f"\n-> Cycle detected: {cycle_path}"


# --- PRE-LOADED SAMPLES & LIVE JUDGE INPUT ---
if __name__ == "__main__":
    print("=== TEST 1: Standard Sample List ===")
    sample_1 = """
    A: B, C
    B: C
    C:
    """
    print(resolve_dependencies(sample_1))

    print("\n=== TEST 2: Circular Dependency (Cycle Sample) ===")
    sample_2 = """
    A: B, C
    B: C, A
    C:
    """
    print(resolve_dependencies(sample_2))

    print("\n=== TEST 3: Needed But Not Defined ===")
    sample_3 = """
    A: B, D
    B: C
    C:
    """
    print(resolve_dependencies(sample_3))

    # --- LIVE INPUT MODE FOR JUDGES ---
    print("\n" + "=" * 55)
    print("   LIVE JUDGE INPUT MODE (Type 'exit' to quit)")
    print("=" * 55)
    print("Type your package lines below. Press ENTER twice when done:\n")

    while True:
        judge_lines = []
        while True:
            line = input()
            if line.strip().lower() == "exit":
                exit()
            # Pressing Enter on a blank line finishes the input block
            if line.strip() == "":
                break
            judge_lines.append(line)

        if len(judge_lines) > 0:
            custom_text = "\n".join(judge_lines)
            print(resolve_dependencies(custom_text))
            print("\n" + "-" * 55)
            print("Enter next package list (Press ENTER twice to run, or 'exit'):\n")