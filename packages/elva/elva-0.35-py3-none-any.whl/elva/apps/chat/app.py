"""
App definition.
"""

import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import emoji
from pycrdt import Array, ArrayEvent, Doc, Map, MapEvent, Text, TextEvent
from rich.markdown import Markdown as RichMarkdown
from textual.app import App
from textual.containers import VerticalScroll
from textual.css.query import NoMatches
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Rule, Static, TabbedContent, TabPane
from websockets.exceptions import InvalidStatus, WebSocketException

from elva.cli import get_data_file_path, get_render_file_path
from elva.parser import ArrayEventParser, MapEventParser
from elva.provider import WebsocketProvider
from elva.renderer import TextRenderer
from elva.store import SQLiteStore
from elva.widgets.awareness import AwarenessView
from elva.widgets.config import ConfigView
from elva.widgets.screens import Dashboard, ErrorScreen, InputScreen
from elva.widgets.ytextarea import YTextArea

log = logging.getLogger(__name__)

WHITESPACE_ONLY = re.compile(r"^\s*$")
"""Regular Expression for whitespace-only messages."""


class MessageView(Widget):
    """
    Widget displaying a single message alongside its metadata.
    """

    def __init__(self, author: str, text: Text, **kwargs: dict):
        """
        Arguments:
            author: the author of the message.
            text: an instance of a Y text data type holding the message content.
            kwargs: keyword arguments passed to [`Widget`][textual.widget.Widget].
        """
        super().__init__(**kwargs)
        self.text = text
        self.author = author

        content = emoji.emojize(str(text))
        self.text_field = Static(RichMarkdown(content), classes="field content")
        self.text_field.border_title = self.author

    def on_mount(self):
        """
        Hook called on mounting the widget.

        This method subscribes to changes in the message text and displays it if there is some content to show.
        """
        if not str(self.text):
            self.display = False
        self.subscription = self.text.observe(self.text_callback)

    def compose(self):
        """
        Hook arranging child widgets.
        """
        yield self.text_field

    def on_unmount(self):
        """
        Hook called on unmounting.
        """
        if hasattr(self, "subscription"):
            self.text.unobserve(self.subscription)
            del self.subscription

    def text_callback(self, event: TextEvent):
        """
        Hook called on changes in the message text.

        This method updates the visibility of the view in dependence of the message content.

        Arguments:
            event: object holding information about the changes in the Y text.
        """
        text = str(event.target)
        if re.match(WHITESPACE_ONLY, text) is None:
            self.display = True
            content = emoji.emojize(text)
            self.text_field.update(RichMarkdown(content))
        else:
            self.display = False


class MessageList(VerticalScroll):
    """
    Base container class for [`MessageView`][elva.apps.chat.app.MessageView] widgets.
    """

    def __init__(self, messages: Array | Map, user: str, **kwargs: dict):
        """
        Arguments:
            messages: Y array or Y map containing message objects.
            user: the current username of the app.
            kwargs: keyword arguments passed to [`VerticalScroll`][textual.containers.VerticalScroll].
        """
        super().__init__(**kwargs)
        self.user = user
        self.messages = messages

    def get_message_view(
        self, message: Map | dict, message_id: None | str = None
    ) -> MessageView:
        """
        Create a [`MessageView`][elva.apps.chat.app.MessageView].

        Arguments:
            message: mapping of message attributes.
            message_id: `Textual` DOM tree identifier to assign to the message view.

        Returns:
            a message view to be mounted inside an instance of this class.
        """
        author = message["author_display"]
        text = message["text"]
        if message_id is None:
            message_id = "id" + message["id"]
        message_view = MessageView(author, text, classes="message", id=message_id)
        if message["author"] == self.user:
            border_title_align = "right"
        else:
            border_title_align = "left"
        message_view.text_field.styles.border_title_align = border_title_align
        return message_view


class History(MessageList, can_focus=False):
    """
    List of already sent messages.
    """

    def compose(self):
        """
        Hook arranging child widgets.
        """
        for message in self.messages:
            message_view = self.get_message_view(message)
            yield message_view


