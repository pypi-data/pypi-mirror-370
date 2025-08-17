"""
Main entry point for DBGear Editor.
A FastHTML-based web interface for viewing and managing DBGear projects.
"""

import argparse
from uuid import uuid4

import uvicorn
from fasthtml.common import *
from monsterui.all import *

from .project import load_project

# Import route registration functions
from .routes.dashboard import register_dashboard_routes
from .routes.tables import register_table_routes
from .routes.views import register_view_routes
from .routes.procedures import register_procedure_routes
from .routes.triggers import register_trigger_routes
from .routes.dependencies import register_dependency_routes

# Initialize FastHTML app
app, rt = fast_app(hdrs=[*Theme.blue.headers(highlightjs=True)], secret_key=str(uuid4()))

# Register all routes
register_dashboard_routes(rt)
register_table_routes(rt)
register_view_routes(rt)
register_procedure_routes(rt)
register_trigger_routes(rt)
register_dependency_routes(rt)


def main():
    """Main entry point for the dbgear-editor command."""
    parser = argparse.ArgumentParser(description='DBGear FastHTML Editor')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--project', default='database', help='Project directory to load (default: database)')

    args = parser.parse_args()

    # Load project (default to 'database' if not specified)
    success = load_project(args.project)
    if success:
        print(f"✅ Loaded project from: {args.project}")
    else:
        print(f"❌ Failed to load project from: {args.project}")
        print("Please check that the directory contains a valid project.yaml file.")
        exit(1)

    print(f"🚀 Starting DBGear Editor on http://{args.host}:{args.port}")

    uvicorn.run(
        "dbgear_editor.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
