from typing import TYPE_CHECKING, Any

from matplotlib.pyplot import figure
from numpy import arctan, block, concatenate, cos, diag, hstack, sin, zeros
from numpy.linalg import lstsq, norm
from py2md.classes import MDReport
from pygeom.geom2d import BSplineCurve2D, Vector2D
from pygeom.tools.solvers import solve_clsq

from .airfoilpoly import AirfoilPoly, AirfoilPolyFit
from .airfoilshape import AirfoilShape, AirfoilShapeFit
from .chordspacing import ChordSpacing

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from numpy.typing import NDArray


class AirfoilBSpline():
    name: str = None
    adef: AirfoilPoly | AirfoilShape = None
    bspline_u: 'BSplineCurve2D' = None
    bspline_l: 'BSplineCurve2D' = None
    c: float = None
    num: int = None
    _spacing: 'ChordSpacing' = None
    _xu: 'NDArray' = None
    _yu: 'NDArray' = None
    _xl: 'NDArray' = None
    _yl: 'NDArray' = None
    _x: 'NDArray' = None
    _y: 'NDArray' = None

    def __init__(self, name: str, adef: AirfoilPoly | AirfoilShape,
                 bspline_u: 'BSplineCurve2D', bspline_l: 'BSplineCurve2D',
                 c: float = 1.0, num: int = 101) -> None:
        self.name = name
        self.adef = adef
        self.bspline_u = bspline_u
        self.bspline_l = bspline_l
        self.c = c
        self.num = num

    def reset(self) -> None:
        for attr in self.__dict__.keys():
            if attr.startswith('_'):
                setattr(self, attr, None)

    def set_chord(self, c: float) -> None:
        self.c = c

    @property
    def spacing(self) -> ChordSpacing:
        if self._spacing is None:
            self._spacing = ChordSpacing.from_num(self.num)
        return self._spacing

    @property
    def th(self) -> 'NDArray':
        return self.spacing.th

    @property
    def xu(self) -> 'NDArray':
        if self._xu is None:
            pnts_u = self.bspline_u.evaluate_points_at_t(self.spacing.s)
            self._xu, self._yu = pnts_u.to_xy()
        return self._xu

    @property
    def yu(self) -> 'NDArray':
        if self._yu is None:
            pnts_u = self.bspline_u.evaluate_points_at_t(self.spacing.s)
            self._xu, self._yu = pnts_u.to_xy()
        return self._yu

    @property
    def xl(self) -> 'NDArray':
        if self._xl is None:
            pnts_l = self.bspline_l.evaluate_points_at_t(self.spacing.s)
            self._xl, self._yl = pnts_l.to_xy()
        return self._xl

    @property
    def yl(self) -> 'NDArray':
        if self._yl is None:
            pnts_l = self.bspline_l.evaluate_points_at_t(self.spacing.s)
            self._xl, self._yl = pnts_l.to_xy()
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
        return f'<AirfoilBSpline: {self.name:s}>'

    def to_mdobj(self) -> MDReport:
        return self.adef.to_mdobj()

    def _repr_markdown_(self) -> str:
        return self.to_mdobj()._repr_markdown_()

    def __str__(self) -> str:
        return f'AirfoilBSpline: {self.name:s}\nBSpline_u = \n{self.bspline_u}\nBSpline_l = \n{self.bspline_l}'


