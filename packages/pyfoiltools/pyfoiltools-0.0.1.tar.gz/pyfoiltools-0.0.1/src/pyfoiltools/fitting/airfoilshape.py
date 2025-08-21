from typing import TYPE_CHECKING, Any

from matplotlib.pyplot import figure
from numpy import (absolute, arctan, argwhere, concatenate, degrees, diag,
                   divide, hstack, logical_and, logical_or, pi, radians, split,
                   sqrt, vstack, zeros)
from numpy.linalg import norm
from py2md.classes import MDReport
from pygeom.tools.solvers import solve_clsq

from ..airfoil import Airfoil
from .chordspacing import ChordSpacing

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from numpy.typing import NDArray


class AirfoilShape():
    name: str = None
    Cn: 'NDArray' = None
    Tn: 'NDArray' = None
    c: float = None
    num: int = None
    _co2: float = None
    _spacing: 'ChordSpacing' = None
    _Nc: int = None
    _Nt: int = None
    _xc: 'NDArray' = None
    _yc: 'NDArray' = None
    _my: 'NDArray' = None
    _tc: 'NDArray' = None
    _mt: 'NDArray' = None
    _cc: 'NDArray' = None
    _sc: 'NDArray' = None
    _xu: 'NDArray' = None
    _yu: 'NDArray' = None
    _xl: 'NDArray' = None
    _yl: 'NDArray' = None
    _x: 'NDArray' = None
    _y: 'NDArray' = None
    _al0: float = None
    _Cmqc: float = None
    _max_tc: float = None
    _max_tc_pc: float = None
    _max_yc: float = None
    _max_yc_pc: float = None

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

    def set_yte(self, yte: float, ind: int = 2) -> None:
        if ind <= 0:
            raise ValueError('Specified ind must be greater than 0.')
        elif ind % 2:
            raise ValueError('Specified ind must be even.')
        elif self.Cn.size < 2:
            raise IndexError('AirfoilPoly Cn attribute needs size >= 2.')
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
        elif ind % 2:
            raise ValueError('Specified ind must be even.')
        elif self.Tn.size < 2:
            raise IndexError('AirfoilPoly Tn attribute needs size >= 2.')
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
    def co2(self) -> float:
        if self._co2 is None:
            self._co2 = self.c/2
        return self._co2

    @property
    def spacing(self) -> 'ChordSpacing':
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

    def calc_dxcdth(self, spc: ChordSpacing) -> 'NDArray':
        dxcdth = self.co2*spc.sinth
        return dxcdth

    def calc_dycdCn(self, spc: ChordSpacing, Cn: 'NDArray' = None) -> 'NDArray':
        costh = spc.costh
        sinth = spc.sinth
        dycdCn = zeros((*spc.shape, self.Nc))
        for n in range(self.Nc):
            if n == 1:
                dycdCn[..., n] = self.co2*spc.sinth**2/2
            else:
                cosnth = spc.cosnth(n)
                n_sinnth = spc.n_sinnth(n)
                fac = self.co2/(n**2 - 1)
                dycdCn[..., n] = (sinth*n_sinnth + costh*cosnth - 1.0)*fac
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
            dmydCn[..., n] = spc.cosnth(n)
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

    def calc_dmydth(self, spc: ChordSpacing, Cn: 'NDArray') -> 'NDArray':
        dmydth = zeros(*spc.shape)
        for n, Cn in enumerate(Cn):
            dmydth += -Cn*spc.n_sinnth(n)
        return dmydth

    def calc_dycdth(self, spc: ChordSpacing, Cn: 'NDArray') -> 'NDArray':
        dycdxc = self.calc_my(spc, Cn)
        dxcdth = self.calc_dxcdth(spc)
        dycdth = dycdxc*dxcdth
        return dycdth

    def calc_dtcdTn(self, spc: ChordSpacing, Tn: 'NDArray' = None) -> 'NDArray':
        th = spc.th
        costh = spc.costh
        sinth = spc.sinth
        dtcdTn = zeros((*spc.shape, self.Nt))
        for n in range(self.Nt):
            if n == 0:
                dtcdTn[..., n] = self.co2*(th + sinth)
            elif n == 1:
                dtcdTn[..., n] = self.co2*sinth**2/2
            else:
                cosnth = spc.cosnth(n)
                n_sinnth = spc.n_sinnth(n)
                fac = self.co2/(n**2 - 1)
                dtcdTn[..., n] = (sinth*n_sinnth + costh*cosnth - 1.0)*fac
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
        costh = spc.costh
        sinth = spc.sinth
        for n in range(self.Nt):
            if n == 0:
                mt0 = zeros(*spc.shape)
                divide((1 + costh), sinth, out=mt0, where=sinth != 0.0)
                mt0[spc.th == 0.0] = float('inf')
                dmtdTn[..., n] += mt0
            else:
                dmtdTn[..., n] += spc.cosnth(n)
        if Tn is not None:
            ind_Tn_not0 = argwhere(Tn != 0.0).flatten()
            dmtdTn = dmtdTn[..., ind_Tn_not0]@Tn[ind_Tn_not0]
        return dmtdTn

    def calc_mt(self, spc: ChordSpacing, Tn: 'NDArray') -> 'NDArray':
        mt = self.calc_dmtdTn(spc, Tn)
        return mt

    def calc_dtcdth(self, spc: ChordSpacing, Tn: 'NDArray') -> 'NDArray':
        dtcdxc = self.calc_mt(spc, Tn)
        dxcdth = self.calc_dxcdth(spc)
        dtcdth = dtcdxc*dxcdth
        return dtcdth

    @property
    def mt(self) -> 'NDArray':
        if self._mt is None:
            self._mt = self.calc_mt(self.spacing, self.Tn)
        return self._mt

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

    @property
    def al0(self) -> float:
        if self._al0 is None:
            if self.Cn.size == 0:
                self._al0 = 0.0
            elif self.Cn.size == 1:
                self._al0 = self.Cn[0]
            else:
                self._al0 = self.Cn[0] - self.Cn[1]/2
        return self._al0

    @property
    def Cmqc(self) -> float:
        if self._Cmqc is None:
            if self.Cn.size <= 1:
                self._Cmqc = 0.0
            elif self.Cn.size == 2:
                self._Cmqc = -pi/4**self.Cn[1]
            else:
                self._Cmqc = pi/4*(self.Cn[2] - self.Cn[1])
        return self._Cmqc

    def calc_max_tc_result(self) -> tuple[float, float]:
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

    def calc_max_yc_result(self) -> tuple[float, float]:
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
        my = self.my
        if as_angle:
            my = degrees(arctan(self.my))
        if vs_th:
            ax.plot(self.th, my, label=self.name)
        else:
            ax.plot(self.xc, my, label=self.name)
        return ax

    def gamma(self, aldeg: float, speed: float = 1.0) -> 'NDArray':
        alrad = radians(aldeg)
        gamma = zeros(self.num)
        costh = self.spacing.costh
        sinth = self.spacing.sinth
        for n, Cn in enumerate(self.Cn):
            if n == 0:
                An = alrad - Cn
                Tn = zeros(self.num)
                divide(1.0 + costh, sinth, out=Tn, where=sinth != 0.0)
                divide(-sinth, costh, out=Tn, where=sinth == 0.0)
                Tn[self.th == 0.0] = float('inf')
                gamma += 2*speed*An*Tn
            else:
                if Cn == 0.0:
                    continue
                An = Cn
                gamma += 2*speed*An*self.spacing.sinnth(n)
        return gamma

    def plot_gamma(self, aldeg: float, speed: float = 1.0,
                   ax: 'Axes' = None, vs_th: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            ax.set_ylabel(r'$\gamma$')
        gamma = self.gamma(aldeg, speed)
        if vs_th:
            ax.plot(self.th, gamma, label=self.name)
        else:
            ax.plot(self.xc, gamma, label=self.name)
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

    def sigma(self, speed: float = 1.0) -> 'NDArray':
        costh = self.spacing.costh
        sinth = self.spacing.sinth
        sigma = zeros(self.num)
        for n, Tn in enumerate(self.Tn):
            if Tn == 0.0:
                continue
            if n == 0:
                sigma0 = zeros(self.num)
                divide(Tn*(1 + costh), sinth, out=sigma0, where=sinth != 0.0)
                sigma0[self.th == 0.0] = float('inf')
                sigma += 2*speed*sigma0
            else:
                sigma += 2*speed*Tn*self.spacing.sinnth(n)
        return sigma

    def plot_sigma(self, speed: float = 1.0,
                   ax: 'Axes' = None, vs_th: bool = False) -> 'Axes':
        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            if vs_th:
                ax.set_xlabel(r'$\theta$')
            else:
                ax.set_xlabel(r'$x_c$')
            ax.set_ylabel(r'$\sigma$')
        sigma = self.sigma(speed)
        if vs_th:
            ax.plot(self.th, sigma, label=self.name)
        else:
            ax.plot(self.xc, sigma, label=self.name)
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
        return f'<AirfoilShape: {self.name:s}>'

    def to_mdobj(self) -> MDReport:
        report = MDReport()
        report.add_heading(f'Airfoil Shape: {self.name:s}', level=1)
        table = report.add_table()
        if self.Cn.size > 0:
            table.add_column('Max Camber %', '.3f', data=[self.max_yc/self.c*100])
            table.add_column('Max Camber Position %', '.3f', data=[self.max_yc_pc*100])
        if self.Tn.size > 0:
            table.add_column('Max Thickness %', '.3f', data=[self.max_tc/self.c*100])
            table.add_column('Max Thickness Position %', '.3f', data=[self.max_tc_pc*100])
        table = report.add_table()
        table.add_column('a<sub>l0</sub>', '.3f', data=[degrees(self.al0)])
        table.add_column('C<sub>m1/4c</sub>', '.3f', data=[self.Cmqc])
        return report

    def _repr_markdown_(self) -> str:
        return self.to_mdobj()._repr_markdown_()

    def __str__(self) -> str:
        return f'AirfoilShape: {self.name:s}\nCn = \n{self.Cn}\nTn = \n{self.Tn}'

class AirfoilShapeFit():
    airfoil: Airfoil = None
    Ncs: int = None
    Nts: int = None
    yte: float = None
    tte: float = None
    xu: 'NDArray' = None
    yu: 'NDArray' = None
    xl: 'NDArray' = None
    yl: 'NDArray' = None
    spcu: 'ChordSpacing' = None
    spcl: 'ChordSpacing' = None
    ashp: AirfoilShape = None
    lmda: 'NDArray' = None

    def __init__(self, airfoil: Airfoil, Ncs: int, Nts: int,
                 yte: float = None, tte: float = None) -> None:
        self.airfoil = airfoil
        self.Ncs = Ncs
        self.Nts = Nts
        self.yte = yte
        if self.yte is None:
            self.yte = self.airfoil.yte
        self.tte = tte
        if self.tte is None:
            self.tte = self.airfoil.tte
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

    def fit(self) -> float:

        self.xu = self.airfoil.xu[1:-1]
        self.yu = self.airfoil.yu[1:-1]
        self.spcu = ChordSpacing.from_x_and_c(self.xu, self.airfoil.chord)

        self.xl = self.airfoil.xl[1:-1]
        self.yl = self.airfoil.yl[1:-1]
        self.spcl = ChordSpacing.from_x_and_c(self.xl, self.airfoil.chord)

        Cn = zeros(self.Ncs)
        Tn = zeros(self.Nts)

        self.ashp = AirfoilShape(self.airfoil.name, Cn, Tn,
                                 self.airfoil.chord)

        dtcdTnu = self.ashp.calc_dtcdTn(self.spcu)
        dtcdTnl = self.ashp.calc_dtcdTn(self.spcl)
        dycdCnu = self.ashp.calc_dycdCn(self.spcu)
        dycdCnl = self.ashp.calc_dycdCn(self.spcl)

        dyudvar = hstack((dycdCnu, 0.5*dtcdTnu))
        dyldvar = hstack((dycdCnl, -0.5*dtcdTnl))

        Amat = vstack((dyudvar, dyldvar))

        Bmat = zeros(Amat.shape[0])
        Bmat[:self.yu.size] = self.yu
        Bmat[self.yu.size:] = self.yl

        spcte = ChordSpacing.from_th(pi)

        dttedCn = zeros(self.Ncs)
        dttedTn = self.ashp.calc_dtcdTn(spcte)

        dttedvar = hstack((dttedCn, dttedTn))
        tte = self.tte

        if self.Ncs > 0:
            dytedCn = self.ashp.calc_dycdCn(spcte)
            dytedTn = zeros(self.Nts)
            dytedvar = hstack((dytedCn, dytedTn))
            yte = self.yte
            Cmat = vstack((dytedvar, dttedvar))
            Dmat = zeros(Cmat.shape[0])
            Dmat[0] = yte
            Dmat[1] = tte
        else:
            Cmat = dttedvar.reshape(1, -1)
            Dmat = zeros(Cmat.shape[0])
            Dmat[0] = tte

        var, self.lmda = solve_clsq(Amat, Bmat, Cmat, Dmat)

        Cn = var[:self.Ncs]
        Tn = var[self.Ncs:]

        self.ashp = AirfoilShape(self.airfoil.name, Cn, Tn,
                                 self.airfoil.chord, self.ashp.num)

        ycu = self.ashp.calc_yc(self.spcu, Cn)
        tcu = self.ashp.calc_tc(self.spcu, Tn)
        yu = ycu + 0.5*tcu

        ycl = self.ashp.calc_yc(self.spcl, Cn)
        tcl = self.ashp.calc_tc(self.spcl, Tn)
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

        Cn = self.ashp.Cn.copy()
        Tn = self.ashp.Tn.copy()
        thu = self.spcu.th.copy()
        thl = self.spcl.th.copy()
        lmda = self.lmda.copy()

        if display:

            print(f'Cn = {Cn}\n')
            print(f'Tn = {Tn}\n')
            print(f'thu = {thu}\n')
            print(f'thl = {thl}\n')

            print(f'Cn.size = {Cn.size}\n')
            print(f'Tn.size = {Tn.size}\n')
            print(f'thu.size = {thu.size}\n')
            print(f'thl.size = {thl.size}\n')

        xcu = self.ashp.calc_xc(self.spcu)
        dxcdthu = self.ashp.calc_dxcdth(self.spcu)

        xcl = self.ashp.calc_xc(self.spcl)
        dxcdthl = self.ashp.calc_dxcdth(self.spcl)

        ycu = self.ashp.calc_yc(self.spcu, Cn)
        dycdthu = self.ashp.calc_dycdth(self.spcu, Cn)
        dycdCnu = self.ashp.calc_dycdCn(self.spcu)

        ycl = self.ashp.calc_yc(self.spcl, Cn)
        dycdthl = self.ashp.calc_dycdth(self.spcl, Cn)
        dycdCnl = self.ashp.calc_dycdCn(self.spcl)

        tcu = self.ashp.calc_tc(self.spcu, Tn)
        dtcdthu = self.ashp.calc_dtcdth(self.spcu, Tn)
        dtcdTnu = self.ashp.calc_dtcdTn(self.spcu)

        tcl = self.ashp.calc_tc(self.spcl, Tn)
        dtcdthl = self.ashp.calc_dtcdth(self.spcl, Tn)
        dtcdTnl = self.ashp.calc_dtcdTn(self.spcl)

        dmydthu = self.ashp.calc_dmydth(self.spcu, Cn)
        dmydCnu = self.ashp.calc_dmydCn(self.spcu)

        dmydthl = self.ashp.calc_dmydth(self.spcl, Cn)
        dmydCnl = self.ashp.calc_dmydCn(self.spcl)

        myu = self.ashp.calc_my(self.spcu, Cn)
        myu2 = myu**2
        ccu = 1.0/sqrt(1.0 + myu2)
        scu = myu*ccu

        ccu3 = ccu**3
        myuccu3 = myu*ccu3
        myu2ccu3 = myu*myuccu3

        dscdthu = ccu*dmydthu - myu2ccu3*dmydthu
        dccdthu = -myuccu3*dmydthu

        myl = self.ashp.calc_my(self.spcl, Cn)
        myl2 = myl**2
        ccl = 1.0/sqrt(1.0 + myl2)
        scl = myl*ccl

        ccl3 = ccl**3
        mylccl3 = myl*ccl3
        myl2ccl3 = myl*mylccl3

        dscdthl = ccl*dmydthl - myl2ccl3*dmydthl
        dccdthl = -mylccl3*dmydthl

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

        dxudthu = diag(dxcdthu - 0.5*(tcu@dscdthu + scu@dtcdthu))
        dyudthu = diag(dycdthu + 0.5*(tcu@dccdthu + ccu@dtcdthu))
        dxldthu = zeros((thl.size, thu.size))
        dyldthu = zeros((thl.size, thu.size))

        dxudthl = zeros((thu.size, thl.size))
        dyudthl = zeros((thu.size, thl.size))
        dxldthl = diag(dxcdthl + 0.5*(tcl@dscdthl + scl@dtcdthl))
        dyldthl = diag(dycdthl - 0.5*(tcl@dccdthl + ccl@dtcdthl))

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

        spcte = ChordSpacing.from_th(pi)

        ytep = self.yte
        yte = self.ashp.calc_yc(spcte, Cn)
        Dyte = yte - ytep

        ttep = self.tte
        tte = self.ashp.calc_tc(spcte, Tn)
        Dtte = tte - ttep

        dytedCn = self.ashp.calc_dycdCn(spcte)
        dytedTn = zeros(Tn.size)
        dytedthu = zeros(thu.size)
        dytedthl = zeros(thl.size)

        dttedCn = zeros(Cn.size)
        dttedTn = self.ashp.calc_dtcdTn(spcte)
        dttedthu = zeros(thu.size)
        dttedthl = zeros(thl.size)

        dres = concatenate((Dxu, Dyu, Dxl, Dyl))
        normdres = norm(dres)

        if self.Ncs > 0:
            dcon = zeros(2)
            dcon[0] = Dtte
            dcon[1] = Dyte
        else:
            dcon = zeros(1)
            dcon[0] = Dtte

        normdcon = norm(dcon)

        if display:
            print(f'dres = {dres.flatten()}\n')
            print(f'normdres = {normdres}\n')
            print(f'dcon = {dcon.flatten()}\n')
            print(f'normdcon = {normdcon}\n')

        dxudvar = hstack((dxudCnu, dxudTnu, dxudthu, dxudthl))
        dyudvar = hstack((dyudCnu, dyudTnu, dyudthu, dyudthl))
        dxldvar = hstack((dxldCnl, dxldTnl, dxldthu, dxldthl))
        dyldvar = hstack((dyldCnl, dyldTnl, dyldthu, dyldthl))

        Amat = vstack((dxudvar, dyudvar, dxldvar, dyldvar))

        Bmat = dres

        dttedvar = hstack((dttedCn, dttedTn, dttedthu, dttedthl))

        if self.Ncs > 0:
            dytedvar = hstack((dytedCn, dytedTn, dytedthu, dytedthl))
            Cmat = vstack((dttedvar, dytedvar))
        else:
            Cmat = dttedvar
            Dmat = zeros((Cmat.shape[0], 1))

        Dmat = dcon

        dvar, dlmda = solve_clsq(Amat, Bmat, Cmat, Dmat)

        normdvar = norm(dvar)
        normdlmda = norm(dlmda)

        if display:
            print(f'dvar = {dvar.flatten()}\n')
            print(f'normdvar = {normdvar}\n')
            print(f'dlmda = {dlmda.flatten()}\n')
            print(f'normdlmda = {normdlmda}\n')

        var = concatenate((Cn, Tn, thu, thl))
        lmda = self.lmda

        var -= dvar
        lmda -= dlmda

        sections = [
            Cn.size,
            Cn.size + Tn.size,
            Cn.size + Tn.size + thu.size
            ]

        Cn, Tn, thu, thl = split(var, sections)

        self.ashp = AirfoilShape(self.airfoil.name, Cn, Tn, self.airfoil.chord)
        self.spcu = ChordSpacing.from_th(thu)
        self.spcl = ChordSpacing.from_th(thl)
        self.lmda = lmda

        return normdcon, normdvar

    def improved_fit_loop(self, tol_dcon: float = 1e-12, tol_dvar: float = 1e-12,
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
        return f'<AirfoilShapeFit: {self.airfoil.name:s}>'

    def __str__(self) -> str:
        return f'AirfoilShapeFit: {self.airfoil.name:s}'
