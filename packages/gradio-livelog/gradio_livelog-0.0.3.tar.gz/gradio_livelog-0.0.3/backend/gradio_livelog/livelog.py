# backend/gradio_livelog/livelog.py

from __future__ import annotations
from typing import Any, Dict, List, Callable, Literal

from gradio_client.documentation import document
from gradio.component_meta import ComponentMeta
from gradio.events import Events
from gradio.components.base import Component 

@document()
class LiveLog(Component, metaclass=ComponentMeta):
    """
    A component for displaying real-time logs and progress bars.
    It receives structured data via a generator to update its state.
    """
    EVENTS = [Events.change, Events.clear]

    def __init__(
        self,
        value: List[Dict[str, Any]] | Callable | None = None,
        *,
        label: str | None = None,
        every: float | None = None,
        height: int | str = 400,
        autoscroll: bool = True,
        line_numbers: bool = False,
        background_color: str = "#000000",
        display_mode: Literal["full", "log", "progress"] = "full",
        disable_console: bool = True,
        show_download_button: bool = True,
        show_copy_button: bool = True,
        show_clear_button: bool = True,
        show_label: bool = True,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
    ):
        """
        Parameters:
            value: The initial value, a list of log/progress dictionaries. Can be a callable.
            label: The component label.
            every: If `value` is a callable, run the function 'every' seconds.
            height: The height of the log panel in pixels or CSS units.
            autoscroll: If True, the panel will automatically scroll to the bottom on new logs.
            line_numbers: If True, shows line numbers for logs.
            background_color: The background color of the log panel as a CSS-valid string.
            display_mode: "full" (logs and progress), "log" (only logs), or "progress" (only progress bar).
            disable_console: If True, logs will not be propagated to the standard Python console.
            show_download_button: If True, shows the download button in the header.
            show_copy_button: If True, shows the copy button in the header.
            show_clear_button: If True, shows the clear button in the header.
            show_label: If True, will display label.
            container: If True, will place the component in a container.
            scale: Relative size compared to adjacent Components.
            min_width: Minimum pixel width, will wrap if not sufficient screen space.
            visible: If False, the component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM.
            elem_classes: An optional string or list of strings assigned as the class of this component.
            render: If False, this component will not be rendered.
            key: A unique key for the component.
        """
        self.height = height
        self.autoscroll = autoscroll
        self.line_numbers = line_numbers
        self.background_color = background_color
        self.display_mode = display_mode
        self.disable_console = disable_console
        self.show_download_button = show_download_button
        self.show_copy_button = show_copy_button
        self.show_clear_button = show_clear_button
        
        super().__init__(
            label=label,
            every=every,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            value=value,
        )

    def preprocess(self, payload: List[Dict[str, Any]] | None) -> List[Dict[str, Any]] | None:
        return payload

    def postprocess(self, value: List[Dict[str, Any]] | None) -> List[Dict[str, Any]] | None:
        return value

    def api_info(self) -> Dict[str, Any]:
        return {"type": "array", "items": {"type": "object"}}

    def example_payload(self) -> Any:
        return [
            {"type": "log", "level": "INFO", "content": "Cloning repository..."},
            {"type": "progress", "current": 50, "total": 100, "desc": "Downloading..."}
        ]

    def example_value(self) -> Any:
        return [
            {"type": "log", "level": "INFO", "content": "Cloning repository..."},
            {"type": "progress", "current": 50, "total": 100, "desc": "Downloading..."}
        ]