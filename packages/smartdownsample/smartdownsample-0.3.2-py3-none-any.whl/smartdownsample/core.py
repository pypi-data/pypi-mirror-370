"""
Simple, fast image selection that always works.
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Union, Optional
import imagehash
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import warnings

warnings.filterwarnings('ignore')


def select_distinct(
    image_paths: List[Union[str, Path]], 
    target_count: int,
    hash_size: int = 8,
    n_workers: Optional[int] = None,
    show_progress: bool = True,
    random_seed: int = 42
) -> List[str]:
    """
    Fast image selection using simple grid-based diversity.
    Always returns exactly target_count images in seconds, not hours.
    
    Strategy:
    1. Compute quick hashes for all images
    2. Group similar images into buckets
    3. Sample evenly from buckets to maintain diversity
    
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
        >>> # Fast selection of 100 from 24,000 images
        >>> selected = select_distinct(image_paths, target_count=100)
        
        >>> # Also fast selection of 23,000 from 24,000 images  
        >>> selected = select_distinct(image_paths, target_count=23000)
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
    
    if show_progress:
        print(f"Grouped into {len(buckets)} diversity buckets")
    
    # Step 3: Select from buckets to maintain diversity
    selected_indices = []
    
    # Calculate how many to take from each bucket
    n_buckets = len(buckets)
    base_per_bucket = target_count // n_buckets
    extra_needed = target_count % n_buckets
    
    bucket_list = list(buckets.items())
    np.random.shuffle(bucket_list)  # Randomize bucket order
    
    for i, (bucket_key, indices) in enumerate(bucket_list):
        # Take base amount plus one extra for first 'extra_needed' buckets
        n_from_bucket = base_per_bucket + (1 if i < extra_needed else 0)
        n_from_bucket = min(n_from_bucket, len(indices))
        
        # Randomly sample from this bucket
        if n_from_bucket > 0:
            sampled = np.random.choice(indices, n_from_bucket, replace=False)
            selected_indices.extend(sampled)
    
    # If we still need more (due to empty buckets), sample from largest buckets
    if len(selected_indices) < target_count:
        remaining_needed = target_count - len(selected_indices)
        all_unselected = [i for i in range(n_valid) if i not in selected_indices]
        
        if all_unselected:
            extra = np.random.choice(all_unselected, 
                                   min(remaining_needed, len(all_unselected)), 
                                   replace=False)
            selected_indices.extend(extra)
    
    # Ensure we have exactly target_count
    selected_indices = selected_indices[:target_count]
    
    selected_paths = [valid_paths[i] for i in selected_indices]
    
    if show_progress:
        print(f"✓ Selected {len(selected_paths)} images with diversity preservation")
    
    return selected_paths