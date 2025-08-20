"""
IR Workflow representation for AXL Workflows.

This module contains the IRWorkflow class that represents the complete
workflow structure for backend compilation.
"""

from typing import Any

from .nodes import IREdge, IRNode


class IRWorkflow:
    """
    Intermediate representation of a workflow.

    This class contains the complete workflow structure including
    nodes (steps), edges (dependencies), and metadata needed for
    backend compilation.
    """

    def __init__(
        self,
        name: str,
        image: str,
        io_handler: str,
        nodes: list[IRNode],
        edges: list[IREdge],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize IR workflow.

        Args:
            name: Workflow name
            image: Docker image for execution
            io_handler: Default IO handler
            nodes: List of workflow nodes (steps)
            edges: List of workflow edges (dependencies)
            metadata: Additional workflow metadata
        """
        self.name = name
        self.image = image
        self.io_handler = io_handler
        self.nodes = nodes
        self.edges = edges
        self.metadata = metadata or {}

        # Fast index for node lookups
        self._node_index: dict[str, IRNode] = {node.name: node for node in self.nodes}

    def get_node(self, name: str) -> IRNode | None:
        """
        Get a node by name.

        Args:
            name: Node name to find

        Returns:
            IRNode if found, None otherwise
        """
        return self._node_index.get(name)

    def get_node_dependencies(self, node_name: str) -> list[IRNode]:
        """
        Get all nodes that the given node depends on.

        Args:
            node_name: Name of the node

        Returns:
            List of dependency nodes
        """
        dependencies = []
        for edge in self.edges:
            if edge.target == node_name:
                dep_node = self.get_node(edge.source)
                if dep_node:
                    dependencies.append(dep_node)
        return dependencies

    def get_node_dependents(self, node_name: str) -> list[IRNode]:
        """
        Get all nodes that depend on the given node.

        Args:
            node_name: Name of the node

        Returns:
            List of dependent nodes
        """
        dependents = []
        for edge in self.edges:
            if edge.source == node_name:
                dep_node = self.get_node(edge.target)
                if dep_node:
                    dependents.append(dep_node)
        return dependents

    def validate(self) -> None:
        """
        Validate the workflow structure.

        Raises:
            ValueError: If workflow is invalid
        """
        # Check for cycles
        if self._has_cycles():
            raise ValueError(f"Workflow '{self.name}' contains cycles")

        # Check for orphaned nodes
        orphaned = self._find_orphaned_nodes()
        if orphaned:
            raise ValueError(f"Workflow '{self.name}' has orphaned nodes: {orphaned}")

        # Check for missing dependencies
        missing = self._find_missing_dependencies()
        if missing:
            raise ValueError(
                f"Workflow '{self.name}' has missing dependencies: {missing}"
            )

    def _has_cycles(self) -> bool:
        """Check if the workflow has cycles using DFS."""
        visited = set()
        rec_stack = set()

        def dfs(node_name: str) -> bool:
            if node_name in rec_stack:
                return True
            if node_name in visited:
                return False

            visited.add(node_name)
            rec_stack.add(node_name)

            for edge in self.edges:
                if edge.source == node_name:
                    if dfs(edge.target):
                        return True

            rec_stack.remove(node_name)
            return False

        for node in self.nodes:
            if dfs(node.name):
                return True
        return False

    def _find_orphaned_nodes(self) -> list[str]:
        """Find nodes that are not connected to the workflow."""
        # Special case: single node workflows are valid (no edges needed)
        if len(self.nodes) == 1:
            return []

        connected = set()
        for edge in self.edges:
            connected.add(edge.source)
            connected.add(edge.target)

        orphaned = []
        for node in self.nodes:
            if node.name not in connected:
                orphaned.append(node.name)
        return orphaned

    def _find_missing_dependencies(self) -> list[str]:
        """Find edges that reference non-existent nodes."""
        node_names = {node.name for node in self.nodes}
        missing = []
        for edge in self.edges:
            if edge.source not in node_names:
                missing.append(f"source '{edge.source}'")
            if edge.target not in node_names:
                missing.append(f"target '{edge.target}'")
        return missing

    def __repr__(self) -> str:
        """String representation of the IR workflow."""
        return (
            f"IRWorkflow(name='{self.name}', "
            f"nodes={len(self.nodes)}, "
            f"edges={len(self.edges)})"
        )
