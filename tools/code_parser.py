"""Deterministic AST and language-specific code parser for repository files."""

import ast
import re
import os
import logging
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path

from models.code_structure import CodeSymbol, FileCodeAnalysis, CodeStructureData

logger = logging.getLogger("agentic_github_analyzer.code_parser")


class PythonASTParser:
    """Deterministic AST parser for Python source files."""

    @staticmethod
    def parse(file_path: str, source_code: str) -> FileCodeAnalysis:
        classes: List[CodeSymbol] = []
        functions: List[CodeSymbol] = []
        imports: List[str] = []
        internal_calls: List[str] = []
        is_entry = False

        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError as e:
            logger.debug(f"[DEBUG] Syntax error parsing Python file {file_path}: {e}")
            return FileCodeAnalysis(
                file_path=file_path,
                language="Python",
                lines_of_code=len(source_code.splitlines())
            )

        for node in ast.walk(tree):
            # Classes
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                classes.append(CodeSymbol(
                    name=node.name,
                    symbol_type="class",
                    line_number=node.lineno,
                    docstring=doc[:100] if doc else None
                ))

            # Functions & Methods
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                params = [arg.arg for arg in node.args.args if arg.arg != "self"]
                functions.append(CodeSymbol(
                    name=node.name,
                    symbol_type="function" if not isinstance(node, ast.AsyncFunctionDef) else "async_function",
                    line_number=node.lineno,
                    docstring=doc[:100] if doc else None,
                    parameters=params[:6]
                ))

            # Imports: import x, import x.y as z
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            # Imports: from x import y
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                dots = "." * node.level
                full_mod = f"{dots}{mod}" if dots else mod
                imports.append(full_mod)

            # Detect main execution block
            elif isinstance(node, ast.If):
                if isinstance(node.test, ast.Compare):
                    left = getattr(node.test.left, "id", None)
                    if left == "__name__":
                        is_entry = True

        basename = Path(file_path).name.lower()
        if basename in ("main.py", "app.py", "cli.py", "run.py", "server.py", "__main__.py"):
            is_entry = True

        return FileCodeAnalysis(
            file_path=file_path,
            language="Python",
            classes=classes,
            functions=functions,
            imports=list(dict.fromkeys(imports)),
            is_entry_point=is_entry,
            lines_of_code=len(source_code.splitlines())
        )


class JavaScriptTypeScriptParser:
    """Deterministic parser for JavaScript and TypeScript source files."""

    IMPORT_ES_REGEX = re.compile(r"""(?:import\s+.*?\s+from\s+['"]([^'"]+)['"]|import\s+['"]([^'"]+)['"])""")
    REQUIRE_REGEX = re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""")
    CLASS_REGEX = re.compile(r"""class\s+([A-Za-z0-9_$]+)""")
    FUNCTION_REGEX = re.compile(r"""(?:function\s+([A-Za-z0-9_$]+)|const\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)""")
    EXPORT_REGEX = re.compile(r"""export\s+(?:default\s+)?(?:class|function|const|let|var)\s+([A-Za-z0-9_$]+)""")

    @classmethod
    def parse(cls, file_path: str, source_code: str) -> FileCodeAnalysis:
        lines = source_code.splitlines()
        imports = []
        classes = []
        functions = []
        exports = []

        # Find imports
        for match in cls.IMPORT_ES_REGEX.finditer(source_code):
            mod = match.group(1) or match.group(2)
            if mod:
                imports.append(mod)
        for match in cls.REQUIRE_REGEX.finditer(source_code):
            imports.append(match.group(1))

        # Find classes
        for match in cls.CLASS_REGEX.finditer(source_code):
            classes.append(CodeSymbol(
                name=match.group(1),
                symbol_type="class",
                line_number=1
            ))

        # Find functions & React components
        for match in cls.FUNCTION_REGEX.finditer(source_code):
            fname = match.group(1) or match.group(2)
            if fname:
                # Check if React component (Capitalized)
                is_comp = fname[0].isupper()
                functions.append(CodeSymbol(
                    name=fname,
                    symbol_type="component" if is_comp else "function",
                    line_number=1
                ))

        # Find exports
        for match in cls.EXPORT_REGEX.finditer(source_code):
            exports.append(match.group(1))

        basename = Path(file_path).name.lower()
        is_entry = basename in ("index.js", "index.ts", "server.js", "server.ts", "app.js", "app.ts", "main.ts", "main.js")

        lang = "TypeScript" if file_path.endswith((".ts", ".tsx")) else "JavaScript"

        return FileCodeAnalysis(
            file_path=file_path,
            language=lang,
            classes=classes,
            functions=functions,
            imports=list(dict.fromkeys(imports)),
            exports=list(dict.fromkeys(exports)),
            is_entry_point=is_entry,
            lines_of_code=len(lines)
        )


class GenericCodeParser:
    """Fallback parser for Go, Rust, Java, and other languages."""

    GO_IMPORT_REGEX = re.compile(r"""import\s+(?:\(\s*([^)]+)\s*\)|"([^"]+)")""")
    RUST_USE_REGEX = re.compile(r"""use\s+([^;]+);""")

    @classmethod
    def parse(cls, file_path: str, source_code: str) -> FileCodeAnalysis:
        imports = []
        lang = "Unknown"

        if file_path.endswith(".go"):
            lang = "Go"
            for match in cls.GO_IMPORT_REGEX.finditer(source_code):
                block = match.group(1)
                single = match.group(2)
                if block:
                    imports.extend([line.strip().strip('"') for line in block.splitlines() if line.strip()])
                elif single:
                    imports.append(single)
        elif file_path.endswith(".rs"):
            lang = "Rust"
            for match in cls.RUST_USE_REGEX.finditer(source_code):
                imports.append(match.group(1).strip())

        basename = Path(file_path).name.lower()
        is_entry = basename in ("main.go", "main.rs")

        return FileCodeAnalysis(
            file_path=file_path,
            language=lang,
            imports=list(dict.fromkeys(imports)),
            is_entry_point=is_entry,
            lines_of_code=len(source_code.splitlines())
        )


