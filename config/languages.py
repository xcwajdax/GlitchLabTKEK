"""
Language configuration and translations for Glitch Lab.
"""

# Available languages
AVAILABLE_LANGUAGES = {
    'pl': 'Polski',
    'en': 'English'
}

# Default language
DEFAULT_LANGUAGE = 'pl'

# Translation dictionaries
TRANSLATIONS = {
    'pl': {
        # Application title and version
        'app_title': '⚡ GLITCH LAB v_0.72.34',
        'topkek_productions': 'PRODUCTIONS',
        
        # Main sections
        'input_directory': '📁 Katalog z klatkami:',
        'output_directory': '📂 Katalog wyjściowy:',
        'frame_multiplier': '⚙️ Mnożnik klatek',
        'glitch_section': '💥 Glitch',
        'glitch_animation': '🎬 Animacja Glitcha',
        'effects_section': '🎨 Efekty',
        'progress_section': '📊 Postęp',
        'language_section': '🌐 Język',
        
        # Buttons
        'browse_button': '...',
        'new_output': 'Nowy Output',
        'reimport': 'Reimportuj',
        'generate': '🎬 GENERUJ',
        'refresh': '🔄 Odśwież',
        'preview': '👁️ Podgląd',
        'all_effects': 'Wszystkie',
        'no_effects': 'Żadne',
        'random_effects': 'Losowe',
        'keyframe_button': 'Keyframe',
        'reset_all': '↺ Resetuj wszystko',
        'clear_log': 'Wyczyść log',
        
        # Checkboxes and options
        'enable_multiplier': '✓ Włącz mnożnik klatek',
        'enable_glitch': '✓ Włącz efekty glitch',
        'advanced_mode': '⚙️ Tryb zaawansowany',
        'sync_players': 'Sync',
        
        # Labels
        'multiplier_label': 'Mnożnik:',
        'intensity_label': 'Intensywność:',
        'pattern_label': 'Wzorzec:',
        'intensity_mode_label': 'Tryb intensywności:',
        'language_label': 'Język interfejsu:',
        
        # Pattern options
        'pattern_every': 'every',
        'pattern_every_n': 'every_n',
        'pattern_random': 'random',
        'pattern_burst': 'burst',
        'pattern_keyframes': 'keyframes',
        
        # Intensity mode options
        'intensity_constant': 'constant',
        'intensity_fade_in': 'fade_in',
        'intensity_fade_out': 'fade_out',
        'intensity_pulse': 'pulse',
        'intensity_random': 'random',
        
        # Preview section
        'original_preview': 'Oryginał',
        'result_preview': 'Wynik',
        'common_navigation': 'Wspólna nawigacja klatek',
        'frame_info': 'Klatka: {current}/{total}',
        'frame_info_empty': 'Klatka: -/-',
        
        # Advanced parameters
        'advanced_params_title': '⚙️ PARAMETRY ZAAWANSOWANE',
        'advanced_params_desc': 'Dostosuj parametry aktywnych efektów',
        'no_active_effects': 'Brak aktywnych efektów.\nZaznacz efekty w lewym panelu.',
        
        # Log section
        'log_section': 'Log',
        
        # Status messages
        'status_ready': 'Gotowy',
        'status_processing': 'Przetwarzanie...',
        'status_error': 'Błąd!',
        'status_complete': 'Gotowe! {count} klatek',
        
        # Descriptions
        'multiplier_desc': 'Duplikuje każdą klatkę X razy i numeruje je kolejno.\nNp. mnożnik 2: klatka_01 → klatka_01, klatka_02',
        
        # Dialog messages
        'error_no_pil': 'Brak bibliotek!\n\npip install Pillow numpy',
        'error_no_input': 'Wybierz katalog z klatkami!',
        'error_input_not_exists': 'Katalog wejściowy nie istnieje!',
        'warning_no_output_first': 'Najpierw wybierz katalog wejściowy!',
        'warning_no_output_exists': 'Katalog wyjściowy nie istnieje!',
        'warning_no_images': 'W katalogu wyjściowym nie znaleziono plików obrazów!',
        'warning_no_frames_preview': 'Najpierw załaduj podgląd aby określić liczbę klatek!',
        'success_frames_created': 'Utworzono {count} klatek',
        
        # Log messages
        'log_topkek_opened': 'Otwarto link TOPKEK w przeglądarce',
        'log_topkek_error': 'Nie można otworzyć linku: {error}',
        'log_input_selected': 'Wybrano katalog wejściowy: {path}',
        'log_output_selected': 'Wybrano katalog wyjściowy: {path}',
        'log_output_created': 'Utworzono nowy katalog wyjściowy: {path}',
        'log_output_error': 'Błąd tworzenia katalogu: {error}',
        'log_reimported': 'Reimportowano katalog wyjściowy jako wejściowy: {path}',
        'log_new_output_created': 'Utworzono nowy katalog wyjściowy: {path}',
        'log_new_output_error': 'Błąd tworzenia katalogu wyjściowego: {error}',
        'log_frames_loaded': 'Załadowano {count} klatek do podglądu',
        'log_frames_loaded_original': 'Załadowano {count} klatek do podglądu oryginału',
        'log_previews_refreshed': 'Oryginał: {orig} klatek, Wynik: {result} klatek',
        'log_no_frames': '⚠ Brak załadowanych klatek do podglądu',
        'log_glitch_disabled': 'Glitch wyłączony - pokazuję oryginał',
        'log_no_effects': '⚠ Brak wybranych efektów',
        'log_preview_generated': 'Podgląd klatki {frame} z efektami: {effects}',
        'log_preview_error': '❌ Błąd podglądu: {error}',
        'log_animation_configured': 'Zaawansowana animacja została skonfigurowana',
        'log_animation_cancelled': 'Anulowano edycję animacji',
        'log_all_effects_selected': 'Wybrano wszystkie efekty',
        'log_no_effects_selected': 'Odznaczono wszystkie efekty',
        'log_random_effects_selected': 'Wybrano losowo {count} efektów',
        'log_advanced_enabled': 'Tryb zaawansowany: WŁĄCZONY',
        'log_advanced_disabled': 'Tryb zaawansowany: WYŁĄCZONY',
        'log_params_reset': 'Zresetowano wszystkie parametry zaawansowane do wartości domyślnych',
        'log_refreshing': 'Odświeżanie podglądów...',
        'log_playing_both': 'Odtwarzanie obu podglądów',
        'log_stopped_both': 'Zatrzymano oba podglądy',
        'log_result_loaded': 'Załadowano wynik do podglądu',
        'log_language_changed': 'Zmieniono język na: {language}',
        
        # Processing log messages
        'log_generation_start': 'Rozpoczynam generowanie...',
        'log_input_path': 'Wejście: {path}',
        'log_output_path': 'Wyjście: {path}',
        'log_multiplier_info': 'Mnożnik: {mult}x {status}',
        'log_multiplier_enabled': '(włączony)',
        'log_multiplier_disabled': '(wyłączony)',
        'log_intensity_info': 'Intensywność: {intensity}',
        'log_glitch_status': 'Glitch: {status}',
        'log_glitch_yes': 'TAK',
        'log_glitch_no': 'NIE',
        'log_effects_list': 'Efekty: {effects}',
        'log_pattern_info': 'Wzorzec: {pattern}',
        'log_intensity_mode_info': 'Animacja intensywności: {mode}',
        'log_advanced_mode_info': 'Tryb zaawansowany: WŁĄCZONY',
        'log_progress': 'Postęp: {percent}%',
        'log_completed': 'Zakończono! Utworzono {count} klatek',
        'log_saved_to': 'Zapisano do: {path}',
        'log_error': 'BŁĄD: {error}',
    },
    
    'en': {
        # Application title and version
        'app_title': '⚡ GLITCH LAB v_0.72.34',
        'topkek_productions': 'PRODUCTIONS',
        
        # Main sections
        'input_directory': '📁 Input Directory:',
        'output_directory': '📂 Output Directory:',
        'frame_multiplier': '⚙️ Frame Multiplier',
        'glitch_section': '💥 Glitch',
        'glitch_animation': '🎬 Glitch Animation',
        'effects_section': '🎨 Effects',
        'progress_section': '📊 Progress',
        'language_section': '🌐 Language',
        
        # Buttons
        'browse_button': '...',
        'new_output': 'New Output',
        'reimport': 'Reimport',
        'generate': '🎬 GENERATE',
        'refresh': '🔄 Refresh',
        'preview': '👁️ Preview',
        'all_effects': 'All',
        'no_effects': 'None',
        'random_effects': 'Random',
        'keyframe_button': 'Keyframe',
        'reset_all': '↺ Reset All',
        'clear_log': 'Clear Log',
        
        # Checkboxes and options
        'enable_multiplier': '✓ Enable frame multiplier',
        'enable_glitch': '✓ Enable glitch effects',
        'advanced_mode': '⚙️ Advanced mode',
        'sync_players': 'Sync',
        
        # Labels
        'multiplier_label': 'Multiplier:',
        'intensity_label': 'Intensity:',
        'pattern_label': 'Pattern:',
        'intensity_mode_label': 'Intensity mode:',
        'language_label': 'Interface language:',
        
        # Pattern options
        'pattern_every': 'every',
        'pattern_every_n': 'every_n',
        'pattern_random': 'random',
        'pattern_burst': 'burst',
        'pattern_keyframes': 'keyframes',
        
        # Intensity mode options
        'intensity_constant': 'constant',
        'intensity_fade_in': 'fade_in',
        'intensity_fade_out': 'fade_out',
        'intensity_pulse': 'pulse',
        'intensity_random': 'random',
        
        # Preview section
        'original_preview': 'Original',
        'result_preview': 'Result',
        'common_navigation': 'Common Frame Navigation',
        'frame_info': 'Frame: {current}/{total}',
        'frame_info_empty': 'Frame: -/-',
        
        # Advanced parameters
        'advanced_params_title': '⚙️ ADVANCED PARAMETERS',
        'advanced_params_desc': 'Adjust parameters for active effects',
        'no_active_effects': 'No active effects.\nSelect effects in the left panel.',
        
        # Log section
        'log_section': 'Log',
        
        # Status messages
        'status_ready': 'Ready',
        'status_processing': 'Processing...',
        'status_error': 'Error!',
        'status_complete': 'Done! {count} frames',
        
        # Descriptions
        'multiplier_desc': 'Duplicates each frame X times and numbers them sequentially.\nE.g. multiplier 2: frame_01 → frame_01, frame_02',
        
        # Dialog messages
        'error_no_pil': 'Missing libraries!\n\npip install Pillow numpy',
        'error_no_input': 'Select input directory!',
        'error_input_not_exists': 'Input directory does not exist!',
        'warning_no_output_first': 'First select input directory!',
        'warning_no_output_exists': 'Output directory does not exist!',
        'warning_no_images': 'No image files found in output directory!',
        'warning_no_frames_preview': 'First load preview to determine frame count!',
        'success_frames_created': 'Created {count} frames',
        
        # Log messages
        'log_topkek_opened': 'Opened TOPKEK link in browser',
        'log_topkek_error': 'Cannot open link: {error}',
        'log_input_selected': 'Selected input directory: {path}',
        'log_output_selected': 'Selected output directory: {path}',
        'log_output_created': 'Created new output directory: {path}',
        'log_output_error': 'Error creating directory: {error}',
        'log_reimported': 'Reimported output directory as input: {path}',
        'log_new_output_created': 'Created new output directory: {path}',
        'log_new_output_error': 'Error creating output directory: {error}',
        'log_frames_loaded': 'Loaded {count} frames for preview',
        'log_frames_loaded_original': 'Loaded {count} frames for original preview',
        'log_previews_refreshed': 'Original: {orig} frames, Result: {result} frames',
        'log_no_frames': '⚠ No frames loaded for preview',
        'log_glitch_disabled': 'Glitch disabled - showing original',
        'log_no_effects': '⚠ No effects selected',
        'log_preview_generated': 'Preview of frame {frame} with effects: {effects}',
        'log_preview_error': '❌ Preview error: {error}',
        'log_animation_configured': 'Advanced animation has been configured',
        'log_animation_cancelled': 'Animation editing cancelled',
        'log_all_effects_selected': 'Selected all effects',
        'log_no_effects_selected': 'Deselected all effects',
        'log_random_effects_selected': 'Randomly selected {count} effects',
        'log_advanced_enabled': 'Advanced mode: ENABLED',
        'log_advanced_disabled': 'Advanced mode: DISABLED',
        'log_params_reset': 'Reset all advanced parameters to default values',
        'log_refreshing': 'Refreshing previews...',
        'log_playing_both': 'Playing both previews',
        'log_stopped_both': 'Stopped both previews',
        'log_result_loaded': 'Loaded result for preview',
        'log_language_changed': 'Changed language to: {language}',
        
        # Processing log messages
        'log_generation_start': 'Starting generation...',
        'log_input_path': 'Input: {path}',
        'log_output_path': 'Output: {path}',
        'log_multiplier_info': 'Multiplier: {mult}x {status}',
        'log_multiplier_enabled': '(enabled)',
        'log_multiplier_disabled': '(disabled)',
        'log_intensity_info': 'Intensity: {intensity}',
        'log_glitch_status': 'Glitch: {status}',
        'log_glitch_yes': 'YES',
        'log_glitch_no': 'NO',
        'log_effects_list': 'Effects: {effects}',
        'log_pattern_info': 'Pattern: {pattern}',
        'log_intensity_mode_info': 'Intensity animation: {mode}',
        'log_advanced_mode_info': 'Advanced mode: ENABLED',
        'log_progress': 'Progress: {percent}%',
        'log_completed': 'Completed! Created {count} frames',
        'log_saved_to': 'Saved to: {path}',
        'log_error': 'ERROR: {error}',
    }
}

