"""
preprocessing.py – low-level helpers for the Python SNID port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Public API
----------
  • init_wavelength_grid
  • medfilt
  • clip_aband
  • clip_sky_lines
  • clip_host_emission_lines
  • apply_wavelength_mask
  • log_rebin
  • fit_continuum_spline
  • apodize
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
from typing import List, Tuple, Optional, Dict
import logging
import numpy as np
from numpy.typing import NDArray
from typing import Tuple
from numpy import ma


_LOG = logging.getLogger("snid.preprocessing")

# ------------------------------------------------------------------
# global logarithmic grid
# ------------------------------------------------------------------
# NW: int        = 1024
# W0: float      = 2500.0      # Å
# W1: float      = 10000.0     # Å
# DWLOG: float | None = None   # filled by init_wavelength_grid()

def init_wavelength_grid(num_points: int = 1024,
                         min_wave: float = 2500.0,
                         max_wave: float = 10000.0) -> None:
    """Define the fixed log-λ grid shared by all spectra."""
    global NW, W0, W1, DWLOG
    NW, W0, W1 = int(num_points), float(min_wave), float(max_wave)
    DWLOG = np.log(W1 / W0) / (NW)
    _LOG.debug("Grid initialised: NW=%d  W0=%.1f  W1=%.1f  DWLOG=%.6e",
               NW, W0, W1, DWLOG)

def _ensure_grid() -> None:
    if DWLOG is None:
        init_wavelength_grid()

def get_grid_params() -> tuple[int, float, float, float]:
    """
    Return (NW, W0, W1, DWLOG); initialises the grid if necessary.
    """
    _ensure_grid()
    return NW, W0, W1, DWLOG

# ------------------------------------------------------------------
# filters & masks
# ------------------------------------------------------------------
def savgol_filter_fixed(data: NDArray[np.floating], window_length: int = 11, polyorder: int = 3) -> NDArray[np.floating]:
    """
    Apply Savitzky-Golay filter with fixed window length (pixel-based smoothing).
    Replaces the old medfilt function.
    
    Parameters:
    -----------
    data : NDArray[np.floating]
        Input flux array to filter
    window_length : int
        Length of the filter window in pixels (must be odd, default: 11)
    polyorder : int
        Order of the polynomial used to fit the samples (default: 3)
        
    Returns:
    --------
    NDArray[np.floating]
        Filtered flux array
    """
    from scipy.signal import savgol_filter
    
    if window_length < 3:
        return data.copy()
    
    # Ensure window length is odd and valid
    if window_length % 2 == 0:
        window_length += 1
    
    # Ensure window length is not larger than data
    window_length = min(window_length, len(data))
    if window_length < 3:
        return data.copy()
    
    # Ensure polynomial order is less than window length
    polyorder = min(polyorder, window_length - 1)
    
    try:
        return savgol_filter(data, window_length, polyorder)
    except Exception:
        # Return original data if filtering fails
        return data.copy()


# Legacy function names for backward compatibility
def medfilt(data: NDArray[np.floating], medlen: int) -> NDArray[np.floating]:
    """
    Legacy wrapper for savgol_filter_fixed.
    Apply Savitzky-Golay filter with pixel-based window length.
    """
    # Convert old median filter length to appropriate savgol window
    window_length = max(3, medlen)
    return savgol_filter_fixed(data, window_length, polyorder=3)


# medwfilt removed (wavelength-based filtering no longer supported)

# --- clipping helpers --------------------------------------------------------
def clip_aband(w: np.ndarray, f: np.ndarray,
               band: Tuple[float,float] = (7575.0, 7675.0)
              ) -> Tuple[np.ndarray, np.ndarray]:
    """Remove telluric A-band."""
    a, b = band
    keep = ~((w >= a) & (w <= b))
    return w[keep], f[keep]

def clip_sky_lines(w: np.ndarray, f: np.ndarray,
                   width: float = 40.0,
                   lines: Tuple[float,...] = (5577.0, 6300.2, 6364.0)
                  ) -> Tuple[np.ndarray, np.ndarray]:
    keep = np.ones_like(w, bool)
    for l in lines:
        keep &= ~((w >= l-width) & (w <= l+width))
    return w[keep], f[keep]

def clip_host_emission_lines(w: np.ndarray, f: np.ndarray,
                             z: float,
                             width: float = 40.0
                            ) -> Tuple[np.ndarray, np.ndarray]:
    if z < 0:
        return w, f
    rest = [3727.3, 4861.3, 4958.9, 5006.8,
            6548.1, 6562.8, 6583.6, 6716.4, 6730.8]
    keep = np.ones_like(w, bool)
    for l in rest:
        ll = l*(1+z)
        keep &= ~((w >= ll-width) & (w <= ll+width))
    return w[keep], f[keep]

def apply_wavelength_mask(w: np.ndarray, f: np.ndarray,
                          ranges: List[Tuple[float,float]]
                         ) -> Tuple[np.ndarray, np.ndarray]:
    keep = np.ones_like(w, bool)
    for a, b in ranges:
        if b < a:
            raise ValueError(f"mask ({a},{b}) has b < a")
        keep &= ~((w >= a) & (w <= b))
    return w[keep], f[keep]

# ------------------------------------------------------------------
# cosine bell taper
# ------------------------------------------------------------------
def apodize(arr, n1, n2, percent=5.0):
    """Raised-cosine taper exactly like SNID's APOWID, but only over the valid region.
    Apodizes `arr` between `n1` and `n2` (inclusive), where these are the start and end indices of the valid (nonzero) region.
    The percentage is relative to the valid region length (n2-n1+1).
    """
    out = arr.copy()
    if not (0 <= n1 <= n2 < len(arr)):
        _LOG.warning(f"Apodize range [{n1},{n2}] invalid for array of length {len(arr)}. Skipping.")
        return out

    if percent is None or percent <= 0:
        return out

    valid_data_len = (n2 - n1 + 1)
    if valid_data_len <= 0:
        return out
    ns = int(round(valid_data_len * percent / 100.0))
    ns = min(ns, int(valid_data_len / 2.0))

    if ns < 1:
        return out

    if ns == 1:
        ramp = np.array([0.0])
    elif ns > 1:
        ramp = 0.5 * (1 - np.cos(np.pi * np.arange(ns) / (ns - 1.0)))
    else:
        return out

    if n1 + ns > len(arr) or n2 - ns + 1 < 0:
        _LOG.warning("Apodize slice out of bounds after ns calculation.")
        return out

    out[n1 : n1 + ns] *= ramp
    out[n2 - ns + 1 : n2 + 1] *= ramp[::-1]
    return out

# ------------------------------------------------------------------
# log-λ rebin, continuum spline  (unchanged from previous version)
# ------------------------------------------------------------------
def log_rebin(
    wave: NDArray[np.floating],
    fsrc: NDArray[np.floating],
) -> Tuple[NDArray[np.floating], NDArray[np.floating]]:
    """
    Exactly reproduces the Fortran `rebin` subroutine:
      - Splits each input pixel [s0,s1] in linear λ
      - Maps its boundaries into log‐bin indices s0log, s1log
      - Distributes fsrc[l] * Δλ over all overlapping log‐bins
        in proportion to fractional overlap (alen/(s1log-s0log))
      - Converts the result to flux density by dividing by each bin's width
    Returns
    -------
    log_wave : 1-D array of length NW
        Bin centers on the log‐λ grid: W0 * exp(i * DWLOG), i=0..NW-1
    log_flux : 1-D array of length NW
        Flux density per Å on that grid
    """
    # 1) Ensure the global log-grid is set
    _ensure_grid()

    # 2) Grab grid params
    nlog  = NW
    w0    = W0
    dwlog = DWLOG

    # 3) Build output log‐wavelength axis
    log_wave = w0 * np.exp((np.arange(nlog) + 0.5) * dwlog)

    # 4) Prepare destination accumulator
    fdest = np.zeros(nlog, dtype=fsrc.dtype)

    # 5) Compute linear‐λ pixel edges s[k], k=0..len(wave)
    s = np.empty(wave.size + 1, dtype=float)
    s[1:-1] = 0.5 * (wave[:-1] + wave[1:])
    # extrapolate first/last
    s[0]    = 1.5 * wave[0] - 0.5 * wave[1]
    s[-1]   = 1.5 * wave[-1] - 0.5 * wave[-2]

    # 6) Map those edges into log‐bin coordinates (1‐indexed to match Fortran)
    slog = np.log(s / w0) / dwlog + 1.0

    # 7) Loop each source pixel ℓ
    for l in range(wave.size):
        s0log = slog[l]
        s1log = slog[l + 1]
        dλ     = s[l + 1] - s[l]   # Δλ for this pixel

        # Fortran's: DO i = INT(s0log), INT(s1log)
        i0 = max(1, int(np.floor(s0log)))
        i1 = min(nlog, int(np.floor(s1log)))

        width_log = (s1log - s0log)  # total width in log‐units
        for i in range(i0, i1 + 1):
            # overlap of [s0log,s1log] with bin i..i+1
            alen = min(s1log, i + 1.0) - max(s0log, float(i))
            if alen <= 0:
                continue
            # fraction of pixel's flux to put in this bin
            frac = alen / width_log
            fdest[i - 1] += fsrc[l] * frac * dλ

    # 8) Convert accumulated integrated flux into flux density per Å
    edges = w0 * np.exp((np.arange(nlog + 1) - 0.5) * dwlog)
    binw   = np.diff(edges)
    fdest  = fdest / binw

    return log_wave, fdest


def fit_continuum(
    flux: NDArray[np.floating],
    *,
    method: str = "spline",
    # spline args:
    knotnum: int = 13,
    izoff:    int = 0,
) -> Tuple[NDArray[np.floating], NDArray[np.floating]]:
    """
    Remove a smooth continuum from `flux` on the fixed log‐λ grid.

    Returns
    -------
    flat : flux/cont - 1
    cont : continuum estimate

    Parameters
    ----------
    method : "spline"
       - "spline": use the original SNID cubic‐spline (fit_continuum_spline) (DEFAULT)
    knotnum, izoff
      passed to fit_continuum_spline
    """
    if method == "spline":
        flat, cont = fit_continuum_spline(flux, knotnum=knotnum, izoff=izoff)
    else:
        raise ValueError(f"Unknown method={method!r}; only 'spline' is supported")

    # ——— zero‐out anything outside the observed data range ———
    # find first/last valid data bins (including negative values for continuum-subtracted spectra)
    valid_indices = np.where((flux != 0) & np.isfinite(flux))[0]
    if valid_indices.size:
        i0, i1 = valid_indices[0], valid_indices[-1]
        # outside [i0,i1] we have no data → zero flat, unity continuum
        flat[:i0]   = 0.0
        flat[i1+1:] = 0.0
        cont[:i0]   = 0.0
        cont[i1+1:] = 0.0

    return flat, cont



def fit_continuum_spline(
    flux: NDArray[np.floating],
    knotnum: int = 13,
    izoff:    int = 0,
) -> Tuple[NDArray[np.floating], NDArray[np.floating]]:
    """
    Port of the Fortran MEANZERO + scale‐removal steps:
      1) find usable range [l1..l2] by chopping off up to one zero
         or negative pixel at each end,
      2) place knots by averaging within kw = n//knotnum bins,
         with a phase offset istart = (izoff % kw) - kw,
      3) build a natural cubic spline through (xknot, yknot) in log10,
      4) evaluate the spline to get cont[i] = 10**spl(i),
      5) return flat = flux/cont - 1, plus cont itself.
    Parameters
    ----------
    flux : 1D array of flux (must be ≥0 for real data points)
    knotnum : number of average‐knots (Fortran used 13)
    izoff   : integer offset in log‐bins (Fortran z‐centroid → knot phase)
    Returns
    -------
    flat : flux with continuum removed (flat[i] = flux[i]/cont[i] - 1)
    cont : the continuum model sampled at every i (same shape as flux)
    """
    n = flux.size

    # trivial case
    if n < 10 or knotnum < 3:
        return np.zeros_like(flux), np.ones_like(flux)

    # --- 1) chop off up to one zero/neg at each end ---
    l1 = 0
    nuked = 0
    while l1 < n - 1 and (flux[l1] <= 0 or nuked < 1):
        if flux[l1] > 0:
            nuked += 1
        l1 += 1

    l2 = n - 1
    nuked = 0
    while l2 > 1 and (flux[l2] <= 0 or nuked < 1):
        if flux[l2] > 0:
            nuked += 1
        l2 -= 1

    if (l2 - l1) < 3 * knotnum:
        return np.zeros_like(flux), np.ones_like(flux)

    # --- 2) place knots using Fortran-congruent averages ---
    # Use log10(mean(flux)) per block (NOT mean(log10(flux))).
    kwidth = n // knotnum
    istart = ((izoff % kwidth) - kwidth) if izoff > 0 else 0

    xknot = []
    yknot = []
    nave = 0.0
    sum_x = 0.0
    sum_flux = 0.0

    for i in range(n):
        if l1 < i < l2 and flux[i] > 0:
            nave += 1.0
            sum_x += (i - 0.5)
            sum_flux += flux[i]
        if ((i - istart) % kwidth) == 0 and nave > 0:
            xknot.append(sum_x / nave)
            yknot.append(np.log10(sum_flux / nave))
            nave = 0.0
            sum_x = 0.0
            sum_flux = 0.0

    nk = len(xknot)
    if nk < 3:
        return np.zeros_like(flux), np.ones_like(flux)

    xknot = np.array(xknot, dtype=float)
    yknot = np.array(yknot, dtype=float)


    # --- 3) build spline second derivatives y2 ---
    h = np.diff(xknot)
    rhs = 6.0 * (
        (yknot[2:] - yknot[1:-1]) / h[1:]
      - (yknot[1:-1] - yknot[:-2]) / h[:-1]
    )
    A = 2.0 * (h[:-1] + h[1:])
    C = h[1:]

    u = np.empty_like(A)
    z = np.empty_like(rhs)
    u[0], z[0] = A[0], rhs[0]
    for i in range(1, len(rhs)):
        li = C[i-1] / u[i-1]
        u[i]  = A[i] - li * C[i-1]
        z[i]  = rhs[i] - li * z[i-1]

    y2 = np.zeros(nk, dtype=float)
    if len(rhs) > 0:
        y2[-2] = z[-1] / u[-1]
        for i in range(len(rhs)-2, -1, -1):
            y2[i+1] = (z[i] - C[i] * y2[i+2]) / u[i]


    # --- 4) evaluate spline to get continuum cont ---
    cont = np.empty(n, dtype=float)
    for j in range(n):
        xp = j - 0.5
        idx = np.clip(np.searchsorted(xknot, xp) - 1, 0, nk-2)
        h_i = xknot[idx+1] - xknot[idx]
        a = (xknot[idx+1] - xp) / h_i
        b = (xp - xknot[idx])   / h_i
        logc = (
            a * yknot[idx]
          + b * yknot[idx+1]
          + ((a**3 - a)*y2[idx] + (b**3 - b)*y2[idx+1]) * (h_i**2) / 6.0
        )
        cont[j] = 10.0**logc


    # --- 5) form normalized residuals ---
    flat = np.zeros_like(flux)
    mask = (flux > 0) & (cont > 0)
    flat[mask] = flux[mask] / cont[mask] - 1.0

    return flat, cont


# hybrid method removed per request; strengthened gaussian edge handling is now default

def unflatten_on_loggrid(flat_tpl: np.ndarray,
                         cont: np.ndarray) -> np.ndarray:
    """
    Given a template flux on the log-λ grid that has been flattened
    (i.e. continuum removed), restore it by multiplying back the
    continuum model.  flat_tpl must be on the same log_wave grid as cont.
    """
    return (flat_tpl + 1.0) * cont


def pad_to_NW(arr: np.ndarray, NW: int) -> np.ndarray:
    """Return an NW-long view: arr left-justified, rest filled with 0."""
    if arr.size == NW:
        return arr                     # already full length
    out = np.zeros(NW, arr.dtype)
    out[:arr.size] = arr
    return out


def prep_template(tpl_wave: np.ndarray, flux_tpl: np.ndarray, skip_if_rebinned: bool = False) -> np.ndarray:
    """
    Rebin the template onto the log-λ grid.
    
    Parameters
    ----------
    tpl_wave : np.ndarray
        Template wavelength array
    flux_tpl : np.ndarray  
        Template flux array
    skip_if_rebinned : bool, optional
        If True, skip rebinning if flux is already on standard grid
        
    Returns
    -------
    np.ndarray
        Rebinned flux array
    """
    # Check if already rebinned to standard grid
    if skip_if_rebinned and len(flux_tpl) == NW:
        _LOG.debug("Template already rebinned to standard grid, skipping rebinning")
        return flux_tpl
    
    _, rebinned_flux = log_rebin(tpl_wave, flux_tpl)
    return rebinned_flux

def flatten_spectrum(wave: np.ndarray, flux: np.ndarray, 
                    apodize_percent: float = 5.0,
                    median_filter_type: str = "none",
                    median_filter_value: float = 0.0,
                    num_points: int = 1024) -> Dict[str, np.ndarray]:
    """
    Flatten a spectrum by removing continuum and applying log rebinning.
    
    Parameters:
        wave: Wavelength array
        flux: Flux array
        apodize_percent: Percentage of spectrum ends to apodize
        median_filter_type: Type of smoothing filter ("none", "pixel", "angstrom") 
                           Note: Now uses Savitzky-Golay filtering instead of median
        median_filter_value: Value for smoothing filter (window size or FWHM)
        num_points: Number of points in log grid
        
    Returns:
        Dict containing processed wavelength and flux arrays
    """
    # Apply apodization if requested (requires valid region indices)
    if apodize_percent > 0:
        try:
            valid_mask = (flux != 0) & np.isfinite(flux)
            if np.any(valid_mask):
                n1 = int(np.argmax(valid_mask))
                n2 = int(len(flux) - 1 - np.argmax(valid_mask[::-1]))
                flux = apodize(flux, n1, n2, percent=apodize_percent)
        except Exception:
            # If anything goes wrong, skip apodization
            pass
    
    # Apply Savitzky-Golay filtering if requested (replaces old median filtering)
    if median_filter_type != "none" and median_filter_value > 0:
        if median_filter_type == "pixel":
            # Pixel-based Savitzky-Golay filter (3rd order polynomial)
            window_length = max(3, int(median_filter_value))
            flux = savgol_filter_fixed(flux, window_length, polyorder=3)
    
    # Apply log rebinning (grid size comes from init_wavelength_grid)
    log_wave, log_flux = log_rebin(wave, flux)
    
    # Fit and remove continuum
    flat_flux, continuum = fit_continuum(log_flux, method="spline")
    
    return {
        'wave': log_wave,
        'flux': flat_flux,
        'continuum': continuum,
        'original_wave': wave,
        'original_flux': flux
    }

__all__ = [
    "init_wavelength_grid",
    "medfilt",
    "clip_aband", "clip_sky_lines", "clip_host_emission_lines",
    "apply_wavelength_mask",
    "log_rebin", "fit_continuum", "fit_continuum_spline", "apodize", "unflatten_on_loggrid", "prep_template", "flatten_spectrum",
]
