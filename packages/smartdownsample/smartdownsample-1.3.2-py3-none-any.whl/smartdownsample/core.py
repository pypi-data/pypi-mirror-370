"""
Simple, fast image selection that always works.
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Union, Optional, Tuple, Dict, Any
import imagehash
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import warnings
from natsort import natsorted

warnings.filterwarnings('ignore')

# Simple visualization functions integrated into core
def _print_bucket_summary(bucket_stats: List[Dict[str, Any]]) -> None:
    """Print a simple text summary of bucket statistics."""
    if not bucket_stats:
        print("No bucket statistics available")
        return
    
    print("\n" + "="*60)
    print("BUCKET DISTRIBUTION SUMMARY")
    print("="*60)
    
    # Sort by original size
    sorted_buckets = sorted(bucket_stats, key=lambda x: x['original_size'], reverse=True)
    
    total_images = sum(b['original_size'] for b in bucket_stats)
    total_selected = sum(b['kept'] for b in bucket_stats)
    
    print(f"Total images: {total_images:,}")
    print(f"Selected: {total_selected:,} ({(total_selected/total_images)*100:.1f}%)")
    print(f"Visual diversity buckets: {len(bucket_stats)}")
    print()
    
    print("Per-bucket breakdown:")
    print("-" * 60)
    print(f"{'Bucket':<8} {'Size':<8} {'Kept':<8} {'Rate':<8} {'Strategy':<12}")
    print("-" * 60)
    
    for i, bucket in enumerate(sorted_buckets):
        size = bucket['original_size']
        kept = bucket['kept']
        rate = f"{(kept/size)*100:.0f}%" if size > 0 else "0%"
        strategy = "All kept" if kept == size else f"Stride ({bucket.get('stride', '?')})"
        
        print(f"#{i+1:<7} {size:<8,} {kept:<8,} {rate:<8} {strategy:<12}")
    
    print("-" * 60)
    print()


def _plot_bucket_distribution(bucket_stats: List[Dict[str, Any]], viz_data: Dict = None) -> None:
    """Create a horizontal bucket distribution chart with image thumbnails."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        from PIL import Image
    except ImportError:
        print("matplotlib not available - skipping distribution chart")
        return
    
    if not bucket_stats:
        print("No bucket statistics available")
        return
    
    # Sort buckets by original size (largest first)
    sorted_buckets = sorted(bucket_stats, key=lambda x: x['original_size'], reverse=True)
    
    bucket_names = [f"Bucket {i+1}" for i in range(len(sorted_buckets))]
    kept_counts = [b['kept'] for b in sorted_buckets]
    excluded_counts = [b['excluded'] for b in sorted_buckets]
    
    # Create figure with subplots: thumbnails on left, bars on right
    fig = plt.figure(figsize=(16, max(8, len(sorted_buckets) * 0.8)))
    
    # Create grid: thumbnails take 30% width, bars take 70%
    gs = fig.add_gridspec(len(sorted_buckets), 10, hspace=0.3, wspace=0.1)
    
    # Create thumbnail grid function
    def create_thumbnail_grid(bucket_images, max_thumbs=16):
        """Create a grid of thumbnails from bucket images."""
        if not bucket_images or not viz_data:
            return np.ones((60, 60, 3), dtype=np.uint8) * 200  # Gray placeholder
        
        # Limit number of thumbnails
        sample_images = bucket_images[:max_thumbs]
        
        # Calculate grid size
        grid_size = int(np.ceil(np.sqrt(len(sample_images))))
        if grid_size == 0:
            return np.ones((60, 60, 3), dtype=np.uint8) * 200
        
        # Create thumbnail grid
        thumb_size = 60 // grid_size
        grid_img = np.ones((60, 60, 3), dtype=np.uint8) * 240
        
        for idx, img_path in enumerate(sample_images):
            if idx >= grid_size * grid_size:
                break
                
            try:
                # Load and resize image
                with Image.open(img_path) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img_thumb = img.resize((thumb_size, thumb_size), Image.Resampling.LANCZOS)
                    img_array = np.array(img_thumb)
                    
                    # Calculate position in grid
                    row = idx // grid_size
                    col = idx % grid_size
                    y_start = row * thumb_size
                    x_start = col * thumb_size
                    y_end = min(y_start + thumb_size, 60)
                    x_end = min(x_start + thumb_size, 60)
                    
                    # Place thumbnail in grid
                    grid_img[y_start:y_end, x_start:x_end] = img_array[:y_end-y_start, :x_end-x_start]
                    
            except Exception:
                # Skip failed images
                continue
        
        return grid_img
    
    # Process each bucket
    for i, (bucket_idx, bucket_data) in enumerate(enumerate(sorted_buckets)):
        kept = bucket_data['kept']
        excluded = bucket_data['excluded']
        total = kept + excluded
        
        # Get bucket images if viz_data is available
        bucket_images = []
        if viz_data and 'bucket_assignments' in viz_data and 'all_paths' in viz_data:
            bucket_assignments = viz_data['bucket_assignments']
            all_paths = viz_data['all_paths']
            
            # Find images in this bucket (using original bucket order)
            original_bucket_idx = len(sorted_buckets) - 1 - i  # Reverse index since we sorted
            for path_idx, assigned_bucket in enumerate(bucket_assignments):
                if assigned_bucket == original_bucket_idx:
                    bucket_images.append(all_paths[path_idx])
        
        # Create thumbnail subplot (left side)
        thumb_ax = fig.add_subplot(gs[i, :3])
        thumb_grid = create_thumbnail_grid(bucket_images, max_thumbs=16)
        thumb_ax.imshow(thumb_grid)
        thumb_ax.set_title(f'{bucket_names[i]}\n({total} images)', fontsize=10, pad=5)
        thumb_ax.axis('off')
        
        # Create horizontal bar subplot (right side)
        bar_ax = fig.add_subplot(gs[i, 3:])
        
        # Horizontal stacked bar
        y_pos = 0
        bar_height = 0.6
        
        # Plot kept (green) and excluded (red) portions
        if kept > 0:
            bar_ax.barh(y_pos, kept, bar_height, label='Kept' if i == 0 else "", 
                       color='#2E8B57', alpha=0.8)
        if excluded > 0:
            bar_ax.barh(y_pos, excluded, bar_height, left=kept, label='Excluded' if i == 0 else "", 
                       color='#CD5C5C', alpha=0.8)
        
        # Add percentage label
        if total > 0:
            kept_pct = (kept / total) * 100
            bar_ax.text(total / 2, y_pos, f'{kept_pct:.0f}% kept', 
                       ha='center', va='center', fontweight='bold', color='white')
        
        # Format bar subplot
        bar_ax.set_xlim(0, max(kept_counts[0] + excluded_counts[0], 1))
        bar_ax.set_ylim(-0.5, 0.5)
        bar_ax.set_xlabel('Number of Images' if i == len(sorted_buckets) - 1 else '')
        bar_ax.tick_params(left=False, labelleft=False)
        
        # Add grid for easier reading
        bar_ax.grid(axis='x', alpha=0.3)
    
    # Overall title and legend
    fig.suptitle('Bucket Distribution: Visual Similarity Groups with Thumbnails', fontsize=14, y=0.95)
    
    # Create legend
    handles, labels = bar_ax.get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(0.98, 0.93))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.show()




