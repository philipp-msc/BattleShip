from random import randint, choice
import time

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы доски!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, orientation):
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            current_x = self.bow.x
            current_y = self.bow.y

            if self.orientation == 0:
                current_x += i

            elif self.orientation == 1:
                current_y += i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots

    def is_shot(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hide_board=False, board_size=6):
        self.board_size = board_size
        self.hide_board = hide_board
        self.shot_count = 0
        self.field = [["O"] * board_size for _ in range(board_size)]
        self.occupied = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.occupied:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.occupied.append(d)

        self.ships.append(ship)
        self.outline(ship)

    def outline(self, ship, verb=False):
        nearby = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2)]
        for d in ship.dots:
            for dx, dy in nearby:
                current = Dot(d.x + dx, d.y + dy)
                if not (self.out(current)) and current not in self.occupied:
                    if verb:
                        self.field[current.x][current.y] = "."
                    self.occupied.append(current)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hide_board:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.board_size) and (0 <= d.y < self.board_size))

    def shot(self, d):  #вопрос с доп ходом после потопления
        if self.out(d):
            raise BoardOutException()

        if d in self.occupied:
            raise BoardUsedException()

        self.occupied.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"

                if ship.lives == 0:
                    self.shot_count += 1
                    self.outline(ship, verb=True)
                    print("Убит!")
                    return True
                else:
                    print("Ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.occupied = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def __init__(self, board, enemy):
        super().__init__(board, enemy)
        self.last_hit = None

    def ask(self):
        if self.last_hit is None:
            x = randint(0, self.board.board_size - 1)
            y = randint(0, self.board.board_size - 1)
        else:
            possible_moves = self.get_connected_positions(self.last_hit)
            x, y = choice(possible_moves)

        d = Dot(x, y)
        print(f"Ход компьютера: {x + 1} {y + 1}")
        return d

    def get_connected_positions(self, center):
        connected_positions = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x, new_y = center.x + dx, center.y + dy
                if 0 <= new_x < self.board.size and 0 <= new_y < self.board.size:
                    connected_positions.append((new_x, new_y))
        return connected_positions

class User(Player):
    def ask(self):
        while True:
            try:
                cords = input("Ваш ход: ").split()

                if len(cords) != 2:
                    raise ValueError(" Введите 2 координаты! ")

                x, y = map(int, cords)

                if not (1 <= x <= self.board.board_size) or not (1 <= y <= self.board.board_size):
                    raise ValueError(" Введите числа! ")

                return Dot(x - 1, y - 1)

            except ValueError as e:
                print(f"Ошибка: ")

class Game:
    def __init__(self, size = 6):
        self.size = size
        player_board = self.random_board()
        computer_board = self.random_board()
        computer_board.hide_board = True
        self.ai = AI(computer_board, player_board)
        self.user = User(player_board, computer_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(board_size=self.size)
        attempts = 0

        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                orientation = randint(0,1)
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, orientation)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board


    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.user.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*20)
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("-"*20)
                print("Ходит компьютер!")
                time.sleep(3)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.shot_count == 7:
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.user.board.shot_count == 7:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()