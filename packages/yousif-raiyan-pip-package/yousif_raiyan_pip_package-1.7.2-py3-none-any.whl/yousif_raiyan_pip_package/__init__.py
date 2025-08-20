__version__ = "1.7.2"

from .eeg_graph_representation import EEGGraphProcessor
from .edf_loader import EDFLoader
from .trigger_detector import TriggerDetector
from .analyzer import Analyzer
from .fooof_analyzer import FOOOFAnalyzer

__all__ = ["EEGGraphProcessor",
           "EDFLoader",
           "TriggerDetector",
           "Analyzer",
           "FOOOFAnalyzer"]