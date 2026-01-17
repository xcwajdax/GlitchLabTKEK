"""
Dark theme styling for Glitch Lab.
"""

import tkinter as tk
from tkinter import ttk


class NeonTheme:
    """Ciemny motyw z neonowym niebieskim akcentem."""
    
    # Kolory
    BG_DARK = '#1a1a2e'
    BG_MEDIUM = '#1a1a2e'
    BG_LIGHT = '#16213e'
    BG_CARD = '#1a1a2e'
    
    NEON_BLUE = '#00d4ff'
    NEON_BLUE_DIM = '#0099cc'
    NEON_GLOW = '#00ffff'
    
    TEXT_PRIMARY = '#ffffff'
    TEXT_SECONDARY = '#a0a0a0'
    TEXT_ACCENT = '#00d4ff'
    
    BORDER = '#2a2a4a'
    BORDER_GLOW = '#00d4ff'
    
    SUCCESS = '#00ff88'
    ERROR = '#ff4466'
    
    @classmethod
    def apply(cls, root):
        """Aplikuje ciemny motyw do aplikacji."""
        root.configure(bg=cls.BG_DARK)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Główne tło
        style.configure('.', 
                       background=cls.BG_DARK,
                       foreground=cls.TEXT_PRIMARY,
                       fieldbackground=cls.BG_MEDIUM,
                       troughcolor=cls.BG_MEDIUM,
                       bordercolor=cls.BORDER,
                       darkcolor=cls.BG_DARK,
                       lightcolor=cls.BG_LIGHT)
        
        # Frame
        style.configure('TFrame', background=cls.BG_DARK)
        style.configure('Card.TFrame', background=cls.BG_CARD)
        
        # Label
        style.configure('TLabel', 
                       background=cls.BG_DARK, 
                       foreground=cls.TEXT_PRIMARY,
                       font=('Segoe UI', 9))
        style.configure('Title.TLabel',
                       background=cls.BG_DARK,
                       foreground=cls.NEON_BLUE,
                       font=('Segoe UI', 12, 'bold'))
        style.configure('Accent.TLabel',
                       background=cls.BG_DARK,
                       foreground=cls.NEON_BLUE,
                       font=('Segoe UI', 9))
        style.configure('Card.TLabel',
                       background=cls.BG_CARD,
                       foreground=cls.TEXT_SECONDARY,
                       font=('Segoe UI', 8))
        
        # LabelFrame
        style.configure('TLabelframe', 
                       background=cls.BG_CARD,
                       foreground=cls.NEON_BLUE,
                       bordercolor=cls.BORDER,
                       relief='solid',
                       borderwidth=1)
        style.configure('TLabelframe.Label', 
                       background=cls.BG_CARD,
                       foreground=cls.NEON_BLUE,
                       font=('Segoe UI', 10, 'bold'))
        
        # Button
        style.configure('TButton',
                       background=cls.BG_LIGHT,
                       foreground=cls.TEXT_PRIMARY,
                       bordercolor=cls.NEON_BLUE_DIM,
                       focuscolor=cls.NEON_BLUE,
                       padding=(12, 6),
                       font=('Segoe UI', 9))
        style.map('TButton',
                 background=[('active', cls.BG_MEDIUM), ('pressed', cls.NEON_BLUE_DIM)],
                 foreground=[('active', cls.NEON_BLUE)],
                 bordercolor=[('active', cls.NEON_BLUE)])
        
        # Accent Button
        style.configure('Accent.TButton',
                       background=cls.NEON_BLUE_DIM,
                       foreground=cls.BG_DARK,
                       bordercolor=cls.NEON_BLUE,
                       padding=(15, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton',
                 background=[('active', cls.NEON_BLUE), ('pressed', cls.NEON_GLOW)],
                 foreground=[('active', cls.BG_DARK)])
        
        # Entry
        style.configure('TEntry',
                       fieldbackground=cls.BG_MEDIUM,
                       foreground=cls.TEXT_PRIMARY,
                       bordercolor=cls.BORDER,
                       insertcolor=cls.NEON_BLUE,
                       padding=5)
        style.map('TEntry',
                 bordercolor=[('focus', cls.NEON_BLUE)],
                 fieldbackground=[('focus', cls.BG_LIGHT)])
        
        # Combobox
        style.configure('TCombobox',
                       fieldbackground=cls.BG_MEDIUM,
                       background=cls.BG_LIGHT,
                       foreground=cls.TEXT_PRIMARY,
                       bordercolor=cls.BORDER,
                       arrowcolor=cls.NEON_BLUE,
                       padding=5)
        style.map('TCombobox',
                 bordercolor=[('focus', cls.NEON_BLUE)],
                 fieldbackground=[('focus', cls.BG_LIGHT)])
        
        # Spinbox
        style.configure('TSpinbox',
                       fieldbackground=cls.BG_MEDIUM,
                       background=cls.BG_LIGHT,
                       foreground=cls.TEXT_PRIMARY,
                       bordercolor=cls.BORDER,
                       arrowcolor=cls.NEON_BLUE,
                       padding=5)
        style.map('TSpinbox',
                 bordercolor=[('focus', cls.NEON_BLUE)])
        
        # Checkbutton
        style.configure('TCheckbutton',
                       background=cls.BG_DARK,
                       foreground=cls.TEXT_PRIMARY,
                       indicatorcolor=cls.BG_MEDIUM,
                       font=('Segoe UI', 9))
        style.map('TCheckbutton',
                 background=[('active', cls.BG_DARK)],
                 foreground=[('active', cls.NEON_BLUE)],
                 indicatorcolor=[('selected', cls.NEON_BLUE)])
        
        # Scale (Slider)
        style.configure('TScale',
                       background=cls.BG_DARK,
                       troughcolor=cls.BG_MEDIUM,
                       bordercolor=cls.BORDER,
                       sliderthickness=15,
                       sliderlength=20)
        style.configure('Horizontal.TScale',
                       background=cls.BG_DARK,
                       troughcolor=cls.BG_MEDIUM)
        style.map('TScale',
                 background=[('active', cls.NEON_BLUE_DIM)])
        
        # Progressbar
        style.configure('TProgressbar',
                       background=cls.NEON_BLUE,
                       troughcolor=cls.BG_MEDIUM,
                       bordercolor=cls.BORDER,
                       thickness=8)
        style.configure('Horizontal.TProgressbar',
                       background=cls.NEON_BLUE,
                       troughcolor=cls.BG_MEDIUM)
        
        # Scrollbar
        style.configure('TScrollbar',
                       background=cls.BG_LIGHT,
                       troughcolor=cls.BG_MEDIUM,
                       bordercolor=cls.BORDER,
                       arrowcolor=cls.NEON_BLUE)
        style.map('TScrollbar',
                 background=[('active', cls.NEON_BLUE_DIM)])
        
        # PanedWindow
        style.configure('TPanedwindow',
                       background=cls.BG_DARK)
        
        # Notebook (jeśli używany)
        style.configure('TNotebook',
                       background=cls.BG_DARK,
                       bordercolor=cls.BORDER)
        style.configure('TNotebook.Tab',
                       background=cls.BG_MEDIUM,
                       foreground=cls.TEXT_PRIMARY,
                       padding=(10, 5))
        style.map('TNotebook.Tab',
                 background=[('selected', cls.BG_CARD)],
                 foreground=[('selected', cls.NEON_BLUE)])
        
        return cls