def sample_diverse(
    image_paths: List[Union[str, Path]], 
    target_count: int,
    hash_size: int = 8,
    n_workers: Optional[int] = None,
    show_progress: bool = True,
    random_seed: int = 42,
    show_summary: bool = True,
    show_distribution: bool = False
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
        show_summary: Whether to print bucket distribution summary (default: True)
        show_distribution: Whether to show bucket distribution chart (default: False)
        
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
    
    # Show visualizations if requested
    if show_summary or show_distribution:
        # Create bucket statistics for visualization
        bucket_stats = []
        selected_indices_set = set(selected_indices)
        
        for bucket_idx, (bucket_key, indices) in enumerate(bucket_list):
            bucket_size = len(indices)
            kept = sum(1 for i in indices if i in selected_indices_set)
            excluded = bucket_size - kept
            
            bucket_stats.append({
                'original_size': bucket_size,
                'kept': kept,
                'excluded': excluded,
                'stride': bucket_size // kept if kept > 0 else 0
            })
        
        if show_summary:
            _print_bucket_summary(bucket_stats)
        
        if show_distribution:
            # Create bucket assignment mapping for visualization
            bucket_assignments = [0] * len(valid_paths)
            for bucket_idx, (bucket_key, indices) in enumerate(bucket_list):
                for idx in indices:
                    bucket_assignments[idx] = bucket_idx
            
            # Prepare visualization data
            viz_data = {
                'bucket_assignments': bucket_assignments,
                'all_paths': valid_paths
            }
            
            _plot_bucket_distribution(bucket_stats, viz_data)
    
    return selected_paths


