# Docker Build Instructions for MirCAT-v2

## Overview

This repository provides two Docker images:

1. **Full CUDA/GPU Integration** (`Dockerfile.cuda`) - Includes all features with GPU acceleration for segmentation
2. **CPU-Only Integration** (`Dockerfile.cpu`) - Lightweight version without segmentation capabilities

## Building the Images

### Full CUDA/GPU Integration

```bash
# Build the image
docker build -f Dockerfile.cuda -t mircat-v2:cuda .

# Run with GPU support
docker run --gpus all -v /path/to/data:/data mircat-v2:cuda segment --help
```

### CPU-Only Integration

```bash
# Build the image
docker build -f Dockerfile.cpu -t mircat-v2:cpu .

# Run without GPU
docker run -v /path/to/data:/data mircat-v2:cpu stats --help
```

## Usage Examples

### CUDA Version - Running Segmentation

```bash
# Segment a single NIfTI file
docker run --gpus all \
  -v /path/to/input:/data/input \
  -v /path/to/output:/data/output \
  mircat-v2:cuda segment \
  --input /data/input/scan.nii.gz \
  --output /data/output \
  --tasks 999 \
  --model-type 3d

# Process multiple files
docker run --gpus all \
  -v /path/to/input:/data/input \
  -v /path/to/output:/data/output \
  mircat-v2:cuda segment \
  --input /data/input/file_list.txt \
  --output /data/output \
  --tasks 999 485 \
  --n-processes 4
```

### CPU Version - Running Statistics

```bash
# Analyze statistics
docker run \
  -v /path/to/data:/data \
  mircat-v2:cpu stats \
  --input /data/scan_with_segs.nii.gz \
  --tasks all \
  --resolution normal

# Convert DICOM to NIfTI
docker run \
  -v /path/to/dicom:/data/input \
  -v /path/to/nifti:/data/output \
  mircat-v2:cpu convert \
  --input /data/input \
  --output /data/output
```

## Volume Mounts

Both images expect data to be mounted at `/data`:

- `/data/input` - Input files (DICOM, NIfTI)
- `/data/output` - Output directory
- `/data/models` - Model weights (CUDA version only)

## Environment Variables

### CUDA Version
- `CUDA_VISIBLE_DEVICES` - Control GPU visibility
- `nnUNet_raw`, `nnUNet_preprocessed`, `nnUNet_results` - nnUNet paths (preset but can be overridden)

### Both Versions
- `PYTHONUNBUFFERED=1` - Real-time logging output

## Notes

1. **CUDA Compatibility**: The CUDA image supports CUDA 12.2+. Ensure your NVIDIA drivers support this version.

2. **Model Files**: The CUDA image includes the nnUNet models from `src/mircat_v2/segmentation/models/`. The CPU image excludes these to save space.

3. **Image Sizes**:
   - CUDA version: ~8-10GB (includes PyTorch, CUDA libraries, and models)
   - CPU version: ~1-2GB (lightweight, no deep learning dependencies)

4. **Performance**:
   - Use `--n-processes` to control multiprocessing
   - CUDA version benefits from GPU acceleration for segmentation
   - CPU version is suitable for DICOM conversion and statistics calculation

5. **Database Operations**: Both images support database operations. Mount a database file:
   ```bash
   docker run -v /path/to/db:/data/db mircat-v2:cpu dbase create --dbase-path /data/db/mircat.db
   ```

## Troubleshooting

### CUDA/GPU Issues
- Ensure NVIDIA Container Toolkit is installed
- Check GPU availability: `docker run --gpus all nvidia/cuda:12.2.2-base-ubuntu22.04 nvidia-smi`
- Verify CUDA version compatibility with your drivers

### Memory Issues
- Increase Docker memory limits for large batch processing
- Use smaller batch sizes with `--cache-size` parameter

### Permission Issues
- Use appropriate user mappings: `--user $(id -u):$(id -g)`
- Ensure mounted volumes have correct permissions