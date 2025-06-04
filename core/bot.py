from contextlib import nullcontext
from random import randint, choice 
from core.ship_container import ShipType
from enum import Enum
from icecream import ic


class Bomb(int, Enum):
    miss = -1
    hit = 0
    killed = 1
    

class BotState(Enum):
    fill = "fill"
    find_way = "find_way"
    kill = "kill"
    another_way = "another_way"
    panic = "panic"

class Bot:
    def __init__(self, 
                 self_check_alive, 
                 self_bombs_enable, 
                 user_bomb_action):
        ic.configureOutput(prefix="Bot | ")
        self.check_alive = self_check_alive 
        self.bombs_enable = self_bombs_enable 
        self.user_bomb_action = user_bomb_action

        self.map = list()
        self.black_or_white = None
        self.state = None
        self.bombed_ship = []
        self.ship_counter = {ship.cells_count: ship.count for ship in ShipType if ship is not ShipType.PATROL_BOAT}
        
        self.reload()
    def constrain(self, unit, lower_order, upper_order):
        unit = unit if unit >= lower_order else lower_order 
        unit = unit if unit <= upper_order else upper_order
        return unit

    def reload(self):
        self.map = [[True for _ in range(10)] for _ in range(10)]
        black_or_white_flag = randint(0, 1)
        self.black_or_white = [[True if ((x + y) % 2) is black_or_white_flag else False for x in range(10)] for y in range(10)]
        ic(self.black_or_white)
        # for row in self.black_or_white:
            # print(row)
        
        self.bombed_ship = []
        self.state = BotState.fill

    def bomb_request(self, prefire):
        ic.enable()
        fire = ic(choice(ic(prefire)))
        self.map[fire[1]][fire[0]] = False
        return (ic(self.user_bomb_action(fire)), fire)

    def bomb_action(self):
        ic.enable()
        ic(self.map)
        prefire = []
        result = None
        match self.state:
            case BotState.fill:
                intersections = [[all(units) for units in zip(rows[0], rows[1])] for rows in zip(self.map, self.black_or_white)]
                ic(intersections)
                for y, row in enumerate(intersections):
                    for x, unit in enumerate(row):
                        if unit:
                            prefire.append((x, y))
                ic(prefire)
                if len(prefire) > 0:
                    result, fire = self.bomb_request(prefire)
                    match result:
                        case Bomb.miss:
                            ic()
                        case Bomb.hit:
                            ic()
                            self.bombed_ship.append(fire)
                            self.state = BotState.find_way
                        case Bomb.killed:
                            self.bombed_ship.append(fire)
                            fire_range = []
                            for ind in range(2):
                                fire_range.append([self.constrain(fire[ind]-1, 0, 10), self.constrain(fire[ind]+2, 0, 10)])
                            for y in range(fire_range[1][0] , fire_range[1][1]):
                                for x in range(fire_range[0][0], fire_range[0][1]):
                                    self.map[y][x] = False
                            # self.ship_counter[len(self.bombed_ship)] -= 1
                            if sum(self.ship_counter.values()) == 0:
                                self.state = BotState.panic
                            else:
                                self.state = BotState.fill
                            self.bombed_ship = []

            case BotState.find_way:
                for axis in range(2):
                    for offset in range(-1, 2, 2):
                        temp = list(self.bombed_ship[0])
                        temp[axis] += offset
                        temp[axis] = self.constrain(temp[axis], 0, 9)
                        if self.map[temp[1]][temp[0]]:
                            prefire.append(temp)
                            
                if len(prefire) > 0:
                    result, fire = self.bomb_request(prefire)
                    match result:
                        case Bomb.miss:
                            ic()
                            self.map[fire[1]][fire[0]] = False
                        case Bomb.hit:
                            self.bombed_ship.append(fire)
                            self.state = BotState.kill
                        case Bomb.killed:
                            self.bombed_ship.append(fire)
                            for pos in self.bombed_ship:
                                fire_range = []
                                for ind in range(2):
                                    ic(pos)
                                    ic(pos[ind]-1)
                                    fire_range.append([self.constrain(pos[ind]-1, 0, 10), self.constrain(pos[ind]+2, 0, 10)])
                                for y in range(fire_range[1][0] , fire_range[1][1]):
                                    for x in range(fire_range[0][0], fire_range[0][1]):
                                        self.map[y][x] = False
                            self.ship_counter[len(self.bombed_ship)] -= 1
                            if sum(self.ship_counter.values()) == 0:
                                self.state = BotState.panic
                            else:
                                self.state = BotState.fill
                            self.bombed_ship = []
                            # self.state = BotState.fill

            case BotState.kill:
                for axis in range(2):
                    if self.bombed_ship[0][axis] == self.bombed_ship[-1][axis]:
                        offset = self.bombed_ship[-1][not axis] - self.bombed_ship[0][not axis]
                        offset = ic(offset // abs(offset))
                        temp = list(self.bombed_ship[-1])
                        temp[not axis] += offset
                        if temp[not axis] != self.constrain(temp[not axis],0,9) or not self.map[temp[1]][temp[0]]:
                            self.state = BotState.another_way
                            self.bomb_action()
                            return
                        ic(temp)
                        if self.map[temp[1]][temp[0]]:
                            prefire.append(temp)
                if len(prefire) > 0:
                    result, fire = self.bomb_request(prefire)
                    match result:
                        case Bomb.miss:
                            self.map[fire[1]][fire[0]] = False
                            self.state = BotState.another_way
                        case Bomb.hit:
                            self.bombed_ship.append(fire)
                            self.state = BotState.kill
                        case Bomb.killed:
                            self.bombed_ship.append(fire)
                            ic(self.bombed_ship)
                            for pos in self.bombed_ship:
                                fire_range = []
                                for ind in range(2):
                                    fire_range.append([self.constrain(pos[ind]-1,0, 10), self.constrain(pos[ind]+2,0, 10)])
                                ic(fire_range)
                                for y in range(fire_range[1][0] , fire_range[1][1]):
                                    for x in range(fire_range[0][0], fire_range[0][1]):
                                        self.map[y][x] = False
                            self.ship_counter[len(self.bombed_ship)] -= 1
                            if sum(self.ship_counter.values()) == 0:
                                self.state = BotState.panic
                            else:
                                self.state = BotState.fill
                            self.bombed_ship = []
                            # self.state = BotState.fill
                            
            case BotState.another_way:
                for axis in range(2):
                    if self.bombed_ship[0][axis] == self.bombed_ship[-1][axis]:
                        offset = self.bombed_ship[0][not axis] - self.bombed_ship[-1][not axis]
                        offset = ic(offset // abs(offset))
                        temp = list(self.bombed_ship[0])
                        temp[not axis] += offset
                        if self.map[temp[1]][temp[0]]:
                            prefire.append(temp)
                if len(prefire) > 0:
                    result, fire = self.bomb_request(prefire)
                    match result:
                        case Bomb.miss:
                            self.map[fire[1]][fire[0]] = False
                            self.state = BotState.fill
                        case Bomb.hit:
                            self.bombed_ship.append(fire)
                            self.state = BotState.kill
                        case Bomb.killed:
                            self.bombed_ship.append(fire)
                            ic(self.bombed_ship)
                            for pos in self.bombed_ship:
                                fire_range = []
                                for ind in range(2):
                                    fire_range.append([self.constrain(pos[ind]-1, 0, 10), self.constrain(pos[ind]+2,0,10)])
                                for y in range(fire_range[1][0] , fire_range[1][1]):
                                    for x in range(fire_range[0][0], fire_range[0][1]):
                                        self.map[y][x] = False
                            self.ship_counter[len(self.bombed_ship)] -= 1
                            if sum(self.ship_counter.values()) == 0:
                                self.state = BotState.panic
                            else:
                                self.state = BotState.fill
                            self.bombed_ship = []
                            # self.state = BotState.fill
            
            case BotState.panic:
                for y, row in enumerate(self.map):
                    for x, unit in enumerate(row):
                        if unit:
                            prefire.append((x, y))
                if len(prefire) > 0:
                    result, fire = self.bomb_request(prefire)
                    self.map[fire[1]][fire[0]] = False
                    if result is Bomb.killed:
                        fire_range = []
                        for ind in range(2):
                            fire_range.append([self.constrain(fire[ind]-1, 0, 10), self.constrain(fire[ind]+2,0,10)])
                        for y in range(fire_range[1][0] , fire_range[1][1]):
                            for x in range(fire_range[0][0], fire_range[0][1]):
                                self.map[y][x] = False

        return result
                
