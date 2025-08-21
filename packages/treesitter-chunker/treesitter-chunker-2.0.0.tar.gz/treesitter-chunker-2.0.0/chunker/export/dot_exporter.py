"""DOT (Graphviz) export implementation for code chunks."""

from pathlib import Path

from .graph_exporter_base import GraphEdge, GraphExporterBase, GraphNode


class DotExporter(GraphExporterBase):
    """Export code chunks as DOT format for Graphviz visualization."""

    def __init__(self):
        super().__init__()
        self.graph_attrs: dict[str, str] = {
            "rankdir": "TB",
            "fontname": "Arial",
            "fontsize": "10",
            "compound": "true",
        }
        self.node_attrs: dict[str, str] = {
            "shape": "box",
            "style": "rounded,filled",
            "fillcolor": "lightblue",
            "fontname": "Arial",
            "fontsize": "10",
        }
        self.edge_attrs: dict[str, str] = {
            "fontname": "Arial",
            "fontsize": "8",
        }
        self.chunk_type_styles: dict[str, dict[str, str]] = {
            "class": {"shape": "box", "fillcolor": "lightgreen", "style": "filled"},
            "function": {
                "shape": "ellipse",
                "fillcolor": "lightblue",
                "style": "filled",
            },
            "method": {
                "shape": "ellipse",
                "fillcolor": "lightyellow",
                "style": "filled",
            },
            "module": {"shape": "tab", "fillcolor": "lightgray", "style": "filled"},
            "import": {"shape": "note", "fillcolor": "pink", "style": "filled"},
        }
        self.edge_type_styles: dict[str, dict[str, str]] = {
            "CONTAINS": {"style": "solid", "color": "black"},
            "IMPORTS": {"style": "dashed", "color": "blue"},
            "CALLS": {"style": "dotted", "color": "red"},
            "INHERITS": {"style": "solid", "color": "green", "arrowhead": "empty"},
            "DEFINES": {"style": "solid", "color": "purple", "penwidth": "2"},
            "HAS_METHOD": {"style": "solid", "color": "orange", "arrowhead": "diamond"},
        }

    @staticmethod
    def _escape_label(text: str) -> str:
        """Escape text for DOT labels."""
        text = text.replace("\\", "\\\\")
        text = text.replace('"', '\\"')
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "\\r")
        text = text.replace("\t", "\\t")
        return text

    @staticmethod
    def _format_node_id(node_id: str) -> str:
        """Format node ID for DOT syntax."""
        safe_id = node_id.replace(":", "_").replace("/", "_").replace(".", "_")
        safe_id = safe_id.replace("-", "_").replace(" ", "_")
        return f'"{safe_id}"'

    def _get_node_attributes(self, node: GraphNode) -> dict[str, str]:
        """Get attributes for a node based on its type."""
        attrs = self.node_attrs.copy()
        chunk_type = (
            node.chunk.metadata.get(
                "chunk_type",
                node.chunk.node_type,
            )
            if node.chunk.metadata
            else node.chunk.node_type
        )
        if chunk_type and chunk_type in self.chunk_type_styles:
            attrs.update(self.chunk_type_styles[chunk_type])
        label_parts = []
        chunk_type = (
            node.chunk.metadata.get(
                "chunk_type",
            )
            if node.chunk.metadata
            else None
        )
        chunk_type = chunk_type or node.chunk.node_type or "chunk"
        if node.chunk.metadata and "name" in node.chunk.metadata:
            label_parts.append(f"{node.chunk.metadata['name']} ({chunk_type})")
        else:
            label_parts.append(chunk_type)
        label_parts.append(
            f"{node.chunk.file_path}:{node.chunk.start_line}-{node.chunk.end_line}",
        )
        if node.chunk.metadata:
            if "complexity" in node.chunk.metadata:
                label_parts.append(f"Complexity: {node.chunk.metadata['complexity']}")
            if "token_count" in node.chunk.metadata:
                label_parts.append(f"Tokens: {node.chunk.metadata['token_count']}")
        attrs["label"] = self._escape_label("\\n".join(label_parts))
        return attrs

    def _get_edge_attributes(self, edge: GraphEdge) -> dict[str, str]:
        """Get attributes for an edge based on its type."""
        attrs = self.edge_attrs.copy()
        if edge.relationship_type in self.edge_type_styles:
            attrs.update(self.edge_type_styles[edge.relationship_type])
        attrs["label"] = edge.relationship_type
        if edge.properties:
            tooltip_parts = [f"{k}: {v}" for k, v in edge.properties.items()]
            attrs["tooltip"] = self._escape_label("; ".join(tooltip_parts))
        return attrs

    @staticmethod
    def _format_attributes(attrs: dict[str, str]) -> str:
        """Format attributes for DOT syntax."""
        if not attrs:
            return ""
        attr_parts = []
        for key, value in attrs.items():
            attr_parts.append(f'{key}="{value}"')
        return f" [{', '.join(attr_parts)}]"

    def export_string(self, use_clusters: bool = True, **_options) -> str:
        """Export the graph as a DOT string.

        Args:
            use_clusters: Whether to group nodes by file/module
            **options: Additional options

        Returns:
            DOT representation as a string
        """
        lines = []
        lines.append("digraph CodeGraph {")
        for key, value in self.graph_attrs.items():
            lines.append(f'  {key}="{value}";')
        lines.append(f"  node{self._format_attributes(self.node_attrs)};")
        lines.append(f"  edge{self._format_attributes(self.edge_attrs)};")
        lines.append("")
        if use_clusters:
            clusters = self.get_subgraph_clusters()
            for cluster_idx, (cluster_name, node_ids) in enumerate(clusters.items()):
                lines.append(f"  subgraph cluster_{cluster_idx} {{")
                lines.append(
                    f'    label="{self._escape_label(cluster_name)}";',
                )
                lines.append('    style="rounded,filled";')
                lines.append('    fillcolor="lightgray";')
                lines.append('    color="black";')
                lines.append("")
                for node_id in node_ids:
                    if node_id in self.nodes:
                        node = self.nodes[node_id]
                        attrs = self._get_node_attributes(node)
                        lines.append(
                            f"    {self._format_node_id(node_id)}{self._format_attributes(attrs)};",
                        )
                lines.append("  }")
                lines.append("")
            clustered_nodes = set()
            for node_ids in clusters.values():
                clustered_nodes.update(node_ids)
            for node_id, node in self.nodes.items():
                if node_id not in clustered_nodes:
                    attrs = self._get_node_attributes(node)
                    lines.append(
                        f"  {self._format_node_id(node_id)}{self._format_attributes(attrs)};",
                    )
        else:
            for node_id, node in self.nodes.items():
                attrs = self._get_node_attributes(node)
                lines.append(
                    f"  {self._format_node_id(node_id)}{self._format_attributes(attrs)};",
                )
        lines.append("")
        for edge in self.edges:
            attrs = self._get_edge_attributes(edge)
            source = self._format_node_id(edge.source_id)
            target = self._format_node_id(edge.target_id)
            lines.append(f"  {source} -> {target}{self._format_attributes(attrs)};")
        lines.append("}")
        return "\n".join(lines)

    def export(
        self,
        output_path: Path,
        use_clusters: bool = True,
        **options,
    ) -> None:
        """Export the graph to a DOT file.

        Args:
            output_path: Path to write the DOT file
            use_clusters: Whether to group nodes by file/module
            **options: Additional options
        """
        dot_content = self.export_string(use_clusters=use_clusters, **options)
        output_path.write_text(dot_content, encoding="utf-8")

    def set_graph_attribute(self, key: str, value: str) -> None:
        """Set a graph-level attribute."""
        self.graph_attrs[key] = value

    def set_node_style(self, chunk_type: str, **style_attrs) -> None:
        """Set style attributes for a specific chunk type.

        Args:
            chunk_type: The chunk type to style
            **style_attrs: DOT style attributes (e.g., shape="box", fillcolor="red")
        """
        if chunk_type not in self.chunk_type_styles:
            self.chunk_type_styles[chunk_type] = {}
        self.chunk_type_styles[chunk_type].update(style_attrs)

    def set_edge_style(self, relationship_type: str, **style_attrs) -> None:
        """Set style attributes for a specific relationship type.

        Args:
            relationship_type: The relationship type to style
            **style_attrs: DOT style attributes (e.g., style="dashed", color="blue")
        """
        if relationship_type not in self.edge_type_styles:
            self.edge_type_styles[relationship_type] = {}
        self.edge_type_styles[relationship_type].update(style_attrs)
