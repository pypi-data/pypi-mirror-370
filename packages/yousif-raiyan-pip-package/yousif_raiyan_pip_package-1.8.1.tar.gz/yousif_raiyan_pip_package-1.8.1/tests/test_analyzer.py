#!/usr/bin/env python3
"""
Test script for Analyzer class
Tests EEG frequency-domain analysis functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.yousif_raiyan_pip_package import EDFLoader, TriggerDetector, Analyzer

def test_analyzer():
    """Test the Analyzer class with Sebastian dataset"""
    
    print("=" * 60)
    print("Testing Analyzer Class")
    print("=" * 60)
    
    # Step 1: Initialize EDFLoader
    print("Step 1: Initializing EDFLoader...")
    folder_path = "data"
    name = "Sebastian"
    
    try:
        loader = EDFLoader(folder_path=folder_path, name=name)
        print("✅ EDFLoader initialized successfully")
        
        # Load a subset of signals to find triggers
        print("\nLoading T2 and T6 with 20 minutes duration...")
        loader.load_and_plot_signals(
            signal_indices=[15,25], # T6, T2
            duration=12000.0, 
            save_plots=True
        )
        print("✅ Signals loaded successfully")
        
        # Step 2: Initialize TriggerDetector
        print("\nStep 2: Initializing TriggerDetector...")
        
        # Get available signal names
        signal_names = list(loader.signals_dict.keys())
        print(f"Available signals: {signal_names}")
        
        # Use the first signal for trigger detection
        signal_choice = signal_names[0]
        print(f"Using signal '{signal_choice}' for trigger detection")
        
        trigger_detector = TriggerDetector(loader, signal_choice)
        print("✅ TriggerDetector initialized successfully")
        
        # Detect triggers
        print("\nDetecting triggers...")
        trigger_detector.detect_triggers()
        print(f"✅ Found {len(trigger_detector.df_triggers)} triggers")
        
        if len(trigger_detector.df_triggers) > 0:
            print("Trigger summary:")
            print(trigger_detector.df_triggers[['start_time (s)', 'end_time (s)', 'duration_time (s)']].head())
        else:
            print("⚠️  No triggers found - creating dummy triggers for testing")
            # Create dummy triggers for testing if none found
            import pandas as pd
            import numpy as np
            sample_rate = loader.signals_dict[signal_choice]['sample_rate']
            signal_length = len(loader.signals_dict[signal_choice]['data'])
            
            # Create 3 dummy triggers with proper non-overlapping segments
            # Each trigger is 10 seconds long with 20 second gaps between them
            trigger_duration = int(10 * sample_rate)  # 10 seconds
            gap_duration = int(20 * sample_rate)      # 20 seconds
            
            start_indices = [
                0,
                trigger_duration + gap_duration,
                2 * (trigger_duration + gap_duration)
            ]
            end_indices = [
                trigger_duration,
                2 * trigger_duration + gap_duration,
                3 * trigger_duration + 2 * gap_duration
            ]
            
            # Ensure we don't exceed signal length
            end_indices = [min(end_idx, signal_length - 1) for end_idx in end_indices]
            
            dummy_triggers = pd.DataFrame({
                'start_index': start_indices,
                'end_index': end_indices,
                'duration_samples': [end_indices[i] - start_indices[i] for i in range(3)],
                'start_time (s)': [idx / sample_rate for idx in start_indices],
                'end_time (s)': [idx / sample_rate for idx in end_indices],
                'duration_time (s)': [(end_indices[i] - start_indices[i]) / sample_rate for i in range(3)]
            })
            trigger_detector.df_triggers = dummy_triggers
            print(f"✅ Created {len(dummy_triggers)} dummy triggers for testing")
        
        # Step 3: Initialize Analyzer
        print("\nStep 3: Initializing Analyzer...")
        analyzer = Analyzer(loader, trigger_detector, target_length=50)
        print("✅ Analyzer initialized successfully")
        
        # Display analyzer configuration
        print(f"\nAnalyzer Configuration:")
        print(f"  - Target length: {analyzer.target_length}")
        print(f"  - EEG bands: {list(analyzer.bands.keys())}")
        print(f"  - Smoothing windows: {analyzer.smoothing_window_secs} seconds")
        print(f"  - Loaded channels: {analyzer.channels}")
        print(f"  - Number of channels: {len(analyzer.channels)}")
        print(f"  - Standard EEG channels available for reference: {len(analyzer.standard_eeg_channels)}")
        
        # Step 4: Test plotting methods
        print("\nStep 4: Testing plotting methods...")
        
        # Test plot_signal_window
        if len(trigger_detector.df_triggers) > 1:
            print("Testing plot_signal_window()...")
            try:
                analyzer.plot_signal_window(window_index=0, lead=signal_choice)
                print("✅ plot_signal_window() completed successfully")
            except Exception as e:
                print(f"⚠️  plot_signal_window() failed: {e}")
        
        # Test plot_average_window with different aggregation methods
        print("Testing plot_average_window() methods...")
        try:
            # Test mean aggregation
            print("Testing mean aggregation...")
            analyzer.plot_average_window(
                channel=signal_choice, 
                start_window=0, 
                end_window=min(3, len(trigger_detector.df_triggers)), 
                target_length=100,
                aggregation_method='mean'
            )
            print("✅ Mean aggregation completed")
            
            # Test median aggregation
            print("Testing median aggregation...")
            analyzer.plot_average_window(
                channel=signal_choice, 
                start_window=0, 
                end_window=min(3, len(trigger_detector.df_triggers)), 
                target_length=100,
                aggregation_method='median'
            )
            print("✅ Median aggregation completed")
            
            # Test trimmed mean aggregation (trim 10% from each side)
            print("Testing trimmed mean aggregation...")
            analyzer.plot_average_window(
                channel=signal_choice, 
                start_window=0, 
                end_window=min(3, len(trigger_detector.df_triggers)), 
                target_length=100,
                aggregation_method='trimmed',
                trim_ratio=0.1
            )
            print("✅ Trimmed mean aggregation completed")
            
        except Exception as e:
            print(f"⚠️  plot_average_window() methods failed: {e}")
        
        # Step 5: Test main analysis
        print("\nStep 5: Testing main analysis...")
        print("⚠️  WARNING: extract_signals() will process all frequency bands and may take time...")
        
        response = input("Do you want to run extract_signals()? This will create CSV files and plots (y/n): ")
        if response.lower() == 'y':
            print("Running extract_signals()...")
            print("This will create frequency-domain analysis for all EEG bands...")
            
            try:
                analyzer.extract_signals()
                print("✅ extract_signals() completed successfully!")
                print(f"Check the folder: {loader.folder_path}/{loader.name}/ for output files")
            except Exception as e:
                print(f"❌ extract_signals() failed: {e}")
        else:
            print("⏭️  Skipping extract_signals()")
        
        print("\n" + "=" * 60)
        print("Analyzer Testing Complete!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure the file exists at: data/Sebastian/Sebastian.edf")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analyzer()