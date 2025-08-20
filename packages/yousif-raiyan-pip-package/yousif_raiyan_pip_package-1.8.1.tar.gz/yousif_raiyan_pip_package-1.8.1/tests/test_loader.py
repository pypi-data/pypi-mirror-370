#!/usr/bin/env python3
"""
Simple test script for EDFLoader class
Tests loading and inspecting an EDF file
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.yousif_raiyan_pip_package import EDFLoader

def test_edf_loader():
    """Test the EDFLoader with Sebastian dataset"""
    
    print("=" * 50)
    print("Testing EDFLoader")
    print("=" * 50)
    
    # Initialize the loader
    folder_path = "data"
    name = "Sebastian"
    
    try:
        print(f"Initializing EDFLoader with folder: {folder_path}, name: {name}")
        loader = EDFLoader(folder_path=folder_path, name=name)
        print("✅ EDFLoader initialized successfully")
        
        # Test inspect_data function
        print("\n" + "-" * 30)
        print("Testing inspect_data()...")
        print("-" * 30)
        loader.inspect_data()
        
        # Test load_and_plot_signals function with new features
        print("\n" + "-" * 30)
        print("Testing load_and_plot_signals() with new features...")
        print("-" * 30)
        
        # Give user options for testing new features
        print("Test options:")
        print("1. Load first 3 signals, 10 seconds duration, display plots")
        print("2. Load first 3 signals, 10 seconds duration, save plots")
        print("3. Load all signals (will show memory warning)")
        print("4. Skip signal loading")
        
        choice = input("Choose option (1/2/3/4): ").strip()
        
        if choice == '1':
            print("Testing: First 3 signals, 10 seconds, display...")
            loader.load_and_plot_signals(
                signal_indices=[0, 1, 2], 
                duration=10.0, 
                save_plots=False
            )
            print("✅ Test completed successfully")
            
        elif choice == '2':
            print("Testing: First 3 signals, 10 seconds, save to Plots/Sebastian...")
            loader.load_and_plot_signals(
                signal_indices=[0, 1, 2], 
                duration=10.0, 
                save_plots=True
            )
            print("✅ Test completed successfully")
            
        elif choice == '3':
            print("Testing: All signals (will show memory warning)...")
            confirm = input("This will show the memory warning. Continue? (y/n): ")
            if confirm.lower() == 'y':
                # Load just first few seconds to avoid potential crash but still show the memory warning
                loader.load_and_plot_signals(duration=3.0)
                print("✅ Memory warning test completed")
            else:
                print("⏭️  Cancelled")
        else:
            print("⏭️  Skipping signal loading")
        
        # Show info about loaded signals if any were loaded
        if hasattr(loader, 'signals_dict') and loader.signals_dict:
            print(f"\n📊 Loaded {len(loader.signals_dict)} signals:")
            for signal_name, signal_info in loader.signals_dict.items():
                data_shape = signal_info['data'].shape
                sample_rate = signal_info['sample_rate']
                print(f"  - {signal_name}: {data_shape} samples @ {sample_rate} Hz")
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure the file exists at: data/Sebastian/Sebastian.edf")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_edf_loader()