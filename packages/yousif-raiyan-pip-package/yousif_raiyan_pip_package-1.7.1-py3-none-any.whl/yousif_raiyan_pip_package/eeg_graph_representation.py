# Graph representation
import os
import pickle
import numpy as np
from pathlib import Path
import mne
import h5py
import gc
from tqdm import tqdm

from numpy import mean, ones, expand_dims, sum, \
    linalg, array, floor, corrcoef, zeros, \
    where, angle

from multiprocessing import Process, Pool
from scipy.signal import csd, butter, lfilter

from typing import Tuple

def _compute_correlation(x):
    """
    Compute correlation matrix with robust handling of flat/constant signals.
    
    Handles cases where channels have zero standard deviation (flat signals) that
    can occur with bad channels, artifacts, or very short time windows.
    Suppresses warnings and ensures valid correlation matrix properties.
    """
    import warnings
    
    # Compute correlation with warning suppression for flat channels
    # corrcoef() correctly produces NaN for flat channels, which we handle below
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        corr_matrix = corrcoef(x)
    
    # Handle NaN values from flat signals (zero standard deviation)
    # Flat signals have no meaningful correlation with other signals
    # Replace NaN with 0 (no correlation) while preserving valid correlations
    corr_matrix = np.nan_to_num(corr_matrix, nan=0.0, posinf=1.0, neginf=-1.0)
    
    # Ensure diagonal remains 1.0 (perfect self-correlation)
    np.fill_diagonal(corr_matrix, 1.0)
    
    # Clamp to valid correlation range [-1, 1] to handle any numerical precision issues
    corr_matrix = np.clip(corr_matrix, -1.0, 1.0)
    
    return corr_matrix

def calculate_coherence_signal_trace(signal_trace, fs):
    electrode_no = len(signal_trace)
    # Initialize output matrices for coherence and phase values, and freq_indices:
    coherence_dict = {}
    phase_dict = {}
    freq_bands = _compute_frequency_bands(fs)
    # Fill-in initialized matrices
    for band in freq_bands.keys():
        coherence_dict[band] = zeros((electrode_no, electrode_no))
        phase_dict[band] = zeros((electrode_no, electrode_no))

    # get initialized 3D arrays (matrices) of the coherence, phase, and ij_pairs
    ij_pairs = get_ij_pairs(electrode_no)

    # initialize Cxy_dict and phase dictionaries, and list of frequencies
    # Cxy_dict is a dictionary in the form of: (0, 1): [coh-freq1, coh-freq2, ..., coh-freqNyq]
    # for all pairs of electrodes
    # Cxy_phase_dict is also a dictionary in the form of: (0, 1): [time1, time2, ..., timeN] for all electrodes
    # fqs is a list of frequencies
    Cxy_dict = {}
    Cxy_phase_dict = {}
    freqs = []
    # check every electrode pair only once
    for electrode_pair in ij_pairs:
        # initialization of dictionaries to electrode_pair key
        Cxy_dict.setdefault(electrode_pair, {})
        Cxy_phase_dict.setdefault(electrode_pair, {})
        # get signals by index
        x = signal_trace[electrode_pair[0]]
        y = signal_trace[electrode_pair[1]]
        # compute coherence
        nperseg = _nperseg(fs)
        freqs, Cxy, ph, Pxx, Pyy, Pxy = coherence(x, y, fs=fs, nperseg=nperseg, noverlap=16)
        # x and y are the first and second signal we compare against
        # freqs = frequencies that are returned by the coherence function
        # in coherence function computing cross spectral density which gives us this evaluation
        # cross spectral density is a function that looks at what are the frequencies that compose the signal in x

        Cxy_dict[electrode_pair] = Cxy
        Cxy_phase_dict[electrode_pair] = ph

    # Create numpy array of keys and values:
    Cxy_keys = array(list(Cxy_dict.keys()))
    Cxy_values = array(list(Cxy_dict.values()))
    phase_keys = array(list(Cxy_phase_dict.keys()))
    phase_values = array(list(Cxy_phase_dict.values()))

    # Create dictionary with freq-band as keys and list of frequency indices from freqs as values, i.e.
    # freq_indices = {'delta': [1, 2]}
    freq_indices = {}
    for band in freq_bands.keys():
        freq_indices[band] = list(where((freqs >= freq_bands[band][0]) & (freqs <= freq_bands[band][1]))[0])

    # filter for signals that are present that correspond to different bands
    # For each freq band (delta...) is a range, here we are filtering using freqs, which contains frequencies found
    # in signal when converted to frequency domain

    # average over the frequency bands; row averaging
    coh_mean = {}
    phase_mean = {}
    for band in freq_bands.keys():
        coh_mean[band] = mean(Cxy_values[:, freq_indices[band]], axis=1)
        phase_mean[band] = mean(phase_values[:, freq_indices[band]], axis=1)

    for band in freq_bands.keys():
        # Fill coherence_dict matrices:
        # Set diagonals = 1
        coherence_dict[band][range(electrode_no), range(electrode_no)] = 1
        # Fill in rest of the matrices
        for pp, pair in enumerate(Cxy_keys):
            coherence_dict[band][pair[0], pair[1]] = coh_mean[band][pp]
            coherence_dict[band][pair[1], pair[0]] = coh_mean[band][pp]

        # Fill phase matrices:
        # Set diagonals = 1
        phase_dict[band][range(electrode_no), range(electrode_no)] = 1
        # Fill in rest of the matrices
        for pp, pair in enumerate(phase_keys):
            phase_dict[band][pair[0], pair[1]] = phase_mean[band][pp]
            phase_dict[band][pair[1], pair[0]] = phase_mean[band][pp]

    return {'coherence': coherence_dict, 'phase_dict': phase_dict, 'freq_dicts': freq_indices, 'freqs': freqs}

def _compute_energy(x):
    nf = zeros(x.shape[0], dtype=x.dtype)
    for i in range(x.shape[0]):
        nf[i] = sum([j ** 2 for j in x[i]])
    nf /= linalg.norm(nf)
    nf = expand_dims(nf, -1)
    return nf

