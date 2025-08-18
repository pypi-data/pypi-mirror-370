from typing import Self

import glfw
import skia

from ..event import SkEvent
from ..styles.color import make_color
from ..var import SkStringVar
from .widget import SkWidget


class SkTextInputBase(SkWidget):
    """A single-line input box without border 【不带边框的单行输入框】"""

    # region Init 初始化

    def __init__(
        self,
        *args,
        size: tuple[int, int] = (105, 35),
        text: str = "",
        textvariable: SkStringVar | None = None,
        placeholder: str | None = None,
        cursor="ibeam",
        **kwargs,
    ) -> None:
        """Text input widget

        :param text: 初始文本
        :param textvariable: 绑定的字符串变量
        :param placeholder: 占位符
        :param cursor: 光标样式
        """
        super().__init__(*args, size=size, cursor=cursor, **kwargs)
        self.attributes["text"] = text
        self.attributes["textvariable"]: SkStringVar = textvariable
        self.attributes["placeholder"] = placeholder
        self.cursor_index = 0
        self.visible_start_index = 0

        self.cursor_visible = True
        self.attributes["blink_interval"] = 500  # 闪烁间隔 (毫秒)

        self.textvariable = textvariable

        self.focusable = True

        self.bind("char", self._char)
        self.bind("key_pressed", self._key)
        self.bind("key_repeated", self._key)

    # endregion

    # region Text&Cursor 文本、光标操作

    def _char(self, event: SkEvent):
        """Triggered when input text is entered."""
        cursor_index = self.cursor_index
        text = self.get()

        self.set(text[:cursor_index] + event.char + text[cursor_index:])
        self.cursor_index += 1

    def _key(self, event: SkEvent):
        """Key event 按键事件触发

        :param event:
        :return:
        """

        text = self.get()
        key = event.key

        match key:
            case glfw.KEY_BACKSPACE:
                """Delete the text before the cursor"""
                self.cursor_backspace()
            case glfw.KEY_LEFT:
                """Move the cursor to the left"""
                self.cursor_left()
            case glfw.KEY_RIGHT:
                """Move the cursor to the right"""
                self.cursor_right()
            case glfw.KEY_V:
                """Paste Text"""
                if event.mods == "control":
                    if isinstance(self.clipboard_get(), str):
                        self.set(
                            text[: self.cursor_index]
                            + self.clipboard_get()
                            + text[self.cursor_index :]
                        )
                        self.cursor_index += len(self.clipboard_get())
            case glfw.KEY_HOME:
                """Move the cursor to the start"""
                self.cursor_home()
            case glfw.KEY_END:
                """Move the cursor to the end"""
                self.cursor_end()
        self._update()

    def _update(self): ...

    def get(self) -> str:
        """Get the input text"""
        if self.attributes["textvariable"]:
            return self.attributes["textvariable"].get()
        else:
            return self.attributes["text"]

    def set(self, text) -> Self:
        """Set the input text"""
        if self.attributes["textvariable"]:
            self.attributes["textvariable"].set(text)
        else:
            self.attributes["text"] = text
        return self

    def cursor_index(self, index: int) -> Self:
        """Set cursor index"""
        self.cursor_index = index
        return self

    def cursor_left(self) -> Self:
        """Move the cursor to the left"""
        if self.cursor_index > 0:
            self.cursor_index -= 1
        return self

    def cursor_right(self) -> Self:
        """Move the cursor to the right"""
        if self.cursor_index < len(self.get()):
            self.cursor_index += 1
        return self

    def cursor_backspace(self) -> Self:
        """Delete the text before the cursor"""
        if self.cursor_index > 0:
            self.set(
                self.get()[: self.cursor_index - 1] + self.get()[self.cursor_index :]
            )
            self.cursor_index -= 1
        return self

    def cursor_home(self) -> Self:
        """Move the cursor to the start"""
        self.cursor_index = 0
        return self

    def cursor_end(self) -> Self:
        """Move the cursor to the end"""
        self.cursor_index = len(self.get())
        return self

    # endregion

    def _draw_text_input(
        self, canvas: skia.Canvas, rect: skia.Rect, fg, placeholder
    ) -> None:
        """Draw the text input"""

        # Draw text
        text_paint = skia.Paint(
            AntiAlias=True,
        )
        text_paint.setColor(make_color(fg))
        font = self.attributes["font"]
        padding = 4  # sheets["width"] * 2
        metrics = font.getMetrics()
        draw_x = rect.left() + padding
        draw_y = (
            rect.top() + rect.height() / 2 - (metrics.fAscent + metrics.fDescent) / 2
        )

        # Define the display area for text to prevent overflow
        # 【划定文本可以显示的区域，防止文本超出显示】
        canvas.save()
        canvas.clipRect(
            skia.Rect.MakeLTRB(
                rect.left() + padding,
                rect.top(),
                rect.right() - padding,
                rect.bottom(),
            )
        )

        if self.get():
            # Draw the text
            canvas.drawSimpleText(self.get(), draw_x, draw_y, font, text_paint)

        if self.is_focus:
            # Draw the cursor
            cursor_index = self.cursor_index
            cursor_x = draw_x + font.measureText(self.get()[:cursor_index])
            canvas.drawLine(
                x0=cursor_x,
                y0=draw_y + metrics.fAscent,
                x1=cursor_x,
                y1=draw_y + metrics.fDescent,
                paint=text_paint,
            )
        else:
            # Draw the placeholder
            if self.attributes["placeholder"] and not self.get():
                text_paint.setColor(make_color(placeholder))
                canvas.drawSimpleText(
                    self.attributes["placeholder"], draw_x, draw_y, font, text_paint
                )

        canvas.restore()
