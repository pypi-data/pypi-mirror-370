# smartdownsample

**Fast, simple image downsampling that just works**

SmartDownsample samples diverse images from large collections in seconds, not hours. One simple function that works equally fast whether you're sampling 100 or 23,000 images from 24,000.

## Installation

```bash
pip install smartdownsample
```

## Features

- ⚡ **Always fast** - Seconds for any selection ratio
- 🎯 **Smart bucketing** - Better than random, faster than complex algorithms
- 📊 **Scales linearly** - 24k images? No problem
- 🔧 **Dead simple** - One function, always works
- 🎲 **Reproducible** - Set seed for consistent results

## Usage

```python
from smartdownsample import sample_diverse

# Sample 100 diverse images from 24,000 - takes seconds
selected = sample_diverse(
    image_paths=my_24k_images,
    target_count=100
)

# Sample 23,000 images from 24,000 - also takes seconds!
selected = sample_diverse(
    image_paths=my_24k_images,
    target_count=23000
)

# It's that simple.
print(f"Sampled {len(selected)} diverse images")
```

## How It Works

1. **Hash images** - Quick perceptual hashing (4 parallel workers)
2. **Create buckets** - Group similar images together
3. **Sample evenly** - Take images from each bucket for diversity

Result: Better than random selection, without the complexity.

## Performance

| Task | Time |
|------|------|
| 100 from 1,000 | <5 sec |
| 900 from 1,000 | <5 sec |
| 1,000 from 24,000 | ~30 sec |
| 23,000 from 24,000 | ~30 sec |
| Any ratio | Fast ✓ |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `image_paths` | Required | List of image file paths (str or Path objects) |
| `target_count` | Required | Exact number of images to select |
| `n_workers` | `4` | Number of parallel workers (4 is optimal) |
| `hash_size` | `8` | Hash size (8 is fast and good enough) |
| `random_seed` | `42` | Random seed for reproducible results |
| `show_progress` | `True` | Whether to display progress bars |

## Why It's Fast

- **Fixed algorithm** - No switching between methods
- **Simple hashing** - DHash is faster than PHash
- **Smart bucketing** - O(n) grouping instead of O(n²) comparisons
- **Parallel processing** - But capped at 4 workers (diminishing returns above that)

## License

MIT License – see LICENSE file.