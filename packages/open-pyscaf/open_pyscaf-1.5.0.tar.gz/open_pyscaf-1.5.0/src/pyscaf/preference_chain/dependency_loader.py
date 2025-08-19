from collections import defaultdict
from typing import List

import yaml
from pydantic import ValidationError

from .model import Node

# Load dependencies from a YAML file and complete the 'after' property if possible
# Returns a list of Node objects
# - If 'after' is missing and there is only one 'depends', it is auto-completed
# - Warns if there are multiple 'depends' but no 'after'


def load_and_complete_dependencies(yaml_path: str) -> List[Node]:
    """
    Load dependencies from a YAML file and complete the 'after' property if possible.
    Returns a list of Node objects.
    """
    with open(yaml_path, "r") as f:
        raw_dependencies = yaml.safe_load(f)

    dependencies = []
    for entry in raw_dependencies:
        try:
            # Convert entry to Node format
            node_data = {
                "id": entry["id"],
                "depends": set(entry.get("depends", [])),
                "after": entry.get("after"),
            }
            dep = Node(**node_data)
        except ValidationError as e:
            print(f"Validation error for dependency '{entry.get('id', '?')}': {e}")
            continue
        # If 'after' is missing and there is only one 'depends', set 'after' to that dependency
        if dep.after is None:
            if dep.depends:
                if len(dep.depends) == 1:
                    dep.after = next(iter(dep.depends))
                else:
                    print(
                        f"WARNING: Dependency '{dep.id}' has multiple 'depends' but no 'after'."
                    )
        dependencies.append(dep)
    return dependencies


# Build a dependency tree starting from root_id, following 'after' recursively
# Returns a tuple (tree, extra_depends) where:
#   - tree is a nested dict representing the after-chain
#   - extra_depends is a set of ids that are depends but not in the after-chain


def build_dependency_tree(
    dependencies: list[Node], root_id: str
) -> tuple[dict, set[str]]:
    """
    Build a dependency tree starting from root_id, following 'after' recursively.
    Returns a tuple (tree, extra_depends) where:
      - tree is a nested dict representing the after-chain
      - extra_depends is a set of ids that are depends but not in the after-chain
    """
    # Build a reverse index: for each id, who has after == id ?
    after_targets: defaultdict[str, list[Node]] = defaultdict(list)
    for dep in dependencies:
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

    tree = {root_id: _build(root_id)}
    return tree, extra_depends
