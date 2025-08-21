#!/usr/bin/env python3
"""
Convert c2_exp txt format to npz format with frame slicing functionality.
"""

import numpy as np
import argparse
import os
import json
from pathlib import Path


def load_c2_exp_txt(filepath):
    """
    Load c2_exp data from txt format and reshape to 3D if needed.
    
    Args:
        filepath (str): Path to the txt file
        
    Returns:
        numpy.ndarray: 3D array with shape (1, time_frames, delay_frames)
    """
    try:
        data = np.loadtxt(filepath)
        print(f"Loaded data with original shape: {data.shape}")
        
        # If 2D, reshape to 3D with first dimension = 1
        if data.ndim == 2:
            data = data.reshape(1, data.shape[0], data.shape[1])
            print(f"Reshaped to 3D: {data.shape}")
        
        return data
    except Exception as e:
        print(f"Error loading file {filepath}: {e}")
        return None


def slice_frames(data, start_frame, end_frame):
    """
    Slice the data from start_frame to end_frame in both time dimensions.
    
    Args:
        data (numpy.ndarray): Input 3D array with shape (1, time_frames, delay_frames)
        start_frame (int): Starting frame index (inclusive)
        end_frame (int): Ending frame index (exclusive)
        
    Returns:
        numpy.ndarray: Sliced data with shape (1, sliced_frames, sliced_frames)
    """
    if data is None:
        return None
    
    if data.ndim == 3:
        # For 3D data: (1, time_frames, delay_frames)
        total_frames_time = data.shape[1]
        total_frames_delay = data.shape[2]
        
        # Validate frame indices for time dimension
        if start_frame < 0:
            start_frame = 0
        if end_frame > total_frames_time:
            end_frame = total_frames_time
        if start_frame >= end_frame:
            raise ValueError(f"Invalid frame range: start_frame ({start_frame}) >= end_frame ({end_frame})")
        
        # Also validate for delay dimension (assuming square matrix behavior)
        delay_start_frame = start_frame
        delay_end_frame = end_frame
        if delay_end_frame > total_frames_delay:
            delay_end_frame = total_frames_delay
        
        print(f"Slicing frames {start_frame} to {end_frame} from (1, {total_frames_time}, {total_frames_delay}) total frames")
        print(f"Output will be (1, {end_frame-start_frame}, {delay_end_frame-delay_start_frame})")
        
        # Slice both time dimensions, keep first dimension
        return data[:, start_frame:end_frame, delay_start_frame:delay_end_frame]
    
    else:
        # Fallback for 2D data
        total_frames_rows = data.shape[0]
        total_frames_cols = data.shape[1]
        
        if start_frame < 0:
            start_frame = 0
        if end_frame > total_frames_rows:
            end_frame = total_frames_rows
        if start_frame >= end_frame:
            raise ValueError(f"Invalid frame range: start_frame ({start_frame}) >= end_frame ({end_frame})")
        
        col_start_frame = start_frame
        col_end_frame = end_frame
        if col_end_frame > total_frames_cols:
            col_end_frame = total_frames_cols
        
        print(f"Slicing frames {start_frame} to {end_frame} from ({total_frames_rows}, {total_frames_cols}) total frames")
        print(f"Output will be ({end_frame-start_frame}, {col_end_frame-col_start_frame})")
        
        return data[start_frame:end_frame, col_start_frame:col_end_frame]


def save_as_npz(data, output_path, start_frame, end_frame, metadata=None):
    """
    Save the data as npz format.
    
    Args:
        data (numpy.ndarray): Data to save
        output_path (str): Output file path
        start_frame (int): Starting frame index
        end_frame (int): Ending frame index
        metadata (dict): Additional metadata to save
    """
    if data is None:
        print("No data to save")
        return
        
    save_dict = {
        'c2_exp': data,
        'start_frame': start_frame,
        'end_frame': end_frame,
        'shape': data.shape
    }
    
    if metadata:
        save_dict.update(metadata)
    
    np.savez_compressed(output_path, **save_dict)
    print(f"Saved data to: {output_path}")
    print(f"Data shape: {data.shape}")
    print(f"Frame range: {start_frame} to {end_frame}")


