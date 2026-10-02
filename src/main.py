import random
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from board import PuzzleBoard, ImageLoader
from panels import ReferencePanel, PuzzlePanel
from tiles import Swap, Rotate, Flip


class PuzzleApp(tk.Tk):
    MAX_HINTS = 3

    def __init__(self):
        super().__init__()
        self.title("Picture Restore")
        self.resizable(False, False)
        self.configure(padx=12, pady=12)

        self.board = None
        self.locked = True
        self.hints_left = 0
        self.grid_size = tk.IntVar(value=3)
        self.status = tk.StringVar()
        self.side = max(240, min(self.winfo_screenwidth() // 2 - 60, self.winfo_screenheight() - 260))

        self._build()
        self._update_status()

    def _build(self):
        bar = tk.Frame(self)
        bar.pack(fill="x", pady=(0, 10))

        tk.Label(bar, text="Grid:").pack(side="left")
        for n in (3, 4, 5):
            tk.Radiobutton(bar, text=f"{n} x {n}", value=n, variable=self.grid_size).pack(side="left")

        tk.Button(bar, text="Load Image", command=self.load_image).pack(side="left", padx=(16, 4))
        self.hint_button = tk.Button(bar, text="Hint", command=self.give_hint, state="disabled")
        self.hint_button.pack(side="left", padx=4)
        self.solve_button = tk.Button(bar, text="Solve", command=self.solve, state="disabled")
        self.solve_button.pack(side="left", padx=4)

        tk.Label(self, textvariable=self.status, anchor="w", font=("Segoe UI", 11, "bold")).pack(fill="x", pady=(0, 8))

        boards = tk.Frame(self)
        boards.pack()
        left, right = tk.Frame(boards), tk.Frame(boards)
        left.pack(side="left", padx=(0, 12))
        right.pack(side="left")

        tk.Label(left, text="Original").pack()
        tk.Label(right, text="Puzzle").pack()
        self.reference = ReferencePanel(left, self.side)
        self.reference.pack()
        self.puzzle = PuzzlePanel(right, self.side)
        self.puzzle.pack()

        self.puzzle.bind("<Button-1>", self.on_click)
        self.puzzle.bind("<Shift-Button-1>", self.on_flip)
        self.puzzle.bind("<Button-3>", self.on_rotate)
        if sys.platform == "darwin":
            self.puzzle.bind("<Button-2>", self.on_rotate)

    def load_image(self):
        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            image = ImageLoader.prepare(path, self.grid_size.get(), self.side)
        except ValueError as err:
            messagebox.showerror("Can't load image", str(err))
            return

        self.board = PuzzleBoard(image, self.grid_size.get())
        self.board.scramble()
        self.hints_left = self.MAX_HINTS
        self.locked = False
        self.reference.attach(self.board)
        self.puzzle.attach(self.board)
        self._update_status()

    def _cell(self, event):
        if self.locked:
            return None
        return self.puzzle.position_at(event.x, event.y)

    def on_click(self, event):
        pos = self._cell(event)
        if pos is None:
            return
        first = self.puzzle.selected
        if first is None:
            self.puzzle.selected = pos
            self.puzzle.refresh()
        elif first == pos:
            self.puzzle.selected = None
            self.puzzle.refresh()
        else:
            self._move(Swap(first, pos))

    def on_rotate(self, event):
        pos = self._cell(event)
        if pos is not None:
            self._move(Rotate(pos, 1))

    def on_flip(self, event):
        pos = self._cell(event)
        if pos is not None:
            self._move(Flip(pos, "h"))

    def _move(self, transformation):
        self.board.perform(transformation)
        self._clear_marks()
        self._redraw()

        if self.board.is_solved():
            self.locked = True
            self._update_status()
            messagebox.showinfo("Picture restored", f"Nice work! You restored it in {self.board.moves} moves.")

    def give_hint(self):
        if self.locked or self.hints_left == 0:
            return
        wrong = self.board.wrong_positions()
        if self.puzzle.hint in wrong and len(wrong) > 1:
            wrong.remove(self.puzzle.hint)
        pos = random.choice(wrong)
        self.puzzle.hint = pos
        self.reference.hint = self.board.tile_at(pos).home
        self.hints_left -= 1
        self._redraw()

    def solve(self):
        if self.board is None or self.locked:
            return
        self.board.solve()
        self.locked = True
        self._clear_marks()
        self._redraw()

    def _clear_marks(self):
        self.puzzle.selected = None
        self.puzzle.hint = None
        self.reference.hint = None

    def _redraw(self):
        self.reference.refresh()
        self.puzzle.refresh()
        self._update_status()

    def _update_status(self):
        if self.board is None:
            self.status.set("Pick a grid size and load an image.")
        else:
            wrong = len(self.board.wrong_positions())
            text = f"Moves: {self.board.moves}    Tiles incorrect: {wrong}    Hints left: {self.hints_left}"
            if self.board.is_solved():
                text += "    — Solved!"
            self.status.set(text)

        active = not self.locked
        self.hint_button.config(state="normal" if active and self.hints_left > 0 else "disabled")
        self.solve_button.config(state="normal" if active else "disabled")


if __name__ == "__main__":
    PuzzleApp().mainloop()
