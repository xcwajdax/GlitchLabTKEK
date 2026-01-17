"""
Glitch effects for Glitch Lab.
"""

import random
import numpy as np
from io import BytesIO

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def effect_rgb_shift(arr, intensity, params=None):
    if params is None:
        params = {}
    max_shift = params.get('max_shift', 15)
    shift_r = random.randint(-int(max_shift * intensity), int(max_shift * intensity))
    shift_b = random.randint(-int(max_shift * intensity), int(max_shift * intensity))
    arr[:, :, 0] = np.roll(arr[:, :, 0], shift_r, axis=1)
    arr[:, :, 2] = np.roll(arr[:, :, 2], shift_b, axis=1)
    return arr


def effect_horizontal_shift(arr, intensity, params=None):
    if params is None:
        params = {}
    height = arr.shape[0]
    num_strips = int(params.get('num_strips', 3) * intensity)
    max_height_pct = params.get('max_height_pct', 0.15)
    max_shift_pct = params.get('max_shift_pct', 0.2)
    for _ in range(num_strips):
        y_start = random.randint(0, height - 1)
        h = random.randint(5, max(6, int(height * max_height_pct * intensity)))
        y_end = min(y_start + h, height)
        shift = random.randint(-int(arr.shape[1] * max_shift_pct * intensity), int(arr.shape[1] * max_shift_pct * intensity))
        arr[y_start:y_end] = np.roll(arr[y_start:y_end], shift, axis=1)
    return arr


def effect_block_displacement(arr, intensity, params=None):
    if params is None:
        params = {}
    height, width = arr.shape[:2]
    num_blocks = int(params.get('num_blocks', 2) * intensity)
    block_h_pct = params.get('block_h_pct', 0.1)
    block_w_pct = params.get('block_w_pct', 0.3)
    for _ in range(num_blocks):
        block_h = random.randint(10, max(11, int(height * block_h_pct * intensity)))
        block_w = random.randint(20, max(21, int(width * block_w_pct * intensity)))
        src_y = random.randint(0, height - block_h)
        src_x = random.randint(0, width - block_w)
        dst_y = random.randint(0, height - block_h)
        dst_x = random.randint(0, width - block_w)
        arr[dst_y:dst_y+block_h, dst_x:dst_x+block_w] = arr[src_y:src_y+block_h, src_x:src_x+block_w].copy()
    return arr


def effect_scanlines(arr, intensity, params=None):
    if params is None:
        params = {}
    height = arr.shape[0]
    num_lines = int(params.get('num_lines', 10) * intensity)
    max_shift = params.get('max_shift', 30)
    for _ in range(num_lines):
        y = random.randint(0, height - 1)
        shift = random.randint(-max_shift, max_shift)
        arr[y] = np.roll(arr[y], shift, axis=0)
    return arr


def effect_color_channel_swap(arr, intensity, params=None):
    if params is None:
        params = {}
    height = arr.shape[0]
    min_height = params.get('min_height', 50)
    y_start = random.randint(0, height // 2)
    y_end = random.randint(y_start + min_height, height)
    swap_type = random.choice(['rgb_to_brg', 'rgb_to_gbr', 'invert_one'])
    if swap_type == 'rgb_to_brg':
        arr[y_start:y_end, :, 0], arr[y_start:y_end, :, 2] = \
            arr[y_start:y_end, :, 2].copy(), arr[y_start:y_end, :, 0].copy()
    elif swap_type == 'rgb_to_gbr':
        temp = arr[y_start:y_end, :, 0].copy()
        arr[y_start:y_end, :, 0] = arr[y_start:y_end, :, 1]
        arr[y_start:y_end, :, 1] = arr[y_start:y_end, :, 2]
        arr[y_start:y_end, :, 2] = temp
    else:
        channel = random.randint(0, 2)
        arr[y_start:y_end, :, channel] = 255 - arr[y_start:y_end, :, channel]
    return arr


def effect_noise_bands(arr, intensity, params=None):
    if params is None:
        params = {}
    height, width = arr.shape[:2]
    num_bands = int(params.get('num_bands', 3) * intensity)
    max_band_height = params.get('max_band_height', 10)
    noise_strength = params.get('noise_strength', 50)
    for _ in range(num_bands):
        y_start = random.randint(0, height - 10)
        h = random.randint(2, max(3, int(max_band_height * intensity)))
        y_end = min(y_start + h, height)
        noise = np.random.randint(0, int(noise_strength * intensity), (y_end - y_start, width, 3), dtype=np.int16)
        arr[y_start:y_end, :, :3] = np.clip(arr[y_start:y_end, :, :3].astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return arr


def effect_vhs_tracking(arr, intensity, params=None):
    if params is None:
        params = {}
    height = arr.shape[0]
    wave_amplitude = int(params.get('wave_amplitude', 10) * intensity)
    wave_freq_min = params.get('wave_freq_min', 0.01)
    wave_freq_max = params.get('wave_freq_max', 0.05)
    wave_freq = random.uniform(wave_freq_min, wave_freq_max)
    for y in range(height):
        shift = int(wave_amplitude * np.sin(y * wave_freq + random.random() * 10))
        arr[y] = np.roll(arr[y], shift, axis=0)
    return arr


def effect_jpeg_artifacts(img, intensity, params=None):
    if params is None:
        params = {}
    base_quality = params.get('base_quality', 30)
    quality_reduction = params.get('quality_reduction', 5)
    quality = max(1, int(base_quality - intensity * quality_reduction))
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    return Image.open(buffer).convert('RGB')