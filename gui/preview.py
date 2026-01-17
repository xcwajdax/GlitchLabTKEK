"""
Preview player component for Glitch Lab.
"""

import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from core.utils import get_frame_info


class PreviewPlayer:
    """Odtwarzacz podglądu animacji."""
    
    def __init__(self, parent, title, width=320, height=240):
        self.frame = ttk.LabelFrame(parent, text=title, padding=8)
        self.title = title  # Store title for updates
        self.width = width
        self.height = height
        self.frames = []  # Thumbnails
        self.full_frames = []  # Pełne obrazy
        self.frame_paths = []  # Ścieżki do plików
        self.current_frame = 0
        self.playing = False
        self.fps = 24
        self.after_id = None
        
        # Zoom i pan
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.is_panning = False
        
        # Kolor tła obrazu
        self.bg_mode = 'black'  # 'black', 'white', 'checkerboard'
        
        # Dynamiczny rozmiar canvas
        self.canvas_width = width
        self.canvas_height = height
        self.image_aspect_ratio = None
        
        # Canvas do wyświetlania z ciemnym tłem i obramowaniem
        canvas_frame = tk.Frame(self.frame, bg='#00d4ff', padx=1, pady=1)
        canvas_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_frame, width=width, height=height, 
                                bg='#2a2a2a', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind na zmianę rozmiaru canvas
        self.canvas.bind("<Configure>", self.update_canvas_size)
        
        # Obsługa myszy dla zoom i pan
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux scroll down
        self.canvas.focus_set()  # Umożliwia obsługę klawiatury
        
        # Zmienne dla opcji podglądu (przeniesione do canvas)
        self.bg_var = tk.StringVar(value='black')
        self.zoom_info_var = tk.StringVar(value="Zoom: 100%")
        
        # Slider klatki - bezpośrednio pod oknem podglądu, 100% szerokości
        self.slider = ttk.Scale(self.frame, from_=0, to=1, orient=tk.HORIZONTAL, 
                                command=self.on_slider)
        self.slider.pack(fill=tk.X, pady=(5, 2))
        
        # Info o klatce i FPS - pod sliderem
        info_fps_frame = ttk.Frame(self.frame)
        info_fps_frame.pack(pady=2)
        
        # Info o klatce
        self.frame_info_var = tk.StringVar(value="Brak klatek")
        ttk.Label(info_fps_frame, textvariable=self.frame_info_var, style='Accent.TLabel').pack(side=tk.LEFT, padx=5)
        
        # FPS
        ttk.Label(info_fps_frame, text="FPS:").pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=24)
        fps_spin = ttk.Spinbox(info_fps_frame, from_=1, to=60, width=5, textvariable=self.fps_var,
                               command=self.update_fps)
        fps_spin.pack(side=tk.LEFT, padx=5)
        fps_spin.bind('<Return>', lambda e: self.update_fps())
        
        # Kontrolki odtwarzania - pod licznikiem i FPS
        ctrl_frame = ttk.Frame(self.frame)
        ctrl_frame.pack(pady=5)
        
        self.play_btn = ttk.Button(ctrl_frame, text="▶", width=4, command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=3)
        
        ttk.Button(ctrl_frame, text="⏸", width=4, command=self.stop).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="⏹", width=4, command=self.stop).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="◀", width=4, command=self.prev_frame).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="▶", width=4, command=self.next_frame).pack(side=tk.LEFT, padx=3)
        
        # Metadane (przeniesione pod kontrolki)
        self.metadata_frame = ttk.LabelFrame(self.frame, text="Metadane", padding=5)
        self.metadata_frame.pack(pady=5, fill=tk.X)
        
        self.metadata_dimensions = tk.StringVar(value="Wymiary: -")
        self.metadata_extension = tk.StringVar(value="Rozszerzenie: -")
        self.metadata_location = tk.StringVar(value="Lokalizacja: -")
        
        ttk.Label(self.metadata_frame, textvariable=self.metadata_dimensions, 
                 font=('Segoe UI', 8)).pack(anchor=tk.W)
        ttk.Label(self.metadata_frame, textvariable=self.metadata_extension, 
                 font=('Segoe UI', 8)).pack(anchor=tk.W)
        ttk.Label(self.metadata_frame, textvariable=self.metadata_location, 
                 font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        self.photo = None
        self.checkerboard_pattern = None
        
        # Zmienne dla overlay przycisków
        self.overlay_visible = True
        self.overlay_fade_timer = None
        
        # Bind na ruch myszy dla pokazywania/ukrywania overlay
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
    
    def on_mouse_motion(self, event):
        """Pokazuje overlay przy ruchu myszy."""
        self.show_overlay()
        # Anuluj timer ukrywania jeśli istnieje
        if self.overlay_fade_timer:
            self.frame.after_cancel(self.overlay_fade_timer)
            self.overlay_fade_timer = None
        # Ustaw timer na ukrycie overlay po 3 sekundach
        self.overlay_fade_timer = self.frame.after(3000, self.hide_overlay)
    
    def on_mouse_leave(self, event):
        """Ukrywa overlay gdy mysz opuszcza canvas."""
        if self.overlay_fade_timer:
            self.frame.after_cancel(self.overlay_fade_timer)
        self.overlay_fade_timer = self.frame.after(1000, self.hide_overlay)
    
    def show_overlay(self):
        """Pokazuje overlay z przyciskami."""
        if not self.overlay_visible:
            self.overlay_visible = True
            if self.frames:
                self.show_frame(self.current_frame)
    
    def hide_overlay(self):
        """Ukrywa overlay z przyciskami."""
        if self.overlay_visible:
            self.overlay_visible = False
            if self.frames:
                self.show_frame(self.current_frame)
    
    def draw_overlay_controls(self):
        """Rysuje półprzezroczyste kontrolki na canvas."""
        if not self.overlay_visible:
            return
        
        # Pobierz rzeczywisty rozmiar canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = self.canvas_width
            canvas_height = self.canvas_height
        
        # Półprzezroczyste tło na dole canvas
        overlay_height = 60
        overlay_y = canvas_height - overlay_height
        
        # Tło overlay (półprzezroczyste)
        self.canvas.create_rectangle(
            0, overlay_y, canvas_width, canvas_height,
            fill='#000000', stipple='gray50', tags='overlay'
        )
        
        # Lewa strona - opcje zoom
        left_x = 10
        button_y = overlay_y + 10
        button_height = 25
        button_spacing = 5
        
        # Przyciski zoom
        zoom_buttons = [
            ("FIT", self.fit_to_canvas),
            ("100%", self.set_zoom_100),
            ("Reset", self.reset_view)
        ]
        
        current_x = left_x
        for text, command in zoom_buttons:
            button_width = len(text) * 8 + 10
            # Tło przycisku
            btn_id = self.canvas.create_rectangle(
                current_x, button_y, current_x + button_width, button_y + button_height,
                fill='#333333', outline='#00d4ff', width=1, tags='overlay'
            )
            # Tekst przycisku
            text_id = self.canvas.create_text(
                current_x + button_width // 2, button_y + button_height // 2,
                text=text, fill='white', font=('Segoe UI', 8), tags='overlay'
            )
            # Bind na kliknięcie
            self.canvas.tag_bind(btn_id, '<Button-1>', lambda e, cmd=command: cmd())
            self.canvas.tag_bind(text_id, '<Button-1>', lambda e, cmd=command: cmd())
            
            current_x += button_width + button_spacing
        
        # Informacja o zoom
        zoom_text = self.zoom_info_var.get()
        self.canvas.create_text(
            current_x + 10, button_y + button_height // 2,
            text=zoom_text, fill='#00d4ff', font=('Segoe UI', 8, 'bold'), 
            anchor=tk.W, tags='overlay'
        )
        
        # Prawa strona - opcje tła
        right_x = canvas_width - 10
        bg_buttons = [
            ("Czarne", 'black'),
            ("Białe", 'white'), 
            ("Kratka", 'checkerboard')
        ]
        
        current_x = right_x
        for text, value in reversed(bg_buttons):
            button_width = len(text) * 8 + 10
            current_x -= button_width + button_spacing
            
            # Sprawdź czy to aktywny przycisk
            is_active = self.bg_var.get() == value
            fill_color = '#00d4ff' if is_active else '#333333'
            text_color = '#000000' if is_active else 'white'
            
            # Tło przycisku
            btn_id = self.canvas.create_rectangle(
                current_x, button_y, current_x + button_width, button_y + button_height,
                fill=fill_color, outline='#00d4ff', width=1, tags='overlay'
            )
            # Tekst przycisku
            text_id = self.canvas.create_text(
                current_x + button_width // 2, button_y + button_height // 2,
                text=text, fill=text_color, font=('Segoe UI', 8), tags='overlay'
            )
            # Bind na kliknięcie
            self.canvas.tag_bind(btn_id, '<Button-1>', lambda e, val=value: self.set_bg_mode(val))
            self.canvas.tag_bind(text_id, '<Button-1>', lambda e, val=value: self.set_bg_mode(val))
    
    def set_bg_mode(self, mode):
        """Ustawia tryb tła i odświeża widok."""
        self.bg_var.set(mode)
        self.on_bg_change()
    
    def update_canvas_size(self, event=None):
        """Aktualizuje rozmiar canvas zachowując aspect ratio obrazu."""
        if event:
            # Pobierz dostępną przestrzeń
            available_width = event.width
            available_height = event.height
            
            # Sprawdź czy rozmiar faktycznie się zmienił
            if abs(self.canvas_width - available_width) < 2 and abs(self.canvas_height - available_height) < 2:
                return  # Rozmiar nie zmienił się znacząco, uniknij rekurencji
            
            # Jeśli mamy obraz, zachowaj jego aspect ratio
            if self.image_aspect_ratio and self.image_aspect_ratio > 0:
                # Oblicz nowy rozmiar zachowując proporcje
                canvas_aspect = available_width / available_height if available_height > 0 else 1.0
                if self.image_aspect_ratio > canvas_aspect:
                    # Obraz jest szerszy - dopasuj do szerokości
                    new_width = available_width
                    new_height = int(available_width / self.image_aspect_ratio)
                else:
                    # Obraz jest wyższy - dopasuj do wysokości
                    new_height = available_height
                    new_width = int(available_height * self.image_aspect_ratio)
            else:
                # Brak obrazu - użyj dostępnej przestrzeni
                new_width = available_width
                new_height = available_height
            
            # Aktualizuj tylko jeśli rozmiar się zmienił
            if abs(self.canvas_width - new_width) > 1 or abs(self.canvas_height - new_height) > 1:
                self.canvas_width = new_width
                self.canvas_height = new_height
                
                # Przerysuj jeśli mamy obraz
                if self.frames:
                    self.show_frame(self.current_frame)
    
    def load_frames(self, frame_paths, progress_callback=None):
        """Ładuje klatki z listy ścieżek."""
        self.stop()
        self.frames = []
        self.full_frames = []
        self.frame_paths = []
        self.current_frame = 0
        # Reset zoom i pan
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        
        total_frames = len(frame_paths)
        for i, path in enumerate(frame_paths):
            try:
                img = Image.open(path)
                # Zapisz pełny obraz
                self.full_frames.append(img.copy())
                self.frame_paths.append(path)
                # Utwórz thumbnail
                thumb = img.copy()
                thumb.thumbnail((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)
                self.frames.append(thumb)
                
                # Callback postępu - aktualizuj częściej dla płynności
                if progress_callback and total_frames > 0:
                    progress = (i + 1) / total_frames * 100
                    # Aktualizuj komunikat co 5% lub co klatkę dla małych zestawów
                    update_frequency = max(1, total_frames // 20) if total_frames > 20 else 1
                    if i == 0 or (i + 1) % update_frequency == 0 or i == total_frames - 1:
                        progress_callback(f"Ładowanie klatek: {i + 1}/{total_frames} ({progress:.0f}%)")
                    
                    # Sprawdź czy progress_callback ma metodę update_progress_only dla częstszych aktualizacji
                    if hasattr(progress_callback, '__self__') and hasattr(progress_callback.__self__, 'update_progress_only'):
                        progress_callback.__self__.update_progress_only(progress)
                    elif isinstance(progress, (int, float)):
                        # Fallback - wyślij wartość liczbową przez zwykły callback
                        progress_callback(progress)
            except:
                pass
        
        if self.frames:
            # Ustaw aspect ratio pierwszego obrazu
            if self.full_frames:
                img = self.full_frames[0]
                self.image_aspect_ratio = img.width / img.height if img.height > 0 else None
            self.slider.configure(to=len(self.frames) - 1)
            self.show_frame(0)
            self.frame_info_var.set(f"Klatka 1/{len(self.frames)}")
            if progress_callback:
                progress_callback(f"✓ Załadowano {len(self.frames)} klatek do podglądu")
        else:
            self.frame_info_var.set("Brak klatek")
            self.zoom_info_var.set("Zoom: -")
            self.image_aspect_ratio = None
            self.canvas.delete("all")
            self.update_metadata(None)
            if progress_callback:
                progress_callback("⚠ Nie znaleziono klatek do załadowania")
    
    def load_from_directory(self, directory, progress_callback=None):
        """Ładuje klatki z katalogu."""
        if not directory or not os.path.exists(directory):
            return
        
        if progress_callback:
            progress_callback("Skanowanie katalogu...")
            # Resetuj pasek postępu na początku
            progress_callback(0)
        
        frames = []
        for file in Path(directory).iterdir():
            if file.is_file():
                frame_num, ext, _ = get_frame_info(file.name)
                if frame_num is not None:
                    frames.append((frame_num, file))
        
        frames.sort(key=lambda x: x[0])
        
        if progress_callback:
            progress_callback("=" * 30)
            progress_callback("Ładowanie podglądu...")
            progress_callback(f"Znaleziono {len(frames)} klatek")
        
        self.load_frames([str(f[1]) for f in frames], progress_callback)
    
    def create_checkerboard(self, size=20):
        """Tworzy wzór kratki jako obraz PIL."""
        pattern = Image.new('RGB', (size * 2, size * 2), color='white')
        pixels = pattern.load()
        for y in range(size * 2):
            for x in range(size * 2):
                if (x // size + y // size) % 2 == 0:
                    pixels[x, y] = (240, 240, 240)  # Jasny szary
                else:
                    pixels[x, y] = (200, 200, 200)  # Ciemniejszy szary
        return pattern
    
    def draw_image_background(self, img_width, img_height, x, y):
        """Rysuje tło obrazu pod obrazem z alpha."""
        bg_mode = self.bg_var.get()
        margin = 5  # Margines wokół obrazu
        
        if bg_mode == 'black':
            # Czarne tło obrazu
            self.canvas.create_rectangle(
                x - margin, y - margin,
                x + img_width + margin, y + img_height + margin,
                fill='#0d0d0d', outline='', tags='image_bg'
            )
        elif bg_mode == 'white':
            # Białe tło obrazu
            self.canvas.create_rectangle(
                x - margin, y - margin,
                x + img_width + margin, y + img_height + margin,
                fill='white', outline='', tags='image_bg'
            )
        elif bg_mode == 'checkerboard':
            # Wzór kratki jako tło obrazu
            if self.checkerboard_pattern is None:
                self.checkerboard_pattern = self.create_checkerboard()
            # Utwórz obraz kratki o rozmiarze obrazu + margines
            pattern_width = img_width + margin * 2
            pattern_height = img_height + margin * 2
            pattern_img = Image.new('RGB', (pattern_width, pattern_height))
            for py in range(0, pattern_height, 20):
                for px in range(0, pattern_width, 20):
                    pattern_img.paste(self.checkerboard_pattern, (px, py))
            self.checkerboard_photo = ImageTk.PhotoImage(pattern_img)
            self.canvas.create_image(x - margin, y - margin, anchor=tk.NW, 
                                    image=self.checkerboard_photo, tags='image_bg')
    
    def show_frame(self, idx):
        """Wyświetla klatkę o danym indeksie."""
        if not self.frames or idx < 0 or idx >= len(self.frames):
            return
        
        self.current_frame = idx
        
        # Użyj pełnego obrazu jeśli dostępny, w przeciwnym razie thumbnail
        if idx < len(self.full_frames):
            img = self.full_frames[idx].copy()
            # Aktualizuj aspect ratio
            self.image_aspect_ratio = img.width / img.height if img.height > 0 else None
        else:
            img = self.frames[idx].copy()
        
        # Zastosuj zoom
        if self.zoom != 1.0:
            new_width = int(img.width * self.zoom)
            new_height = int(img.height * self.zoom)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        self.canvas.delete("all")
        
        # Oblicz pozycję z uwzględnieniem pan
        # Użyj rzeczywistego rozmiaru canvas, jeśli dostępny, w przeciwnym razie użyj przechowywanych wartości
        actual_width = self.canvas.winfo_width()
        actual_height = self.canvas.winfo_height()
        
        # Jeśli canvas nie został jeszcze narysowany (rozmiar 1), użyj przechowywanych wartości
        if actual_width <= 1:
            actual_width = self.canvas_width
        if actual_height <= 1:
            actual_height = self.canvas_height
        
        canvas_center_x = actual_width // 2
        canvas_center_y = actual_height // 2
        
        x = canvas_center_x - img.width // 2 + self.pan_x
        y = canvas_center_y - img.height // 2 + self.pan_y
        
        # Rysuj tło obrazu przed obrazem
        self.draw_image_background(img.width, img.height, x, y)
        
        # Rysuj obraz
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo, tags='image')
        
        # Rysuj overlay kontrolki
        self.draw_overlay_controls()
        
        # Aktualizuj informacje o zoomie
        zoom_percent = int(self.zoom * 100)
        self.zoom_info_var.set(f"Zoom: {zoom_percent}%")
        
        # Aktualizuj informacje o klatce
        self.frame_info_var.set(f"Klatka {idx + 1}/{len(self.frames)}")
        self.slider.set(idx)
        
        # Aktualizuj metadane
        if idx < len(self.frame_paths):
            self.update_metadata(self.frame_paths[idx])
        else:
            self.update_metadata(None)
    
    def update_metadata(self, file_path):
        """Aktualizuje wyświetlane metadane."""
        if file_path is None or not os.path.exists(file_path):
            self.metadata_dimensions.set("Wymiary: -")
            self.metadata_extension.set("Rozszerzenie: -")
            self.metadata_location.set("Lokalizacja: -")
            return
        
        try:
            # Wymiary
            if self.current_frame < len(self.full_frames):
                img = self.full_frames[self.current_frame]
                self.metadata_dimensions.set(f"Wymiary: {img.width} × {img.height} px")
            else:
                self.metadata_dimensions.set("Wymiary: -")
            
            # Rozszerzenie
            _, ext = os.path.splitext(file_path)
            ext = ext[1:] if ext else "brak"
            self.metadata_extension.set(f"Rozszerzenie: {ext.upper()}")
            
            # Lokalizacja
            path_obj = Path(file_path)
            location = str(path_obj.parent)
            # Skróć jeśli zbyt długie
            if len(location) > 50:
                location = "..." + location[-47:]
            self.metadata_location.set(f"Lokalizacja: {location}")
        except:
            self.metadata_dimensions.set("Wymiary: -")
            self.metadata_extension.set("Rozszerzenie: -")
            self.metadata_location.set("Lokalizacja: -")
    
    def on_bg_change(self):
        """Wywoływane przy zmianie koloru tła obrazu."""
        if self.frames:
            self.show_frame(self.current_frame)
    
    def fit_to_canvas(self):
        """Dopasowuje rozmiar obrazu tak, aby mieścił się w oknie podglądu (zachowując proporcje)."""
        if not self.frames or self.current_frame >= len(self.full_frames):
            return
        
        img = self.full_frames[self.current_frame]
        if img.width == 0 or img.height == 0:
            return
        
        # Użyj rzeczywistego rozmiaru canvas
        actual_width = self.canvas.winfo_width()
        actual_height = self.canvas.winfo_height()
        
        # Jeśli canvas nie został jeszcze narysowany (rozmiar 1), użyj przechowywanych wartości
        if actual_width <= 1:
            actual_width = self.canvas_width
        if actual_height <= 1:
            actual_height = self.canvas_height
        
        # Oblicz dostępną przestrzeń (z marginesem)
        available_width = actual_width - 20
        available_height = actual_height - 20
        
        if available_width <= 0 or available_height <= 0:
            return
        
        # Oblicz zoom potrzebny do dopasowania obrazu do canvas
        # Użyj mniejszego z dwóch współczynników, aby cały obraz się zmieścił
        zoom_x = available_width / img.width
        zoom_y = available_height / img.height
        self.zoom = min(zoom_x, zoom_y)
        
        # Ogranicz zoom do rozsądnych wartości
        if self.zoom < 0.01:
            self.zoom = 0.01
        elif self.zoom > 10.0:
            self.zoom = 10.0
        
        # Centruj obraz (reset pan)
        self.pan_x = 0
        self.pan_y = 0
        
        if self.frames:
            self.show_frame(self.current_frame)
    
    def set_zoom_100(self):
        """Ustawia zoom na 100% (1.0) i centruje obraz."""
        self.zoom = 1.0
        # Centruj obraz (reset pan)
        self.pan_x = 0
        self.pan_y = 0
        if self.frames:
            self.show_frame(self.current_frame)
    
    def reset_view(self):
        """Centruje obraz w podglądzie (resetuje pan, zachowuje zoom)."""
        self.pan_x = 0
        self.pan_y = 0
        if self.frames:
            self.show_frame(self.current_frame)
    
    def on_mouse_down(self, event):
        """Rozpoczyna panowanie, ale tylko jeśli nie kliknięto na overlay."""
        # Sprawdź czy kliknięto na overlay
        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in clicked_items:
            if 'overlay' in self.canvas.gettags(item):
                return  # Nie rozpoczynaj panowania jeśli kliknięto na overlay
        
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
    
    def on_mouse_drag(self, event):
        """Przesuwa obraz podczas panowania."""
        if self.is_panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.pan_x += dx
            self.pan_y += dy
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            if self.frames:
                self.show_frame(self.current_frame)
    
    def on_mouse_up(self, event):
        """Kończy panowanie."""
        self.is_panning = False
    
    def on_mousewheel(self, event):
        """Obsługuje zoom kółkiem myszy."""
        if not self.frames:
            return
        
        # Wykryj kierunek scrollowania
        if event.num == 4 or event.delta > 0:  # Scroll up
            zoom_factor = 1.1
        elif event.num == 5 or event.delta < 0:  # Scroll down
            zoom_factor = 0.9
        else:
            return
        
        # Ogranicz zoom
        new_zoom = self.zoom * zoom_factor
        if 0.1 <= new_zoom <= 10.0:
            self.zoom = new_zoom
            # Zoom względem pozycji myszy
            if self.zoom != 1.0:
                # Przybliż/oddal względem środka canvas
                canvas_center_x = self.canvas_width // 2
                canvas_center_y = self.canvas_height // 2
                mouse_x = event.x
                mouse_y = event.y
                
                # Dostosuj pan tak, aby punkt pod myszą pozostał w tym samym miejscu
                if self.current_frame < len(self.full_frames):
                    img = self.full_frames[self.current_frame]
                    img_w = int(img.width * self.zoom)
                    img_h = int(img.height * self.zoom)
                    
                    # Oblicz pozycję obrazu
                    img_x = canvas_center_x - img_w // 2 + self.pan_x
                    img_y = canvas_center_y - img_h // 2 + self.pan_y
                    
                    # Punkt na obrazie pod myszą
                    img_point_x = mouse_x - img_x
                    img_point_y = mouse_y - img_y
                    
                    # Nowa pozycja obrazu po zoom
                    old_zoom = self.zoom / zoom_factor
                    new_img_w = int(img.width * self.zoom)
                    new_img_h = int(img.height * self.zoom)
                    new_img_x = canvas_center_x - new_img_w // 2
                    new_img_y = canvas_center_y - new_img_h // 2
                    
                    # Dostosuj pan tak, aby punkt pozostał w tym samym miejscu
                    scale_factor = self.zoom / old_zoom
                    self.pan_x = mouse_x - new_img_x - (img_point_x * scale_factor)
                    self.pan_y = mouse_y - new_img_y - (img_point_y * scale_factor)
            
            self.show_frame(self.current_frame)
    
    def next_frame(self):
        if self.frames:
            self.show_frame((self.current_frame + 1) % len(self.frames))
    
    def prev_frame(self):
        if self.frames:
            self.show_frame((self.current_frame - 1) % len(self.frames))
    
    def toggle_play(self):
        if self.playing:
            self.stop()
        else:
            self.play()
    
    def play(self):
        if not self.frames:
            return
        self.playing = True
        self.play_btn.configure(text="⏸")
        self.animate()
    
    def stop(self):
        self.playing = False
        self.play_btn.configure(text="▶")
        if self.after_id:
            self.frame.after_cancel(self.after_id)
            self.after_id = None
    
    def animate(self):
        if not self.playing:
            return
        self.next_frame()
        delay = int(1000 / self.fps_var.get())
        self.after_id = self.frame.after(delay, self.animate)
    
    def on_slider(self, value):
        if self.frames:
            idx = int(float(value))
            if idx != self.current_frame:
                self.show_frame(idx)
    
    def update_title(self, new_title):
        """Updates the title of the preview player."""
        self.title = new_title
        self.frame.config(text=new_title)
    
    def set_frame(self, idx):
        """Sets the current frame to the specified index."""
        if self.frames and 0 <= idx < len(self.frames):
            self.show_frame(idx)
    
    def update_fps(self):
        self.fps = self.fps_var.get()