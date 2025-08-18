import numpy as np
from scipy.signal import find_peaks
from scipy.sparse.csgraph import connected_components
import mne

# -------------------------
# Helper functions
# -------------------------
def _get_peaks_and_troughs(signal_array):
    """Identify peaks and troughs in a 1D signal.

    Args:
        signal_array: 1D input signal array.

    Returns:
        peaks: Indices of detected peaks.
        troughs: Indices of detected troughs.
    """
    diff = np.diff(signal_array)
    peaks = np.where((diff[:-1] > 0) & (diff[1:] <= 0))[0] + 1
    troughs = np.where((diff[:-1] < 0) & (diff[1:] >= 0))[0] + 1
    # fill with (-)inf when there are no peaks and/or troughs:
    # it serves for dealing with signal polarity (sign_corr == 'peaks_troughs')
    if len(peaks) == 0 and len(troughs) == 0:
        # assume peak (-np.inf) before a trough (np.inf)
        peaks = np.array([-np.inf])
        troughs = np.array([np.inf])
    elif len(peaks) == 0:
        peaks = np.array([np.inf])  # assume peak (np.inf) after the trough (int)
    elif len(troughs) == 0:
        troughs = np.array([np.inf])  # assume trough (np.inf) after the peak (int)
    return peaks, troughs


