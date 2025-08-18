import numpy as np
import mne
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
from types import SimpleNamespace
from .helpers import (_compute_tep_peaks, _neigh_correction,
                     _validate_ntop, _validate_pick_ch,
                     _compute_timefreq)
from .timefreq import TimeFreq  # Import from sibling module

# -------------------------
# Core TEP Class
# -------------------------
class TEP:
    def __init__(self, epochs, exclude_channels=None,
                 p1_range=[0.01, 0.04], low_limit=35,
                 sign_corr='convexity'):
        """
        Initialize TEP object with automatic peak computation

        Args:
            epochs (mne.Epochs): Input epochs.
            exclude_channels (list[str] | None): Channel names to drop before processing.
            p1_range (list[float, float]): Search window for the first peak P1 in seconds.
                Default: [0.01, 0.04].
            low_limit (float): Maximum frequency (Hz) used to enforce a minimum separation
                between consecutive peaks:
                    min_interval = 1 / (2 * low_limit)  [seconds]
                Lower values enforce wider spacing; higher values allow closer peaks.
                Default: 35 (≈14 ms).
            sign_corr (str): Method for signal sign correction. Default: 'convexity'.
        """
        # Process epochs
        if np.any(exclude_channels):
            self.epochs = epochs.copy().drop_channels(exclude_channels)
        else:
            self.epochs = epochs.copy()

        # heuristic: data are either in V or µV: if data are in V, this condition is satisfied for typical EEG values
        if np.max(self.epochs._data) < 1e-3:
            self.epochs._data *= 1e6  # Convert to µV
        # Core data attributes
        self.tep_data = self.epochs.average()  # mne evoked object
        self.times = self.epochs.times
        self.ch_names = np.array(self.epochs.ch_names, dtype='object')

        # Create structured metadata container
        self.info = SimpleNamespace(
            n_channels=len(self.ch_names),
            n_epochs=len(self.epochs),
            sfreq=self.epochs.info['sfreq'],
            p1_range=p1_range,
            low_limit=low_limit,
            sign_corr=sign_corr
        )

        # Compute peaks immediately using helper function '_compute_tep_peaks'
        (self.idxs_peaks,
         self.amp_peaks,
         self.lat_peaks,
         self.amp_p2p,
         self.interpeak) = _compute_tep_peaks(
            times=self.times,
            tep_data=self.tep_data.get_data(),
            sfreq=self.info.sfreq,
            p1_range=p1_range,
            low_limit=low_limit,
            sign_corr=sign_corr
        )

    def __repr__(self):
        # Calculate time range
        time_range = (self.times[0], self.times[-1])
        time_str = f"{time_range[0]:.3f}-{time_range[1]:.3f}s"
        # Format sampling frequency
        sfreq_str = f"{self.info.sfreq:.1f} Hz"
        # Format peak detection parameters
        peak_info = (f"  P1 range: [{self.info.p1_range[0]:.3f}, {self.info.p1_range[1]:.3f}] s\n"
                     f"  Low limit: {self.info.low_limit} Hz\n"
                     f"  Sign correction: {self.info.sign_corr}")

        return (f"<TEP\n"
                f"  Channels: {self.info.n_channels}\n"
                f"  Epochs: {self.info.n_epochs}\n"
                f"  Time points: {len(self.times)}\n"
                f"  Time range: {time_str}\n"
                f"  Sampling: {sfreq_str}\n"
                f"  Peak detection:\n{peak_info}\n"
                f">")

    # -------------------------
    # Core Data Access Methods
    # -------------------------
    def get_epo(self, pick_ch=None):
        """
        Return epoched data as a NumPy array.
        
        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select.
                If None, all channels are returned.
        
        Returns:
            np.ndarray: Shape (n_epochs, n_channels_selected, n_times), in µV.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.epochs.get_data()[:, ch_idxs]
        return self.epochs.get_data()

    def get_tep(self, pick_ch=None):
        """
        Return the averaged TEP (Evoked) data as a NumPy array.
        
        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select.
                If None, all channels are returned.
        
        Returns:
            np.ndarray: Shape (n_channels_selected, n_times), in µV.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.tep_data.get_data()[ch_idxs]
        return self.tep_data.get_data()

    def get_gmfp(self, pick_ch=None):
        """
        Return the (global or local) mean field power over channels.
                
        Args:
            pick_ch (list[str | int] | None): Channel names or indices to define a local
                GMFP. If None, all channels are used (global GMFP).
        
        Returns:
            np.ndarray: Shape (n_times,), in µV.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return np.sqrt(np.mean(self.tep_data.get_data()[ch_idxs] ** 2, 0))
        return np.sqrt(np.mean(self.tep_data.get_data() ** 2, 0))

    # -------------------------
    # Feature Access Methods
    # -------------------------
    def get_amplitudes(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """
        Get peak amplitudes for P1, P2, P3.

        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select.
                If provided, `ntop` is ignored and channels are returned in the given order.
            ntop (int | None): Number of channels to return, ranked by P1–P2 peak-to-peak
                amplitude. If None, all channels are returned unsorted.
            neighbors_correction (bool): Enforce spatial contiguity of the ntop channels.
            verbose (bool): Print selection details.
        
        Returns:
            np.ndarray: Shape (n_channels_selected, 3), columns = [P1, P2, P3] in µV.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.amp_peaks[ch_idxs]

        if ntop is None or ntop == self.info.n_channels:
            return self.amp_peaks

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.amp_peaks[idxs_ntop]

    def get_latencies(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """
        Get peak latencies for P1, P2, P3.

        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select.
                If provided, `ntop` is ignored and channels are returned in the given order.
            ntop (int | None): Number of channels to return, ranked by P1–P2 peak-to-peak
                amplitude. If None, all channels are returned unsorted.
            neighbors_correction (bool): Enforce spatial contiguity of the ntop channels.
            verbose (bool): Print selection details.

        Returns:
            np.ndarray: Shape (n_channels_selected, 3), columns = [P1, P2, P3] in seconds.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.lat_peaks[ch_idxs]

        if ntop is None:
            return self.lat_peaks

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.lat_peaks[idxs_ntop]

    def get_peaktopeak(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """
        Get peak-to-peak amplitudes.
        
        Computes P1–P2 and P2–P3 peak-to-peak amplitudes.

        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select.
                If provided, `ntop` is ignored and channels are returned in the given order.
            ntop (int | None): Number of channels to return, ranked by P1–P2 peak-to-peak
                amplitude. If None, all channels are returned unsorted.
            neighbors_correction (bool): Enforce spatial contiguity of the ntop channels.
            verbose (bool): Print selection details.
    
        Returns:
            np.ndarray: Shape (n_channels_selected, 2), columns = [P1–P2, P2–P3] in µV.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.amp_p2p[ch_idxs]

        if ntop is None:
            return self.amp_p2p

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.amp_p2p[idxs_ntop]

    def get_interpeak(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """
        Get the inter-peak interval P3–P1.
        
        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select.
                If provided, `ntop` is ignored and channels are returned in the given order.
            ntop (int | None): Number of channels to return, ranked by P1–P2 peak-to-peak
                amplitude. If None, all channels are returned unsorted.
            neighbors_correction (bool): Enforce spatial contiguity of the ntop channels.
            verbose (bool): Print selection details.

        Returns:
            np.ndarray: Shape (n_channels_selected,), values = P3–P1 interval in seconds.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.interpeak[ch_idxs]

        if ntop is None:
            return self.interpeak

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.interpeak[idxs_ntop]

    def get_slope_peaks(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """
        Get slopes between consecutive peaks (µV/ms).
        
        Computes the slopes between P1–P2 and P2–P3:
            slope = (Δamplitude) / (Δlatency), with latency in milliseconds.

        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select.
                If provided, `ntop` is ignored and channels are returned in the given order.
            ntop (int | None): Number of channels to return, ranked by P1–P2 peak-to-peak
                amplitude. If None, all channels are returned unsorted.
            neighbors_correction (bool): Enforce spatial contiguity of the ntop channels.
            verbose (bool): Print selection details.

        Returns:
            np.ndarray: Shape (n_channels_selected, 2), columns = [P1–P2, P2–P3] in µV/ms.
        """
        slope = lambda x1, y1, x2, y2: np.divide((y2 - y1), (x2 - x1),
                                                 out=np.full_like(x1, np.inf, dtype=float),
                                                 where=(x2 != x1))
        lat_p1, lat_p2, lat_p3 = self.lat_peaks.T * 1e3  # from s to ms
        amp_p1, amp_p2, amp_p3 = self.amp_peaks.T
        slope_p1p2 = slope(lat_p1, amp_p1, lat_p2, amp_p2)
        slope_p2p3 = slope(lat_p2, amp_p2, lat_p3, amp_p3)
        slope_peaks = np.vstack((slope_p1p2, slope_p2p3)).T

        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return slope_peaks[ch_idxs]

        if ntop is None:
            return slope_peaks

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return slope_peaks[idxs_ntop]

    # -------------------------
    # Info selected channels
    # -------------------------
    def get_ntop_ch(self, ntop=4, neighbors_correction=True, verbose=False):
        """
        Get names of the top channels ranked by P1–P2 peak-to-peak amplitude.

        Args:
            ntop (int): Number of channels to return.
            neighbors_correction (bool): Enforce spatial contiguity of the ntop channels.
            verbose (bool): Print selection details.

        Returns:
            np.ndarray: Channel names, shape (ntop,).
        """
        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.ch_names[idxs_ntop]

    def get_ntop_idx(self, ntop=4, neighbors_correction=True, return_orig=False, verbose=False):
        """
        Get indices of the top channels ranked by P1–P2 peak-to-peak amplitude.

        Args:
            ntop (int): Number of channels to return.
            neighbors_correction (bool): Enforce spatial contiguity of the ntop channels.
            return_orig (bool): If True, also return the pre-correction indices.
            verbose (bool): Print selection details.

        Returns:
            np.ndarray | tuple[np.ndarray, np.ndarray]:
                If `return_orig` is False:
                    idxs_ntop: shape (ntop,)
                If `return_orig` is True:
                    (idxs_ntop, idxs_ntop_orig), each shape (ntop,).
        """
        # Get P1-P2 amplitudes (first column of amp_p2p)
        amp_p1p2 = self.amp_p2p[:, 0]
        # Get initial top channels based on amplitude
        idxs_ntop_orig = np.argsort(amp_p1p2)[::-1][:ntop]
        # Apply neighbor correction if requested
        if neighbors_correction:
            idxs_ntop, idxs_ntop_orig = _neigh_correction(
                self.epochs.info,
                amp_p1p2,
                idxs_ntop_orig
            )
        else:
            idxs_ntop = idxs_ntop_orig.copy()
        if verbose:
            if np.array_equal(idxs_ntop, idxs_ntop_orig):
                print(f'Neighbors correction not applied! Selected channels: {self.ch_names[idxs_ntop]}')
            else:
                print(f'New channels: {self.ch_names[idxs_ntop]}')
                print(f'Original channels: {self.ch_names[idxs_ntop_orig]}')
        if return_orig:
            return idxs_ntop, idxs_ntop_orig
        else:
            return idxs_ntop

    def info_ntop(self, ntop=4, neighbors_correction=True, verbose=False, ):
        """
        Summarize information about the top channels.

        Args:
            ntop (int): Number of channels to summarize.
            neighbors_correction (bool): Enforce spatial contiguity of the ntop channels.
            verbose (bool): Print selection details.
        
        Returns:
            dict: With keys
                - 'channels' (list[str]): Corrected top channel names.
                - 'channels_original' (list[str]): Original (pre-correction) channel names.
                - 'amplitudes' (np.ndarray): Shape (ntop, 3), [P1, P2, P3] in µV.
                - 'latencies' (np.ndarray): Shape (ntop, 3), [P1, P2, P3] in seconds.
                - 'peak_to_peak' (np.ndarray): Shape (ntop, 2), [P1–P2, P2–P3] in µV.
                - 'interpeaks' (np.ndarray): Shape (ntop,), P3–P1 in seconds.
                - 'slopes' (np.ndarray): Shape (ntop, 2), [P1–P2, P2–P3] in µV/ms.
        """
        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop, idxs_ntop_orig = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=True
        )

        return {
            'channels': self.ch_names[idxs_ntop].tolist(),
            'channels_original': self.ch_names[idxs_ntop_orig].tolist(),
            'amplitudes': self.amp_peaks[idxs_ntop],
            'latencies': self.lat_peaks[idxs_ntop],
            'peak_to_peak': self.amp_p2p[idxs_ntop],
            'interpeaks': self.interpeak[idxs_ntop],
            'slopes': self.get_slope_peaks(ntop=ntop, neighbors_correction=neighbors_correction)
        }

    # -------------------------
    # Visualization
    # -------------------------
    def plot_summary(self, ntop=4, tlim=(-100, 300), title='',
                     neighbors_correction=True, verbose=False,
                     cmap_topo='viridis', topo_lim=(0, None), contours=3, 
                     table_max_ch=4, figsize=(6,5),dpi=100):
        """
        Generate a summary figure for the TEP analysis on the selected channels.
        
        The figure includes:
            1) Time series of the averaged TEP for the top channels with detected peaks.
            2) A table of P1–P2–P3 latencies for the top channels.
            3) A topographic map of the P1–P2 peak-to-peak amplitude.
        

        Args:
            ntop (int): Number of top channels to display. Default: 4.
            tlim (tuple[float, float]): Time limits for the TEP plot in milliseconds.
            title (str): Figure title. Default: ''.
            neighbors_correction (bool): Enforce spatial contiguity of the top channels.
            verbose (bool): Print selection details.
            cmap_topo (str): Colormap for the topography. Default: 'viridis'.
            topo_lim (tuple[float | None, float | None]): Color scale limits (vmin, vmax).
                Use None to auto-scale. Default: (0, None).
            contours (int): (int | array_like): The number of contour lines to draw. 
                For further details, see mne.viz.plot_topomap
            table_max_ch (int): Maximum number of rows displayed in the latency table.
            figsize (tuple, optional): Figure dimensions in inches. Default: (6,5).
            dpi (int, optional): Figure resolution. Default: 300.


        Returns:
            matplotlib.figure.Figure: The created figure.

        Example:
            fig = tep.plot_summary(
                ntop=5,
                tlim=(-50, 250),
                title="Subject 01 - TEP Summary",
                cmap_topo='viridis',
                topo_lim=(0, 10)
            )
            fig.savefig('tep_summary.png')
        """

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False)

        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor='none')
        gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])

        ax = fig.add_subplot(gs[0, :])
        plt.suptitle(title)
        plt.grid()
        peak_col = ['darkred', 'red', 'salmon']
        for i, ch in enumerate(idxs_ntop):
            peaks_time = self.lat_peaks[ch]
            lab = self.ch_names[ch]
            ax.plot(self.times * 1e3, self.tep_data.get_data()[ch], label=lab, lw=2)
            for p in range(3):
                pks_plot = ax.plot(peaks_time[p] * 1e3, self.tep_data.get_data()[ch, self.idxs_peaks[ch, p]],
                                   'o', ms=6, zorder=6, color=peak_col[p])
            ax.set_xlim(tlim)
            ax.set_xlabel('time (ms)')
            ax.set_ylabel(r'amplitude ($\mu$V)')
            ax.legend(fontsize=6)
        ax.legend()
        ax.set_xticks(np.arange(tlim[0], tlim[1] + 1, step=50))
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')

        ax2 = fig.add_subplot(gs[1, 0])
        ax2.axis('off')
        col_labels = [f'P$_{n + 1}$' for n in range(3)]
        row_labels = self.ch_names[idxs_ntop]
        rcol = plt.get_cmap('tab10').colors[:ntop]
        rcol = [(r, g, b, 0.5) for (r, g, b) in rcol]
        ccol = [mcolors.to_rgba(c, alpha=0.5) for c in peak_col]
        table = ax2.table(cellText=np.round(self.lat_peaks[idxs_ntop][:table_max_ch] * 1e3, 1),
                          rowLabels=row_labels[:table_max_ch], colLabels=col_labels,
                          loc='center', cellLoc='center', bbox=[0, 0, 1, 1],
                          rowColours=rcol[:table_max_ch], colColours=ccol)
        for key, cell in table.get_celld().items():
            cell.get_text().set_fontsize(14)
        for col in range(len(col_labels)):
            table[(0, col)].get_text().set_fontweight('bold')
        for row in range(len(row_labels[:table_max_ch])):
            table[(row + 1, -1)].get_text().set_fontweight('bold')

        ax3 = fig.add_subplot(gs[1, 1])
        amp_p1p2 = self.amp_p2p[:, 0]
        im, cn = mne.viz.plot_topomap(amp_p1p2, self.epochs.info, axes=ax3, 
                                      names=self.ch_names, sensors=False, 
                                      cmap=cmap_topo, vlim=topo_lim, 
                                      contours=contours,show=False)
        cax = fig.colorbar(im, ax=ax3, shrink=0.5)
        cax.set_label(f'peak-to-peak ($\\mu$V)', fontsize=8)

        plt.subplots_adjust(wspace=0, hspace=0.05)
        plt.show()

        return fig

    def compute_timefreq(self, epochs=False, pick_ch=None, ntop=4, neighbors_correction=True,
                         fmin=4, fmax=45, compute_itc=False, 
                         baseline_correction=True, baseline_range=(-0.5,-0.1),
                         method='stock1', width=0.7, nfft=2048, n_jobs=None,
                         gamma=2, window='gauss', return_complex=False):
        """Compute time-frequency decomposition for EEG data.

        Args:
            epochs (bool): If True, time-frequency is computed on single trials (epochs). 
                If False, computed on averaged TEP
            pick_ch (list[str | int] | None): Channels to select (names or indices) for time-frequency computation. 
                Overrides ntop parameter when specified.
            ntop (int): Number of top channels to select based on P1-P2 amplitude. 
                Ignored if pick_ch is specified.
            neighbors_correction (bool): Apply spatial neighborhood correction in channel selection. 
                Enforce spatial contiguity of the ntop channels.
            fmin (float): Minimum frequency in Hz for analysis.
            fmax (float): Maximum frequency in Hz for analysis.
            compute_itc (bool): Compute inter-trial coherence.  It requires epochs=True.
            baseline_correction (bool): Apply baseline correction.
            baseline_range (tuple[float, float]): Time window [start, end] in seconds for baseline correction. 
            method (str): Time-frequency method:
                - 'stock1': MNE's Stockwell implementation
                - 'stock2': Alternative Stockwell implementation (https://github.com/claudiodsf/stockwell)
            width (float): Width parameter for Stockwell transform (stock1 method only). 
                Larger values improve frequency resolution at the cost of time precision.
            nfft (int): FFT length. Default: 2048.
            n_jobs (int | None): Number of parallel jobs (stock1 method only). None uses all available cores. 
            gamma (float): Gamma parameter for stock2 method only. 
                Larger values improve frequency resolution at the cost of time precision.
            window (str): Window type for stock2 method only. ('gauss' or 'kazemi')
            return_complex (bool): Return complex coefficients (stock2 method only).

        Returns:
            TimeFreq: Object containing time-frequency analysis results.
        """
        
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)

        else:
            ntop = _validate_ntop(ntop, self.info.n_channels)
            ch_idxs = self.get_ntop_idx(
                ntop=ntop,
                neighbors_correction=neighbors_correction,
                verbose=False,
                return_orig=False
            )

        if epochs:
            data = self.epochs.get_data()
        else:
            data = self.tep_data.get_data()

        # Get time-frequency results
        freqs, power, itc, s_transform = _compute_timefreq(data=data, times=self.times, ch_idxs=ch_idxs, sfreq=self.info.sfreq, 
                                                           fmin=fmin, fmax=fmax, compute_itc=compute_itc,
                                                           baseline_correction=baseline_correction, 
                                                           baseline_range=baseline_range, method=method, 
                                                           width=width, nfft=nfft, n_jobs=n_jobs, gamma=gamma,
                                                           window=window, return_complex=return_complex)
        
        return TimeFreq(freqs=freqs, times=self.times, power=power,
                        itc=itc, complex_coeff=s_transform,
                        ch_names=self.ch_names[ch_idxs], method=method,
                        baseline_correction=baseline_correction,
                        baseline_range=baseline_range, computed_on_epochs=epochs, 
                        sfreq=self.info.sfreq, tep_data=self.tep_data)
