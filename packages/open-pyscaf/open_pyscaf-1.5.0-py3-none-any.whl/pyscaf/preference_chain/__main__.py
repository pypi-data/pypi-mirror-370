import logging
import os
import sys

from pyscaf.preference_chain import best_execution_order

from .dependency_loader import load_and_complete_dependencies

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    if "-v" in sys.argv:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s %(name)s::%(funcName)s: \n    %(message)s",
        )
        logger.debug("Mode debug activé")
    else:
        logging.basicConfig(
            level=logging.WARNING, format="\n    %(levelname)s: %(message)s"
        )

    # Load and complete dependencies from YAML
    yaml_path = os.path.join(os.path.dirname(__file__), "dependencies.yaml")
    dependencies = load_and_complete_dependencies(yaml_path)
    best_execution_order(dependencies)
    # tree = DependencyTreeWalker(dependencies, "root")
    # extended_dependencies = extend_nodes(dependencies)
    # # for dep in extended_dependencies:
    # #     logger.debug(dep)
    # #     print("\n")
    # clusters = build_chains(extended_dependencies)

    # # for cluster in clusters:
    # #     logger.debug(cluster)
    # #     print("\n")
    # # logger.debug(tree.print_tree())
    # all_resolution_pathes = list(compute_all_resolution_pathes(clusters))
    # logger.debug(f"Found {len(all_resolution_pathes)} resolution pathes")
    # all_resolution_pathes.sort(key=lambda path: -compute_path_score(list(path)))
    # for path in all_resolution_pathes:
    #     logger.debug(f"Score : {compute_path_score(path)}")
    #     for chain in list(path):
    #         logger.debug(f"Chain: {chain.ids}")
    # final_path = [id for chain in all_resolution_pathes[0] for id in chain.ids]
    # logger.info(f"Best resolution path: {final_path}")
