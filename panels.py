import base64
import tkinter as tk

import cv2


def to_photo(image):
    ok, buffer = cv2.imencode(".png", image)
    return tk.PhotoImage(data=base64.b64encode(buffer.tobytes()).decode("ascii"))


class ImagePanel(tk.Canvas):
    def __init__(self, master, side):
        super().__init__(master, width=side, height=side, bg="#202124", highlightthickness=0)
        self.side = side
        self.board = None
        self.hint = None
        self._photo = None
        self.refresh()

    def attach(self, board):
        self.board = board
        self.hint = None
        h, w = board.image.shape[:2]
        self.config(width=w, height=h)
        self.refresh()

    def picture(self):
        raise NotImplementedError

    def decorate(self):
        pass

    def refresh(self):
        self.delete("all")
        if self.board is None:
            self.create_text(self.side // 2, self.side // 2, text="Load an image to start",
                             fill="#9aa0a6", font=("Segoe UI", 12))
            return
        self._photo = to_photo(self.picture())
        self.create_image(0, 0, anchor="nw", image=self._photo)
        self.decorate()
        if self.hint is not None:
            self._circle(self.hint)

    def box(self, pos):
        t = self.board.tile_px
        r, c = divmod(pos, self.board.size)
        return c * t, r * t, (c + 1) * t, (r + 1) * t

    def _circle(self, pos):
        x0, y0, x1, y1 = self.box(pos)
        pad = (x1 - x0) * 0.2
        self.create_oval(x0 + pad, y0 + pad, x1 - pad, y1 - pad, outline="#1e90ff", width=4)


class ReferencePanel(ImagePanel):
    def picture(self):
        return self.board.image


class PuzzlePanel(ImagePanel):
    def __init__(self, master, side):
        self.selected = None
        super().__init__(master, side)

    def attach(self, board):
        self.selected = None
        super().attach(board)

    def picture(self):
        return self.board.compose()

    def decorate(self):
        t = self.board.tile_px
        end = t * self.board.size
        for i in range(1, self.board.size):
            self.create_line(i * t, 0, i * t, end, fill="#e0e0e0", dash=(3, 4))
            self.create_line(0, i * t, end, i * t, fill="#e0e0e0", dash=(3, 4))

        for pos in range(self.board.cells):
            if self.board.is_correct(pos):
                self._tick(pos)

        if self.selected is not None:
            x0, y0, x1, y1 = self.box(self.selected)
            self.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2, outline="#ffb000", width=4)

    def _tick(self, pos):
        x0, y0, x1, _ = self.box(pos)
        s = max(14, (x1 - x0) // 6)
        x, y = x1 - s - 6, y0 + 6
        self.create_oval(x - 2, y - 2, x + s + 2, y + s + 2, fill="white", outline="")
        self.create_line(x + s * 0.2, y + s * 0.55, x + s * 0.42, y + s * 0.78, x + s * 0.82, y + s * 0.25,
                         fill="#1e9e4a", width=3, capstyle="round", joinstyle="round")

    def position_at(self, x, y):
        if self.board is None:
            return None
        t = self.board.tile_px
        c, r = x // t, y // t
        if 0 <= c < self.board.size and 0 <= r < self.board.size:
            return r * self.board.size + c
        return None
