import logging
from typing import List

from pyscaf.preference_chain.chain import (
    build_chains,
    compute_all_resolution_pathes,
    compute_path_score,
    extend_nodes,
)
from pyscaf.preference_chain.model import Node

from .circular_dependency_error import CircularDependencyError
from .dependency_loader import load_and_complete_dependencies
from .model import Node
from .tree_walker import DependencyTreeWalker

logger = logging.getLogger(__name__)


def best_execution_order(nodes: List[Node]) -> List[str]:
    """
    Determine the best execution order using the preference chain logic.

    Args:
        nodes: List of Node objects with 'id', 'depends', and 'after' attributes

    Returns:
        List of node IDs in optimal execution order

    Raises:
        CircularDependencyError: If no valid resolution path can be found
    """
    # Ensure all nodes have proper 'after' field set if they have dependencies
    node_objects: List[Node] = []
    for node in nodes:
        # If node has dependencies but no 'after' is specified, use the first dependency
        if node.depends and node.after is None:
            after = next(iter(node.depends))
        else:
            after = node.after

        # Validate that 'after' is in the dependencies if specified
        if after is not None and after not in node.depends:
            raise ValueError(
                f"Node '{node.id}' has 'after'='{after}' but it's not in depends={node.depends}"
            )

        node_obj = Node(id=node.id, depends=node.depends, after=after)
        node_objects.append(node_obj)

    logger.debug(f"Processed {len(node_objects)} nodes")

    # Use the new preference chain logic
    extended_dependencies = extend_nodes(node_objects)
    clusters = build_chains(extended_dependencies)

    logger.debug(f"Built {len(clusters)} chains")

    # Compute all possible resolution paths
    all_resolution_paths = list(compute_all_resolution_pathes(clusters))

    if not all_resolution_paths:
        # No valid resolution path found - this indicates a serious dependency issue
        node_ids = [node.id for node in node_objects]
        error_msg = (
            f"No valid resolution path found for nodes: {node_ids}. "
            "This indicates circular dependencies or unsatisfiable constraints."
        )
        logger.error(error_msg)
        raise CircularDependencyError(error_msg)

    logger.debug(f"Found {len(all_resolution_paths)} resolution paths")

    # Sort paths by score (best score first)
    all_resolution_paths.sort(key=lambda path: -compute_path_score(list(path)))

    # Extract the final execution order from the best path
    best_path = all_resolution_paths[0]
    final_order = [node_id for chain in best_path for node_id in chain.ids]

    logger.debug(f"Best execution order: {final_order}")

    return final_order
