import re
import sys

class DependencyResolver:
    """
    O(1) Dynamics - Complete Dependency Resolver & Version Engine
    Implements DFS Topological Sort, Cycle Detection, ASCII Tree Visualization,
    and Semantic Version Constraint Resolution.
    """
    def __init__(self, raw_input):
        self.raw_input = raw_input
        self.graph = {}               # {pkg: [dep_pkg_1, dep_pkg_2]}
        self.constraints = {}         # {dep_pkg: [(required_by_pkg, operator_str, version_num)]}
        self.available_versions = {}  # {pkg: [v1, v2, v3]}
        self.has_version_rules = False

    def parse_input(self):
        """
        Parses standard lines like 'A: B, C' as well as versioned lines like:
        'A: B >= 2, C == 1' or 'B [1, 2, 3]: C'
        """
        lines = self.raw_input.strip().split('\n')
        dep_pattern = re.compile(r'^([a-zA-Z0-9_-]+)\s*(?:(>=|<=|==|!=|>|<)\s*(\d+(?:\.\d+)?))?$')
        pkg_header_pattern = re.compile(r'^([a-zA-Z0-9_-]+)(?:\s*\[([\d\s,.]+)\])?$')

        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                continue

            lhs, rhs = line.split(':', 1)
            lhs = lhs.strip()
            rhs = rhs.strip()

            # Parse package name and optional available versions (e.g., "B [1, 2, 3]")
            header_match = pkg_header_pattern.match(lhs)
            if header_match:
                pkg_name = header_match.group(1)
                vers_str = header_match.group(2)
                if vers_str:
                    self.available_versions[pkg_name] = sorted(
                        [float(v.strip()) if '.' in v else int(v.strip()) for v in vers_str.split(',') if v.strip()]
                    )
                else:
                    # Default available versions [1, 2, 3, 4, 5] if not explicitly listed
                    self.available_versions.setdefault(pkg_name, [1, 2, 3, 4, 5])
            else:
                pkg_name = lhs
                self.available_versions.setdefault(pkg_name, [1, 2, 3, 4, 5])

            self.graph.setdefault(pkg_name, [])

            # Handle packages with no dependencies
            if not rhs:
                continue

            # Parse each dependency and any attached version rule (e.g., "B >= 2")
            for raw_dep in rhs.split(','):
                raw_dep = raw_dep.strip()
                if not raw_dep:
                    continue

                match = dep_pattern.match(raw_dep)
                if match:
                    dep_name = match.group(1)
                    op_str = match.group(2)
                    ver_str = match.group(3)

                    self.graph[pkg_name].append(dep_name)

                    if op_str and ver_str:
                        self.has_version_rules = True
                        ver_val = float(ver_str) if '.' in ver_str else int(ver_str)
                        self.constraints.setdefault(dep_name, []).append((pkg_name, op_str, ver_val))
                else:
                    self.graph[pkg_name].append(raw_dep)

    def check_undefined_packages(self):
        """
        Checks if any required dependency is missing from the defined package list.
        """
        defined = set(self.graph.keys())
        for pkg, deps in self.graph.items():
            for dep in deps:
                if dep not in defined:
                    return (
                        f"Missing Dependency Error: Package '{dep}' is needed by '{pkg}', "
                        f"but '{dep}' is not defined in the package list."
                    )
        return None

    def check_version_Rule(self, version, op, target):
        if op == '>=': return version >= target
        if op == '<=': return version <= target
        if op == '==': return version == target
        if op == '!=': return version != target
        if op == '>':  return version > target
        if op == '<':  return version < target
        return True

    def resolve_versions(self):
        """
        BONUS: Evaluates version rules, picks the newest compatible version,
        or explains a conflict in plain English words.
        """
        selected_versions = {}
        for pkg, avail_list in self.available_versions.items():
            pkg_constraints = self.constraints.get(pkg, [])
            if not pkg_constraints:
                # Pick newest version by default
                selected_versions[pkg] = max(avail_list)
                continue

            compatible = []
            for v in avail_list:
                if all(self.check_version_Rule(v, op, target) for _, op, target in pkg_constraints):
                    compatible.append(v)

            if not compatible:
                # Explain the conflict in plain words
                reasons = [f"Package '{req_by}' requires {pkg} {op} {target}" for req_by, op, target in pkg_constraints]
                explanation = " and ".join(reasons)
                return None, (
                    f"Version Conflict Explained: Cannot install package '{pkg}'. "
                    f"{explanation}. Available versions for '{pkg}' are {avail_list}, "
                    f"and no single version satisfies all rules simultaneously."
                )

            # Pick the newest compatible version
            selected_versions[pkg] = max(compatible)

        return selected_versions, None

    def build_dependency_tree(self):
        """
        BONUS: Generates a visual ASCII dependency tree for all root packages.
        Safely guards against infinite recursion if a cycle exists.
        """
        lines = ["Dependency Tree:"]
        
        def _render_node(node, prefix="", is_last=True, visited_in_branch=None):
            if visited_in_branch is None:
                visited_in_branch = set()
                
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{node}")
            
            if node in visited_in_branch:
                lines[-1] += " (CYCLE LOOP!)"
                return
                
            new_visited = visited_in_branch | {node}
            deps = self.graph.get(node, [])
            for idx, dep in enumerate(deps):
                last_child = (idx == len(deps) - 1)
                extension = "    " if is_last else "│   "
                _render_node(dep, prefix + extension, last_child, new_visited)

        for idx, pkg in enumerate(self.graph.keys()):
            _render_node(pkg, "", idx == len(self.graph) - 1)
            
        return "\n".join(lines)

    def resolve(self):
        """
        Main execution pipeline:
        1. Parse Input
        2. Build Dependency Tree
        3. Check Undefined Packages
        4. Run DFS Topological Sort & Cycle Detection
        5. Resolve Version Rules (if present)
        """
        self.parse_input()
        if not self.graph:
            return "Error: No valid packages found in input."

        tree_output = self.build_dependency_tree()

        # Check for undefined packages first
        undefined_err = self.check_undefined_packages()
        if undefined_err:
            return f"{tree_output}\n\n-> {undefined_err}"

        # DFS States: 0 = unvisited, 1 = visiting (in current stack), 2 = done
        state = {pkg: 0 for pkg in self.graph}
        install_order = []
        path_stack = []

        def dfs(node):
            if state[node] == 1:
                cycle_start = path_stack.index(node)
                cycle_loop = path_stack[cycle_start:] + [node]
                raise ValueError(f"Cycle detected: {' -> '.join(cycle_loop)}")
            if state[node] == 2:
                return

            state[node] = 1
            path_stack.append(node)

            for dep in self.graph[node]:
                dfs(dep)

            path_stack.pop()
            state[node] = 2
            install_order.append(node)

        try:
            for pkg in self.graph:
                if state[pkg] == 0:
                    dfs(pkg)
        except ValueError as cycle_err:
            return f"{tree_output}\n\n-> {cycle_err}"

        # Check version constraints if any were specified
        if self.has_version_rules:
            selected_vers, conflict_err = self.resolve_versions()
            if conflict_err:
                return f"{tree_output}\n\n-> {conflict_err}"
            
            formatted_order = [
                f"{pkg} (v{selected_vers[pkg]})" if pkg in self.constraints else pkg
                for pkg in install_order
            ]
            return f"{tree_output}\n\n-> Install order (with newest compatible versions): {', '.join(formatted_order)}"

        return f"{tree_output}\n\n-> Install order: {', '.join(install_order)}"


