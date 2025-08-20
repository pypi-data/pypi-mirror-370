"""
Visualization tools for smartdownsample selection patterns.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def plot_bucket_distribution(
    bucket_stats: List[Dict[str, Any]], 
    title: str = "Bucket Distribution: Kept vs Excluded",
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> None:
    """
    Create a bar chart showing bucket distribution with kept/excluded breakdown.
    
    Args:
        bucket_stats: List of bucket statistics from sample_diverse_with_stats()
        title: Chart title
        figsize: Figure size (width, height)
        save_path: Optional path to save the figure
    """
    
    if not bucket_stats:
        print("No bucket statistics available")
        return
    
    # Sort buckets by original size (largest first)
    sorted_buckets = sorted(bucket_stats, key=lambda x: x['original_size'], reverse=True)
    
    bucket_names = [f"Bucket {i+1}\n({b['original_size']} total)" for i, b in enumerate(sorted_buckets)]
    kept_counts = [b['kept'] for b in sorted_buckets]
    excluded_counts = [b['excluded'] for b in sorted_buckets]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    x = np.arange(len(bucket_names))
    width = 0.6
    
    # Create stacked bars
    bars_kept = ax.bar(x, kept_counts, width, label='Kept', color='#2E8B57', alpha=0.8)
    bars_excluded = ax.bar(x, excluded_counts, width, bottom=kept_counts, 
                          label='Excluded', color='#CD5C5C', alpha=0.8)
    
    ax.set_xlabel('Visual Similarity Buckets (sorted by size)')
    ax.set_ylabel('Number of Images')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(bucket_names, rotation=45, ha='right')
    ax.legend()
    
    # Add percentage labels on bars
    for i, (kept, excluded) in enumerate(zip(kept_counts, excluded_counts)):
        total = kept + excluded
        if total > 0:
            kept_pct = (kept / total) * 100
            # Only show percentage if bar is tall enough
            if kept > total * 0.1:
                ax.text(i, kept/2, f'{kept_pct:.0f}%', ha='center', va='center', 
                       fontweight='bold', color='white')
            if excluded > total * 0.1:
                ax.text(i, kept + excluded/2, f'{(100-kept_pct):.0f}%', ha='center', va='center', 
                       fontweight='bold', color='white')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Bucket distribution chart saved to: {save_path}")
    
    plt.show()


def plot_hash_similarity_scatter(
    selection_data: Dict[str, Any],
    title: str = "Image Selection by Visual Similarity",
    save_path: Optional[str] = None,
    show_browser: bool = True
) -> None:
    """
    Create an interactive scatter plot showing image selection patterns in hash space.
    
    Args:
        selection_data: Selection data from sample_diverse_with_stats()
        title: Chart title
        save_path: Optional path to save the HTML file
        show_browser: Whether to open the plot in browser
    """
    
    # Extract data
    all_paths = selection_data['all_paths']
    selected_indices = set(selection_data['selected_indices'])
    hash_arrays = selection_data['hash_arrays']
    bucket_assignments = selection_data['bucket_assignments']
    
    # Use PCA or t-SNE for 2D projection of hash space
    # For now, use first two hash dimensions as a simple projection
    if hash_arrays.size > 0:
        # Flatten hash arrays and take first 2 dimensions for visualization
        x_coords = hash_arrays[:, 0] if hash_arrays.shape[1] > 0 else np.zeros(len(all_paths))
        y_coords = hash_arrays[:, 1] if hash_arrays.shape[1] > 1 else np.random.randn(len(all_paths)) * 0.1
    else:
        x_coords = np.zeros(len(all_paths))
        y_coords = np.zeros(len(all_paths))
    
    # Create selection status and colors
    selection_status = ['Selected' if i in selected_indices else 'Excluded' for i in range(len(all_paths))]
    colors = ['#2E8B57' if status == 'Selected' else '#CD5C5C' for status in selection_status]
    
    # Extract folder names for hover info
    folder_names = [str(Path(path).parent) for path in all_paths]
    file_names = [Path(path).name for path in all_paths]
    
    # Create the scatter plot
    fig = go.Figure()
    
    # Add excluded points first (so selected points appear on top)
    excluded_mask = np.array(selection_status) == 'Excluded'
    if np.any(excluded_mask):
        fig.add_trace(go.Scatter(
            x=x_coords[excluded_mask],
            y=y_coords[excluded_mask],
            mode='markers',
            name='Excluded',
            marker=dict(
                color='#CD5C5C',
                size=6,
                opacity=0.6,
                line=dict(width=0.5, color='DarkSlateGrey')
            ),
            text=[f"{folder_names[i]}<br>{file_names[i]}<br>Bucket: {bucket_assignments[i]}" 
                  for i in range(len(all_paths)) if excluded_mask[i]],
            hovertemplate='<b>%{text}</b><br>Hash X: %{x:.3f}<br>Hash Y: %{y:.3f}<extra></extra>'
        ))
    
    # Add selected points
    selected_mask = np.array(selection_status) == 'Selected'
    if np.any(selected_mask):
        fig.add_trace(go.Scatter(
            x=x_coords[selected_mask],
            y=y_coords[selected_mask],
            mode='markers',
            name='Selected',
            marker=dict(
                color='#2E8B57',
                size=8,
                opacity=0.9,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            text=[f"{folder_names[i]}<br>{file_names[i]}<br>Bucket: {bucket_assignments[i]}" 
                  for i in range(len(all_paths)) if selected_mask[i]],
            hovertemplate='<b>%{text}</b><br>Hash X: %{x:.3f}<br>Hash Y: %{y:.3f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16)
        ),
        xaxis_title="Hash Dimension 1",
        yaxis_title="Hash Dimension 2",
        width=900,
        height=600,
        showlegend=True,
        hovermode='closest',
        plot_bgcolor='rgba(240,240,240,0.8)',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Add summary statistics as annotation
    total_images = len(all_paths)
    selected_count = len(selected_indices)
    selection_rate = (selected_count / total_images) * 100 if total_images > 0 else 0
    
    fig.add_annotation(
        text=f"Selected: {selected_count:,} / {total_images:,} ({selection_rate:.1f}%)",
        xref="paper", yref="paper",
        x=0.99, y=0.01,
        xanchor="right", yanchor="bottom",
        showarrow=False,
        font=dict(size=12),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1
    )
    
    if save_path:
        fig.write_html(save_path)
        print(f"Interactive scatter plot saved to: {save_path}")
    
    if show_browser:
        fig.show()
    
    return fig


def plot_stride_pattern(
    selection_data: Dict[str, Any],
    bucket_id: int = 0,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (15, 8),
    save_path: Optional[str] = None
) -> None:
    """
    Visualize the stride sampling pattern within a specific bucket.
    Shows selected (green) vs excluded (red) images in chronological order.
    
    Args:
        selection_data: Selection data from sample_diverse_with_stats()
        bucket_id: Which bucket to visualize (0 = largest bucket)
        title: Chart title
        figsize: Figure size (width, height)
        save_path: Optional path to save the figure
    """
    
    # Extract data
    all_paths = selection_data['all_paths']
    selected_indices = set(selection_data['selected_indices'])
    bucket_assignments = selection_data['bucket_assignments']
    bucket_stats = selection_data['bucket_stats']
    
    if bucket_id >= len(bucket_stats):
        print(f"Error: bucket_id {bucket_id} not found. Available buckets: 0-{len(bucket_stats)-1}")
        return
    
    # Find all images in the specified bucket
    bucket_images = []
    for i, bucket_assignment in enumerate(bucket_assignments):
        if bucket_assignment == bucket_id:
            bucket_images.append((i, all_paths[i], i in selected_indices))
    
    if not bucket_images:
        print(f"No images found in bucket {bucket_id}")
        return
    
    # Sort by natural path order (same as algorithm does)
    bucket_images.sort(key=lambda x: x[1])  # Sort by path
    
    bucket_size = len(bucket_images)
    bucket_stat = bucket_stats[bucket_id]
    kept_count = bucket_stat['kept']
    
    if title is None:
        title = f"Stride Pattern: Bucket {bucket_id+1} ({kept_count}/{bucket_size} images selected)"
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[3, 1])
    
    # Main timeline plot
    positions = list(range(bucket_size))
    colors = ['#2E8B57' if selected else '#CD5C5C' for _, _, selected in bucket_images]
    
    # Create scatter plot showing selection pattern
    ax1.scatter(positions, [1]*bucket_size, c=colors, s=50, alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # Add stride lines to show the pattern
    selected_positions = [i for i, (_, _, selected) in enumerate(bucket_images) if selected]
    if len(selected_positions) > 1:
        # Draw vertical lines at selected positions
        for pos in selected_positions:
            ax1.axvline(x=pos, color='#2E8B57', alpha=0.3, linestyle='--', linewidth=1)
        
        # Calculate and show stride information
        if len(selected_positions) > 1:
            avg_stride = bucket_size / kept_count
            ax1.text(0.02, 0.95, f'Average stride: {avg_stride:.1f}', 
                    transform=ax1.transAxes, fontsize=12, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    ax1.set_xlim(-bucket_size*0.02, bucket_size*1.02)
    ax1.set_ylim(0.5, 1.5)
    ax1.set_ylabel('Images in Chronological Order', fontsize=12)
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Remove y-axis ticks (not meaningful)
    ax1.set_yticks([])
    
    # Bottom plot: Selection density
    window_size = max(1, bucket_size // 50)  # Adaptive window size
    density_selected = []
    density_positions = []
    
    for i in range(0, bucket_size, window_size):
        window_end = min(i + window_size, bucket_size)
        window_images = bucket_images[i:window_end]
        selected_in_window = sum(1 for _, _, selected in window_images if selected)
        total_in_window = len(window_images)
        density = (selected_in_window / total_in_window) * 100 if total_in_window > 0 else 0
        
        density_selected.append(density)
        density_positions.append(i + window_size // 2)
    
    ax2.bar(density_positions, density_selected, width=window_size*0.8, 
            color='#4CAF50', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax2.set_xlim(-bucket_size*0.02, bucket_size*1.02)
    ax2.set_ylim(0, 100)
    ax2.set_xlabel('Image Position (chronologically sorted)', fontsize=12)
    ax2.set_ylabel('Selection %', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_title(f'Selection Density (window size: {window_size})', fontsize=12)
    
    # Add expected density line
    expected_density = (kept_count / bucket_size) * 100
    ax2.axhline(y=expected_density, color='red', linestyle='--', alpha=0.7, 
                label=f'Expected: {expected_density:.1f}%')
    ax2.legend()
    
    # Add summary statistics
    summary_text = f"""Bucket {bucket_id+1} Summary:
    • Total images: {bucket_size:,}
    • Selected: {kept_count:,} ({(kept_count/bucket_size)*100:.1f}%)
    • Selection ratio: 1 in {bucket_size/kept_count:.1f}"""
    
    fig.text(0.02, 0.02, summary_text, fontsize=10, 
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f0f0", alpha=0.8))
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Stride pattern visualization saved to: {save_path}")
    
    plt.show()


def plot_all_bucket_strides(
    selection_data: Dict[str, Any],
    max_buckets: int = 6,
    figsize: Tuple[int, int] = (16, 10),
    save_path: Optional[str] = None
) -> None:
    """
    Show stride patterns for multiple buckets in a grid layout.
    
    Args:
        selection_data: Selection data from sample_diverse_with_stats()
        max_buckets: Maximum number of buckets to show (largest first)
        figsize: Figure size (width, height)
        save_path: Optional path to save the figure
    """
    
    bucket_stats = selection_data['bucket_stats']
    n_buckets = min(max_buckets, len(bucket_stats))
    
    if n_buckets == 0:
        print("No buckets found in selection data")
        return
    
    # Create subplot grid
    cols = min(3, n_buckets)
    rows = (n_buckets + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    if rows == 1 and cols == 1:
        axes = [axes]
    elif rows == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    all_paths = selection_data['all_paths']
    selected_indices = set(selection_data['selected_indices'])
    bucket_assignments = selection_data['bucket_assignments']
    
    for bucket_id in range(n_buckets):
        ax = axes[bucket_id]
        
        # Find all images in this bucket
        bucket_images = []
        for i, bucket_assignment in enumerate(bucket_assignments):
            if bucket_assignment == bucket_id:
                bucket_images.append((i, all_paths[i], i in selected_indices))
        
        if not bucket_images:
            ax.text(0.5, 0.5, f'Bucket {bucket_id+1}\n(No images)', 
                   ha='center', va='center', transform=ax.transAxes)
            continue
        
        # Sort by natural path order
        bucket_images.sort(key=lambda x: x[1])
        
        bucket_size = len(bucket_images)
        kept_count = bucket_stats[bucket_id]['kept']
        
        # Plot stride pattern
        positions = list(range(bucket_size))
        colors = ['#2E8B57' if selected else '#CD5C5C' for _, _, selected in bucket_images]
        
        ax.scatter(positions, [1]*bucket_size, c=colors, s=20, alpha=0.8)
        
        # Add stride lines
        selected_positions = [i for i, (_, _, selected) in enumerate(bucket_images) if selected]
        if len(selected_positions) > 1:
            for pos in selected_positions[::max(1, len(selected_positions)//10)]:  # Show every 10th line to avoid clutter
                ax.axvline(x=pos, color='#2E8B57', alpha=0.2, linewidth=0.5)
        
        ax.set_title(f'Bucket {bucket_id+1}: {kept_count}/{bucket_size}\n({(kept_count/bucket_size)*100:.0f}% selected)', 
                    fontsize=10, fontweight='bold')
        ax.set_xlim(-bucket_size*0.05, bucket_size*1.05)
        ax.set_ylim(0.5, 1.5)
        ax.set_yticks([])
        ax.grid(True, alpha=0.2)
        
        if bucket_id >= n_buckets - cols:  # Bottom row
            ax.set_xlabel('Image Position', fontsize=9)
    
    # Hide unused subplots
    for i in range(n_buckets, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle('Stride Sampling Patterns Across Buckets\nGreen = Selected, Red = Excluded', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Multi-bucket stride visualization saved to: {save_path}")
    
    plt.show()


def print_bucket_summary(bucket_stats: List[Dict[str, Any]]) -> None:
    """
    Print a text summary of bucket statistics.
    
    Args:
        bucket_stats: List of bucket statistics from sample_diverse_with_stats()
    """
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