"""
Frame processing functions for Glitch Lab.
"""

import shutil
from pathlib import Path
import numpy as np

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from core.utils import get_frame_info
from core.animation import calculate_glitch_intensity
from core.effects import effect_jpeg_artifacts
from config.effects_registry import EFFECTS


def apply_glitch(file_path, intensity, enabled_effects, effect_params=None):
    """Aplikuje efekty glitch do obrazu."""
    if not PIL_AVAILABLE:
        return False
    if effect_params is None:
        effect_params = {}
    
    img = Image.open(file_path)
    if img.mode == 'RGBA':
        arr = np.array(img)
        has_alpha = True
    else:
        img = img.convert('RGB')
        arr = np.array(img)
        has_alpha = False
    
    if 'jpeg' in enabled_effects:
        params = effect_params.get('jpeg', {})
        if has_alpha:
            rgb_img = Image.fromarray(arr[:, :, :3])
            rgb_img = effect_jpeg_artifacts(rgb_img, intensity, params)
            arr[:, :, :3] = np.array(rgb_img)
        else:
            img = Image.fromarray(arr)
            img = effect_jpeg_artifacts(img, intensity, params)
            arr = np.array(img)
    
    for effect_key in enabled_effects:
        if effect_key == 'jpeg':
            continue
        if effect_key in EFFECTS:
            _, effect_func = EFFECTS[effect_key]
            if effect_func:
                params = effect_params.get(effect_key, {})
                arr = effect_func(arr, intensity, params)
    
    if has_alpha:
        result = Image.fromarray(arr, 'RGBA')
    else:
        result = Image.fromarray(arr)
    result.save(file_path)
    return True


def apply_glitch_to_image(img, intensity, enabled_effects, effect_params=None):
    """Aplikuje efekty glitch do PIL Image (bez zapisu)."""
    if effect_params is None:
        effect_params = {}
    
    if img.mode == 'RGBA':
        arr = np.array(img)
        has_alpha = True
    else:
        img = img.convert('RGB')
        arr = np.array(img)
        has_alpha = False
    
    if 'jpeg' in enabled_effects:
        params = effect_params.get('jpeg', {})
        if has_alpha:
            rgb_img = Image.fromarray(arr[:, :, :3])
            rgb_img = effect_jpeg_artifacts(rgb_img, intensity, params)
            arr[:, :, :3] = np.array(rgb_img)
        else:
            pil_img = Image.fromarray(arr)
            pil_img = effect_jpeg_artifacts(pil_img, intensity, params)
            arr = np.array(pil_img)
    
    for effect_key in enabled_effects:
        if effect_key == 'jpeg':
            continue
        if effect_key in EFFECTS:
            _, effect_func = EFFECTS[effect_key]
            if effect_func:
                params = effect_params.get(effect_key, {})
                arr = effect_func(arr, intensity, params)
    
    if has_alpha:
        return Image.fromarray(arr, 'RGBA')
    return Image.fromarray(arr)


def process_frames(input_dir, output_dir, multiplier, intensity, enabled_effects, 
                   glitch_enabled=True, anim_params=None, effect_params=None, progress_callback=None):
    """Przetwarza klatki z efektami glitch."""
    if anim_params is None:
        anim_params = {'pattern_mode': 'every', 'intensity_mode': 'constant'}
    if effect_params is None:
        effect_params = {}
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if progress_callback:
        progress_callback("Skanowanie plików wejściowych...")
    
    frames = []
    for file in input_path.iterdir():
        if file.is_file():
            frame_num, ext, meta = get_frame_info(file.name)
            if frame_num is not None:
                frames.append((frame_num, ext, meta, file))
    
    if not frames:
        return 0, "Nie znaleziono plików klatek."
    
    frames.sort(key=lambda x: x[0])
    total_input = len(frames)
    total_output = total_input * multiplier
    _, _, (prefix, padding), _ = frames[0]
    
    if progress_callback:
        progress_callback(f"Znaleziono {total_input} klatek, generowanie {total_output} klatek...")
    
    new_frame_num = 0
    output_frame_idx = 0
    
    for i, (frame_num, ext, meta, file_path) in enumerate(frames):
        for j in range(multiplier):
            new_name = f"{prefix}{str(new_frame_num).zfill(padding)}.{ext}"
            dest_path = output_path / new_name
            shutil.copy2(file_path, dest_path)
            
            can_glitch = glitch_enabled and enabled_effects and (j > 0 or multiplier == 1)
            if can_glitch:
                should_glitch, frame_intensity = calculate_glitch_intensity(
                    output_frame_idx, total_output, intensity, anim_params
                )
                if should_glitch and frame_intensity > 0:
                    if progress_callback:
                        progress_callback(f"Przetwarzanie klatki {i + 1}/{total_input}: {file_path.name} → {new_name} (glitch)")
                    apply_glitch(dest_path, frame_intensity, enabled_effects, effect_params)
                else:
                    if progress_callback:
                        progress_callback(f"Przetwarzanie klatki {i + 1}/{total_input}: {file_path.name} → {new_name}")
            else:
                if progress_callback:
                    progress_callback(f"Przetwarzanie klatki {i + 1}/{total_input}: {file_path.name} → {new_name}")
            
            new_frame_num += 1
            output_frame_idx += 1
            
            # Aktualizuj pasek postępu częściej - po każdej wygenerowanej klatce
            if progress_callback:
                current_progress = round(output_frame_idx / total_output * 100)
                progress_callback(current_progress)
        
        # Dodatkowa aktualizacja po zakończeniu przetwarzania każdej klatki wejściowej
        if progress_callback:
            overall_progress = round((i + 1) / total_input * 100)
            # Nie duplikuj aktualizacji jeśli multiplier == 1
            if multiplier == 1:
                pass  # Już zaktualizowane powyżej
            else:
                progress_callback(overall_progress)
    
    return new_frame_num, None