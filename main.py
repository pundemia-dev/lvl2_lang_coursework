import customtkinter as ctk

from core.battleship import Battleship

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Морской бой")
        self.geometry(f"{603}x{910}")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.battleship = Battleship(master=self)
        self.battleship.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()
