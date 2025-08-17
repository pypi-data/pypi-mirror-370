"""
Trigger-related UI components for DBGear Editor.
"""

from fasthtml.common import *
from monsterui.all import *

from .common import info_section, sql_section, badge


def trigger_grid(triggers: dict, schema_name: str):
    """Create a grid of trigger cards."""
    if not triggers:
        return Div()

    trigger_cards = []
    for trigger_name, trigger in triggers.items():
        # Get trigger details
        timing = getattr(trigger, 'timing', '')
        event = getattr(trigger, 'event', '')
        table_name = getattr(trigger, 'table_name', '')

        trigger_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("flash", height=20, cls="text-yellow-500"),
                        H3(trigger_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P(f"{timing} {event} on {table_name}", cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/triggers/{trigger_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *trigger_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


def trigger_info_section(trigger, schema_name: str, trigger_name: str):
    """Create trigger information section."""
    timing_styles = {
        "BEFORE": "yellow",
        "AFTER": "blue",
        "INSTEAD OF": "purple",
    }

    event_styles = {
        "INSERT": "green",
        "UPDATE": "orange",
        "DELETE": "red",
    }

    info_items = [
        ("Trigger Name", trigger_name),
        ("Display Name", trigger.display_name),
        ("Schema", schema_name),
        ("Target Table", trigger.table_name),
    ]

    # Create the base info section
    info_div = info_section(info_items)

    # Add timing and event badges
    timing_badge_div = Div(
        Div("Timing", cls="text-sm font-medium text-gray-500"),
        badge(trigger.timing, timing_styles.get(trigger.timing, "gray")),
        cls="py-2"
    )

    event_badge_div = Div(
        Div("Event", cls="text-sm font-medium text-gray-500"),
        badge(trigger.event, event_styles.get(trigger.event, "gray")),
        cls="py-2"
    )

    # Add condition if present
    condition_div = []
    if trigger.condition:
        condition_div = [
            Div(
                Div("Condition", cls="text-sm font-medium text-gray-500"),
                Code(trigger.condition, cls="text-sm font-mono text-gray-900"),
                cls="py-2"
            )
        ]

    return Div(
        info_div,
        timing_badge_div,
        event_badge_div,
        *condition_div,
        cls="grid grid-cols-1 gap-2 sm:grid-cols-3"
    )


def trigger_sql_section(trigger):
    """Create trigger SQL section with syntax highlighting."""
    return sql_section(trigger.body, "SQL Body")