def butter_bandpass(lowcut: float, highcut: float, fs: float, order: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Design a Butterworth bandpass filter and return its filter coefficients.

    Parameters:
        lowcut (float): The lower cutoff frequency.
        highcut (float): The upper cutoff frequency.
        fs (float): The sampling frequency of the signal.
        order (int, optional): The order of the filter. Defaults to 5.

    Returns:
        Tuple[np.ndarray, np.ndarray]: The numerator (b) and denominator (a) filter coefficients.
    """
    nyquist: float = 0.5 * fs
    # Validate cutoff frequencies
    if lowcut <= 0:
        raise ValueError("lowcut frequency must be greater than 0.")
    if highcut >= nyquist:
        raise ValueError("highcut frequency must be less than Nyquist frequency (0.5 * fs).")
    
    normalized_low: float = lowcut / nyquist
    normalized_high: float = highcut / nyquist
    b, a = butter(order, [normalized_low, normalized_high], btype='band')
    return b, a

def butter_bandpass_filter(data: np.ndarray, lowcut: float, highcut: float, fs: float, order: int = 5) -> np.ndarray:
    """
    Apply a Butterworth bandpass filter to the input data.

    Parameters:
        data (np.ndarray): The input signal array.
        lowcut (float): The lower cutoff frequency.
        highcut (float): The upper cutoff frequency.
        fs (float): The sampling frequency of the signal.
        order (int, optional): The order of the filter. Defaults to 5.

    Returns:
        np.ndarray: The filtered signal.
    """
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    filtered_signal = lfilter(b, a, data)
    return filtered_signal

def _compute_frequency_bands(fs):
    """
    Pass segments of frequency bands constrained to the sampling frequency 'fs'
    :param fs: int, sampling frequency
    :return: dictionary with frequency bands
    """
    if fs < 499:
        return {'delta': (1, 4), 'theta': (4, 8), 'alpha': (8, 13), 'beta': (13, 30), 'gamma': (30, 70),
                'gammaHi': (70, 100)}
    elif fs < 999:
        return {'delta': (1, 4), 'theta': (4, 8), 'alpha': (8, 13), 'beta': (13, 30), 'gamma': (30, 70),
                'gammaHi': (70, 100), 'ripples': (100, 250)}
    # Define frequency oscillation bands, range in Hz:
    return {'delta': (1, 4), 'theta': (4, 8), 'alpha': (8, 13), 'beta': (13, 30), 'gamma': (30, 70),
            'gammaHi': (70, 100), 'ripples': (100, 250), 'fastRipples': (250, 500)}


    # return {'delta': (1, 4), 'theta': (4, 8), 'alpha': (8, 13), 'b1': (13, 20), 'b2': (20,30), 'g1': (30, 40),
    #         'g2': (40,50), 'g3': (50,60), 'g4': (60,70),
    #         'gh1': (70, 80), 'gh2': (80, 90), 'gh3': (90, 100),
    #         'r1': (100, 130), 'r2': (130, 160), 'r3': (160, 190), 'r4': (190, 220), 'r5': (220, 250),
    #         'fr1': (250, 300), 'fr2': (300, 350), 'fr3': (350, 400), 'fr4': (400, 450), 'fr5': (450, 500)
    #         }

def get_ij_pairs(electrode_no):
    """
    Get list of tuples with i, j pairs of electrodes;
        i, j are indices
    :param electrode_no: int, number of electrodes
    :return: ij_pairs (list of tuples(ints))
    """
    # Define electrode pairs over which to calculate
    # the coherence and save it as list of tuples
    ij_pairs = []
    for i in range(electrode_no):
        for j in range(i + 1, electrode_no):
            ij_pairs.append((i, j))

    return ij_pairs

def _nperseg(fs):
    if fs <= 250:
        return 128
    return 256

def coherence(x, y, fs=1.0, window='hann', nperseg=None, noverlap=None,
              nfft=None, detrend='constant', axis=-1):
    """
    Overriding scipy.signal.spectral.coherence method
    to calculate phase lag from CSD
    :return: freqs (ndarray), Cxy (ndarray), phase (ndarray), Pxx (ndarray), Pyy (ndarray), Pxy (ndarray)
    """


    # power spectral density = signal in frequency domain
    # pxx and pyy are the PSD lines
    freqs, Pxx = csd(x, x, fs=fs, window=window, nperseg=nperseg,
                     noverlap=noverlap, nfft=nfft, detrend=detrend, axis=axis)
    _, Pyy = csd(y, y, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap,
                 nfft=nfft, detrend=detrend, axis=axis)
    _, Pxy = csd(x, y, fs=fs, window=window, nperseg=nperseg,
                 noverlap=noverlap, nfft=nfft, detrend=detrend, axis=axis)

    ph = angle(Pxy, deg=False)

    # formula for coherence with safe division to prevent warnings
    # Handle division by zero that can occur with:
    # - Flat/constant signals (zero power spectral density)
    # - Very short time windows or bad channels  
    # - Edge effects in segmented processing
    denominator = Pxx * Pyy
    # Add machine epsilon to prevent division by zero warnings
    # Machine epsilon (~2.22e-16) is so small it doesn't affect valid calculations
    # but prevents true zero denominators from causing runtime warnings
    eps = np.finfo(np.float64).eps  
    Cxy = abs(Pxy) ** 2 / (denominator + eps)
    
    # Clamp to valid coherence range [0,1] and handle any remaining invalid values
    Cxy = np.clip(Cxy, 0.0, 1.0)
    Cxy = np.nan_to_num(Cxy, nan=0.0, posinf=1.0, neginf=0.0)

    return freqs, Cxy, ph, Pxx, Pyy, Pxy

########################################################

# save preprocessed data for patient sub with all combinations
def graph_representation_elements(sub, w_sz=None, a_sz=None, w_st=0.125):
    """
    Compute and save graph representation elements
    Creates three subprocesses, one for each signal trace

    After getting the preprocessed signal traces (see projects.gnn_to_soz.preprocess), the function
    creates 3 subprocesses that call the function save_gres() for the preictal, ictal, and postictal traces.
    save_gres() will compute all co-activity measurements (currently correlation, coherence, and phase-lock value),
    to then create the graph, node and edge features. These metrics are then stored in pickle files at the directory
    graph_representation_elements_dir/{patientID} (see native.datapaths).

    Preprocessed signal traces are stored in the preprocessed_data_dir directory declared in native.datapaths.
    This function will save gres for every subject run. For instance, if there are 2 subject runs in
    datarecord_path/{subject}, then there will be 2 gres for every signal trace.

    :param sub: string, patient ID (i.e., pt2).
    :param w_sz: float, window size to analyze signal
    :param w_st: float, percentage of window size to be used as
                window step to analyze signal. 0 < w_st <= 1
    :return: nothing, it saves the signal traces into pickle files.
    """
    # load data (pickle file)
    with open("pp_preictal_1.pickle", "rb") as f:
        pp_preictal = pickle.load(f)

    with open("pp_ictal_1.pickle", "rb") as f:
        pp_ictal = pickle.load(f)

    with open("pp_postictal_1.pickle", "rb") as f:
        pp_postictal = pickle.load(f)

    preictal_trace = pp_preictal.get_data()
    ictal_trace = pp_ictal.get_data()
    postictal_trace = pp_postictal.get_data()

    # default to sampling frequency
    if w_sz is None:
        window_size = int(pp_ictal.info["sfreq"])
    else:
        window_size = w_sz

    # default to sampling frequency, floor
    window_step = int(floor(window_size * w_st))

    # create directory to store data
    data_dir = Path.cwd() / "graph_representation"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # save channel names
    ch_names = pp_ictal.ch_names
    data_file = Path(data_dir, "ch_names.pickle")
    print('creating ch_names')
    pickle.dump(ch_names, open(data_file, 'wb'))

    p_save_preictal_trace = Process(target=save_gres,
                                    args=(preictal_trace, pp_preictal.info["sfreq"], window_size,
                                            window_step, data_dir, "preictal", a_sz))
    p_save_preictal_trace.daemon = False
    p_save_ictal_trace = Process(target=save_gres,
                                    args=(ictal_trace, pp_ictal.info["sfreq"], window_size,
                                        window_step, data_dir, "ictal", a_sz))
    p_save_ictal_trace.daemon = False
    p_save_postictal_trace = Process(target=save_gres,
                                        args=(postictal_trace, pp_postictal.info["sfreq"], window_size,
                                            window_step, data_dir, "postictal", a_sz))
    p_save_postictal_trace.daemon = False

    p_save_preictal_trace.start()
    p_save_ictal_trace.start()
    p_save_postictal_trace.start()

    p_save_preictal_trace.join()
    p_save_ictal_trace.join()
    p_save_postictal_trace.join()

def save_gres(signal_trace, sfreq, window_size, window_step, data_dir, trace_type, adj_window_size=20*1000):
    """
    Create sequences of graph representations of the signal traces by considering
    windows of size 'window_size'

    :param signal_trace: ndarray, EEG signal trace
    :param run: int, run number
    :param sfreq: float, sampling frequency
    :param window_size: int, size of window
    :param window_step: int, step that window takes when iterating through signal trace
    :param data_dir: string, directory where to dump serialized (pickle) graph representations
    :param trace_type: string, preictal, ictal, postictal
    :return:
    """
    last_step = signal_trace.shape[1] - window_size
    # pool = Pool(3) FIXME: changed
    pool = Pool()
    """
    # Regular processes - Adj matrix computed from the same window_size as features
    processes = [pool.apply_async(get_all, args=(signal_trace[:, i:i + window_size], sfreq))
                 for i in range(0, last_step, window_step)]
    """


    # Custom processes - Adj matrix computed from adj_window_size while features are computed from window_size
    # processes = [pool.apply_async(custom_adj_get_all, args=(signal_trace[:, i:i + window_size],
    #                                                         # [int(i - min(max(i - adj_window_size / 2, 0), last_step - adj_window_size)), int(i + window_size - min(max(i - adj_window_size / 2, 0), last_step - adj_window_size))],
    #                                                           signal_trace[:, int (min(max(i - adj_window_size / 2, 0), last_step - adj_window_size)): int( min( max(adj_window_size, i + adj_window_size / 2), last_step ))],
    #                                                           sfreq, i, last_step))
    #              for i in range(0, last_step, window_step)]

    # Custom processes - Adj matrix computed from adj_window_size while features are computed from window_size - this version is the most consistent
    processes = [pool.apply_async(custom_adj_get_all, args=(signal_trace[:, i:i + window_size],
                                                            signal_trace[:, int(i - adj_window_size / 2):
                                                                            int(i + adj_window_size / 2)],
                                                            sfreq, i, last_step))
                 for i in range(int(adj_window_size / 2), int(last_step - adj_window_size / 2), window_step)]



    result = [p.get() for p in processes]
    pool.close()
    pool.join()
    file_name = trace_type + ".pickle"
    data_file = Path(data_dir, file_name)
    with open(data_file, 'wb') as save_file:
        print('dumping some file')
        pickle.dump(result, save_file)

def custom_adj_get_all(x_features, x_adj, sfreq, i, last_step):
    """
        Compute adjacency matrix (from the window x_adj), node and edge features (both from the window x_features)
        :param x_features: ndarray, EEG signal trace
        :param x_adj: ndarray, EEG signal trace
        :param sfreq: float, sampling frequency of signal
        :param i: float, step index for tracking progress
        :param last_step: float, last step for tracking progress
        :return: ndarrays of adj_matrices
    """

    print(f'On step {i} / {last_step}')

    # get adj_matrices
    adj_matrices = generate_adjacency_matrices(x_adj, sfreq)

    # get all other features
    node_features, edge_features = generate_node_and_edge_features(x_features, sfreq)

    return adj_matrices, node_features, edge_features

def generate_adjacency_matrices(x, sfreq):
    """
        Compute adjacency matrix
        :param x: ndarray, EEG signal trace
        :param sfreq: float, sampling frequency of signal
        :return: ndarrays of adj_matrices
    """

    # "corr"
    corr_x = _compute_correlation(x)

    # "coh"
    coherence_result = calculate_coherence_signal_trace(x, sfreq)
    coherences_dict = coherence_result['coherence']
    coherences = []
    for key in coherences_dict.keys():
        coherences.append(coherences_dict[key])
    coherences = mean(coherences, axis=0)

    # "phase"
    phases_dict = coherence_result['phase_dict']
    phases = []
    for key in phases_dict.keys():
        phases.append(phases_dict[key])
    phases = mean(phases, axis=0)

    adj_matrices = [ones((x.shape[0], x.shape[0]), dtype=x.dtype),  # "ones"
                    corr_x,  # "corr"
                    coherences,  # "coh"
                    phases]  # "phase"

    return adj_matrices

# Function to compute node and edge features
def generate_node_and_edge_features(x, sfreq):
    """
    Get all combinations of node and edge features, WITHOUT adjacency matrices
    :param x: ndarray, EEG signal trace
    :param sfreq: float, sampling frequency of signal
    :return: ndarrays of node_features, edge_features
    """
    # ---------- edge features ----------
    # "ones"
    edge_features = [ones((x.shape[0], x.shape[0], 1), dtype=x.dtype)]

    # "corr"
    corr_x = _compute_correlation(x)
    edge_features.append(expand_dims(corr_x, -1))

    # "coh"
    coherence_result = calculate_coherence_signal_trace(x, sfreq)
    coherences_dict = coherence_result['coherence']
    coherences = []
    for key in coherences_dict.keys():
        coherences.append(coherences_dict[key])
    coherences = mean(coherences, axis=0)
    edge_features.append(expand_dims(coherences, -1))

    # "coh+" expanded with extra features for each band
    coherence_result = calculate_coherence_signal_trace(x, sfreq)
    coherences_dict = coherence_result['coherence']
    coherences = []
    for key in coherences_dict.keys():
        coherences.append(coherences_dict[key])
    coherences.insert(0,mean(coherences, axis=0))
    combined_coherences = [
        [[sublists[i][j] for sublists in coherences] for j in range(len(coherences[0][0]))]
        for i in range(len(coherences[0]))
    ]
    combined_coherences = np.array(combined_coherences)
    edge_features.append(combined_coherences)

    # "phase"
    phases_dict = coherence_result['phase_dict']
    phases = []
    for key in phases_dict.keys():
        phases.append(phases_dict[key])
    phases = mean(phases, axis=0)
    edge_features.append(expand_dims(phases, -1))

    # ---------- node features ----------
    # "ones"
    node_features = [ones((x.shape[0], 1), dtype=x.dtype)]

    # "energy"
    nf = _compute_energy(x)
    node_features.append(nf)

    # "band_energy"
    freq_dicts = coherence_result['freq_dicts']
    freqs = coherence_result['freqs']
    nf = [[] for _i in range(x.shape[0])]
    for i in range(x.shape[0]):
        for band in freq_dicts.keys():
            lowcut = freqs[min(freq_dicts[band])]
            highcut = freqs[max(freq_dicts[band])]
            if lowcut == highcut:
                lowcut = freqs[min(freq_dicts[band])-1]
            # lowcut frequencies must be greater than 0, so currently set to 0.1
            if lowcut == 0:
                lowcut += 0.1
            # highcut frequencies must be less than sfreq / 2, so subtract 1 from max
            if highcut == sfreq / 2:
                highcut -= 0.1
            freq_sig = butter_bandpass_filter(x[i], lowcut, highcut, sfreq)
            nf[i].append(sum([j ** 2 for j in freq_sig]))
        nf[i] = nf[i]
    nf /= linalg.norm(nf, axis=0, keepdims=True)
    node_features.append(nf)

    return node_features, edge_features

# ── Top‑level streaming worker ──────────────────────────────────────────────────

def _stream_and_compute(
    edf_path: str,
    feat_start: int,
    feat_stop: int,
    adj_start: int,
    adj_stop: int,
    sfreq: float,
    i: int,
    last_step: int
):
    """Reopen EDF in each worker, grab two small slices, run graph logic."""
    raw = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
    x_feat = raw.get_data(start=feat_start, stop=feat_stop)
    x_adj  = raw.get_data(start=adj_start,  stop=adj_stop)

    adj_matrices = generate_adjacency_matrices(x_adj, sfreq)
    node_feats, edge_feats = generate_node_and_edge_features(x_feat, sfreq)
    return adj_matrices, node_feats, edge_feats

# ── HDF5 Helper Functions ──────────────────────────────────────────────────

def _create_hdf5_datasets(h5_file, n_electrodes: int, n_adj_types: int = 4, 
                         n_node_features: int = None, n_edge_features: int = None):
    """
    Create expandable HDF5 datasets for graph representation data.
    
    :param h5_file: Open HDF5 file handle
    :param n_electrodes: Number of electrodes/channels
    :param n_adj_types: Number of adjacency matrix types (default: 4)
    :param n_node_features: Number of node feature types (estimated if None)
    :param n_edge_features: Number of edge feature types (estimated if None)
    """
    # Estimate feature dimensions if not provided
    if n_node_features is None:
        n_node_features = 3  # ones, energy, band_energy
    if n_edge_features is None:
        n_edge_features = 4  # ones, corr, coh, phase (simplified estimate)
    
    # Create expandable datasets with chunking for efficient I/O
    chunk_size = min(100, 10)  # Reasonable chunk size for I/O efficiency
    
    # Adjacency matrices: (n_windows, n_adj_types, n_electrodes, n_electrodes)
    # This matches the natural data structure from generate_adjacency_matrices()
    h5_file.create_dataset(
        'adjacency_matrices',
        shape=(0, n_adj_types, n_electrodes, n_electrodes),
        maxshape=(None, n_adj_types, n_electrodes, n_electrodes),
        chunks=(chunk_size, n_adj_types, n_electrodes, n_electrodes),
        compression='gzip',
        compression_opts=6,
        dtype=np.float32
    )
    
    # Node features: (n_windows, n_electrodes, n_node_features) - variable last dim
    h5_file.create_dataset(
        'node_features',
        shape=(0,),
        maxshape=(None,),
        chunks=(chunk_size,),
        compression='gzip',
        compression_opts=6,
        dtype=h5py.special_dtype(vlen=np.float32)  # Variable length for different feature sizes
    )
    
    # Edge features: (n_windows, n_electrodes, n_electrodes, n_edge_features) - variable last dim
    h5_file.create_dataset(
        'edge_features',
        shape=(0,),
        maxshape=(None,),
        chunks=(chunk_size,),
        compression='gzip',
        compression_opts=6,
        dtype=h5py.special_dtype(vlen=np.float32)  # Variable length for different feature sizes
    )
    
    # Metadata
    h5_file.create_dataset(
        'window_starts',
        shape=(0,),
        maxshape=(None,),
        chunks=(chunk_size,),
        dtype=np.float64
    )
    
    # Store processing parameters as attributes
    h5_file.attrs['n_electrodes'] = n_electrodes
    h5_file.attrs['n_adj_types'] = n_adj_types

def _append_to_hdf5(h5_file, adj_matrices_list, node_features_list, 
                   edge_features_list, window_starts_list):
    """
    Append new data to HDF5 datasets without loading existing data.
    
    :param h5_file: Open HDF5 file handle
    :param adj_matrices_list: List of adjacency matrices for windows
    :param node_features_list: List of node features for windows  
    :param edge_features_list: List of edge features for windows
    :param window_starts_list: List of window start times
    """
    n_new_windows = len(adj_matrices_list)
    if n_new_windows == 0:
        return
    
    # Get current sizes
    current_size = h5_file['adjacency_matrices'].shape[0]
    new_size = current_size + n_new_windows
    
    # Resize datasets
    h5_file['adjacency_matrices'].resize((new_size, 
                                         h5_file['adjacency_matrices'].shape[1],
                                         h5_file['adjacency_matrices'].shape[2],
                                         h5_file['adjacency_matrices'].shape[3]))
    h5_file['node_features'].resize((new_size,))
    h5_file['edge_features'].resize((new_size,))
    h5_file['window_starts'].resize((new_size,))
    
    # Convert lists to arrays for adjacency matrices
    adj_array = np.array(adj_matrices_list, dtype=np.float32)
    
    # Append new data
    h5_file['adjacency_matrices'][current_size:new_size] = adj_array
    h5_file['window_starts'][current_size:new_size] = window_starts_list
    
    # Handle variable-length node and edge features
    for i, (node_feat, edge_feat) in enumerate(zip(node_features_list, edge_features_list)):
        # Flatten and store node features
        node_flat = np.concatenate([feat.flatten() for feat in node_feat]).astype(np.float32)
        h5_file['node_features'][current_size + i] = node_flat
        
        # Flatten and store edge features  
        edge_flat = np.concatenate([feat.flatten() for feat in edge_feat]).astype(np.float32)
        h5_file['edge_features'][current_size + i] = edge_flat

def _process_segment_windows(edf_path: str, segment_start_samp: int, segment_stop_samp: int,
                           window_size: int, adj_window_size: int, window_step: int, 
                           sfreq: float) -> tuple:
    """
    Process all windows within a single segment.
    
    :param edf_path: Path to EDF file
    :param segment_start_samp: Segment start in samples
    :param segment_stop_samp: Segment stop in samples  
    :param window_size: Analysis window size in samples
    :param adj_window_size: Adjacency window size in samples
    :param window_step: Step size between windows in samples
    :param sfreq: Sampling frequency
    :returns: (adj_matrices_list, node_features_list, edge_features_list, window_starts_list)
    """
    half_adj = adj_window_size // 2
    
    # Build tasks for this segment only
    tasks = []
    window_starts = []
    
    # Adjust range to be within segment bounds and respect adjacency requirements
    start_pos = max(segment_start_samp, half_adj)
    end_pos = min(segment_stop_samp - window_size, segment_stop_samp - half_adj)
    
    for i in range(start_pos, end_pos, window_step):
        if i + window_size <= segment_stop_samp and i - half_adj >= segment_start_samp:
            feat_start = i
            feat_stop = i + window_size
            adj_start = i - half_adj  
            adj_stop = i + half_adj
            
            tasks.append((edf_path, feat_start, feat_stop, adj_start, adj_stop, 
                         sfreq, i, end_pos))
            window_starts.append(i / sfreq)  # Convert to seconds
    
    if not tasks:
        return [], [], [], []
    
    # Process windows in parallel
    with Pool() as pool:
        results = pool.starmap(_stream_and_compute, tasks)
    
    # Separate results
    adj_matrices_list = []
    node_features_list = []
    edge_features_list = []
    
    for adj_matrices, node_feats, edge_feats in results:
        adj_matrices_list.append(adj_matrices)
        node_features_list.append(node_feats)
        edge_features_list.append(edge_feats)
    
    return adj_matrices_list, node_features_list, edge_features_list, window_starts

class EEGGraphProcessor:
    """
    EEG Graph Representation Processor
    
    A comprehensive processor for generating graph-based representations of EEG data
    with multiple analysis methods ranging from simple correlation analysis to complex
    graph feature extraction with memory-safe processing for large files.
    
    The class provides three main categories of functionality:
    1. Graph Generation: Advanced multi-feature connectivity analysis
    2. Independent Analysis: Simple correlation and coherence calculations  
    3. Visualization: Plotting and analysis of connectivity matrices
    
    All methods support memory-efficient processing and organized file output.
    """
    
    def __init__(
        self,
        *,
        edf_loader,
        output_dir: str = None,
        window_size: int = None,
        adj_window_size: int = 20_000,
        window_step_ratio: float = 0.125
    ):
        """
        Initialize EEG Graph Processor.
        
        Args:
            edf_loader: EDF loader object with edf_file_path and name attributes
            output_dir: Output directory path. If None, defaults to 'graph_representation' 
                       subdirectory in the same directory as the EDF file
            window_size: Size of analysis windows in samples. If None, defaults to sampling frequency
            adj_window_size: Size for adjacency matrix computation in samples (default: 20,000)
            window_step_ratio: Step ratio for sliding windows (default: 0.125 = 87.5% overlap)
        
        Raises:
            ValueError: If edf_loader is None
        """
        if edf_loader is None:
            raise ValueError("edf_loader is required for streaming from EDF")
            
        self.edf_loader = edf_loader
        self.filename = edf_loader.name
        
        # Configure output directory
        if output_dir is None:
            edf_path = Path(self.edf_loader.edf_file_path)
            self.output_dir = edf_path.parent / "graph_representation"
        else:
            self.output_dir = Path(output_dir)
            
        # Set processing parameters
        self.window_size = window_size
        self.adj_window_size = adj_window_size
        self.window_step_ratio = window_step_ratio

    # ========================================================================
    # PUBLIC METHODS - Graph Generation
    # ========================================================================
    
    def generate_graphs_from_edf(self, segment_duration_minutes: float = 3.0) -> Path:
        """
        Generate comprehensive graph representations from EDF data with memory-safe processing.
        
        This method processes EEG data by dividing large files into manageable segments,
        computing adjacency matrices, node features, and edge features for each time window.
        Results are saved to an HDF5 file with expandable datasets for efficient storage
        and retrieval.
        
        The method uses overlapping time windows for high temporal resolution while
        maintaining statistical robustness through longer adjacency computation windows.
        Memory usage remains bounded regardless of input file size.
        
        Args:
            segment_duration_minutes: Duration of each processing segment in minutes.
                                    Smaller values use less memory but may be less efficient.
                                    Valid range: 0.1 to 60 minutes (default: 3.0)
        
        Returns:
            Path: Path to the generated HDF5 file containing all graph representations
        
        Raises:
            ValueError: If segment_duration_minutes is outside valid range
            
        Example:
            >>> processor = EEGGraphProcessor(edf_loader=loader)
            >>> hdf5_path = processor.generate_graphs_from_edf(segment_duration_minutes=5.0)
            >>> print(f"Results saved to: {hdf5_path}")
        """
        # Validate input parameters
        if segment_duration_minutes <= 0 or segment_duration_minutes > 60:
            raise ValueError("segment_duration_minutes must be between 0 and 60")
        
        segment_duration_seconds = segment_duration_minutes * 60
        
        # Read EDF header to get file parameters
        print("→ Reading EDF header...")
        raw0 = mne.io.read_raw_edf(self.edf_loader.edf_file_path, preload=False, verbose=False)
        sfreq = raw0.info["sfreq"]
        n_times = raw0.n_times
        n_electrodes = len(raw0.ch_names)
        total_duration_seconds = n_times / sfreq
        raw0.close()
        
        # Configure processing parameters
        if self.window_size is None:
            self.window_size = int(sfreq)
        window_step = int(self.window_size * self.window_step_ratio)
        
        # Calculate segmentation parameters
        n_segments = int(np.ceil(total_duration_seconds / segment_duration_seconds))
        segment_duration_samples = int(segment_duration_seconds * sfreq)
        
        print(f"→ File duration: {total_duration_seconds:.1f}s ({total_duration_seconds/60:.1f} min)")
        print(f"→ Processing {n_segments} segments of {segment_duration_minutes:.1f} minutes each")
        print(f"→ Window size: {self.window_size} samples ({self.window_size/sfreq:.2f}s)")
        print(f"→ Adjacency window size: {self.adj_window_size} samples ({self.adj_window_size/sfreq:.2f}s)")
        
        # Create HDF5 output file with expandable datasets
        hdf5_dir = self.output_dir / "hdf5"
        hdf5_dir.mkdir(parents=True, exist_ok=True)
        hdf5_path = hdf5_dir / f"{self.filename}_graphs.h5"
        
        print(f"→ Creating HDF5 file: {hdf5_path}")
        
        with h5py.File(hdf5_path, 'w') as h5_file:
            # Initialize expandable datasets
            _create_hdf5_datasets(h5_file, n_electrodes)
            
            # Store processing metadata
            h5_file.attrs['edf_file_path'] = str(self.edf_loader.edf_file_path)
            h5_file.attrs['filename'] = self.filename
            h5_file.attrs['sampling_frequency'] = sfreq
            h5_file.attrs['total_duration_seconds'] = total_duration_seconds
            h5_file.attrs['n_segments'] = n_segments
            h5_file.attrs['segment_duration_seconds'] = segment_duration_seconds
            h5_file.attrs['window_size'] = self.window_size
            h5_file.attrs['adj_window_size'] = self.adj_window_size
            h5_file.attrs['window_step_ratio'] = self.window_step_ratio
            h5_file.attrs['window_step'] = window_step
            
            total_windows_processed = 0
            
            # Process each segment with progress tracking
            pbar = tqdm(range(n_segments), desc="Processing EEG segments", unit="segment")
            
            for segment_idx in pbar:
                segment_start_seconds = segment_idx * segment_duration_seconds
                segment_stop_seconds = min(segment_start_seconds + segment_duration_seconds, 
                                         total_duration_seconds)
                
                segment_start_samples = int(segment_start_seconds * sfreq)
                segment_stop_samples = int(segment_stop_seconds * sfreq)
                
                print(f"→ Processing segment {segment_idx + 1}/{n_segments}: "
                      f"{segment_start_seconds:.1f}s - {segment_stop_seconds:.1f}s")
                
                try:
                    # Process windows within current segment
                    adj_matrices_list, node_features_list, edge_features_list, window_starts = \
                        _process_segment_windows(
                            self.edf_loader.edf_file_path,
                            segment_start_samples,
                            segment_stop_samples,
                            self.window_size,
                            self.adj_window_size,
                            window_step,
                            sfreq
                        )
                    
                    n_windows = len(adj_matrices_list)
                    if n_windows > 0:
                        print(f"   → Appending {n_windows} windows to HDF5...")
                        
                        # Save results immediately to HDF5
                        _append_to_hdf5(h5_file, adj_matrices_list, node_features_list, 
                                       edge_features_list, window_starts)
                        
                        total_windows_processed += n_windows
                        print(f"   ✔ Processed {n_windows} windows, total: {total_windows_processed}")
                        
                        # Show current HDF5 file size for debugging
                        current_hdf5_size = h5_file['adjacency_matrices'].shape[0]
                        print(f"   → HDF5 now contains {current_hdf5_size} total windows")
                    else:
                        print(f"   ⚠ No valid windows in segment {segment_idx + 1}")
                    
                    # Explicit memory cleanup
                    del adj_matrices_list, node_features_list, edge_features_list, window_starts
                    gc.collect()
                    
                except Exception as e:
                    print(f"   ✗ Error processing segment {segment_idx + 1}: {e}")
                    continue
            
            # Close progress bar and store final statistics
            pbar.close()
            h5_file.attrs['total_windows_processed'] = total_windows_processed
        
        print(f"✔ Complete graph representation saved to: {hdf5_path}")
        print(f"✔ Total windows processed: {total_windows_processed}")
        print(f"✔ Memory-safe processing completed successfully")
        
        return hdf5_path
    
    # ========================================================================
    # PUBLIC METHODS - Independent Analysis
    # ========================================================================

    def compute_correlation(
        self,
        start_time: float,
        stop_time: float,
        interval_seconds: float,
        edf_path: str = None,
        output_filename: str = None,
        overlap_ratio: float = 0.0
    ) -> Path:
        """
        Compute per‑interval correlation matrices over a subsegment of the EDF.

        :param start_time:      start of the segment (in seconds)
        :param stop_time:       end of the segment (in seconds)
        :param interval_seconds: length of each correlation window (in seconds)
        :param edf_path:        optional EDF filepath (defaults to self.edf_loader)
        :param output_filename: optional output pickle name
                                (defaults to "{filename}_{s0}-{s1}_corr.pickle")
        :returns:               Path to the pickle containing:
                                {
                                  "starts": [t0, t1, …],
                                  "corr_matrices": [mat0, mat1, …]
                                }
        """
        import pickle
        from pathlib import Path
        import mne

        # pick the file
        edf_path = edf_path or self.edf_loader.edf_file_path

        # read header only
        raw0 = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
        sfreq   = raw0.info["sfreq"]
        n_times = raw0.n_times
        raw0.close()

        # compute sample bounds
        start_samp = int(start_time * sfreq)
        stop_samp  = int(stop_time  * sfreq)
        if start_samp < 0 or stop_samp > n_times or stop_samp <= start_samp:
            raise ValueError(f"Invalid segment: {start_time}-{stop_time}s")

        # interval in samples
        interval_samps = int(interval_seconds * sfreq)
        if interval_samps <= 0:
            raise ValueError("interval_seconds must be > 0")

        # prepare accumulators
        corr_matrices = []
        starts        = []

        # slide through the segment in steps of interval_samps
        raw = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
        # calculate step size (with overlap support)
        step_samps = int(interval_samps * (1.0 - overlap_ratio))
        if step_samps <= 0:
            raise ValueError("overlap_ratio too high - results in zero or negative step size")
            
        for seg_start in range(start_samp, stop_samp - interval_samps + 1, step_samps):
            seg_stop  = seg_start + interval_samps
            block     = raw.get_data(start=seg_start, stop=seg_stop)
            mat       = _compute_correlation(block)
            corr_matrices.append(mat)
            # record time (in seconds) of this window’s start
            starts.append(seg_start / sfreq)
        raw.close()

        # default output filename
        if output_filename is None:
            s0 = int(start_time)
            s1 = int(stop_time)
            output_filename = f"{self.filename}_{s0}s-{s1}s_correlation.pickle"

        # Create organized subdirectory structure
        correlation_dir = self.output_dir / "correlation"
        correlation_dir.mkdir(parents=True, exist_ok=True)
        out_path = correlation_dir / output_filename
        
        with open(out_path, "wb") as f:
            pickle.dump({"starts": starts, "corr_matrices": corr_matrices}, f)

        print(f"✔ Saved {len(corr_matrices)} correlation matrices to: {out_path}")
        return out_path

    def compute_coherence_average(
        self,
        start_time: float,
        stop_time: float,
        interval_seconds: float,
        edf_path: str = None,
        output_filename: str = None,
        overlap_ratio: float = 0.0
    ) -> Path:
        """
        Compute per‑interval average coherence matrices over a subsegment of the EDF.
        Averages coherence across all frequency bands for simpler analysis.

        :param start_time:      start of the segment (in seconds)
        :param stop_time:       end of the segment (in seconds)
        :param interval_seconds: length of each coherence window (in seconds)
        :param edf_path:        optional EDF filepath (defaults to self.edf_loader)
        :param output_filename: optional output pickle name
                                (defaults to "{filename}_{s0}-{s1}_coh_avg.pickle")
        :param overlap_ratio:   overlap between windows (0.0 = no overlap, 0.5 = 50% overlap)
        :returns:               Path to the pickle containing:
                                {
                                  "starts": [t0, t1, …],
                                  "coherence_matrices": [mat0, mat1, …]
                                }
        """
        import pickle
        from pathlib import Path
        import mne

        # pick the file
        edf_path = edf_path or self.edf_loader.edf_file_path

        # read header only
        raw0 = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
        sfreq   = raw0.info["sfreq"]
        n_times = raw0.n_times
        raw0.close()

        # compute sample bounds
        start_samp = int(start_time * sfreq)
        stop_samp  = int(stop_time  * sfreq)
        if start_samp < 0 or stop_samp > n_times or stop_samp <= start_samp:
            raise ValueError(f"Invalid segment: {start_time}-{stop_time}s")

        # interval in samples
        interval_samps = int(interval_seconds * sfreq)
        if interval_samps <= 0:
            raise ValueError("interval_seconds must be > 0")

        # calculate step size (with overlap support)
        step_samps = int(interval_samps * (1.0 - overlap_ratio))
        if step_samps <= 0:
            raise ValueError("overlap_ratio too high - results in zero or negative step size")

        # prepare accumulators
        coherence_matrices = []
        starts = []

        # slide through the segment
        raw = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
        try:
            for seg_start in range(start_samp, stop_samp - interval_samps + 1, step_samps):
                seg_stop = seg_start + interval_samps
                if seg_stop > stop_samp:  # ensure we don't exceed bounds
                    break
                    
                block = raw.get_data(start=seg_start, stop=seg_stop)
                
                # validate block has data
                if block.size == 0:
                    print(f"Warning: Empty block at {seg_start/sfreq:.2f}s, skipping")
                    continue
                
                # use legacy coherence calculation
                coherence_result = calculate_coherence_signal_trace(block, sfreq)
                coherences_dict = coherence_result['coherence']
                
                # average across all frequency bands
                coherences = []
                for key in coherences_dict.keys():
                    coherences.append(coherences_dict[key])
                avg_coherence = mean(coherences, axis=0)
                
                coherence_matrices.append(avg_coherence)
                starts.append(seg_start / sfreq)
        finally:
            raw.close()

        # default output filename
        if output_filename is None:
            s0 = int(start_time)
            s1 = int(stop_time)
            output_filename = f"{self.filename}_{s0}s-{s1}s_coherence_avg.pickle"

        # Create organized subdirectory structure
        coherence_dir = self.output_dir / "coherence" / "average"
        coherence_dir.mkdir(parents=True, exist_ok=True)
        out_path = coherence_dir / output_filename
        
        with open(out_path, "wb") as f:
            pickle.dump({"starts": starts, "coherence_matrices": coherence_matrices}, f)

        print(f"✔ Saved {len(coherence_matrices)} average coherence matrices to: {out_path}")
        return out_path

    def compute_coherence_bands(
        self,
        start_time: float,
        stop_time: float,
        interval_seconds: float,
        edf_path: str = None,
        output_filename: str = None,
        overlap_ratio: float = 0.0
    ) -> Path:
        """
        Compute per‑interval coherence matrices by frequency band over a subsegment of the EDF.
        Provides detailed frequency-specific coherence analysis.

        :param start_time:      start of the segment (in seconds)
        :param stop_time:       end of the segment (in seconds)
        :param interval_seconds: length of each coherence window (in seconds)
        :param edf_path:        optional EDF filepath (defaults to self.edf_loader)
        :param output_filename: optional output pickle name
                                (defaults to "{filename}_{s0}s-{s1}s_coherence_bands.pickle")
        :param overlap_ratio:   overlap between windows (0.0 = no overlap, 0.5 = 50% overlap)
        :returns:               Path to the pickle containing:
                                {
                                  "starts": [t0, t1, …],
                                  "coherence_by_band": {
                                    "delta": [mat0, mat1, …],
                                    "theta": [mat0, mat1, …],
                                    ...
                                  },
                                  "frequency_bands": {"delta": (1, 4), "theta": (4, 8), ...}
                                }
        """
        import pickle
        from pathlib import Path
        import mne

        # pick the file
        edf_path = edf_path or self.edf_loader.edf_file_path

        # read header only
        raw0 = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
        sfreq   = raw0.info["sfreq"]
        n_times = raw0.n_times
        raw0.close()

        # compute sample bounds
        start_samp = int(start_time * sfreq)
        stop_samp  = int(stop_time  * sfreq)
        if start_samp < 0 or stop_samp > n_times or stop_samp <= start_samp:
            raise ValueError(f"Invalid segment: {start_time}-{stop_time}s")

        # interval in samples
        interval_samps = int(interval_seconds * sfreq)
        if interval_samps <= 0:
            raise ValueError("interval_seconds must be > 0")

        # calculate step size (with overlap support)
        step_samps = int(interval_samps * (1.0 - overlap_ratio))
        if step_samps <= 0:
            raise ValueError("overlap_ratio too high - results in zero or negative step size")

        # get frequency bands for this sampling rate
        freq_bands = _compute_frequency_bands(sfreq)
        
        # prepare accumulators
        coherence_by_band = {band: [] for band in freq_bands.keys()}
        starts = []

        # slide through the segment
        raw = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
        try:
            for seg_start in range(start_samp, stop_samp - interval_samps + 1, step_samps):
                seg_stop = seg_start + interval_samps
                if seg_stop > stop_samp:  # ensure we don't exceed bounds
                    break
                    
                block = raw.get_data(start=seg_start, stop=seg_stop)
                
                # validate block has data
                if block.size == 0:
                    print(f"Warning: Empty block at {seg_start/sfreq:.2f}s, skipping")
                    continue
                
                # use legacy coherence calculation
                coherence_result = calculate_coherence_signal_trace(block, sfreq)
                coherences_dict = coherence_result['coherence']
                
                # store each frequency band separately
                for band in freq_bands.keys():
                    if band in coherences_dict:
                        coherence_by_band[band].append(coherences_dict[band])
                
                starts.append(seg_start / sfreq)
        finally:
            raw.close()

        # default output filename
        if output_filename is None:
            s0 = int(start_time)
            s1 = int(stop_time)
            output_filename = f"{self.filename}_{s0}s-{s1}s_coherence_bands.pickle"

        # Create organized subdirectory structure
        coherence_dir = self.output_dir / "coherence" / "bands"
        coherence_dir.mkdir(parents=True, exist_ok=True)
        out_path = coherence_dir / output_filename
        
        with open(out_path, "wb") as f:
            pickle.dump({
                "starts": starts, 
                "coherence_by_band": coherence_by_band,
                "frequency_bands": freq_bands
            }, f)

        print(f"✔ Saved {len(starts)} time windows with coherence by frequency band to: {out_path}")
        return out_path
    
    # ========================================================================
    # PUBLIC METHODS - Visualization
    # ========================================================================

    def plot_connectivity_matrices(
        self,
        plot_types: list = None,
        time_range: tuple = None,
        output_subdir: str = "plots",
        save_individual: bool = True,
        save_summary: bool = True,
        dpi: int = 150,
        figsize: tuple = (10, 8)
    ) -> dict:
        """
        Plot connectivity matrices from saved EEGGraphProcessor results.
        
        :param plot_types: List of plot types to generate. Options: 
                          ["correlation", "coherence_avg", "coherence_bands"]
                          If None, plots all available data types
        :param time_range: Tuple of (start_time, stop_time) to filter plots. 
                          If None, plots all available time windows
        :param output_subdir: Subdirectory name for plots (default: "plots")
        :param save_individual: Whether to save individual matrix plots
        :param save_summary: Whether to save summary/comparison plots
        :param dpi: Resolution for saved plots
        :param figsize: Figure size as (width, height) tuple
        :returns: Dictionary mapping plot types to their output directory paths
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
        except ImportError:
            raise ImportError("Plotting requires matplotlib and seaborn. Install with: pip install matplotlib seaborn")
        
        # Set default plot types if none specified
        if plot_types is None:
            plot_types = ["correlation", "coherence_avg", "coherence_bands"]
        
        # Setup plotting configuration
        self._setup_plotting()
        
        # Get channel names for axis labels
        channel_names = self._get_channel_names()
        
        # Initialize results dictionary
        results = {}
        
        print(f"\n🎨 Starting connectivity matrix plotting...")
        print(f"   📊 Plot types: {plot_types}")
        print(f"   📁 Output subdirectory: {output_subdir}")
        
        # Process each plot type
        for plot_type in plot_types:
            try:
                if plot_type == "correlation":
                    output_dir = self._plot_correlation_data(
                        channel_names, time_range, output_subdir, 
                        save_individual, save_summary, dpi, figsize
                    )
                elif plot_type == "coherence_avg":
                    output_dir = self._plot_coherence_avg_data(
                        channel_names, time_range, output_subdir,
                        save_individual, save_summary, dpi, figsize
                    )
                elif plot_type == "coherence_bands":
                    output_dir = self._plot_coherence_bands_data(
                        channel_names, time_range, output_subdir,
                        save_individual, save_summary, dpi, figsize
                    )
                else:
                    print(f"⚠️  Unknown plot type: {plot_type}")
                    continue
                
                if output_dir:
                    results[plot_type] = output_dir
                    print(f"✅ {plot_type} plots completed: {output_dir}")
                else:
                    print(f"⚠️  No data found for {plot_type}")
                    
            except Exception as e:
                print(f"❌ Error plotting {plot_type}: {e}")
                continue
        
        if results:
            print(f"\n🎉 Plotting completed successfully!")
            print(f"📁 Plot directories created:")
            for plot_type, path in results.items():
                print(f"   📈 {plot_type}: {path}")
        else:
            print(f"\n⚠️  No plots were generated. Check that data files exist.")
        
        return results

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _setup_plotting(self):
        """Configure matplotlib and seaborn for consistent plot styling"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.style.use('default')
        sns.set_palette("viridis")
        plt.rcParams['figure.figsize'] = (10, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12

    def _get_channel_names(self):
        """Get channel names from saved data or generate default names"""
        try:
            # Try to load channel names from saved file
            ch_names_file = self.output_dir / "ch_names.pickle"
            if ch_names_file.exists():
                with open(ch_names_file, 'rb') as f:
                    import pickle
                    return pickle.load(f)
        except:
            pass
        
        # Try to get channel names from EDF loader
        try:
            import mne
            raw = mne.io.read_raw_edf(self.edf_loader.edf_file_path, preload=False, verbose=False)
            ch_names = raw.ch_names
            raw.close()
            return ch_names
        except:
            pass
        
        # Fallback: return None (will use indices)
        return None

    def _filter_by_time_range(self, time_points, matrices, time_range):
        """Filter matrices by time range if specified"""
        if time_range is None:
            return time_points, matrices
        
        start_time, stop_time = time_range
        indices = [i for i, t in enumerate(time_points) 
                  if start_time <= t <= stop_time]
        
        filtered_times = [time_points[i] for i in indices]
        filtered_matrices = [matrices[i] for i in indices]
        
        return filtered_times, filtered_matrices

    def _create_plot_directory(self, base_dir, subdir_name):
        """Create and return plot directory path"""
        plot_dir = base_dir / subdir_name
        plot_dir.mkdir(parents=True, exist_ok=True)
        return plot_dir

    def _save_plot_with_channels(self, fig, filepath, channel_names, matrix_shape):
        """Save plot with proper channel name formatting on axes"""
        if channel_names and len(channel_names) >= matrix_shape[0]:
            ax = fig.gca()
            n_channels = matrix_shape[0]
            
            # Show ALL channel names - EEG channel names are typically short
            indices = range(n_channels)
            labels = [channel_names[i] for i in indices]
            
            ax.set_xticks(indices)
            ax.set_yticks(indices)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_xlabel('EEG Channels')
            ax.set_ylabel('EEG Channels')
            
            # Adjust layout to accommodate all labels
            fig.subplots_adjust(bottom=0.15, left=0.15)
        
        fig.savefig(filepath, dpi=150, bbox_inches='tight')

    def _plot_correlation_data(self, channel_names, time_range, output_subdir, 
                              save_individual, save_summary, dpi, figsize):
        """Plot correlation matrices from saved data"""
        import matplotlib.pyplot as plt
        import numpy as np
        import pickle
        import glob
        
        # Find correlation data files
        corr_dir = self.output_dir / "correlation"
        if not corr_dir.exists():
            return None
        
        corr_files = list(corr_dir.glob("*.pickle"))
        if not corr_files:
            return None
        
        # Use the first file found (could be enhanced to handle multiple files)
        corr_file = corr_files[0]
        
        try:
            with open(corr_file, 'rb') as f:
                corr_data = pickle.load(f)
        except Exception as e:
            print(f"Error loading correlation data: {e}")
            return None
        
        matrices = corr_data['corr_matrices']
        time_points = corr_data['starts']
        
        # Filter by time range if specified
        time_points, matrices = self._filter_by_time_range(time_points, matrices, time_range)
        
        if not matrices:
            return None
        
        # Create output directory
        plot_dir = self._create_plot_directory(corr_dir, output_subdir)
        
        print(f"   🔄 Plotting {len(matrices)} correlation matrices...")
        
        # Plot individual matrices if requested
        if save_individual:
            individual_dir = plot_dir / "individual"
            individual_dir.mkdir(exist_ok=True)
            
            for i, (matrix, time_point) in enumerate(zip(matrices, time_points)):
                fig, ax = plt.subplots(figsize=figsize)
                
                # Create heatmap
                im = ax.imshow(matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='equal')
                
                # Customize plot
                ax.set_title(f'Correlation Matrix at t={time_point:.1f}s', 
                           fontsize=14, fontweight='bold')
                
                # Add colorbar
                cbar = plt.colorbar(im, ax=ax, shrink=0.8)
                cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)
                
                # Add grid
                ax.grid(True, alpha=0.3)
                
                # Save with channel names
                filename = f"correlation_t{time_point:06.1f}s.png"
                filepath = individual_dir / filename
                self._save_plot_with_channels(fig, filepath, channel_names, matrix.shape)
                plt.close()
                
                if (i + 1) % 10 == 0:
                    print(f"      📈 Saved {i + 1}/{len(matrices)} individual plots")
        
        # Create summary plots if requested
        if save_summary:
            self._create_correlation_summary(matrices, time_points, plot_dir, channel_names)
        
        return plot_dir

    def _create_correlation_summary(self, matrices, time_points, output_dir, channel_names):
        """Create summary plots for correlation analysis"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Calculate mean correlation over time (excluding diagonal)
        mean_corrs = []
        for matrix in matrices:
            mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)
            mean_corr = np.mean(matrix[mask])
            mean_corrs.append(mean_corr)
        
        # Create summary plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Time series of mean correlation
        ax1.plot(time_points, mean_corrs, 'b-', linewidth=2, marker='o', markersize=4)
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Mean Correlation')
        ax1.set_title('Mean Correlation Over Time', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Histogram of correlation values
        all_corrs = []
        for matrix in matrices:
            mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)
            all_corrs.extend(matrix[mask])
        
        ax2.hist(all_corrs, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.set_xlabel('Correlation Coefficient')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Distribution of All Correlation Values', fontweight='bold')
        ax2.axvline(np.mean(all_corrs), color='red', linestyle='--', 
                    label=f'Mean: {np.mean(all_corrs):.3f}')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "correlation_summary.png", dpi=150, bbox_inches='tight')
        plt.close()

    def _plot_coherence_avg_data(self, channel_names, time_range, output_subdir,
                                save_individual, save_summary, dpi, figsize):
        """Plot average coherence matrices from saved data"""
        import matplotlib.pyplot as plt
        import numpy as np
        import pickle
        
        # Find coherence average data files
        coh_avg_dir = self.output_dir / "coherence" / "average"
        if not coh_avg_dir.exists():
            return None
        
        coh_files = list(coh_avg_dir.glob("*.pickle"))
        if not coh_files:
            return None
        
        # Use the first file found
        coh_file = coh_files[0]
        
        try:
            with open(coh_file, 'rb') as f:
                coh_data = pickle.load(f)
        except Exception as e:
            print(f"Error loading coherence average data: {e}")
            return None
        
        matrices = coh_data['coherence_matrices']
        time_points = coh_data['starts']
        
        # Filter by time range if specified
        time_points, matrices = self._filter_by_time_range(time_points, matrices, time_range)
        
        if not matrices:
            return None
        
        # Create output directory
        plot_dir = self._create_plot_directory(coh_avg_dir, output_subdir)
        
        print(f"   🔄 Plotting {len(matrices)} average coherence matrices...")
        
        # Plot individual matrices if requested
        if save_individual:
            individual_dir = plot_dir / "individual"
            individual_dir.mkdir(exist_ok=True)
            
            for i, (matrix, time_point) in enumerate(zip(matrices, time_points)):
                fig, ax = plt.subplots(figsize=figsize)
                
                # Create heatmap
                im = ax.imshow(matrix, cmap='plasma', vmin=0, vmax=1, aspect='equal')
                
                # Customize plot
                ax.set_title(f'Average Coherence Matrix at t={time_point:.1f}s', 
                           fontsize=14, fontweight='bold')
                
                # Add colorbar
                cbar = plt.colorbar(im, ax=ax, shrink=0.8)
                cbar.set_label('Coherence', rotation=270, labelpad=20)
                
                # Add grid
                ax.grid(True, alpha=0.3)
                
                # Save with channel names
                filename = f"coherence_avg_t{time_point:06.1f}s.png"
                filepath = individual_dir / filename
                self._save_plot_with_channels(fig, filepath, channel_names, matrix.shape)
                plt.close()
                
                if (i + 1) % 10 == 0:
                    print(f"      📈 Saved {i + 1}/{len(matrices)} individual plots")
        
        # Create summary plots if requested
        if save_summary:
            self._create_coherence_avg_summary(matrices, time_points, plot_dir, channel_names)
        
        return plot_dir

    def _create_coherence_avg_summary(self, matrices, time_points, output_dir, channel_names):
        """Create summary plots for average coherence analysis"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Calculate mean coherence over time (excluding diagonal)
        mean_cohs = []
        for matrix in matrices:
            mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)
            mean_coh = np.mean(matrix[mask])
            mean_cohs.append(mean_coh)
        
        # Create summary plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Time series of mean coherence
        ax1.plot(time_points, mean_cohs, 'purple', linewidth=2, marker='o', markersize=4)
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Mean Coherence')
        ax1.set_title('Mean Average Coherence Over Time', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Histogram of coherence values
        all_cohs = []
        for matrix in matrices:
            mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)
            all_cohs.extend(matrix[mask])
        
        ax2.hist(all_cohs, bins=50, alpha=0.7, color='plum', edgecolor='black')
        ax2.set_xlabel('Coherence')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Distribution of All Average Coherence Values', fontweight='bold')
        ax2.axvline(np.mean(all_cohs), color='red', linestyle='--', 
                    label=f'Mean: {np.mean(all_cohs):.3f}')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "coherence_avg_summary.png", dpi=150, bbox_inches='tight')
        plt.close()

    def _plot_coherence_bands_data(self, channel_names, time_range, output_subdir,
                                  save_individual, save_summary, dpi, figsize):
        """Plot frequency-band specific coherence matrices from saved data"""
        import matplotlib.pyplot as plt
        import numpy as np
        import pickle
        
        # Find coherence bands data files
        coh_bands_dir = self.output_dir / "coherence" / "bands"
        if not coh_bands_dir.exists():
            return None
        
        coh_files = list(coh_bands_dir.glob("*.pickle"))
        if not coh_files:
            return None
        
        # Use the first file found
        coh_file = coh_files[0]
        
        try:
            with open(coh_file, 'rb') as f:
                coh_data = pickle.load(f)
        except Exception as e:
            print(f"Error loading coherence bands data: {e}")
            return None
        
        coherence_by_band = coh_data['coherence_by_band']
        frequency_bands = coh_data['frequency_bands']
        time_points = coh_data['starts']
        
        # Create output directory
        plot_dir = self._create_plot_directory(coh_bands_dir, output_subdir)
        
        # Define colors for different frequency bands
        band_colors = {
            'delta': 'Blues',
            'theta': 'Greens', 
            'alpha': 'Oranges',
            'beta': 'Reds',
            'gamma': 'Purples',
            'gammaHi': 'plasma',
            'ripples': 'viridis',
            'fastRipples': 'inferno'
        }
        
        total_plots = sum(len(matrices) for matrices in coherence_by_band.values())
        print(f"   🔄 Plotting {total_plots} band-specific coherence matrices across {len(coherence_by_band)} bands...")
        
        plots_saved = 0
        
        # Plot matrices for each frequency band
        for band_name, matrices in coherence_by_band.items():
            if len(matrices) == 0:
                continue
            
            # Filter by time range if specified
            filtered_times, filtered_matrices = self._filter_by_time_range(
                time_points, matrices, time_range)
            
            if not filtered_matrices:
                continue
            
            freq_range = frequency_bands[band_name]
            colormap = band_colors.get(band_name, 'viridis')
            
            print(f"      🎵 Processing {band_name} band ({freq_range[0]}-{freq_range[1]} Hz): {len(filtered_matrices)} matrices")
            
            # Plot individual matrices if requested
            if save_individual:
                # Create subdirectory for this band
                band_dir = plot_dir / "individual" / band_name
                band_dir.mkdir(parents=True, exist_ok=True)
                
                for i, (matrix, time_point) in enumerate(zip(filtered_matrices, filtered_times)):
                    fig, ax = plt.subplots(figsize=figsize)
                    
                    # Create heatmap
                    im = ax.imshow(matrix, cmap=colormap, vmin=0, vmax=1, aspect='equal')
                    
                    # Customize plot
                    title = f'{band_name.capitalize()} Coherence ({freq_range[0]}-{freq_range[1]} Hz) at t={time_point:.1f}s'
                    ax.set_title(title, fontsize=14, fontweight='bold')
                    
                    # Add colorbar
                    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
                    cbar.set_label('Coherence', rotation=270, labelpad=20)
                    
                    # Add grid
                    ax.grid(True, alpha=0.3)
                    
                    # Save with channel names
                    filename = f"{band_name}_coherence_t{time_point:06.1f}s.png"
                    filepath = band_dir / filename
                    self._save_plot_with_channels(fig, filepath, channel_names, matrix.shape)
                    plt.close()
                    
                    plots_saved += 1
                    if plots_saved % 20 == 0:
                        print(f"         📈 Saved {plots_saved}/{total_plots} band plots")
        
        # Create band comparison summary if requested
        if save_summary:
            self._create_band_coherence_summary(coherence_by_band, frequency_bands, 
                                              time_points, plot_dir, time_range)
        
        return plot_dir

    def _create_band_coherence_summary(self, coherence_by_band, frequency_bands, 
                                     time_points, output_dir, time_range):
        """Create summary comparison across frequency bands"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Calculate mean coherence for each band over time
        band_means = {}
        for band_name, matrices in coherence_by_band.items():
            if len(matrices) == 0:
                continue
            
            # Filter by time range if specified
            filtered_times, filtered_matrices = self._filter_by_time_range(
                time_points, matrices, time_range)
            
            if not filtered_matrices:
                continue
            
            means = []
            for matrix in filtered_matrices:
                mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)
                mean_coh = np.mean(matrix[mask])
                means.append(mean_coh)
            band_means[band_name] = (means, filtered_times)
        
        if not band_means:
            return
        
        # Create comparison plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # Time series comparison
        colors = plt.cm.Set3(np.linspace(0, 1, len(band_means)))
        for i, (band_name, (means, times)) in enumerate(band_means.items()):
            freq_range = frequency_bands[band_name]
            label = f'{band_name} ({freq_range[0]}-{freq_range[1]} Hz)'
            ax1.plot(times, means, color=colors[i], linewidth=2, 
                    marker='o', markersize=3, label=label)
        
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Mean Coherence')
        ax1.set_title('Mean Coherence by Frequency Band Over Time', fontweight='bold')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Box plot comparison
        band_data = []
        band_labels = []
        for band_name, matrices in coherence_by_band.items():
            if len(matrices) == 0:
                continue
            
            # Filter by time range if specified
            _, filtered_matrices = self._filter_by_time_range(
                time_points, matrices, time_range)
            
            if not filtered_matrices:
                continue
            
            all_values = []
            for matrix in filtered_matrices:
                mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)
                all_values.extend(matrix[mask])
            
            if all_values:  # Only add if we have data
                band_data.append(all_values)
                freq_range = frequency_bands[band_name]
                band_labels.append(f'{band_name}\n({freq_range[0]}-{freq_range[1]} Hz)')
        
        if band_data:  # Only create box plot if we have data
            ax2.boxplot(band_data, labels=band_labels)
            ax2.set_ylabel('Coherence')
            ax2.set_title('Coherence Distribution by Frequency Band', fontweight='bold')
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(output_dir / "band_coherence_summary.png", dpi=150, bbox_inches='tight')
        plt.close()
