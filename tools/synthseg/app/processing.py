"""
NIfTI processing utilities: loading, SynthSeg segmentation, and metadata extraction.
"""
from pathlib import Path
import subprocess

import numpy as np
import nibabel as nib


def load_nifti(path: str) -> nib.Nifti1Image:
    return nib.load(path)


def run_synthseg(input_path: str | Path, output_path: str | Path) -> None:
    """Run SynthSeg and keep only hippocampal labels as a binary mask.

    Output voxels are set to 1 for labels 17 (left hippocampus) and
    53 (right hippocampus), otherwise 0.
    """
    in_path = str(input_path)
    out_path = str(output_path)
    cmd = [
        "mri_synthseg",
        "--i",
        in_path,
        "--o",
        out_path,
        "--threads",
        "4",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or str(exc)).strip()
        raise RuntimeError(details) from exc

    seg_img = nib.load(out_path)
    seg_data = seg_img.get_fdata()
    hippo_mask = np.isin(seg_data, (17, 53)).astype(np.uint8)

    out_header = seg_img.header.copy()
    out_header.set_data_dtype(np.uint8)
    out_img = nib.Nifti1Image(hippo_mask, seg_img.affine, out_header)
    nib.save(out_img, out_path)


def get_data_range(img: nib.Nifti1Image) -> dict:
    """Return min/max intensity and basic shape info."""
    data = img.get_fdata()
    non_zero = data[data != 0]
    return {
        "min": float(data.min()),
        "max": float(data.max()),
        "p2": float(np.percentile(non_zero, 2)) if non_zero.size else 0.0,
        "p98": float(np.percentile(non_zero, 98)) if non_zero.size else 0.0,
        "shape": [int(dim) for dim in img.shape],
        "zooms": [float(zoom) for zoom in img.header.get_zooms()[:3]],
    }