class CodeParser:
    """Unified entry point for code parsing and structure aggregation."""

    @staticmethod
    def parse_file(file_path: str, content: str) -> FileCodeAnalysis:
        lower = file_path.lower()
        if lower.endswith(".py"):
            return PythonASTParser.parse(file_path, content)
        elif lower.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")):
            return JavaScriptTypeScriptParser.parse(file_path, content)
        else:
            return GenericCodeParser.parse(file_path, content)

    @classmethod
    def analyze_repository_code(cls, file_map: Dict[str, str]) -> CodeStructureData:
        """
        Analyze all loaded files and categorize internal vs external module imports.
        file_map: dict of relative_path -> source_code
        """
        analyses: List[FileCodeAnalysis] = []
        source_dirs = set()
        entry_points = []
        classes_total = 0
        functions_total = 0
        imports_map: Dict[str, List[str]] = {}

        # Collect all project module base identifiers
        known_modules = set()
        for path in file_map.keys():
            clean = path.replace("\\", "/")
            parts = clean.split("/")
            if len(parts) > 1:
                source_dirs.add(parts[0])
            stem = Path(path).stem
            known_modules.add(stem)
            known_modules.add(clean)

        for file_path, code in file_map.items():
            analysis = cls.parse_file(file_path, code)
            classes_total += len(analysis.classes)
            functions_total += len(analysis.functions)

            if analysis.is_entry_point:
                entry_points.append(file_path)

            # Classify internal vs external imports
            internal_imps = []
            external_imps = []
            for imp in analysis.imports:
                clean_imp = imp.split(".")[0].strip(".")
                if clean_imp in known_modules or imp.startswith(".") or any(p in imp for p in source_dirs):
                    internal_imps.append(imp)
                else:
                    external_imps.append(imp)

            analysis.internal_imports = internal_imps
            analysis.external_imports = external_imps
            imports_map[file_path] = internal_imps
            analyses.append(analysis)

        # Build hierarchical summary
        summary_lines = [
            f"Analyzed {len(analyses)} core source files across {len(source_dirs)} directories.",
            f"Detected {classes_total} classes and {functions_total} functions/components.",
            f"Identified {len(entry_points)} primary entry points: {', '.join(entry_points) if entry_points else 'None explicit'}"
        ]

        return CodeStructureData(
            source_directories=sorted(list(source_dirs)),
            total_modules_analyzed=len(analyses),
            classes_count=classes_total,
            functions_count=functions_total,
            modules=[a.file_path for a in analyses],
            imports_map=imports_map,
            detected_entry_points=sorted(entry_points),
            file_analyses=analyses,
            hierarchical_summary="\n".join(summary_lines)
        )