class HistoryParser(ArrayEventParser):
    """
    Parser for changes in the message history.

    This class reflects the state of the Y array with history message in the [`History`][elva.apps.chat.app.History] message list on changes.
    """

    def __init__(self, history: Array, widget: History):
        """
        Arguments:
            history: Y array containing already sent messages.
        """
        self.history = history
        self.widget = widget

    def history_callback(self, event: ArrayEvent):
        """
        Hook called on a change in the Y array message history.

        This method parses the event and calls the defined action hooks accordingly.

        Arguments:
            event: an object holding information about the change in the Y array.
        """
        self.parse_nowait(event)
        self.log.debug("history callback triggered")

    async def before(self):
        """
        Hook called before the component sets the `RUNNING` state.

        This method subscribes to changes in the Y array message history.
        """
        self.subscription = self.history.observe(self.history_callback)
        self.log.debug("subscribed to changes in history")

    async def on_insert(self, range_offset: int, insert_value: str):
        """
        Hook called on an insert action in a Y array change event.

        This methods creates a new message view and mounts it to the message history.

        Arguments:
            range_offset: the start index of the insert.
            insert_value: the inserted content.
        """
        for message in insert_value:
            message_view = self.widget.get_message_view(message)
            log.debug("mounting message view in history")
            await self.widget.mount(message_view, after=range_offset - 1)

    async def cleanup(self):
        """
        Hook called after cancellation and before the component unsets its state to `NONE`.
        """
        if hasattr(self, "subscription"):
            self.history.unobserve(self.subscription)
            del self.subscription

    async def on_delete(self, range_offset: int, range_length: str):
        """
        Hook called on a delete action in a Y array change event.

        This method removes the all message views in the given index range.

        Arguments:
            range_offset: the start index of the deletion.
            range_length: the number of subsequent indices.
        """
        for message_view in self.widget.children[
            range_offset : range_offset + range_length
        ]:
            log.debug("deleting message view in history")
            await message_view.remove()


class Future(MessageList, can_focus=False):
    """
    List of currently composed messages.
    """

    def __init__(
        self, messages: Map, user: str, show_self: bool = False, **kwargs: dict
    ):
        """
        Arguments:
            messages: mapping of message identifiers to their corresponding message object.
            user: the current username of the app.
            show_self: flag whether to show the own currently composed message.
            kwargs: keyword arguments passed to [`MessageList`][elva.apps.chat.app.MessageList].
        """
        super().__init__(messages, user, **kwargs)
        self.show_self = show_self

    def compose(self):
        """
        Hook arranging child widgets.
        """
        for message_id, message in self.messages.items():
            if not self.show_self and message["author"] == self.user:
                continue
            else:
                message_view = self.get_message_view(
                    message, message_id="id" + message_id
                )
                yield message_view