def load_config(config_path="../my_config.json"):
    """
    Load configuration from JSON file.
    
    Args:
        config_path (str): Path to config file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return None


def get_frame_range_from_config(config):
    """
    Extract start_frame and end_frame from config.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        tuple: (start_frame, end_frame)
    """
    if config is None:
        return None, None
        
    try:
        start_frame = config["analyzer_parameters"]["temporal"]["start_frame"]
        end_frame = config["analyzer_parameters"]["temporal"]["end_frame"]
        print(f"Loaded frame range from config: {start_frame} to {end_frame}")
        return start_frame, end_frame
    except KeyError as e:
        print(f"Error extracting frame range from config: {e}")
        return None, None


def convert_c2_exp_to_npz(input_file, start_frame=None, end_frame=None, output_dir=None, config_path="../my_config.json"):
    """
    Convert c2_exp txt file to npz format with frame slicing.
    
    Args:
        input_file (str): Path to input txt file
        start_frame (int): Starting frame index (if None, load from config)
        end_frame (int): Ending frame index (if None, load from config)
        output_dir (str): Output directory (default: same as input file)
        config_path (str): Path to config file
        
    Returns:
        str: Path to output npz file
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Load frame range from config if not provided
    if start_frame is None or end_frame is None:
        config = load_config(config_path)
        config_start, config_end = get_frame_range_from_config(config)
        
        if start_frame is None:
            start_frame = config_start
        if end_frame is None:
            end_frame = config_end
            
        if start_frame is None or end_frame is None:
            raise ValueError("Could not determine frame range. Please provide start_frame and end_frame or ensure they are in the config file.")
    
    # Load data
    data = load_c2_exp_txt(input_file)
    if data is None:
        return None
    
    # Slice data
    sliced_data = slice_frames(data, start_frame, end_frame)
    
    # Generate output filename
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    output_filename = f"cached_c2_isotropic_frames_{start_frame}_{end_frame}.npz"
    output_path = output_dir / output_filename
    
    # Save as npz
    metadata = {
        'original_file': str(input_path),
        'original_shape': data.shape
    }
    save_as_npz(sliced_data, output_path, start_frame, end_frame, metadata)
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description='Convert c2_exp txt format to npz format with frame slicing')
    parser.add_argument('input_file', help='Input txt file path')
    parser.add_argument('config_or_start_frame', nargs='?', help='Config file path OR starting frame index (if providing frames manually)')
    parser.add_argument('end_frame', type=int, nargs='?', help='Ending frame index (only if second arg is start_frame)')
    parser.add_argument('-o', '--output-dir', help='Output directory (default: same as input file)')
    parser.add_argument('-c', '--config', help='Config file path (alternative to positional config)')
    
    args = parser.parse_args()
    
    # Determine config path and frame parameters
    config_path = '../my_config.json'  # default
    start_frame = None
    end_frame = args.end_frame
    
    if args.config:
        # Config specified with -c flag
        config_path = args.config
    elif args.config_or_start_frame:
        # Check if second argument looks like a config file path or frame number
        if args.config_or_start_frame.endswith('.json') or '/' in args.config_or_start_frame:
            # Looks like a config file path
            config_path = args.config_or_start_frame
        else:
            # Treat as start_frame
            try:
                start_frame = int(args.config_or_start_frame)
            except ValueError:
                print(f"Error: '{args.config_or_start_frame}' is not a valid frame number or config path")
                return 1
    
    try:
        output_path = convert_c2_exp_to_npz(
            args.input_file,
            start_frame,
            end_frame,
            args.output_dir,
            config_path
        )
        
        if output_path:
            print(f"\nConversion completed successfully!")
            print(f"Output file: {output_path}")
        else:
            print("Conversion failed!")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())