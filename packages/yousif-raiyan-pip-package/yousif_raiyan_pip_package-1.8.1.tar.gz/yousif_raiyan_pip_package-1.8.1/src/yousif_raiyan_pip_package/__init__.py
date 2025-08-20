__version__ = "1.8.1"

from .edf_loader import EDFLoader
from .trigger_detector import TriggerDetector
from .analyzer import Analyzer
from .eeg_graph_representation import EEGGraphProcessor
from .fooof_analyzer import FOOOFAnalyzer
from .spectral_analyzer import SpectralAnalyzer
from .connectivity_analyzer import ConnectivityAnalyzer

__all__ = ["EEGGraphProcessor",
           "EDFLoader", 
           "TriggerDetector",
           "Analyzer",
           "FOOOFAnalyzer",
           "SpectralAnalyzer",
           "ConnectivityAnalyzer"]