import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from types import SimpleNamespace
from .helpers import (_return_bands_idxs, _baseline_subtraction, 
                     _power_summation, _validate_pick_ch)

# -------------------------
# Core TimeFreq Class
# -------------------------
class TimeFreq:
    """Container for time-frequency analysis results"""
    def __init__(self, freqs, times, power, itc=None, complex_coeff=None, 
                 ch_names=None, method=None, baseline_correction=None, 
                 baseline_range=None, computed_on_epochs=None, 
                 sfreq=None, tep_data=None):
        """
        Initialize TimeFreq object with time-frequency analysis results.
        
        Args:
            freqs (array_like): Frequency vector (1D array) in Hz.
            times (array_like): Time vector (1D array) in seconds.
            power (np.ndarray): Power spectrum array (4D: epochs × channels × freqs × times).
            itc (np.ndarray): Inter-trial coherence array (3D: channels × freqs × times).
            complex_coeff (np.ndarray): Complex time-frequency coefficients (4D).
            ch_names (list of str): Channel names.
            method (str): Method used ('stock1' or 'stock2').
            baseline_correction (bool): Whether baseline correction was applied.
            baseline_range (tuple): Baseline time range [start, end] in seconds.
            computed_on_epochs (bool): Whether computed on single trials (epochs).
            sfreq (float): Sampling frequency in Hz.
            tep_data (object): TEP data object containing sensor information.
        """
        # Core data arrays
        self.freqs = freqs
        self.times = times
        self.power = power
        self.itc = itc
        self.complex_coeff = complex_coeff
        self.ch_names = ch_names
        self.tep_data = tep_data
        
        # Create structured metadata container
        self.info = SimpleNamespace(
            method=method,
            baseline_correction=baseline_correction,
            baseline_range=baseline_range if baseline_correction else (None, None),
            computed_on_epochs=computed_on_epochs,
            n_epochs=power.shape[0],
            n_channels=power.shape[1],
            n_freqs=len(freqs),
            n_times=len(times),
            sfreq = sfreq
        )
        
    def __repr__(self):
        # Calculate time and frequency ranges
        time_range = (self.times[0], self.times[-1])
        freq_range = (self.freqs[0], self.freqs[-1])
        # Format time and frequency ranges with units
        time_unit = "s"
        time_str = f"{time_range[0]:.3f}-{time_range[1]:.3f}{time_unit}"
        freq_unit = "Hz"
        freq_str = f"{freq_range[0]:.1f}-{freq_range[1]:.1f}{freq_unit}"
        # Format sampling frequency
        sfreq_str = f"{self.info.sfreq:.1f} Hz"
        
        return (f"<TimeFreq\n"
                f"  Dimensions: {self.info.n_epochs} epochs × {self.info.n_channels} channels × "
                f"{self.info.n_freqs} freqs × {self.info.n_times} times\n"
                f"  Time range: {time_str}\n"
                f"  Frequency range: {freq_str}\n"
                f"  Sampling: {sfreq_str}\n"
                f"  Method: {self.info.method}\n"
                f"  Baseline: {'Applied' if self.info.baseline_correction else 'None'} "
                f"{self.info.baseline_range if self.info.baseline_correction else ''}\n"
                f"  Computed on: {'epochs' if self.info.computed_on_epochs else 'TEP'}\n"
                f"  ITC: {'Computed' if self.itc is not None else 'Not available'}\n"
                f"  Complex coefficients: {'Available' if self.complex_coeff is not None else 'Not available'}\n"
                f">")

        
    # -------------------------
    # Core Access Methods
    # -------------------------
    def get_power(self, pick_ch=None, average_channels=False):
        """
        Retrieve time-frequency power data.
    
        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select. If None, all channels are returned.
            average_channels (bool): If True, average across selected channels before returning.
    
        Returns:
            np.ndarray: Power array with dimensions depending on `pick_ch` and `average_channels`.
        """
        power_data = self.power.copy()
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            power_data = power_data[:,ch_idxs]
        if average_channels:
            power_data = power_data.mean(1)     
        return power_data
    
    def get_itc(self, pick_ch=None, average_channels=False):
        """
        Retrieve inter-trial coherence (ITC).
    
        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select. If None, all channels are returned.
            average_channels (bool): If True, average across selected channels before returning. 
            
        Returns:
            np.ndarray or None: ITC array with dimensions depending on `pick_ch` and `average_channels`. Returns None if ITC was not computed.
        """
        if self.itc is None:
            print("ITC has not been computed.")
            return None
        itc_data = self.itc.copy()
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            itc_data = itc_data[ch_idxs]
        if average_channels:
            itc_data = itc_data.mean(0)
        return itc_data
    
    def get_complex(self, pick_ch=None):
        """
        Retrieve complex coefficients of the Stockwell transform.
    
        Args:
            pick_ch (list[str | int] | None): Channel names or indices to select. If None, all channels are returned.
            
        Returns:
            np.ndarray or None: Complex coefficient array with dimensions depending on `pick_ch`. Returns None if complex coefficients are not available.
        """
        if self.complex_coeff is None:
            print("Complex coefficients are not available.")
            return None
        complex_data = self.complex_data.copy()
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            complex_data = complex_data[:,ch_idxs]
        return complex_data
    
    # -------------------------
    # Analysis Methods
    # -------------------------
    def get_evoked_spectrum(self, pick_ch=None, average_channels=True, sum_window=(0.02,0.12), baseline_range=(-0.5,-0.1), return_power=False):
        """
        Compute evoked power spectrum by summing time-frequency power over a specified time window.
            
        Args:
            pick_ch (list[str | int] | None): Channel name(s) to include. If None, all channels are included.
            average_channels (bool): Average channels before computing spectrum.
            sum_window (tuple of float): Start and end times (s) to sum the power. 
            baseline_range (tuple of float): Time range (s) for baseline correction if not already applied. 
            return_power (bool): If True, also return the baseline-corrected time-frequency power array 
                from which the evoked power spectrum is derived.
            
        Returns:
            np.ndarray or tuple: Evoked power spectrum 1D array (freqs,); 
                                 optionally a tuple (evoked_power, baseline-corrected time-frequency power).
                                 
        Notes:
            Baseline subtraction is applied only if not already applied in the TimeFreq object.
        """
        power_data = self.power.copy()
        if not self.info.baseline_correction:
            power_data = _baseline_subtraction(power=power_data, times=self.times, baseline_range=baseline_range)  
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            power_data = power_data[:,ch_idxs]
        power_data = power_data.mean(0) # average epochs; it only affects if n epochs > 1, otherwise it is a squeezing
        if average_channels:
            power_data = power_data.mean(0) # channels; it only affects if n channels > 1, otherwise it is a squeezing
        evoked_spectrum = _power_summation(power=power_data, times=self.times, window_range=sum_window)
        if return_power:
            return evoked_spectrum, power_data
        else:
            return evoked_spectrum

    
    def get_natfreq(self, natfreq_window=(0.02,0.12), pick_ch=None, average_channels=True, baseline_range=(-0.5,-0.1)):
        """
        Compute the natural frequency as the frequency with maximal power in the evoked power spectrum.
    
        Args:
            natfreq_window (tuple of float): Time window (s) used to compute the natural frequency. 
                It corresponds to the summation window of the evoked power spectrum. 
            pick_ch (list[str | int] | None): Channel name(s) to include. If None, all channels are included.
            average_channels (bool): If True, average power across channels before analysis. 
            baseline_range (tuple of float): Time range (s) for baseline correction if not already applied.
    
        Returns:
            float: Natural frequency (Hz) corresponding to the peak of the evoked power spectrum.
        """
        evoked_spectrum = self.get_evoked_spectrum(pick_ch=pick_ch, average_channels=average_channels, 
                                                   sum_window=natfreq_window, baseline_range=baseline_range)
        
        natfreq_idx = np.argmax(evoked_spectrum, axis=-1)
        return self.freqs[natfreq_idx]
    
    # -------------------------
    # Visualization
    # -------------------------
    def plot_natfreq1(self, natfreq_window=(0.02,0.12), pick_ch=None,
                      baseline_range=(-0.5, -0.1), plot_tlim=(-0.1, 0.3), 
                      ch_tep=None, ch_lab_tep=None, ch_color_tep=None,
                      color_spectrum='tab:blue', color_butterfly='gray',
                      cmap='RdBu_r', plot_ms=True, figsize=(7,6), dpi=100,
                      label_cbar=r'$\Delta$power ($\mu V^2$)'):        
        """
        Plot natural frequency analysis (multi-panel version).
        
        The figure includes:
            1) Butterfly plot of TEPs with highlighted channels
            2) Sensor topography of selected channels
            3) Time-frequency representation
            4) Evoked spectrum with frequency bands
            
        Args:
            natfreq_window (tuple of float): Time window (s) used to compute the natural frequency. 
                It corresponds to the summation window of the evoked power spectrum. 
            pick_ch (list[str | int] | None): Channel name(s) to include. If None, all channels are included.
            baseline_range (tuple of float): Time range (s) for baseline correction if not already applied.
            plot_tlim (tuple): Plot time limits [start, end] in seconds.
            ch_tep (list[str | int] | None): Channel name(s) to highlight in butterfly plot. 
                If None, all the channels in the TimeFreq object are highlighted.
            ch_lab_tep (list[str | int] | None): Labels for highlighted channels.
                If None, the labels of the channels in the TimeFreq object are used.
            ch_color_tep (list of str | None): Colors for highlighted channels.
                It should have the same length of ch_tep. If None, colors from XKCD palette are used.
            color_spectrum (str): Color for frequency bands. 
            color_butterfly (str): Color for background TEPs. 
            cmap (str): Colormap for time-frequency plot.
            plot_ms (bool): Display time in milliseconds.
            figsize (tuple): Figure dimensions in inches.
            dpi (int): Figure resolution.
            label_cbar (str): Colorbar label. Default: r'$\Delta$power ($\mu V^2$)'.
            
        Returns:
            matplotlib.figure.Figure: The generated figure object.

        Notes:
            - `pick_ch` uses the channels present in the TimeFreq object (the channels used for time-frequency computation)
            - `ch_tep` uses all channels from the original TEP data object, which may differ from TimeFreq channels
            - Best practice is to use `ch_tep=None` to highlight exactly the same channels used for time-frequency analysis
            - When selecting a single channel with `pick_ch`, to highlight its TEP provide the channel name (str) in 
              `ch_tep` to ensure correct matching
            - Channel indices may differ between TimeFreq and TEP objects - using names (str) is more reliable than indices
        """
        # prepare data
        bands, bands_lab = _return_bands_idxs(self.freqs)
        if any(sum(b) <= 1 for b in bands):
            raise ValueError(f"Insufficient frequency bands detected. Requires theta to gamma range (or alpha to gamma range). Actual frequency range {self.freqs[0]:.1f}-{self.freqs[-1]:.1f}Hz")

        evoked_spectrum, power_data = self.get_evoked_spectrum(pick_ch=pick_ch, 
                                                       average_channels=True, 
                                                       sum_window=natfreq_window, 
                                                       baseline_range=baseline_range,
                                                       return_power=True)
        natfreq_idx = np.argmax(evoked_spectrum)
        natfreq = self.freqs[natfreq_idx]
        window_mask = (self.times>=natfreq_window[0]) & (self.times<=natfreq_window[1])
        vmax = np.percentile(power_data[:,window_mask],95)
        vmin = -vmax
        tlim_mask = (self.times>=plot_tlim[0]) & (self.times<=plot_tlim[1])
        t = self.times[tlim_mask]
        tep_to_plot = self.tep_data.get_data()[...,tlim_mask]
        if ch_tep is None:
            ch_tep = list(self.ch_names)  
        if ch_lab_tep is None:
            ch_lab_tep = list(self.ch_names)  

        # Create figure
        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=None)
        gs = fig.add_gridspec(3, 23)

        # --- plot the TEP ---
        ax_tep = fig.add_subplot(gs[0,:15], facecolor='None')
        # background TEP
        ax_tep.plot(t,tep_to_plot.T, c=color_butterfly, alpha=0.2, lw=0.5)
        if ch_tep:
            # channels to highlight 
            for i,ch in enumerate(ch_tep):
                if isinstance(ch, str): ch = self.tep_data.ch_names.index(ch)
                if not ch_color_tep: ch_color_tep = list(mcolors.XKCD_COLORS)[::-1]
                lab = ch_lab_tep[i] if ch_lab_tep else None
                ax_tep.plot(t,tep_to_plot[ch], c=ch_color_tep[i], label=lab)
            if ch_lab_tep: 
                ax_tep.legend(loc='best', frameon=False, fontsize=8)
        ax_tep.set_xlim(plot_tlim[0], plot_tlim[1])
        ax_tep.axvline(0, ymax=1, ls='--', c='k', lw=0.8)
        ax_tep.plot(0,max(tep_to_plot.max()+1,5), 'v', c='r', ms=8 )
        ax_tep.text(0,max(tep_to_plot.max()+1,5), 'TMS', ha='center', va='bottom')
        ax_tep.set_ylim(tep_to_plot.min()-1, tep_to_plot.max()+1)
        ax_tep.set_axis_off()

        # --- plot the yscale of the TEP ---
        ax_scale = fig.add_subplot(gs[0,15], sharey=ax_tep, facecolor='None')
        ax_scale.set_xlim(0,1)
        ax_scale.vlines(0.4, -5, 5, 'k', lw=1.5)
        ax_scale.text(0.55, 0, r'10 $\mu V$', ha='left', va='center', 
                rotation='vertical', weight='regular', fontsize=10)
        ax_scale.set_axis_off()

        # --- plot the selected sensors ---
        if ch_tep:
            ax_sens = fig.add_subplot(gs[0,15:], facecolor='None')
            im = self.tep_data.plot_sensors(axes=ax_sens, verbose=False, show_names=False)
            ch_points = ax_sens.collections[0]
            ch_clr = ch_points.get_facecolor()
            ch_sizes = np.repeat(1,len(self.tep_data.ch_names))
            for i,ch in enumerate(ch_tep):
                if isinstance(ch, str): ch = self.tep_data.ch_names.index(ch)        
                ch_clr[ch] = mcolors.to_rgba(ch_color_tep[i])
                ch_sizes[ch] = 10
            ch_points.set_color(ch_clr)
            ch_points.set_sizes(ch_sizes)
            ax_sens.set_ylim(bottom=ax_sens.get_ylim()[0] - abs(ax_sens.get_ylim()[0] - ax_sens.get_ylim()[1])/10)
            ax_sens.set_xlim(left=ax_sens.get_xlim()[0] - abs(ax_sens.get_xlim()[0] - ax_sens.get_xlim()[1])/5)

        # --- Time-Frequency Plot ---
        ax_tf = fig.add_subplot(gs[1:,:15], facecolor='None')
        if plot_ms:
            times = self.times * 1000
            plot_tlim = (plot_tlim[0]*1000, plot_tlim[1]*1000)
            xlab = 'time (ms)'
        else:
            times = self.times
            xlab = 'time (s)'
        pcm = ax_tf.pcolormesh(times, self.freqs, power_data, cmap=cmap, shading='gouraud', rasterized=True, vmin=vmin, vmax=vmax)
        ax_tf.axvline(0, ls='--', c='k', lw=0.8)
        ax_tf.set_xlim(plot_tlim[0], plot_tlim[1])
        ax_tf.set_ylim(self.freqs[0], self.freqs[-1])
        ax_tf.set_xlabel(xlab)
        ax_tf.set_ylabel('frequency (Hz)')

        # --- Colorbar ---
        ax_cb=fig.add_subplot(gs[1:,22], facecolor='None')
        cb = plt.colorbar(pcm, cax=ax_cb, aspect=1)
        cb.set_label(label_cbar)

        # --- Spectrum Plot ---
        ax_spec=fig.add_subplot(gs[1:,15:20], facecolor='None')
        ax_bands=fig.add_subplot(gs[1:,20:22], sharey=ax_spec, facecolor='None')
        ax_spec.plot(-evoked_spectrum, self.freqs, c='k' )
        ax_spec.plot(-evoked_spectrum[natfreq_idx], natfreq, 'ro', ms=3)
        for i,(b,l) in enumerate(zip(bands,bands_lab)):
            ax_spec.fill_betweenx(self.freqs, -evoked_spectrum, where=b & (evoked_spectrum>=0), 
                                  color=color_spectrum, alpha=0.9-(0.2*i), edgecolor='None')
            ax_bands.axhspan(self.freqs[b][0], self.freqs[b][-1], facecolor=color_spectrum, alpha=0.9-(0.2*i), edgecolor='None')
            ax_bands.text(0.5, self.freqs[b].mean(), l, va='center', ha='center', fontsize=14)
        ax_spec.set_xlim(right=0)
        ax_spec.set_ylim(self.freqs[0],self.freqs[-1])
        ax_spec.invert_xaxis()
        ax_spec.set_xticks([]), ax_spec.set_yticks([])  
        ax_spec.text(-evoked_spectrum[natfreq_idx], natfreq, f'{round(natfreq,1)} Hz'+' '*2, color='r',
                fontsize=9, va='center', ha='right', weight="bold")
        ax_bands.set_xlim(0,1)
        ax_bands.set_ylim(self.freqs[0], self.freqs[-1])
        ax_bands.set_xticks([])
        ax_spec.spines['right'].set_visible(False)
        ax_bands.spines['left'].set_visible(False)
        
        fig.subplots_adjust(wspace=0, hspace=0)
        plt.show()

        return fig
    
    def plot_natfreq2(self, natfreq_window=(0.02,0.12), pick_ch=None,
                      baseline_range=(-0.5, -0.1), plot_tlim=(-0.1, 0.3), 
                      color_spectrum='tab:blue', cmap='RdBu_r', 
                      plot_ms=True, figsize=(6,3), dpi=100,
                      label_cbar=r'$\Delta$power ($\mu V^2$)'):
        """
        Plot natural frequency analysis (compact version).
        
        The figure includes:
            1) Time-frequency representation
            2) Evoked spectrum with frequency bands    
        Includes:
            - Time-frequency representation
            - Evoked spectrum with frequency bands
    
        Args:
            natfreq_window (tuple of float): Time window (s) used to compute the natural frequency. 
                It corresponds to the summation window of the evoked power spectrum. 
            pick_ch (list[str | int] | None): Channel name(s) to include. If None, all channels are included.
            baseline_range (tuple of float): Time range (s) for baseline correction if not already applied.
            plot_tlim (tuple): Plot time limits [start, end] in seconds.
            color_spectrum (str, optional): Color for frequency bands. 
            cmap (str, optional): Colormap for time-frequency plot.
            plot_ms (bool, optional): Display time in milliseconds. 
            figsize (tuple, optional): Figure dimensions in inches. 
            dpi (int, optional): Figure resolution.
            label_cbar (str, optional): Colorbar label. Default: r'$\Delta$power ($\mu V^2$)'.
            
        Returns:
            matplotlib.figure.Figure: The generated figure object.
        """
        # prepare data
        bands, bands_lab = _return_bands_idxs(self.freqs)
        if any(sum(b) <= 1 for b in bands):
            raise ValueError(
                "Insufficient frequency bands detected. Requires theta to gamma range (or alpha to gamma range). "
                f"Actual frequency range {self.freqs[0]:.1f}-{self.freqs[-1]:.1f}Hz")
            
        evoked_spectrum, power_data = self.get_evoked_spectrum(pick_ch=pick_ch, 
                                                               average_channels=True, 
                                                               sum_window=natfreq_window, 
                                                               baseline_range=baseline_range,
                                                               return_power=True)
        natfreq_idx = np.argmax(evoked_spectrum)
        natfreq = self.freqs[natfreq_idx]
        window_mask = (self.times>=natfreq_window[0]) & (self.times<=natfreq_window[1])
        vmax = np.percentile(power_data[:,window_mask],95)
        vmin = -vmax

        # create figure
        fig = plt.figure(dpi=dpi, figsize=figsize)

        # --- Time-Frequency Plot ---
        ax_tf = fig.add_subplot(1,23,(1,14), facecolor='None')
        if plot_ms:
            times = self.times * 1000
            plot_tlim = (plot_tlim[0]*1000, plot_tlim[1]*1000)
            xlab = 'time (ms)'
        else:
            times = self.times
            xlab = 'time (s)'
        pcm = ax_tf.pcolormesh(times, self.freqs, power_data, cmap=cmap, shading='gouraud', rasterized=True, vmin=vmin, vmax=vmax)
        ax_tf.axvline(0, ls='--', c='k', lw=0.8)
        ax_tf.set_xlim(plot_tlim[0], plot_tlim[1])
        ax_tf.set_ylim(self.freqs[0], self.freqs[-1])
        ax_tf.set_xlabel(xlab)
        ax_tf.set_ylabel('frequency (Hz)')

        # --- Colorbar ---
        ax=fig.add_subplot(1,23,23, facecolor='None')
        cb = plt.colorbar(pcm, cax=ax, aspect=1)
        cb.set_label(label_cbar)

        # --- Spectrum Plot ---
        ax_spec=fig.add_subplot(1,23,(15,19), facecolor='None')
        ax_bands=fig.add_subplot(1,23,(20,22), sharey=ax_spec, facecolor='None')
        ax_spec.plot(-evoked_spectrum, self.freqs, c='k' )
        ax_spec.plot(-evoked_spectrum[natfreq_idx], natfreq, 'ro', ms=3)
        for i,(b,l) in enumerate(zip(bands,bands_lab)):
            ax_spec.fill_betweenx(self.freqs, -evoked_spectrum, where=b & (evoked_spectrum>=0), 
                                  color=color_spectrum, alpha=0.9-(0.2*i), edgecolor='None')
            ax_bands.axhspan(self.freqs[b][0], self.freqs[b][-1], facecolor=color_spectrum, alpha=0.9-(0.2*i), edgecolor='None')
            ax_bands.text(0.5, self.freqs[b].mean(), l, va='center', ha='center', fontsize=14)
        ax_spec.set_xlim(right=0)
        ax_spec.set_ylim(self.freqs[0],self.freqs[-1])
        ax_spec.invert_xaxis()
        ax_spec.set_xticks([]), ax_spec.set_yticks([])  
        ax_spec.text(-evoked_spectrum[natfreq_idx], natfreq, f'{round(natfreq,1)} Hz'+' '*2, color='r',
                fontsize=9, va='center', ha='right', weight="bold")
        ax_bands.set_xlim(0,1)
        ax_bands.set_ylim(self.freqs[0], self.freqs[-1])
        ax_bands.set_xticks([])
        ax_spec.spines['right'].set_visible(False)
        ax_bands.spines['left'].set_visible(False)
        
        fig.subplots_adjust(wspace=0)
        plt.show()

        return fig
        