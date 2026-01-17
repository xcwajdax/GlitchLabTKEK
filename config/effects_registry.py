"""
Effects registry and default parameters for Glitch Lab.
"""

from core.effects import (
    effect_rgb_shift, effect_horizontal_shift, effect_block_displacement,
    effect_scanlines, effect_color_channel_swap,
    effect_noise_bands, effect_vhs_tracking
)
from config.languages import language_manager

def get_effects():
    """Get effects with translated names."""
    return {
        'rgb_shift': (language_manager.get_effect_name('rgb_shift'), effect_rgb_shift),
        'h_shift': (language_manager.get_effect_name('h_shift'), effect_horizontal_shift),
        'blocks': (language_manager.get_effect_name('blocks'), effect_block_displacement),
        'scanlines': (language_manager.get_effect_name('scanlines'), effect_scanlines),
        'color_swap': (language_manager.get_effect_name('color_swap'), effect_color_channel_swap),
        'noise': (language_manager.get_effect_name('noise'), effect_noise_bands),
        'vhs': (language_manager.get_effect_name('vhs'), effect_vhs_tracking),
        'jpeg': (language_manager.get_effect_name('jpeg'), None),
    }

# For backward compatibility
EFFECTS = get_effects()

# Domyślne parametry dla efektów
def get_default_effect_params():
    """Get default effect parameters with translated labels."""
    return {
        'rgb_shift': {
            'max_shift': {'value': 15, 'min': 1, 'max': 50, 'label': language_manager.get_effect_param_label('rgb_shift', 'max_shift')},
        },
        'h_shift': {
            'num_strips': {'value': 3, 'min': 1, 'max': 10, 'label': language_manager.get_effect_param_label('h_shift', 'num_strips')},
            'max_height_pct': {'value': 0.15, 'min': 0.05, 'max': 0.5, 'label': language_manager.get_effect_param_label('h_shift', 'max_height_pct')},
            'max_shift_pct': {'value': 0.2, 'min': 0.05, 'max': 0.5, 'label': language_manager.get_effect_param_label('h_shift', 'max_shift_pct')},
        },
        'blocks': {
            'num_blocks': {'value': 2, 'min': 1, 'max': 10, 'label': language_manager.get_effect_param_label('blocks', 'num_blocks')},
            'block_h_pct': {'value': 0.1, 'min': 0.05, 'max': 0.3, 'label': language_manager.get_effect_param_label('blocks', 'block_h_pct')},
            'block_w_pct': {'value': 0.3, 'min': 0.1, 'max': 0.8, 'label': language_manager.get_effect_param_label('blocks', 'block_w_pct')},
        },
        'scanlines': {
            'num_lines': {'value': 10, 'min': 1, 'max': 50, 'label': language_manager.get_effect_param_label('scanlines', 'num_lines')},
            'max_shift': {'value': 30, 'min': 5, 'max': 100, 'label': language_manager.get_effect_param_label('scanlines', 'max_shift')},
        },
        'color_swap': {
            'min_height': {'value': 50, 'min': 10, 'max': 200, 'label': language_manager.get_effect_param_label('color_swap', 'min_height')},
        },
        'noise': {
            'num_bands': {'value': 3, 'min': 1, 'max': 20, 'label': language_manager.get_effect_param_label('noise', 'num_bands')},
            'max_band_height': {'value': 10, 'min': 2, 'max': 50, 'label': language_manager.get_effect_param_label('noise', 'max_band_height')},
            'noise_strength': {'value': 50, 'min': 10, 'max': 150, 'label': language_manager.get_effect_param_label('noise', 'noise_strength')},
        },
        'vhs': {
            'wave_amplitude': {'value': 10, 'min': 1, 'max': 50, 'label': language_manager.get_effect_param_label('vhs', 'wave_amplitude')},
            'wave_freq_min': {'value': 0.01, 'min': 0.001, 'max': 0.1, 'label': language_manager.get_effect_param_label('vhs', 'wave_freq_min')},
            'wave_freq_max': {'value': 0.05, 'min': 0.01, 'max': 0.2, 'label': language_manager.get_effect_param_label('vhs', 'wave_freq_max')},
        },
        'jpeg': {
            'base_quality': {'value': 30, 'min': 1, 'max': 50, 'label': language_manager.get_effect_param_label('jpeg', 'base_quality')},
            'quality_reduction': {'value': 5, 'min': 1, 'max': 20, 'label': language_manager.get_effect_param_label('jpeg', 'quality_reduction')},
        },
    }

# For backward compatibility
DEFAULT_EFFECT_PARAMS = get_default_effect_params()