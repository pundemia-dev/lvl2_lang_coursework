import customtkinter as ctk 
from enum import Enum
from core.shiptype import ShipType
from core.colors import Color


class CellState(Enum):
    alive = 1
    cell = 0
    dead = -1

class Cell(ctk.CTkButton):
    def __init__(self, master, position, ship_mapping_func, ship_set_func):
        args = {
            "width": 30,
            "height": 30,
            "text": "",
            "fg_color": Color.gray,
            "hover_color": Color.green_dark,
            "command": self.button_command
        }
        super().__init__(master, **args)
        self.state = None
        self.position = position
        self.ship_set_func = ship_set_func
        self.ship_unset_func = None
        self.ship_mapping_func = ship_mapping_func
        self.last_text = ""
        self.default_color = Color.gray
   
    def is_me(self, position):
        return position is self.position

    def set_ship_unset_func(self, func):
        self.ship_unset_func = func

    def button_command(self):
        match self.state: 
            case None:
                self.ship_set_func(self.position)
            case CellState.alive:
                self.ship_unset_func()

    def set_state(self, state):#state: CellState):
        self.state = state
        match state:
            case CellState.alive:
                self.configure(fg_color=Color.green, state="normal")
                self.default_color = Color.green
            case CellState.cell:
                self.configure(fg_color=Color.gray, state="disabled")
                self.default_color = Color.gray
            case CellState.dead:
                self.configure(fg_color=Color.red, state="normal")
                self.default_color = Color.red
            case None:
                self.configure(fg_color=Color.gray, state="normal")
                self.default_color = Color.gray

    def ship_mapping(self, enable: bool):
        if enable:
            self.bind("<Enter>", lambda event: self.ship_mapping_func(self.position, True))
            self.bind("<Leave>", lambda event: self.ship_mapping_func(self.position, False))
            self.configure(state="normal")
        else:
            self.unbind_all()
            self.configure(state="disabled")

    def ship_on_hover(self, enable: bool, flag=True):
        if enable:
            self.configure(fg_color=Color.green if flag and self.state is None else Color.red)
        else:
            self.configure(fg_color=self.default_color)

    def bomb_on_hover(self, enable: bool):
        if enable:
            self.last_text = self.cget("text")
            self.configure(text=" ")
        else:
            self.configure(text=self.last_text)

    def bomb_action(self):
        if self.state is CellState.alive:
            self.configure(text="󱥸 ")
            self.set_state(CellState.dead)
        else:
            self.configure(text=" ")


class ShipsSelector(ctk.CTkFrame):
    def __init__(self, master, select_ship_func):
        super().__init__(master)
        self.grid_rowconfigure(9, weight=1) 
        self.buttons = {ship.type: None for ship in ShipType}

        for row, ship in enumerate(ShipType):
            button = ctk.CTkButton(self, text=f"{ship.type} {"*"*ship.cells_count}", fg_color=Color.purple, hover_color=Color.purple_dark, command=lambda shiptype=ship: select_ship_func(shiptype))
            button.grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
            self.buttons[ship.type] = button

    def enable_selector(self, shiptype, enable:bool):
        self.buttons[shiptype].configure(state="normal" if enable else "disabled")

class Ship:
    def __init__(self, ship_type, ship_unset_func):
        self.ship_type = ship_type
        self.cells_list = list()
        self.positions = list()
        self.alive = True
        self.ship_unset_func = ship_unset_func

    def add_cell(self, cell, position):
        if len(self.cells_list) < self.ship_type.cells_count:
            self.cells_list.append(cell)
            self.positions.append(position)
            cell.set_state(CellState.alive)
            cell.set_ship_unset_func(self.unset)
        else:
            pass # logs

    def unset(self):
        self.ship_unset_func(self.positions, self.ship_type)

    def is_me(self, position):
        return any([position is pos for pos in self.positions])

    def check_alive(self) -> bool:
        return self.alive

