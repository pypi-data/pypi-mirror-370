from collections.abc import Iterable
from typing import TYPE_CHECKING

from matplotlib.pyplot import figure
from numpy import arctan2, argmax, asarray, cos, flip, sin, sqrt

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from numpy.typing import NDArray


class Airfoil():
    name: str = None
    x: 'NDArray' = None
    y: 'NDArray' = None
    _xte: float = None
    _yte: float = None
    _ile: int = None
    _xle: float = None
    _yle: float = None
    _chord: float = None
    _alrad: float = None
    _tte: float = None
    _area: float = None
    _xu: 'NDArray' = None
    _yu: 'NDArray' = None
    _xl: 'NDArray' = None
    _yl: 'NDArray' = None

    def __init__(self, name: str, x: Iterable, y: Iterable) -> None:
        self.name = name
        self.x = asarray(x)
        self.y = asarray(y)
        self.validate_area()

    def reset(self) -> None:
        for attr in self.__dict__:
            if attr.startswith('_'):
                setattr(self, attr, None)

    @property
    def xte(self) -> float:
        if self._xte is None:
            self._xte = (self.x[-1] + self.x[0])/2
        return self._xte

    @property
    def yte(self) -> float:
        if self._yte is None:
            self._yte = (self.y[-1] + self.y[0])/2
        return self._yte

    @property
    def ile(self) -> int:
        if self._ile is None:
            dx = self.x - self.xte
            dy = self.y - self.yte
            d2 = dx**2 + dy**2
            self._ile = argmax(d2)
        return self._ile

    @property
    def xle(self) -> float:
        if self._xle is None:
            self._xle = self.x[self.ile]
        return self._xle

    @property
    def yle(self) -> float:
        if self._yle is None:
            self._yle = self.y[self.ile]
        return self._yle

    def calc_alrad_chord(self) -> None:
        dx = self.xte - self.xle
        dy = self.yte - self.yle
        self._chord = sqrt(dx**2 + dy**2)
        self._alrad = arctan2(dy, dx)

    @property
    def alrad(self) -> float:
        if self._alrad is None:
            self.calc_alrad_chord()
        return self._alrad

    @property
    def chord(self) -> float:
        if self._chord is None:
            self.calc_alrad_chord()
        return self._chord

    @property
    def tte(self) -> float:
        if self._tte is None:
            dx = self.x[-1] - self.x[0]
            dy = self.y[-1] - self.y[0]
            self._tte = sqrt(dx**2 + dy**2)
        return self._tte

    def validate_area(self) -> None:
        xa = self.x[:-1]
        xb = self.x[1:]
        ya = self.y[:-1]
        yb = self.y[1:]
        doubarea = xb*ya - xa*yb
        xa = self.x[-1]
        xb = self.x[0]
        ya = self.y[-1]
        yb = self.y[0]
        doubarea = doubarea.sum() + xb*ya - xa*yb
        if doubarea < 0.0:
            self.reverse()
            self._area = -doubarea/2
        else:
            self._area = doubarea/2

    @property
    def area(self) -> float:
        if self._area is None:
            self.validate_area()
        return self._area

    @property
    def xu(self) -> 'NDArray':
        if self._xu is None:
            self._xu = self.x[self.ile:]
        return self._xu

    @property
    def yu(self) -> 'NDArray':
        if self._yu is None:
            self._yu = self.y[self.ile:]
        return self._yu

    @property
    def xl(self) -> 'NDArray':
        if self._xl is None:
            self._xl = flip(self.x[:self.ile+1])
        return self._xl

    @property
    def yl(self) -> 'NDArray':
        if self._yl is None:
            self._yl = flip(self.y[:self.ile+1])
        return self._yl

    def scale(self, scale: float) -> None:
        self.x = self.x*scale
        self.y = self.y*scale
        self.reset()

    def translate(self, x: float, y: float) -> None:
        self.x = self.x + x
        self.y = self.y + y
        self.reset()

    def rotate(self, angle: float) -> None:
        cosal = cos(angle)
        sinal = sin(angle)
        self.x = self.x*cosal - self.y*sinal
        self.y = self.x*sinal + self.y*cosal
        self.reset()

    def normalise(self) -> None:
        self.translate(-self.xle, -self.yle)
        self.scale(1/self.chord)
        self.rotate(-self.alrad)

    def reverse(self) -> None:
        self.x = self.x[::-1]
        self.y = self.y[::-1]
        self.reset()

    def plot(self, ax: 'Axes' = None) -> 'Axes':
        if ax is None:
            fig = figure()
            ax = fig.gca()
            ax.grid(True)
            ax.set_aspect('equal')
        ax.plot(self.x, self.y, label=self.name)
        return ax

    def __repr__(self) -> str:
        return f'<Airfoil: {self.name:s}>'

    def __str__(self) -> str:
        return f'Airfoil: {self.name:s}'

    @classmethod
    def from_dat(cls, datfilepath: str) -> 'Airfoil':

        name = ''
        x = []
        y = []

        with open(datfilepath, 'rt') as file:
            for i, line in enumerate(file):
                line = line.rstrip('\n')
                if i == 0:
                    name = line.strip()
                else:
                    split = line.split()
                    if len(split) == 2:
                        x.append(float(split[0]))
                        y.append(float(split[1]))

        return cls(name, x, y)
