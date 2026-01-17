"""
Animation editor window for Glitch Lab.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from gui.theme import NeonTheme
from core.animation import calculate_intensity_from_keyframes, INTERPOLATION_FUNCTIONS


class AnimationEditorWindow:
    """Zaawansowane okno edycji animacji glitcha z keyframe'ami."""
    
    def __init__(self, parent, base_intensity, total_frames, anim_params=None):
        self.parent = parent
        self.base_intensity = base_intensity
        self.total_frames = max(1, total_frames)
        self.result = None  # Przechowuje wynik (keyframe'y) po zamknięciu
        
        # Inicjalizuj keyframe'y
        if anim_params and anim_params.get('pattern_mode') == 'keyframes' and anim_params.get('keyframes'):
            self.keyframes = anim_params['keyframes'].copy()
        else:
            # Domyślny keyframe na początku
            self.keyframes = [
                {'frame': 0, 'intensity': base_intensity, 'interpolation': 'linear'}
            ]
        
        # Sortuj keyframe'y
        self.keyframes.sort(key=lambda k: k['frame'])
        
        # Utwórz okno
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Zaawansowana animacja glitcha")
        self.window.resizable(True, True)
        self.window.configure(bg=NeonTheme.BG_DARK)
        
        # Ustaw okno jako modalne
        self.window.transient(parent)
        self.window.grab_set()
        
        # Zmienne dla timeline
        self.timeline_width = 800
        self.timeline_height = 300
        self.timeline_padding = 50
        self.selected_keyframe = None
        self.dragging_keyframe = None
        self.playhead_frame = 0
        
        # Zmienne dla podglądu
        self.preview_playing = False
        self.preview_after_id = None
        
        self.setup_ui()
        self.draw_timeline()
        
        # Automatyczne dopasowanie rozmiaru okna do zawartości
        self.window.update_idletasks()
        req_width = self.window.winfo_reqwidth()
        req_height = self.window.winfo_reqheight()
        # Dodaj margines dla lepszego wyglądu
        self.window.geometry(f"{req_width + 20}x{req_height + 20}")
        # Ustaw minimalny rozmiar aby zapobiec zbyt małym oknom
        self.window.minsize(800, 500)
        
        # Obsługa zamknięcia okna
        self.window.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def setup_ui(self):
        """Konfiguruje interfejs użytkownika."""
        # Główny kontener
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Górny panel - Timeline
        timeline_frame = ttk.LabelFrame(main_frame, text="📊 Timeline", padding=5)
        timeline_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas dla timeline
        canvas_frame = tk.Frame(timeline_frame, bg=NeonTheme.BG_DARK)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.timeline_canvas = tk.Canvas(
            canvas_frame,
            width=self.timeline_width,
            height=self.timeline_height,
            bg=NeonTheme.BG_DARK,
            highlightthickness=0
        )
        self.timeline_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar dla timeline (jeśli potrzebny)
        timeline_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.timeline_canvas.xview)
        self.timeline_canvas.configure(xscrollcommand=timeline_scroll.set)
        timeline_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind na zmianę rozmiaru
        self.timeline_canvas.bind("<Configure>", self.on_timeline_resize)
        
        # Bind na obsługę myszy
        self.timeline_canvas.bind("<Button-1>", self.on_timeline_click)
        self.timeline_canvas.bind("<B1-Motion>", self.on_timeline_drag)
        self.timeline_canvas.bind("<ButtonRelease-1>", self.on_timeline_release)
        self.timeline_canvas.bind("<Button-3>", self.on_timeline_right_click)  # Prawy przycisk
        
        # Dolny panel - podzielony na lewą (keyframe'y) i prawą (podgląd)
        bottom_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        bottom_paned.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Lewy panel - lista keyframe'ów
        left_panel = ttk.Frame(bottom_paned, width=350)
        bottom_paned.add(left_panel, weight=1)
        self.setup_keyframes_panel(left_panel)
        
        # Prawy panel - podgląd
        right_panel = ttk.Frame(bottom_paned, width=300)
        bottom_paned.add(right_panel, weight=1)
        self.setup_preview_panel(right_panel)
        
        # Przyciski akcji
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(actions_frame, text="Eksportuj JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Importuj JSON", command=self.import_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Reset", command=self.reset_keyframes).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(actions_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(actions_frame, text="Anuluj", command=self.on_cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions_frame, text="Zastosuj", style='Accent.TButton', command=self.on_apply).pack(side=tk.RIGHT, padx=5)
    
    def setup_keyframes_panel(self, parent):
        """Konfiguruje panel z listą keyframe'ów."""
        # Tytuł
        ttk.Label(parent, text="🎯 Keyframe'y", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        # Lista keyframe'ów w scrollable frame
        list_frame = ttk.LabelFrame(parent, text="Lista", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas z scrollbarem dla listy
        list_canvas = tk.Canvas(list_frame, bg=NeonTheme.BG_DARK, highlightthickness=0, height=150)
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=list_canvas.yview)
        list_scrollable = ttk.Frame(list_canvas)
        
        list_scrollable.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
        list_canvas.create_window((0, 0), window=list_scrollable, anchor="nw")
        list_canvas.configure(yscrollcommand=list_scrollbar.set)
        
        list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.keyframes_list_frame = list_scrollable
        self.keyframes_list_canvas = list_canvas
        
        # Przyciski akcji keyframe'ów
        kf_actions = ttk.Frame(parent)
        kf_actions.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(kf_actions, text="➕ Dodaj", command=self.add_keyframe_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(kf_actions, text="✏️ Edytuj", command=self.edit_selected_keyframe).pack(side=tk.LEFT, padx=2)
        ttk.Button(kf_actions, text="🗑️ Usuń", command=self.delete_selected_keyframe).pack(side=tk.LEFT, padx=2)
        
        # Panel edycji wybranego keyframe'a
        edit_frame = ttk.LabelFrame(parent, text="Edycja", padding=10)
        edit_frame.pack(fill=tk.X)
        
        # Klatka
        frame_row = ttk.Frame(edit_frame)
        frame_row.pack(fill=tk.X, pady=2)
        ttk.Label(frame_row, text="Klatka:").pack(side=tk.LEFT)
        self.edit_frame_var = tk.IntVar(value=0)
        self.edit_frame_spin = ttk.Spinbox(frame_row, from_=0, to=self.total_frames-1, 
                                           textvariable=self.edit_frame_var, width=10)
        self.edit_frame_spin.pack(side=tk.LEFT, padx=5)
        
        # Intensywność
        intensity_row = ttk.Frame(edit_frame)
        intensity_row.pack(fill=tk.X, pady=2)
        ttk.Label(intensity_row, text="Intensywność:").pack(side=tk.LEFT)
        self.edit_intensity_var = tk.DoubleVar(value=2.0)
        intensity_scale = ttk.Scale(intensity_row, from_=0.0, to=5.0, 
                                   variable=self.edit_intensity_var, orient=tk.HORIZONTAL, length=150)
        intensity_scale.pack(side=tk.LEFT, padx=5)
        self.edit_intensity_label = ttk.Label(intensity_row, text="2.0", style='Accent.TLabel', width=5)
        self.edit_intensity_label.pack(side=tk.LEFT)
        self.edit_intensity_var.trace_add('write', lambda *args: self.edit_intensity_label.config(
            text=f"{self.edit_intensity_var.get():.2f}"))
        
        # Interpolacja
        interp_row = ttk.Frame(edit_frame)
        interp_row.pack(fill=tk.X, pady=2)
        ttk.Label(interp_row, text="Interpolacja:").pack(side=tk.LEFT)
        self.edit_interp_var = tk.StringVar(value='linear')
        interp_combo = ttk.Combobox(interp_row, textvariable=self.edit_interp_var, 
                                    values=list(INTERPOLATION_FUNCTIONS.keys()), state='readonly', width=15)
        interp_combo.pack(side=tk.LEFT, padx=5)
        
        # Przycisk zastosuj zmiany
        ttk.Button(edit_frame, text="Zastosuj zmiany", command=self.apply_edit_changes).pack(pady=(5, 0))
        
        # Odśwież listę
        self.refresh_keyframes_list()
    
    def setup_preview_panel(self, parent):
        """Konfiguruje panel podglądu."""
        ttk.Label(parent, text="👁️ Podgląd", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        # Info o aktualnej klatce
        info_frame = ttk.LabelFrame(parent, text="Aktualna klatka", padding=5)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_frame_var = tk.StringVar(value="Klatka: 0")
        ttk.Label(info_frame, textvariable=self.preview_frame_var).pack()
        
        self.preview_intensity_var = tk.StringVar(value="Intensywność: 2.00")
        ttk.Label(info_frame, textvariable=self.preview_intensity_var, style='Accent.TLabel').pack()
        
        # Kontrolki odtwarzania
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_play_btn = ttk.Button(controls_frame, text="▶", width=4, command=self.toggle_preview)
        self.preview_play_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="⏸", width=4, command=self.stop_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="⏹", width=4, command=self.reset_preview).pack(side=tk.LEFT, padx=2)
        
        # Slider klatki
        self.preview_slider = ttk.Scale(parent, from_=0, to=self.total_frames-1, 
                                        orient=tk.HORIZONTAL, command=self.on_preview_slider)
        self.preview_slider.pack(fill=tk.X, pady=5)
        
        # Wykres intensywności (mini)
        chart_frame = ttk.LabelFrame(parent, text="Wykres intensywności", padding=5)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.mini_chart_canvas = tk.Canvas(chart_frame, height=100, bg=NeonTheme.BG_DARK, highlightthickness=0)
        self.mini_chart_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_mini_chart()
    
    def on_timeline_resize(self, event):
        """Obsługuje zmianę rozmiaru timeline."""
        self.timeline_width = event.width
        self.timeline_height = event.height
        self.draw_timeline()
    
    def draw_timeline(self):
        """Rysuje timeline z osiami, siatką i keyframe'ami."""
        canvas = self.timeline_canvas
        canvas.delete("all")
        
        if self.timeline_width <= 0 or self.timeline_height <= 0:
            return
        
        padding = self.timeline_padding
        graph_width = self.timeline_width - padding * 2
        graph_height = self.timeline_height - padding * 2
        graph_x = padding
        graph_y = padding
        
        # Rysuj siatkę
        canvas.create_rectangle(graph_x, graph_y, graph_x + graph_width, graph_y + graph_height,
                               outline=NeonTheme.BORDER, fill=NeonTheme.BG_MEDIUM)
        
        # Linie poziome (intensywność)
        intensity_steps = 5
        for i in range(intensity_steps + 1):
            y = graph_y + (graph_height * i / intensity_steps)
            canvas.create_line(graph_x, y, graph_x + graph_width, y, 
                             fill=NeonTheme.BORDER, width=1, tags='grid')
            # Etykiety
            intensity_val = 5.0 - (5.0 * i / intensity_steps)
            canvas.create_text(graph_x - 5, y, text=f"{intensity_val:.1f}", 
                             fill=NeonTheme.TEXT_SECONDARY, anchor=tk.E, font=('Segoe UI', 8))
        
        # Linie pionowe (klatki)
        frame_steps = min(20, self.total_frames)
        for i in range(frame_steps + 1):
            x = graph_x + (graph_width * i / frame_steps)
            canvas.create_line(x, graph_y, x, graph_y + graph_height, 
                             fill=NeonTheme.BORDER, width=1, tags='grid')
            # Etykiety
            frame_val = int(self.total_frames * i / frame_steps)
            canvas.create_text(x, graph_y + graph_height + 5, text=str(frame_val), 
                             fill=NeonTheme.TEXT_SECONDARY, anchor=tk.N, font=('Segoe UI', 8))
        
        # Rysuj krzywą interpolacji
        self.draw_interpolation_curve(canvas, graph_x, graph_y, graph_width, graph_height)
        
        # Rysuj keyframe'y
        self.draw_keyframes_on_timeline(canvas, graph_x, graph_y, graph_width, graph_height)
        
        # Rysuj playhead
        self.draw_playhead(canvas, graph_x, graph_y, graph_width, graph_height)
        
        # Etykiety osi
        canvas.create_text(graph_x + graph_width // 2, graph_y + graph_height + 20, 
                          text="Klatka", fill=NeonTheme.TEXT_PRIMARY, font=('Segoe UI', 9))
        canvas.create_text(10, graph_y + graph_height // 2, text="Intensywność", 
                         fill=NeonTheme.TEXT_PRIMARY, font=('Segoe UI', 9), angle=90)
    
    def draw_interpolation_curve(self, canvas, x, y, width, height):
        """Rysuje krzywą interpolacji między keyframe'ami."""
        if len(self.keyframes) < 2:
            return
        
        sorted_kfs = sorted(self.keyframes, key=lambda k: k['frame'])
        points = []
        
        # Dla każdej pary keyframe'ów
        for i in range(len(sorted_kfs) - 1):
            kf_start = sorted_kfs[i]
            kf_end = sorted_kfs[i + 1]
            
            frame_start = kf_start['frame']
            frame_end = kf_end['frame']
            intensity_start = kf_start['intensity']
            intensity_end = kf_end['intensity']
            interp_type = kf_start.get('interpolation', 'linear')
            interp_func = INTERPOLATION_FUNCTIONS.get(interp_type, INTERPOLATION_FUNCTIONS['linear'])
            
            # Generuj punkty krzywej
            num_points = max(10, (frame_end - frame_start) * 2)
            for j in range(num_points + 1):
                t = j / num_points
                frame = frame_start + (frame_end - frame_start) * t
                intensity = interp_func(t, intensity_start, intensity_end)
                
                # Konwertuj na współrzędne canvas
                canvas_x = x + (width * frame / self.total_frames)
                canvas_y = y + (height * (1 - intensity / 5.0))
                
                points.append((canvas_x, canvas_y))
        
        # Rysuj linię przez wszystkie punkty
        if len(points) > 1:
            for i in range(len(points) - 1):
                canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1],
                                 fill=NeonTheme.NEON_GLOW, width=2, tags='curve')
    
    def draw_keyframes_on_timeline(self, canvas, x, y, width, height):
        """Rysuje keyframe'y na timeline."""
        for i, kf in enumerate(self.keyframes):
            frame = kf['frame']
            intensity = kf['intensity']
            
            # Konwertuj na współrzędne canvas
            canvas_x = x + (width * frame / self.total_frames)
            canvas_y = y + (height * (1 - intensity / 5.0))
            
            # Rysuj punkt
            size = 8
            color = NeonTheme.NEON_BLUE if i != self.selected_keyframe else NeonTheme.SUCCESS
            canvas.create_oval(canvas_x - size, canvas_y - size, 
                            canvas_x + size, canvas_y + size,
                            fill=color, outline=NeonTheme.NEON_GLOW, width=2, tags=f'keyframe_{i}')
            
            # Etykieta z wartościami
            label = f"F:{frame}\nI:{intensity:.2f}"
            canvas.create_text(canvas_x, canvas_y - 15, text=label,
                             fill=NeonTheme.TEXT_PRIMARY, font=('Segoe UI', 7), tags=f'keyframe_{i}')
            
            # Bind na kliknięcie
            canvas.tag_bind(f'keyframe_{i}', '<Button-1>', lambda e, idx=i: self.select_keyframe(idx))
            canvas.tag_bind(f'keyframe_{i}', '<B1-Motion>', lambda e, idx=i: self.start_drag_keyframe(e, idx))
    
    def draw_playhead(self, canvas, x, y, width, height):
        """Rysuje wskaźnik aktualnej pozycji (playhead)."""
        if self.total_frames == 0:
            return
        
        canvas_x = x + (width * self.playhead_frame / self.total_frames)
        canvas.create_line(canvas_x, y, canvas_x, y + height,
                          fill=NeonTheme.SUCCESS, width=2, tags='playhead')
        canvas.create_polygon(canvas_x - 5, y - 5, canvas_x + 5, y - 5, canvas_x, y,
                             fill=NeonTheme.SUCCESS, tags='playhead')
    
    def draw_mini_chart(self):
        """Rysuje mini wykres intensywności."""
        canvas = self.mini_chart_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        padding = 10
        graph_width = width - padding * 2
        graph_height = height - padding * 2
        
        # Tło
        canvas.create_rectangle(padding, padding, padding + graph_width, padding + graph_height,
                               fill=NeonTheme.BG_MEDIUM, outline=NeonTheme.BORDER)
        
        if not self.keyframes:
            return
        
        # Oblicz wartości dla wszystkich klatek
        points = []
        for frame in range(self.total_frames):
            intensity = calculate_intensity_from_keyframes(frame, self.total_frames, self.keyframes, self.base_intensity)
            x = padding + (graph_width * frame / self.total_frames)
            y = padding + graph_height - (graph_height * intensity / 5.0)
            points.append((x, y))
        
        # Rysuj linię
        if len(points) > 1:
            for i in range(len(points) - 1):
                canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1],
                                 fill=NeonTheme.NEON_BLUE, width=1)
        
        # Wskaźnik aktualnej klatki
        if self.playhead_frame < len(points):
            px, py = points[self.playhead_frame]
            canvas.create_line(px, padding, px, padding + graph_height,
                            fill=NeonTheme.SUCCESS, width=1)
    
    def refresh_keyframes_list(self):
        """Odświeża listę keyframe'ów."""
        # Usuń wszystkie widgety
        for widget in self.keyframes_list_frame.winfo_children():
            widget.destroy()
        
        # Sortuj keyframe'y
        sorted_kfs = sorted(self.keyframes, key=lambda k: k['frame'])
        
        # Dodaj każdy keyframe
        for i, kf in enumerate(sorted_kfs):
            kf_frame = ttk.Frame(self.keyframes_list_frame)
            kf_frame.pack(fill=tk.X, pady=2)
            
            # Informacje
            info_text = f"Klatka {kf['frame']}: Intensywność {kf['intensity']:.2f} ({kf.get('interpolation', 'linear')})"
            btn = ttk.Button(kf_frame, text=info_text, command=lambda idx=i: self.select_keyframe_from_list(idx))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            if i == self.selected_keyframe:
                btn.configure(style='Accent.TButton')
        
        # Aktualizuj scroll region
        self.keyframes_list_canvas.update_idletasks()
        self.keyframes_list_canvas.configure(scrollregion=self.keyframes_list_canvas.bbox("all"))
    
    def select_keyframe(self, index):
        """Wybiera keyframe po indeksie."""
        if 0 <= index < len(self.keyframes):
            self.selected_keyframe = index
            kf = self.keyframes[index]
            self.edit_frame_var.set(kf['frame'])
            self.edit_intensity_var.set(kf['intensity'])
            self.edit_interp_var.set(kf.get('interpolation', 'linear'))
            self.refresh_keyframes_list()
            self.draw_timeline()
    
    def select_keyframe_from_list(self, index):
        """Wybiera keyframe z listy."""
        sorted_kfs = sorted(self.keyframes, key=lambda k: k['frame'])
        if 0 <= index < len(sorted_kfs):
            # Znajdź oryginalny indeks
            kf = sorted_kfs[index]
            orig_idx = self.keyframes.index(kf)
            self.select_keyframe(orig_idx)
    
    def add_keyframe_dialog(self):
        """Dodaje nowy keyframe przez dialog."""
        # Użyj wartości z edycji lub domyślnych
        frame = self.edit_frame_var.get()
        intensity = self.edit_intensity_var.get()
        interpolation = self.edit_interp_var.get()
        
        # Sprawdź czy keyframe na tej klatce już istnieje
        for kf in self.keyframes:
            if kf['frame'] == frame:
                messagebox.showwarning("Uwaga", f"Keyframe na klatce {frame} już istnieje!")
                return
        
        # Dodaj keyframe
        new_kf = {
            'frame': frame,
            'intensity': intensity,
            'interpolation': interpolation
        }
        self.keyframes.append(new_kf)
        self.keyframes.sort(key=lambda k: k['frame'])
        
        # Wybierz nowy keyframe
        self.selected_keyframe = self.keyframes.index(new_kf)
        self.refresh_keyframes_list()
        self.draw_timeline()
        self.draw_mini_chart()
    
    def edit_selected_keyframe(self):
        """Edytuje wybrany keyframe."""
        if self.selected_keyframe is None or self.selected_keyframe >= len(self.keyframes):
            messagebox.showwarning("Uwaga", "Wybierz keyframe do edycji!")
            return
        
        self.apply_edit_changes()
    
    def apply_edit_changes(self):
        """Zastosowuje zmiany do wybranego keyframe'a."""
        if self.selected_keyframe is None or self.selected_keyframe >= len(self.keyframes):
            return
        
        frame = self.edit_frame_var.get()
        intensity = self.edit_intensity_var.get()
        interpolation = self.edit_interp_var.get()
        
        # Sprawdź czy klatka nie koliduje z innym keyframe'em
        for i, kf in enumerate(self.keyframes):
            if kf['frame'] == frame and i != self.selected_keyframe:
                messagebox.showwarning("Uwaga", f"Keyframe na klatce {frame} już istnieje!")
                return
        
        # Zaktualizuj keyframe
        self.keyframes[self.selected_keyframe]['frame'] = frame
        self.keyframes[self.selected_keyframe]['intensity'] = intensity
        self.keyframes[self.selected_keyframe]['interpolation'] = interpolation
        
        # Sortuj ponownie
        self.keyframes.sort(key=lambda k: k['frame'])
        
        # Zaktualizuj wybór
        for i, kf in enumerate(self.keyframes):
            if kf['frame'] == frame:
                self.selected_keyframe = i
                break
        
        self.refresh_keyframes_list()
        self.draw_timeline()
        self.draw_mini_chart()
    
    def delete_selected_keyframe(self):
        """Usuwa wybrany keyframe."""
        if self.selected_keyframe is None or self.selected_keyframe >= len(self.keyframes):
            messagebox.showwarning("Uwaga", "Wybierz keyframe do usunięcia!")
            return
        
        if len(self.keyframes) <= 1:
            messagebox.showwarning("Uwaga", "Musisz mieć przynajmniej jeden keyframe!")
            return
        
        del self.keyframes[self.selected_keyframe]
        self.selected_keyframe = None
        self.refresh_keyframes_list()
        self.draw_timeline()
        self.draw_mini_chart()
    
    def start_drag_keyframe(self, event, index):
        """Rozpoczyna przeciąganie keyframe'a."""
        self.dragging_keyframe = index
        event.widget = self.timeline_canvas
        self.on_timeline_click(event)
    
    def on_timeline_click(self, event):
        """Obsługuje kliknięcie na timeline."""
        canvas = self.timeline_canvas
        padding = self.timeline_padding
        graph_width = self.timeline_width - padding * 2
        graph_height = self.timeline_height - padding * 2
        
        # Konwertuj współrzędne myszy na klatkę i intensywność
        canvas_x = canvas.canvasx(event.x)
        canvas_y = canvas.canvasy(event.y)
        
        # Sprawdź czy kliknięto na keyframe (zostanie obsłużone przez tag_bind)
        # Jeśli nie, sprawdź czy kliknięto w obszarze wykresu
        if (padding <= canvas_x <= padding + graph_width and 
            padding <= canvas_y <= padding + graph_height):
            
            # Oblicz klatkę i intensywność
            frame = int((canvas_x - padding) / graph_width * self.total_frames)
            frame = max(0, min(self.total_frames - 1, frame))
            intensity = 5.0 - ((canvas_y - padding) / graph_height * 5.0)
            intensity = max(0.0, min(5.0, intensity))
            
            # Sprawdź czy kliknięto blisko istniejącego keyframe'a
            clicked_on_keyframe = False
            for i, kf in enumerate(self.keyframes):
                kf_x = padding + (graph_width * kf['frame'] / self.total_frames)
                kf_y = padding + (graph_height * (1 - kf['intensity'] / 5.0))
                distance = ((canvas_x - kf_x) ** 2 + (canvas_y - kf_y) ** 2) ** 0.5
                if distance < 15:  # Promień kliknięcia
                    self.select_keyframe(i)
                    self.dragging_keyframe = i
                    clicked_on_keyframe = True
                    break
            
            if not clicked_on_keyframe:
                # Ustaw wartości w edycji (użytkownik może dodać keyframe przyciskiem)
                self.edit_frame_var.set(frame)
                self.edit_intensity_var.set(intensity)
    
    def on_timeline_drag(self, event):
        """Obsługuje przeciąganie na timeline."""
        if self.dragging_keyframe is not None and 0 <= self.dragging_keyframe < len(self.keyframes):
            canvas = self.timeline_canvas
            padding = self.timeline_padding
            graph_width = self.timeline_width - padding * 2
            graph_height = self.timeline_height - padding * 2
            
            canvas_x = canvas.canvasx(event.x)
            canvas_y = canvas.canvasy(event.y)
            
            if (padding <= canvas_x <= padding + graph_width and 
                padding <= canvas_y <= padding + graph_height):
                
                # Oblicz klatkę i intensywność
                frame = int((canvas_x - padding) / graph_width * self.total_frames)
                frame = max(0, min(self.total_frames - 1, frame))
                intensity = 5.0 - ((canvas_y - padding) / graph_height * 5.0)
                intensity = max(0.0, min(5.0, intensity))
                
                # Sprawdź czy nie koliduje z innym keyframe'em
                can_move = True
                for i, kf in enumerate(self.keyframes):
                    if i != self.dragging_keyframe and kf['frame'] == frame:
                        can_move = False
                        break
                
                if can_move:
                    self.keyframes[self.dragging_keyframe]['frame'] = frame
                    self.keyframes[self.dragging_keyframe]['intensity'] = intensity
                    self.keyframes.sort(key=lambda k: k['frame'])
                    
                    # Zaktualizuj wybór po sortowaniu
                    kf = self.keyframes[self.dragging_keyframe]
                    for i, k in enumerate(self.keyframes):
                        if k['frame'] == kf['frame'] and k['intensity'] == kf['intensity']:
                            self.selected_keyframe = i
                            break
                    
                    self.refresh_keyframes_list()
                    self.draw_timeline()
                    self.draw_mini_chart()
    
    def on_timeline_release(self, event):
        """Obsługuje zwolnienie przycisku myszy na timeline."""
        self.dragging_keyframe = None
    
    def on_timeline_right_click(self, event):
        """Obsługuje prawy przycisk myszy na timeline."""
        canvas = self.timeline_canvas
        padding = self.timeline_padding
        graph_width = self.timeline_width - padding * 2
        graph_height = self.timeline_height - padding * 2
        
        canvas_x = canvas.canvasx(event.x)
        canvas_y = canvas.canvasy(event.y)
        
        if (padding <= canvas_x <= padding + graph_width and 
            padding <= canvas_y <= padding + graph_height):
            
            # Sprawdź czy kliknięto na keyframe
            clicked_keyframe = None
            for i, kf in enumerate(self.keyframes):
                kf_x = padding + (graph_width * kf['frame'] / self.total_frames)
                kf_y = padding + (graph_height * (1 - kf['intensity'] / 5.0))
                distance = ((canvas_x - kf_x) ** 2 + (canvas_y - kf_y) ** 2) ** 0.5
                if distance < 15:
                    clicked_keyframe = i
                    break
            
            if clicked_keyframe is not None and len(self.keyframes) > 1:
                # Menu kontekstowe - usuń keyframe
                if messagebox.askyesno("Usuń keyframe", "Czy na pewno chcesz usunąć ten keyframe?"):
                    self.selected_keyframe = clicked_keyframe
                    self.delete_selected_keyframe()
    
    def toggle_preview(self):
        """Przełącza odtwarzanie podglądu."""
        if self.preview_playing:
            self.stop_preview()
        else:
            self.start_preview()
    
    def start_preview(self):
        """Rozpoczyna odtwarzanie podglądu."""
        self.preview_playing = True
        self.preview_play_btn.configure(text="⏸")
        self.animate_preview()
    
    def stop_preview(self):
        """Zatrzymuje odtwarzanie podglądu."""
        self.preview_playing = False
        self.preview_play_btn.configure(text="▶")
        if self.preview_after_id:
            self.window.after_cancel(self.preview_after_id)
            self.preview_after_id = None
    
    def reset_preview(self):
        """Resetuje podgląd do początku."""
        self.stop_preview()
        self.playhead_frame = 0
        self.preview_slider.set(0)
        self.update_preview_info()
        self.draw_timeline()
        self.draw_mini_chart()
    
    def animate_preview(self):
        """Animuje podgląd."""
        if not self.preview_playing:
            return
        
        self.playhead_frame = (self.playhead_frame + 1) % self.total_frames
        self.preview_slider.set(self.playhead_frame)
        self.update_preview_info()
        self.draw_timeline()
        self.draw_mini_chart()
        
        # Kontynuuj animację
        delay = int(1000 / 24)  # 24 FPS
        self.preview_after_id = self.window.after(delay, self.animate_preview)
    
    def on_preview_slider(self, value):
        """Obsługuje zmianę slidera podglądu."""
        frame = int(float(value))
        self.playhead_frame = frame
        self.update_preview_info()
        self.draw_timeline()
        self.draw_mini_chart()
    
    def update_preview_info(self):
        """Aktualizuje informacje w podglądzie."""
        self.preview_frame_var.set(f"Klatka: {self.playhead_frame}")
        intensity = calculate_intensity_from_keyframes(
            self.playhead_frame, self.total_frames, self.keyframes, self.base_intensity
        )
        self.preview_intensity_var.set(f"Intensywność: {intensity:.2f}")
    
    def export_json(self):
        """Eksportuje animację do pliku JSON."""
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            data = {
                'keyframes': self.keyframes,
                'total_frames': self.total_frames,
                'base_intensity': self.base_intensity
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Sukces", f"Animacja zapisana do:\n{file_path}")
    
    def import_json(self):
        """Importuje animację z pliku JSON."""
        
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'keyframes' in data:
                    self.keyframes = data['keyframes']
                    if 'total_frames' in data:
                        self.total_frames = data['total_frames']
                    if 'base_intensity' in data:
                        self.base_intensity = data['base_intensity']
                    
                    # Walidacja
                    self.keyframes = [kf for kf in self.keyframes if 0 <= kf['frame'] < self.total_frames]
                    self.keyframes.sort(key=lambda k: k['frame'])
                    
                    if not self.keyframes:
                        # Domyślny keyframe
                        self.keyframes = [
                            {'frame': 0, 'intensity': self.base_intensity, 'interpolation': 'linear'}
                        ]
                    
                    self.selected_keyframe = None
                    self.refresh_keyframes_list()
                    self.draw_timeline()
                    self.draw_mini_chart()
                    messagebox.showinfo("Sukces", "Animacja załadowana!")
                else:
                    messagebox.showerror("Błąd", "Nieprawidłowy format pliku!")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można załadować pliku:\n{str(e)}")
    
    def reset_keyframes(self):
        """Resetuje keyframe'y do domyślnych."""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zresetować wszystkie keyframe'y?"):
            self.keyframes = [
                {'frame': 0, 'intensity': self.base_intensity, 'interpolation': 'linear'}
            ]
            self.selected_keyframe = None
            self.refresh_keyframes_list()
            self.draw_timeline()
            self.draw_mini_chart()
    
    def on_apply(self):
        """Zastosowuje zmiany i zamyka okno."""
        # Zapisz keyframe'y jako wynik
        self.result = {
            'pattern_mode': 'keyframes',
            'keyframes': self.keyframes.copy()
        }
        self.window.destroy()
    
    def on_cancel(self):
        """Anuluje zmiany i zamyka okno."""
        self.result = None
        self.window.destroy()