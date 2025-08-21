#!/usr/bin/env python3
"""
Test script for ConnectivityAnalyzer correlation functionality.
Demonstrates computing correlation matrices from EDF data and visualizing them.
"""
import sys
import os
import matplotlib.pyplot as plt
import pickle
from pathlib import Path

# Make sure our package is on PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.yousif_raiyan_pip_package import EDFLoader, ConnectivityAnalyzer


def save_correlation_matrices_as_images(pickle_path: str, output_folder: str):
    """
    Load a pickle file containing correlation matrices and save each as a PNG.
    
    :param pickle_path: Path to the pickle file containing correlation data
    :param output_folder: Directory where PNG images will be saved
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # Load the pickle file
    with open(pickle_path, "rb") as f:
        data = pickle.load(f)
    
    # Extract matrices and timing info
    if isinstance(data, dict) and "corr_matrices" in data:
        matrices = data["corr_matrices"]
        starts = data.get("starts", list(range(len(matrices))))
    elif isinstance(data, (list, tuple)):
        matrices = data
        starts = list(range(len(matrices)))
    else:
        matrices = [data]
        starts = [0]
    
    # Create visualizations
    for idx, mat in enumerate(matrices):
        fig, ax = plt.subplots(figsize=(8, 6))
        cax = ax.imshow(mat, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
        
        # Add timing info to title if available
        if idx < len(starts):
            ax.set_title(f"Correlation Matrix (t={starts[idx]:.1f}s)")
        else:
            ax.set_title(f"Correlation Matrix {idx}")
            
        ax.set_xlabel("Channel")
        ax.set_ylabel("Channel")
        plt.colorbar(cax, ax=ax, label="Correlation")
        plt.tight_layout()
        
        # Save the plot
        fname = f"corr_{idx:04d}.png"
        path = os.path.join(output_folder, fname)
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)
    
    print(f"✔ Saved {len(matrices)} correlation matrix plots to '{output_folder}'")


def test_correlation_demo():
    """
    Demo script showing correlation matrix computation and visualization.
    """
    print("🧠 EEG Correlation Analysis Demo")
    print("=" * 40)
    
    # Initialize loader and processor
    try:
        loader = EDFLoader(folder_path="data", name="Sebastian")
        print(f"✔ Loaded EDF: {loader.edf_file_path}")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure the EDF file exists at data/Sebastian/Sebastian.edf")
        return
    
    # Create processor with reasonable window size
    proc = ConnectivityAnalyzer(edf_loader=loader, window_size=1000)
    
    # Test 1: Compute correlation matrices for a time segment
    print("\n📊 Computing correlation matrices...")
    try:
        pickle_path = proc.compute_correlation(
            start_time=100.0,      # Start at 100 seconds
            stop_time=140.0,       # End at 140 seconds  
            interval_seconds=1.0   # 1-second windows
        )
        print(f"✔ Correlation data saved to: {pickle_path}")
        
        # Create visualizations
        print("\n🎨 Creating visualization plots...")
        output_folder = "graph_representation/corr_frames"
        save_correlation_matrices_as_images(str(pickle_path), output_folder)
        
        print(f"✔ Correlation plots saved to '{output_folder}'")
        
    except Exception as e:
        print(f"❌ Error during correlation processing: {e}")
        return
    
    # Test 2: Test memory-safe HDF5 graph generation
    print("\n🧠 Testing memory-safe HDF5 graph generation...")
    try:
        hdf5_path = proc.generate_graphs_from_edf(segment_duration_minutes=1.0)
        print(f"✔ HDF5 graph data saved to: {hdf5_path}")
        
        # Test HDF5 file access
        import h5py
        with h5py.File(hdf5_path, 'r') as f:
            n_windows = f['adjacency_matrices'].shape[0]
            n_electrodes = f.attrs['n_electrodes']
            print(f"✔ HDF5 file contains {n_windows} windows with {n_electrodes} electrodes")
        
        print(f"\n🎉 Demo complete! Check outputs in the data directory.")
        
    except Exception as e:
        print(f"❌ Error during HDF5 processing: {e}")
        return


if __name__ == "__main__":
    test_correlation_demo()