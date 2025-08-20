from ..core import (
    ast,
    sys,
    os,
    Path,
    Union,
    Dict,
    Set,
    List,
    t,
    IN_JUPYTER,
    display,
    Markdown,
    show_gui_popup,
)


class PythonFileChecker:
    def __init__(self):
        self.errors: List[Dict[str, str]] = []
        self.imported_names: Set[str] = set()
        self.defined_names: Set[str] = set()
        self.import_lines: Dict[str, int] = {}

    def check_file(self, file_path: Union[str, Path]) -> bool:
        """Check a Python file for all possible errors without stopping"""
        self.errors.clear()
        self.imported_names.clear()
        self.defined_names.clear()
        self.import_lines.clear()

        if not os.path.exists(file_path):
            self._add_error(
                0, t("file_not_found").format(file_path=file_path), "FileNotFound"
            )
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except UnicodeDecodeError:
            self._add_error(0, t("encoding_error"), "EncodingError")
            return False

        tree = None
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            self._add_error(
                e.lineno, t("syntax_error").format(msg=e.msg), "SyntaxError"
            )
            try:
                tree = ast.parse(source_code, mode="exec")
            except:
                pass

        if tree is not None:
            try:
                for node in ast.walk(tree):
                    for child in ast.iter_child_nodes(node):
                        setattr(child, "parent", node)

                self._collect_imports_and_definitions(tree)
                self._check_undefined_names(tree, source_code.splitlines())
                self._check_other_issues(tree, source_code.splitlines())

            except Exception as e:
                self._add_error(
                    0, t("analysis_error").format(msg=str(e)), "AnalysisError"
                )

        return len(self.errors) == 0

    def _add_error(self, line: int, message: str, error_type: str, context: str = None):
        """Helper to add errors with translation support"""
        error = {
            "line": line,
            "message": message,
            "type": error_type,
            "context": context,
        }
        self.errors.append(error)

    def _collect_imports_and_definitions(self, tree: ast.AST) -> None:
        """Collect all imported and defined names in the AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imported_names.add(alias.name)
                    self.import_lines[alias.name] = node.lineno
                    if alias.asname:
                        self.imported_names.add(alias.asname)
                        self.import_lines[alias.asname] = node.lineno

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    self.imported_names.add(full_name)
                    self.import_lines[full_name] = node.lineno
                    if alias.asname:
                        self.imported_names.add(alias.asname)
                        self.import_lines[alias.asname] = node.lineno
                    else:
                        self.imported_names.add(alias.name)
                        self.import_lines[alias.name] = node.lineno

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.defined_names.add(node.name)

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.defined_names.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                self.defined_names.add(elt.id)

    def _check_undefined_names(self, tree: ast.AST, source_lines: List[str]) -> None:
        """Check for undefined names in the AST."""
        defined = self.defined_names.union(self.imported_names)
        builtins = set(dir(__builtins__)).union({
            'self', 'cls', '_', 'print', 'open', 
            'ImportError', 'globals', 'Exception'
        })

        for node in ast.walk(tree):
            try:
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    name = node.id
                    if (name not in defined and 
                        name not in builtins and 
                        not name.startswith('_')):
                        
                        is_attribute = False
                        if hasattr(node, "parent"):
                            parent = node.parent
                            if (isinstance(parent, ast.Attribute) and 
                                parent.value == node):
                                is_attribute = True

                        if not is_attribute:
                            line_content = (
                                source_lines[node.lineno - 1].strip()
                                if node.lineno <= len(source_lines)
                                else ""
                            )
                            self._add_error(
                                node.lineno,
                                t("undefined_name").format(name=name),
                                "NameError",
                                line_content,
                            )
            except Exception:
                continue

    def _check_other_issues(self, tree: ast.AST, source_lines: List[str]) -> None:
        """Check for other potential issues in the code."""
        imported_names = set(self.import_lines.keys())
        all_used_names = set()
        assigned_but_unused = {}

        bad_comparisons = {
            "Eq": {  # ==
                "True": t("redundant_true"),
                "False": t("redundant_false"),
                "None": t("none_comparison"),
            },
            "NotEq": {  # !=
                "True": t("not_true_recommendation"),
                "False": t("not_false_recommendation"),
            },
        }

        for node in ast.walk(tree):
            try:
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    all_used_names.add(node.id)
                    if node.id in imported_names:
                        imported_names.remove(node.id)

                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assigned_but_unused[target.id] = node.lineno
                        elif isinstance(target, ast.Tuple):
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    assigned_but_unused[elt.id] = node.lineno

                elif isinstance(node, ast.Compare):
                    op_type = type(node.ops[0]).__name__ if node.ops else None

                    if op_type in bad_comparisons:
                        for comparator in node.comparators:
                            if isinstance(comparator, ast.Constant):
                                const_value = str(comparator.value)
                                if const_value in bad_comparisons[op_type]:
                                    line_content = source_lines[node.lineno - 1].strip()
                                    self._add_error(
                                        node.lineno,
                                        bad_comparisons[op_type][const_value],
                                        "StyleWarning",
                                        line_content,
                                    )

                elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if not node.body:
                        line_content = source_lines[node.lineno - 1].strip()
                        self._add_error(
                            node.lineno,
                            t("empty_block").format(
                                type=(
                                    t("function")
                                    if isinstance(node, ast.FunctionDef)
                                    else t("class")
                                )
                            ),
                            "IndentationWarning",
                            line_content,
                        )
                    elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        line_content = source_lines[node.lineno - 1].strip()
                        self._add_error(
                            node.lineno,
                            t("empty_block_with_pass").format(
                                type=(
                                    t("function")
                                    if isinstance(node, ast.FunctionDef)
                                    else t("class")
                                )
                            ),
                            "IndentationWarning",
                            line_content,
                        )

            except Exception:
                continue

        # Check for unused imports
        for name in imported_names:
            line = self.import_lines.get(name, 0)
            line_content = source_lines[line - 1].strip() if line > 0 and line <= len(source_lines) else ""
            self._add_error(
                line,
                f"Unused import '{name}'",
                "StyleWarning",
                line_content,
            )

        # Check for unused variables
        for name, line in assigned_but_unused.items():
            if name not in all_used_names:
                line_content = source_lines[line - 1].strip() if line <= len(source_lines) else ""
                self._add_error(
                    line,
                    f"Unused variable '{name}'",
                    "StyleWarning",
                    line_content,
                )

    def get_errors(self) -> List[Dict[str, str]]:
        """Return the list of errors found."""
        return sorted(self.errors, key=lambda e: e["line"])


def check_syntax(file_path: Union[str, Path]) -> None:
    """Check a Python file and show all errors found."""
    checker = PythonFileChecker()
    checker.check_file(file_path)

    errors = checker.get_errors()

    if not errors:
        if IN_JUPYTER:
            display(
                Markdown(f"**{t('syntax_check_title')}**\n\n{t('no_errors_found')}")
            )
        else:
            show_gui_popup(t("syntax_check_title"), t("no_errors_found"))
        return

    error_categories = {
        "Syntax Errors": ["SyntaxError"],
        "File Issues": ["FileNotFound", "EncodingError"],
        "Name Issues": ["NameError"],
        "Style Warnings": ["StyleWarning", "IndentationWarning"],
        "Other Issues": ["AnalysisError"],
    }

    unique_types = sorted(set(e["type"] for e in errors))
    error_text = f"Found {len(errors)} error(s) in {file_path}:\n"
    error_text += f"Error types found: {len(unique_types)}\n\n"

    # Organize errors by category
    categorized_errors = {}
    for category, error_types in error_categories.items():
        category_errors = [e for e in errors if e["type"] in error_types]
        if category_errors:
            categorized_errors[category] = category_errors

    # Show errors by category
    for category, category_errors in categorized_errors.items():
        error_text += f"=== {category} ===\n"
        for error in category_errors:
            error_text += f"Line {error['line']}: {error['message']}\n"
            if error.get("context"):
                error_text += f"Context: {error['context']}\n"
            error_text += f"Type: {error['type']}\n\n"

    if IN_JUPYTER:
        display(Markdown(f"**Python Code Analysis**\n\n```\n{error_text}\n```"))
    else:
        show_gui_popup(t("multiple_errors_title"), error_text)


class This:
    """Clase para obtener información del archivo actual"""

    @staticmethod
    def get_caller_path(levels_up: int = 2) -> str:
        """
        Obtiene la ruta del archivo que llamó a esta función
        :param levels_up: Número de niveles en el stack de llamadas a subir (default 2)
        """
        import inspect

        frame = inspect.currentframe()
        try:
            for _ in range(levels_up):
                frame = frame.f_back
                if frame is None:
                    return None

            return frame.f_globals.get("__file__")
        finally:
            del frame

    @staticmethod
    def get_script_path() -> str:
        """Obtiene la ruta del script principal en ejecución"""
        import sys

        return sys.argv[0] if len(sys.argv) > 0 else None


def run(file_path=None):
    def show_error_and_exit():
        show_gui_popup(t("error"), t("provide_file_path"))
        return

    if hasattr(file_path, "__file__"):
        file_path = file_path.__file__

    if file_path is None:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
        else:
            file_path = This.get_caller_path()

            if file_path is None:
                file_path = This.get_script_path()

    if not file_path or not os.path.exists(file_path):
        show_error_and_exit()
        return

    check_syntax(file_path)