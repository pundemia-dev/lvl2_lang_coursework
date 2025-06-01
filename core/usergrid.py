import customtkinter as ctk 
from enum import Enum


class CellState(Enum):
    alive = 1
    cell = 0
    dead = -1

class Cell(ctk.CTkButton):
    def __init__(self, master, position, ship_mapping_func):
        args = {
            "width": 30,
            "height": 30,
            "text": "",
            "fg_color": "#504945",
            "command": self.
        }
        super().__init__(master, **args)
        self.state = None
        self.position = position
        self.ship_mapping_func = ship_mapping_func
        self.last_text

    def set_state(self, state: CellState):
        self.state = state
        match state:
            case CellState.alive:
                self.configure(fg_color="green")
            case CellState.cell:
                self.configure(fg_color="gray")
            case CellState.dead:
                self.configure(fg_color="red")

    def ship_mapping(self, enable: bool):
        if enable:
            self.bind("<Enter>", lambda event: self.ship_mapping_func(self.position, True))
            self.bind("<Leave>", lambda event: self.ship_mapping_func(self.position, False))
            self.configure(state="normal")
        else:
            self.unbind_all()
            self.configure(state="disabled")

    def ship_on_hover(self):
        if self.state is None:
            self.configure(fg_color="green")
        else:
            self.configure(fg_color="red")

    def bomb_on_hover(self, enable: bool):
        if enable:
            self.last_text = self.cget("text")
            self.configure(text=" ")
        else:
            self.configure(text=self.last_text)

    def bomb_action(self):
        match self.state:
            case CellState.alive:
                self.configure(fg_color="red", text=" ")


class ShipsSelector(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # self.


class Usergrid(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.cell_list = []

        for y in range(10):
            if y >= len(self.cell_list):
                self.cell_list.append([])
            for x in range(10):
                cell = Cell(self)
                cell.grid(row=y, column=x, padx=5, pady=5, sticky="nsew")
                self.cell_list[y].append(cell)


    def 

        
        
        