# Effect names translations
EFFECT_NAMES = {
    'pl': {
        'rgb_shift': 'RGB Shift',
        'h_shift': 'Horizontal Shift',
        'blocks': 'Block Displacement',
        'scanlines': 'Scanlines',
        'color_swap': 'Color Channel Swap',
        'noise': 'Noise Bands',
        'vhs': 'VHS Tracking',
        'jpeg': 'JPEG Artifacts',
    },
    'en': {
        'rgb_shift': 'RGB Shift',
        'h_shift': 'Horizontal Shift',
        'blocks': 'Block Displacement',
        'scanlines': 'Scanlines',
        'color_swap': 'Color Channel Swap',
        'noise': 'Noise Bands',
        'vhs': 'VHS Tracking',
        'jpeg': 'JPEG Artifacts',
    }
}

# Effect parameter labels translations
EFFECT_PARAM_LABELS = {
    'pl': {
        'rgb_shift': {
            'max_shift': 'Maks. przesunięcie',
        },
        'h_shift': {
            'num_strips': 'Liczba pasków',
            'max_height_pct': 'Maks. wysokość (%)',
            'max_shift_pct': 'Maks. przesunięcie (%)',
        },
        'blocks': {
            'num_blocks': 'Liczba bloków',
            'block_h_pct': 'Wysokość bloku (%)',
            'block_w_pct': 'Szerokość bloku (%)',
        },
        'scanlines': {
            'num_lines': 'Liczba linii',
            'max_shift': 'Maks. przesunięcie',
        },
        'color_swap': {
            'min_height': 'Min. wysokość',
        },
        'noise': {
            'num_bands': 'Liczba pasm',
            'max_band_height': 'Maks. wysokość pasma',
            'noise_strength': 'Siła szumu',
        },
        'vhs': {
            'wave_amplitude': 'Amplituda fali',
            'wave_freq_min': 'Min. częstotliwość',
            'wave_freq_max': 'Maks. częstotliwość',
        },
        'jpeg': {
            'base_quality': 'Bazowa jakość',
            'quality_reduction': 'Redukcja jakości',
        },
    },
    'en': {
        'rgb_shift': {
            'max_shift': 'Max. shift',
        },
        'h_shift': {
            'num_strips': 'Number of strips',
            'max_height_pct': 'Max. height (%)',
            'max_shift_pct': 'Max. shift (%)',
        },
        'blocks': {
            'num_blocks': 'Number of blocks',
            'block_h_pct': 'Block height (%)',
            'block_w_pct': 'Block width (%)',
        },
        'scanlines': {
            'num_lines': 'Number of lines',
            'max_shift': 'Max. shift',
        },
        'color_swap': {
            'min_height': 'Min. height',
        },
        'noise': {
            'num_bands': 'Number of bands',
            'max_band_height': 'Max. band height',
            'noise_strength': 'Noise strength',
        },
        'vhs': {
            'wave_amplitude': 'Wave amplitude',
            'wave_freq_min': 'Min. frequency',
            'wave_freq_max': 'Max. frequency',
        },
        'jpeg': {
            'base_quality': 'Base quality',
            'quality_reduction': 'Quality reduction',
        },
    }
}


