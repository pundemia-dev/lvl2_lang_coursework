import customtkinter as ctk 


class Cell(ctk.CTkButton):
    def __init__(self, master):
        args = {
            "width": 30,
            "height": 30,
            "text": "",
            "fg_color": "#504945",
            "hover_color": "#CC241D",
            "command": self.crater_hover
        }
        super().__init__(master, **args)

        # self.type = 

        self.bind("<Enter>", lambda event: self.bomb_hover(enable=True) if self.cget("state")=="normal" else None)
        self.bind("<Leave>", lambda event: self.bomb_hover(enable=False) if self.cget("state")=="normal" else None)

    def bomb_hover(self, enable: bool):
        self.configure(text=" " if enable else "")

    def crater_hover(self):
        self.configure(text="", state="disabled")


class Botgrid(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.ship_imgs = []
        
        self.cell_list = []

        for y in range(10):
            if y >= len(self.cell_list):
                self.cell_list.append([])
            for x in range(10):
                cell = Cell(self)
                cell.grid(row=y, column=x, padx=5, pady=5, sticky="nsew")
                self.cell_list[y].append(cell)

        self.load_map()

    def load_map(self):
        self.ship_imgs

