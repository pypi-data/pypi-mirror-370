"""
DBGear project management for the editor.
"""

from pathlib import Path
from typing import Optional

from dbgear.models.project import Project
from dbgear.models.schema import SchemaManager


class DBGearProject:
    """DBGear project management class for the web editor."""

    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize DBGear project.

        Args:
            project_path: Path to the project directory containing project.yaml
        """
        self.project_path = project_path
        self.project: Optional[Project] = None
        self.schema_manager: Optional[SchemaManager] = None

        if project_path:
            self.load_project(project_path)

    def load_project(self, project_path: str) -> bool:
        """
        Load DBGear project from the specified path.

        Args:
            project_path: Path to the project directory

        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            self.project_path = project_path

            # Load project configuration using DBGear's Project.load
            self.project = Project.load(project_path)

            # Load schema from the same directory
            project_dir = Path(project_path)
            schema_file = project_dir / "schema.yaml"
            if schema_file.exists():
                self.schema_manager = SchemaManager.load(str(schema_file))
            else:
                # Create empty schema manager
                self.schema_manager = SchemaManager()

            return True

        except Exception as e:
            print(f"Error loading project: {e}")
            return False

    def get_schemas(self) -> dict:
        """Get all schemas from the current project."""
        if not self.schema_manager:
            return {}

        return {name: schema for name, schema in self.schema_manager.schemas.items()}

    def get_tables(self, schema_name: str = None) -> dict:
        """
        Get tables from the specified schema or all schemas.

        Args:
            schema_name: Specific schema name, or None for all schemas

        Returns:
            dict: Dictionary of tables organized by schema
        """
        if not self.schema_manager:
            return {}

        if schema_name:
            schema = self.schema_manager.schemas.get(schema_name)
            if schema:
                return {schema_name: schema.tables.tables}
            return {}

        # Return all tables organized by schema
        result = {}
        for name, schema in self.schema_manager.schemas.items():
            result[name] = schema.tables.tables

        return result

    def get_views(self, schema_name: str = None) -> dict:
        """
        Get views from the specified schema or all schemas.

        Args:
            schema_name: Specific schema name, or None for all schemas

        Returns:
            dict: Dictionary of views organized by schema
        """
        if not self.schema_manager:
            return {}

        if schema_name:
            schema = self.schema_manager.schemas.get(schema_name)
            if schema:
                return {schema_name: schema.views.views}
            return {}

        # Return all views organized by schema
        result = {}
        for name, schema in self.schema_manager.schemas.items():
            result[name] = schema.views.views

        return result

    def get_procedures(self, schema_name: str = None) -> dict:
        """
        Get procedures from the specified schema or all schemas.

        Args:
            schema_name: Specific schema name, or None for all schemas

        Returns:
            dict: Dictionary of procedures organized by schema
        """
        if not self.schema_manager:
            return {}

        if schema_name:
            schema = self.schema_manager.schemas.get(schema_name)
            if schema:
                return {schema_name: schema.procedures.procedures}
            return {}

        # Return all procedures organized by schema
        result = {}
        for name, schema in self.schema_manager.schemas.items():
            result[name] = schema.procedures.procedures

        return result

    def get_triggers(self, schema_name: str = None) -> dict:
        """
        Get triggers from the specified schema or all schemas.

        Args:
            schema_name: Specific schema name, or None for all schemas

        Returns:
            dict: Dictionary of triggers organized by schema
        """
        if not self.schema_manager:
            return {}

        if schema_name:
            schema = self.schema_manager.schemas.get(schema_name)
            if schema:
                return {schema_name: schema.triggers.triggers}
            return {}

        # Return all triggers organized by schema
        result = {}
        for name, schema in self.schema_manager.schemas.items():
            result[name] = schema.triggers.triggers

        return result

    def is_loaded(self) -> bool:
        """Check if a project is currently loaded."""
        return self.project is not None and self.schema_manager is not None

    def get_project_info(self) -> dict:
        """Get basic project information."""
        if not self.project:
            return {}

        return {
            "name": getattr(self.project, 'project_name', 'Unknown'),
            "path": self.project_path,
            "schemas_count": len(self.schema_manager.schemas) if self.schema_manager else 0,
            "tables_count": sum(len(schema.tables) for schema in self.schema_manager.schemas.values()) if self.schema_manager else 0,
            "views_count": sum(len(schema.views) for schema in self.schema_manager.schemas.values()) if self.schema_manager else 0,
            "procedures_count": sum(len(schema.procedures) for schema in self.schema_manager.schemas.values()) if self.schema_manager else 0,
            "triggers_count": sum(len(schema.triggers) for schema in self.schema_manager.schemas.values()) if self.schema_manager else 0,
        }


# Global project instance
_current_project: Optional[DBGearProject] = None


def get_current_project() -> Optional[DBGearProject]:
    """Get the current loaded project."""
    return _current_project


def set_current_project(project: DBGearProject):
    """Set the current project."""
    global _current_project
    _current_project = project


def load_project(project_path: str) -> bool:
    """
    Load a project and set it as current.

    Args:
        project_path: Path to the project directory

    Returns:
        bool: True if successfully loaded
    """
    project = DBGearProject()
    if project.load_project(project_path):
        set_current_project(project)
        return True
    return False