class AirfoilBSplineFit():
    afit: AirfoilPolyFit | AirfoilShapeFit = None
    Nu: int = None
    Nl: int = None
    _adef: AirfoilPoly | AirfoilShape = None
    _spcu: ChordSpacing = None
    _THu: 'NDArray' = None
    _Ucu: 'NDArray' = None
    _Vcu: 'NDArray' = None
    _Xcu: 'NDArray' = None
    _Ycu: 'NDArray' = None
    _Tcu: 'NDArray' = None
    _spcl: ChordSpacing = None
    _THl: 'NDArray' = None
    _Ucl: 'NDArray' = None
    _Vcl: 'NDArray' = None
    _Xcl: 'NDArray' = None
    _Ycl: 'NDArray' = None
    _Tcl: 'NDArray' = None
    _aspl: AirfoilBSpline = None
    _tu: 'NDArray' = None
    _tl: 'NDArray' = None
    _carr: 'NDArray' = None
    _darr: 'NDArray' = None
    _dXudTu: 'NDArray' = None
    _dYudTu: 'NDArray' = None
    _dXldTl: 'NDArray' = None
    _dYldTl: 'NDArray' = None
    _lmda: 'NDArray' = None

    def __init__(self, afit: AirfoilPolyFit | AirfoilShapeFit,
                 Nu: int, Nl: int) -> None:
        self.afit = afit
        self.Nu = Nu
        self.Nl = Nl

    @property
    def adef(self) -> AirfoilPoly | AirfoilShape:
        if self._adef is None:
            if isinstance(self.afit, AirfoilPolyFit):
                self._adef = self.afit.aply
            elif isinstance(self.afit, AirfoilShapeFit):
                self._adef = self.afit.ashp
            else:
                raise ValueError('Invalid airfoil shape type.')
        return self._adef

    @property
    def spcu(self) -> ChordSpacing:
        if self._spcu is None:
            self._spcu = ChordSpacing.from_num(self.Nu)
        return self._spcu

    @property
    def THu(self) -> 'NDArray':
        if self._THu is None:
            myu = self.adef.calc_my(self.spcu, self.adef.Cn)
            self._THu = arctan(myu)
        return self._THu

    @property
    def Ucu(self) -> 'NDArray':
        if self._Ucu is None:
            self._Ucu = -sin(self.THu)/2
        return self._Ucu

    @property
    def Vcu(self) -> 'NDArray':
        if self._Vcu is None:
            self._Vcu = cos(self.THu)/2
        return self._Vcu

    @property
    def Tcu(self) -> 'NDArray':
        if self._Tcu is None:
            self._Tcu = self.adef.calc_tc(self.spcu, self.adef.Tn)
            self._Tcu[0] = self._Tcu[1]
        return self._Tcu

    @property
    def Xcu(self) -> 'NDArray':
        if self._Xcu is None:
            self._Xcu = self.adef.calc_xc(self.spcu)
        return self._Xcu

    @property
    def Ycu(self) -> 'NDArray':
        if self._Ycu is None:
            self._Ycu = self.adef.calc_yc(self.spcu, self.adef.Cn)
        return self._Ycu

    @property
    def spcl(self) -> ChordSpacing:
        if self._spcl is None:
            self._spcl = ChordSpacing.from_num(self.Nl)
        return self._spcl

    @property
    def THl(self) -> 'NDArray':
        if self._THl is None:
            myl = self.adef.calc_my(self.spcl, self.adef.Cn)
            self._THl = arctan(myl)
        return self._THl

    @property
    def Ucl(self) -> 'NDArray':
        if self._Ucl is None:
            self._Ucl = sin(self.THl)/2
        return self._Ucl

    @property
    def Vcl(self) -> 'NDArray':
        if self._Vcl is None:
            self._Vcl = -cos(self.THl)/2
        return self._Vcl

    @property
    def Tcl(self) -> 'NDArray':
        if self._Tcl is None:
            self._Tcl = self.adef.calc_tc(self.spcl, self.adef.Tn)
            self._Tcl[0] = self._Tcl[1]
        return self._Tcl

    @property
    def Xcl(self) -> 'NDArray':
        if self._Xcl is None:
            self._Xcl = self.adef.calc_xc(self.spcl)
        return self._Xcl

    @property
    def Ycl(self) -> 'NDArray':
        if self._Ycl is None:
            self._Ycl = self.adef.calc_yc(self.spcl, self.adef.Cn)
        return self._Ycl

    @property
    def aspl(self) -> AirfoilBSpline:
        if self._aspl is None:

            ctlpnts_u = Vector2D.zeros(self.Nu + 1)
            ctlpnts_u.x[1:] = self.Xcu + self.Ucu*self.Tcu
            ctlpnts_u.y[1:] = self.Ycu + self.Vcu*self.Tcu
            bspline_u = BSplineCurve2D(ctlpnts_u, degree=self.Nu)

            ctlpnts_l = Vector2D.zeros(self.Nl + 1)
            ctlpnts_l.x[1:] = self.Xcl + self.Ucl*self.Tcl
            ctlpnts_l.y[1:] = self.Ycl + self.Vcl*self.Tcl
            bspline_l = BSplineCurve2D(ctlpnts_l, degree=self.Nl)

            self._aspl = AirfoilBSpline(self.adef.name, self.adef,
                                        bspline_u, bspline_l)

        return self._aspl

    @property
    def tu(self) -> 'NDArray':
        if self._tu is None:
            self._tu = self.afit.spcu.s.copy()
            self._tu = bspline_lstsq_fit_t(self.aspl.bspline_u, self.afit.xu,
                                           self.afit.yu, self._tu)
        return self._tu

    @property
    def tl(self) -> 'NDArray':
        if self._tl is None:
            self._tl = self.afit.spcl.s.copy()
            self._tl = bspline_lstsq_fit_t(self.aspl.bspline_l, self.afit.xl,
                                           self.afit.yl, self._tl)
        return self._tl

    @property
    def num_Tu(self) -> int:
        return self.Tcu.size - 1

    @property
    def num_Tl(self) -> int:
        return self.Tcl.size - 1

    @property
    def num_tu(self) -> int:
        return self.tu.size

    @property
    def num_tl(self) -> int:
        return self.tl.size

    @property
    def carr(self) -> 'NDArray':
        if self._carr is None:
            c_Tu = zeros((1, self.num_Tu))
            c_Tu[0, 0] = 1.0
            c_Tl = zeros((1, self.num_Tl))
            c_Tl[0, 0] = -1.0
            c_tu = zeros((1, self.num_tu))
            c_tl = zeros((1, self.num_tl))
            self._carr = hstack((c_Tu, c_Tl, c_tu, c_tl))
        return self._carr

    @property
    def darr(self) -> 'NDArray':
        if self._darr is None:
            self._darr = zeros(1)
        return self._darr

    @property
    def dXudTu(self) -> 'NDArray':
        if self._dXudTu is None:
            self._dXudTu = diag(self.Ucu[:-1])
        return self._dXudTu

    @property
    def dYudTu(self) -> 'NDArray':
        if self._dYudTu is None:
            self._dYudTu = diag(self.Vcu[:-1])
        return self._dYudTu

    @property
    def dXldTl(self) -> 'NDArray':
        if self._dXldTl is None:
            self._dXldTl = diag(self.Ucl[:-1])
        return self._dXldTl

    @property
    def dYldTl(self) -> 'NDArray':
        if self._dYldTl is None:
            self._dYldTl = diag(self.Vcl[:-1])
        return self._dYldTl

    @property
    def lmda(self) -> 'NDArray':
        if self._lmda is None:
            self._lmda = zeros(self.carr.shape[0])
        return self._lmda

    def plot_airfoil_bspline_fit(self, ax: 'Axes' = None) -> 'Axes':

        if ax is None:
            fig = figure(figsize=(12, 8))
            ax = fig.gca()
            ax.grid(True)
            ax.set_aspect('equal')
            ax.set_xlabel(r'$x$')
            ax.set_ylabel(r'$y$')

        ax = self.adef.plot_shape(ax=ax)
        ax = self.afit.airfoil.plot(ax=ax)

        pnts_u = self.aspl.bspline_u.evaluate_points(100)
        pnts_l = self.aspl.bspline_l.evaluate_points(100)

        ctls_u = self.aspl.bspline_u.ctlpnts
        ctls_l = self.aspl.bspline_l.ctlpnts

        ax.plot(pnts_u.x, pnts_u.y, label='BSpline Fit Upper')
        ax.plot(pnts_l.x, pnts_l.y, label='BSpline Fit Lower')
        ax.plot(ctls_u.x, ctls_u.y, '-o', label='Control Points Upper')
        ax.plot(ctls_l.x, ctls_l.y, '-o', label='Control Points Lower')
        ax.plot(self.afit.xu, self.afit.yu, 'x', label='Target Points Upper')
        ax.plot(self.afit.xl, self.afit.yl, 'x', label='Target Points Lower')
        _ = ax.legend()
        return ax

    def improved_fit(self, display: bool = False) -> tuple[float, float]:

        xu, yu = self.aspl.bspline_u.evaluate_points_at_t(self.tu).to_xy()

        Dxu = xu - self.afit.xu
        Dyu = yu - self.afit.yu

        xl, yl = self.aspl.bspline_l.evaluate_points_at_t(self.tl).to_xy()

        Dxl = xl - self.afit.xl
        Dyl = yl - self.afit.yl

        f = concatenate((Dxu, Dyu, Dxl, Dyl))

        Ntu = self.aspl.bspline_u.basis_functions(self.tu).transpose()

        dDxudXu = Ntu[:, 1:self.Nu]
        dDyudYu = Ntu[:, 1:self.Nu]

        Ntl = self.aspl.bspline_l.basis_functions(self.tl).transpose()

        dDxldXl = Ntl[:, 1:self.Nl]
        dDyldYl = Ntl[:, 1:self.Nl]

        dDxudTu = dDxudXu@self.dXudTu + dDyudYu@self.dYudTu
        dDxudTl = zeros((xu.size, self.Nl - 1))

        dDyudTu = dDyudYu@self.dYudTu + dDyudYu@self.dYudTu
        dDyudTl = zeros((yu.size, self.Nl - 1))

        dDxldTl = dDxldXl@self.dXldTl + dDyldYl@self.dYldTl
        dDxldTu = zeros((xl.size, self.Nu - 1))

        dDyldTl = dDyldYl@self.dYldTl + dDyldYl@self.dYldTl
        dDyldTu = zeros((yl.size, self.Nu - 1))

        dDxudtu, dDyudtu = self.aspl.bspline_u.evaluate_first_derivatives_at_t(self.tu).to_xy()

        dDxudtu = diag(dDxudtu)
        dDxudtl = zeros((xu.size, self.tl.size))

        dDyudtu = diag(dDyudtu)
        dDyudtl = zeros((yu.size, self.tl.size))

        dDxldtl, dDyldtl = self.aspl.bspline_l.evaluate_first_derivatives_at_t(self.tl).to_xy()

        dDxldtl = diag(dDxldtl)
        dDxldtu = zeros((xl.size, self.tu.size))

        dDyldtl = diag(dDyldtl)
        dDyldtu = zeros((yl.size, self.tu.size))

        dfdTt = block([[dDxudTu, dDxudTl, dDxudtu, dDxudtl],
                    [dDyudTu, dDyudTl, dDyudtu, dDyudtl],
                    [dDxldTu, dDxldTl, dDxldtu, dDxldtl],
                    [dDyldTu, dDyldTl, dDyldtu, dDyldtl]])

        dvTt, dlTt = solve_clsq(dfdTt, f, self.carr, self.darr)

        dTu = dvTt[:self.num_Tu]
        dTl = dvTt[self.num_Tu:self.num_Tu + self.num_Tl]
        dtu = dvTt[self.num_Tu + self.num_Tl:self.num_Tu + self.num_Tl + self.num_tu]
        dtl = dvTt[self.num_Tu + self.num_Tl + self.num_tu:]

        self.Tcu[:-1] -= dTu
        self.Tcl[:-1] -= dTl

        self.tu[:] -= dtu
        self.tl[:] -= dtl

        self.lmda[:] -= dlTt

        self._aspl = None

        normdvar = norm(dvTt)

        dcon = self.darr
        normdcon = norm(dcon)

        if display:
            print(f'normdvar = {normdvar}\n')
            print(f'normdcon = {normdcon}\n')

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
        return f'<AirfoilBSplineFit: {self.adef.name:s}>'

    def __str__(self) -> str:
        return f'AirfoilBSplineFit: {self.adef.name:s}'


