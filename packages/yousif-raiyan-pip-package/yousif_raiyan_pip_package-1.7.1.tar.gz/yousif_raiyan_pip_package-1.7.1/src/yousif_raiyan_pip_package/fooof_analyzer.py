import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend, butter, filtfilt, iirnotch
try:
    # Use modern SpecParam library (successor to FOOOF)
    from specparam import SpectralParameterization as FOOOF
except ImportError:
    # Fallback to legacy fooof package for compatibility
    from fooof import FOOOF


class FOOOFAnalyzer:
    """
    FOOOF/SpecParam (Spectral Parameterization) Analyzer for EEG signals.
    
    Separates neural power spectra into aperiodic (1/f) and periodic (oscillatory) components.
    Uses the modern SpecParam library (with FOOOF fallback for compatibility).
    
    Workflow:
    1. Load EDF using EDFLoader
    2. Instantiate FOOOFAnalyzer with the loader
    3. Run analyze_signals() to process all loaded channels
    """
    
    def __init__(self, edf_loader):
        """
        Initialize FOOOF analyzer with an EDF loader.
        
        :param edf_loader: EDFLoader instance with loaded signals
        """
        self.loader = edf_loader
        
        if not self.loader.signals_dict:
            raise ValueError("No signals loaded in EDFLoader. Call load_and_plot_signals() first.")
        
        self.channels = list(self.loader.signals_dict.keys())
        
        self.fooof_settings = {
            'peak_width_limits': (1, 8),
            'max_n_peaks': 6,
            'min_peak_height': 0.1,
            'peak_threshold': 2.0,
            'aperiodic_mode': 'fixed',
            'verbose': False
        }
        
        self.freq_range = (1, 40)
        self.nperseg = 1024
        self.results = {}
        self._library_info = self._get_library_info()
    
    def get_library_info(self):
        """
        Get information about the spectral parameterization library being used.
        
        :return: dict with library name, version, and description
        """
        return self._library_info.copy()
        
    def set_frequency_range(self, freq_range):
        """
        Set the frequency range for FOOOF analysis.
        
        :param freq_range: tuple, (low_freq, high_freq) in Hz
        """
        self.freq_range = freq_range
        
    def set_fooof_settings(self, **kwargs):
        """
        Update FOOOF model settings.
        
        :param kwargs: FOOOF parameters to update
        """
        self.fooof_settings.update(kwargs)
        
    def preprocess_signal(self, signal, fs, 
                         detrend_signal=True,
                         bandpass=(1, 40),
                         notch_freq=60.0,
                         notch_quality=30.0):
        """
        Preprocess a single signal for FOOOF analysis.
        
        :param signal: 1D numpy array
        :param fs: sampling frequency
        :param detrend_signal: whether to detrend
        :param bandpass: tuple for bandpass filter, None to skip
        :param notch_freq: notch filter frequency, None to skip
        :param notch_quality: Q factor for notch filter
        :return: preprocessed signal
        """
        processed = signal.copy()
        
        if detrend_signal:
            processed = detrend(processed)
            
        if bandpass is not None:
            low, high = bandpass
            nyq = fs / 2
            b, a = butter(N=4, Wn=[low / nyq, high / nyq], btype='band')
            processed = filtfilt(b, a, processed)
            
        if notch_freq is not None:
            nyq = fs / 2
            w0 = notch_freq / nyq
            b, a = iirnotch(w0, notch_quality)
            processed = filtfilt(b, a, processed)
            
        return processed
        
    def compute_psd(self, signal, fs):
        """
        Compute power spectral density using Welch's method.
        
        :param signal: 1D numpy array
        :param fs: sampling frequency
        :return: frequencies, power spectral density
        """
        freqs, psd = welch(signal, fs=fs, nperseg=self.nperseg)
        return freqs, psd
        
    def run_fooof_single(self, signal, fs, channel_name):
        """
        Run FOOOF analysis on a single signal.
        
        :param signal: 1D numpy array
        :param fs: sampling frequency  
        :param channel_name: name of the channel
        :return: dictionary with FOOOF results
        """
        processed_signal = self.preprocess_signal(signal, fs)
        freqs, psd = self.compute_psd(processed_signal, fs)
        fooof = FOOOF(**self.fooof_settings)
        fooof.fit(freqs, psd, self.freq_range)
        
        results = {
            'channel': channel_name,
            'aperiodic_params': fooof.aperiodic_params_,
            'peak_params': fooof.peak_params_,
            'r_squared': fooof.r_squared_,
            'error': fooof.error_,
            'freqs': freqs,
            'psd': psd,
            'fooof_model': fooof
        }
        
        return results
        
    def get_band_powers(self, freqs, psd, bands=None):
        """
        Calculate power in specified frequency bands.
        
        :param freqs: frequency array
        :param psd: power spectral density array
        :param bands: dict of {band_name: (low_freq, high_freq)}
        :return: dict of band powers
        """
        if bands is None:
            bands = {
                'delta': (1, 4),
                'theta': (4, 8),
                'alpha': (8, 12),
                'beta': (12, 30),
                'gamma': (30, 40)
            }
            
        band_powers = {}
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs <= high)
            if np.any(mask):
                power = np.trapezoid(psd[mask], freqs[mask])
                band_powers[band_name] = power
            else:
                band_powers[band_name] = 0.0
                
        return band_powers
        
    def analyze_signals(self, channels_to_analyze=None):
        """
        Run FOOOF analysis on specified channels and save results.
        
        :param channels_to_analyze: list of channel names, None for all channels
        """
        if channels_to_analyze is None:
            channels_to_analyze = self.channels
        else:
            available = set(self.channels)
            requested = set(channels_to_analyze)
            missing = requested - available
            if missing:
                print(f"Warning: Channels {missing} not available. Available: {available}")
                channels_to_analyze = list(requested & available)
                
        if not channels_to_analyze:
            print("No valid channels to analyze.")
            return
            
        print(f"Running spectral parameterization analysis on {len(channels_to_analyze)} channels...")
        print(f"Using {self._library_info['library']} v{self._library_info['version']} ({self._library_info['description']})")
        
        output_dir = os.path.join(self.loader.folder_path, self.loader.name, 'fooof_analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        for channel in channels_to_analyze:
            print(f"Processing channel: {channel}")
            
            signal_data = self.loader.signals_dict[channel]['data']
            fs = self.loader.signals_dict[channel]['sample_rate']
            
            result = self.run_fooof_single(signal_data, fs, channel)
            self.results[channel] = result
            
            self._save_channel_results(result, output_dir)
            
        self._save_summary_results(output_dir)
        
        print(f"Spectral parameterization analysis complete. Results saved to: {output_dir}")
        
    def plot_channel_comparison(self, channels=None, metric='aperiodic_exponent'):
        """
        Plot comparison of FOOOF metrics across channels.
        
        :param channels: list of channels to compare, None for all
        :param metric: metric to compare ('aperiodic_exponent', 'n_peaks', 'r_squared', etc.)
        """
        if not self.results:
            print("No results available. Run analyze_signals() first.")
            return
            
        if channels is None:
            channels = list(self.results.keys())
            
        values = []
        labels = []
        
        for channel in channels:
            if channel in self.results:
                result = self.results[channel]
                if metric == 'aperiodic_exponent':
                    values.append(result['aperiodic_params'][1])
                elif metric == 'aperiodic_offset':
                    values.append(result['aperiodic_params'][0])
                elif metric == 'n_peaks':
                    values.append(len(result['peak_params']))
                elif metric == 'r_squared':
                    values.append(result['r_squared'])
                elif metric == 'error':
                    values.append(result['error'])
                else:
                    print(f"Unknown metric: {metric}")
                    return
                labels.append(channel)
                
        plt.figure(figsize=(12, 6))
        plt.bar(labels, values)
        plt.title(f'{metric.replace("_", " ").title()} Across Channels')
        plt.xlabel('Channel')
        plt.ylabel(metric.replace("_", " ").title())
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def _get_library_info(self):
        """Get information about which spectral parameterization library is being used."""
        try:
            import specparam
            return {
                'library': 'specparam',
                'version': getattr(specparam, '__version__', 'unknown'),
                'description': 'Modern spectral parameterization library'
            }
        except ImportError:
            try:
                import fooof
                return {
                    'library': 'fooof',
                    'version': getattr(fooof, '__version__', 'unknown'),
                    'description': 'Legacy FOOOF library (compatibility mode)'
                }
            except ImportError:
                return {
                    'library': 'none',
                    'version': 'unknown',
                    'description': 'No spectral parameterization library found'
                }
        
    def _save_channel_results(self, result, output_dir):
        """Save results for a single channel."""
        channel = result['channel']
        channel_dir = os.path.join(output_dir, channel)
        os.makedirs(channel_dir, exist_ok=True)
        
        fig_path = os.path.join(channel_dir, f'{channel}_fooof_fit.png')
        result['fooof_model'].plot()
        plt.title(f'FOOOF Model Fit - {channel}')
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        plt.figure(figsize=(10, 6))
        plt.semilogy(result['freqs'], result['psd'], label='PSD', color='blue')
        plt.xlim(self.freq_range)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power')
        plt.title(f'Power Spectral Density - {channel}')
        plt.grid(True)
        plt.legend()
        psd_path = os.path.join(channel_dir, f'{channel}_psd.png')
        plt.savefig(psd_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        params_data = {
            'channel': [channel],
            'aperiodic_offset': [result['aperiodic_params'][0]],
            'aperiodic_exponent': [result['aperiodic_params'][1]],
            'r_squared': [result['r_squared']],
            'error': [result['error']],
            'n_peaks': [len(result['peak_params'])]
        }
        
        if len(result['peak_params']) > 0:
            for i, peak in enumerate(result['peak_params']):
                params_data[f'peak_{i+1}_freq'] = [peak[0]]
                params_data[f'peak_{i+1}_power'] = [peak[1]]
                params_data[f'peak_{i+1}_bandwidth'] = [peak[2]]
        
        params_df = pd.DataFrame(params_data)
        params_path = os.path.join(channel_dir, f'{channel}_fooof_params.csv')
        params_df.to_csv(params_path, index=False)
        
        band_powers = self.get_band_powers(result['freqs'], result['psd'])
        band_df = pd.DataFrame([band_powers])
        band_df['channel'] = channel
        band_path = os.path.join(channel_dir, f'{channel}_band_powers.csv')
        band_df.to_csv(band_path, index=False)
        
        settings_path = os.path.join(channel_dir, f'{channel}_fooof_settings.json')
        with open(settings_path, 'w') as f:
            json.dump(result['fooof_model'].get_settings(), f, indent=4)
            
    def _save_summary_results(self, output_dir):
        """Save summary results across all channels."""
        if not self.results:
            return
            
        summary_data = []
        band_powers_data = []
        
        for channel, result in self.results.items():
            row = {
                'channel': channel,
                'aperiodic_offset': result['aperiodic_params'][0],
                'aperiodic_exponent': result['aperiodic_params'][1],
                'r_squared': result['r_squared'],
                'error': result['error'],
                'n_peaks': len(result['peak_params'])
            }
            
            if len(result['peak_params']) > 0:
                dominant_peak = result['peak_params'][np.argmax(result['peak_params'][:, 1])]
                row['dominant_peak_freq'] = dominant_peak[0]
                row['dominant_peak_power'] = dominant_peak[1]
                row['dominant_peak_bandwidth'] = dominant_peak[2]
            else:
                row['dominant_peak_freq'] = np.nan
                row['dominant_peak_power'] = np.nan
                row['dominant_peak_bandwidth'] = np.nan
                
            summary_data.append(row)
            
            band_powers = self.get_band_powers(result['freqs'], result['psd'])
            band_powers['channel'] = channel
            band_powers_data.append(band_powers)
            
        summary_df = pd.DataFrame(summary_data)
        summary_path = os.path.join(output_dir, 'fooof_summary.csv')
        summary_df.to_csv(summary_path, index=False)
        
        band_summary_df = pd.DataFrame(band_powers_data)
        band_summary_path = os.path.join(output_dir, 'band_powers_summary.csv')
        band_summary_df.to_csv(band_summary_path, index=False)
        
        self._create_summary_plots(summary_df, band_summary_df, output_dir)
        
    def _create_summary_plots(self, summary_df, band_df, output_dir):
        """Create summary visualization plots."""
        
        plt.figure(figsize=(12, 6))
        plt.bar(summary_df['channel'], summary_df['aperiodic_exponent'])
        plt.title('Aperiodic Exponent Across Channels')
        plt.xlabel('Channel')
        plt.ylabel('Aperiodic Exponent')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'aperiodic_exponent_summary.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        plt.figure(figsize=(12, 6))
        plt.bar(summary_df['channel'], summary_df['n_peaks'])
        plt.title('Number of Peaks Across Channels')
        plt.xlabel('Channel')
        plt.ylabel('Number of Peaks')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'n_peaks_summary.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        band_cols = ['delta', 'theta', 'alpha', 'beta', 'gamma']
        band_matrix = band_df[band_cols].values
        
        plt.figure(figsize=(10, 8))
        plt.imshow(band_matrix.T, aspect='auto', cmap='viridis')
        plt.colorbar(label='Power')
        plt.yticks(range(len(band_cols)), band_cols)
        plt.xticks(range(len(band_df)), band_df['channel'], rotation=45)
        plt.title('Band Powers Across Channels')
        plt.xlabel('Channel')
        plt.ylabel('Frequency Band')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'band_powers_heatmap.png'), dpi=300, bbox_inches='tight')
        plt.close()