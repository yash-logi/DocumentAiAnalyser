"""Unit tests for dependency analyzer and Mermaid flowchart generation."""

from tools.code_parser import CodeParser
from tools.dependency_analyzer import DependencyAnalyzer


def test_dependency_analyzer_and_mermaid():
    file_map = {
        "main.py": "import api\nimport config\ndef main(): pass\nif __name__ == '__main__': main()",
        "config.py": "DATABASE = 'sqlite://'",
        "api.py": "import config\nimport database\ndef get_app(): pass",
        "database.py": "import config\nclass DB: pass"
    }

    code_data = CodeParser.analyze_repository_code(file_map)
    graph = DependencyAnalyzer.analyze(code_data)

    assert len(graph.nodes) == 4
    assert len(graph.edges) >= 3
    assert "flowchart TD" in graph.mermaid_diagram
    assert "main_py" in graph.mermaid_diagram
    assert "api_py" in graph.mermaid_diagram
    assert "circular_dependencies" in graph.model_dump()
    assert len(graph.circular_dependencies) == 0