def bspline_lstsq_fit_t(bspline: BSplineCurve2D, x_t: 'NDArray', y_t: 'NDArray',
                        t: 'NDArray', **kwargs: dict[str, Any]) -> 'NDArray':

    max_iter: int = kwargs.get('max_iter', 50)
    display: bool = kwargs.get('display', False)

    count = 0

    while True:

        x, y = bspline.evaluate_points_at_t(t).to_xy()

        Dx = x - x_t
        Dy = y - y_t

        f = concatenate((Dx, Dy))
        norm_f = norm(f)

        if display:
            print(f'f = {f}\n')
            print(f'norm_f = {norm_f}')

        if norm_f < 1.0e-12:
            if display:
                print(f'Converged with norm_f = {norm_f}\n')
            break

        dDxdt, dDydt = bspline.evaluate_first_derivatives_at_t(t).to_xy()
        dDxdt = diag(dDxdt)
        dDydt = diag(dDydt)

        dfdt = block([[dDxdt], [dDydt]])

        dvt, _, _, _ = lstsq(dfdt, f)
        t -= dvt
        norm_dv = norm(dvt)

        if display:
            print(f'dvtt = {dvt}\n')
            print(f'norm_dv = {norm_dv}\n')

        if norm_dv < 1.0e-12:
            if display:
                print(f'Converged with norm_dv = {norm_dv}\n')
            break

        count += 1

        if count > max_iter:
            print(f'Convergence failed in {max_iter} iterations.\n')
            print(f'norm_f = {norm_f}\n')
            print(f'norm_dv = {norm_dv}\n')
            break

    return t
