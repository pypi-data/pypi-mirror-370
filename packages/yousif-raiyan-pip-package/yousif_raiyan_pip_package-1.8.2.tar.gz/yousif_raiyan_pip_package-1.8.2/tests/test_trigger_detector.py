#!/usr/bin/env python3
"""
Test script for TriggerDetector class
Tests seizure trigger detection and window analysis functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.yousif_raiyan_pip_package import EDFLoader, TriggerDetector

def test_trigger_detector():
    """Test the TriggerDetector class with Sebastian dataset"""
    
    print("=" * 60)
    print("Testing TriggerDetector Class")
    print("=" * 60)
    
    # Step 1: Initialize EDFLoader
    print("Step 1: Setting up EDFLoader...")
    folder_path = "data"
    name = "Sebastian"
    
    try:
        loader = EDFLoader(folder_path=folder_path, name=name)
        print("✅ EDFLoader initialized successfully")
        
        # Load T2 signal for trigger detection
        print("\nLoading T2 signal for trigger detection...")
        loader.load_and_plot_signals(
            signal_indices=[25],  # T2 signal
            duration=600.0,  # 10 minutes to find multiple triggers
            save_plots=True
        )
        print("✅ T2 signal loaded successfully")
        
        # Step 2: Initialize TriggerDetector
        print("\nStep 2: Initializing TriggerDetector...")
        
        # Get available signal names
        signal_names = list(loader.signals_dict.keys())
        print(f"Available signals: {signal_names}")
        
        # Use T2 for trigger detection
        signal_choice = 'T2' if 'T2' in signal_names else signal_names[0]
        print(f"Using signal '{signal_choice}' for trigger detection")
        
        detector = TriggerDetector(loader, signal_choice)
        print("✅ TriggerDetector initialized successfully")
        
        # Display detector configuration
        print(f"\nTriggerDetector Configuration:")
        print(f"  - Signal: {detector.signal_choice}")
        print(f"  - Sample rate: {detector.sample_rate} Hz")
        print(f"  - Threshold: {detector.threshold_value} µV")
        print(f"  - Signal length: {len(detector.signal)} samples")
        print(f"  - Duration: {len(detector.signal)/detector.sample_rate:.1f} seconds")
        
        # Step 3: Test trigger detection
        print("\nStep 3: Testing trigger detection...")
        print("Detecting seizure triggers...")
        detector.detect_triggers()
        print(f"✅ Found {len(detector.df_triggers)} triggers")
        
        if len(detector.df_triggers) > 0:
            print("\nTrigger Summary:")
            print(detector.df_triggers[['start_time (s)', 'end_time (s)', 'duration_time (s)']])
        else:
            print("⚠️  No triggers found with current threshold")
            print("Consider adjusting threshold or using longer duration")
        
        # Step 4: Test visualization methods
        print("\nStep 4: Testing visualization methods...")
        
        # Test plot_triggers
        print("Testing plot_triggers()...")
        try:
            detector.plot_triggers()
            print("✅ Trigger plot completed successfully")
        except Exception as e:
            print(f"⚠️  plot_triggers() failed: {e}")
        
        # Step 5: Test file operations
        print("\nStep 5: Testing file operations...")
        
        # Test save_triggers
        print("Testing save_triggers()...")
        try:
            detector.save_triggers()
            print("✅ Triggers saved to CSV successfully")
        except Exception as e:
            print(f"⚠️  save_triggers() failed: {e}")
        
        # Step 6: Test window operations (if triggers found)
        if len(detector.df_triggers) > 0:
            print("\nStep 6: Testing window operations...")
            
            # Test plot_windows
            print("Testing plot_windows()...")
            try:
                detector.plot_windows()
                print("✅ Window plots created successfully")
            except Exception as e:
                print(f"⚠️  plot_windows() failed: {e}")
            
            # Test convert_to_video
            print("Testing convert_to_video()...")
            try:
                detector.convert_to_video()
                print("✅ Video conversion completed successfully")
            except Exception as e:
                print(f"⚠️  convert_to_video() failed: {e}")
            
            # Optional: Test ML-based filtering
            print("\nOptional: ML-based window filtering...")
            response = input("Test filter_bad_windows()? Uses built-in ML models (y/n): ")
            if response.lower() == 'y':
                try:
                    detector.filter_bad_windows()  # Uses built-in models automatically
                    print("✅ ML-based filtering completed successfully")
                except Exception as e:
                    print(f"⚠️  filter_bad_windows() failed: {e}")
            else:
                print("⏭️  Skipping ML filtering")
        else:
            print("\n⏭️  Skipping window operations - no triggers found")
        
        # Step 7: Summary
        print("\n" + "=" * 60)
        print("TriggerDetector Testing Summary")
        print("=" * 60)
        print(f"✅ Signal loaded: {signal_choice}")
        print(f"✅ Triggers detected: {len(detector.df_triggers)}")
        print(f"✅ Threshold used: {detector.threshold_value} µV")
        print(f"✅ Duration analyzed: {len(detector.signal)/detector.sample_rate:.1f} seconds")
        
        if len(detector.df_triggers) > 0:
            avg_duration = detector.df_triggers['duration_time (s)'].mean()
            print(f"✅ Average trigger duration: {avg_duration:.1f} seconds")
            print(f"✅ Output files saved to: {loader.folder_path}/{loader.name}/")
        
        print("=" * 60)
        print("TriggerDetector Testing Complete!")
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
    test_trigger_detector()