class FutureParser(MapEventParser):
    """
    Parser for changes in currently composed messages.

    This class reflects the state of the Y map with currently composed messaged in the [`Future`][elva.apps.chat.app.Future] message list on changes.
    """

    def __init__(self, future: Map, widget: Future, user: str, show_self: bool):
        """
        Arguments:
            future: Y map mapping message identifiers to their corresponding message objects.
            widget: the message list widget displaying the currently composed messages.
            user: the current username.
            show_self: flag whether to show the own currently composed message.
        """
        self.future = future
        self.widget = widget
        self.user = user
        self.show_self = show_self

    def future_callback(self, event: MapEvent):
        """
        Hook called on changes in the Y map.

        This method parses the event object and calls action hooks accordingly.

        Arguments:
            event: an object holding information about the change in the Y map.
        """
        self.parse_nowait(event)
        log.debug("future callback triggered")

    async def before(self):
        """
        Hook called before the component sets the `RUNNING` signal.

        This method subscribes to changes in the mapping of currently composed messages.
        """
        self.subscription = self.future.observe(self.future_callback)
        self.log.debug("subscribed to changes in future")

    async def cleanup(self):
        """
        Hook called after cancellation and before the component unsets its state to `NONE`.
        """
        if hasattr(self, "subscription"):
            self.future.unobserve(self.subscription)
            del self.subscription

    async def on_add(self, key: str, new_value: dict):
        """
        Hook called on an add action.

        This methods generates a message view from the added message object and mounts it to the list of currently composed messages.

        Arguments:
            key: the message id that has been added.
            new_value: the message object that has been added.
        """
        # TODO: fix the origin of empty values
        if not new_value:
            return

        if not self.show_self and new_value["author"] == self.user:
            return

        message_view = self.widget.get_message_view(new_value, message_id="id" + key)
        log.debug("mounting message view in future")
        self.widget.mount(message_view)

    async def on_delete(self, key: str, old_value: dict):
        """
        Hook called on a delete action.

        This methods removes the message view corresponding to the removed message id.

        Arguments:
            key: the message id that has been deleted.
            old_value: the message object that has been deleted.
        """
        # TODO: fix the origin of empty values
        if not old_value:
            return

        try:
            message = self.widget.query_one("#id" + key)
            log.debug("deleting message view in future")
            message.remove()
        except NoMatches:
            pass


class MessagePreview(Static):
    """
    Preview of the rendered markdown content.
    """

    def __init__(self, ytext: Text, *args: tuple, **kwargs: dict):
        """
        Arguments:
            ytext: Y text with the markdown content of the own currently composed message.
            args: positional arguments passed to [`Static`][textual.widgets.Static].
            kwargs: keyword arguments passed to [`Static`][textual.widgets.Static].
        """
        super().__init__(*args, **kwargs)
        self.ytext = ytext

    async def on_show(self):
        """
        Hook called on a show message.
        """
        self.update(RichMarkdown(emoji.emojize(str(self.ytext))))