class ShipContainer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.cells_frame = ctk.CTkFrame(self)
        self.cells_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.ship_selector = ShipsSelector(self, self.set_active_shiptype_selector)
        self.ship_selector.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.cell_list = []
        self.play_button = ctk.CTkButton(self.ship_selector, text="Play", fg_color=Color.aqua, hover_color=Color.aqua_dark, command=self.play_game)

        for y in range(10):
            if y >= len(self.cell_list):
                self.cell_list.append([])
            for x in range(10):
                cell = Cell(self.cells_frame, (x, y), self.ship_on_hover, self.ship_set)
                cell.grid(row=y, column=x, padx=5, pady=5, sticky="nsew")
                self.cell_list[y].append(cell)

        self.alive = True
        self.ships_counts = {ship.name: ship.count for ship in ShipType}
        self.ships = {ship.name: [] for ship in ShipType}
        self.active_shiptype_selector = None
        self.selector_rotation = True
        self.selector_position = ()
        self.reload()

    def toggle_selector_rotation(self, _):
        self.ship_on_hover(self.selector_position, False)
        self.selector_rotation = not self.selector_rotation
        self.ship_on_hover(self.selector_position, True)

    def set_active_shiptype_selector(self, shiptype):
        self.active_shiptype_selector = shiptype

    def enable_ship_selector(self, enable: bool):
        for row in self.cell_list:
            for cell in row:
                cell.ship_mapping(enable)
        # list(map(lambda row: map(lambda cell: cell.ship_mapping(enable), row), self.cell_list))
        if enable:
            self.master.master.bind("<BackSpace>", self.toggle_selector_rotation)
        else:
            self.unbind_all()

    def ship_on_hover(self, position, enable:bool):
        self.selector_position = position
        center = self.active_shiptype_selector.cells_count // 2 
        begin_pos = position[self.selector_rotation] - center
        end_pos = begin_pos + self.active_shiptype_selector.cells_count
        positions = [(position[0], p) if self.selector_rotation else (p, position[1]) for p in range(begin_pos, end_pos)]
        filtered_positions = [pos for pos in positions if all(0 <= unit < 10 for unit in pos)]
        flag = len(positions) is len(filtered_positions) and self.ships_counts[self.active_shiptype_selector.name]
        list(map(lambda pos: self.cell_list[pos[1]][pos[0]].ship_on_hover(enable, flag), filtered_positions))

    def ship_set(self, position):
        center = self.active_shiptype_selector.cells_count // 2 
        begin_pos = position[self.selector_rotation] - center
        end_pos = begin_pos + self.active_shiptype_selector.cells_count
        positions = [(position[0], p) if self.selector_rotation else (p, position[1]) for p in range(begin_pos, end_pos)]
        filtered_positions = [pos for pos in positions if all(0 <= unit < 10 for unit in pos)]
        flag = len(positions) is len(filtered_positions)
        
        if flag and self.ships_counts[self.active_shiptype_selector.name]:
            ship = Ship(self.active_shiptype_selector, self.ship_unset_func)
            self.ships[self.active_shiptype_selector.name].append(ship)
            self.ships_counts[self.active_shiptype_selector.name] -= 1
            for pos in positions:
                for x in range(pos[0]-1, pos[0]+2):
                    for y in range(pos[1]-1, pos[1]+2):
                        if x in range(10) and y in range(10):
                            self.cell_list[y][x].set_state(CellState.cell)
            for pos in positions:
                self.ships[self.active_shiptype_selector.name][-1].add_cell(self.cell_list[pos[1]][pos[0]], pos)

            if not sum(self.ships_counts.values()):
                self.play_button.grid(row=10, column=0, padx=5, pady=5, sticky="sew")

    def ship_unset_func(self, positions, shiptype):
        for pos in positions:
            for x in range(pos[0]-1, pos[0]+2):
                for y in range(pos[1]-1, pos[1]+2):
                    if x in range(10) and y in range(10):
                        self.cell_list[y][x].set_state(None)
        self.ships[shiptype.name] = [ship for ship in self.ships[shiptype.name] if ship.is_me(positions[0])]
        self.ships_counts[shiptype.name] += 1
        if sum(self.ships_counts.values()):
            self.play_button.grid_forget()

    def bomb_action(self, position):
        for y in range(position[1]):
            self.cell_list[y][position[0]].bomb_on_hover(True)
            [x for x in range(10000)] 
            self.cell_list[y][position[0]].bomb_on_hover(False)

        self.cell_list[position[1]][position[0]].bomb_action()

    def play_game(self):
        

    def reload(self):
        self.enable_ship_selector(True)

