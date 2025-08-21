from typing import TYPE_CHECKING

from matplotlib.pyplot import figure
from numpy import (arctan, cos, cumsum, flip, multiply, pi, sin, sqrt, square,
                   zeros)
from pygeom.tools.spacing import (equal_spacing, full_cosine_spacing,
                                  linear_bias_left)

if TYPE_CHECKING:
    from numpy.typing import NDArray
    from matplotlib.axes import Axes


class NACA4():
    code: str = None
    cnum: int = None
    cspc: str = None
    teclosed: bool = None
    _name: str = None
    _mt: float = None
    _mc: float = None
    _pc: float = None
    _cdst: 'NDArray' = None
    _xc: 'NDArray' = None
    _indpc: int = None
    _xcfwd: 'NDArray' = None
    _xcaft: 'NDArray' = None
    _yc: 'NDArray' = None
    _dydx: 'NDArray' = None
    _thc: 'NDArray' = None
    _sc: 'NDArray' = None
    _t: 'NDArray' = None
    _dtdx: 'NDArray' = None
    _tht: 'NDArray' = None
    _xu: 'NDArray' = None
    _yu: 'NDArray' = None
    _thu: 'NDArray' = None
    _xl: 'NDArray' = None
    _yl: 'NDArray' = None
    _thl: 'NDArray' = None
    _x: 'NDArray' = None
    _y: 'NDArray' = None
    _s: 'NDArray' = None
    _th: 'NDArray' = None

    def __init__(self, code: str, teclosed: bool = False,
                 cnum: int = 80) -> None:
        self.code = code
        self.teclosed = teclosed
        self.update(cnum)

    def update(self, cnum: int, cspc: str = 'full-cosine') -> None:
        self.cnum = cnum
        self.cspc = cspc
        self.reset()

    def reset(self) -> None:
        for attr in self.__dict__:
            if attr[0] == '_':
                self.__dict__[attr] = None

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = f'NACA {self.code:s}'
        return self._name

    @property
    def mt(self) -> float:
        if self._mt is None:
            self._mt = float(self.code[2])/10+float(self.code[3])/100
        return self._mt

    @property
    def mc(self) -> float:
        if self._mc is None:
            self._mc = float(self.code[0])/100
        return self._mc

    @property
    def pc(self) -> float:
        if self._pc is None:
            self._pc = float(self.code[1])/10
        return self._pc

    @property
    def cdst(self) -> 'NDArray':
        if self._cdst is None:
            if self.cspc == 'full-cosine':
                self._cdst = full_cosine_spacing(self.cnum)
            elif self.cspc == 'equal':
                self._cdst = equal_spacing(self.cnum)
            else:
                raise ValueError('Incorrect distribution on NACA4')
        return self._cdst

    @property
    def xc(self) -> 'NDArray':
        if self._xc is None:
            self._xc = linear_bias_left(self.cdst, 0.2)
            self._xc = linear_bias_left(self.cdst, 1.0)
        return self._xc

    @property
    def indpc(self) -> int:
        if self._indpc is None:
            for i, xi in enumerate(self.xc):
                if xi > self.pc:
                    self._indpc = i
                    break
        return self._indpc

    @property
    def xcfwd(self) -> 'NDArray':
        if self._xcfwd is None:
            self._xcfwd = self.xc[:self.indpc]
        return self._xcfwd

    @property
    def xcaft(self) -> 'NDArray':
        if self._xcaft is None:
            self._xcaft = self.xc[self.indpc:]
        return self._xcaft

    @property
    def yc(self) -> 'NDArray':
        if self._yc is None:
            self._yc = zeros(self.cnum+1)
            if self.mc != 0.0:
                xcfwd2 = square(self.xcfwd)
                Cfwd = self.mc/self.pc**2
                self._yc[:self.indpc] = Cfwd*(2*self.pc*self.xcfwd-xcfwd2)
                xcaft2 = square(self.xcaft)
                Caft = self.mc/(1-self.pc)**2
                self._yc[self.indpc:] = Caft*((1-2*self.pc)+2*self.pc*self.xcaft-xcaft2)
        return self._yc

    @property
    def dydx(self) -> 'NDArray':
        if self._dydx is None:
            self._dydx = zeros(self.cnum+1)
            if self.mc != 0.0:
                Cfwd = self.mc/self.pc**2
                self._dydx[:self.indpc] = Cfwd*(2*self.pc-2*self.xcfwd)
                Caft = self.mc/(1-self.pc)**2
                self._dydx[self.indpc:] = Caft*(2*self.pc-2*self.xcaft)
        return self._dydx

    @property
    def thc(self) -> 'NDArray':
        if self._thc is None:
            self._thc = arctan(self.dydx)
        return self._thc

    @property
    def sc(self) -> 'NDArray':
        if self._sc is None:
            self._sc = zeros(self.cnum+1)
            dx = self.xc[1:] - self.xc[:-1]
            dy = self.yc[1:] - self.yc[:-1]
            ds = sqrt(square(dx) + square(dy))
            self._sc[1:] = cumsum(ds)
        return self._sc

    @property
    def t(self) -> 'NDArray':
        if self._t is None:
            xi = self.xc
            xi2 = square(xi)
            xi3 = multiply(xi, xi2)
            xi4 = square(xi2)
            ft = 1.4845*sqrt(xi)
            if self.teclosed:
                self._t = self.mt*(ft-0.63*xi-1.758*xi2+1.4215*xi3-0.518*xi4)
            else:
                self._t = self.mt*(ft-0.63*xi-1.758*xi2+1.4215*xi3-0.5075*xi4)
        return self._t

    @property
    def dtdx(self) -> 'NDArray':
        if self._dtdx is None:
            xi = self.xc[1:]
            xi2 = square(xi)
            xi3 = multiply(xi, xi2)
            self._dtdx = zeros(self.cnum+1)
            ft = 0.74225/sqrt(xi)
            if self.teclosed:
                self._dtdx[1:] = self.mt*(ft-0.63-3.516*xi+4.2645*xi2-2.072*xi3)
            else:
                self._dtdx[1:] = self.mt*(ft-0.63-3.516*xi+4.2645*xi2-2.03*xi3)
        return self._dtdx

    @property
    def tht(self) -> 'NDArray':
        if self._tht is None:
            self._tht = zeros(self.cnum+1)
            self._tht[0] = pi/2
            self._tht[1:] = arctan(self.dtdx[1:])
        return self._tht

    @property
    def xu(self) -> 'NDArray':
        if self._xu is None:
            self._xu = self.xc - multiply(self.t, sin(self.thc))
        return self._xu

    @property
    def yu(self) -> 'NDArray':
        if self._yu is None:
            self._yu = self.yc + multiply(self.t, cos(self.thc))
        return self._yu

    @property
    def thu(self) -> 'NDArray':
        if self._thu is None:
            self._thu = self.thc + self.tht
        return self._thu

    @property
    def xl(self) -> 'NDArray':
        if self._xl is None:
            self._xl = self.xc + multiply(self.t, sin(self.thc))
        return self._xl

    @property
    def yl(self) -> 'NDArray':
        if self._yl is None:
            self._yl = self.yc - multiply(self.t, cos(self.thc))
        return self._yl

    @property
    def thl(self) -> 'NDArray':
        if self._thl is None:
            self._thl = self.thc - self.tht
        return self._thl

    @property
    def x(self) -> 'NDArray':
        if self._x is None:
            self._x = zeros(2*self.cnum+1)
            self._x[:self.cnum+1] = flip(self.xl)
            self._x[self.cnum+1:] = self.xu[1:]
        return self._x

    @property
    def y(self) -> 'NDArray':
        if self._y is None:
            self._y = zeros(2*self.cnum+1)
            self._y[:self.cnum+1] = flip(self.yl)
            self._y[self.cnum+1:] = self.yu[1:]
        return self._y

    @property
    def th(self) -> 'NDArray':
        if self._th is None:
            self._th = zeros(2*self.cnum+1)
            self._th[:self.cnum+1] = flip(self.thl)-pi
            self._th[self.cnum+1:] = self.thu[1:]
        return self._th

    @property
    def s(self) -> 'NDArray':
        if self._s is None:
            self._s = zeros(2*self.cnum+1)
            dx = self.x[1:] - self.x[:-1]
            dy = self.y[1:] - self.y[:-1]
            ds = sqrt(square(dx) + square(dy))
            self._s[1:] = cumsum(ds)
        return self._s

    def plot_airfoil(self, ax: 'Axes' = None, figsize=(10, 8), **kwargs) -> 'Axes':
        if ax is None:
            fig = figure(figsize=figsize)
            ax = fig.gca()
            ax.grid(True)
            ax.set_aspect('equal')
        ax.plot(self.x, self.y, label=f'NACA {self.code:s}', **kwargs)
        return ax

    def plot_camber(self, ax: 'Axes' = None, figsize=(10, 8), **kwargs) -> 'Axes':
        if ax is None:
            fig = figure(figsize=figsize)
            ax = fig.gca()
            ax.grid(True)
            ax.set_aspect('equal')
        ax.plot(self.xc, self.yc, label=f'NACA {self.code:s}', **kwargs)
        return ax

    def fill_airfoil(self, ax: 'Axes' = None, figsize=(10, 8), **kwargs) -> 'Axes':
        if ax is None:
            fig = figure(figsize=figsize)
            ax = fig.gca()
            ax.grid(True)
            ax.set_aspect('equal')
        ax.fill(self.x, self.y, label=f'NACA {self.code:s}', **kwargs)
        return ax

    def __repr__(self) -> str:
        return f'<NACA {self.code:s}>'

    def __str__(self) -> str:
        return f'NACA {self.code:s}'
