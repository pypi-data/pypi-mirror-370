"""
Procedure-related UI components for DBGear Editor.
"""

from fasthtml.common import *
from monsterui.all import *

from .common import info_section, sql_section, badge, data_table


def procedure_grid(procedures: dict, schema_name: str):
    """Create a grid of procedure cards."""
    if not procedures:
        return Div()

    procedure_cards = []
    for procedure_name, procedure in procedures.items():
        # Determine if it's a function or procedure
        proc_type = "Function" if getattr(procedure, 'is_function', False) else "Procedure"
        param_count = len(getattr(procedure, 'parameters', []))

        procedure_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("zap", height=20, cls="text-orange-500"),
                        H3(procedure_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P(f"{proc_type} ({param_count} parameters)", cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/procedures/{procedure_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *procedure_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


def procedure_info_section(procedure, schema_name: str, procedure_name: str):
    """Create procedure information section."""
    info_items = [
        ("Name", procedure_name),
        ("Display Name", procedure.display_name),
        ("Type", "Function" if procedure.is_function else "Stored Procedure"),
        ("Schema", schema_name),
        ("Language", procedure.language),
        ("Security Type", procedure.security_type),
    ]

    if procedure.is_function and procedure.return_type:
        info_items.append(("Return Type", procedure.return_type))

    info_items.extend([
        ("Deterministic", "Yes" if procedure.deterministic else "No"),
        ("Reads SQL Data", "Yes" if procedure.reads_sql_data else "No"),
        ("Modifies SQL Data", "Yes" if procedure.modifies_sql_data else "No"),
    ])

    return info_section(info_items)


def procedure_parameters_section(procedure):
    """Create procedure parameters section."""
    parameters = procedure.parameters

    if not parameters:
        return P("No parameters defined", cls="text-gray-500")

    headers = ["Parameter Name", "Type", "Data Type", "Default Value"]
    rows = [parameter_row(param) for param in parameters]

    return data_table(headers, rows)


def parameter_row(parameter):
    """Create a table row for a parameter."""
    param_type_styles = {
        "IN": "blue",
        "OUT": "green",
        "INOUT": "purple",
    }

    param_type_badge = badge(parameter.parameter_type, param_type_styles.get(parameter.parameter_type, "gray"))

    return Tr(
        Td(
            Code(parameter.parameter_name, cls="text-sm font-mono text-blue-600"),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(
            param_type_badge,
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(
            Code(parameter.data_type, cls="text-sm font-mono text-gray-900"),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(
            Code(parameter.default_value or "", cls="text-sm font-mono text-gray-500") if parameter.default_value else "",
            cls="px-6 py-4 whitespace-nowrap"
        ),
        cls="hover:bg-gray-50"
    )


def procedure_sql_section(procedure):
    """Create procedure SQL section with syntax highlighting."""
    return sql_section(procedure.body, "SQL Body")
