from abc import ABC
from typing import Any, Iterable, List

import numpy as np
import pandas as pd

from ..base import BaseMetric
from PIL import Image
from scipy.ndimage import gaussian_filter

class ImageMetric(BaseMetric, ABC):
    """
    Abstract base class for metrics that operate on image data.
    Input can be various image representations (e.g., np.array, image path).
    """

    pass

class ImageSSIM(ImageMetric):
    """
    Structural Similarity Index (SSIM) for perceptual image similarity.

    - Compares local patterns of pixel intensities normalized for luminance/contrast.
    - Computes per-channel SSIM on RGB (or single-channel) and averages across channels.
    - Returns a scalar in [0, 1], where 1.0 indicates perfect structural similarity.
    """

    def __init__(self, resize: bool = True, **kwargs: Any):
        super().__init__(**kwargs)
        self.resize = resize

    @staticmethod
    def _to_ndarray_rgb(x: Any) -> np.ndarray:
        """PIL -> RGB ndarray; passthrough for ndarray."""
        if isinstance(x, Image.Image):
            x = x.convert("RGB")
            x = np.array(x)
        return np.asarray(x)

    @staticmethod
    def _to_u8_if_needed(arr: np.ndarray) -> np.ndarray:
        """
        Ensure uint8 domain for SSIM with L=255.
        - If dtype is uint8, return as-is.
        - If float-like and looks normalized (roughly [0,1]), scale by 255 then cast.
        - Otherwise assume values are already in 0–255 range; just clip and cast.
        """
        arr = np.asarray(arr)
        if arr.dtype == np.uint8:
            return arr

        vmax = float(np.nanmax(arr))
        vmin = float(np.nanmin(arr))
        if vmax <= 1.5 and vmin >= -0.1:  # tolerant of tiny FP noise
            arr = (arr * 255.0)

        return np.clip(np.round(arr), 0, 255).astype(np.uint8)

    def _compute_ssim_grayscale(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        SSIM on a single channel using Gaussian windows (sigma=1.5).
        Assumes inputs are uint8-like; converts to float32 for filtering.
        """
        # Convert to float BEFORE filtering
        x = img1.astype(np.float32)
        y = img2.astype(np.float32)

        # Constants for 8-bit images
        K1, K2 = 0.01, 0.03
        L = 255.0
        C1 = (K1 * L) ** 2
        C2 = (K2 * L) ** 2

        # Local means
        mu1 = gaussian_filter(x, sigma=1.5)
        mu2 = gaussian_filter(y, sigma=1.5)

        mu1_sq = mu1 * mu1
        mu2_sq = mu2 * mu2
        mu1_mu2 = mu1 * mu2

        # Local variances and covariance
        sigma1_sq = gaussian_filter(x * x, sigma=1.5) - mu1_sq
        sigma2_sq = gaussian_filter(y * y, sigma=1.5) - mu2_sq
        sigma12  = gaussian_filter(x * y, sigma=1.5) - mu1_mu2

        # Guard tiny negatives from round-off
        sigma1_sq = np.maximum(sigma1_sq, 0.0)
        sigma2_sq = np.maximum(sigma2_sq, 0.0)

        numerator   = (2 * mu1_mu2 + C1) * (2 * sigma12 + C2)
        denominator = (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
        ssim_map = numerator / (denominator + 1e-8)

        return float(np.mean(ssim_map))

    def _single_calculate(self, generated_item: Any, reference_item: Any, **kwargs: Any) -> float:
        """
        Compute SSIM between a pair of images.
        Handles PIL/ndarray inputs, optional resizing, alpha stripping, and RGB averaging.
        """
        gen = self._to_ndarray_rgb(generated_item)
        ref = self._to_ndarray_rgb(reference_item)

        # If images have >3 channels (e.g., RGBA), drop alpha
        if gen.ndim == 3 and gen.shape[2] > 3:
            gen = gen[..., :3]
        if ref.ndim == 3 and ref.shape[2] > 3:
            ref = ref[..., :3]

        # Harmonize dtype/range for 8-bit SSIM
        gen = self._to_u8_if_needed(gen)
        ref = self._to_u8_if_needed(ref)

        # Resize if shapes differ
        if gen.shape != ref.shape:
            if not self.resize:
                raise ValueError("Input images for ImageSSIM must have the same dimensions.")
            # Ensure uint8 input to PIL for resizing
            ref_img = Image.fromarray(ref)
            gen_img = Image.fromarray(gen).resize(ref_img.size, Image.Resampling.LANCZOS)
            gen = np.array(gen_img)
            ref = np.array(ref_img)

        # Per-channel SSIM (RGB) or single-channel
        if gen.ndim == 3 and gen.shape[2] == 3:
            ssim_val = float(np.mean([
                self._compute_ssim_grayscale(gen[..., c], ref[..., c])
                for c in range(3)
            ]))
        else:
            ssim_val = self._compute_ssim_grayscale(gen.squeeze(), ref.squeeze())

        # Contract to [0,1] as the public contract
        return float(np.clip(ssim_val, 0.0, 1.0))

    def _batch_calculate(self, generated_items: Iterable, reference_items: Iterable, **kwargs: Any) -> List[float]:
        return [self._single_calculate(gen, ref, **kwargs) for gen, ref in zip(generated_items, reference_items)]


# class ImagePSNR(ImageMetric):
#     """
#     Peak Signal-to-Noise Ratio (ImagePSNR) for pixel-level image similarity.

#     ImagePSNR is a simple metric based on the Mean Squared Error (MSE) between two images.
#     It measures the ratio between the maximum possible pixel value and the magnitude 
#     of noise (error). While easy to compute and interpret, ImagePSNR does not account 
#     for perceptual factors and may overestimate similarity in some cases.

#     Output is in decibels (dB), where higher values indicate better quality.
#     """
#     def __init__(self, resize: bool = True, **kwargs: Any):
#         """Initialize ImagePSNR similarity metric with optional resizing."""
#         super().__init__(**kwargs)
#         self.resize = resize

#     def _single_calculate(self, generated_item: Any, reference_item: Any, **kwargs: Any) -> float:
#         """
#         Compute ImagePSNR between a pair of images.
#         Handles resizing, RGB conversion, and normalization.
#         """
#         # Convert to NumPy arrays if inputs are PIL Images
#         if isinstance(generated_item, Image.Image):
#             generated_item = np.array(generated_item.convert("RGB"))
#         if isinstance(reference_item, Image.Image):
#             reference_item = np.array(reference_item.convert("RGB"))

#         # Normalize float inputs to 0-255 uint8
#         if generated_item.dtype != np.uint8:
#             generated_item = (np.clip(generated_item, 0, 1) * 255).astype(np.uint8)
#         if reference_item.dtype != np.uint8:
#             reference_item = (np.clip(reference_item, 0, 1) * 255).astype(np.uint8)

#         # Resize if images differ in shape
#         if generated_item.shape != reference_item.shape:
#             if not self.resize:
#                 raise ValueError("Input images for ImagePSNR must have the same dimensions.")
#             ref_img = Image.fromarray(reference_item)
#             gen_img = Image.fromarray(generated_item).resize(ref_img.size, Image.Resampling.LANCZOS)
#             generated_item = np.array(gen_img)
#             reference_item = np.array(ref_img)

#         # Compute Mean Squared Error (MSE)
#         mse = np.mean((generated_item.astype(np.float32) - reference_item.astype(np.float32)) ** 2)

#         # ImagePSNR formula: 10 * log10(MAX^2 / MSE)
#         if mse == 0:
#             return float("inf")  # Perfect match
#         return float(10 * np.log10((255.0 ** 2) / mse))

#     def _batch_calculate(self, generated_items: Iterable, reference_items: Iterable, **kwargs: Any) -> List[float]:
#         return [self._single_calculate(gen, ref, **kwargs) for gen, ref in zip(generated_items, reference_items)]

class ImageAverageHash(ImageMetric):
    """
    Normalized average hash (aHash) similarity for images.
    This method compares 8x8 grayscale downsampled images and computes
    Hamming similarity of the resulting binary hash. The score is normalized to [0, 1].
    """

    def __init__(self, **kwargs: Any):
        """Initialize the aHash-based image similarity metric."""
        super().__init__(**kwargs)

    def _single_calculate(
        self, generated_item: Any, reference_item: Any, **kwargs: Any
    ) -> float | dict:
        """
        Calculate normalized aHash similarity for a single pair of images.

        :param generated_item: The generated image (e.g., np.array, path).
        :type generated_item: Any
        :param reference_item: The reference image.
        :type reference_item: Any
        :param kwargs: Additional keyword arguments (not used here).
        :return: Normalized aHash similarity score between 0 and 1.
        :rtype: float | dict
        """
        # Convert to PIL image if input is a NumPy array.
        if isinstance(generated_item, np.ndarray):
            generated_item = Image.fromarray(generated_item)
        if isinstance(reference_item, np.ndarray):
            reference_item = Image.fromarray(reference_item)

        # Resize to 8x8 and convert to grayscale.
        gen_resized = generated_item.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
        ref_resized = reference_item.convert("L").resize((8, 8), Image.Resampling.LANCZOS)

        # Compute average pixel values.
        gen_array = np.array(gen_resized, dtype=np.float32)
        ref_array = np.array(ref_resized, dtype=np.float32)
        gen_mean = gen_array.mean()
        ref_mean = ref_array.mean()

        # Compute binary hash: 1 if pixel > mean, else 0.
        gen_hash = (gen_array > gen_mean).astype(np.uint8).flatten()
        ref_hash = (ref_array > ref_mean).astype(np.uint8).flatten()

        # Hamming similarity: proportion of matching bits.
        similarity = 1.0 - np.sum(gen_hash != ref_hash) / len(gen_hash)
        return float(similarity)

    def _batch_calculate(
        self,
        generated_items: Iterable | np.ndarray | pd.Series,
        reference_items: Iterable | np.ndarray | pd.Series,
        **kwargs: Any,
    ) -> List[float] | List[dict] | np.ndarray | pd.Series:
        """
        Calculate normalized aHash similarity for a batch of image pairs.

        :param generated_items: Iterable of generated images.
        :type generated_items: Iterable | np.ndarray | pd.Series
        :param reference_items: Iterable of reference images.
        :type reference_items: Iterable | np.ndarray | pd.Series
        :param kwargs: Additional keyword arguments (not used here).
        :return: List of normalized aHash similarity scores.
        :rtype: List[float] | List[dict] | np.ndarray | pd.Series
        """
        results = []
        for gen, ref in zip(generated_items, reference_items):
            results.append(self._single_calculate(gen, ref, **kwargs))
        return results


class ImageHistogramMatch(ImageMetric):
    """
    Color histogram-based similarity metric for images.
    Computes normalized histogram intersection between RGB histograms of two images.
    The output is a similarity score in the range [0, 1], where 1 means the histograms are identical.
    """

    def __init__(self, **kwargs: Any):
        """Initialize the histogram-based similarity metric."""
        super().__init__(**kwargs)

    def _single_calculate(
        self, generated_item: Any, reference_item: Any, **kwargs: Any
    ) -> float | dict:
        """
        Calculate histogram intersection similarity for a single pair of images.

        :param generated_item: The generated image (e.g., np.array, path).
        :type generated_item: Any
        :param reference_item: The reference image.
        :type reference_item: Any
        :param kwargs: Additional keyword arguments (e.g., number of histogram bins).
        :return: Normalized histogram intersection score in the range [0, 1].
        :rtype: float | dict
        """
        # Convert to PIL image if input is a NumPy array.
        if isinstance(generated_item, np.ndarray):
            generated_item = Image.fromarray(generated_item)
        if isinstance(reference_item, np.ndarray):
            reference_item = Image.fromarray(reference_item)

        # Get number of bins for histogram, default to 256.
        bins = kwargs.get("bins", 256)

        # Convert both images to RGB and extract arrays.
        gen_arr = np.array(generated_item.convert("RGB"))
        ref_arr = np.array(reference_item.convert("RGB"))

        # Compute histogram intersection across R, G, B channels.
        intersection = 0.0
        total = 0.0
        for ch in range(3):  # Iterate over R, G, B.
            gen_hist = np.histogram(gen_arr[:, :, ch], bins=bins, range=(0, 255))[0]
            ref_hist = np.histogram(ref_arr[:, :, ch], bins=bins, range=(0, 255))[0]

            # Sum minimum of each bin across histograms.
            intersection += np.sum(np.minimum(gen_hist, ref_hist))
            total += np.sum(gen_hist)

        # Normalize similarity score to [0, 1].
        similarity = intersection / total if total > 0 else 0.0
        return similarity

    def _batch_calculate(
        self,
        generated_items: Iterable | np.ndarray | pd.Series,
        reference_items: Iterable | np.ndarray | pd.Series,
        **kwargs: Any,
    ) -> List[float] | List[dict] | np.ndarray | pd.Series:
        """
        Calculate histogram intersection similarity for a batch of image pairs.

        :param generated_items: Iterable of generated images.
        :type generated_items: Iterable | np.ndarray | pd.Series
        :param reference_items: Iterable of reference images.
        :type reference_items: Iterable | np.ndarray | pd.Series
        :param kwargs: Additional keyword arguments (e.g., number of histogram bins).
        :return: List of normalized histogram intersection scores for all pairs.
        :rtype: List[float] | List[dict] | np.ndarray | pd.Series
        """
        results = []
        for gen, ref in zip(generated_items, reference_items):
            results.append(self._single_calculate(gen, ref, **kwargs))
        return results



