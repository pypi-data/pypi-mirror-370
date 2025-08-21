from typing import TYPE_CHECKING

from numpy import arccos, asarray, cos, linspace, pi, sin, sqrt

if TYPE_CHECKING:
    from numpy.typing import NDArray


class ChordSpacing():

    s: 'NDArray' = None
    _sqrts: 'NDArray' = None
    _th: 'NDArray' = None
    _cosnth: dict[int, 'NDArray'] = None
    _sinnth: dict[int, 'NDArray'] = None
    _n_sinnth: dict[int, 'NDArray'] = None
    _n_cosnth: dict[int, 'NDArray'] = None
    _n2_sinnth: dict[int, 'NDArray'] = None
    _n2_cosnth: dict[int, 'NDArray'] = None
    _sn: dict[int, 'NDArray'] = None
    _nsnm1: dict[int, 'NDArray'] = None
    _nnm1snm2: dict[int, 'NDArray'] = None

    def __init__(self, s: 'NDArray') -> None:
        s = asarray(s)
        if s.ndim > 1:
            raise ValueError('Spacing array must be a scalar or 1D array.')
        if s.min() < 0.0 or s.max() > 1.0:
            raise ValueError('Spacing values must be between 0.0 and 1.0.')
        self.s = s

    def reset(self) -> None:
        for attr in self.__dict__.keys():
            if attr.startswith('_'):
                setattr(self, attr, None)

    @property
    def size(self) -> int:
        return self.s.size

    @property
    def shape(self) -> int | tuple[int, ...]:
        return self.s.shape

    @property
    def ndim(self) -> int:
        return self.s.ndim

    @classmethod
    def from_th(cls: 'ChordSpacing', th: 'NDArray') -> 'ChordSpacing':
        s = (1.0 - cos(th))/2
        return cls(s)

    @classmethod
    def from_x_and_c(cls, x: 'NDArray', c: float = 1.0) -> 'ChordSpacing':
        return cls(x/c)

    @classmethod
    def from_num(cls, num: int = 100) -> 'ChordSpacing':
        th = linspace(0.0, pi, num)
        return ChordSpacing.from_th(th)

    @property
    def sqrts(self) -> 'NDArray':
        if self._sqrts is None:
            self._sqrts = sqrt(self.s)
        return self._sqrts

    @property
    def th(self) -> 'NDArray':
        if self._th is None:
            self._th = arccos(1.0 - 2*self.s)
        return self._th

    def cosnth(self, n: int) -> 'NDArray':
        if self._cosnth is None:
            self._cosnth = {}
        if n not in self._cosnth:
            self._cosnth[n] = cos(n*self.th)
        return self._cosnth[n]

    def sinnth(self, n: int) -> 'NDArray':
        if self._sinnth is None:
            self._sinnth = {}
        if n not in self._sinnth:
            self._sinnth[n] = sin(n*self.th)
        return self._sinnth[n]

    @property
    def costh(self) -> 'NDArray':
        return self.cosnth(1)

    @property
    def sinth(self) -> 'NDArray':
        return self.sinnth(1)

    def n_cosnth(self, n: int) -> 'NDArray':
        if self._n_cosnth is None:
            self._n_cosnth = {}
        if n not in self._n_cosnth:
            self._n_cosnth[n] = n*self.cosnth(n)
        return self._n_cosnth[n]

    def n_sinnth(self, n: int) -> 'NDArray':
        if self._n_sinnth is None:
            self._n_sinnth = {}
        if n not in self._n_sinnth:
            self._n_sinnth[n] = n*self.sinnth(n)
        return self._n_sinnth[n]

    def n2_cosnth(self, n: int) -> 'NDArray':
        if self._n2_cosnth is None:
            self._n2_cosnth = {}
        if n not in self._n2_cosnth:
            self._n2_cosnth[n] = n*self.n_cosnth(n)
        return self._n2_cosnth[n]

    def n2_sinnth(self, n: int) -> 'NDArray':
        if self._n2_sinnth is None:
            self._n2_sinnth = {}
        if n not in self._n2_sinnth:
            self._n2_sinnth[n] = n*self.n_sinnth(n)
        return self._n2_sinnth[n]

    def sn(self, n: int) -> 'NDArray':
        if self._sn is None:
            self._sn = {}
        if n not in self._sn:
            self._sn[n] = self.s**n
        return self._sn[n]

    def nsnm1(self, n: int) -> 'NDArray':
        if self._nsnm1 is None:
            self._nsnm1 = {}
        if n not in self._nsnm1:
            self._nsnm1[n] = n*self.sn(n - 1)
        return self._nsnm1[n]

    def nnm1snm2(self, n: int) -> 'NDArray':
        if self._nnm1snm2 is None:
            self._nnm1snm2 = {}
        if n not in self._nnm1snm2:
            self._nnm1snm2[n] = n*self.nsnm1(n - 1)
        return self._nnm1snm2[n]

    def __repr__(self):
        return f'ChordSpacing({self.s})'
