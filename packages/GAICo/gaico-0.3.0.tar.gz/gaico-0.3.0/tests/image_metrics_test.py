import numpy as np
import pytest
from PIL import Image
import warnings
import os

from gaico.metrics.image import ImageSSIM, ImageAverageHash, ImageHistogramMatch

# Dummy image generator.
def generate_test_images(shape=(64, 64, 3)):
    base = np.random.randint(0, 255, size=shape, dtype=np.uint8)
    similar = base.copy()
    noisy = np.clip(base + np.random.randint(-40, 40, size=shape), 0, 255).astype(np.uint8)
    different = np.random.randint(0, 255, size=shape, dtype=np.uint8)
    return base, similar, noisy, different

class TestImageMetrics:

    @pytest.fixture(scope="class")
    def test_images(self):
        return generate_test_images()

    def test_ssim_normalized(self, test_images):
        img1, img2, img3, _ = test_images
        metric = ImageSSIM()
        assert metric._single_calculate(img1, img1) == pytest.approx(1.0)
        score_similar = metric._single_calculate(img2, img1)
        score_noisy = metric._single_calculate(img3, img1)
        assert score_similar >= score_noisy

    def test_average_hash(self, test_images):
        img1, img2, img3, _ = test_images
        metric = ImageAverageHash()
        assert 0 <= metric._single_calculate(img1, img2) <= 1
        assert 0 <= metric._single_calculate(img2, img3) <= 1

    def test_histogram_match(self, test_images):
        img1, img2, img3, _ = test_images
        metric = ImageHistogramMatch()
        score1 = metric._single_calculate(img1, img2)
        score2 = metric._single_calculate(img1, img3)
        assert 0 <= score1 <= 1
        assert 0 <= score2 <= 1
        assert score1 > score2

    def test_batch_consistency(self, test_images):
        img1, img2, img3, _ = test_images
        batch = [img2, img3]
        ref_batch = [img1, img1]
        assert len(ImageSSIM()._batch_calculate(batch, ref_batch)) == 2
        assert len(ImageAverageHash()._batch_calculate(batch, ref_batch)) == 2
        assert len(ImageHistogramMatch()._batch_calculate(batch, ref_batch)) == 2

    def test_mismatched_shapes_handled_by_resize(self):
        img1 = np.random.randint(0, 255, size=(64, 64, 3), dtype=np.uint8)
        img2 = np.random.randint(0, 255, size=(32, 32, 3), dtype=np.uint8)
        # Should not raise error due to auto-resize
        for Metric in [ImageSSIM, ImageAverageHash, ImageHistogramMatch]:
            metric = Metric()
            score = metric._single_calculate(img1, img2)
            assert isinstance(score, float)

    def test_grayscale_input(self):
        img1 = np.random.randint(0, 255, size=(64, 64), dtype=np.uint8)
        img2 = np.random.randint(0, 255, size=(64, 64), dtype=np.uint8)
        for Metric in [ImageSSIM, ImageAverageHash, ImageHistogramMatch]:
            metric = Metric()
            score = metric._single_calculate(img1, img2)
            assert isinstance(score, float)