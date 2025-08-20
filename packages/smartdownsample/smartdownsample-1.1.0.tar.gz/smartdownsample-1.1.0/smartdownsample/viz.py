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