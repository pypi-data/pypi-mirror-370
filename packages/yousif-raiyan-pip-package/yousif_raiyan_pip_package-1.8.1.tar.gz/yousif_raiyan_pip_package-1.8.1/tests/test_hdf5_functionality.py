#!/usr/bin/env python3
"""
Test script for new HDF5 functionality in ConnectivityAnalyzer.
Verifies that the memory-safe graph generation works correctly.
"""
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Make sure our package is on PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_hdf5_imports():
    """Test that all required dependencies can be imported."""
    print("Testing imports...")
    
    try:
        import h5py
        print("✔ h5py imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import h5py: {e}")
        return False
    
    try:
        import tqdm
        print("✔ tqdm imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import tqdm: {e}")
        return False
    
    try:
        from src.yousif_raiyan_pip_package import ConnectivityAnalyzer, EDFLoader
        print("✔ ConnectivityAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ConnectivityAnalyzer: {e}")
        return False
    
    return True

def test_hdf5_method_exists():
    """Test that the generate_graphs_from_edf method exists and has correct signature."""
    print("\nTesting method signature...")
    
    try:
        from src.yousif_raiyan_pip_package import ConnectivityAnalyzer
        
        # Check if method exists
        if not hasattr(ConnectivityAnalyzer, 'generate_graphs_from_edf'):
            print("❌ generate_graphs_from_edf method not found")
            return False
        
        # Check method signature
        import inspect
        sig = inspect.signature(ConnectivityAnalyzer.generate_graphs_from_edf)
        params = list(sig.parameters.keys())
        
        if 'segment_duration_minutes' not in params:
            print("❌ segment_duration_minutes parameter not found")
            return False
        
        print("✔ Method signature is correct")
        return True
        
    except Exception as e:
        print(f"❌ Error checking method: {e}")
        return False

def test_hdf5_with_mock_data():
    """Test HDF5 functionality with mock data if available."""
    print("\nTesting with mock data...")
    
    # Check if test data exists
    test_data_path = Path("data/Sebastian/Sebastian.edf")
    if not test_data_path.exists():
        print("⚠ No test data found - skipping functional test")
        print("  (This is normal if you don't have test EDF files)")
        return True
    
    try:
        from src.yousif_raiyan_pip_package import ConnectivityAnalyzer, EDFLoader
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize loader and processor
            loader = EDFLoader(folder_path="data", name="Sebastian")
            processor = ConnectivityAnalyzer(
                edf_loader=loader,
                output_dir=temp_dir,
                window_step_ratio=1.0  # No overlap for faster testing
            )
            
            # Test the HDF5 method with very small segment
            print("  → Testing HDF5 graph generation...")
            hdf5_path = processor.generate_graphs_from_edf(segment_duration_minutes=0.5)
            
            # Verify HDF5 file was created
            if not Path(hdf5_path).exists():
                print("❌ HDF5 file was not created")
                return False
            
            # Test HDF5 file structure
            import h5py
            with h5py.File(hdf5_path, 'r') as f:
                required_datasets = ['adjacency_matrices', 'node_features', 'edge_features', 'window_starts']
                for dataset in required_datasets:
                    if dataset not in f:
                        print(f"❌ Required dataset '{dataset}' not found in HDF5 file")
                        return False
                
                # Check metadata
                required_attrs = ['sampling_frequency', 'n_electrodes', 'total_windows_processed']
                for attr in required_attrs:
                    if attr not in f.attrs:
                        print(f"❌ Required attribute '{attr}' not found in HDF5 file")
                        return False
                
                print(f"✔ HDF5 file created successfully with {f.attrs['total_windows_processed']} windows")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during functional test: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing HDF5 Functionality")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_hdf5_imports),
        ("Method Signature Test", test_hdf5_method_exists),
        ("Functional Test", test_hdf5_with_mock_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    for i, (test_name, _) in enumerate(tests):
        status = "✔ PASS" if results[i] else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results)
    print(f"\nOverall: {'✔ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())