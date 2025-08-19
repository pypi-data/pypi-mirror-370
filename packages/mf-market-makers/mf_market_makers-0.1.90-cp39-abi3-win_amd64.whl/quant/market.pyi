###############################################################################
#
# (C) Copyright 2020 Maikon Araujo
#
# This is an unpublished work containing confidential and proprietary
# information of Maikon Araujo. Disclosure, use, or reproduction
# without authorization of Maikon Araujo is prohibited.
#
###############################################################################

from typing import TypeVar
import pyarrow as pa
import numpy as np
import numpy.typing as npt

T = TypeVar("T")
Quote = tuple[T, T]

class ZeroCrv:
    def __init__(self, ts: list[int], log_f: list[float]): ...
    def logf(self, t: int) -> float: ...
    @staticmethod
    def from_steps(ts: npt.NDArray[np.uint16], steps: npt.NDArray[np.float64]): ...
    def steps(self) -> tuple[npt.NDArray[np.uint16], npt.NDArray[np.float64]]: ...

def bootstrap(
    copom_t: npt.NDArray[np.float64],
    di_t: npt.NDArray[np.float64],
    di_rates: npt.NDArray[np.float64],
    s_1: float,
) -> tuple[ZeroCrv, float]:
    pass

class OptMarket:
    spot: Quote[float]
    t: int
    strikes: npt.NDArray[np.float64]
    call: Quote[npt.NDArray[np.float64]]
    putt: Quote[npt.NDArray[np.float64]]
    symbols_cp: Quote[pa.StringArray]
    def __init__(
        self,
        spot: Quote[float],
        t: int,
        strikes: npt.NDArray[np.float64],
        call: Quote[npt.NDArray[np.float64]],
        putt: Quote[npt.NDArray[np.float64]],
        symbols_cp: Quote[pa.StringArray],
    ): ...

class ImpliedMarket:
    taus: list[int]

    def fwd(self, tau: int) -> float: ...
    def borrow(self, tau: int) -> float: ...
    def discount(self, tau: int) -> float: ...
    def bs_price_greeks(
        self, tau: int, strikes: np.ndarray
    ) -> tuple[
        npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]
    ]:
        """Given a fitted tenor and a strike's array
        returns calls an puts with ther greeks:

        `(call, puts, vols)` each array with shape (n, 21)

        price, theta, rho, rho_borrow, spot, vol, t2, rt, r2, bt, br, b2, st, sr, sb, s2, vt, vr, vb, vs, v2.
        """
        pass

    def bs_prices(
        self, tau: int, strikes: npt.NDArray[np.float64]
    ) -> tuple[
        npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]
    ]: ...
    def bs_prices_simul(
        self,
        spots: npt.NDArray[np.float64],
        strikes: npt.NDArray[np.float64],
        is_call: npt.NDArray[np.bool_],
        tau: int,
        dw_t: tuple[float, int],
    ) -> npt.NDArray[np.float64]: ...
    def ws(
        self, tau: int, k_or_moneyness: npt.NDArray[np.float64], is_moneyness: bool
    ) -> npt.NDArray[np.float64]: ...

# def fit_prices(
#     crv: ZeroCrv, underlyings: list[str], markets: list[OptMarket], verbose: bool
# ) -> list[tuple[str, ImpliedMarket]]: ...
