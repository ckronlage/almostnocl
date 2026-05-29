"""
NIfTI processing utilities: loading, thresholding, and metadata extraction.
"""
import numpy as np
import nibabel as nib


def load_nifti(path: str) -> nib.Nifti1Image:
    return nib.load(path)


def apply_threshold(img: nib.Nifti1Image, lower: float, upper: float) -> nib.Nifti1Image:
    """Zero out voxels outside [lower, upper] intensity range."""
    data = np.array(img.dataobj, dtype=np.float32)
    thresholded = np.where((data >= lower) & (data <= upper), data, 0.0)
    return nib.Nifti1Image(thresholded, img.affine, img.header)


def get_data_range(img: nib.Nifti1Image) -> dict:
    """Return min/max intensity and basic shape info."""
    data = np.array(img.dataobj, dtype=np.float32)
    non_zero = data[data != 0]
    return {
        "min": float(data.min()),
        "max": float(data.max()),
        "p2": float(np.percentile(non_zero, 2)) if non_zero.size else 0.0,
        "p98": float(np.percentile(non_zero, 98)) if non_zero.size else 0.0,
        "shape": [int(dim) for dim in img.shape],
        "zooms": [float(zoom) for zoom in img.header.get_zooms()[:3]],
    }
