import pickle
import socket
from enum import Enum
import customtkinter as ctk
from icecream import ic


class SocketState(str, Enum):
    host = "host"
    client = "client"


class Socket(ctk.CTkFrame):
    def __init__(self, master, self_check_alive, user_bomb_action):
        super().__init__(master)
        self.check_alive = self_check_alive  # Проверка жизни соединения
        self.user_bomb_action = user_bomb_action  # Приём выстрела от оппонента

        self.host = '127.0.0.1'
        self.port = 12345
        self.socket = None
        self.connection = None
        self.state = SocketState.host

    def set_state(self, state):
        self.state = state

    def create_lobby(self):
        """Создание лобби (сервер)"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print("Ожидание подключения...")
        self.connection, addr = self.socket.accept()
        ic(self.connection)
        print(f"Подключено: {addr}")
        self.state = SocketState.host

    def connect_lobby(self):
        """Подключение к лобби (клиент)"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            self.connection = self.socket
            self.state = SocketState.client
            print("Подключено к серверу")
        except Exception as e:
            print(f"Ошибка подключения: {e}")

    def reload(self):
        """Перезапуск сокета при переподключении или рестарте игры"""
        if self.connection:
            self.connection.close()
        if self.socket:
            self.socket.close()
        self.connection = None
        self.socket = None

    def send_with_ack(self, data):
        """
        Отправляет данные и ожидает подтверждение (ACK).
        :param data: данные для отправки (уже сериализованные, например bytes)
        """
        while True:
            try:
                self.connection.sendall(pickle.dumps(data))
                ack = self.connection.recv(1024)
                if ack == b"ACK":
                    print("Подтверждение получения получено.")
                    return
            except Exception as e:
                print(f"Ошибка при отправке: {e}")
                continue

    def receive_with_ack(self):
        """
        Ожидает данные в цикле. После получения отправляет ACK.
        :return: полученные данные (bytes)
        """
        while True:
            try:
                data = self.connection.recv(4096)
                if data:
                    self.connection.sendall(b"ACK")
                    return pickle.loads(data)
            except Exception as e:
                print(f"Ошибка при приёме: {e}")
                continue
    
    def set_turn(self, turn:bool):
        if self.state == SocketState.host:
            try:
                self.send_with_ack(not turn)
                print(f"Отправлена играющая сторона: {"host" if turn else "client"}")
                return turn
            except Exception as e:
                print(f"Ошибка при отправке играющей стороны хода: {e}")

        else: # client
            try:
                data = self.receive_with_ack()
                print(f"Принята играющая сторона: {"host" if data else "client"}")
                return data
            except Exception as e:
                print(f"Ошибка при приеме играющей стороны хода: {e}")
             

    def bomb_action(self):
        """
        Получает координаты выстрела от соперника.
        После обработки, возвращает управление (например, для передачи хода).
        """
        try:
            print("Ожидание хода от соперника...")
            data = self.receive_with_ack()  # Ждём сообщение с подтверждением
            print(f"Получен ход от соперника: {data}")

            # Вызываем обработчик хода
            return self.user_bomb_action(data)

        except Exception as e:
            print(f"Ошибка при ожидании хода: {e}")

    def callback_send(self, pos):
        """Отправляет координаты выстрела на сторону соперника."""
        try:
            self.send_with_ack(pos)
            print(f"Отправлен ход: {pos}")
        except Exception as e:
            print(f"Ошибка при отправке данных: {e}")

    def swap_map(self, ships_set, ships):
        """
        Обменивается картой кораблей с соперником с подтверждением получения.
        :param ship_set_func: функция установки кораблей на карте
        :param ships: собственные корабли (список списков координат)
        """

        try:
            # --- Подготовка ---
            # own_data = pickle.dumps({name: [ship for ship in ship_box] for name, ship_box in ships.items()})#.encode()

            if self.state == SocketState.host:
                # ХОСТ: ожидает корабли клиента -> ставит -> отправляет свои
                print("Ожидание кораблей от клиента...")
                enemy_ships = self.receive_with_ack()
                print("Корабли противника получены.")

                # <<< ТУТ МЕСТО ДЛЯ ТВОЕЙ ЛОГИКИ >>> #
                ships_set(enemy_ships)

                print("Отправка своих кораблей клиенту...")
                self.send_with_ack(ships)


            elif self.state == SocketState.client:
                # КЛИЕНТ: отправляет свои корабли -> получает от хоста -> ставит
                print("Отправка своих кораблей хосту...")
                self.send_with_ack(ships)

                print("Ожидание кораблей от хоста...")
                enemy_ships = self.receive_with_ack()
                print("Корабли противника получены.")

                # <<< ТУТ МЕСТО ДЛЯ ТВОЕЙ ЛОГИКИ >>> #
                ships_set(enemy_ships)

        except Exception as e:
            print(f"Ошибка при обмене картами: {e}")

