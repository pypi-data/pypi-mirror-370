"""Components for the CLI."""

from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.styles.base import BaseStyle
from prompt_toolkit.widgets import Label, RadioList

BETA_BANNER = "[red][bold]BETA[/bold][/red]"


# https://github.com/prompt-toolkit/python-prompt-toolkit/issues/756
def radiolist_dialog(
    title: str = "",
    values: list[tuple[str, str]] = [],
    style: BaseStyle | None = None,
    default_value_index: int = 0,
    navigation_help: bool = False,
    async_: bool = True,
) -> Any:  # prompt_toolkit returns private _AppResult type
    """
    Create a radio list for prompt.

    Will create a prompt version of a radio button.

    :param title: Title to show
    :param values: Values to select
    :param style: Custom styling
    :param default_value_index: Start with cursor at this index
    :param navigation_help: Print navigation help
    :param async_: If called form async runtime
    """
    # Add exit key binding.
    bindings = KeyBindings()

    radio_list = RadioList(values)

    # Don't show a marker, it's just confusing. Use the cursor to indicate which
    # selection will be made.
    radio_list.current_value = ""

    # But we can specify where we want the marker to begin.
    if default_value_index != 0:
        radio_list._selected_index = default_value_index

    # Remove the enter key binding so that we can augment it
    radio_list.control.key_bindings.remove("enter")  # type: ignore
    radio_list.control.key_bindings.remove("space")  # type: ignore

    @bindings.add("c-c")
    def exit_(event: KeyPressEvent) -> None:
        """Pressing Ctrl-d will exit the user interface."""
        event.app.exit()

    @bindings.add("enter")
    def exit_with_value(event: KeyPressEvent) -> None:
        """Pressing Ctrl-a will exit the user interface returning the selected value."""
        radio_list._handle_enter()
        event.app.exit(result=radio_list.current_value)

    panel = [
        Label(title),
        radio_list,
    ]

    if navigation_help:
        panel.insert(0, Label("↑ ← ↓ → to navigate, [Enter] to select current row\n"))

    application: Application = Application(
        layout=Layout(HSplit(panel)),  # type: ignore
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=False,
    )

    if async_:
        return application.run_async()

    return application.run()


async def proceed_with_operation(auto_approve: bool) -> bool:
    """Request confirmation before performing an operation."""
    if auto_approve:
        return True

    print()
    print("Do you want to perform these operations?")
    print("\tOnly 'yes' is accepted to approve")

    session: PromptSession = PromptSession()
    p = await session.prompt_async("Enter a value: ")
    if p != "yes":
        print("Cancelled")
        return False

    return True
