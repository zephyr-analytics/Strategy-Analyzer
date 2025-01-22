import tkinter as tk
from tkinter import font

def show_fonts():
    root = tk.Tk()
    root.title("Font Preview")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    fonts = ['Terminal', 'Courier', 'Arial', 'Arial Black', 'Javanese Text', 'Lucida Sans Unicode', 'Mongolian Baiti',
             'Myanmar Text', 'Palatino Linotype', 'Tahoma', 'Bodoni MT', 'Bodoni MT Black', 'Bookman Old Style', 'Copperplate Gothic Bold', 'Copperplate Gothic Light', 'Century Gothic', 'Modern No. 20'
    ]

    for f in fonts:
        label = tk.Label(frame, text=f"This is {f}", font=(f, 16))
        label.pack(pady=5)

    root.mainloop()

show_fonts()
