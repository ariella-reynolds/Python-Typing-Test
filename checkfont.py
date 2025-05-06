import tkinter as tk
import tkinter.font as tkFont

def show_fonts():
    root = tk.Tk()
    root.title("Available Fonts")

    canvas = tk.Canvas(root, width=800, height=600)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)

    canvas.configure(yscrollcommand=scrollbar.set)

    for font_name in sorted(tkFont.families()):
        try:
            label = tk.Label(frame, text=f"{font_name} - The quick brown fox jumps over the lazy dog", font=(font_name, 14))
            label.pack(anchor='w')
        except tk.TclError:
            pass  # Skip fonts that can't be rendered

    frame.update_idletasks()
    canvas.create_window((0, 0), window=frame, anchor='nw')
    canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

show_fonts()