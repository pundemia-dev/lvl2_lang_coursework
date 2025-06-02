import customtkinter as ctk
from core.ship_container import ShipContainer
from core.bot import Bot


class Battleship(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.botgrid = ShipContainer(self, hidden=True)
        self.botgrid.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.usergrid = ShipContainer(self)
        self.usergrid.grid(row=1, column=0, padx=10, pady=10, sticky="nsew" )
        self.bot = Bot(self.botgrid.ship_set, self.botgrid.ship_unset_func, self.botgrid.check_alive, self.botgrid.bombs_enable, self.usergrid.bomb_action)

    def play_game(self):
        self.usergrid.

        
