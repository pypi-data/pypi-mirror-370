import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt


class Analyzer:
    """
    EEG Analyzer – Multi‑band power with moving‑average smoothing.
    ----------------------------------------------------------------
    Pipeline per trigger‑defined segment:
      1. **Band‑pass filter** (canonical EEG bands: Delta, Theta, Alpha, Beta, Gamma).
      2. **Rectify** → absolute value (proxy for instantaneous power).
      3. **Smooth** with multiple moving‑average (MA) windows.

    All public method signatures from the original implementation are preserved.
    The x‑axis of generated plots is now expressed in **minutes** instead of
    seconds.
    """

    # ─────────────────────────────── Init ────────────────────────────────

    def __init__(self, loader, trigger_detector, target_length: int = 50):
        self.loader = loader
        self.trigger_detector = trigger_detector
        self.df_triggers = trigger_detector.df_triggers

        # Use channels from the loaded signals (only those actually loaded)
        self.channels = list(loader.signals_dict.keys()) if loader.signals_dict else []
        
        # Reference: Standard EEG channel list for full recordings
        # ['Fp1', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2',
        #  'F7', 'F8', 'T3', 'T4', 'T5', 'T6', 'Fz']
        self.standard_eeg_channels = [
            'Fp1', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2',
            'F7', 'F8', 'T3', 'T4', 'T5', 'T6', 'Fz'
        ]

        # Canonical EEG bands
        self.bands = {
            "Delta": (0.5, 4),
            "Theta": (4, 8),
            "Alpha": (8, 12),
            "Beta": (12, 30),
            "Gamma": (30, 80)
        }

        # Resampled points per segment for downstream aggregation
        self.target_length = target_length

        # Moving‑average window lengths **in seconds**
        self.smoothing_window_secs = [0.10, 0.25, 0.50]

    # ─────────────────────── Low‑level helpers ──────────────────────────

    def _resample_array(self, arr: np.ndarray, target_length: int) -> np.ndarray:
        """Linear resampling of 1‑D array to *target_length* points."""
        if arr.size == 0:
            return np.array([])
        old = np.linspace(0, arr.size - 1, num=arr.size)
        new = np.linspace(0, arr.size - 1, num=target_length)
        return np.interp(new, old, arr)

    @staticmethod
    def _bandpass_filter(data: np.ndarray, lowcut: float, highcut: float,
                         fs: float, order: int = 4) -> np.ndarray:
        nyq = 0.5 * fs
        low, high = lowcut / nyq, highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, data)

    @staticmethod
    def _moving_average(data: np.ndarray, window_samples: int) -> np.ndarray:
        if window_samples <= 1:
            return data
        kernel = np.ones(window_samples) / window_samples
        return np.convolve(data, kernel, mode='same')

    # ───────────────────────────── Plotting ─────────────────────────────

    def plot_signal_window(self, window_index: int, lead: str):
        """Plot **raw** data for a single trigger‑defined window (x‑axis in minutes)."""
        try:
            if window_index >= len(self.df_triggers) - 1:
                raise ValueError("window_index out of range – needs a subsequent trigger.")
            s = int(self.df_triggers.iloc[window_index]['end_index'])
            e = int(self.df_triggers.iloc[window_index + 1]['start_index'])
            sig = self.loader.signals_dict[lead]['data']
            fs = self.loader.signals_dict[lead]['sample_rate']

            t_min = np.arange(e - s) / fs / 60  # minutes
            plt.figure(figsize=(10, 4))
            plt.plot(t_min, sig[s:e])
            plt.title(f'Signal Window {window_index} | {lead}')
            plt.xlabel('Time (min)')
            plt.ylabel('Amplitude')
            plt.tight_layout()
            plt.show()
        except Exception as exc:
            print(f"Error plotting window {window_index} for {lead}: {exc}")

    def plot_average_window(self, channel: str, start_window: int | None = None,
                             end_window: int | None = None, target_length: int = 500,
                             aggregation_method: str = 'mean', trim_ratio: float = 0.1):
        """Aggregate **raw** segments & plot them with x‑axis in minutes."""
        if start_window is None:
            start_window = 0
        if end_window is None:
            end_window = len(self.df_triggers) - 1

        sig = self.loader.signals_dict[channel]['data']
        fs = self.loader.signals_dict[channel]['sample_rate']
        segments, durations = [], []

        for i in range(start_window, min(end_window, len(self.df_triggers) - 1)):
            s = int(self.df_triggers.iloc[i]['end_index'])
            e = int(self.df_triggers.iloc[i + 1]['start_index'])
            if e <= s:
                continue
            seg = sig[s:e]
            segments.append(self._resample_array(seg, target_length))
            durations.append((e - s) / fs)

        if not segments:
            print("No valid windows in requested range.")
            return

        stack = np.stack(segments)
        if aggregation_method == 'mean':
            agg = np.mean(stack, axis=0)
        elif aggregation_method == 'median':
            agg = np.median(stack, axis=0)
        elif aggregation_method == 'trimmed':
            from scipy.stats import trim_mean
            agg = np.array([trim_mean(stack[:, i], trim_ratio) for i in range(stack.shape[1])])
        else:
            raise ValueError("aggregation_method must be 'mean', 'median', or 'trimmed'.")

        t_axis_min = np.linspace(0, np.mean(durations) / 60, target_length)
        plt.figure(figsize=(10, 4))
        plt.plot(t_axis_min, agg)
        plt.title(f'Aggregated Raw Signal ({aggregation_method}) | {channel}')
        plt.xlabel('Time (min)')
        plt.ylabel('Amplitude')
        plt.tight_layout()
        plt.show()

    # ───────────────────── Legacy private (extended) ──────────────────

    def __get_fft_values(self, data: np.ndarray, sample_rate: float,
                          window_sec: float = 2, overlap_sec: float = 1):
        """Return rectified & smoothed power traces for all bands."""
        results = {}
        for band, (low, high) in self.bands.items():
            filtered = self._bandpass_filter(data, low, high, sample_rate)
            rectified = np.abs(filtered)
            win = int(sample_rate * self.smoothing_window_secs[1])
            smoothed = self._moving_average(rectified, win)
            results[band] = smoothed
        return results

    # ───────────────────────────── Core run ─────────────────────────────

    def extract_signals(self, channels_to_extract=None):
        """Process specified channels & bands, export CSV & plots with x‑axis in minutes.
        
        :param channels_to_extract: list of str, channel names to process (None = all loaded channels)
        """
        if channels_to_extract is None:
            channels_to_extract = self.channels
        else:
            # Validate that requested channels are available
            available_channels = set(self.channels)
            requested_channels = set(channels_to_extract)
            missing_channels = requested_channels - available_channels
            if missing_channels:
                print(f"Warning: Channels {missing_channels} not available. Available: {available_channels}")
                channels_to_extract = list(requested_channels & available_channels)
        
        print(f"Processing {len(channels_to_extract)} channels: {channels_to_extract}")
        
        for ch in channels_to_extract:
            ch_dict = self.loader.signals_dict[ch]
            sig = ch_dict['data']
            fs = ch_dict['sample_rate']

            ma_windows = [int(fs * s) for s in self.smoothing_window_secs]
            durations = []  # seconds per segment (same for all bands)

            # Pre‑allocate a dict: {band -> {window -> list[…]}}
            per_band_results = {
                band: {w: [] for w in ma_windows} for band in self.bands
            }

            for i in range(len(self.df_triggers) - 1):
                s = int(self.df_triggers.iloc[i]['end_index'])
                e = int(self.df_triggers.iloc[i + 1]['start_index'])
                if e - s < 2 * fs:
                    continue

                seg = sig[s:e]
                dur = (e - s) / fs
                durations.append(dur)

                # Per‑band processing
                for band_name, (low_f, high_f) in self.bands.items():
                    filtered = self._bandpass_filter(seg, low_f, high_f, fs)
                    rectified = np.abs(filtered)
                    for w in ma_windows:
                        sm = self._moving_average(rectified, w)
                        per_band_results[band_name][w].append(self._resample_array(sm, self.target_length))

            if not durations:
                print(f"No valid windows for {ch}.")
                continue

            avg_dur_sec = np.mean(durations)
            t_axis_min = np.linspace(0, avg_dur_sec / 60, self.target_length)

            # Prepare output dirs
            base_dir = os.path.join(self.loader.folder_path, self.loader.name)
            for band_name in self.bands:
                csv_dir = os.path.join(base_dir, band_name, 'csv')
                plot_dir = os.path.join(base_dir, band_name, 'plots')
                os.makedirs(csv_dir, exist_ok=True)
                os.makedirs(plot_dir, exist_ok=True)

                plt.figure(figsize=(10, 6))
                for w in ma_windows:
                    if not per_band_results[band_name][w]:
                        continue
                    median_sig = np.median(np.stack(per_band_results[band_name][w]), axis=0)
                    win_ms = int(1000 * w / fs)

                    # CSV export
                    csv_path = os.path.join(csv_dir, f"{ch}_{band_name}_ma{win_ms}ms_median.csv")
                    pd.DataFrame({f"{ch}_{band_name}_ma{win_ms}ms": median_sig}).to_csv(csv_path, index=False)
                    print(f"Saved {csv_path}.")

                    # Plot line
                    plt.plot(t_axis_min, median_sig, label=f"MA {win_ms} ms")

                plt.title(f'Median {band_name}‑band Power | {ch}')
                plt.xlabel('Time (min)')
                plt.ylabel('Amplitude (a.u.)')
                plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
                plt.tight_layout()
                plot_path = os.path.join(plot_dir, f"{ch}_{band_name}_ma_plot.png")
                plt.savefig(plot_path)
                plt.show()
                print(f"Plot saved to {plot_path}.")
