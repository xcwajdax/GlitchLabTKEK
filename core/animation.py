"""
Animation and keyframe system for Glitch Lab.
"""

import math
import random


def interpolate_linear(t, start, end):
    """Interpolacja liniowa."""
    t = max(0.0, min(1.0, t))
    return start + (end - start) * t


def interpolate_ease_in(t, start, end):
    """Interpolacja ease-in (powolny start)."""
    t = max(0.0, min(1.0, t))
    t_eased = t * t
    return start + (end - start) * t_eased


def interpolate_ease_out(t, start, end):
    """Interpolacja ease-out (powolny koniec)."""
    t = max(0.0, min(1.0, t))
    t_eased = 1 - (1 - t) * (1 - t)
    return start + (end - start) * t_eased


def interpolate_ease_in_out(t, start, end):
    """Interpolacja ease-in-out."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        t_eased = 2 * t * t
    else:
        t_eased = 1 - pow(-2 * t + 2, 2) / 2
    return start + (end - start) * t_eased


def interpolate_step(t, start, end):
    """Bezpośrednia zmiana wartości (bez interpolacji)."""
    return end if t >= 1.0 else start


INTERPOLATION_FUNCTIONS = {
    'linear': interpolate_linear,
    'ease_in': interpolate_ease_in,
    'ease_out': interpolate_ease_out,
    'ease_in_out': interpolate_ease_in_out,
    'step': interpolate_step,
}


def calculate_intensity_from_keyframes(frame_idx, total_frames, keyframes, base_intensity):
    """Oblicza intensywność dla danej klatki na podstawie keyframe'ów."""
    if not keyframes:
        return base_intensity
    
    # Sortuj keyframe'y po klatce
    sorted_keyframes = sorted(keyframes, key=lambda k: k['frame'])
    
    # Jeśli klatka jest przed pierwszym keyframe'em
    if frame_idx <= sorted_keyframes[0]['frame']:
        return sorted_keyframes[0]['intensity']
    
    # Jeśli klatka jest po ostatnim keyframe'ie
    if frame_idx >= sorted_keyframes[-1]['frame']:
        return sorted_keyframes[-1]['intensity']
    
    # Znajdź keyframe'y przed i po aktualnej klatce
    for i in range(len(sorted_keyframes) - 1):
        kf_start = sorted_keyframes[i]
        kf_end = sorted_keyframes[i + 1]
        
        if kf_start['frame'] <= frame_idx <= kf_end['frame']:
            # Oblicz t (0.0 - 1.0) między keyframe'ami
            frame_range = kf_end['frame'] - kf_start['frame']
            if frame_range == 0:
                return kf_start['intensity']
            
            t = (frame_idx - kf_start['frame']) / frame_range
            
            # Użyj interpolacji z keyframe'a startowego
            interp_type = kf_start.get('interpolation', 'linear')
            interp_func = INTERPOLATION_FUNCTIONS.get(interp_type, interpolate_linear)
            
            return interp_func(t, kf_start['intensity'], kf_end['intensity'])
    
    return base_intensity


def calculate_glitch_intensity(frame_idx, total_frames, base_intensity, anim_params):
    """Oblicza intensywność glitcha dla danej klatki."""
    pattern_mode = anim_params.get('pattern_mode', 'every')
    
    # Obsługa keyframe'ów
    if pattern_mode == 'keyframes':
        keyframes = anim_params.get('keyframes', [])
        if keyframes:
            intensity = calculate_intensity_from_keyframes(frame_idx, total_frames, keyframes, base_intensity)
            return True, max(0.1, intensity)
        else:
            # Brak keyframe'ów - użyj domyślnej intensywności
            return True, base_intensity
    
    intensity_mode = anim_params.get('intensity_mode', 'constant')
    
    should_glitch = True
    if pattern_mode == 'every':
        should_glitch = True
    elif pattern_mode == 'every_n':
        n = anim_params.get('every_n', 2)
        should_glitch = (frame_idx % n == 0)
    elif pattern_mode == 'random':
        chance = anim_params.get('random_chance', 50) / 100.0
        should_glitch = random.random() < chance
    elif pattern_mode == 'burst':
        on_frames = anim_params.get('burst_on', 3)
        off_frames = anim_params.get('burst_off', 5)
        cycle = on_frames + off_frames
        pos_in_cycle = frame_idx % cycle
        should_glitch = pos_in_cycle < on_frames
    
    if not should_glitch:
        return False, 0
    
    intensity = base_intensity
    progress = frame_idx / max(1, total_frames - 1)
    
    if intensity_mode == 'constant':
        intensity = base_intensity
    elif intensity_mode == 'fade_in':
        intensity = base_intensity * progress
    elif intensity_mode == 'fade_out':
        intensity = base_intensity * (1 - progress)
    elif intensity_mode == 'pulse':
        cycles = anim_params.get('pulse_cycles', 3)
        intensity = base_intensity * (0.3 + 0.7 * abs(math.sin(progress * math.pi * cycles)))
    elif intensity_mode == 'random':
        intensity = base_intensity * random.uniform(0.3, 1.0)
    
    return True, max(0.1, intensity)