from collections import defaultdict

from .model import Node


class DependencyTreeWalker:
    def __init__(self, dependencies: list[Node], root_id: str):
        self.dependencies = dependencies
        self.root_id = root_id
        self.tree = None
        self.external_depends = set()
        self.fullfilled_depends = set()
        self._build_tree()

    def _build_tree(self):
        # Build a reverse index: for each id, who has after == id ?
        after_targets: defaultdict[str, list[Node]] = defaultdict(list)
        for dep in self.dependencies:
            if dep.after:
                after_targets[dep.after].append(dep)

        visited: set[str] = set()
        extra_depends: set[str] = set()

        # Recursive helper to build the tree
        def _build(current_id: str) -> dict:
            if current_id in visited:
                return {}  # Prevent cycles
            visited.add(current_id)
            children = {}
            for dep in after_targets.get(current_id, []):
                # For each dependency that targets current_id via 'after', build its subtree
                children[dep.id] = _build(dep.id)
                # If there are multiple 'depends', collect additional dependencies as external
                if dep.depends and len(dep.depends) > 1:
                    for d in dep.depends:
                        if d != current_id:
                            extra_depends.add(d)
            return children

        # Build the tree and collect external and fulfilled dependencies
        self.tree = {self.root_id: _build(self.root_id)}
        self.external_depends = extra_depends
        self.fullfilled_depends = visited

    def print_tree(self):
        """
        Print the dependency tree in a graphical way (like the 'tree' utility).
        External dependencies (extra_depends) are shown in red.
        Fulfilled dependencies are shown in green.
        """
        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        def _print_subtree(subtree, prefix=""):
            items = list(subtree.items())
            for idx, (node, children) in enumerate(items):
                connector = "└── " if idx == len(items) - 1 else "├── "
                print(prefix + connector + node)
                if children:
                    extension = "    " if idx == len(items) - 1 else "│   "
                    _print_subtree(children, prefix + extension)

        # Print the main tree
        _print_subtree(self.tree)
        # Print external dependencies not shown in the tree
        shown = set()

        def _collect_shown(subtree):
            for node, children in subtree.items():
                shown.add(node)
                _collect_shown(children)

        _collect_shown(self.tree)
