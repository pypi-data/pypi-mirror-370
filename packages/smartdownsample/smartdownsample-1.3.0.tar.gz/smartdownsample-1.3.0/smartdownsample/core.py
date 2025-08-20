"""
Simple, fast image selection that always works.
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Union, Optional, Tuple, Dict
import imagehash
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import warnings
from natsort import natsorted

warnings.filterwarnings('ignore')




def sample_diverse(
    image_paths: List[Union[str, Path]], 
    target_count: int,
    hash_size: int = 8,
    n_workers: Optional[int] = None,
    show_progress: bool = True,
    random_seed: int = 42
) -> List[str]:
    """
    Fast diverse sampling from large image collections.
    Preserves maximum diversity by ensuring representation from all visual groups.
    
    Strategy:
    1. Compute quick hashes for all images
    2. Group similar images into buckets (~16 visual groups)
    3. Diversity-first: Sample from every bucket to preserve visual variety, then fill largest buckets
    
    Args:
        image_paths: List of paths to images
        target_count: Exact number of images to return
        hash_size: Size of perceptual hash (8 is fast and good enough)
        n_workers: Number of parallel workers (default: 4)
        show_progress: Whether to show progress bars
        random_seed: Random seed for reproducibility
        
    Returns:
        List of exactly target_count selected image paths
        
    Examples:
        >>> # Fast diverse sampling of 100 from 24,000 images
        >>> selected = sample_diverse(image_paths, target_count=100)
        
        >>> # Also fast for large selections like 23,000 from 24,000 images  
        >>> selected = sample_diverse(image_paths, target_count=23000)
    """
    
    np.random.seed(random_seed)
    
    n_images = len(image_paths)
    
    if target_count >= n_images:
        return [str(p) for p in image_paths]
    
    if target_count <= 0:
        return []
    
    if n_workers is None:
        n_workers = min(4, max(1, 4))  # Default to 4 workers
    
    if show_progress:
        print(f"Selecting {target_count} from {n_images} images using fast grid selection")
    
    # Step 1: Compute hashes in parallel
    if show_progress:
        print("Computing image hashes...")
    
    def compute_hash(path):
        try:
            with Image.open(path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # Use dhash for speed (faster than phash)
                hash_val = imagehash.dhash(img, hash_size=hash_size)
                return str(path), hash_val
        except:
            return str(path), None
    
    valid_paths = []
    hashes = []
    
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(compute_hash, path) for path in image_paths]
        
        if show_progress:
            futures_iter = tqdm(futures, desc="Hashing images")
        else:
            futures_iter = futures
        
        for future in futures_iter:
            path, hash_val = future.result()
            if hash_val is not None:
                valid_paths.append(path)
                hashes.append(hash_val)
    
    n_valid = len(valid_paths)
    
    if target_count >= n_valid:
        return valid_paths
    
    # Step 2: Create diversity grid using hash bits
    if show_progress:
        print("Creating diversity grid...")
    
    # Convert hashes to bit arrays for bucketing
    hash_arrays = np.array([np.array(h.hash).flatten() for h in hashes])
    
    # Use first few bits to create buckets (trade-off between diversity and speed)
    n_bucket_bits = min(4, hash_size)  # Use 4 bits = 16 buckets max
    bucket_keys = []
    
    for h in hash_arrays:
        # Create bucket key from first few bits
        key = tuple(h.flatten()[:n_bucket_bits] > 0)
        bucket_keys.append(key)
    
    # Group images by bucket
    buckets = {}
    for i, key in enumerate(bucket_keys):
        if key not in buckets:
            buckets[key] = []
        buckets[key].append(i)
    
    # Sort indices within each bucket by natural path order
    # This ensures folder structure is preserved during stride sampling
    for key, indices in buckets.items():
        # Create list of (path, index) pairs, sort by path using natsort, extract indices
        path_index_pairs = [(valid_paths[i], i) for i in indices]
        sorted_pairs = natsorted(path_index_pairs, key=lambda x: x[0])
        buckets[key] = [pair[1] for pair in sorted_pairs]
    
    if show_progress:
        print(f"Grouped into {len(buckets)} diversity buckets with natural sorting")
    
    # Step 3: Diversity-preserving selection
    if show_progress:
        print(f"Using diversity-first with proportional distribution across {len(buckets)} buckets")
    
    # Sort buckets by size (largest first)
    bucket_list = [(key, indices) for key, indices in buckets.items()]
    bucket_list.sort(key=lambda x: len(x[1]), reverse=True)
    
    selected_indices = []
    remaining_quota = target_count
    
    # Phase 1: Ensure diversity by taking at least 1 image from each bucket (if quota allows)
    min_per_bucket = max(1, target_count // len(bucket_list))  # At least 1, but more if quota is large
    diversity_quota = min(len(bucket_list) * min_per_bucket, target_count)
    
    # First pass: guarantee diversity by sampling from each bucket
    bucket_taken = []  # Track how many taken from each bucket
    for bucket_key, indices in bucket_list:
        bucket_size = len(indices)
        
        if diversity_quota > 0 and bucket_size > 0:
            # Take min_per_bucket images from each bucket to preserve diversity
            take_count = min(min_per_bucket, bucket_size, diversity_quota)
            if take_count > 0:
                stride = max(1, bucket_size // take_count)
                sampled = indices[::stride][:take_count]
                selected_indices.extend(sampled)
                diversity_quota -= take_count
                remaining_quota -= take_count
                bucket_taken.append(take_count)
            else:
                bucket_taken.append(0)
        else:
            bucket_taken.append(0)
    
    # Phase 2: Distribute remaining quota proportionally across all available buckets
    if remaining_quota > 0:
        # Find all buckets that still have available images
        available_buckets = []
        for i, (bucket_key, indices) in enumerate(bucket_list):
            bucket_size = len(indices)
            already_taken = bucket_taken[i]
            available_in_bucket = bucket_size - already_taken
            if available_in_bucket > 0:
                available_buckets.append((i, available_in_bucket))
        
        if available_buckets:
            # Calculate total available images across all buckets
            total_available = sum(available for _, available in available_buckets)
            
            # Distribute remaining quota proportionally
            for bucket_idx, available_in_bucket in available_buckets:
                if remaining_quota <= 0:
                    break
                
                # Calculate proportional share (but don't exceed what's available in this bucket)
                proportional_share = (available_in_bucket / total_available) * remaining_quota
                take_additional = min(int(proportional_share), available_in_bucket, remaining_quota)
                
                if take_additional > 0:
                    # Sample additional images using stride from remaining images
                    bucket_key, indices = bucket_list[bucket_idx]
                    already_taken = bucket_taken[bucket_idx]
                    remaining_indices = indices[already_taken:]  # Skip already selected
                    stride = max(1, len(remaining_indices) // take_additional)
                    additional_sampled = remaining_indices[::stride][:take_additional]
                    
                    selected_indices.extend(additional_sampled)
                    remaining_quota -= take_additional
            
            # If there's still remaining quota due to rounding, give it to largest available buckets
            while remaining_quota > 0 and available_buckets:
                # Find bucket with most available images
                bucket_idx = max(available_buckets, key=lambda x: x[1])[0]
                bucket_key, indices = bucket_list[bucket_idx]
                already_taken = bucket_taken[bucket_idx]
                available_in_bucket = len(indices) - already_taken
                
                if available_in_bucket > 0:
                    take_additional = min(1, available_in_bucket, remaining_quota)
                    remaining_indices = indices[already_taken:]
                    additional_sampled = remaining_indices[:take_additional]
                    
                    selected_indices.extend(additional_sampled)
                    remaining_quota -= take_additional
                    
                    # Update available count for this bucket
                    available_buckets = [(idx, len(bucket_list[idx][1]) - bucket_taken[idx] - (1 if idx == bucket_idx else 0)) 
                                       for idx, _ in available_buckets 
                                       if len(bucket_list[idx][1]) - bucket_taken[idx] - (1 if idx == bucket_idx else 0) > 0]
                else:
                    break
    
    selected_paths = [valid_paths[i] for i in selected_indices]
    
    if show_progress:
        print(f"✓ Selected {len(selected_paths)} images with diversity preservation")
    
    return selected_paths


def sample_diverse_with_stats(
    image_paths: List[Union[str, Path]], 
    target_count: int,
    hash_size: int = 8,
    n_workers: Optional[int] = None,
    show_progress: bool = True,
    random_seed: int = 42
) -> Tuple[List[str], Dict]:
    """
    Same as sample_diverse but returns additional statistics for visualization.
    
    Returns:
        Tuple of (selected_paths, visualization_data) where visualization_data contains:
        - bucket_stats: List of per-bucket statistics
        - all_paths: All processed image paths
        - selected_indices: Indices of selected images
        - hash_arrays: Hash arrays for scatter plot
        - bucket_assignments: Bucket assignment for each image
    """
    
    np.random.seed(random_seed)
    
    n_images = len(image_paths)
    
    if target_count >= n_images:
        # Return all images with minimal stats
        all_paths = [str(p) for p in image_paths]
        viz_data = {
            'bucket_stats': [{'original_size': n_images, 'kept': n_images, 'excluded': 0, 'stride': 1}],
            'all_paths': all_paths,
            'selected_indices': list(range(n_images)),
            'hash_arrays': np.array([]),
            'bucket_assignments': [0] * n_images
        }
        return all_paths, viz_data
    
    if target_count <= 0:
        viz_data = {
            'bucket_stats': [],
            'all_paths': [],
            'selected_indices': [],
            'hash_arrays': np.array([]),
            'bucket_assignments': []
        }
        return [], viz_data
    
    if n_workers is None:
        n_workers = min(4, max(1, 4))  # Default to 4 workers
    
    if show_progress:
        print(f"Selecting {target_count} from {n_images} images using fast grid selection")
    
    # Step 1: Compute hashes in parallel
    if show_progress:
        print("Computing image hashes...")
    
    def compute_hash(path):
        try:
            with Image.open(path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # Use dhash for speed (faster than phash)
                hash_val = imagehash.dhash(img, hash_size=hash_size)
                return str(path), hash_val
        except:
            return str(path), None
    
    valid_paths = []
    hashes = []
    
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(compute_hash, path) for path in image_paths]
        
        if show_progress:
            futures_iter = tqdm(futures, desc="Hashing images")
        else:
            futures_iter = futures
        
        for future in futures_iter:
            path, hash_val = future.result()
            if hash_val is not None:
                valid_paths.append(path)
                hashes.append(hash_val)
    
    n_valid = len(valid_paths)
    
    if target_count >= n_valid:
        viz_data = {
            'bucket_stats': [{'original_size': n_valid, 'kept': n_valid, 'excluded': 0, 'stride': 1}],
            'all_paths': valid_paths,
            'selected_indices': list(range(n_valid)),
            'hash_arrays': np.array([np.array(h.hash).flatten() for h in hashes]),
            'bucket_assignments': [0] * n_valid
        }
        return valid_paths, viz_data
    
    # Step 2: Create diversity grid using hash bits
    if show_progress:
        print("Creating diversity grid...")
    
    # Convert hashes to bit arrays for bucketing
    hash_arrays = np.array([np.array(h.hash).flatten() for h in hashes])
    
    # Use first few bits to create buckets (trade-off between diversity and speed)
    n_bucket_bits = min(4, hash_size)  # Use 4 bits = 16 buckets max
    bucket_keys = []
    
    for h in hash_arrays:
        # Create bucket key from first few bits
        key = tuple(h.flatten()[:n_bucket_bits] > 0)
        bucket_keys.append(key)
    
    # Group images by bucket
    buckets = {}
    for i, key in enumerate(bucket_keys):
        if key not in buckets:
            buckets[key] = []
        buckets[key].append(i)
    
    # Sort indices within each bucket by natural path order
    # This ensures folder structure is preserved during stride sampling
    for key, indices in buckets.items():
        # Create list of (path, index) pairs, sort by path using natsort, extract indices
        path_index_pairs = [(valid_paths[i], i) for i in indices]
        sorted_pairs = natsorted(path_index_pairs, key=lambda x: x[0])
        buckets[key] = [pair[1] for pair in sorted_pairs]
    
    if show_progress:
        print(f"Grouped into {len(buckets)} diversity buckets with natural sorting")
    
    # Step 3: Trim from top with stride sampling
    if show_progress:
        print(f"Using diversity-first with proportional distribution across {len(buckets)} buckets")
    
    # Sort buckets by size (largest first)
    bucket_list = [(key, indices) for key, indices in buckets.items()]
    bucket_list.sort(key=lambda x: len(x[1]), reverse=True)
    
    selected_indices = []
    remaining_quota = target_count
    bucket_stats = []
    
    # Create bucket assignment mapping
    bucket_assignments = [0] * len(valid_paths)
    for bucket_idx, (bucket_key, indices) in enumerate(bucket_list):
        for idx in indices:
            bucket_assignments[idx] = bucket_idx
    
    # Phase 1: Ensure diversity by taking at least 1 image from each bucket (if quota allows)
    min_per_bucket = max(1, target_count // len(bucket_list))  # At least 1, but more if quota is large
    diversity_quota = min(len(bucket_list) * min_per_bucket, target_count)
    
    # First pass: guarantee diversity by sampling from each bucket
    for bucket_idx, (bucket_key, indices) in enumerate(bucket_list):
        bucket_size = len(indices)
        
        if diversity_quota > 0 and bucket_size > 0:
            # Take min_per_bucket images from each bucket to preserve diversity
            take_count = min(min_per_bucket, bucket_size, diversity_quota)
            if take_count > 0:
                stride = max(1, bucket_size // take_count)
                sampled = indices[::stride][:take_count]
                selected_indices.extend(sampled)
                diversity_quota -= take_count
                remaining_quota -= take_count
                
                bucket_stats.append({
                    'original_size': bucket_size,
                    'kept': take_count,
                    'excluded': bucket_size - take_count,
                    'stride': stride,
                    'phase': 'diversity'
                })
            else:
                bucket_stats.append({
                    'original_size': bucket_size,
                    'kept': 0,
                    'excluded': bucket_size,
                    'stride': 0,
                    'phase': 'diversity'
                })
        else:
            bucket_stats.append({
                'original_size': bucket_size,
                'kept': 0,
                'excluded': bucket_size,
                'stride': 0,
                'phase': 'diversity'
            })
    
    # Phase 2: Distribute remaining quota proportionally across all available buckets
    if remaining_quota > 0:
        # Find all buckets that still have available images
        available_buckets = []
        for bucket_idx, (bucket_key, indices) in enumerate(bucket_list):
            bucket_size = len(indices)
            already_taken = bucket_stats[bucket_idx]['kept']
            available_in_bucket = bucket_size - already_taken
            if available_in_bucket > 0:
                available_buckets.append((bucket_idx, available_in_bucket))
        
        if available_buckets:
            # Calculate total available images across all buckets
            total_available = sum(available for _, available in available_buckets)
            
            # Distribute remaining quota proportionally
            for bucket_idx, available_in_bucket in available_buckets:
                if remaining_quota <= 0:
                    break
                
                # Calculate proportional share (but don't exceed what's available in this bucket)
                proportional_share = (available_in_bucket / total_available) * remaining_quota
                take_additional = min(int(proportional_share), available_in_bucket, remaining_quota)
                
                if take_additional > 0:
                    # Sample additional images using stride from remaining images
                    bucket_key, indices = bucket_list[bucket_idx]
                    already_taken = bucket_stats[bucket_idx]['kept']
                    remaining_indices = indices[already_taken:]  # Skip already selected
                    stride = max(1, len(remaining_indices) // take_additional)
                    additional_sampled = remaining_indices[::stride][:take_additional]
                    
                    selected_indices.extend(additional_sampled)
                    remaining_quota -= take_additional
                    
                    # Update bucket stats
                    bucket_stats[bucket_idx]['kept'] += take_additional
                    bucket_stats[bucket_idx]['excluded'] -= take_additional
                    bucket_stats[bucket_idx]['phase'] = 'diversity+proportional'
        
        # If there's still remaining quota due to rounding, give it to largest available buckets
        while remaining_quota > 0 and available_buckets:
            # Find bucket with most available images
            bucket_idx = max(available_buckets, key=lambda x: x[1])[0]
            bucket_key, indices = bucket_list[bucket_idx]
            already_taken = bucket_stats[bucket_idx]['kept']
            available_in_bucket = len(indices) - already_taken
            
            if available_in_bucket > 0:
                take_additional = min(1, available_in_bucket, remaining_quota)
                remaining_indices = indices[already_taken:]
                additional_sampled = remaining_indices[:take_additional]
                
                selected_indices.extend(additional_sampled)
                remaining_quota -= take_additional
                
                bucket_stats[bucket_idx]['kept'] += take_additional
                bucket_stats[bucket_idx]['excluded'] -= take_additional
                bucket_stats[bucket_idx]['phase'] = 'diversity+proportional+rounding'
                
                # Update available count for this bucket
                available_buckets = [(idx, len(bucket_list[idx][1]) - bucket_stats[idx]['kept']) 
                                   for idx, _ in available_buckets 
                                   if len(bucket_list[idx][1]) - bucket_stats[idx]['kept'] > 0]
            else:
                break
    
    selected_paths = [valid_paths[i] for i in selected_indices]
    
    if show_progress:
        print(f"✓ Selected {len(selected_paths)} images with diversity preservation")
    
    # Prepare visualization data
    viz_data = {
        'bucket_stats': bucket_stats,
        'all_paths': valid_paths,
        'selected_indices': selected_indices,
        'hash_arrays': hash_arrays,
        'bucket_assignments': bucket_assignments
    }
    
    return selected_paths, viz_data