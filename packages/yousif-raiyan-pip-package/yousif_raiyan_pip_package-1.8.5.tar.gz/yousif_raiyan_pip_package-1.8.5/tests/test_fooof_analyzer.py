#!/usr/bin/env python3
"""
Test script for FOOOFAnalyzer class
Tests spectral parameterization functionality (SpecParam/FOOOF)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.yousif_raiyan_pip_package import EDFLoader, FOOOFAnalyzer

def test_fooof_analyzer():
    """Test the FOOOFAnalyzer class with Sebastian dataset"""
    
    print("=" * 60)
    print("Testing FOOOFAnalyzer Class")
    print("=" * 60)
    
    # Step 1: Initialize EDFLoader
    print("Step 1: Initializing EDFLoader...")
    folder_path = "data"
    name = "Sebastian"
    
    try:
        loader = EDFLoader(folder_path=folder_path, name=name)
        print("✅ EDFLoader initialized successfully")
        
        # Load a subset of signals for spectral parameterization analysis
        print("\nLoading T2 and T6 with 20 minutes duration...")
        loader.load_and_plot_signals(
            signal_indices=[15, 25],  # T6, T2
            duration=1200.0,  # 20 minutes
            save_plots=True
        )
        print("✅ Signals loaded successfully")
        
        # Get available signal names
        signal_names = list(loader.signals_dict.keys())
        print(f"Available signals: {signal_names}")
        
        # Step 2: Initialize FOOOFAnalyzer
        print("\nStep 2: Initializing FOOOFAnalyzer...")
        fooof_analyzer = FOOOFAnalyzer(loader)
        print("✅ FOOOFAnalyzer initialized successfully")
        
        # Display analyzer configuration
        print(f"\nFOOOFAnalyzer Configuration:")
        print(f"  - Frequency range: {fooof_analyzer.freq_range} Hz")
        print(f"  - Analysis settings: {fooof_analyzer.fooof_settings}")
        
        # Display library information
        lib_info = fooof_analyzer.get_library_info()
        print(f"  - Library: {lib_info['library']} v{lib_info['version']}")
        print(f"  - Description: {lib_info['description']}")
        print(f"  - Available channels: {fooof_analyzer.channels}")
        print(f"  - Number of channels: {len(fooof_analyzer.channels)}")
        
        # Step 3: Test configuration methods
        print("\nStep 3: Testing configuration methods...")
        
        # Test frequency range setting
        print("Testing set_frequency_range()...")
        fooof_analyzer.set_frequency_range((1, 50))
        print(f"✅ Frequency range updated to: {fooof_analyzer.freq_range} Hz")
        
        # Test analysis settings
        print("Testing set_fooof_settings()...")
        fooof_analyzer.set_fooof_settings(
            max_n_peaks=8,
            peak_threshold=1.5,
            aperiodic_mode='knee'
        )
        print(f"✅ Analysis settings updated: max_n_peaks=8, peak_threshold=1.5, aperiodic_mode='knee'")
        
        # Step 4: Test single channel analysis
        print("\nStep 4: Testing single channel analysis...")
        test_channel = signal_names[0]
        print(f"Testing run_fooof_single() on channel: {test_channel}")
        
        try:
            signal_data = loader.signals_dict[test_channel]['data']
            fs = loader.signals_dict[test_channel]['sample_rate']
            
            result = fooof_analyzer.run_fooof_single(signal_data, fs, test_channel)
            print("✅ Single channel spectral parameterization analysis completed")
            
            # Display results
            print(f"Results for {test_channel}:")
            print(f"  - Aperiodic offset: {result['aperiodic_params'][0]:.3f}")
            print(f"  - Aperiodic exponent: {result['aperiodic_params'][1]:.3f}")
            print(f"  - Number of peaks: {len(result['peak_params'])}")
            print(f"  - R-squared: {result['r_squared']:.3f}")
            print(f"  - Error: {result['error']:.3f}")
            
            if len(result['peak_params']) > 0:
                print("  - Peak frequencies:", [f"{peak[0]:.1f} Hz" for peak in result['peak_params']])
            
        except Exception as e:
            print(f"⚠️  Single channel analysis failed: {e}")
        
        # Step 5: Test band power calculation
        print("\nStep 5: Testing band power calculation...")
        try:
            # Use the PSD from the single channel test
            if 'result' in locals():
                band_powers = fooof_analyzer.get_band_powers(result['freqs'], result['psd'])
                print("✅ Band power calculation completed")
                print("Band powers:")
                for band, power in band_powers.items():
                    print(f"  - {band}: {power:.3f}")
            else:
                print("⏭️  Skipping band power test (no PSD available)")
        except Exception as e:
            print(f"⚠️  Band power calculation failed: {e}")
        
        # Step 6: Test full analysis
        print("\nStep 6: Testing full analysis...")
        print("⚠️  WARNING: analyze_signals() will process all channels and create output files...")
        
        response = input("Do you want to run analyze_signals()? This will create comprehensive spectral parameterization analysis (y/n): ")
        if response.lower() == 'y':
            print("Running analyze_signals()...")
            print("This will create spectral parameterization analysis for all loaded channels...")
            
            try:
                fooof_analyzer.analyze_signals()
                print("✅ analyze_signals() completed successfully!")
                print(f"Check the folder: {loader.folder_path}/{loader.name}/fooof_analysis/ for output files")
                
                # Display summary of results
                if fooof_analyzer.results:
                    print("\nAnalysis Summary:")
                    for channel, result in fooof_analyzer.results.items():
                        print(f"  {channel}:")
                        print(f"    - Aperiodic exponent: {result['aperiodic_params'][1]:.3f}")
                        print(f"    - Number of peaks: {len(result['peak_params'])}")
                        print(f"    - R-squared: {result['r_squared']:.3f}")
                
            except Exception as e:
                print(f"❌ analyze_signals() failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⏭️  Skipping analyze_signals()")
        
        # Step 7: Test comparison plotting (if analysis was run)
        if hasattr(fooof_analyzer, 'results') and fooof_analyzer.results:
            print("\nStep 7: Testing comparison plotting...")
            
            response = input("Do you want to test comparison plots? (y/n): ")
            if response.lower() == 'y':
                try:
                    print("Testing aperiodic exponent comparison...")
                    fooof_analyzer.plot_channel_comparison(metric='aperiodic_exponent')
                    print("✅ Aperiodic exponent comparison completed")
                    
                    print("Testing number of peaks comparison...")
                    fooof_analyzer.plot_channel_comparison(metric='n_peaks')
                    print("✅ Number of peaks comparison completed")
                    
                    print("Testing R-squared comparison...")
                    fooof_analyzer.plot_channel_comparison(metric='r_squared')
                    print("✅ R-squared comparison completed")
                    
                except Exception as e:
                    print(f"⚠️  Comparison plotting failed: {e}")
            else:
                print("⏭️  Skipping comparison plots")
        
        print("\n" + "=" * 60)
        print("FOOOFAnalyzer Testing Complete!")
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
    test_fooof_analyzer()