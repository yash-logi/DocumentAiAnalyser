"""Dependency analyzer and Mermaid flowchart diagram generator."""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path

from models.code_structure import CodeStructureData, FileCodeAnalysis
from models.analysis import DependencyNode, DependencyEdge, DependencyGraphData
from models.repository import RepositoryOverview

logger = logging.getLogger("agentic_github_analyzer.dependency_analyzer")


def sanitize_node_id(path: str) -> str:
    """Convert file path or module name to valid Mermaid alphanumeric ID."""
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", path).strip("_")
    if not clean or clean[0].isdigit():
        clean = "node_" + clean
    return clean


class DependencyAnalyzer:
    """Constructs internal dependency graphs and Mermaid visualizations."""

    @classmethod
    def analyze(cls, code_data: CodeStructureData, overview: Optional[RepositoryOverview] = None) -> DependencyGraphData:
        nodes: List[DependencyNode] = []
        edges: List[DependencyEdge] = []
        file_analyses = code_data.file_analyses

        module_to_id: Dict[str, str] = {}
        id_to_label: Dict[str, str] = {}

        for analysis in file_analyses:
            node_id = sanitize_node_id(analysis.file_path)
            label = Path(analysis.file_path).name
            module_to_id[analysis.file_path] = node_id
            module_to_id[Path(analysis.file_path).stem] = node_id
            id_to_label[node_id] = label

            node_type = "module"
            if analysis.is_entry_point:
                node_type = "entry_point"
            elif any(d in analysis.file_path.lower() for d in ("service", "api", "client", "controller")):
                node_type = "service"
            elif any(d in analysis.file_path.lower() for d in ("model", "schema", "entity")):
                node_type = "model"
            elif any(d in analysis.file_path.lower() for d in ("tool", "util", "helper")):
                node_type = "tool"

            nodes.append(DependencyNode(
                id=node_id,
                label=analysis.file_path,
                node_type=node_type,
                module_path=analysis.file_path
            ))

        seen_edges = set()
        adjacency: Dict[str, Set[str]] = {n.id: set() for n in nodes}

        for analysis in file_analyses:
            src_id = module_to_id.get(analysis.file_path)
            if not src_id:
                continue

            for imp in analysis.internal_imports:
                matched_target_id = None
                clean_imp = imp.replace("/", ".").strip(".")
                imp_parts = clean_imp.split(".")

                for part in reversed(imp_parts):
                    if part in module_to_id:
                        matched_target_id = module_to_id[part]
                        break

                if matched_target_id and matched_target_id != src_id:
                    edge_key = (src_id, matched_target_id)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(DependencyEdge(
                            source=src_id,
                            target=matched_target_id,
                            relationship="imports"
                        ))
                        adjacency[src_id].add(matched_target_id)

        cycles = cls._find_cycles(adjacency)

        in_degree = {n.id: 0 for n in nodes}
        out_degree = {n.id: 0 for n in nodes}
        for src, tgt in seen_edges:
            out_degree[src] += 1
            in_degree[tgt] += 1

        entry_point_ids = [n.id for n in nodes if n.node_type == "entry_point" or (in_degree[n.id] == 0 and out_degree[n.id] > 0)]
        leaf_ids = [n.id for n in nodes if out_degree[n.id] == 0 and in_degree[n.id] > 0]
        isolated_ids = [n.id for n in nodes if in_degree[n.id] == 0 and out_degree[n.id] == 0]

        mermaid_chart = cls._generate_mermaid(nodes, edges, entry_point_ids)

        pattern = "Layered Architecture"
        if len(edges) == 0:
            pattern = "Script or Flat Collection"
        elif any(n.node_type == "service" for n in nodes) and any(n.node_type == "model" for n in nodes):
            pattern = "Service-Oriented / MVC Architecture"

        return DependencyGraphData(
            nodes=nodes,
            edges=edges,
            mermaid_diagram=mermaid_chart,
            entry_point_nodes=[id_to_label.get(i, i) for i in entry_point_ids],
            leaf_nodes=[id_to_label.get(i, i) for i in leaf_ids],
            isolated_nodes=[id_to_label.get(i, i) for i in isolated_ids],
            circular_dependencies=cycles,
            architectural_pattern=pattern
        )

    @staticmethod
    def _find_cycles(adj: Dict[str, Set[str]]) -> List[str]:
        visited = {}
        cycles = []

        def dfs(node, path):
            visited[node] = 1
            for neighbor in adj.get(node, []):
                if neighbor in path:
                    cycle_slice = path[path.index(neighbor):] + [neighbor]
                    cycle_str = " -> ".join(cycle_slice)
                    if cycle_str not in cycles:
                        cycles.append(cycle_str)
                elif visited.get(neighbor) != 2:
                    dfs(neighbor, path + [neighbor])
            visited[node] = 2

        for n in adj:
            if visited.get(n) != 2:
                dfs(n, [n])
        return cycles

    @staticmethod
    def _generate_mermaid(nodes: List[DependencyNode], edges: List[DependencyEdge], entry_point_ids: List[str]) -> str:
        lines = ["flowchart TD"]
        lines.append("    classDef entry fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff;")
        lines.append("    classDef service fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff;")
        lines.append("    classDef model fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff;")
        lines.append("    classDef tool fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff;")
        lines.append("    classDef default fill:#ECEFF1,stroke:#607D8B,stroke-width:1px,color:#263238;")

        if not edges:
            if not nodes:
                lines.append("    Empty[No source code modules detected]")
            else:
                for n in nodes[:15]:
                    lines.append(f'    {n.id}["{Path(n.label).name}"]:::default')
            return "\n".join(lines)

        rendered_nodes = set()
        for edge in edges:
            for nid in (edge.source, edge.target):
                if nid not in rendered_nodes:
                    n = next((x for x in nodes if x.id == nid), None)
                    label = Path(n.label).name if n else nid
                    style = "entry" if nid in entry_point_ids else (n.node_type if n and n.node_type in ("service", "model", "tool") else "default")
                    lines.append(f'    {nid}["{label}"]:::{style}')
                    rendered_nodes.add(nid)

        for edge in edges:
            lines.append(f"    {edge.source} --> {edge.target}")

        return "\n".join(lines)
