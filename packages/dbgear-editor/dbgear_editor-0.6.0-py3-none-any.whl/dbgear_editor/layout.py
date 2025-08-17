"""
Main layout component for DBGear Editor.
Implements a 3-pane layout with header, sidebar, and content areas.
"""

from fasthtml.common import *
from monsterui.all import *

from .components.header import header_component
from .components.sidebar import sidebar_component


def layout(content, title="DBGear Editor", current_path="", sidebar_content=None):
    """
    Create the main 3-pane layout for the application.

    Args:
        content: Main content to display
        title: Page title (default: "DBGear Editor")
        current_path: Current URL path for navigation highlighting
        sidebar_content: Optional right sidebar content

    Returns:
        FastHTML document with complete layout
    """
    return (
        Title(title),
        # Add Cytoscape.js CDN and layout extensions
        # Script(src="https://unpkg.com/cytoscape@3.30.3/dist/cytoscape.min.js"),
        # Script(src="https://unpkg.com/dagre@0.8.5/dist/dagre.min.js"),
        # Script(src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"),
        # Script(src="https://unpkg.com/cytoscape-klay@3.1.4/cytoscape-klay.js"),
        # Add JavaScript for dropdown and collapsible functionality
        Script("""
            document.addEventListener('DOMContentLoaded', function() {
                // Dropdown toggle functionality
                const dropdownToggles = document.querySelectorAll('[data-dropdown-toggle]');
                dropdownToggles.forEach(toggle => {
                    toggle.addEventListener('click', function(e) {
                        e.preventDefault();
                        const dropdownId = this.getAttribute('data-dropdown-toggle');
                        const dropdown = document.getElementById(dropdownId);
                        if (dropdown) {
                            dropdown.classList.toggle('hidden');
                        }
                    });
                });

                // Collapsible sections for sidebar
                const sectionToggles = document.querySelectorAll('[data-toggle]');
                sectionToggles.forEach(toggle => {
                    toggle.addEventListener('click', function(e) {
                        e.preventDefault();
                        const sectionId = this.getAttribute('data-toggle');
                        const section = document.getElementById(sectionId);
                        const chevron = this.querySelector('[data-chevron]');

                        if (section && chevron) {
                            section.classList.toggle('hidden');
                            if (section.classList.contains('hidden')) {
                                chevron.style.transform = 'rotate(0deg)';
                            } else {
                                chevron.style.transform = 'rotate(90deg)';
                            }
                        }
                    });
                });

                // Close dropdowns when clicking outside
                document.addEventListener('click', function(e) {
                    if (!e.target.closest('[data-dropdown-toggle]')) {
                        const dropdowns = document.querySelectorAll('[id$="-dropdown"]');
                        dropdowns.forEach(dropdown => {
                            dropdown.classList.add('hidden');
                        });
                    }
                });
            });
        """),

        # Main layout container with flex column
        Div(
            # Header
            header_component(),

            # Main content area with sidebar and content
            Div(
                # Left Sidebar
                sidebar_component(current_path),

                # Main content area
                Main(
                    Div(
                        content,
                        cls="p-6"
                    ),
                    cls="flex-1 bg-white overflow-y-auto"
                ),

                # Right Sidebar (conditional)
                Div(
                    sidebar_content,
                    cls="w-80 bg-gray-50 border-l border-gray-200 overflow-y-auto"
                ) if sidebar_content else None,

                cls="flex flex-1 min-h-0"
            ),

            cls="flex flex-col h-screen bg-gray-100"
        )
    )


def content_header(title: str, subtitle: str = None, actions=None):
    """
    Create a content header with title, optional subtitle, and action buttons.

    Args:
        title: Main title
        subtitle: Optional subtitle
        actions: Optional action buttons or components

    Returns:
        FastHTML component for content header
    """
    header_content = [
        Div(
            H1(title, cls="text-2xl font-bold text-gray-900"),
            P(subtitle, cls="mt-1 text-sm text-gray-600") if subtitle else None,
            cls="flex-1"
        )
    ]

    if actions:
        header_content.append(
            Div(actions, cls="flex space-x-2")
        )

    return Div(
        *header_content,
        cls="flex items-center justify-between pb-4 border-b border-gray-200 mb-6"
    )


def empty_state(icon: str, title: str, description: str, action=None):
    """
    Create an empty state component.

    Args:
        icon: UkIcon icon name
        title: Empty state title
        description: Empty state description
        action: Optional action button or link

    Returns:
        FastHTML component for empty state
    """
    components = [
        UkIcon(icon, height=48, cls="mx-auto text-gray-400"),
        H3(title, cls="mt-4 text-lg font-medium text-gray-900"),
        P(description, cls="mt-2 text-sm text-gray-500 max-w-sm")
    ]

    if action:
        components.append(
            Div(action, cls="mt-4")
        )

    return Div(
        *components,
        cls="text-center py-12"
    )


def breadcrumb(*items):
    """
    Create a breadcrumb navigation component.

    Args:
        *items: Breadcrumb items (strings or tuples of (text, href))

    Returns:
        FastHTML component for breadcrumb
    """
    breadcrumb_items = []

    for i, item in enumerate(items):
        if isinstance(item, tuple):
            text, href = item
            breadcrumb_items.append(
                A(text, href=href, cls="text-blue-600 hover:text-blue-700")
            )
        else:
            breadcrumb_items.append(
                Span(item, cls="text-gray-500")
            )

        # Add separator except for last item
        if i < len(items) - 1:
            breadcrumb_items.append(
                UkIcon("chevron-right", height=16, cls="mx-2 text-gray-400")
            )

    return Nav(
        Ol(
            *[Li(item, cls="inline-flex items-center") for item in breadcrumb_items],
            cls="inline-flex items-center space-x-1"
        ),
        cls="mb-4"
    )