class UI(App):
    """
    User interface.
    """

    CSS_PATH = "style.tcss"
    """The path to the default CSS."""

    SCREENS = {
        "dashboard": Dashboard,
        "input": InputScreen,
    }
    """The installed screens."""

    BINDINGS = [
        ("shift+enter", "send", "Send currently composed message"),
        ("ctrl+enter", "send", "Send currently composed message"),
        ("ctrl+o", "send", "Send currently composed message"),
        ("ctrl+b", "toggle_dashboard", "Toggle the dashboard"),
        ("ctrl+s", "save", "Save to data file"),
        ("ctrl+r", "render", "Render to file"),
    ]
    """Key bindings for controlling the app."""

    def __init__(
        self,
        config: dict,
        *args: tuple,
        **kwargs: dict,
    ):
        """
        Arguments:
            config: mapping of configuration parameters.
            args: positional arguments passed to [`App`][textual.app.App].
            kwargs: keyword arguments passed to [`App`][textual.app.App].
        """
        super().__init__(*args, **kwargs)

        # structure
        self.ydoc = ydoc = Doc()
        ydoc["history"] = self.history = Array()
        ydoc["future"] = self.future = Map()

        self.config = c = config

        self.client_id = str(self.ydoc.client_id)
        self.user = c.get("user", self.client_id)
        self.display_name = c.get("name")
        self.show_self = show_self = c.get("show_self", True)

        self.message, self.ytext, message_id = self.get_message("")

        # widgets
        self.history_widget = History(self.history, self.user, id="history")
        self.future_widget = Future(
            self.future, self.user, show_self=show_self, id="future"
        )

        # components
        self.history_parser = HistoryParser(self.history, self.history_widget)
        self.future_parser = FutureParser(
            self.future,
            self.future_widget,
            self.user,
            show_self,
        )

        self.components = [
            self.history_parser,
            self.future_parser,
        ]

        if c.get("file") is not None:
            self.store = SQLiteStore(
                self.ydoc,
                c["identifier"],
                c["file"],
            )
            self.components.append(self.store)

        if c.get("host") is not None:
            self.provider = WebsocketProvider(
                ydoc,
                c["identifier"],
                c["host"],
                port=c.get("port"),
                safe=c.get("safe", True),
                on_exception=self.on_provider_exception,
            )

            data = {}
            if c.get("name") is not None:
                data = {"user": {"name": c["name"]}}

            self.provider.awareness.set_local_state(data)

            self.components.append(self.provider)

        if c.get("render") is not None:
            self.renderer = TextRenderer(
                self.history,
                c["render"],
                c.get("auto_save", True),
            )
            self.components.append(self.renderer)

    def get_new_id(self) -> str:
        """
        Get a new message id.

        Returns:
            a UUID v4 identifier.
        """
        return str(uuid.uuid4())

    def get_message(
        self, text: str, message_id: None | str = None
    ) -> tuple[Map, Text, str]:
        """
        Get a message object.

        Arguments:
            text: the content of the message.
            message_id: the identifier of the message.

        Returns:
            a Y Map containing a mapping of message attributes as well as the Y Text and the message ID included therein.
        """
        if message_id is None:
            message_id = self.get_new_id()

        ytext = Text(text)
        ymap = Map(
            {
                "text": ytext,
                "author_display": self.display_name or self.client_id,
                # we assume that self.user is unique in the room, ensured by the server
                "author": self.user,
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return ymap, ytext, message_id

    async def run_components(self):
        """
        Run all components the chat app needs.
        """
        for comp in self.components:
            self.run_worker(comp.start())
            sub = comp.subscribe()
            while comp.states.RUNNING not in comp.state:
                await sub.receive()
            comp.unsubscribe(sub)

    async def on_mount(self):
        """
        Hook called on mounting the app.

        This methods waits for all components to set their `RUNNING` state.
        """
        if hasattr(self, "provider"):
            self.subscription = self.provider.awareness.observe(
                self.on_awareness_update
            )

        await self.run_components()

        self.future[self.client_id] = self.message

        tabbed_content = self.query_one(TabbedContent)
        ytext_pane = TabPane(
            "Message",
            YTextArea(
                self.ytext,
                id="editor",
                language="markdown",
            ),
            id="tab-message",
        )
        preview_pane = TabPane(
            "Preview",
            VerticalScroll(MessagePreview(self.ytext)),
            id="tab-preview",
        )

        for pane in (ytext_pane, preview_pane):
            await tabbed_content.add_pane(pane)

        message_widget = self.query_one(YTextArea)
        message_widget.focus()

    def compose(self):
        """
        Hook arranging child widgets.
        """
        yield self.history_widget
        yield Rule(line_style="heavy")
        yield self.future_widget
        yield TabbedContent(id="tabview")

    def on_unmount(self):
        """
        Hook called on unmounting.

        It cancels the subscription to changes in the awareness states.
        """
        if hasattr(self, "subscription"):
            self.provider.awareness.unobserve(self.subscription)
            del self.subscription

    async def action_send(self):
        """
        Hook called on an invoked send action.

        This method transfers the message from the future to the history.
        """
        text = str(self.ytext)
        if re.match(WHITESPACE_ONLY, text) is None:
            message, *_ = self.get_message(text, message_id=self.message["id"])
            self.history.append(message)

            self.ytext.clear()
            self.message["id"] = self.get_new_id()

    def on_tabbed_content_tab_activated(self, event: Message):
        """
        Hook called on a tab activated message from a tabbed content widget.

        Arguments:
            event: object holding information about the tab activated message.
        """
        message_widget = self.query_one(YTextArea)
        if event.pane.id == "tab-message":
            message_widget.focus()

    def on_provider_exception(self, exc: WebSocketException, config: dict):
        """
        Wrapper method around the provider exception handler
        [`_on_provider_exception`][elva.apps.editor.app.UI._on_provider_exception].

        Arguments:
            exc: the exception raised by the provider.
            config: the configuration stored in the provider.
        """
        self.run_worker(self._on_provider_exception(exc, config))

    async def _on_provider_exception(self, exc: WebSocketException, config: dict):
        """
        Handler for exceptions raised by the provider.

        It exits the app after displaying the error message to the user.

        Arguments:
            exc: the exception raised by the provider.
            config: the configuration stored in the provider.
        """
        await self.provider.stop()

        if type(exc) is InvalidStatus:
            response = exc.response
            exc = f"HTTP {response.status_code}: {response.reason_phrase}"

        await self.push_screen_wait(ErrorScreen(exc))
        self.exit(return_code=1)

    def on_awareness_update(
        self, topic: Literal["update", "change"], data: tuple[dict, Any]
    ):
        """
        Wrapper method around the
        [`_on_awareness_update`][elva.apps.editor.app.UI._on_awareness_update]
        callback.

        Arguments:
            topic: the topic under which the changes are published.
            data: manipulation actions taken as well as the origin of the changes.
        """
        if topic == "change":
            self.run_worker(self._on_awareness_update(topic, data))

    async def _on_awareness_update(
        self, topic: Literal["update", "change"], data: tuple[dict, Any]
    ):
        """
        Hook called on a change in the awareness states.

        It pushes client states to the dashboard and removes offline client IDs from the future.

        Arguments:
            topic: the topic under which the changes are published.
            data: manipulation actions taken as well as the origin of the changes.
        """
        if self.screen == self.get_screen("dashboard"):
            self.push_client_states()

        actions, origin = data
        removed = actions["removed"]
        for client_id in removed:
            if str(client_id) != self.client_id:
                try:
                    self.future.pop(str(client_id))
                except KeyError:
                    pass

    async def action_save(self):
        """
        Action performed on triggering the `save` key binding.
        """
        if self.config.get("file") is None:
            self.run_worker(self.get_and_set_file_paths())

    async def get_and_set_file_paths(self, data_file: bool = True):
        """
        Get and set the data or render file paths after the input prompt.

        Arguments:
            data_file: flag whether to add a data file path to the config.
        """
        name = await self.push_screen_wait("input")

        if not name:
            return

        path = Path(name)

        data_file_path = get_data_file_path(path)
        if data_file:
            self.config["file"] = data_file_path
            self.store = SQLiteStore(
                self.ydoc, self.config["identifier"], data_file_path
            )
            self.components.append(self.store)
            self.run_worker(self.store.start())

        if self.config.get("render") is None:
            render_file_path = get_render_file_path(data_file_path)
            self.config["render"] = render_file_path

            self.renderer = TextRenderer(
                self.history, render_file_path, self.config.get("auto_save", True)
            )
            self.components.append(self.renderer)
            self.run_worker(self.renderer.start())

        if self.screen == self.get_screen("dashboard"):
            self.push_config()

    async def action_render(self):
        """
        Action performed on triggering the `render` key binding.
        """
        if self.config.get("render") is None:
            self.run_worker(self.get_and_set_file_paths(data_file=False))
        else:
            await self.renderer.write()

    async def action_toggle_dashboard(self):
        """
        Action performed on triggering the `toggle_dashboard` key binding.
        """
        if self.screen == self.get_screen("dashboard"):
            self.pop_screen()
        else:
            await self.push_screen("dashboard")
            self.push_client_states()
            self.push_config()

    def push_client_states(self):
        """
        Method pushing the client states to the active dashboard.
        """
        if hasattr(self, "provider"):
            client_states = self.provider.awareness.client_states.copy()
            client_id = self.provider.awareness.client_id
            if client_id not in client_states:
                return
            states = list()
            states.append((client_id, client_states.pop(client_id)))
            states.extend(list(client_states.items()))
            states = tuple(states)

            awareness_view = self.screen.query_one(AwarenessView)
            awareness_view.states = states

    def push_config(self):
        """
        Method pushing the configuration mapping to the active dashboard.
        """
        config = tuple(self.config.items())

        config_view = self.screen.query_one(ConfigView)
        config_view.config = config
