import customtkinter as ctk 
from random import randint
from icecream import ic

from core.bot import Bot, Bomb
from core.ship_container import ShipContainer


class Battleship(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.users = []
        botgrid = ShipContainer(self, iter_callback=self.play_iter, hidden=True)
        botgrid.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        botgrid.bombs_enable(False)
        self.users.append(botgrid)
        self.label = ctk.CTkLabel(self, text="Let's play")
        self.label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        usergrid = ShipContainer(self)
        usergrid.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.users.append(usergrid)
        self.bot = Bot(
            self.users[0].check_alive,
            self.users[0].bombs_enable,
            self.users[1].bomb_action,
        )
        self.turn = True
        self.last_res = Bomb.miss
        self.master.bind("<Control-a>", lambda _: self.toggle_turn())
        self.users[1].win_window()

    def play_game(self):
        self.users[0].load_random_map()
        self.turn = 0# randint(0, 1)
        self.play_iter()

    def toggle_turn(self):
        self.turn = self.turn
        self.play_iter()

    def play_iter(self, last_res=None):
        ic(last_res)
        if all([user.check_alive() for user in self.users]):
            if last_res is not None:
                self.last_res = last_res
            if self.last_res == Bomb.miss:
                self.turn = not self.turn
            self.label.configure(text="Your turn" if self.turn else "Bot's turn")
            self.users[0].bombs_enable(self.turn)
            if not self.turn:
                self.last_res = self.bot.bomb_action()
                self.play_iter()
        else:
            
            self.users[1].win_window()
