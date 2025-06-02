import customtkinter as ctk
from core.botgrid import Botgrid
from core.usergrid import ShipContainer


class Battleship(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.botgrid = Botgrid(master=self)
        self.botgrid.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.usergrid = ShipContainer(self)
        self.usergrid.grid(row=1, column=0, padx=10, pady=10, sticky="nsew" )
        
