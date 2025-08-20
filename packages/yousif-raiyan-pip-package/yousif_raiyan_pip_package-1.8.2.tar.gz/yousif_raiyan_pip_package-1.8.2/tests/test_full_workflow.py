#!/usr/bin/env python3
"""
Complete EEG analysis workflow test script
Tests EDFLoader -> TriggerDetector -> Analyzer pipeline
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.yousif_raiyan_pip_package import EDFLoader, TriggerDetector, Analyzer

def test_full_workflow():
    """Test the complete EEG analysis workflow"""
    
    print("=" * 70)
    print("Complete EEG Analysis Workflow Test")
    print("=" * 70)
    
    # Step 1: EDFLoader
    print("Step 1: EDFLoader")
    print("-" * 30)
    
    folder_path = "data"
    name = "Sebastian"
    
    try:
        # Initialize loader
        loader = EDFLoader(folder_path, name)
        print("✅ EDFLoader initialized")
        
        # Inspect data to identify available signals
        print("\nInspecting EDF file structure...")
        loader.inspect_data()
        print("✅ Data inspection complete - T2 and T6 signals identified for analysis")
        
        # Load T2 and T6 signals
        print("\nLoading T2 and T6 temporal channels...")
        loader.load_and_plot_signals(
            signal_indices=[15,25],  # T6, T2
            duration=1200.0,  # 20 minutes to capture multiple seizure events
            save_plots=True
        )
        print("✅ T2 and T6 temporal channels loaded and plotted")
        
        # Step 2: TriggerDetector
        print("\n" + "=" * 50)
        print("Step 2: TriggerDetector")
        print("-" * 30)
        
        # Initialize detector with T2 signal
        available_signals = list(loader.signals_dict.keys())
        signal_choice = 'T2' if 'T2' in available_signals else available_signals[0]
        print(f"Using signal: {signal_choice}")
        
        detector = TriggerDetector(loader, signal_choice)
        print("✅ TriggerDetector initialized")
        
        # Detect triggers in T2 signal
        print("\nDetecting triggers...")
        detector.detect_triggers()
        print(f"✅ Found {len(detector.df_triggers)} triggers")
        
        # Visualize detected triggers
        print("\nPlotting trigger detection results...")
        detector.plot_triggers()
        print("✅ Trigger visualization completed")
        
        # Generate window plots for inter-trigger intervals
        print("\nGenerating window plots...")
        detector.plot_windows()
        print("✅ Window plots created")
        
        # Step 3: Analyzer
        print("\n" + "=" * 50)
        print("Step 3: Analyzer")
        print("-" * 30)
        
        # Initialize frequency-domain analyzer
        analyzer = Analyzer(loader, detector, target_length=50)
        print("✅ Analyzer initialized")
        
        # Test window aggregation methods
        print("\nTesting window aggregation methods...")
        
        # Use T6 for temporal lobe analysis
        test_channel = 'T6' if 'T6' in available_signals else available_signals[0]
        print(f"Analyzing channel: {test_channel}")
        
        try:
            # Test arithmetic mean aggregation
            print("Testing mean aggregation...")
            analyzer.plot_average_window(test_channel, start_window=0, end_window=None, 
                                       target_length=500, aggregation_method='mean')
            print("✅ Mean aggregation completed")
            
            # Test median aggregation (robust to outliers)
            print("Testing median aggregation...")
            analyzer.plot_average_window(test_channel, start_window=0, end_window=None, 
                                       target_length=500, aggregation_method='median')
            print("✅ Median aggregation completed")
            
            # Test trimmed mean aggregation (trim 10% from each side)
            print("Testing trimmed mean aggregation...")
            analyzer.plot_average_window(test_channel, start_window=0, end_window=None, 
                                       target_length=500, aggregation_method='trimmed', trim_ratio=0.1)
            print("✅ Trimmed mean aggregation completed")
            
        except Exception as e:
            print(f"⚠️  Window aggregation failed: {e}")
        
        # Optional: Full frequency-domain analysis
        print("\n" + "-" * 40)
        print("Optional: Frequency-Domain Analysis")
        print("-" * 40)
        
        response = input("Run full frequency-domain analysis? This processes all EEG bands (y/n): ")
        if response.lower() == 'y':
            print("Running frequency-domain analysis across all EEG bands...")
            analyzer.extract_signals()
            print("✅ Frequency-domain analysis completed!")
            print(f"Output files saved to: {loader.folder_path}/{loader.name}/")
        else:
            print("⏭️  Skipping frequency-domain analysis")
        
        print("\n" + "=" * 70)
        print("EEG Analysis Workflow Complete!")
        print("Successfully tested EDFLoader -> TriggerDetector -> Analyzer pipeline")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure the file exists at: data/Sebastian/Sebastian.edf")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_workflow()