import random

import cv2


class Tile:
    def __init__(self, home):
        self.home = home
        self._turns = 0
        self._mirrored = False

    def rotate(self, turns=1):
        self._turns = (self._turns + turns) % 4

    def flip(self, axis="h"):
        offset = 0 if axis == "h" else 2
        self._turns = (offset - self._turns) % 4
        self._mirrored = not self._mirrored

    @property
    def upright(self):
        return self._turns == 0 and not self._mirrored

    def render(self, source):
        img = cv2.flip(source, 1) if self._mirrored else source
        for _ in range(self._turns):
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        return img


class Transformation:
    def apply(self, board):
        raise NotImplementedError

    def undo(self, board):
        raise NotImplementedError

    @classmethod
    def random(cls, cells):
        raise NotImplementedError


class Swap(Transformation):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def apply(self, board):
        board.swap(self.a, self.b)

    def undo(self, board):
        board.swap(self.a, self.b)

    @classmethod
    def random(cls, cells):
        return cls(*random.sample(range(cells), 2))


class Rotate(Transformation):
    def __init__(self, pos, turns=1):
        self.pos, self.turns = pos, turns

    def apply(self, board):
        board.tile_at(self.pos).rotate(self.turns)

    def undo(self, board):
        board.tile_at(self.pos).rotate(-self.turns)

    @classmethod
    def random(cls, cells):
        return cls(random.randrange(cells), random.choice((1, 2, 3)))


class Flip(Transformation):
    def __init__(self, pos, axis="h"):
        self.pos, self.axis = pos, axis

    def apply(self, board):
        board.tile_at(self.pos).flip(self.axis)

    def undo(self, board):
        self.apply(board)

    @classmethod
    def random(cls, cells):
        return cls(random.randrange(cells), random.choice("hv"))
