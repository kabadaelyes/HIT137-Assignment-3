import random

import cv2
import numpy as np

from tiles import Tile, Swap, Rotate, Flip


class PuzzleBoard:
    STEPS = {3: 6, 4: 12, 5: 20}
    KINDS = (Swap, Rotate, Flip)

    def __init__(self, image, size):
        self.image = image
        self.size = size
        self.tile_px = image.shape[0] // size
        t = self.tile_px
        self._sources = [image[r * t:(r + 1) * t, c * t:(c + 1) * t]
                         for r in range(size) for c in range(size)]
        self._slots = [Tile(i) for i in range(size * size)]
        self._history = []
        self.moves = 0

    @property
    def cells(self):
        return self.size * self.size

    def tile_at(self, pos):
        return self._slots[pos]

    def swap(self, a, b):
        self._slots[a], self._slots[b] = self._slots[b], self._slots[a]

    def perform(self, transformation, counted=True):
        transformation.apply(self)
        self._history.append(transformation)
        if counted:
            self.moves += 1

    def scramble(self):
        steps = self.STEPS.get(self.size, self.cells)
        while True:
            kinds = list(self.KINDS) + random.choices(self.KINDS, k=steps - len(self.KINDS))
            random.shuffle(kinds)
            for kind in kinds:
                self.perform(kind.random(self.cells), counted=False)
            if not self.is_solved():
                break
            self.solve()

    def solve(self):
        while self._history:
            self._history.pop().undo(self)
        self.moves = 0

    def is_correct(self, pos):
        tile = self._slots[pos]
        return tile.home == pos and tile.upright

    def wrong_positions(self):
        return [p for p in range(self.cells) if not self.is_correct(p)]

    def is_solved(self):
        return not self.wrong_positions()

    def compose(self):
        pieces = [tile.render(self._sources[tile.home]) for tile in self._slots]
        rows = [np.hstack(pieces[r * self.size:(r + 1) * self.size]) for r in range(self.size)]
        return np.vstack(rows)


class ImageLoader:
    @staticmethod
    def read(path):
        data = np.fromfile(path, dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("That file could not be opened as an image.")
        return image

    @classmethod
    def prepare(cls, path, size, max_side):
        image = cls.read(path)
        h, w = image.shape[:2]
        scale = max_side / min(h, w)
        method = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
        image = cv2.resize(image, (max(1, round(w * scale)), max(1, round(h * scale))), interpolation=method)

        side = max_side // size * size
        h, w = image.shape[:2]
        top, left = (h - side) // 2, (w - side) // 2
        return image[top:top + side, left:left + side].copy()
