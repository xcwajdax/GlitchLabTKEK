"""
Glitch Lab - Eksperymentalne efekty glitch na klatkach animacji.
Z podglądem animacji oryginału i wyniku.
"""

import os
import shutil
import re
import random
import math
import json
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import modularnych komponentów
from core.utils import get_frame_info
from core.processing import process_frames, apply_glitch_to_image
from core.animation import calculate_glitch_intensity
from config.effects_registry import get_effects, get_default_effect_params
from config.languages import language_manager
from gui.theme import NeonTheme
from gui.preview import PreviewPlayer
from gui.animation_editor import AnimationEditorWindow


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Glitch Lab")
        self.root.geometry("1400x800")
        self.root.state('zoomed')  # Otwórz zmaksymalizowane
        self.root.resizable(True, True)
        
        # Aplikuj ciemny motyw
        self.theme = NeonTheme.apply(root)
        
        # Register language change callback
        language_manager.register_callback(self.on_language_changed)
        
        # Główny kontener
        main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Lewy panel - ustawienia podstawowe
        left_frame = ttk.Frame(main_paned, width=380)
        main_paned.add(left_frame, weight=0)
        
        # Środkowy panel - parametry zaawansowane (początkowo ukryty)
        self.middle_frame = ttk.Frame(main_paned, width=350)
        
        # Prawy panel - podglądy
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        self.main_paned = main_paned
        self.middle_panel_visible = False
        
        # Zmienne stanu widoczności zawartości paneli
        self.multiplier_content_visible = False
        self.glitch_content_visible = False
        self.anim_visible = False
        self.effects_visible = False
        
        # Store references to UI elements that need translation updates
        self.ui_elements = {}
        
        self.setup_left_panel(left_frame)
        self.setup_middle_panel(self.middle_frame)
        self.setup_right_panel(right_frame)
    
    def on_pattern_change(self, event):
        """Handle pattern selection change."""
        for widget in self.pattern_params_frame.winfo_children():
            widget.pack_forget()
        mode = self.pattern_var.get()
        if mode == 'every_n':
            self.every_n_frame.pack()
        elif mode == 'random':
            self.random_frame.pack()
        elif mode == 'burst':
            self.burst_frame.pack()
        elif mode == 'keyframes':
            # Tryb keyframes - ukryj parametry wzorca
            pass
        
        # Zarządzaj aktywnością suwaka intensywności i trybu intensywności
        if mode == 'keyframes':
            # Deaktywuj suwak i combobox intensywności
            self.intensity_scale.config(state='disabled')
            self.intensity_mode_combo.config(state='disabled')
            # Aktywuj przycisk Keyframe
            self.keyframe_button.config(state='normal')
        else:
            # Aktywuj suwak i combobox intensywności
            self.intensity_scale.config(state='normal')
            self.intensity_mode_combo.config(state='readonly')
            # Deaktywuj przycisk Keyframe
            self.keyframe_button.config(state='disabled')
    
    def on_intensity_mode_change(self, event):
        """Handle intensity mode selection change."""
        for widget in self.intensity_params_frame.winfo_children():
            widget.pack_forget()
        if self.intensity_mode_var.get() == 'pulse':
            self.pulse_frame.pack()
    
    def on_multiplier_enabled_change(self):
        """Aktualizuje stan spinboxa mnożnika w zależności od checkboxa."""
        if self.multiplier_enabled_var.get():
            self.multiplier_spinbox.config(state='normal')
            # Pokaż zawartość mnożnika
            if not self.multiplier_content_visible:
                self.show_content(self.multiplier_content_frame, 'multiplier')
        else:
            self.multiplier_spinbox.config(state='disabled')
            # Ukryj zawartość mnożnika
            if self.multiplier_content_visible:
                self.hide_content(self.multiplier_content_frame, 'multiplier')
    
    def on_glitch_enabled_change(self):
        """Obsługuje włączanie/wyłączanie sekcji glitcha, animacji i efektów."""
        if self.glitch_enabled_var.get():
            # Pokaż zawartość glitcha
            if not self.glitch_content_visible:
                self.show_content(self.glitch_content_frame, 'glitch')
            # Pokaż całą sekcję animacji
            if not self.anim_visible:
                self.show_frame(self.anim_frame, 'anim')
            # Pokaż całą sekcję efektów
            if not self.effects_visible:
                self.show_frame(self.effects_frame, 'effects')
        else:
            # Ukryj zawartość glitcha
            if self.glitch_content_visible:
                self.hide_content(self.glitch_content_frame, 'glitch')
            # Ukryj całą sekcję animacji
            if self.anim_visible:
                self.hide_frame(self.anim_frame, 'anim')
            # Ukryj całą sekcję efektów
            if self.effects_visible:
                self.hide_frame(self.effects_frame, 'effects')
    
    def show_content(self, frame, content_type):
        """Pokazuje zawartość sekcji."""
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        if content_type == 'multiplier':
            self.multiplier_content_visible = True
        elif content_type == 'glitch':
            self.glitch_content_visible = True
    
    def hide_content(self, frame, content_type):
        """Ukrywa zawartość sekcji."""
        frame.pack_forget()
        if content_type == 'multiplier':
            self.multiplier_content_visible = False
        elif content_type == 'glitch':
            self.glitch_content_visible = False
    
    def show_frame(self, frame, frame_type):
        """Pokazuje całą ramkę sekcji."""
        # Znajdź pasek postępu jako punkt odniesienia
        progress_frame = None
        for child in frame.master.winfo_children():
            if isinstance(child, ttk.LabelFrame) and hasattr(self, 'ui_elements') and 'progress_frame' in self.ui_elements:
                if child == self.ui_elements['progress_frame']:
                    progress_frame = child
                    break
        
        # Pakuj przed paskiem postępu aby zachować właściwą kolejność
        if progress_frame:
            frame.pack(fill=tk.X, pady=(0, 10), before=progress_frame)
        else:
            frame.pack(fill=tk.X, pady=(0, 10))
            
        if frame_type == 'anim':
            self.anim_visible = True
        elif frame_type == 'effects':
            self.effects_visible = True
    
    def hide_frame(self, frame, frame_type):
        """Ukrywa całą ramkę sekcji."""
        frame.pack_forget()
        if frame_type == 'anim':
            self.anim_visible = False
        elif frame_type == 'effects':
            self.effects_visible = False
    
    def on_effect_toggle(self):
        """Callback wywoływany gdy zmienia się stan efektu - aktualizuje panel zaawansowany."""
        if hasattr(self, 'advanced_mode_var') and self.advanced_mode_var.get():
            self.update_advanced_params_display()
    
    def open_topkek_link(self, event):
        """Otwiera link TOPKEK w przeglądarce."""
        try:
            webbrowser.open("https://xcwajdax.github.io/topkek")
            self.log(language_manager.t('log_topkek_opened'))
        except Exception as e:
            self.log(language_manager.t('log_topkek_error', error=str(e)))
    
    def setup_left_panel(self, parent):
        """Konfiguruje lewy panel z ustawieniami."""
        # Scrollable canvas z ciemnym tłem
        canvas = tk.Canvas(parent, highlightthickness=0, bg=NeonTheme.BG_DARK)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Obsługa scrollowania myszką
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        main_frame = ttk.Frame(scrollable_frame, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł sekcji z wersją i linkiem
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(anchor=tk.W, pady=(0, 15), fill=tk.X)
        
        # Główny tytuł z wersją
        self.ui_elements['title_label'] = ttk.Label(title_frame, text=language_manager.t('app_title'), style='Title.TLabel')
        self.ui_elements['title_label'].pack(anchor=tk.W)
        
        # Ramka dla TOPKEK wyrównana do prawej
        topkek_frame = ttk.Frame(title_frame)
        topkek_frame.pack(anchor=tk.E, pady=(2, 0))
        
        # Link TOPKEK - IMPACT z mniejszą czcionką bez pogrubienia
        topkek_label = tk.Label(topkek_frame, text="T O P K E K", 
                               font=('Impact', 14, 'normal'),
                               fg=NeonTheme.NEON_BLUE, bg=NeonTheme.BG_DARK,
                               cursor='hand2')
        topkek_label.pack(anchor=tk.E)
        topkek_label.bind("<Button-1>", self.open_topkek_link)
        
        # PRODUCTIONS - cienka czcionka
        self.ui_elements['productions_label'] = tk.Label(topkek_frame, text=language_manager.t('topkek_productions'),
                                   font=('Segoe UI', 8, 'normal'),
                                   fg=NeonTheme.TEXT_SECONDARY, bg=NeonTheme.BG_DARK)
        self.ui_elements['productions_label'].pack(anchor=tk.E)
        
        # Sekcja wyboru języka - dodana na początku
        language_frame = ttk.LabelFrame(main_frame, padding=10)
        self.ui_elements['language_frame'] = language_frame
        language_frame.pack(fill=tk.X, pady=(0, 10))
        
        lang_row = ttk.Frame(language_frame)
        lang_row.pack(fill=tk.X, pady=3)
        self.ui_elements['language_label'] = ttk.Label(lang_row, text=language_manager.t('language_label'))
        self.ui_elements['language_label'].pack(side=tk.LEFT)
        
        self.language_var = tk.StringVar(value=language_manager.get_language())
        self.language_combo = ttk.Combobox(lang_row, textvariable=self.language_var, width=12, state='readonly')
        available_langs = language_manager.get_available_languages()
        self.language_combo['values'] = list(available_langs.values())
        self.language_combo.pack(side=tk.LEFT, padx=8)
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Katalog wejściowy
        self.ui_elements['input_label'] = ttk.Label(main_frame, text=language_manager.t('input_directory'), style='Accent.TLabel')
        self.ui_elements['input_label'].pack(anchor=tk.W)
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(2, 10))
        
        self.input_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_var, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ui_elements['input_browse_btn'] = ttk.Button(input_frame, text=language_manager.t('browse_button'), width=4, command=self.browse_input)
        self.ui_elements['input_browse_btn'].pack(side=tk.RIGHT, padx=(8, 0))
        
        # Katalog wyjściowy
        self.ui_elements['output_label'] = ttk.Label(main_frame, text=language_manager.t('output_directory'), style='Accent.TLabel')
        self.ui_elements['output_label'].pack(anchor=tk.W)
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(2, 10))
        
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ui_elements['output_browse_btn'] = ttk.Button(output_frame, text=language_manager.t('browse_button'), width=4, command=self.browse_output)
        self.ui_elements['output_browse_btn'].pack(side=tk.RIGHT, padx=(8, 0))
        
        # Przyciski pod katalogiem wyjściowym
        output_buttons_frame = ttk.Frame(main_frame)
        output_buttons_frame.pack(fill=tk.X, pady=(2, 10))
        self.ui_elements['new_output_btn'] = ttk.Button(output_buttons_frame, text=language_manager.t('new_output'), command=self.create_new_output)
        self.ui_elements['new_output_btn'].pack(side=tk.LEFT, padx=(0, 8))
        self.ui_elements['reimport_btn'] = ttk.Button(output_buttons_frame, text=language_manager.t('reimport'), command=self.reimport_output)
        self.ui_elements['reimport_btn'].pack(side=tk.LEFT)
        
        # Ustawienia podstawowe - mnożnik klatek
        settings_frame = ttk.LabelFrame(main_frame, padding=10)
        self.ui_elements['multiplier_frame'] = settings_frame
        settings_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Checkbox do włączania mnożnika
        self.multiplier_enabled_var = tk.BooleanVar(value=False)
        self.ui_elements['multiplier_checkbox'] = ttk.Checkbutton(settings_frame, 
                       variable=self.multiplier_enabled_var,
                       command=self.on_multiplier_enabled_change)
        self.ui_elements['multiplier_checkbox'].pack(anchor=tk.W, pady=(0, 5))
        
        # Zawartość mnożnika - początkowo ukryta
        self.multiplier_content_frame = ttk.Frame(settings_frame)
        # Nie pakujemy na początku - zostanie spakowana przez animację
        
        row1 = ttk.Frame(self.multiplier_content_frame)
        row1.pack(fill=tk.X, pady=3)
        self.ui_elements['multiplier_label'] = ttk.Label(row1, text=language_manager.t('multiplier_label'))
        self.ui_elements['multiplier_label'].pack(side=tk.LEFT)
        self.multiplier_var = tk.IntVar(value=2)
        self.multiplier_spinbox = ttk.Spinbox(row1, from_=1, to=10, width=5, textvariable=self.multiplier_var, state='disabled')
        self.multiplier_spinbox.pack(side=tk.LEFT, padx=8)
        
        # Opis mnożnika
        self.ui_elements['multiplier_desc'] = ttk.Label(self.multiplier_content_frame, text=language_manager.t('multiplier_desc'), 
                 style='Card.TLabel', foreground='#a0a0a0')
        self.ui_elements['multiplier_desc'].pack(anchor=tk.W, pady=(5, 0))
        
        # Ustawienia glitcha - osobna ramka
        glitch_frame = ttk.LabelFrame(main_frame, padding=10)
        self.ui_elements['glitch_frame'] = glitch_frame
        glitch_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.glitch_enabled_var = tk.BooleanVar(value=True)
        self.ui_elements['glitch_checkbox'] = ttk.Checkbutton(glitch_frame, 
                       variable=self.glitch_enabled_var,
                       command=self.on_glitch_enabled_change)
        self.ui_elements['glitch_checkbox'].pack(anchor=tk.W)
        
        # Zawartość glitcha - początkowo ukryta (teraz pusta, animacja przeniesiona na zewnątrz)
        self.glitch_content_frame = ttk.Frame(glitch_frame)
        # Nie pakujemy na początku - zostanie spakowana przez animację
        
        # Animacja glitcha - osobna sekcja na tym samym poziomie co efekty
        self.anim_frame = ttk.LabelFrame(main_frame, padding=10)
        self.ui_elements['anim_frame'] = self.anim_frame
        # Nie pakujemy na początku - zostanie spakowana przez on_glitch_enabled_change
        
        # Suwak intensywności (przeniesiony z sekcji Glitch)
        intensity_row = ttk.Frame(self.anim_frame)
        intensity_row.pack(fill=tk.X, pady=(0, 10))
        self.ui_elements['intensity_label'] = ttk.Label(intensity_row, text=language_manager.t('intensity_label'))
        self.ui_elements['intensity_label'].pack(side=tk.LEFT)
        self.intensity_var = tk.DoubleVar(value=2.0)
        self.intensity_scale = ttk.Scale(intensity_row, from_=0.5, to=5.0, variable=self.intensity_var, 
                  orient=tk.HORIZONTAL, length=150)
        self.intensity_scale.pack(side=tk.LEFT, padx=8)
        self.intensity_label = ttk.Label(intensity_row, text="2.0", style='Accent.TLabel')
        self.intensity_label.pack(side=tk.LEFT)
        
        # Aktualizuj label przy zmianie slidera
        def update_intensity_label(*args):
            self.intensity_label.config(text=f"{self.intensity_var.get():.1f}")
        self.intensity_var.trace_add('write', update_intensity_label)
        
        # Wzorzec
        pattern_row = ttk.Frame(self.anim_frame)
        pattern_row.pack(fill=tk.X, pady=3)
        self.ui_elements['pattern_label'] = ttk.Label(pattern_row, text=language_manager.t('pattern_label'))
        self.ui_elements['pattern_label'].pack(side=tk.LEFT)
        self.pattern_var = tk.StringVar(value='every')
        pattern_combo = ttk.Combobox(pattern_row, textvariable=self.pattern_var, width=12, state='readonly')
        pattern_combo['values'] = ('every', 'every_n', 'random', 'burst', 'keyframes')
        pattern_combo.pack(side=tk.LEFT, padx=8)
        pattern_combo.bind('<<ComboboxSelected>>', self.on_pattern_change)
        
        self.pattern_params_frame = ttk.Frame(pattern_row)
        self.pattern_params_frame.pack(side=tk.LEFT, padx=5)
        
        self.every_n_frame = ttk.Frame(self.pattern_params_frame)
        ttk.Label(self.every_n_frame, text="Co:").pack(side=tk.LEFT)
        self.every_n_var = tk.IntVar(value=2)
        ttk.Spinbox(self.every_n_frame, from_=2, to=20, width=4, textvariable=self.every_n_var).pack(side=tk.LEFT, padx=3)
        
        self.random_frame = ttk.Frame(self.pattern_params_frame)
        self.random_chance_var = tk.IntVar(value=50)
        ttk.Spinbox(self.random_frame, from_=1, to=100, width=4, textvariable=self.random_chance_var).pack(side=tk.LEFT)
        ttk.Label(self.random_frame, text="%").pack(side=tk.LEFT, padx=3)
        
        self.burst_frame = ttk.Frame(self.pattern_params_frame)
        ttk.Label(self.burst_frame, text="On:").pack(side=tk.LEFT)
        self.burst_on_var = tk.IntVar(value=3)
        ttk.Spinbox(self.burst_frame, from_=1, to=20, width=3, textvariable=self.burst_on_var).pack(side=tk.LEFT, padx=2)
        ttk.Label(self.burst_frame, text="Off:").pack(side=tk.LEFT, padx=(5, 0))
        self.burst_off_var = tk.IntVar(value=5)
        ttk.Spinbox(self.burst_frame, from_=1, to=20, width=3, textvariable=self.burst_off_var).pack(side=tk.LEFT, padx=2)
        
        # Intensywność animowana
        int_row = ttk.Frame(self.anim_frame)
        int_row.pack(fill=tk.X, pady=(0, 3))
        self.ui_elements['intensity_mode_label'] = ttk.Label(int_row, text=language_manager.t('intensity_mode_label'))
        self.ui_elements['intensity_mode_label'].pack(side=tk.LEFT)
        self.intensity_mode_var = tk.StringVar(value='constant')
        self.intensity_mode_combo = ttk.Combobox(int_row, textvariable=self.intensity_mode_var, width=12, state='readonly')
        self.intensity_mode_combo['values'] = ('constant', 'fade_in', 'fade_out', 'pulse', 'random')
        self.intensity_mode_combo.pack(side=tk.LEFT, padx=8)
        self.intensity_mode_combo.bind('<<ComboboxSelected>>', self.on_intensity_mode_change)
        
        self.intensity_params_frame = ttk.Frame(int_row)
        self.intensity_params_frame.pack(side=tk.LEFT, padx=5)
        
        self.pulse_frame = ttk.Frame(self.intensity_params_frame)
        ttk.Label(self.pulse_frame, text="Cykle:").pack(side=tk.LEFT)
        self.pulse_cycles_var = tk.IntVar(value=3)
        ttk.Spinbox(self.pulse_frame, from_=1, to=10, width=3, textvariable=self.pulse_cycles_var).pack(side=tk.LEFT, padx=3)
        
        # Przycisk keyframe'ów
        advanced_anim_row = ttk.Frame(self.anim_frame)
        advanced_anim_row.pack(fill=tk.X, pady=(10, 0))
        self.keyframe_button = ttk.Button(advanced_anim_row, text=language_manager.t('keyframe_button'), 
                  command=self.open_animation_editor, style='Accent.TButton', state='disabled')
        self.ui_elements['keyframe_button'] = self.keyframe_button
        self.keyframe_button.pack()
        
        # Przechowywanie keyframe'ów
        self.animation_keyframes = None
        
        # Efekty
        self.effects_frame = ttk.LabelFrame(main_frame, padding=10)
        self.ui_elements['effects_frame'] = self.effects_frame
        # Nie pakujemy na początku - zostanie spakowana przez on_glitch_enabled_change
        
        # Checkbox główny do włączania efektów - usunięty, teraz kontrolowany przez glitch_enabled_var
        
        self.effect_vars = {}
        effects_grid = ttk.Frame(self.effects_frame)
        effects_grid.pack(fill=tk.X)
        
        # Get current effects with translations
        current_effects = get_effects()
        
        row, col = 0, 0
        for key, (name, _) in current_effects.items():
            var = tk.BooleanVar(value=key in ['rgb_shift', 'h_shift', 'blocks'])
            self.effect_vars[key] = var
            # Dodaj callback do aktualizacji panelu zaawansowanego
            var.trace_add('write', lambda *args: self.on_effect_toggle())
            ttk.Checkbutton(effects_grid, text=name, variable=var).grid(row=row, column=col, sticky=tk.W, pady=2)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        quick_frame = ttk.Frame(self.effects_frame)
        quick_frame.pack(pady=(10, 0))
        self.ui_elements['all_effects_btn'] = ttk.Button(quick_frame, text=language_manager.t('all_effects'), command=self.select_all)
        self.ui_elements['all_effects_btn'].pack(side=tk.LEFT, padx=3)
        self.ui_elements['no_effects_btn'] = ttk.Button(quick_frame, text=language_manager.t('no_effects'), command=self.select_none)
        self.ui_elements['no_effects_btn'].pack(side=tk.LEFT, padx=3)
        self.ui_elements['random_effects_btn'] = ttk.Button(quick_frame, text=language_manager.t('random_effects'), command=self.select_random)
        self.ui_elements['random_effects_btn'].pack(side=tk.LEFT, padx=3)
        
        # Przycisk trybu zaawansowanego
        advanced_frame = ttk.Frame(self.effects_frame)
        advanced_frame.pack(pady=(10, 0))
        
        self.advanced_mode_var = tk.BooleanVar(value=False)
        self.ui_elements['advanced_checkbox'] = ttk.Checkbutton(advanced_frame, text=language_manager.t('advanced_mode'), 
                       variable=self.advanced_mode_var,
                       command=self.toggle_advanced_mode)
        self.ui_elements['advanced_checkbox'].pack()
        
        # Przechowywanie parametrów zaawansowanych
        self.effect_params = {}
        
        self.on_pattern_change(None)
        self.on_intensity_mode_change(None)
        self.on_multiplier_enabled_change()
        # Pokaż zawartość glitcha i efektów na początku (domyślnie włączone)
        self.on_glitch_enabled_change()
        
        # Pasek postępu - tworzony po sekcjach, żeby był pod nimi
        progress_frame = ttk.LabelFrame(main_frame, padding=10)
        self.ui_elements['progress_frame'] = progress_frame
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        self.status_var = tk.StringVar(value=language_manager.t('status_ready'))
        ttk.Label(progress_frame, textvariable=self.status_var, style='Accent.TLabel').pack()
        
        # Przyciski akcji - na samym spodzie
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(5, 10))
        
        self.start_btn = ttk.Button(btn_frame, text=language_manager.t('generate'), style='Accent.TButton', command=self.start_process)
        self.ui_elements['start_btn'] = self.start_btn
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.ui_elements['refresh_btn'] = ttk.Button(btn_frame, text=language_manager.t('refresh'), command=self.refresh_previews)
        self.ui_elements['refresh_btn'].pack(side=tk.LEFT, padx=5)
        
        self.ui_elements['preview_btn'] = ttk.Button(btn_frame, text=language_manager.t('preview'), command=self.preview_current_frame)
        self.ui_elements['preview_btn'].pack(side=tk.LEFT, padx=5)
    
    def setup_middle_panel(self, parent):
        """Konfiguruje środkowy panel z zaawansowanymi parametrami efektów."""
        # Scrollable canvas
        canvas = tk.Canvas(parent, highlightthickness=0, bg=NeonTheme.BG_DARK)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Obsługa scrollowania myszką
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.middle_scrollable_frame = scrollable_frame
        self.middle_canvas = canvas
        
        main_frame = ttk.Frame(scrollable_frame, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        self.ui_elements['advanced_title'] = ttk.Label(main_frame, text=language_manager.t('advanced_params_title'), 
                  style='Title.TLabel')
        self.ui_elements['advanced_title'].pack(anchor=tk.W, pady=(0, 10))
        
        self.ui_elements['advanced_desc'] = ttk.Label(main_frame, text=language_manager.t('advanced_params_desc'), 
                 font=('Segoe UI', 8), foreground='#a0a0a0')
        self.ui_elements['advanced_desc'].pack(anchor=tk.W, pady=(0, 10))
        
        # Przycisk resetowania wszystkiego
        self.ui_elements['reset_all_btn'] = ttk.Button(main_frame, text=language_manager.t('reset_all'), 
                  command=self.reset_all_params)
        self.ui_elements['reset_all_btn'].pack(anchor=tk.W, pady=(0, 10))
        
        # Kontener na efekty - będzie dynamicznie aktualizowany
        self.effects_container = ttk.Frame(main_frame)
        self.effects_container.pack(fill=tk.BOTH, expand=True)
        
        # Słownik do przechowywania zmiennych i ramek
        self.param_vars = {}
        self.effect_frames = {}
        
        # Inicjalne wypełnienie
        self.update_advanced_params_display()
    
    def update_advanced_params_display(self):
        """Aktualizuje wyświetlanie parametrów zaawansowanych - pokazuje tylko aktywne efekty."""
        # Usuń wszystkie istniejące ramki
        for widget in self.effects_container.winfo_children():
            widget.destroy()
        
        self.effect_frames = {}
        
        # Pobierz aktywne efekty
        enabled_effects = self.get_enabled_effects()
        
        if not enabled_effects:
            # Pokaż komunikat gdy brak aktywnych efektów
            msg_label = ttk.Label(self.effects_container, 
                    text=language_manager.t('no_active_effects'),
                    font=('Segoe UI', 9),
                    foreground='#a0a0a0')
            msg_label.pack(pady=20)
            return
        
        # Dla każdego aktywnego efektu stwórz sekcję
        for effect_key in enabled_effects:
            current_params = get_default_effect_params()
            if effect_key not in current_params:
                continue
            
            current_effects = get_effects()
            effect_name = current_effects[effect_key][0]
            
            # Ramka dla efektu
            effect_frame = ttk.LabelFrame(self.effects_container, text=f"🎨 {effect_name}", padding=8)
            effect_frame.pack(fill=tk.X, pady=(0, 8))
            
            self.effect_frames[effect_key] = effect_frame
            
            if effect_key not in self.param_vars:
                self.param_vars[effect_key] = {}
            
            # Dla każdego parametru efektu
            for param_name, param_info in current_params[effect_key].items():
                param_frame = ttk.Frame(effect_frame)
                param_frame.pack(fill=tk.X, pady=2)
                
                # Label
                label_text = param_info['label']
                ttk.Label(param_frame, text=label_text, width=20, 
                        foreground=NeonTheme.TEXT_SECONDARY, 
                        font=('Segoe UI', 8), anchor=tk.W).pack(side=tk.TOP, anchor=tk.W)
                
                control_frame = ttk.Frame(param_frame)
                control_frame.pack(fill=tk.X)
                
                # Pobierz aktualną wartość lub domyślną
                current_value = self.effect_params.get(effect_key, {}).get(param_name, param_info['value'])
                
                # Zmienna - użyj istniejącej lub stwórz nową
                if param_name not in self.param_vars[effect_key]:
                    if isinstance(param_info['value'], float):
                        var = tk.DoubleVar(value=current_value)
                    else:
                        var = tk.IntVar(value=current_value)
                    self.param_vars[effect_key][param_name] = var
                else:
                    var = self.param_vars[effect_key][param_name]
                
                # Slider
                slider = ttk.Scale(control_frame, from_=param_info['min'], to=param_info['max'],
                                   variable=var, orient=tk.HORIZONTAL, length=180)
                slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Wartość
                value_label = ttk.Label(control_frame, 
                                       text=f"{current_value:.2f}" if isinstance(current_value, float) else str(current_value),
                                       style='Accent.TLabel', width=6, font=('Segoe UI', 8))
                value_label.pack(side=tk.LEFT, padx=3)
                
                # Aktualizuj label przy zmianie i zapisz do effect_params
                def update_param(val, eff=effect_key, par=param_name, lbl=value_label, 
                               v=var, is_float=isinstance(param_info['value'], float)):
                    if is_float:
                        lbl.config(text=f"{v.get():.2f}")
                    else:
                        lbl.config(text=str(int(v.get())))
                    # Zapisz do effect_params
                    if eff not in self.effect_params:
                        self.effect_params[eff] = {}
                    self.effect_params[eff][par] = v.get()
                
                # Usuń stare trace jeśli istnieje, dodaj nowe
                var.trace_add('write', lambda *args, u=update_param: u(None))
                
                # Przycisk reset
                def reset_param(eff=effect_key, par=param_name, v=var, default=param_info['value']):
                    v.set(default)
                
                ttk.Button(control_frame, text="↺", width=3, 
                          command=reset_param).pack(side=tk.LEFT, padx=2)
        
        # Aktualizuj region scrollowania
        self.effects_container.update_idletasks()
        self.middle_canvas.configure(scrollregion=self.middle_canvas.bbox("all"))
    
    def reset_all_params(self):
        """Resetuje wszystkie parametry zaawansowane do wartości domyślnych."""
        for effect_key in self.param_vars:
            current_params = get_default_effect_params()
            for param_name, var in self.param_vars[effect_key].items():
                if effect_key in current_params and param_name in current_params[effect_key]:
                    default_value = current_params[effect_key][param_name]['value']
                    var.set(default_value)
        self.log(language_manager.t('log_params_reset'))
    
    def setup_right_panel(self, parent):
        """Konfiguruje prawy panel z podglądami."""
        # Dwa odtwarzacze obok siebie
        players_frame = ttk.Frame(parent)
        players_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.original_player = PreviewPlayer(players_frame, language_manager.t('original_preview'), 320, 240)
        self.original_player.frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.output_player = PreviewPlayer(players_frame, language_manager.t('result_preview'), 320, 240)
        self.output_player.frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Wspólny slider dla obu podglądów
        slider_frame = ttk.LabelFrame(parent, padding=5)
        self.ui_elements['slider_frame'] = slider_frame
        slider_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sync_slider_var = tk.IntVar(value=0)
        self.sync_slider = ttk.Scale(slider_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                                      command=self.on_sync_slider)
        self.sync_slider.pack(fill=tk.X, pady=2)
        
        # Kontrolki wspólne - pod sliderem, wyśrodkowane
        common_ctrl_frame = ttk.Frame(slider_frame)
        common_ctrl_frame.pack(pady=5)
        
        ttk.Button(common_ctrl_frame, text="▶", width=4, command=self.play_both).pack(side=tk.LEFT, padx=3)
        ttk.Button(common_ctrl_frame, text="⏸", width=4, command=self.stop_both).pack(side=tk.LEFT, padx=3)
        ttk.Button(common_ctrl_frame, text="⏹", width=4, command=self.stop_both).pack(side=tk.LEFT, padx=3)
        ttk.Button(common_ctrl_frame, text="◀", width=4, command=self.prev_both_frames).pack(side=tk.LEFT, padx=3)
        ttk.Button(common_ctrl_frame, text="▶", width=4, command=self.next_both_frames).pack(side=tk.LEFT, padx=3)
        
        # Synchronizacja
        self.sync_var = tk.BooleanVar(value=True)
        self.ui_elements['sync_checkbox'] = ttk.Checkbutton(common_ctrl_frame, text=language_manager.t('sync_players'), variable=self.sync_var)
        self.ui_elements['sync_checkbox'].pack(side=tk.LEFT, padx=10)
        
        self.sync_frame_info = tk.StringVar(value=language_manager.t('frame_info_empty'))
        ttk.Label(slider_frame, textvariable=self.sync_frame_info).pack(pady=2)
        
        # Log panel
        log_frame = ttk.LabelFrame(parent, padding=5)
        self.ui_elements['log_frame'] = log_frame
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=8, width=60, state=tk.DISABLED, 
                                 bg=NeonTheme.BG_MEDIUM, fg='#00ff00', font=('Consolas', 9),
                                 insertbackground='#00ff00', selectbackground='#2a2a4a')
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Przycisk czyszczenia logu
        self.ui_elements['clear_log_btn'] = ttk.Button(parent, text=language_manager.t('clear_log'), command=self.clear_log)
        self.ui_elements['clear_log_btn'].pack(pady=2)
    
    def log(self, message):
        """Dodaje wiadomość do logu."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Czyści log."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def on_pattern_change(self, event):
        """Handle pattern selection change."""
        for widget in self.pattern_params_frame.winfo_children():
            widget.pack_forget()
        mode = self.pattern_var.get()
        if mode == 'every_n':
            self.every_n_frame.pack()
        elif mode == 'random':
            self.random_frame.pack()
        elif mode == 'burst':
            self.burst_frame.pack()
        elif mode == 'keyframes':
            # Tryb keyframes - ukryj parametry wzorca
            pass
        
        # Zarządzaj aktywnością suwaka intensywności i trybu intensywności
        if mode == 'keyframes':
            # Deaktywuj suwak i combobox intensywności
            self.intensity_scale.config(state='disabled')
            self.intensity_mode_combo.config(state='disabled')
            # Aktywuj przycisk Keyframe
            self.keyframe_button.config(state='normal')
        else:
            # Aktywuj suwak i combobox intensywności
            self.intensity_scale.config(state='normal')
            self.intensity_mode_combo.config(state='readonly')
            # Deaktywuj przycisk Keyframe
            self.keyframe_button.config(state='disabled')
    
    def on_intensity_mode_change(self, event):
        """Handle intensity mode selection change."""
        for widget in self.intensity_params_frame.winfo_children():
            widget.pack_forget()
        if self.intensity_mode_var.get() == 'pulse':
            self.pulse_frame.pack()
    
    def on_multiplier_enabled_change(self):
        """Aktualizuje stan spinboxa mnożnika w zależności od checkboxa."""
        if self.multiplier_enabled_var.get():
            self.multiplier_spinbox.config(state='normal')
            # Pokaż zawartość mnożnika
            if not self.multiplier_content_visible:
                self.show_content(self.multiplier_content_frame, 'multiplier')
        else:
            self.multiplier_spinbox.config(state='disabled')
            # Ukryj zawartość mnożnika
            if self.multiplier_content_visible:
                self.hide_content(self.multiplier_content_frame, 'multiplier')
    
    def on_glitch_enabled_change(self):
        """Obsługuje włączanie/wyłączanie sekcji glitcha, animacji i efektów."""
        if self.glitch_enabled_var.get():
            # Pokaż zawartość glitcha
            if not self.glitch_content_visible:
                self.show_content(self.glitch_content_frame, 'glitch')
            # Pokaż całą sekcję animacji
            if not self.anim_visible:
                self.show_frame(self.anim_frame, 'anim')
            # Pokaż całą sekcję efektów
            if not self.effects_visible:
                self.show_frame(self.effects_frame, 'effects')
        else:
            # Ukryj zawartość glitcha
            if self.glitch_content_visible:
                self.hide_content(self.glitch_content_frame, 'glitch')
            # Ukryj całą sekcję animacji
            if self.anim_visible:
                self.hide_frame(self.anim_frame, 'anim')
            # Ukryj całą sekcję efektów
            if self.effects_visible:
                self.hide_frame(self.effects_frame, 'effects')
    
    def show_content(self, frame, content_type):
        """Pokazuje zawartość sekcji."""
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        if content_type == 'multiplier':
            self.multiplier_content_visible = True
        elif content_type == 'glitch':
            self.glitch_content_visible = True
    
    def hide_content(self, frame, content_type):
        """Ukrywa zawartość sekcji."""
        frame.pack_forget()
        if content_type == 'multiplier':
            self.multiplier_content_visible = False
        elif content_type == 'glitch':
            self.glitch_content_visible = False
    
    def show_frame(self, frame, frame_type):
        """Pokazuje całą ramkę sekcji."""
        # Znajdź pasek postępu jako punkt odniesienia
        progress_frame = None
        for child in frame.master.winfo_children():
            if isinstance(child, ttk.LabelFrame) and "progress_section" in str(child.cget('text')):
                progress_frame = child
                break
        
        # Pakuj przed paskiem postępu aby zachować właściwą kolejność
        if progress_frame:
            frame.pack(fill=tk.X, pady=(0, 10), before=progress_frame)
        else:
            frame.pack(fill=tk.X, pady=(0, 10))
            
        if frame_type == 'anim':
            self.anim_visible = True
        elif frame_type == 'effects':
            self.effects_visible = True
    
    def hide_frame(self, frame, frame_type):
        """Ukrywa całą ramkę sekcji."""
        frame.pack_forget()
        if frame_type == 'anim':
            self.anim_visible = False
        elif frame_type == 'effects':
            self.effects_visible = False
    
    def on_effect_toggle(self):
        """Callback wywoływany gdy zmienia się stan efektu - aktualizuje panel zaawansowany."""
        if hasattr(self, 'advanced_mode_var') and self.advanced_mode_var.get():
            self.update_advanced_params_display()
    
    def open_topkek_link(self, event):
        """Otwiera link TOPKEK w przeglądarce."""
        try:
            webbrowser.open("https://xcwajdax.github.io/topkek")
            self.log(language_manager.t('log_topkek_opened'))
        except Exception as e:
            self.log(language_manager.t('log_topkek_error', error=str(e)))
    
    def create_new_output(self):
        """Tworzy nowy katalog wyjściowy."""
        from datetime import datetime
        
        # Pobierz katalog wejściowy jako bazę
        input_dir = self.input_var.get()
        if not input_dir:
            messagebox.showwarning(language_manager.t('warning_no_output_first'), language_manager.t('warning_no_output_first'))
            return
        
        # Utwórz nazwę nowego katalogu z timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"output_{timestamp}"
        
        # Znajdź katalog nadrzędny katalogu wejściowego
        input_path = Path(input_dir)
        parent_dir = input_path.parent
        
        # Utwórz pełną ścieżkę nowego katalogu
        new_output_path = parent_dir / base_name
        
        try:
            # Utwórz katalog
            new_output_path.mkdir(parents=True, exist_ok=True)
            
            # Ustaw w polu wyjściowym
            self.output_var.set(str(new_output_path))
            self.log(language_manager.t('log_output_created', path=new_output_path))
            
        except Exception as e:
            messagebox.showerror(language_manager.t('status_error'), f"{language_manager.t('log_output_error', error=str(e))}")
            self.log(language_manager.t('log_output_error', error=str(e)))
    
    def reimport_output(self):
        """Reimportuje obecny katalog wyjściowy jako wejściowy."""
        output_dir = self.output_var.get()
        
        if not output_dir:
            messagebox.showwarning(language_manager.t('warning_no_output_first'), language_manager.t('warning_no_output_first'))
            return
        
        if not os.path.exists(output_dir):
            messagebox.showerror(language_manager.t('status_error'), language_manager.t('warning_no_output_exists'))
            return
        
        # Sprawdź czy w katalogu są jakieś pliki obrazów
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}
        has_images = False
        
        try:
            for file in os.listdir(output_dir):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    has_images = True
                    break
        except Exception as e:
            messagebox.showerror(language_manager.t('status_error'), f"Nie można odczytać katalogu:\n{str(e)}")
            return
        
        if not has_images:
            messagebox.showwarning(language_manager.t('warning_no_images'), language_manager.t('warning_no_images'))
            return
        
        # Ustaw katalog wyjściowy jako wejściowy
        self.input_var.set(output_dir)
        self.log(language_manager.t('log_reimported', path=output_dir))
        
        # Wyciągnij bazową nazwę (bez _re_v_X)
        output_path = Path(output_dir)
        parent_dir = output_path.parent
        current_name = output_path.name
        
        # Znajdź bazową nazwę (usuń _re_v_X jeśli istnieje)
        if "_re_v_" in current_name:
            # Znajdź ostatnie wystąpienie _re_v_ i obetnij
            base_name = current_name.rsplit("_re_v_", 1)[0]
        else:
            base_name = current_name
        
        # Znajdź najwyższy numer wersji dla tej bazowej nazwy
        version_number = 1
        base_pattern = f"{base_name}_re_v_"
        
        try:
            for existing_dir in parent_dir.iterdir():
                if existing_dir.is_dir() and existing_dir.name.startswith(base_pattern):
                    try:
                        # Wyciągnij numer z nazwy katalogu
                        version_part = existing_dir.name[len(base_pattern):]
                        existing_version = int(version_part)
                        version_number = max(version_number, existing_version + 1)
                    except ValueError:
                        continue
        except Exception:
            pass  # Jeśli nie można odczytać katalogu, użyj domyślnej wersji
        
        # Utwórz nową nazwę katalogu wyjściowego
        new_output_name = f"{base_name}_re_v_{version_number}"
        new_output_path = parent_dir / new_output_name
        
        try:
            # Utwórz nowy katalog wyjściowy
            new_output_path.mkdir(parents=True, exist_ok=True)
            
            # Ustaw nowy katalog wyjściowy
            self.output_var.set(str(new_output_path))
            self.log(language_manager.t('log_new_output_created', path=new_output_path))
            
        except Exception as e:
            messagebox.showerror(language_manager.t('status_error'), f"{language_manager.t('log_new_output_error', error=str(e))}")
            self.log(language_manager.t('log_new_output_error', error=str(e)))
            return
        
        # Odśwież podgląd oryginału
        self.original_player.load_from_directory(output_dir, self.log)
        self.update_sync_slider_range()
        self.log(language_manager.t('log_frames_loaded_original', count=len(self.original_player.frames)))
    
    def refresh_previews(self):
        """Odświeża podglądy."""
        self.log(language_manager.t('log_refreshing'))
        self.original_player.load_from_directory(self.input_var.get(), self.log)
        self.output_player.load_from_directory(self.output_var.get(), self.log)
        self.update_sync_slider_range()
        self.log(language_manager.t('log_previews_refreshed', orig=len(self.original_player.frames), result=len(self.output_player.frames)))
    
    def preview_current_frame(self):
        """Renderuje aktualnie wybraną klatkę z włączonymi efektami i ładuje do podglądu."""
        if not PIL_AVAILABLE:
            messagebox.showerror(language_manager.t('status_error'), language_manager.t('error_no_pil'))
            return
        
        # Sprawdź czy są załadowane klatki oryginalne
        if not self.original_player.frames or not self.original_player.frame_paths:
            self.log(language_manager.t('log_no_frames'))
            return
        
        # Pobierz aktualną klatkę
        current_idx = self.original_player.current_frame
        if current_idx >= len(self.original_player.full_frames):
            return
        
        original_img = self.original_player.full_frames[current_idx]
        
        # Sprawdź czy glitch jest włączony
        if not self.glitch_enabled_var.get():
            self.log(language_manager.t('log_glitch_disabled'))
            # Skopiuj oryginalną klatkę do podglądu wyniku
            temp_path = "temp_preview_original.png"
            original_img.save(temp_path)
            self.output_player.load_frames([temp_path])
            # Usuń plik tymczasowy po chwili
            self.root.after(1000, lambda: os.path.exists(temp_path) and os.remove(temp_path))
            return
        
        # Zastosuj efekty
        enabled_effects = self.get_enabled_effects()
        if not enabled_effects:
            self.log(language_manager.t('log_no_effects'))
            return
        
        # Przygotuj parametry efektów
        effect_params = self.effect_params if self.advanced_mode_var.get() else {}
        
        try:
            # Zastosuj efekty
            result_img = apply_glitch_to_image(original_img, self.intensity_var.get(), 
                                             enabled_effects, effect_params)
            
            # Zapisz tymczasowo i załaduj do podglądu
            temp_path = "temp_preview.png"
            result_img.save(temp_path)
            self.output_player.load_frames([temp_path])
            
            # Usuń plik tymczasowy po chwili
            self.root.after(1000, lambda: os.path.exists(temp_path) and os.remove(temp_path))
            
            self.log(language_manager.t('log_preview_generated', frame=current_idx + 1, effects=', '.join(enabled_effects)))
            
        except Exception as e:
            messagebox.showerror(language_manager.t('status_error'), f"Nie można wygenerować podglądu:\n{str(e)}")
            self.log(language_manager.t('log_preview_error', error=str(e)))
    
    def open_animation_editor(self):
        """Otwiera edytor zaawansowanej animacji."""
        if not self.original_player.frames:
            messagebox.showwarning(language_manager.t('warning_no_frames_preview'), language_manager.t('warning_no_frames_preview'))
            return
        
        total_frames = len(self.original_player.frames)
        if self.multiplier_enabled_var.get():
            total_frames *= self.multiplier_var.get()
        
        editor = AnimationEditorWindow(self.root, self.intensity_var.get(), total_frames, self.get_anim_params())
        self.root.wait_window(editor.window)
        
        if editor.result:
            # Zapisz keyframe'y
            self.animation_keyframes = editor.result.get('keyframes', [])
            self.pattern_var.set('keyframes')
            self.log(language_manager.t('log_animation_configured'))
        else:
            self.log(language_manager.t('log_animation_cancelled'))
    
    def get_anim_params(self):
        """Zwraca parametry animacji."""
        params = {
            'pattern_mode': self.pattern_var.get(),
            'every_n': self.every_n_var.get(),
            'random_chance': self.random_chance_var.get(),
            'burst_on': self.burst_on_var.get(),
            'burst_off': self.burst_off_var.get(),
            'intensity_mode': self.intensity_mode_var.get(),
            'pulse_cycles': self.pulse_cycles_var.get(),
        }
        
        # Dodaj keyframe'y jeśli są ustawione
        if self.pattern_var.get() == 'keyframes' and self.animation_keyframes:
            params['keyframes'] = self.animation_keyframes
        
        return params
    
    def update_progress(self, value):
        """Aktualizuje pasek postępu."""
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def on_language_changed(self, new_language):
        """Called when language is changed - updates all UI elements."""
        # Update all stored UI elements
        if hasattr(self, 'ui_elements'):
            # Update labels
            if 'title_label' in self.ui_elements:
                self.ui_elements['title_label'].config(text=language_manager.t('app_title'))
            if 'productions_label' in self.ui_elements:
                self.ui_elements['productions_label'].config(text=language_manager.t('topkek_productions'))
            if 'language_frame' in self.ui_elements:
                self.ui_elements['language_frame'].config(text=language_manager.t('language_section'))
            if 'language_label' in self.ui_elements:
                self.ui_elements['language_label'].config(text=language_manager.t('language_label'))
            if 'input_label' in self.ui_elements:
                self.ui_elements['input_label'].config(text=language_manager.t('input_directory'))
            if 'output_label' in self.ui_elements:
                self.ui_elements['output_label'].config(text=language_manager.t('output_directory'))
            if 'input_browse_btn' in self.ui_elements:
                self.ui_elements['input_browse_btn'].config(text=language_manager.t('browse_button'))
            if 'output_browse_btn' in self.ui_elements:
                self.ui_elements['output_browse_btn'].config(text=language_manager.t('browse_button'))
            if 'new_output_btn' in self.ui_elements:
                self.ui_elements['new_output_btn'].config(text=language_manager.t('new_output'))
            if 'reimport_btn' in self.ui_elements:
                self.ui_elements['reimport_btn'].config(text=language_manager.t('reimport'))
            if 'multiplier_frame' in self.ui_elements:
                self.ui_elements['multiplier_frame'].config(text=language_manager.t('frame_multiplier'))
            if 'multiplier_checkbox' in self.ui_elements:
                self.ui_elements['multiplier_checkbox'].config(text=language_manager.t('enable_multiplier'))
            if 'multiplier_label' in self.ui_elements:
                self.ui_elements['multiplier_label'].config(text=language_manager.t('multiplier_label'))
            if 'multiplier_desc' in self.ui_elements:
                self.ui_elements['multiplier_desc'].config(text=language_manager.t('multiplier_desc'))
            if 'glitch_frame' in self.ui_elements:
                self.ui_elements['glitch_frame'].config(text=language_manager.t('glitch_section'))
            if 'glitch_checkbox' in self.ui_elements:
                self.ui_elements['glitch_checkbox'].config(text=language_manager.t('enable_glitch'))
            if 'anim_frame' in self.ui_elements:
                self.ui_elements['anim_frame'].config(text=language_manager.t('glitch_animation'))
            if 'intensity_label' in self.ui_elements:
                self.ui_elements['intensity_label'].config(text=language_manager.t('intensity_label'))
            if 'pattern_label' in self.ui_elements:
                self.ui_elements['pattern_label'].config(text=language_manager.t('pattern_label'))
            if 'intensity_mode_label' in self.ui_elements:
                self.ui_elements['intensity_mode_label'].config(text=language_manager.t('intensity_mode_label'))
            if 'keyframe_button' in self.ui_elements:
                self.ui_elements['keyframe_button'].config(text=language_manager.t('keyframe_button'))
            if 'effects_frame' in self.ui_elements:
                self.ui_elements['effects_frame'].config(text=language_manager.t('effects_section'))
            if 'all_effects_btn' in self.ui_elements:
                self.ui_elements['all_effects_btn'].config(text=language_manager.t('all_effects'))
            if 'no_effects_btn' in self.ui_elements:
                self.ui_elements['no_effects_btn'].config(text=language_manager.t('no_effects'))
            if 'random_effects_btn' in self.ui_elements:
                self.ui_elements['random_effects_btn'].config(text=language_manager.t('random_effects'))
            if 'advanced_checkbox' in self.ui_elements:
                self.ui_elements['advanced_checkbox'].config(text=language_manager.t('advanced_mode'))
            if 'progress_frame' in self.ui_elements:
                self.ui_elements['progress_frame'].config(text=language_manager.t('progress_section'))
            if 'start_btn' in self.ui_elements:
                self.ui_elements['start_btn'].config(text=language_manager.t('generate'))
            if 'refresh_btn' in self.ui_elements:
                self.ui_elements['refresh_btn'].config(text=language_manager.t('refresh'))
            if 'preview_btn' in self.ui_elements:
                self.ui_elements['preview_btn'].config(text=language_manager.t('preview'))
            
            # Middle panel elements
            if 'advanced_title' in self.ui_elements:
                self.ui_elements['advanced_title'].config(text=language_manager.t('advanced_params_title'))
            if 'advanced_desc' in self.ui_elements:
                self.ui_elements['advanced_desc'].config(text=language_manager.t('advanced_params_desc'))
            if 'reset_all_btn' in self.ui_elements:
                self.ui_elements['reset_all_btn'].config(text=language_manager.t('reset_all'))
            
            # Right panel elements
            if 'slider_frame' in self.ui_elements:
                self.ui_elements['slider_frame'].config(text=language_manager.t('common_navigation'))
            if 'sync_checkbox' in self.ui_elements:
                self.ui_elements['sync_checkbox'].config(text=language_manager.t('sync_players'))
            if 'log_frame' in self.ui_elements:
                self.ui_elements['log_frame'].config(text=language_manager.t('log_section'))
            if 'clear_log_btn' in self.ui_elements:
                self.ui_elements['clear_log_btn'].config(text=language_manager.t('clear_log'))
        
        # Update status
        if hasattr(self, 'status_var'):
            self.status_var.set(language_manager.t('status_ready'))
        
        # Update frame info
        if hasattr(self, 'sync_frame_info'):
            self.sync_frame_info.set(language_manager.t('frame_info_empty'))
        
        # Update preview player titles
        if hasattr(self, 'original_player'):
            self.original_player.update_title(language_manager.t('original_preview'))
        if hasattr(self, 'output_player'):
            self.output_player.update_title(language_manager.t('result_preview'))
        
        # Update effects registry and refresh effects display
        from config.effects_registry import get_effects, get_default_effect_params
        
        # Refresh effects checkboxes if they exist
        if hasattr(self, 'effect_vars'):
            self.refresh_effects_display()
        
        # Update advanced parameters display if visible
        if hasattr(self, 'advanced_mode_var') and self.advanced_mode_var.get():
            self.update_advanced_params_display()
    
    def refresh_effects_display(self):
        """Refresh the effects section with updated translations."""
        if not hasattr(self, 'effect_vars') or not hasattr(self, 'effects_frame'):
            return
        
        # Get current effects with translations
        current_effects = get_effects()
        
        # Find the effects grid frame
        effects_grid = None
        for child in self.effects_frame.winfo_children():
            if isinstance(child, ttk.Frame) and len(child.winfo_children()) > 0:
                # Check if this frame contains checkbuttons (effects grid)
                first_child = child.winfo_children()[0]
                if isinstance(first_child, ttk.Checkbutton):
                    effects_grid = child
                    break
        
        if effects_grid is None:
            return
        
        # Update checkbutton texts
        checkbuttons = []
        for child in effects_grid.winfo_children():
            if isinstance(child, ttk.Checkbutton):
                checkbuttons.append(child)
        
        # Map checkbuttons to effect keys by their order
        effect_keys = list(current_effects.keys())
        for i, checkbutton in enumerate(checkbuttons):
            if i < len(effect_keys):
                effect_key = effect_keys[i]
                effect_name = current_effects[effect_key][0]
                checkbutton.config(text=effect_name)
        for widget in self.pattern_params_frame.winfo_children():
            widget.pack_forget()
        mode = self.pattern_var.get()
        if mode == 'every_n':
            self.every_n_frame.pack()
        elif mode == 'random':
            self.random_frame.pack()
        elif mode == 'burst':
            self.burst_frame.pack()
        elif mode == 'keyframes':
            # Tryb keyframes - ukryj parametry wzorca
            pass
        
        # Zarządzaj aktywnością suwaka intensywności i trybu intensywności
        if mode == 'keyframes':
            # Deaktywuj suwak i combobox intensywności
            self.intensity_scale.config(state='disabled')
            self.intensity_mode_combo.config(state='disabled')
            # Aktywuj przycisk Keyframe
            self.keyframe_button.config(state='normal')
        else:
            # Aktywuj suwak i combobox intensywności
            self.intensity_scale.config(state='normal')
            self.intensity_mode_combo.config(state='readonly')
            # Deaktywuj przycisk Keyframe
            self.keyframe_button.config(state='disabled')
    
    def on_intensity_mode_change(self, event):
        for widget in self.intensity_params_frame.winfo_children():
            widget.pack_forget()
        if self.intensity_mode_var.get() == 'pulse':
            self.pulse_frame.pack()
    
    def on_multiplier_enabled_change(self):
        """Aktualizuje stan spinboxa mnożnika w zależności od checkboxa."""
        if self.multiplier_enabled_var.get():
            self.multiplier_spinbox.config(state='normal')
            # Pokaż zawartość mnożnika
            if not self.multiplier_content_visible:
                self.show_content(self.multiplier_content_frame, 'multiplier')
        else:
            self.multiplier_spinbox.config(state='disabled')
            # Ukryj zawartość mnożnika
            if self.multiplier_content_visible:
                self.hide_content(self.multiplier_content_frame, 'multiplier')
    
    def on_glitch_enabled_change(self):
        """Obsługuje włączanie/wyłączanie sekcji glitcha, animacji i efektów."""
        if self.glitch_enabled_var.get():
            # Pokaż zawartość glitcha (jeśli ma jakąś)
            if not self.glitch_content_visible:
                self.show_content(self.glitch_content_frame, 'glitch')
            # Pokaż całą sekcję animacji
            if not self.anim_visible:
                self.show_frame(self.anim_frame, 'anim')
            # Pokaż całą sekcję efektów
            if not self.effects_visible:
                self.show_frame(self.effects_frame, 'effects')
        else:
            # Ukryj zawartość glitcha
            if self.glitch_content_visible:
                self.hide_content(self.glitch_content_frame, 'glitch')
            # Ukryj całą sekcję animacji
            if self.anim_visible:
                self.hide_frame(self.anim_frame, 'anim')
            # Ukryj całą sekcję efektów
            if self.effects_visible:
                self.hide_frame(self.effects_frame, 'effects')
    
    def show_content(self, frame, content_type):
        """Pokazuje zawartość sekcji."""
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        if content_type == 'multiplier':
            self.multiplier_content_visible = True
        elif content_type == 'glitch':
            self.glitch_content_visible = True
    
    def hide_content(self, frame, content_type):
        """Ukrywa zawartość sekcji."""
        frame.pack_forget()
        if content_type == 'multiplier':
            self.multiplier_content_visible = False
        elif content_type == 'glitch':
            self.glitch_content_visible = False
    
    def show_frame(self, frame, frame_type):
        """Pokazuje całą ramkę sekcji."""
        # Znajdź pasek postępu jako punkt odniesienia
        progress_frame = None
        for child in frame.master.winfo_children():
            if isinstance(child, ttk.LabelFrame) and "Postęp" in str(child.cget('text')):
                progress_frame = child
                break
        
        # Pakuj przed paskiem postępu aby zachować właściwą kolejność
        if progress_frame:
            frame.pack(fill=tk.X, pady=(0, 10), before=progress_frame)
        else:
            frame.pack(fill=tk.X, pady=(0, 10))
            
        if frame_type == 'anim':
            self.anim_visible = True
        elif frame_type == 'effects':
            self.effects_visible = True
    
    def hide_frame(self, frame, frame_type):
        """Ukrywa całą ramkę sekcji."""
        frame.pack_forget()
        if frame_type == 'anim':
            self.anim_visible = False
        elif frame_type == 'effects':
            self.effects_visible = False
    
    def on_effect_toggle(self):
        """Callback wywoływany gdy zmienia się stan efektu - aktualizuje panel zaawansowany."""
        if hasattr(self, 'advanced_mode_var') and self.advanced_mode_var.get():
            self.update_advanced_params_display()
    
    def toggle_advanced_mode(self):
        """Przełącza tryb zaawansowany - pokazuje/ukrywa środkowy panel."""
        if self.advanced_mode_var.get():
            # Pokaż środkowy panel
            if not self.middle_panel_visible:
                self.main_paned.add(self.middle_frame, weight=0, before=self.main_paned.panes()[-1])
                self.middle_panel_visible = True
            self.update_advanced_params_display()
            self.log(language_manager.t('log_advanced_enabled'))
        else:
            # Ukryj środkowy panel
            if self.middle_panel_visible:
                self.main_paned.forget(self.middle_frame)
                self.middle_panel_visible = False
            self.log(language_manager.t('log_advanced_disabled'))
    
    def get_enabled_effects(self):
        """Zwraca listę włączonych efektów."""
        return [key for key, var in self.effect_vars.items() if var.get()]
    
    def select_all(self):
        """Wybiera wszystkie efekty."""
        for var in self.effect_vars.values():
            var.set(True)
        self.log(language_manager.t('log_all_effects_selected'))
    
    def select_none(self):
        """Odznacza wszystkie efekty."""
        for var in self.effect_vars.values():
            var.set(False)
        self.log(language_manager.t('log_no_effects_selected'))
    
    def select_random(self):
        """Wybiera losowe efekty."""
        for var in self.effect_vars.values():
            var.set(random.choice([True, False]))
        enabled = self.get_enabled_effects()
        self.log(language_manager.t('log_random_effects_selected', count=len(enabled)))
    
    def browse_input(self):
        """Wybiera katalog wejściowy i automatycznie ładuje klatki."""
        path = filedialog.askdirectory(title=language_manager.t('input_directory'))
        if path:
            self.input_var.set(path)
            if not self.output_var.get():
                self.output_var.set(path + "_glitched")
            self.log(language_manager.t('log_input_selected', path=path))
            self.original_player.load_from_directory(path, self.log)
            self.update_sync_slider_range()
            self.log(language_manager.t('log_frames_loaded', count=len(self.original_player.frames)))
    
    def browse_output(self):
        """Wybiera katalog wyjściowy."""
        path = filedialog.askdirectory(title=language_manager.t('output_directory'))
        if path:
            self.output_var.set(path)
            self.log(language_manager.t('log_output_selected', path=path))
    
    def create_new_output(self):
        """Tworzy nowy katalog wyjściowy."""
        from datetime import datetime
        
        # Pobierz katalog wejściowy jako bazę
        input_dir = self.input_var.get()
        if not input_dir:
            messagebox.showwarning(language_manager.t('warning_no_output_first'), language_manager.t('warning_no_output_first'))
            return
        
        # Utwórz nazwę nowego katalogu z timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"output_{timestamp}"
        
        # Znajdź katalog nadrzędny katalogu wejściowego
        input_path = Path(input_dir)
        parent_dir = input_path.parent
        
        # Utwórz pełną ścieżkę nowego katalogu
        new_output_path = parent_dir / base_name
        
        try:
            # Utwórz katalog
            new_output_path.mkdir(parents=True, exist_ok=True)
            
            # Ustaw w polu wyjściowym
            self.output_var.set(str(new_output_path))
            self.log(language_manager.t('log_output_created', path=new_output_path))
            
        except Exception as e:
            messagebox.showerror(language_manager.t('status_error'), f"{language_manager.t('log_output_error', error=str(e))}")
            self.log(language_manager.t('log_output_error', error=str(e)))
    
    def reimport_output(self):
        """Reimportuje obecny katalog wyjściowy jako wejściowy."""
        output_dir = self.output_var.get()
        
        if not output_dir:
            messagebox.showwarning("Uwaga", "Najpierw wybierz katalog wyjściowy!")
            return
        
        if not os.path.exists(output_dir):
            messagebox.showerror("Błąd", "Katalog wyjściowy nie istnieje!")
            return
        
        # Sprawdź czy w katalogu są jakieś pliki obrazów
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}
        has_images = False
        
        try:
            for file in os.listdir(output_dir):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    has_images = True
                    break
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można odczytać katalogu:\n{str(e)}")
            return
        
        if not has_images:
            messagebox.showwarning("Uwaga", "W katalogu wyjściowym nie znaleziono plików obrazów!")
            return
        
        # Ustaw katalog wyjściowy jako wejściowy
        self.input_var.set(output_dir)
        self.log(f"Reimportowano katalog wyjściowy jako wejściowy: {output_dir}")
        
        # Wyciągnij bazową nazwę (bez _re_v_X)
        output_path = Path(output_dir)
        parent_dir = output_path.parent
        current_name = output_path.name
        
        # Znajdź bazową nazwę (usuń _re_v_X jeśli istnieje)
        if "_re_v_" in current_name:
            # Znajdź ostatnie wystąpienie _re_v_ i obetnij
            base_name = current_name.rsplit("_re_v_", 1)[0]
        else:
            base_name = current_name
        
        # Znajdź najwyższy numer wersji dla tej bazowej nazwy
        version_number = 1
        base_pattern = f"{base_name}_re_v_"
        
        try:
            for existing_dir in parent_dir.iterdir():
                if existing_dir.is_dir() and existing_dir.name.startswith(base_pattern):
                    try:
                        # Wyciągnij numer z nazwy katalogu
                        version_part = existing_dir.name[len(base_pattern):]
                        existing_version = int(version_part)
                        version_number = max(version_number, existing_version + 1)
                    except ValueError:
                        continue
        except Exception:
            pass  # Jeśli nie można odczytać katalogu, użyj domyślnej wersji
        
        # Utwórz nową nazwę katalogu wyjściowego
        new_output_name = f"{base_name}_re_v_{version_number}"
        new_output_path = parent_dir / new_output_name
        
        try:
            # Utwórz nowy katalog wyjściowy
            new_output_path.mkdir(parents=True, exist_ok=True)
            
            # Ustaw nowy katalog wyjściowy
            self.output_var.set(str(new_output_path))
            self.log(f"Utworzono nowy katalog wyjściowy: {new_output_path}")
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można utworzyć nowego katalogu wyjściowego:\n{str(e)}")
            self.log(f"Błąd tworzenia katalogu wyjściowego: {str(e)}")
            return
        
        # Odśwież podgląd oryginału
        self.original_player.load_from_directory(output_dir, self.log)
        self.update_sync_slider_range()
        self.log(f"Załadowano {len(self.original_player.frames)} klatek do podglądu oryginału")
    
    def refresh_previews(self):
        """Odświeża podglądy."""
        self.log("Odświeżanie podglądów...")
        self.original_player.load_from_directory(self.input_var.get(), self.log)
        self.output_player.load_from_directory(self.output_var.get(), self.log)
        self.update_sync_slider_range()
        self.log(f"Oryginał: {len(self.original_player.frames)} klatek, Wynik: {len(self.output_player.frames)} klatek")
    
    def preview_current_frame(self):
        """Renderuje aktualnie wybraną klatkę z włączonymi efektami i ładuje do podglądu."""
        if not PIL_AVAILABLE:
            messagebox.showerror("Błąd", "PIL/Pillow nie jest dostępne!")
            return
        
        # Sprawdź czy są załadowane klatki oryginalne
        if not self.original_player.frames or not self.original_player.frame_paths:
            self.log("⚠ Brak załadowanych klatek do podglądu")
            return
        
        # Pobierz aktualną klatkę
        current_idx = self.original_player.current_frame
        if current_idx >= len(self.original_player.full_frames):
            return
        
        original_img = self.original_player.full_frames[current_idx]
        
        # Sprawdź czy glitch jest włączony
        if not self.glitch_enabled_var.get():
            self.log("Glitch wyłączony - pokazuję oryginał")
            # Skopiuj oryginalną klatkę do podglądu wyniku
            temp_path = "temp_preview_original.png"
            original_img.save(temp_path)
            self.output_player.load_frames([temp_path])
            # Usuń plik tymczasowy po chwili
            self.root.after(1000, lambda: os.path.exists(temp_path) and os.remove(temp_path))
            return
        
        # Zastosuj efekty
        enabled_effects = self.get_enabled_effects()
        if not enabled_effects:
            self.log("⚠ Brak wybranych efektów")
            return
        
        # Przygotuj parametry efektów
        effect_params = self.effect_params if self.advanced_mode_var.get() else {}
        
        try:
            # Zastosuj efekty
            result_img = apply_glitch_to_image(original_img, self.intensity_var.get(), 
                                             enabled_effects, effect_params)
            
            # Zapisz tymczasowo i załaduj do podglądu
            temp_path = "temp_preview.png"
            result_img.save(temp_path)
            self.output_player.load_frames([temp_path])
            
            # Usuń plik tymczasowy po chwili
            self.root.after(1000, lambda: os.path.exists(temp_path) and os.remove(temp_path))
            
            self.log(f"Podgląd klatki {current_idx + 1} z efektami: {', '.join(enabled_effects)}")
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wygenerować podglądu:\n{str(e)}")
            self.log(f"❌ Błąd podglądu: {str(e)}")
    
    def open_animation_editor(self):
        """Otwiera edytor zaawansowanej animacji."""
        if not self.original_player.frames:
            messagebox.showwarning("Uwaga", "Najpierw załaduj podgląd aby określić liczbę klatek!")
            return
        
        total_frames = len(self.original_player.frames)
        if self.multiplier_enabled_var.get():
            total_frames *= self.multiplier_var.get()
        
        editor = AnimationEditorWindow(self.root, self.intensity_var.get(), total_frames, self.get_anim_params())
        self.root.wait_window(editor.window)
        
        if editor.result:
            # Zapisz keyframe'y
            self.animation_keyframes = editor.result.get('keyframes', [])
            self.pattern_var.set('keyframes')
            self.log("Zaawansowana animacja została skonfigurowana")
        else:
            self.log("Anulowano edycję animacji")
    
    def get_anim_params(self):
        """Zwraca parametry animacji."""
        params = {
            'pattern_mode': self.pattern_var.get(),
            'every_n': self.every_n_var.get(),
            'random_chance': self.random_chance_var.get(),
            'burst_on': self.burst_on_var.get(),
            'burst_off': self.burst_off_var.get(),
            'intensity_mode': self.intensity_mode_var.get(),
            'pulse_cycles': self.pulse_cycles_var.get(),
        }
        
        # Dodaj keyframe'y jeśli są ustawione
        if self.pattern_var.get() == 'keyframes' and self.animation_keyframes:
            params['keyframes'] = self.animation_keyframes
        
        return params
    
    def update_progress(self, value):
        """Aktualizuje pasek postępu."""
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def start_process(self):
        """Rozpoczyna przetwarzanie klatek."""
        input_dir = self.input_var.get()
        output_dir = self.output_var.get()
        
        if not input_dir:
            messagebox.showerror(language_manager.t('status_error'), language_manager.t('error_no_input'))
            return
        if not os.path.exists(input_dir):
            messagebox.showerror(language_manager.t('status_error'), language_manager.t('error_input_not_exists'))
            return
        if not output_dir:
            output_dir = input_dir + "_glitched"
            self.output_var.set(output_dir)
        
        enabled_effects = self.get_enabled_effects()
        anim_params = self.get_anim_params()
        
        # Użyj parametrów zaawansowanych jeśli tryb jest włączony
        effect_params = self.effect_params if self.advanced_mode_var.get() else {}
        
        self.log("=" * 40)
        self.log(language_manager.t('log_generation_start'))
        self.log(language_manager.t('log_input_path', path=input_dir))
        self.log(language_manager.t('log_output_path', path=output_dir))
        multiplier = self.multiplier_var.get() if self.multiplier_enabled_var.get() else 1
        multiplier_status = language_manager.t('log_multiplier_enabled') if self.multiplier_enabled_var.get() else language_manager.t('log_multiplier_disabled')
        self.log(language_manager.t('log_multiplier_info', mult=multiplier, status=multiplier_status))
        self.log(language_manager.t('log_intensity_info', intensity=f"{self.intensity_var.get():.1f}"))
        glitch_status = language_manager.t('log_glitch_yes') if self.glitch_enabled_var.get() else language_manager.t('log_glitch_no')
        self.log(language_manager.t('log_glitch_status', status=glitch_status))
        if enabled_effects:
            self.log(language_manager.t('log_effects_list', effects=', '.join(enabled_effects)))
        self.log(language_manager.t('log_pattern_info', pattern=anim_params['pattern_mode']))
        self.log(language_manager.t('log_intensity_mode_info', mode=anim_params['intensity_mode']))
        if self.advanced_mode_var.get():
            self.log(language_manager.t('log_advanced_mode_info'))
        
        self.start_btn.config(state=tk.DISABLED)
        self.status_var.set(language_manager.t('status_processing'))
        self.progress['value'] = 0
        
        def process():
            # Użyj mnożnika tylko jeśli jest włączony, w przeciwnym razie 1
            multiplier = self.multiplier_var.get() if self.multiplier_enabled_var.get() else 1
            count, error = process_frames(
                input_dir, output_dir,
                multiplier,
                self.intensity_var.get(),
                enabled_effects,
                self.glitch_enabled_var.get(),
                anim_params,
                effect_params,
                self.update_progress_with_log
            )
            self.root.after(0, lambda: self.finish_process(count, error))
        
        threading.Thread(target=process, daemon=True).start()
    
    def update_progress_with_log(self, value):
        """Aktualizuje progress i loguje komunikaty."""
        if isinstance(value, str):
            # Komunikat tekstowy
            self.root.after(0, lambda msg=value: self.log(msg))
        else:
            # Wartość procentowa - aktualizuj pasek postępu natychmiast
            self.progress['value'] = value
            # Loguj co 5% zamiast co 10% dla lepszej informacji zwrotnej
            if int(value) % 5 == 0 and int(value) != int(getattr(self, '_last_logged_progress', -1)):
                self._last_logged_progress = int(value)
                self.root.after(0, lambda v=value: self.log(language_manager.t('log_progress', percent=int(v))))
        # Wymuszaj odświeżenie interfejsu dla płynnej aktualizacji
        self.root.update_idletasks()
    
    def update_progress_only(self, value):
        """Aktualizuje tylko pasek postępu bez logowania (dla częstych aktualizacji)."""
        if isinstance(value, (int, float)):
            self.progress['value'] = value
            self.root.update_idletasks()
    
    def finish_process(self, count, error):
        """Kończy proces przetwarzania."""
        self.start_btn.config(state=tk.NORMAL)
        if error:
            self.status_var.set(language_manager.t('status_error'))
            self.log(language_manager.t('log_error', error=error))
            messagebox.showerror(language_manager.t('status_error'), error)
        else:
            self.status_var.set(language_manager.t('status_complete', count=count))
            self.log(language_manager.t('log_completed', count=count))
            self.log(language_manager.t('log_saved_to', path=self.output_var.get()))
            self.output_player.load_from_directory(self.output_var.get(), self.log)
            self.update_sync_slider_range()
            self.log(language_manager.t('log_result_loaded'))
            messagebox.showinfo(language_manager.t('status_complete', count=count), language_manager.t('success_frames_created', count=count))
    
    # Preview synchronization methods
    def play_both(self):
        """Odtwarza oba podglądy jednocześnie."""
        self.original_player.play()
        self.output_player.play()
        self.log(language_manager.t('log_playing_both'))
    
    def stop_both(self):
        """Zatrzymuje oba podglądy."""
        self.original_player.stop()
        self.output_player.stop()
        self.log(language_manager.t('log_stopped_both'))
    
    def prev_both_frames(self):
        """Przechodzi do poprzedniej klatki w obu podglądach."""
        if self.sync_var.get():
            # Synchronizowany - użyj wspólnego slidera
            current_value = int(self.sync_slider.get())
            if current_value > 0:
                self.sync_slider.set(current_value - 1)
                self.on_sync_slider(current_value - 1)
        else:
            # Niesynchronizowany - przesuń oba niezależnie
            self.original_player.prev_frame()
            self.output_player.prev_frame()
    
    def next_both_frames(self):
        """Przechodzi do następnej klatki w obu podglądach."""
        if self.sync_var.get():
            # Synchronizowany - użyj wspólnego slidera
            current_value = int(self.sync_slider.get())
            max_value = int(self.sync_slider.cget('to'))
            if current_value < max_value:
                self.sync_slider.set(current_value + 1)
                self.on_sync_slider(current_value + 1)
        else:
            # Niesynchronizowany - przesuń oba niezależnie
            self.original_player.next_frame()
            self.output_player.next_frame()
    
    def on_sync_slider(self, value):
        """Obsługuje wspólny slider dla obu podglądów."""
        if not self.sync_var.get():
            return
        
        frame_idx = int(float(value))
        
        # Synchronizuj oba odtwarzacze
        if self.original_player.frames:
            self.original_player.set_frame(frame_idx)
        if self.output_player.frames:
            self.output_player.set_frame(frame_idx)
        
        # Aktualizuj info
        total_frames = max(len(self.original_player.frames), len(self.output_player.frames))
        self.sync_frame_info.set(language_manager.t('frame_info', current=frame_idx + 1, total=total_frames))
    
    def update_sync_slider_range(self):
        """Aktualizuje zakres wspólnego slidera."""
        max_frames = max(len(self.original_player.frames), len(self.output_player.frames))
        if max_frames > 0:
            self.sync_slider.config(to=max_frames - 1)
            self.sync_frame_info.set(language_manager.t('frame_info', current=1, total=max_frames))
        else:
            self.sync_slider.config(to=1)
            self.sync_frame_info.set(language_manager.t('frame_info_empty'))


if __name__ == '__main__':
    if not PIL_AVAILABLE:
        root = tk.Tk()
        root.withdraw()
        # Import language manager for error message
        from config.languages import language_manager
        messagebox.showerror(language_manager.t('status_error'), language_manager.t('error_no_pil'))
        exit(1)
    
    root = tk.Tk()
    app = App(root)
    root.mainloop()