import typing

import glfw
import skia

from ..base.windowbase import SkWindowBase
from ..event import SkEvent
from ..styles.color import style_to_color
from ..styles.texture import SkAcrylic
from ..styles.theme import SkTheme, default_theme
from .app import SkApp
from .container import SkContainer


class SkWindow(SkWindowBase, SkContainer):
    # region __init__ 初始化

    def __init__(
        self,
        parent: typing.Self | SkApp = None,
        *args,
        theme: SkTheme = default_theme,
        size: tuple[int, int] = (300, 300),
        anti_alias: bool = True,
        **kwargs,
    ) -> None:
        """SkWindow, inherited from SkWindowBase

        :param args: SkWindowBase Args
        :param theme: Theme
        :param kwargs: SkWindowBase Kwargs
        """
        SkWindowBase.__init__(self, parent=parent, *args, size=size, **kwargs)
        SkContainer.__init__(self)

        self.theme: SkTheme = theme

        self.focus_widget = self
        self.draws: list[typing.Callable] = []

        self.window: SkWindow = self
        self.anti_alias: bool = anti_alias

        self.previous_widget = None

        self.set_draw_func(self._draw)
        self.bind("mouse_motion", self._motion, add=True)
        self.bind("mouse_pressed", self._mouse)
        self.bind("mouse_released", self._mouse_released)

        self.bind("focus_loss", self._leave)
        self.bind("mouse_leave", self._leave)

        self.bind("char", self._char)

        self.bind("key_pressed", self._key_pressed)
        self.bind("key_repeated", self._key_repected)
        self.bind("key_released", self._key_released)

        self.bind("scroll", self._scroll)

    # endregion

    # region Theme related 主题相关

    def apply_theme(self, new_theme: SkTheme):
        """Apply theme to the window and its children.

        :param new_theme:
        :return:
        """
        self.theme = new_theme
        self.styles = self.theme.styles
        for child in self.children:
            child.apply_theme(new_theme)

    # endregion

    # region Event handlers 事件处理

    def destroy(self) -> None:
        super().destroy()

    def _key_pressed(self, event):
        """Key press event for SkWindow.

        :param event: SkEvent
        :return:
        """
        # print(cls.cget("focus_widget"))
        if self.focus_get() is not self:
            self.focus_get().event_trigger("key_pressed", event)
        del event

    def _scroll(self, event: SkEvent) -> None:
        if self.focus_get() is not self:
            self.focus_get().event_trigger("scroll", event)
        del event

    def _key_repected(self, event: SkEvent) -> None:
        if self.focus_get() is not self:
            self.focus_get().event_trigger("key_repeated", event)
        del event

    def _key_released(self, event: SkEvent) -> None:
        if self.focus_get() is not self:
            self.focus_get().event_trigger("key_released", event)
        del event

    def _char(self, event: SkEvent) -> None:
        # print(12)
        if self.focus_get() is not self:
            self.focus_get().event_trigger("char", event)
        del event

    def _leave(self, event: SkEvent) -> None:
        event = SkEvent(
            event_type="mouse_leave",
            x=event.x,
            y=event.y,
            rootx=event.rootx,
            rooty=event.rooty,
        )
        for widget in self.children:
            widget.is_mouse_pressed = False
            widget.event_trigger("mouse_leave", event)
        del event

    def _mouse(self, event: SkEvent) -> None:
        for widget in self.children:
            if (
                widget.canvas_x <= event.x <= widget.canvas_x + widget.width
                and widget.canvas_y <= event.y <= widget.canvas_y + widget.height
            ):
                widget.is_mouse_floating = True
                if widget.focusable:
                    widget.focus_set()
                widget.is_mouse_pressed = True
                widget.button = event.button
                widget.event_trigger("mouse_pressed", event)

    def _motion(self, event: SkEvent) -> None:
        """Mouse motion event for SkWindow.

        :param event: SkEvent
        :return:
        """
        current_widget = None
        event = SkEvent(
            event_type="mouse_motion",
            x=event.x,
            y=event.y,
            rootx=event.rootx,
            rooty=event.rooty,
        )

        # 找到当前鼠标所在的视觉元素
        for widget in reversed(self.children):
            if (
                widget.canvas_x <= event.x <= widget.canvas_x + widget.width
                and widget.canvas_y <= event.y <= widget.canvas_y + widget.height
            ):
                current_widget = widget
                break

        # 处理上一个元素的离开事件
        if self.previous_widget and self.previous_widget != current_widget:
            event.event_type = "mouse_leave"
            self.cursor(self.default_cursor())
            self.previous_widget.event_trigger("mouse_leave", event)
            self.previous_widget.is_mouse_floating = False

        # 处理当前元素的进入和移动事件
        if current_widget:
            if current_widget.visible:
                if not current_widget.is_mouse_floating:
                    event.event_type = "mouse_enter"
                    self.cursor(current_widget.attributes["cursor"])
                    current_widget.is_floating = True
                    current_widget.event_trigger("mouse_enter", event)
                    current_widget.is_mouse_floating = True
                else:
                    event.event_type = "mouse_motion"
                    self.cursor(current_widget.attributes["cursor"])
                    current_widget.is_floating = True
                    current_widget.event_trigger("mouse_motion", event)
                self.previous_widget = current_widget
        else:
            self.previous_widget = None
        del current_widget, event

    def _draw(self, canvas: skia.Canvas) -> None:
        # print(style_to_color())
        bg = self.theme.get_style("SkWindow")["bg"]
        canvas.clear(style_to_color(bg, self.theme).color)
        # canvas.clear(skia.ColorTRANSPARENT)

        self.draw_children(canvas)

        return None

    def _mouse_released(self, event: SkEvent) -> None:
        """Mouse release event for SkWindow.

        :param event:
        :return:
        """
        event = SkEvent(
            event_type="mouse_released",
            x=event.x,
            y=event.y,
            rootx=self.mouse_rootx,
            rooty=self.mouse_rooty,
        )
        for widget in self.children:
            if widget.is_mouse_pressed:
                widget.is_mouse_pressed = False
                widget.event_trigger("mouse_released", event)
        return None

    # endregion

    # region Focus related 焦点相关

    def focus_get(self):
        """Get the current widget as the focus

        :return:
        """
        return self.focus_widget

    def focus_set(self):
        """Set the current widget as the focus

        :return:
        """
        self.focus_widget = self
        glfw.focus_window(self.glfw_window)

    # endregion
