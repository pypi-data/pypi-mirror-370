from json import dump, load
from typing import TYPE_CHECKING, Any

from matplotlib.pyplot import figure
from numpy import (absolute, arctan, argwhere, asarray, concatenate, cumsum,
                   degrees, diag, divide, full, hstack, logical_and,
                   logical_or, split, sqrt, vstack, zeros)
from numpy.linalg import norm
from py2md.classes import MDReport
from pygeom.tools.solvers import solve_clsq

from ..airfoil import Airfoil
from .chordspacing import ChordSpacing

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from numpy.typing import NDArray


class AirfoilPoly():
    name: str = None
    Cn: 'NDArray' = None
    Tn: 'NDArray' = None
    c: float = None
    num: int = None
    _spacing: ChordSpacing = None
    _Nc: int = None
    _Nt: int = None
    _xc: 'NDArray' = None
    _yc: 'NDArray' = None
    _my: 'NDArray' = None
    _dmyds: 'NDArray' = None
    _tc: 'NDArray' = None
    _mt: 'NDArray' = None
    _dmtds: 'NDArray' = None
    _At: 'NDArray' = None
    _St: 'NDArray' = None
    _cc: 'NDArray' = None
    _sc: 'NDArray' = None
    _xu: 'NDArray' = None
    _yu: 'NDArray' = None
    _xl: 'NDArray' = None
    _yl: 'NDArray' = None
    _x: 'NDArray' = None
    _y: 'NDArray' = None
    _max_tc: float = None
    _max_tc_pc: float = None
    _max_yc: float = None
    _max_yc_pc: float = None
    _spc_le: ChordSpacing = None
    _spc_te: ChordSpacing = None
    _yc_le: float = None
    _yc_te: float = None
    _tc_te: float = None
    _thy_le: float = None
    _thy_te: float = None
    _tht_te: float = None

    def __init__(self, name: str, Cn: 'NDArray', Tn: 'NDArray',
                 c: float = 1.0, num: int = 101) -> None:
        self.name = name
        self.Cn = Cn
        self.Tn = Tn
        self.c = c
        self.num = num

    def reset(self) -> None:
        for attr in self.__dict__.keys():
            if attr.startswith('_'):
                setattr(self, attr, None)

    def set_chord(self, c: float) -> None:
        self.c = c

    @classmethod
    def from_dict(cls, dict_obj: dict[str, Any]) -> 'AirfoilPoly':
        name = dict_obj['name']
        Cn = asarray(dict_obj['Cn'])
        Tn = asarray(dict_obj['Tn'])
        c = dict_obj['c']
        num = dict_obj['num']
        return cls(name, Cn, Tn, c, num)

    def to_dict(self) -> dict[str, Any]:
        dict_obj = {}
        dict_obj['name'] = self.name
        dict_obj['Cn'] = self.Cn.tolist()
        dict_obj['Tn'] = self.Tn.tolist()
        dict_obj['c'] = self.c
        dict_obj['num'] = self.num
        return dict_obj

    @classmethod
    def from_json(cls, filename: str) -> 'AirfoilPoly':
        with open(filename, 'r') as f:
            dict_obj = load(f)
        return cls.from_dict(dict_obj)

    def to_json(self, filename: str) -> None:
        with open(filename, 'w') as f:
            dump(self.to_dict(), f, indent=4)

    def set_yte(self, yte: float, ind: int = 1) -> None:
        if ind <= 0:
            raise ValueError('Specified ind must be greater than 0.')
        elif self.Cn.size < 2:
            return
        elif self.Cn.size <= ind:
            raise IndexError(f'Specified ind={ind:d} does not exist in Cn.')
        cur_yte = self.calc_yc(ChordSpacing(1.0), self.Cn)
        Cn = zeros(self.Cn.size)
        Cn[ind] = 1.0
        dytedCn = self.calc_dycdCn(ChordSpacing(1.0), Cn)
        dytedCn = dytedCn.item()
        diff_yte = yte - cur_yte
        dCn = diff_yte/dytedCn
        Cn = self.Cn.copy()
        Cn[ind] += dCn
        self.Cn = Cn
        self.reset()

    def set_tte(self, tte: float, ind: int = 2) -> None:
        if ind <= 0:
            raise ValueError('Specified ind must be greater than 0.')
        elif self.Tn.size < 3:
            raise IndexError('AirfoilPoly Tn attribute needs size >= 3.')
        elif self.Tn.size <= ind:
            raise IndexError(f'Specified ind={ind:d} does not exist in Tn.')
        cur_tte = self.calc_tc(ChordSpacing(1.0), self.Tn)
        Tn = zeros(self.Tn.size)
        Tn[ind] = 1.0
        dttedTn = self.calc_dtcdTn(ChordSpacing(1.0), Tn)
        dttedTn = dttedTn.item()
        diff_tte = tte - cur_tte
        dTn = diff_tte/dttedTn
        Tn = self.Tn.copy()
        Tn[ind] += dTn
        self.Tn = Tn
        self.reset()

    @property
    def spacing(self) -> ChordSpacing:
        if self._spacing is None:
            self._spacing = ChordSpacing.from_num(self.num)
        return self._spacing

    @property
    def Nc(self) -> int:
        if self._Nc is None:
            self._Nc = self.Cn.size
        return self._Nc

    @property
    def Nt(self) -> int:
        if self._Nt is None:
            self._Nt = self.Tn.size
        return self._Nt

    @property
    def th(self) -> 'NDArray':
        return self.spacing.th

    def calc_xc(self, spc: ChordSpacing) -> 'NDArray':
        xc = self.c*spc.s
        return xc

    @property
    def xc(self) -> 'NDArray':
        if self._xc is None:
            self._xc = self.calc_xc(self.spacing)
        return self._xc

    def calc_dxcds(self, spc: ChordSpacing) -> 'NDArray':
        dxcds = full(spc.s.shape, self.c)
        return dxcds

    def calc_dycdCn(self, spc: ChordSpacing, Cn: 'NDArray' = None) -> 'NDArray':
        dycdCn = zeros((*spc.shape, self.Nc))
        for n in range(self.Nc):
            dycdCn[..., n] = self.c*spc.sn(n)
        if Cn is not None:
            ind_Cn_not0 = argwhere(Cn != 0.0).flatten()
            dycdCn = dycdCn[..., ind_Cn_not0]@Cn[ind_Cn_not0]
        return dycdCn

    def calc_yc(self, spc: ChordSpacing, Cn: 'NDArray') -> 'NDArray':
        yc = self.calc_dycdCn(spc, Cn)
        return yc

    @property
    def yc(self) -> 'NDArray':
        if self._yc is None:
            self._yc = self.calc_yc(self.spacing, self.Cn)
        return self._yc

    def calc_dmydCn(self, spc: ChordSpacing, Cn: 'NDArray' = None) -> 'NDArray':
        dmydCn = zeros((*spc.shape, self.Nc))
        for n in range(self.Nc):
            if n >= 1:
                dmydCn[..., n] = spc.nsnm1(n)
        if Cn is not None:
            ind_Cn_not0 = argwhere(Cn != 0.0).flatten()
            dmydCn = dmydCn[..., ind_Cn_not0]@Cn[ind_Cn_not0]
        return dmydCn

    def calc_my(self, spc: ChordSpacing, Cn: 'NDArray') -> 'NDArray':
        my = self.calc_dmydCn(spc, Cn)
        return my

    @property
    def my(self) -> 'NDArray':
        if self._my is None:
            self._my = self.calc_my(self.spacing, self.Cn)
        return self._my

    def calc_dycds(self, spc: ChordSpacing, Cn: 'NDArray') -> 'NDArray':
        dycdxc = self.calc_my(spc, Cn)
        dxcds = self.calc_dxcds(spc)
        dycds = dycdxc*dxcds
        return dycds

    def calc_d2mydsdCn(self, spc: ChordSpacing, Cn: 'NDArray' = None) -> 'NDArray':
        d2mydsdCn = zeros((*spc.shape, self.Nc))
        for n in range(self.Nc):
            if n >= 2:
                d2mydsdCn[..., n] = spc.nnm1snm2(n)
        if Cn is not None:
            ind_Cn_not0 = argwhere(Cn != 0.0).flatten()
            d2mydsdCn = d2mydsdCn[..., ind_Cn_not0]@Cn[ind_Cn_not0]
        return d2mydsdCn

    def calc_dmyds(self, spc: ChordSpacing, Cn: 'NDArray') -> 'NDArray':
        dmyds = self.calc_d2mydsdCn(spc, Cn)
        return dmyds

    @property
    def dmyds(self) -> 'NDArray':
        if self._dmyds is None:
            self._dmyds = self.calc_dmyds(self.spacing, self.Cn)
        return self._dmyds

    def calc_dtcdTn(self, spc: ChordSpacing, Tn: 'NDArray' = None) -> 'NDArray':
        dtcdTn = zeros((*spc.shape, self.Nt))
        for n in range(self.Nt):
            if n == 0:
                dtcdTn[..., n] = self.c*spc.sqrts
            else:
                dtcdTn[..., n] = self.c*spc.sn(n)
        if Tn is not None:
            ind_Tn_not0 = argwhere(Tn != 0.0).flatten()
            dtcdTn = dtcdTn[..., ind_Tn_not0]@Tn[ind_Tn_not0]
        return dtcdTn

    def calc_tc(self, spc: ChordSpacing, Tn: 'NDArray') -> 'NDArray':
        tc = self.calc_dtcdTn(spc, Tn)
        return tc

    @property
    def tc(self) -> 'NDArray':
        if self._tc is None:
            self._tc = self.calc_tc(self.spacing, self.Tn)
        return self._tc

    def calc_dmtdTn(self, spc: ChordSpacing, Tn: 'NDArray' = None) -> 'NDArray':
        dmtdTn = zeros((*spc.shape, self.Nt))
        for n in range(self.Nt):
            if n == 0:
                mt0 = zeros(spc.shape)
                divide(0.5, spc.sqrts, out = mt0, where=spc.sqrts != 0.0)
                mt0[spc.s == 0.0] = float('inf')
                dmtdTn[..., n] += mt0
            else:
                dmtdTn[..., n] += spc.nsnm1(n)
        if Tn is not None:
            ind_Tn_not0 = argwhere(Tn != 0.0).flatten()
            dmtdTn = dmtdTn[..., ind_Tn_not0]@Tn[ind_Tn_not0]
        return dmtdTn

    def calc_mt(self, spc: ChordSpacing, Tn: 'NDArray') -> 'NDArray':
        mt = self.calc_dmtdTn(spc, Tn)
        return mt

    @property
    def mt(self) -> 'NDArray':
        if self._mt is None:
            self._mt = self.calc_mt(self.spacing, self.Tn)
        return self._mt

    def calc_dtcds(self, spc: ChordSpacing, Tn: 'NDArray') -> 'NDArray':
        dtcdxc = self.calc_mt(spc, Tn)
        dxcds = self.calc_dxcds(spc)
        dtcds = dtcdxc*dxcds
        return dtcds

    def calc_d2mtdsdTn(self, spc: ChordSpacing, Tn: 'NDArray' = None) -> 'NDArray':
        d2mtdsdTn = zeros((*spc.shape, self.Nt))
        for n in range(self.Nt):
            if n == 0:
                dmtds0 = zeros(spc.shape)
                divide(-0.25, spc.sqrts**3, out=dmtds0, where=spc.sqrts != 0.0)
                dmtds0[spc.s == 0.0] = float('-inf')
                d2mtdsdTn[..., n] += dmtds0
            elif n >= 2:
                d2mtdsdTn[..., n] = spc.nnm1snm2(n)
        if Tn is not None:
            ind_Tn_not0 = argwhere(Tn != 0.0).flatten()
            d2mtdsdTn = d2mtdsdTn[..., ind_Tn_not0]@Tn[ind_Tn_not0]
        return d2mtdsdTn

    def calc_dmtds(self, spc: ChordSpacing, Tn: 'NDArray') -> 'NDArray':
        dmtds = self.calc_d2mtdsdTn(spc, Tn)
        return dmtds

    @property
    def dmtds(self) -> 'NDArray':
        if self._dmtds is None:
            self._dmtds = self.calc_dmtds(self.spacing, self.Tn)
        return self._dmtds

    def calc_dAtdTn(self, spc: ChordSpacing, Tn: 'NDArray' = None) -> 'NDArray':
        dAtdTn = zeros((*spc.shape, self.Nt))
        for n in range(self.Nt):
            if n == 0:
                dAtdTn[..., n] = self.c*2.0*spc.sqrts**3/3.0
            else:
                dAtdTn[..., n] = self.c*spc.sn(n + 1)/(n + 1)
        if Tn is not None:
            ind_Tn_not0 = argwhere(Tn != 0.0).flatten()
            dAtdTn = dAtdTn[..., ind_Tn_not0]@Tn[ind_Tn_not0]
        return dAtdTn

    def calc_At(self, spc: ChordSpacing, Tn: 'NDArray') -> 'NDArray':
        At = self.calc_dAtdTn(spc, Tn)
        return At

    @property
    def At(self) -> 'NDArray':
        if self._At is None:
            self._At = self.calc_At(self.spacing, self.Tn)
        return self._At

    @property
    def St(self) -> 'NDArray':
        if self._St is None:
            x = self.spacing.s
            y = self.tc/2
            dx = x[1:] - x[:-1]
            dy = y[1:] - y[:-1]
            ds = sqrt(dx**2 + dy**2)
            self._St = zeros(self.spacing.s.size)
            self._St[1:] = cumsum(ds)
        return self._St

    @property
    def cc(self) -> 'NDArray':
        if self._cc is None:
            self._cc = 1.0/sqrt(1.0 + self.my**2)
        return self._cc

    @property
    def sc(self) -> 'NDArray':
        if self._sc is None:
            self._sc = self.my*self.cc
        return self._sc

    @property
    def xu(self) -> 'NDArray':
        if self._xu is None:
            self._xu = self.xc - self.tc*self.sc/2
        return self._xu

    @property
    def yu(self) -> 'NDArray':
        if self._yu is None:
            self._yu = self.yc + self.tc*self.cc/2
        return self._yu

    @property
    def xl(self) -> 'NDArray':
        if self._xl is None:
            if self.Nc == 0:
                self._xl = self.xu
            else:
                self._xl = self.xc + self.tc*self.sc/2
        return self._xl

    @property
    def yl(self) -> 'NDArray':
        if self._yl is None:
            if self.Nc == 0:
                self._yl = -self.yu
            else:
                self._yl = self.yc - self.tc*self.cc/2
        return self._yl

    @property
    def x(self) -> 'NDArray':
        if self._x is None:
            self._x = hstack((self.xl[::-1], self.xu[1:]))
        return self._x

    @property
    def y(self) -> 'NDArray':
        if self._y is None:
            self._y = hstack((self.yl[::-1], self.yu[1:]))
        return self._y

    def calc_max_tc_guess(self) -> tuple[float, float]:
        spacing = ChordSpacing.from_num(1001)
        mt = self.calc_mt(spacing, self.Tn)
        chk1 = logical_and(mt[:-1] <= 0.0, mt[1:] >= 0.0)
        chk2 = logical_and(mt[:-1] >= 0.0, mt[1:] <= 0.0)
        chk = logical_or(chk1, chk2)
        ind = argwhere(chk).flatten()
        tc = self.calc_tc(spacing, self.Tn)
        max_tcs = tc[ind]
        max_tc = max_tcs.max()
        ind_max_tc = argwhere(tc == max_tc).flatten()
        max_tc_pc = spacing.s[ind_max_tc].item()
        return max_tc_pc, max_tc

    def calc_max_tc_result(self) -> tuple[float, float]:
        s_cur, _ = self.calc_max_tc_guess()
        spacing = ChordSpacing(s_cur)
        mt = self.calc_mt(spacing, self.Tn)
        count = 0
        while abs(mt) > 1e-12:
            dmtds = self.calc_dmtds(spacing, self.Tn)
            s_cur -= mt/dmtds
            spacing = ChordSpacing(s_cur)
            mt = self.calc_mt(spacing, self.Tn)
            count += 1
            if count > 100:
                raise ValueError('Failed to converge max thickness.')
        tc = self.calc_tc(spacing, self.Tn)
        tc = tc.item()
        return s_cur, tc

    @property
    def max_tc(self) -> float:
        if self._max_tc is None:
            self._max_tc_pc, self._max_tc = self.calc_max_tc_result()
        return self._max_tc

    @property
    def max_tc_pc(self) -> float:
        if self._max_tc_pc is None:
            self._max_tc_pc, self._max_tc = self.calc_max_tc_result()
        return self._max_tc_pc

    def calc_max_yc_guess(self) -> tuple[float, float]:
        spacing = ChordSpacing.from_num(1001)
        my = self.calc_my(spacing, self.Cn)
        chk1 = logical_and(my[:-1] <= 0.0, my[1:] >= 0.0)
        chk2 = logical_and(my[:-1] >= 0.0, my[1:] <= 0.0)
        chk = logical_or(chk1, chk2)
        ind = argwhere(chk).flatten()
        yc = self.calc_yc(spacing, self.Cn)
        max_ycs = yc[ind]
        max_yc = max_ycs.max()
        ind_max_yc = argwhere(yc == max_yc).flatten()
        max_yc_pc = spacing.s[ind_max_yc].item()
        return max_yc_pc, max_yc

    def calc_max_yc_result(self) -> tuple[float, float]:
        s_cur, _ = self.calc_max_yc_guess()
        spacing = ChordSpacing(s_cur)
        my = self.calc_my(spacing, self.Cn)
        count = 0
        while abs(my) > 1e-12:
            dmyds = self.calc_dmyds(spacing, self.Cn)
            s_cur -= my/dmyds
            spacing = ChordSpacing(s_cur)
            my = self.calc_my(spacing, self.Cn)
            count += 1
            if count > 100:
                raise ValueError('Failed to converge max camber.')
        yc = self.calc_yc(spacing, self.Cn)
        yc = yc.item()
        return s_cur, yc

    @property
    def max_yc(self) -> float:
        if self._max_yc is None:
            self._max_yc_pc, self._max_yc = self.calc_max_yc_result()
        return self._max_yc

    @property
    def max_yc_pc(self) -> float:
        if self._max_yc_pc is None:
            self._max_yc_pc, self._max_yc = self.calc_max_yc_result()
        return self._max_yc_pc

    @property
    def spc_le(self) -> ChordSpacing:
        if self._spc_le is None:
            self._spc_le = ChordSpacing(0.0)
        return self._spc_le

    @property
    def spc_te(self) -> ChordSpacing:
        if self._spc_te is None:
            self._spc_te = ChordSpacing(1.0)
        return self._spc_te

    @property
    def yc_le(self) -> float:
        if self._yc_le is None:
            self._yc_le = self.calc_yc(self.spc_le, self.Cn)
        return self._yc_le

    @property
    def yc_te(self) -> float:
        if self._yc_te is None:
            self._yc_te = self.calc_yc(self.spc_te, self.Cn)
        return self._yc_te

    @property
    def tc_te(self) -> float:
        if self._tc_te is None:
            self._tc_te = self.calc_tc(self.spc_te, self.Tn)
        return self._tc_te

    @property
    def thy_le(self) -> float:
        if self._thy_le is None:
            self._thy_le = arctan(self.calc_my(self.spc_le, self.Cn))
        return self._thy_le

    @property
    def thy_te(self) -> float:
        if self._thy_te is None:
            self._thy_te = arctan(self.calc_my(self.spc_te, self.Cn))
        return self._thy_te

    @property
    def tht_te(self) -> float:
        if self._tht_te is None:
            self._tht_te = arctan(self.calc_mt(self.spc_te, self.Tn))
        return self._tht_te

    def plot_camber(self, ax: 'Axes' = None, vs_th: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            ax.set_aspect('equal')
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            ax.set_ylabel(r'$y_c$')
        if vs_th:
            ax.plot(self.th, self.yc, label=self.name)
        else:
            ax.plot(self.xc, self.yc, label=self.name)
        return ax

    def plot_camber_derivative(self, ax: 'Axes' = None, vs_th: bool = False,
                               as_angle: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            if as_angle:
                ax.set_ylabel(r'$\arctan{\frac{dy_c}{dx}}$ ($\degree$)')
            else:
                ax.set_ylabel(r'$\frac{dy_c}{dx}$')
        if as_angle:
            my = degrees(arctan(self.my))
        if vs_th:
            ax.plot(self.th, my, label=self.name)
        else:
            ax.plot(self.xc, my, label=self.name)
        return ax

    def plot_camber_curvature(self, ax: 'Axes' = None, vs_th: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            ax.set_ylabel(r'$\frac{dm_y}{ds}$')
        if vs_th:
            ax.plot(self.th, self.dmyds, label=self.name)
        else:
            ax.plot(self.xc, self.dmyds, label=self.name)
        return ax

    def plot_thickness(self, ax: 'Axes' = None, vs_th: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            ax.set_aspect('equal')
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            ax.set_ylabel(r'$t_c$')
        if vs_th:
            ax.plot(self.th, self.tc, label=self.name)
        else:
            ax.plot(self.xc, self.tc, label=self.name)
        return ax

    def plot_thickness_derivative(self, ax: 'Axes' = None, vs_th: bool = False,
                                  as_angle: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            if as_angle:
                ax.set_ylabel(r'$\arctan{\frac{dt_c}{dx}}$ ($\degree$)')
            else:
                ax.set_ylabel(r'$\frac{dt_c}{dx}$')
        mt = self.mt
        if as_angle:
            mt = degrees(arctan(mt))
        if vs_th:
            ax.plot(self.th, mt, label=self.name)
        else:
            ax.plot(self.xc, mt, label=self.name)
        return ax

    def plot_thickness_curvature(self, ax: 'Axes' = None, vs_th: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            ax.set_ylabel(r'$\frac{dm_t}{ds}$')
        if vs_th:
            ax.plot(self.th, self.dmtds, label=self.name)
        else:
            ax.plot(self.xc, self.dmtds, label=self.name)
        return ax

    def plot_thickness_area(self, ax: 'Axes' = None, vs_th: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            ax.set_ylabel(r'$A_c$')
        if vs_th:
            ax.plot(self.th, self.At, label=self.name)
        else:
            ax.plot(self.xc, self.At, label=self.name)
        return ax

    def plot_thickness_length(self, ax: 'Axes' = None, vs_th: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            ax.set_ylabel(r'$S_c$')
        if vs_th:
            ax.plot(self.th, self.St, label=self.name)
        else:
            ax.plot(self.xc, self.St, label=self.name)
        return ax

    def plot_shape(self, ax: 'Axes' = None, **kwargs: dict[str, Any]) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            ax.set_aspect('equal')
            ax.set_xlabel(r'$x$')
            ax.set_ylabel(r'$y$')

        kwargs.setdefault('label', self.name)

        ax.plot(self.x, self.y, **kwargs)
        return ax

    def __repr__(self) -> str:
        return f'<AirfoilPoly: {self.name:s}>'

    def to_mdobj(self) -> MDReport:
        report = MDReport()
        report.add_heading(f'Airfoil Shape: {self.name:s}', level=1)
        table = report.add_table()
        if self.Cn.size > 0:
            table.add_column('Leading Edge Camber %', '.3f', data=[self.yc_le/self.c])
            table.add_column('Trailing Edge Camber %', '.3f', data=[self.yc_te/self.c])
            table.add_column('Max Camber %', '.3f', data=[self.max_yc/self.c*100])
            table.add_column('Max Camber Position %', '.3f', data=[self.max_yc_pc*100])
            table.add_column('Leading Edge Angle (deg)', '.3f', data=[degrees(self.thy_le)])
            table.add_column('Trailing Edge Angle (deg)', '.3f', data=[degrees(self.thy_te)])
        table = report.add_table()
        if self.Tn.size > 0:
            table.add_column('Trailing Edge Thickness %', '.3f', data=[self.tc_te/self.c])
            table.add_column('Max Thickness %', '.3f', data=[self.max_tc/self.c*100])
            table.add_column('Max Thickness Position %', '.3f', data=[self.max_tc_pc*100])
            table.add_column('Trailing Edge Angle (deg)', '.3f', data=[degrees(self.tht_te)])
        return report

    def _repr_markdown_(self) -> str:
        return self.to_mdobj()._repr_markdown_()

    def __str__(self) -> str:
        return f'AirfoilPoly: {self.name:s}\nCn = \n{self.Cn}\nTn = \n{self.Tn}'

class AirfoilPolyFit():
    airfoil: Airfoil = None
    Ncs: int = None
    Nts: int = None
    Ry: list[tuple[int, float, float]] = None
    Rt: list[tuple[int, float, float]] = None
    yte: float = None
    tte: float = None
    xu: 'NDArray' = None
    yu: 'NDArray' = None
    xl: 'NDArray' = None
    yl: 'NDArray' = None
    spcu: ChordSpacing = None
    spcl: ChordSpacing = None
    aply: AirfoilPoly = None
    lmda: 'NDArray' = None

    def __init__(self, airfoil: Airfoil, Ncs: int, Nts: int,
                 yte: float = None, tte: float = None) -> None:
        if Ncs == 1:
            raise ValueError('The value of Ncs may not equal 1.')
        self.airfoil = airfoil
        self.Ncs = Ncs
        self.Nts = Nts
        self.yte = yte
        if self.yte is None:
            self.yte = self.airfoil.yte
        self.tte = tte
        if self.tte is None:
            self.tte = self.airfoil.tte
        self.Rt = [(0, 1.0, self.tte)]
        self.Ry = [(0, 0.0, 0.0), (0, 1.0, self.yte)]
        self.validate()

    def validate(self) -> None:
        Nu = self.airfoil.xu.size - 2
        Nl = self.airfoil.xl.size - 2
        Nmin = min(Nu, Nl)
        Nmax = max(Nu, Nl)
        if self.Ncs >= Nmin:
            err = f'The number of camber terms must be less than {Nmin:d} for this airfoil.'
            raise RuntimeError(err)
        if self.Nts >= Nmax:
            err = f'The number of thickness terms must be less than {Nmax:d} for this airfoil.'
            raise RuntimeError(err)

    def add_camber_constraint(self, deriv: int, svalue: float, yvalue: float) -> None:
        if self.Ry is None:
            self.Ry = []
        self.Ry.append((deriv, svalue, yvalue))

    def add_thickness_constraint(self, deriv: int, svalue: float, tvalue: float) -> None:
        if self.Rt is None:
            self.Rt = []
        self.Rt.append((deriv, svalue, tvalue))

    def fit(self) -> float:

        self.xu = self.airfoil.xu[1:-1]
        self.yu = self.airfoil.yu[1:-1]
        self.spcu = ChordSpacing.from_x_and_c(self.xu, self.airfoil.chord)

        self.xl = self.airfoil.xl[1:-1]
        self.yl = self.airfoil.yl[1:-1]
        self.spcl = ChordSpacing.from_x_and_c(self.xl, self.airfoil.chord)

        Cn = zeros(self.Ncs)
        Tn = zeros(self.Nts)

        self.aply = AirfoilPoly(self.airfoil.name, Cn, Tn,
                                self.airfoil.chord)

        dtcdTnu = self.aply.calc_dtcdTn(self.spcu)
        dtcdTnl = self.aply.calc_dtcdTn(self.spcl)
        dycdCnu = self.aply.calc_dycdCn(self.spcu)
        dycdCnl = self.aply.calc_dycdCn(self.spcl)

        dyudvar = hstack((dycdCnu, 0.5*dtcdTnu))
        dyldvar = hstack((dycdCnl, -0.5*dtcdTnl))

        Amat = vstack((dyudvar, dyldvar))

        Bmat = zeros(Amat.shape[0])
        Bmat[:self.yu.size] = self.yu
        Bmat[self.yu.size:] = self.yl

        Clist = []
        Dlist = []

        numt = 0
        for deriv, svalue, tvalue in self.Rt:
            if numt == self.Nts:
                break
            numt += 1
            spct = ChordSpacing(svalue)
            if deriv == 0:
                dtcdCn = zeros((*spct.shape, self.Ncs))
                dtcdTn = self.aply.calc_dtcdTn(spct)
                dtcdvar = hstack((dtcdCn, dtcdTn))
                tc = tvalue
                Clist.append(dtcdvar)
                Dlist.append(tc)
            elif deriv == 1:
                dmtdCn = zeros((*spct.shape, self.Ncs))
                dmtdTn = self.aply.calc_dmtdTn(spct)
                dmtdvar = hstack((dmtdCn, dmtdTn))
                mt = tvalue
                Clist.append(dmtdvar)
                Dlist.append(mt)
            elif deriv == 2:
                d2mtdsdCn = zeros((*spct.shape, self.Ncs))
                d2mtdsdTn = self.aply.calc_d2mtdsdTn(spct)
                d2mtdsdvar = hstack((d2mtdsdCn, d2mtdsdTn))
                dmtds = tvalue
                Clist.append(d2mtdsdvar)
                Dlist.append(dmtds)
            else:
                raise ValueError('Invalid derivative value for thickness constraint.')

        numy = 0
        for deriv, svalue, yvalue in self.Ry:
            if numy == self.Ncs:
                break
            numy += 1
            spcy = ChordSpacing(svalue)
            if deriv == 0:
                dycdCn = self.aply.calc_dycdCn(spcy)
                dycdTn = zeros((*spcy.shape, self.Nts))
                dycdvar = hstack((dycdCn, dycdTn))
                yc = yvalue
                Clist.append(dycdvar)
                Dlist.append(yc)
            elif deriv == 1:
                dmydCn = self.aply.calc_dmydCn(spcy)
                dmydTn = zeros((*spcy.shape, self.Nts))
                dmydvar = hstack((dmydCn, dmydTn))
                my = yvalue
                Clist.append(dmydvar)
                Dlist.append(my)
            elif deriv == 2:
                d2mydsdCn = self.aply.calc_d2mydsdCn(spcy)
                d2mydsdTn = zeros((*spcy.shape, self.Nts))
                d2mydsdvar = hstack((d2mydsdCn, d2mydsdTn))
                dmyds = yvalue
                Clist.append(d2mydsdvar)
                Dlist.append(dmyds)
            else:
                raise ValueError('Invalid derivative value for camber constraint.')

        Cmat = vstack(tuple(Clist))
        Dmat = asarray(Dlist)

        var, self.lmda = solve_clsq(Amat, Bmat, Cmat, Dmat)

        Cn = var[:self.Ncs]
        Tn = var[self.Ncs:]

        self.aply = AirfoilPoly(self.airfoil.name, Cn, Tn,
                                self.airfoil.chord, self.aply.num)

        ycu = self.aply.calc_yc(self.spcu, Cn)
        tcu = self.aply.calc_tc(self.spcu, Tn)
        yu = ycu + 0.5*tcu

        ycl = self.aply.calc_yc(self.spcl, Cn)
        tcl = self.aply.calc_tc(self.spcl, Tn)
        yl = ycl - 0.5*tcl

        Dyu = absolute(yu - self.yu)
        Dyl = absolute(yl - self.yl)

        res = norm(Dyu) + norm(Dyl)

        return res

    def improved_fit(self, display: bool = False) -> tuple[float, float]:

        xup = self.airfoil.xu[1:-1]
        yup = self.airfoil.yu[1:-1]
        xlp = self.airfoil.xl[1:-1]
        ylp = self.airfoil.yl[1:-1]

        Cn = self.aply.Cn.copy()
        Tn = self.aply.Tn.copy()
        su = self.spcu.s.copy()
        sl = self.spcl.s.copy()
        lmda = self.lmda.copy()

        if display:

            print(f'Cn = {Cn}\n')
            print(f'Tn = {Tn}\n')
            print(f'su = {su}\n')
            print(f'sl = {sl}\n')

            print(f'Cn.size = {Cn.size}\n')
            print(f'Tn.size = {Tn.size}\n')
            print(f'su.size = {su.size}\n')
            print(f'sl.size = {sl.size}\n')

        xcu = self.aply.calc_xc(self.spcu)
        dxcdsu = self.aply.calc_dxcds(self.spcu)

        xcl = self.aply.calc_xc(self.spcl)
        dxcdsl = self.aply.calc_dxcds(self.spcl)

        ycu = self.aply.calc_yc(self.spcu, Cn)
        dycdsu = self.aply.calc_dycds(self.spcu, Cn)
        dycdCnu = self.aply.calc_dycdCn(self.spcu)

        ycl = self.aply.calc_yc(self.spcl, Cn)
        dycdsl = self.aply.calc_dycds(self.spcl, Cn)
        dycdCnl = self.aply.calc_dycdCn(self.spcl)

        tcu = self.aply.calc_tc(self.spcu, Tn)
        dtcdsu = self.aply.calc_dtcds(self.spcu, Tn)
        dtcdTnu = self.aply.calc_dtcdTn(self.spcu)

        tcl = self.aply.calc_tc(self.spcl, Tn)
        dtcdsl = self.aply.calc_dtcds(self.spcl, Tn)
        dtcdTnl = self.aply.calc_dtcdTn(self.spcl)

        dmydsu = self.aply.calc_dmyds(self.spcu, Cn)
        dmydCnu = self.aply.calc_dmydCn(self.spcu)

        dmydsl = self.aply.calc_dmyds(self.spcl, Cn)
        dmydCnl = self.aply.calc_dmydCn(self.spcl)

        myu = self.aply.calc_my(self.spcu, Cn)
        myu2 = myu**2
        ccu = 1.0/sqrt(1.0 + myu2)
        scu = myu*ccu

        ccu3 = ccu**3
        myuccu3 = myu*ccu3
        myu2ccu3 = myu*myuccu3

        dscdsu = ccu*dmydsu - myu2ccu3*dmydsu
        dccdsu = -myuccu3*dmydsu

        myl = self.aply.calc_my(self.spcl, Cn)
        myl2 = myl**2
        ccl = 1.0/sqrt(1.0 + myl2)
        scl = myl*ccl

        ccl3 = ccl**3
        mylccl3 = myl*ccl3
        myl2ccl3 = myl*mylccl3

        dscdsl = ccl*dmydsl - myl2ccl3*dmydsl
        dccdsl = -mylccl3*dmydsl

        xu = xcu - 0.5*tcu*scu
        yu = ycu + 0.5*tcu*ccu
        xl = xcl + 0.5*tcl*scl
        yl = ycl - 0.5*tcl*ccl

        ccu = diag(ccu)
        scu = diag(scu)

        myu = diag(myu)
        myuccu3 = diag(myuccu3)
        myu2ccu3 = diag(myu2ccu3)

        dscdCnu = ccu@dmydCnu - myu2ccu3@dmydCnu
        dccdCnu = -myuccu3@dmydCnu

        ccl = diag(ccl)
        scl = diag(scl)

        myl = diag(myl)
        mylccl3 = diag(mylccl3)
        myl2ccl3 = diag(myl2ccl3)

        dscdCnl = ccl@dmydCnl - myl2ccl3@dmydCnl
        dccdCnl = -mylccl3@dmydCnl

        tcu = diag(tcu)
        tcl = diag(tcl)

        dxudsu = diag(dxcdsu - 0.5*(tcu@dscdsu + scu@dtcdsu))
        dyudsu = diag(dycdsu + 0.5*(tcu@dccdsu + ccu@dtcdsu))
        dxldsu = zeros((sl.size, su.size))
        dyldsu = zeros((sl.size, su.size))

        dxudsl = zeros((su.size, sl.size))
        dyudsl = zeros((su.size, sl.size))
        dxldsl = diag(dxcdsl + 0.5*(tcl@dscdsl + scl@dtcdsl))
        dyldsl = diag(dycdsl - 0.5*(tcl@dccdsl + ccl@dtcdsl))

        dxudCnu = -0.5*tcu@dscdCnu
        dyudCnu = dycdCnu + 0.5*tcu@dccdCnu
        dxldCnl = 0.5*tcl@dscdCnl
        dyldCnl = dycdCnl - 0.5*tcl@dccdCnl

        dxudTnu = -0.5*scu@dtcdTnu
        dyudTnu = 0.5*ccu@dtcdTnu
        dxldTnl = 0.5*scl@dtcdTnl
        dyldTnl = -0.5*ccl@dtcdTnl

        Dxu = xu - xup
        Dyu = yu - yup
        Dxl = xl - xlp
        Dyl = yl - ylp

        dres = concatenate((Dxu, Dyu, Dxl, Dyl))
        normdres = norm(dres)

        if display:
            print(f'dres = {dres.flatten()}\n')
            print(f'normdres = {normdres}\n')

        dxudvar = hstack((dxudCnu, dxudTnu, dxudsu, dxudsl))
        dyudvar = hstack((dyudCnu, dyudTnu, dyudsu, dyudsl))
        dxldvar = hstack((dxldCnl, dxldTnl, dxldsu, dxldsl))
        dyldvar = hstack((dyldCnl, dyldTnl, dyldsu, dyldsl))

        Amat = vstack((dxudvar, dyudvar, dxldvar, dyldvar))

        Bmat = dres

        Clist = []
        Dlist = []

        numt = 0
        for deriv, svalue, tvalue in self.Rt:
            if numt == self.Nts:
                break
            numt += 1
            spct = ChordSpacing(svalue)
            if deriv == 0:
                dtcdCn = zeros((*spct.shape, self.Ncs))
                dtcdTn = self.aply.calc_dtcdTn(spct)
                dtcdsu = zeros((*spct.shape, su.size))
                dtcdsl = zeros((*spct.shape, sl.size))
                dtcdvar = hstack((dtcdCn, dtcdTn, dtcdsu, dtcdsl))
                tc = self.aply.calc_tc(spct, Tn)
                Dtc = tc - tvalue
                Clist.append(dtcdvar)
                Dlist.append(Dtc)
            elif deriv == 1:
                dmtdCn = zeros((*spct.shape, self.Ncs))
                dmtdTn = self.aply.calc_dmtdTn(spct)
                dmtdsu = zeros((*spct.shape, su.size))
                dmtdsl = zeros((*spct.shape, sl.size))
                dmtdvar = hstack((dmtdCn, dmtdTn, dmtdsu, dmtdsl))
                mt = self.aply.calc_mt(spct, Tn)
                Dmt = mt - tvalue
                Clist.append(dmtdvar)
                Dlist.append(Dmt)
            elif deriv == 2:
                d2mtdsdCn = zeros((*spct.shape, self.Ncs))
                d2mtdsdTn = self.aply.calc_d2mtdsdTn(spct)
                d2mtdsdsu = zeros((*spct.shape, su.size))
                d2mtdsdsl = zeros((*spct.shape, sl.size))
                d2mtdsdvar = hstack((d2mtdsdCn, d2mtdsdTn, d2mtdsdsu, d2mtdsdsl))
                dmtds = self.aply.calc_dmtds(spct, Tn)
                Ddmtds = dmtds - tvalue
                Clist.append(d2mtdsdvar)
                Dlist.append(Ddmtds)
            else:
                raise ValueError('Invalid derivative value for thickness constraint.')

        numy = 0
        for deriv, svalue, yvalue in self.Ry:
            if numy == self.Ncs:
                break
            numy += 1
            spcy = ChordSpacing(svalue)
            if deriv == 0:
                dycdCn = self.aply.calc_dycdCn(spcy)
                dycdTn = zeros((*spcy.shape, self.Nts))
                dycdsu = zeros((*spcy.shape, su.size))
                dycdsl = zeros((*spcy.shape, sl.size))
                dycdvar = hstack((dycdCn, dycdTn, dycdsu, dycdsl))
                yc = self.aply.calc_yc(spcy, Cn)
                Dyc = yc - yvalue
                Clist.append(dycdvar)
                Dlist.append(Dyc)
            elif deriv == 1:
                dmydCn = self.aply.calc_dmydCn(spcy)
                dmydTn = zeros((*spcy.shape, self.Nts))
                dmydsu = zeros((*spcy.shape, su.size))
                dmydsl = zeros((*spcy.shape, sl.size))
                dmydvar = hstack((dmydCn, dmydTn, dmydsu, dmydsl))
                my = self.aply.calc_my(spcy, Cn)
                Dmy = my - yvalue
                Clist.append(dmydvar)
                Dlist.append(Dmy)
            elif deriv == 2:
                d2mydsdCn = self.aply.calc_d2mydsdCn(spcy)
                d2mydsdTn = zeros((*spcy.shape, self.Nts))
                d2mydsdsu = zeros((*spcy.shape, su.size))
                d2mydsdsl = zeros((*spcy.shape, sl.size))
                d2mydsdvar = hstack((d2mydsdCn, d2mydsdTn, d2mydsdsu, d2mydsdsl))
                dmyds = self.aply.calc_dmyds(spcy, Cn)
                Ddmyds = dmyds - yvalue
                Clist.append(d2mydsdvar)
                Dlist.append(Ddmyds)
            else:
                raise ValueError('Invalid derivative value for camber constraint.')

        Cmat = vstack(tuple(Clist))
        Dmat = asarray(Dlist)

        dcon = Dmat
        normdcon = norm(dcon)

        if display:
            print(f'dcon = {dcon.flatten()}\n')
            print(f'normdcon = {normdcon}\n')

        dvar, dlmda = solve_clsq(Amat, Bmat, Cmat, Dmat)

        normdvar = norm(dvar)
        normdlmda = norm(dlmda)

        if display:
            print(f'dvar = {dvar.flatten()}\n')
            print(f'normdvar = {normdvar}\n')
            print(f'dlmda = {dlmda.flatten()}\n')
            print(f'normdlmda = {normdlmda}\n')

        var = concatenate((Cn, Tn, su, sl))
        lmda = self.lmda

        var -= dvar
        lmda -= dlmda

        sections = [
            Cn.size,
            Cn.size + Tn.size,
            Cn.size + Tn.size + su.size
            ]

        Cn, Tn, su, sl = split(var, sections)

        self.aply = AirfoilPoly(self.airfoil.name, Cn, Tn, self.airfoil.chord)
        self.spcu = ChordSpacing(su)
        self.spcl = ChordSpacing(sl)
        self.lmda = lmda

        return normdcon, normdvar

    def improved_fit_loop(self, tol_dcon: float = 1e-12, tol_dvar: float = 1e-3,
                          max_iter: int = 50, display: bool = False) -> tuple[float, float]:

        normdcon, normdvar = float('inf'), float('inf')

        iter = 1
        while normdcon > tol_dcon or normdvar > tol_dvar:
            normdcon, normdvar = self.improved_fit()
            if display:
                print(f'Iteration {iter}')
                print(f'normdcon = {normdcon:.12f}')
                print(f'normdvar = {normdvar:.12f}')
                print()
            if iter >= max_iter:
                err = f'Maximum number of iterations ({max_iter}) reached.'
                raise RuntimeError(err)
            iter += 1

        return normdcon, normdvar

    def __repr__(self) -> str:
        return f'<AirfoilPolyFit: {self.airfoil.name:s}>'

    def __str__(self) -> str:
        return f'AirfoilPolyFit: {self.airfoil.name:s}'