def _compute_tep_peaks(times, tep_data, sfreq, p1_range, low_limit, sign_corr):
    """Core peak detection algorithm for TEP analysis.

    Args:
        times: Time vector (1D array).
        tep_data: TEP data array (channels × times).
        sfreq: Sampling frequency (Hz).
        p1_range: Time window for P1 peak detection [start, end] in seconds.
        low_limit: Maximum frequency (Hz) for minimum peak separation.
            Determines the minimum time interval between consecutive peaks as:
                        min_interval = 1/(low_limit * 2) seconds
            Lower values enforce stricter temporal separation (wider peak spacing).
            Higher values allow closer peak detection (tighter peak spacing).
            (Default: 35 Hz ≈ 14 ms separation)
        sign_corr: Method for signal correction ('convexity' or 'peaks_troughs').

    Returns:
        idxs_peaks: Peak indices (channels × 3).
        amp_peaks: Peak amplitudes (µV) (channels × 3).
        lat_peaks: Peak latencies (s) (channels × 3).
        amp_p2p: Peak-to-peak amplitudes (µV) (channels × 2).
        interpeak: P3-P1 intervals (s) per channel.
    """
    n_channels = tep_data.shape[0]
    amp_peaks = np.zeros((n_channels, 3))
    idxs_peaks = np.zeros((n_channels, 3), dtype=int)
    lat_peaks = np.zeros((n_channels, 3))
    amp_p2p = np.zeros((n_channels, 2))
    interpeak = np.zeros((n_channels))

    # Time indices for p1 range
    p1_range = np.arange(np.where(times >= p1_range[0])[0][0],
                         np.where(times <= p1_range[1])[0][-1] + 1)

    # Determine sign correction
    if sign_corr == 'convexity':
        midpoint = p1_range[len(p1_range) // 2]
        sign_tep = np.sign(tep_data[:, midpoint] -
                           (tep_data[:, p1_range[0]] + tep_data[:, p1_range[-1]]) / 2)

    elif sign_corr == 'peaks_troughs':
        sign_tep = np.array([np.sign(t[0] - p[0])
                             for p, t in (_get_peaks_and_troughs(tep_data[ch, p1_range])
                                          for ch in range(n_channels))])
    # Main peak detection
    half_lim = int((1 / (low_limit * 2)) / (1 / sfreq))  # minimum time interval between consecutive peaks (in samples)
    end = len(times)
    for ch in range(n_channels):
        tep_corrected = tep_data[ch] * sign_tep[ch]
        p_idxs, _ = find_peaks(tep_corrected)
        p_peaks = np.intersect1d(p_idxs, p1_range, assume_unique=True)
        if len(p_peaks) > 0:
            # First peak
            p1 = p_peaks[0]
            # Trough detection
            pinv_idxs = find_peaks(-tep_corrected)[0]
            # Second peak (trough)
            p2_range = np.arange(p1 + half_lim, end)
            p2_ = np.intersect1d(pinv_idxs, p2_range, assume_unique=True)
            if len(p2_) == 0: continue  # skip this channel
            p2 = p2_[0]
            # Third peak
            p3_range = np.arange(p2 + half_lim, end)
            p3_ = np.intersect1d(p_idxs, p3_range, assume_unique=True)
            if len(p3_) == 0: continue  # skip this channel
            p3 = p3_[0]
            # Store results
            idxs_peaks[ch] = [p1, p2, p3]
            amp_peaks[ch] = [tep_data[ch, p1], tep_data[ch, p2], tep_data[ch, p3]]
            lat_peaks[ch] = [times[p1], times[p2], times[p3]]
            amp_p2p[ch] = [np.abs(tep_data[ch, p1] - tep_data[ch, p2]),
                           np.abs(tep_data[ch, p2] - tep_data[ch, p3])]
            interpeak[ch] = times[p3] - times[p1]

    return idxs_peaks, amp_peaks, lat_peaks, amp_p2p, interpeak


def _neigh_correction(info, amp_p1p2, idxs_ntop):
    """Apply spatial neighbor correction to channel selection.

    Args:
        info: MNE info object containing channel adjacency.
        amp_p1p2: P1-P2 amplitudes per channel.
        idxs_ntop: Indices of top channels before correction.

    Returns:
        idxs_ntop: Corrected channel indices after neighbor check.
        idxs_ntop_old: Original channel indices before correction.
    """
    ntop = len(idxs_ntop)
    old_verbose = mne.set_log_level('WARNING')  # Suppress output
    adj = mne.channels.find_ch_adjacency(info, 'eeg')[0].toarray()
    mne.set_log_level(old_verbose)  # Restore level
    np.fill_diagonal(adj, 0)
    # adjacency with only the ntop channels
    sub_adj = adj[idxs_ntop][:, idxs_ntop]
    # get the connected components in the sub_adj
    n_cc, lab_cc = connected_components(sub_adj, directed=False)
    idxs_ntop_old = idxs_ntop.copy()
    if n_cc > 1:
        un_labs, un_counts = np.unique(lab_cc, return_counts=True)
        # find the chs outside the "main" connected component (cc). The main component is the one containing the ch with the largest p1p2 amp
        non_neighbors = np.where(lab_cc != lab_cc[0])[
            0]  # [0] is the first ch in the sorted set: ch with the largest p1p2 amp
        # only the chs in the selected cc are retained
        idxs_ntop = np.delete(idxs_ntop, non_neighbors)
        # the potential neighbors are the chs with at least 1 connection with the chs in idxs_ntop
        pot_neighbors = np.where(np.any(adj[idxs_ntop], axis=0))[0]
        # remove the chs already present in idxs_ntop
        pot_neighbors = np.setdiff1d(pot_neighbors, idxs_ntop)
        # sort the pot_neighbors based on their p1-to-p2 ampl
        pot_neighbors_sorted = pot_neighbors[amp_p1p2[pot_neighbors].argsort()[::-1]]
        # extend the idxs_ntop with the pot_neighbors_sorted to get ntop chs in idxs_ntop
        to_add = pot_neighbors_sorted[:ntop - len(idxs_ntop)]
        idxs_ntop = np.append(idxs_ntop, to_add)
        # if there are not enough pot_neighbors, readd the delated non-neighbors
        if len(idxs_ntop) < ntop:
            non_neighbors = np.setdiff1d(idxs_ntop_old, idxs_ntop)
            non_neighbors_sorted = non_neighbors[amp_p1p2[non_neighbors].argsort()[::-1]]
            to_add = non_neighbors_sorted[:ntop - len(idxs_ntop)]
            idxs_ntop = np.append(idxs_ntop, to_add)
    return idxs_ntop, idxs_ntop_old


def _validate_ntop(ntop, n_channels):
    """Validate ntop parameter.

    Args:
        ntop: Number of top channels requested.
        n_channels: Total number of available channels.

    Returns:
        ntop: Validated ntop value.
    """
    if not isinstance(ntop, int):
        raise ValueError(f"ntop must be integer, got {type(ntop)}")
    if ntop <= 0:
        raise ValueError(f"ntop must be positive integer, got {ntop}")
    if ntop > n_channels:
        raise ValueError(f"ntop ({ntop}) exceeds channel count ({n_channels})")
    return ntop


def _validate_pick_ch(ch_spec, ch_names):
    """Convert channel specification to integer indices.

    Args:
        ch_spec: Channel specification (str, int, list, tuple, or array).
        ch_names: List of all channel names.

    Returns:
        indices: Validated integer indices.
    """
    ch_names = list(ch_names)
    if not isinstance(ch_spec, (list, tuple, np.ndarray)):
        ch_spec = [ch_spec]
    indices = []
    for ch in ch_spec:
        if isinstance(ch, str):
            if ch in ch_names:
                indices.append(ch_names.index(ch))
            else:
                raise ValueError(f"Channel '{ch}' not found. Available: {ch_names}")
        elif isinstance(ch, int):
            if 0 <= ch < len(ch_names):
                indices.append(ch)
            else:
                raise ValueError(f"Index {ch} out of range (0-{len(ch_names) - 1})")
        else:
            raise TypeError(f"Invalid channel spec type: {type(ch)}. Use str or int")
    return indices


def _compute_timefreq(data, times, ch_idxs, sfreq, fmin, fmax, compute_itc=False,
                      baseline_correction=True, baseline_range=(-0.5, -0.1),
                      method='stock1', width=0.7, nfft=2048, n_jobs=None,
                      gamma=2, window='gauss', return_complex=False):
    """Compute time-frequency decomposition for EEG data

    Args:
        data: Input EEG data array (channels × times) or (epochs × channels × times)
        times: Time vector (1D array)
        sfreq: Sampling frequency (Hz)
        ch_idxs: Channel indices to include
        fmin: Minimum frequency (Hz)
        fmax: Maximum frequency (Hz)
        compute_itc: Compute inter-trial coherence (default: False)
        baseline_correction: Apply baseline correction (default: True)
        baseline_range: Time window for baseline (s)
        method: 'stock1' (MNE) or 'stock2'
        width: Width parameter for Stockwell transform (stock1)
        nfft: FFT length
        n_jobs: Number of parallel jobs (stock1)
        gamma: Gamma parameter for stock2
        window: Window type for stock2
        return_complex: Return complex coefficients (default: False); valid only for stock2

    Returns:
        freqs: Frequency vector (Hz)
        power: Time-frequency power (epochs × channels × freqs × times)
               The output is always 4D even if data is a TEP and the computation is on a single channel
        itc: Inter-trial coherence [0-1] (channels × freqs × times) (if compute_itc=True, else None)
        s_transform: Complex Stockwell coefficients (epochs × channels × freqs × times) (if return_complex=True, else None)
    """

    if data.ndim == 2:
        # when data is a TEP data, add a dummy dimension for epochs (for compatibility)
        data = data[np.newaxis]

    if method not in ['stock1', 'stock2']:
        raise ValueError(f"Invalid method '{method}'. Choose 'stock1' or 'stock2'")

    if method == 'stock1':
        # https://mne.tools/stable/generated/mne.time_frequency.tfr_array_stockwell.html
        power, itc, freqs = mne.time_frequency.tfr_array_stockwell(data=data[:, ch_idxs], sfreq=sfreq,
                                                                   fmin=fmin, fmax=fmax, n_fft=nfft,
                                                                   width=width, return_itc=compute_itc,
                                                                   n_jobs=n_jobs, decim=1, verbose=None)
        # mne method always average across epochs, we want to keep the epochs axis (epochs, channels, freqs, times); also when data is a TEP.
        power = power[np.newaxis]
        # mne function doesn't output the complex coefficients
        s_transform = None
        # if there is only a single epoch (such as when data is a TEP), itc cannot be estimated
        if data.shape[0] == 1:
            itc = None

    elif method == 'stock2':
        # https://github.com/claudiodsf/stockwell
        freqs, power, itc, s_transform = _stockwell_transform(data=data, times=times,
                                                              ch_idxs=ch_idxs, sfreq=sfreq,
                                                              fmin=fmin, fmax=fmax, nfft=nfft,
                                                              compute_itc=compute_itc, gamma=gamma,
                                                              window='gauss', return_complex=return_complex)

    if baseline_correction:
        power = _baseline_subtraction(power=power, times=times, baseline_range=baseline_range)

    return freqs, power, itc, s_transform


def _stockwell_transform(data, times, ch_idxs, sfreq, fmin, fmax, compute_itc=False,
                         nfft=2048, gamma=2, window='gauss', return_complex=False):
    """Compute Stockwell transform (method 'stock2').

    Args:
        data: Input EEG data (epochs × channels × times).
        times: Time vector (1D array).
        ch_idxs: Channel indices to include.
        sfreq: Sampling frequency (Hz).
        fmin: Minimum frequency (Hz).
        fmax: Maximum frequency (Hz).
        compute_itc: Compute inter-trial coherence (default: False).
        nfft: FFT length (default: 2048).
        gamma: Gamma parameter for Stockwell (default: 2).
        window: Window type (default: 'gauss').
        return_complex: Return complex coefficients (default: False).

    Returns:
        freqs: Frequency vector (Hz).
        power: Power spectrum (epochs × channels × freqs × times).
        itc: Inter-trial coherence (channels × freqs × times) or None.
        s_transform: Complex coefficients or None.
    """
    from stockwell import st

    # prepare data and parameters
    dt = 1. / sfreq
    original_N = len(times)
    if nfft > original_N:
        data = np.pad(data, ((0, 0), (0, 0), (0, nfft - original_N)), mode='constant')  # zero padding
        N = nfft
    else:
        N = original_N
    df = 1. / (N * dt)
    fmin_samples = int(fmin / df)
    fmax_samples = int(fmax / df)
    freqs = np.arange(fmin_samples, fmax_samples + 1) * df

    # perform stockwell transform
    s_transform = np.array([[st.st(epoch[ch],
                                   fmin_samples,
                                   fmax_samples,
                                   gamma=gamma,
                                   win_type=window) for ch in ch_idxs] for epoch in data])[...,
                  :original_N]  # trim padded zeros

    # extract
    power = np.abs(
        s_transform) ** 2  # shape: (epochs, channels, freqs, times). If data is a TEP, epochs dimension is 1.
    if compute_itc:
        if s_transform.shape[0] > 1:  # shape: (epochs, channels, freqs, times)
            phase_vectors = s_transform / np.abs(s_transform)
            itc = np.abs(np.mean(phase_vectors, axis=0))  # shape: (channels, freqs, times)
        else:
            raise ValueError("ITC computation requires multiple epochs.")
    else:
        itc = None
    if not return_complex:
        s_transform = None

    return freqs, power, itc, s_transform


def _baseline_subtraction(power, times, baseline_range):
    """Apply baseline correction to time-frequency power data.

    Args:
        power: time-frequency power data array (last dimension must be times).
        times: Time vector (1D array).
        baseline_range: Baseline time window [start, end] in seconds.

    Returns:
        power: Baseline-corrected power data.
    """
    baseline_mask = (times >= baseline_range[0]) & (times <= baseline_range[1])
    if not np.any(baseline_mask):
        raise ValueError(f"No samples in baseline range {baseline_range}")
    baseline_mean = power[..., baseline_mask].mean(axis=-1, keepdims=True)
    return power - baseline_mean


def _power_summation(power, times, window_range):
    """Sum power over a specified time window.

    Args:
        power: Power data array.
        times: Time vector in seconds (1D array).
        window_range: Time window [start, end] in seconds.

    Returns:
        summed_power: Power summed over window_range.
    """
    window_mask = (times >= window_range[0]) & (times <= window_range[1])
    if not np.any(window_mask):
        raise ValueError(f"No samples in window range {window_range}")
    return power[..., window_mask].sum(axis=-1)


def _return_bands_idxs(freqs):
    """Define frequency band indices and labels.

    Args:
        freqs: Frequency vector (Hz).

    Returns:
        bands: List of boolean masks for frequency bands.
        bands_lab: List of band labels (Greek symbols).
    """
    bands_lab = [r'$\theta$', r'$\alpha$', r'$\beta 1$', r'$\beta 2$', r'$\gamma$']
    if freqs.min() > 7.5:
        bands_lab = bands_lab[1:]
        alpha = (freqs >= freqs[0]) & (freqs <= 13)
        beta1 = (freqs >= freqs[alpha][-1]) & (freqs <= 20)
        beta2 = (freqs >= freqs[beta1][-1]) & (freqs <= 30)
        gamma = freqs >= freqs[beta2][-1]
        bands = [alpha, beta1, beta2, gamma]
    else:
        theta = (freqs >= freqs[0]) & (freqs <= 8)
        alpha = (freqs >= freqs[theta][-1]) & (freqs <= 13)
        beta1 = (freqs >= freqs[alpha][-1]) & (freqs <= 20)
        beta2 = (freqs >= freqs[beta1][-1]) & (freqs <= 30)
        gamma = freqs >= freqs[beta2][-1]
        bands = [theta, alpha, beta1, beta2, gamma]
    return bands, bands_lab
