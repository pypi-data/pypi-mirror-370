"""
Python code generator for creating SQLAlchemy classes from SQL templates.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

from pathlib import Path
from typing import Any
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader

from splurge_sql_generator.sql_parser import SqlParser


class PythonCodeGenerator:
    """Generator for Python classes with SQLAlchemy methods using Jinja2 templates."""

    def __init__(self) -> None:
        self._parser = SqlParser()
        # Set up Jinja2 environment with templates directory
        template_dir = Path(__file__).parent / "templates"
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Preload template once for reuse
        self._template = self._jinja_env.get_template("python_class.j2")

    @property
    def parser(self) -> SqlParser:
        """Public read-only access to the SQL parser instance."""
        return self._parser

    @property
    def jinja_env(self) -> Environment:
        """Public read-only access to the Jinja environment."""
        return self._jinja_env

    def generate_class(
        self,
        sql_file_path: str,
        *,
        output_file_path: str | None = None,
    ) -> str:
        """
        Generate a Python class from a SQL file.

        Args:
            sql_file_path: Path to the SQL template file
            output_file_path: Optional path to save the generated Python file

        Returns:
            Generated Python code as string
        """
        # Parse the SQL file
        class_name, method_queries = self.parser.parse_file(sql_file_path)

        # Generate the Python code using template
        python_code = self._generate_python_code(class_name, method_queries)

        # Save to file if output path provided
        if output_file_path:
            try:
                Path(output_file_path).write_text(python_code, encoding="utf-8")
            except OSError as e:
                raise OSError(
                    f"Error writing Python file {output_file_path}: {e}"
                ) from e

        return python_code

    def _generate_python_code(
        self,
        class_name: str,
        method_queries: dict[str, str],
    ) -> str:
        """
        Generate Python class code from method queries using Jinja2 template.

        Args:
            class_name: Name of the class to generate
            method_queries: Dictionary mapping method names to SQL queries

        Returns:
            Generated Python code
        """
        # Prepare methods data for template
        methods: list[dict[str, Any]] = []
        for method_name, sql_query in method_queries.items():
            method_info = self.parser.get_method_info(sql_query)
            method_data = self._prepare_method_data(method_name, sql_query, method_info)
            methods.append(method_data)

        # Render template (preloaded)
        return self._template.render(class_name=class_name, methods=methods)

    @dataclass
    class _MethodData:
        name: str
        parameters: str
        parameters_list: list[str]
        param_mapping: dict[str, str]
        return_type: str
        type: str
        statement_type: str
        is_fetch: bool
        sql_lines: list[str]

    def _prepare_method_data(
        self,
        method_name: str,
        sql_query: str,
        method_info: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare method data for template rendering.

        Args:
            method_name: Name of the method
            sql_query: SQL query string
            method_info: Analysis information about the method

        Returns:
            Dictionary with method data for template
        """
        # Generate method signature
        parameters = self._generate_method_signature(method_info["parameters"])

        # Prepare SQL lines for template
        sql_lines = sql_query.split("\n")

        # Prepare parameter mapping
        param_mapping: dict[str, str] = {}
        parameters_list: list[str] = []
        if method_info["parameters"]:
            for param in method_info["parameters"]:
                python_param = param  # Preserve original parameter name
                param_mapping[param] = python_param
                if python_param not in parameters_list:
                    parameters_list.append(python_param)

        data = self._MethodData(
            name=method_name,
            parameters=parameters,
            parameters_list=parameters_list,
            param_mapping=param_mapping,
            return_type="List[Row]" if method_info["is_fetch"] else "Result",
            type=method_info["type"],
            statement_type=method_info["statement_type"],
            is_fetch=method_info["is_fetch"],
            sql_lines=sql_lines,
        )

        # Jinja template expects a dict-like object; dataclass is easily serializable
        return {
            "name": data.name,
            "parameters": data.parameters,
            "parameters_list": data.parameters_list,
            "param_mapping": data.param_mapping,
            "return_type": data.return_type,
            "type": data.type,
            "statement_type": data.statement_type,
            "is_fetch": data.is_fetch,
            "sql_lines": data.sql_lines,
        }

    def _generate_method_signature(self, parameters: list[str]) -> str:
        """
        Generate method signature with parameters.

        Args:
            parameters: List of parameter names

        Returns:
            Method signature string
        """
        if not parameters:
            return ""

        # Convert SQL parameters to Python parameters and remove duplicates
        python_params: list[str] = []
        seen_params: set[str] = set()
        for param in parameters:
            # Use original parameter name (preserve underscores)
            python_param = param
            if python_param not in seen_params:
                python_params.append(f"{python_param}: Any")
                seen_params.add(python_param)

        return ", ".join(python_params)

    def generate_multiple_classes(
        self,
        sql_files: list[str],
        *,
        output_dir: str | None = None,
    ) -> dict[str, str]:
        """
        Generate multiple Python classes from SQL files.

        Args:
            sql_files: List of SQL file paths
            output_dir: Optional directory to save generated files

        Returns:
            Dictionary mapping class names to generated code
        """
        generated_classes: dict[str, str] = {}

        for sql_file in sql_files:
            # Parse once per file and render directly to avoid duplicate parsing
            class_name, method_queries = self.parser.parse_file(sql_file)
            python_code = self._generate_python_code(class_name, method_queries)
            generated_classes[class_name] = python_code

            # Save to file if output directory provided
            if output_dir:
                # Ensure output directory exists
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                output_path = Path(output_dir) / f"{class_name}.py"
                try:
                    output_path.write_text(python_code, encoding="utf-8")
                except OSError as e:
                    raise OSError(
                        f"Error writing Python file {output_path}: {e}"
                    ) from e

        return generated_classes
