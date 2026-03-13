from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

import numpy as np


def _read_ppm(path: Path) -> np.ndarray:
    with path.open('rb') as f:
        magic = f.readline().strip()
        if magic not in {b'P6', b'P5'}:
            raise ValueError(f'unsupported PPM/PGM format: {magic!r}')

        def next_token() -> bytes:
            while True:
                line = f.readline()
                if not line:
                    raise ValueError('unexpected EOF in header')
                line = line.strip()
                if not line or line.startswith(b'#'):
                    continue
                return line

        dims = next_token().split()
        if len(dims) != 2:
            raise ValueError('invalid image dimensions')
        width, height = map(int, dims)
        maxval = int(next_token())
        if maxval > 255:
            raise ValueError('only 8-bit PPM/PGM supported')
        raw = f.read()
        if magic == b'P6':
            arr = np.frombuffer(raw, dtype=np.uint8).reshape(height, width, 3)
        else:
            gray = np.frombuffer(raw, dtype=np.uint8).reshape(height, width)
            arr = np.stack([gray, gray, gray], axis=-1)
        return arr.astype(np.float32) / 255.0


def read_image_array(path: str | Path) -> np.ndarray:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == '.npy':
        arr = np.load(p)
    elif suffix == '.npz':
        with np.load(p) as data:
            if 'image' in data:
                arr = data['image']
            else:
                key = next(iter(data.keys()))
                arr = data[key]
    elif suffix in {'.ppm', '.pgm'}:
        arr = _read_ppm(p)
    else:
        raise ValueError(f'unsupported image format: {suffix}')
    arr = np.asarray(arr, dtype=np.float32)
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    if arr.max() > 1.0:
        arr = arr / 255.0
    return arr


def write_image_array(path: str | Path, image: np.ndarray) -> None:
    p = Path(path)
    arr = np.asarray(image, dtype=np.float32)
    if p.suffix.lower() == '.npy':
        np.save(p, arr)
        return
    if p.suffix.lower() != '.ppm':
        raise ValueError('write_image_array currently supports .npy and .ppm only')
    arr = np.clip(arr, 0.0, 1.0)
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    h, w, c = arr.shape
    if c != 3:
        raise ValueError('PPM output requires 3 channels')
    data = (arr * 255.0).round().astype(np.uint8)
    with p.open('wb') as f:
        f.write(f'P6\n{w} {h}\n255\n'.encode('ascii'))
        f.write(data.tobytes())


def luminance(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image, dtype=np.float32)
    if image.ndim == 2:
        return image
    return 0.299 * image[..., 0] + 0.587 * image[..., 1] + 0.114 * image[..., 2]


def box_blur(image: np.ndarray, radius: int = 2) -> np.ndarray:
    image = np.asarray(image, dtype=np.float32)
    if radius <= 0:
        return image.copy()
    padded = np.pad(image, [(radius, radius), (radius, radius), (0, 0)], mode='edge')
    out = np.zeros_like(image)
    size = 2 * radius + 1
    area = float(size * size)
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            patch = padded[y:y + size, x:x + size]
            out[y, x] = patch.sum(axis=(0, 1)) / area
    return out


def lowpass(image: np.ndarray, radius: int = 4) -> np.ndarray:
    return box_blur(image, radius=radius)


def edge_magnitude(image: np.ndarray) -> np.ndarray:
    gray = luminance(image)
    gx = np.zeros_like(gray)
    gy = np.zeros_like(gray)
    gx[:, 1:-1] = 0.5 * (gray[:, 2:] - gray[:, :-2])
    gy[1:-1, :] = 0.5 * (gray[2:, :] - gray[:-2, :])
    return np.sqrt(gx * gx + gy * gy)


def radial_frequency_masks(shape: Sequence[int], bands: int = 4) -> List[np.ndarray]:
    h, w = int(shape[0]), int(shape[1])
    fy = np.fft.fftfreq(h)
    fx = np.fft.fftfreq(w)
    yy, xx = np.meshgrid(fy, fx, indexing='ij')
    rr = np.sqrt(xx * xx + yy * yy)
    max_r = rr.max() + 1e-12
    edges = np.linspace(0.0, max_r, bands + 1)
    masks: List[np.ndarray] = []
    for i in range(bands):
        lo, hi = edges[i], edges[i + 1]
        if i == bands - 1:
            mask = (rr >= lo) & (rr <= hi)
        else:
            mask = (rr >= lo) & (rr < hi)
        masks.append(mask.astype(np.float32))
    return masks


def spectral_band_energies(image: np.ndarray, bands: int = 4) -> List[float]:
    image = np.asarray(image, dtype=np.float32)
    if image.ndim == 3:
        gray = luminance(image)
    else:
        gray = image
    fft = np.fft.fft2(gray)
    power = np.abs(fft) ** 2
    masks = radial_frequency_masks(gray.shape, bands=bands)
    energies = []
    total = float(power.sum()) + 1e-12
    for mask in masks:
        energies.append(float((power * mask).sum() / total))
    return energies


def coarse_to_fine_pyramid(image: np.ndarray, levels: int = 4) -> List[np.ndarray]:
    image = np.asarray(image, dtype=np.float32)
    out: List[np.ndarray] = []
    current = image
    for level in range(levels):
        radius = max(levels - level, 1)
        out.append(lowpass(current, radius=radius))
    return out


def segmentation_mask(image: np.ndarray, threshold: float | None = None) -> np.ndarray:
    gray = luminance(image)
    if threshold is None:
        threshold = 0.5
    mask = gray > float(threshold)
    if mask.mean() in {0.0, 1.0}:
        centered = np.abs(gray - gray.mean())
        alt = centered > max(float(centered.std()), 1e-6)
        if 0.0 < alt.mean() < 1.0:
            mask = alt
    return mask.astype(np.float32)


def apply_soft_foreground_blur(image: np.ndarray, mask: np.ndarray, radius: int = 3) -> np.ndarray:
    image = np.asarray(image, dtype=np.float32)
    if mask.ndim == 2:
        mask = mask[..., None]
    blurred = box_blur(image, radius=radius)
    return (1.0 - mask) * image + mask * blurred
