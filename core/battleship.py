from random import randint

import customtkinter as ctk
from icecream import ic

from core.bot import Bomb, Bot
from core.colors import Color
from core.ship_container import ShipContainer
from core.socket import Socket
from core.spinbox import Spinbox
from core.tools import start_timer


class Settings(ctk.CTkToplevel):
    def __init__(self, game_run, default_bots_delay, bots_delay, set_bots_delay_func):
        super().__init__()
        self.title("Морской бой: настройки")
        self.default_bots_delay = default_bots_delay
        self.set_bots_delay_func = set_bots_delay_func

        lr_pad = 20
        ud_pad = 25
        between_pad = 5
        block_pad = 10

        self.socket_label = ctk.CTkLabel(self, text="Socket")
        self.socket_label.grid(row=0, column=0, padx=(lr_pad, between_pad), pady=(ud_pad, block_pad), sticky="nsew")
        self.socket_input = ctk.CTkEntry(self, state="disabled" if game_run else "normal")
        self.socket_input.grid(row=0, column=1, padx=between_pad, pady=(ud_pad, block_pad), sticky="nsew")
        self.socket_reload = ctk.CTkButton(self, text=" ", width=30, height=30, command=print, state="disabled" if game_run else "normal")
        self.socket_reload.grid(row=0, column=2, padx=(between_pad, lr_pad), pady=(ud_pad, block_pad), sticky="nsew")

        self.bot_delay_label = ctk.CTkLabel(self, text="Bot delay")
        self.bot_delay_label.grid(row=1, column=0, padx=(lr_pad, between_pad), pady=block_pad, sticky="nsew")
        self.bot_delay_spinbox = Spinbox(self, width=150, step_size=0.1, command=self.set_bots_delay)
        self.bot_delay_spinbox.set(bots_delay)
        self.bot_delay_spinbox.grid(row=1, column=1, padx=between_pad, pady=block_pad, sticky="nsew")
        self.bot_delay_reload = ctk.CTkButton(self, text=" ", width=30, height=30, command=self.reload_bots_delay)
        self.bot_delay_reload.grid(row=1, column=2, padx=(between_pad, lr_pad), pady=block_pad, sticky="nsew")

    def reload_bots_delay(self):
        self.set_bots_delay_func(self.default_bots_delay)
        self.bot_delay_spinbox.set(self.default_bots_delay)

    def set_bots_delay(self):
        self.set_bots_delay_func(self.bot_delay_spinbox.get())
        

class Battleship(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        
        # ----- Grids ----- #
        self.users = []
        botgrid = ShipContainer(self, reload_callback=self.reload, iter_callback=self.play_iter, hidden=True)
        botgrid.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=5)
        self.users.append(botgrid)
        usergrid = ShipContainer(self, reload_callback=self.reload)
        usergrid.grid(row=2, column=0, padx=10, pady=10, sticky="nsew", columnspan=5)
        self.users.append(usergrid)
        
        # ---- Rivals ---- #
        self.rival = []
        bot = Bot(
            self.users[0].check_alive,
            self.users[1].bomb_action
        )
        self.rival.append(bot)
        socket = Socket(
            self,
            self.users[0].check_alive,
            self.users[1].bomb_action
        )
        self.rival.append(socket)
        
        # --- Control --- #
        self.label = ctk.CTkLabel(self, text="Let's play", fg_color="transparent", corner_radius=5)
        self.label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.rival_selector = ctk.CTkOptionMenu(self, values=["Bot", "User"] ,width=100, command=self.change_rival)
        self.rival_selector.grid(row=1, column=1, padx=(10, 5), pady=10, sticky="nsew")
        self.create_lobby = ctk.CTkButton(self, text="Create lobby", command=self.rival[1].create_lobby)
        self.connect_lobby = ctk.CTkButton(self, text="Connect lobby", command=self.rival[1].connect_lobby)
            
        self.settings = ctk.CTkButton(self, text=" ", fg_color=Color.orange, hover_color=Color.orange_dark, width=30, height=30, command=self.settings_callback)
        self.settings.grid(row=1, column=4, padx=(5, 25), pady=10, sticky="nsew")
            
        # -- Variables -- #
        self.game_run = False
        self.default_bots_delay = 2
        self.bots_delay = self.default_bots_delay
        self.selected_rival = 0
        self.turn = True
        self.last_res = Bomb.miss

    def change_rival(self, value):
        match value:
            case "Bot":
                self.selected_rival = 0
                self.show_rival_control(False)
            case "User":
                self.selected_rival = 1 
                self.show_rival_control(True)
                
        self.selected_rival = 0 if value == "Bot" else 1
        
    def show_rival_control(self, enable:bool):
        if enable:
            self.create_lobby.grid(row=1, column=2, padx=5, pady=10, sticky="nsew")
            self.connect_lobby.grid(row=1, column=3, padx=5, pady=10, sticky="nsew")
        else:
            self.create_lobby.grid_forget()
            self.connect_lobby.grid_forget()

    def set_bots_delay(self, value):
        self.bots_delay = value

    def settings_callback(self):
        Settings(self.game_run, self.default_bots_delay, self.bots_delay, self.set_bots_delay)

    def play_game(self):
        self.last_res = Bomb.miss
        if not self.selected_rival:
            self.users[0].load_random_map()
            self.turn = randint(0, 1)
        else:
            self.rival[1].swap_map(self.users[0].set_ships, self.users[1].get_ships())
            self.turn = self.rival[1].set_turn(randint(0, 1))
            
        
        self.rival_selector.configure(state="disabled")
        self.show_rival_control(False)
        self.game_run = True
        self.play_iter()

    def reload(self):
        for user in self.users:
            user.reload()
        for rival in self.rivals:
            rival.reload()
        self.label.configure(text="Let's play", fg_color="transparent")
        self.rival_selector.configure(state="normal")
        self.show_rival_control(self.selected_rival)
        self.game_run = False

    def play_iter(self, last_res=None, last_pos=None):
        ic.disable()
        ic(last_res)
        if all([user.check_alive() for user in self.users]):
            if last_res is not None:
                self.last_res = last_res
            if last_res is not None:
                if self.selected_rival:
                    self.rival[1].callback_send(last_pos)
            if self.last_res == Bomb.miss:
                self.turn = not self.turn
            self.label.configure(text="Your turn" if self.turn else "Bot's turn", fg_color=Color.green if self.turn else Color.red)
            self.users[0].bombs_enable(self.turn)
            if not self.turn:
                self.last_res = ic(self.rival[self.selected_rival].bomb_action())
                if all([user.check_alive() for user in self.users]):
                    start_timer(self.play_iter, 0 if self.selected_rival else self.bots_delay)
                else:
                    self.users[1].win_window()
        else:
            if last_res is not None:
                if self.selected_rival:
                    self.rival[1].callback_send(last_pos)
            self.users[1].win_window()