def run_benchmark_suite():
    print("=" * 65)
    print("   O(1) DYNAMICS - PACKAGE DEPENDENCY RESOLVER (BENCHMARK SUITE)")
    print("=" * 65)

    tests = [
        ("1. Standard Sample List (Must-Have)", """
A: B, C
B: C
C:
"""),
        ("2. Circular Dependency Detection (Must-Have)", """
A: B, C
B: C, A
C:
"""),
        ("3. Undefined Package Reporting (Must-Have)", """
A: B, D
B: C
C:
"""),
        ("4. Version Rules & Newest Compatible Pick (Bonus Level-Up)", """
A: B >= 2, C
B [1, 2, 3]: C >= 2
C [1, 2, 3, 4]:
"""),
        ("5. Plain-English Version Conflict Explanation (Bonus Level-Up)", """
App: Database >= 3, Auth
Auth: Database < 2
Database [1, 2, 3, 4]:
""")
    ]

    for title, sample_input in tests:
        print(f"\n[{title}]")
        print("Input:")
        for line in sample_input.strip().split('\n'):
            print(f"  {line}")
        print("-" * 45)
        resolver = DependencyResolver(sample_input)
        print(resolver.resolve())
        print("=" * 65)


def interactive_mode():
    print("\n--- INTERACTIVE JUDGE TESTING MODE ---")
    print("Paste or type your package list below. Type 'DONE' on a new line to run (or 'EXIT' to quit):")
    while True:
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                return
            if line.strip().upper() == 'EXIT':
                return
            if line.strip().upper() == 'DONE':
                break
            lines.append(line)
        
        if lines:
            print("\n--- Resolution Output ---")
            resolver = DependencyResolver("\n".join(lines))
            print(resolver.resolve())
            print("\nType another package list followed by 'DONE', or 'EXIT' to quit:")


if __name__ == "__main__":
    run_benchmark_suite()
    interactive_mode()
