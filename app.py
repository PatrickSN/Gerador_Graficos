from gui.main_window import MainWindow
import customtkinter as ctk

if __name__ == "__main__":
    ctk.set_appearance_mode("Systen")
    ctk.set_default_color_theme("green")

    app = MainWindow()
    app.mainloop()