class LanguageManager:
    """Manages language settings and translations."""
    
    def __init__(self, language=DEFAULT_LANGUAGE):
        self.current_language = language
        self._callbacks = []
    
    def set_language(self, language):
        """Set the current language."""
        if language in AVAILABLE_LANGUAGES:
            self.current_language = language
            # Notify all registered callbacks
            for callback in self._callbacks:
                callback(language)
    
    def get_language(self):
        """Get the current language."""
        return self.current_language
    
    def get_available_languages(self):
        """Get list of available languages."""
        return AVAILABLE_LANGUAGES
    
    def register_callback(self, callback):
        """Register a callback to be called when language changes."""
        self._callbacks.append(callback)
    
    def t(self, key, **kwargs):
        """Translate a key to current language with optional formatting."""
        translation = TRANSLATIONS.get(self.current_language, {}).get(key, key)
        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation
        return translation
    
    def get_effect_name(self, effect_key):
        """Get translated effect name."""
        return EFFECT_NAMES.get(self.current_language, {}).get(effect_key, effect_key)
    
    def get_effect_param_label(self, effect_key, param_key):
        """Get translated effect parameter label."""
        return EFFECT_PARAM_LABELS.get(self.current_language, {}).get(effect_key, {}).get(param_key, param_key)


# Global language manager instance
language_manager = LanguageManager()