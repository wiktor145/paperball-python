import random
import sys
import time
from enum import Enum
import pygame
import pygameMenu
from pygameMenu.locals import *
from pygameMenu import fonts

# screen resolution - must be even
H_SIZE = 800
W_SIZE = 1100
SCREEN_SIZE = 800

# colours
LIGHT_GRAY = (240, 240, 240)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 64, 0)


class Opponent(Enum):
    CPU = 1
    HUMAN = 2


class CPULevel(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class Turn(Enum):
    PLAYER1 = 1
    PLAYER2 = 2


def menu_background(surface):
    surface.fill(WHITE)


help_background_image = pygame.image.load("./helpbackground.png")


def help_background(surface):
    surface.blit(help_background_image, (100, 0))


# class, which holds statistics about current game
# and also shows statistics on screen
class Statistics(object):
    # type of opponent # level of CPU
    def __init__(self, player2, cpu_level, player1_color, player2_color):
        # beginning of game
        self.timer_start = time.time()
        # actual time
        self.timer_actual = time.time()

        # players moves
        self.player1_moves = 0
        self.player2_moves = 0

        # opponent
        self.player2 = player2
        self.cpu_level = cpu_level

        # who's turn is now
        self.turn = Turn.PLAYER1

        # player colors
        self.player1_color = player1_color
        self.player2_color = player2_color

        # fonts
        self.font_30 = pygame.font.Font("font.ttf", 30)
        self.font_12 = pygame.font.Font("font.ttf", 12)
        self.font_24 = pygame.font.Font("font.ttf", 24)

    def player1_add_move(self):
        self.player1_moves += 1

    def player2_add_move(self):
        self.player2_moves += 1

    def change_player(self):
        if self.turn == Turn.PLAYER1:
            self.turn = Turn.PLAYER2
        else:
            self.turn = Turn.PLAYER1

    def draw_static_statistics(self, surface):

        # drawing timer
        pygame.draw.rect(surface, BLACK, (860, 380, 100, 40), 2)

        text = self.font_30.render('Timer', False, BLACK)
        surface.blit(text, (862, 340))

        # drawing player 2 information
        pygame.draw.rect(surface, self.player2_color,
                         (780, 30, 260, 120), 4)
        player = self.font_24.render("PLAYER 2", False, BLACK)
        surface.blit(player, (845, 35))

        if self.player2 == Opponent.CPU:

            player = self.font_24.render("CPU", False, BLACK)
            surface.blit(player, (820, 105))
            player = self.font_24.render(self.cpu_level.name, False, BLACK)
            surface.blit(player, (890, 105))
        else:
            player = self.font_24.render("HUMAN", False, BLACK)
            surface.blit(player, (862, 105))

        # drawing player 1 information
        pygame.draw.rect(surface, self.player1_color,
                         (780, 650, 260, 120), 4)
        player = self.font_24.render("PLAYER 1", False, BLACK)
        surface.blit(player, (845, 655))

        player = self.font_24.render("HUMAN", False, BLACK)
        surface.blit(player, (862, 725))

    def draw_statistics(self, surface):

        self.timer_actual = time.time()
        game_time = int(self.timer_actual - self.timer_start)

        minutes = game_time // 60
        if minutes >= 10:
            min_str = str(minutes)
        else:
            min_str = "0" + str(minutes)

        seconds = game_time % 60

        if seconds >= 10:
            sec = str(seconds)
        else:
            sec = "0" + str(seconds)

        if minutes > 99:
            min_str = "99"
            sec = "59"

        # drawing time
        time_str = min_str + ":" + sec
        time_str = self.font_24.render(time_str, False, BLACK)
        surface.fill(WHITE, (864, 384, 90, 30))
        surface.blit(time_str, (872, 384))

        # drawing your move

        surface.fill(WHITE, (778, 568, 264, 44))
        surface.fill(WHITE, (778, 183, 264, 44))

        if self.turn == Turn.PLAYER1:
            pygame.draw.rect(surface, self.player1_color,
                             (780, 570, 260, 40), 3)
            move = self.font_24.render("YOUR   MOVE!", False, BLACK)
            surface.blit(move, (825, 573))

        else:
            pygame.draw.rect(surface, self.player2_color,
                             (780, 185, 260, 40), 3)
            move = self.font_24.render("YOUR   MOVE!", False, BLACK)
            surface.blit(move, (825, 188))

        # drawing moves for player 2 (up)
        surface.fill(WHITE, (788, 69, 200, 30))
        moves = self.font_24.render("MOVES:    {}".format(self.player2_moves),
                                    False, BLACK)
        surface.blit(moves, (790, 70))

        # drawing moves for player 1 (down)
        surface.fill(WHITE, (788, 689, 200, 30))
        moves = self.font_24.render("MOVES:    {}".format(self.player1_moves),
                                    False, BLACK)
        surface.blit(moves, (790, 690))


class Game(object):

    def __init__(self):

        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()

        pygame.init()

        pygame.font.init()

        # resolution
        self.res = (W_SIZE, H_SIZE)

        # screen initialisation
        self.surface = pygame.display.set_mode(self.res)
        # game title
        pygame.display.set_caption('Paper Ball 2020')

        # game clock
        self.clock = pygame.time.Clock()

        self.margin = SCREEN_SIZE / 10

        self.board_size = 8 * SCREEN_SIZE / 10

        # borders width - must be odd
        self.board_border_width = 3

        # number of rows/ columns - must be even and be
        # dividend of 800
        self.board_rows = 10

        self.row_size = self.board_size / self.board_rows

        # goal width
        self.goal_width = 2 * self.row_size

        # ball size
        self.ball_size = 7

        # game layers
        self.game_board = pygame.Surface((self.board_size, self.board_size))
        self.game_outlines = pygame.Surface((self.board_size,
                                             self.board_size),
                                            pygame.SRCALPHA)

        # visited points
        #
        #  1  2  3
        #  8  0  4
        #  7  6  5
        #
        self.visited = [[[False for _ in range(0, self.board_rows + 1)]
                         for _ in range(0, self.board_rows + 1)]
                        for _ in range(0, 10)]

        # help menu
        self.help_menu = pygameMenu.TextMenu(self.surface,
                                             font=fonts.FONT_NEVIS,
                                             title='Help',
                                             title_offsety=5,
                                             window_height=H_SIZE,
                                             window_width=W_SIZE,
                                             menu_height=H_SIZE,
                                             menu_width=W_SIZE,
                                             dopause=True,
                                             menu_color=WHITE,
                                             menu_color_title=WHITE,
                                             font_color=BLACK,
                                             title_offsetx=510,
                                             bgfun=lambda i=self.surface:
                                             help_background(i),
                                             text_color=BLACK,
                                             text_fontsize=20,
                                             text_margin=15,
                                             draw_region_y=55,
                                             menu_alpha=10)

        with open('help.txt') as f:
            lines = f.readlines()
            for line in lines:
                self.help_menu.add_line(line)

        self.help_menu.add_option('Return to menu', PYGAME_MENU_BACK)

        # options menu
        self.options_menu = pygameMenu.Menu(self.surface,
                                            font=fonts.FONT_NEVIS,
                                            title='Options',
                                            title_offsety=5,
                                            window_height=H_SIZE,
                                            window_width=W_SIZE,
                                            menu_height=H_SIZE,
                                            menu_width=W_SIZE,
                                            dopause=True,
                                            menu_color=WHITE,
                                            menu_color_title=WHITE,
                                            font_color=BLACK,
                                            title_offsetx=450,
                                            bgfun=lambda i=self.surface:
                                            help_background(i),
                                            menu_alpha=100
                                            )

        self.options_menu.add_selector("Opponent",
                                       [("Human", Opponent.HUMAN),
                                        ("CPU", Opponent.CPU)],
                                       onchange=self.change_opponent,
                                       onreturn=self.change_opponent)

        self.options_menu.add_selector("CPU Level",
                                       [("Easy", CPULevel.EASY),
                                        ("Medium", CPULevel.MEDIUM),
                                        ("Maybe Hard", CPULevel.HARD)],
                                       onchange=self.change_cpu_level,
                                       onreturn=self.change_cpu_level)

        self.options_menu.add_selector("Player1 Color",
                                       [("Red", RED), ("Blue", BLUE),
                                        ("Green", GREEN),
                                        ("Yellow", YELLOW),
                                        ("Orange", ORANGE)],
                                       onchange=self.change_player1_color,
                                       onreturn=self.change_player1_color
                                       )

        self.options_menu.add_selector("Player2 Color",
                                       [("Blue", BLUE), ("Red", RED),
                                        ("Green", GREEN),
                                        ("Yellow", YELLOW),
                                        ("Orange", ORANGE)],
                                       onchange=self.change_player2_color,
                                       onreturn=self.change_player2_color
                                       )

        self.options_menu.add_selector("Board Size",
                                       [("10", 10), ("16", 16),
                                        ("20", 20), ("8", 8)],
                                       onchange=self.change_board_size,
                                       onreturn=self.change_board_size)

        self.options_menu.add_selector("Music", [("ON", True), ("OFF", False)],
                                       onchange=self.toggle_music,
                                       onreturn=self.toggle_music
                                       )

        self.options_menu.add_selector("Music Volume",
                                       [("5", 1), ("4", 0.8),
                                        ("3", 0.6), ("2", 0.4), ("1", 0.2),
                                        ("0", 0)], onchange=self.change_volume,
                                       onreturn=self.change_volume)

        self.options_menu.add_selector("Sound effects",
                                       [("ON", True), ("OFF", False)],
                                       onchange=self.toggle_music_effects,
                                       onreturn=self.toggle_music_effects
                                       )

        self.options_menu.add_option('Return to menu', PYGAME_MENU_BACK)

        # controls menu
        self.control_menu = pygameMenu.TextMenu(self.surface,
                                                font=fonts.FONT_NEVIS,
                                                title='Controls',
                                                title_offsety=5,
                                                window_height=H_SIZE,
                                                window_width=W_SIZE,
                                                menu_height=H_SIZE,
                                                menu_width=W_SIZE,
                                                dopause=True,
                                                menu_color=WHITE,
                                                menu_color_title=WHITE,
                                                font_color=BLACK,
                                                title_offsetx=455,
                                                bgfun=lambda i=self.surface:
                                                help_background(i),
                                                text_color=BLACK,
                                                text_fontsize=30,
                                                menu_alpha=100)

        with open('controls.txt') as f:
            lines = f.readlines()
            for line in lines:
                self.control_menu.add_line(line)

        self.control_menu.add_option('Return to menu', PYGAME_MENU_BACK)

        # game main menu
        self.main_menu = pygameMenu.Menu(self.surface,
                                         font=fonts.FONT_8BIT,
                                         title='Paper Ball',
                                         title_offsety=5,
                                         window_height=H_SIZE,
                                         window_width=W_SIZE,
                                         menu_height=H_SIZE,
                                         menu_width=W_SIZE,
                                         dopause=True,
                                         menu_color=WHITE,
                                         menu_color_title=WHITE,
                                         font_color=BLACK,
                                         title_offsetx=310,
                                         bgfun=lambda i=self.surface:
                                         help_background(i),
                                         menu_alpha=100)

        self.main_menu.add_option("Play game", self.game)
        self.main_menu.add_option("Options", self.options_menu)
        self.main_menu.add_option("Controls", self.control_menu)
        self.main_menu.add_option("Help", self.help_menu)
        self.main_menu.add_option('Exit', PYGAME_MENU_EXIT)

        # by default play with human
        self.opponent = Opponent.HUMAN
        # by default easy CPU level
        self.difficulty = CPULevel.EASY

        # player colours
        self.player1_colour = RED
        self.player2_colour = BLUE

        # music mode
        self.music = True
        self.volume = 1.0
        pygame.mixer_music.load("./music/music.mp3")
        pygame.mixer_music.play(loops=-1)
        self.winning_music = pygame.mixer.Sound("./music/Victory.wav")
        self.move_sound = pygame.mixer.Sound("./music/move.wav")
        self.music_effects = True

        # fonts
        self.font_50 = pygame.font.Font("font.ttf", 50)

        self.font_24 = pygame.font.Font("font.ttf", 24)

    def gen_visited(self):
        self.visited = [[[False for _ in range(0, self.board_rows + 1)]
                         for _ in range(0, self.board_rows + 1)]
                        for _ in range(0, 10)]

        index = int(self.board_size / 2 / self.row_size)

        self.visited[0][index][index] = True

        # for left border
        for i in range(0, self.board_rows + 1):
            self.visited[1][0][i] = True
            self.visited[2][0][i] = True
            self.visited[6][0][i] = True
            self.visited[7][0][i] = True
            self.visited[8][0][i] = True

        # for top
        for i in range(0, self.board_rows + 1):
            self.visited[1][i][0] = True
            self.visited[2][i][0] = True
            self.visited[3][i][0] = True
            self.visited[4][i][0] = True
            self.visited[8][i][0] = True

        # for bottom
        for i in range(0, self.board_rows + 1):
            self.visited[4][i][self.board_rows] = True
            self.visited[5][i][self.board_rows] = True
            self.visited[6][i][self.board_rows] = True
            self.visited[7][i][self.board_rows] = True
            self.visited[8][i][self.board_rows] = True

        # for right
        for i in range(0, self.board_rows + 1):
            self.visited[2][self.board_rows][i] = True
            self.visited[3][self.board_rows][i] = True
            self.visited[4][self.board_rows][i] = True
            self.visited[5][self.board_rows][i] = True
            self.visited[6][self.board_rows][i] = True

    def check_block(self, x, y):

        x_red = int(x / self.row_size)
        y_red = int(y / self.row_size)

        for i in range(1, 9):
            if not self.visited[i][x_red][y_red]:
                return False

        return True

    @staticmethod
    def increment_player_moves(statistics, player):
        if player == 1:
            statistics.player1_add_move()
        else:
            statistics.player2_add_move()

    def translate_position(self, x):

        if x < self.margin:
            return 0
        if x >= self.margin + self.board_size:
            return self.board_size
        return x - self.margin

    def get_player_colour(self, player):

        if player == 1:
            return self.player1_colour
        else:
            return self.player2_colour

    def clear_game_outlines(self):

        self.game_outlines.fill((255, 255, 255, 0))

    def draw_ball(self, x, y):

        pygame.draw.circle(self.game_board, RED, (int(x), int(y)),
                           self.ball_size, 0)

    def draw_outline(self, player, x, y, x_dir, y_dir):

        colour = self.get_player_colour(player)

        direction = self.get_direction(x_dir, y_dir)

        x_red = int(x / self.row_size)
        y_red = int(y / self.row_size)

        if not self.visited[direction][x_red][y_red]:
            self.clear_game_outlines()
            pygame.draw.line(self.game_outlines, colour, (x, y),
                             (x + x_dir * self.row_size,
                              y + y_dir * self.row_size),
                             self.board_border_width)

    @staticmethod
    def get_direction(x_dir, y_dir):
        if (x_dir, y_dir) == (-1, -1):
            return 1
        elif (x_dir, y_dir) == (0, -1):
            return 2
        elif (x_dir, y_dir) == (1, -1):
            return 3
        elif (x_dir, y_dir) == (1, 0):
            return 4
        elif (x_dir, y_dir) == (1, 1):
            return 5
        elif (x_dir, y_dir) == (0, 1):
            return 6
        elif (x_dir, y_dir) == (-1, 1):
            return 7
        elif (x_dir, y_dir) == (-1, 0):
            return 8
        else:
            return 0

    @staticmethod
    def get_xy_from_direction(direction):

        if direction == 1:
            return -1, -1
        elif direction == 2:
            return 0, -1
        elif direction == 3:
            return 1, -1
        elif direction == 4:
            return 1, 0
        elif direction == 5:
            return 1, 1
        elif direction == 6:
            return 0, 1
        elif direction == 7:
            return -1, 1
        elif direction == 8:
            return -1, 0
        else:
            return 0, 0

    def run(self):

        while True:
            pygame.time.delay(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN \
                        and event.key == pygame.K_ESCAPE:
                    self.main_menu.enable()

            self.main_menu.mainloop(pygame.event.get())

            pygame.display.flip()

    def game_board_update(self, game_board_cpy, x, y):
        self.surface.blit(game_board_cpy, (self.margin, self.margin))
        self.game_board.blit(game_board_cpy, (0, 0))
        self.game_board.blit(self.game_outlines, (0, 0))
        self.draw_ball(x, y)
        self.surface.blit(self.game_board, (self.margin, self.margin))

    def gen_board(self):
        self.surface.fill(WHITE)
        self.game_board.fill(WHITE)

        for i in range(0, self.board_rows + 1, 1):
            pygame.draw.line(self.game_board,
                             LIGHT_GRAY, (0, i * self.row_size),
                             (self.board_size, i * self.row_size), 1)

            pygame.draw.line(self.game_board, LIGHT_GRAY,
                             (i * self.row_size, 0),
                             (i * self.row_size, self.board_size), 1)

            pygame.draw.line(self.game_board, LIGHT_GRAY,
                             (i * self.row_size, 0),
                             (self.board_size,
                              self.board_size - i * self.row_size), 1)

            pygame.draw.line(self.game_board, LIGHT_GRAY,
                             (0, i * self.row_size),
                             (self.board_size - i * self.row_size,
                              self.board_size), 1)

            pygame.draw.line(self.game_board, LIGHT_GRAY,
                             (self.board_size - i * self.row_size, 0),
                             (0, self.board_size - i * self.row_size), 1)

            pygame.draw.line(self.game_board, LIGHT_GRAY,
                             (self.board_size,
                              self.board_size - i * self.row_size),
                             (self.board_size - i * self.row_size,
                              self.board_size), 1)

        pygame.draw.rect(self.game_board, BLACK,
                         (0, 0, self.board_size, self.board_size),
                         self.board_border_width)

        pygame.draw.line(self.game_board, RED,
                         ((self.board_size - self.goal_width) / 2, 0),
                         ((self.board_size + self.goal_width) / 2, 0),
                         self.board_border_width)

        pygame.draw.line(self.game_board, RED,
                         ((self.board_size - self.goal_width) / 2,
                          self.board_size - 1),
                         ((self.board_size + self.goal_width) / 2,
                          self.board_size - 1), self.board_border_width)

    # cpu level Easy
    def cpu_easy(self, x, y):

        x_dir = random.randint(-1, 1)
        y_dir = random.randint(-1, 1)

        if x == 0:
            x_dir = 1
        if y == 0:
            y_dir = 1
        if x == self.board_size:
            x_dir = -1
        if y == self.board_size:
            y_dir = -1

        direction = self.get_direction(x_dir, y_dir)
        n_direction = self.get_direction(-x_dir, -y_dir)

        x_red_plus = int(x / self.row_size + x_dir)
        y_red_plus = int(y / self.row_size + y_dir)

        x_red = int(x / self.row_size)
        y_red = int(y / self.row_size)

        while self.visited[n_direction][x_red_plus][y_red_plus] \
                or self.visited[direction][x_red][y_red]:
            x_dir = random.randint(-1, 1)
            y_dir = random.randint(-1, 1)

            if x == 0:
                x_dir = 1
            if y == 0:
                y_dir = 1
            if x == self.board_size:
                x_dir = -1
            if y == self.board_size:
                y_dir = -1

            x_red_plus = int(x / self.row_size + x_dir)
            y_red_plus = int(y / self.row_size + y_dir)

            x_red = int(x / self.row_size)
            y_red = int(y / self.row_size)

            direction = self.get_direction(x_dir, y_dir)
            n_direction = self.get_direction(-x_dir, -y_dir)

        return x_dir, y_dir

    def cpu_medium(self, x, y):

        moves = ((6, 5, 7, 4, 8, 3, 1, 2), (6, 7, 5, 8, 4, 1, 3, 2))

        strategy = random.randint(0, 1)

        i = 0

        (x_dir, y_dir) = self.get_xy_from_direction(moves[strategy][i])

        if x == 0:
            x_dir = 1
        if y == 0:
            y_dir = 1
        if x == self.board_size:
            x_dir = -1
        if y == self.board_size:
            y_dir = -1

        direction = self.get_direction(x_dir, y_dir)
        n_direction = self.get_direction(-x_dir, -y_dir)

        x_red_plus = int(x / self.row_size + x_dir)
        y_red_plus = int(y / self.row_size + y_dir)

        x_red = int(x / self.row_size)
        y_red = int(y / self.row_size)

        while self.visited[n_direction][x_red_plus][y_red_plus] \
                or self.visited[direction][x_red][y_red]:

            i += 1

            (x_dir, y_dir) = self.get_xy_from_direction(moves[strategy][i])

            if x == 0:
                x_dir = 1
            if y == 0:
                y_dir = 1
            if x == self.board_size:
                x_dir = -1
            if y == self.board_size:
                y_dir = -1

            x_red_plus = int(x / self.row_size + x_dir)
            y_red_plus = int(y / self.row_size + y_dir)

            x_red = int(x / self.row_size)
            y_red = int(y / self.row_size)

            direction = self.get_direction(x_dir, y_dir)
            n_direction = self.get_direction(-x_dir, -y_dir)

        return x_dir, y_dir

    def cpu_maybe_hard(self, x, y):

        moves = ((6, 7, 5, 8, 4, 1, 3, 2),
                 (5, 6, 4, 7, 8, 3, 2, 1),
                 (7, 6, 8, 5, 4, 1, 2, 3))

        if x == self.board_size / 2:
            strategy = 0
        elif x < self.board_size / 2:
            strategy = 1
        else:
            strategy = 2

        i = 0

        (x_dir, y_dir) = self.get_xy_from_direction(moves[strategy][i])

        if x == 0:
            x_dir = 1
        if y == 0:
            y_dir = 1
        if x == self.board_size:
            x_dir = -1
        if y == self.board_size:
            y_dir = -1

        direction = self.get_direction(x_dir, y_dir)
        n_direction = self.get_direction(-x_dir, -y_dir)

        x_red_plus = int(x / self.row_size + x_dir)
        y_red_plus = int(y / self.row_size + y_dir)

        x_red = int(x / self.row_size)
        y_red = int(y / self.row_size)

        while self.visited[n_direction][x_red_plus][y_red_plus] \
                or self.visited[direction][x_red][y_red]:

            i += 1
            print(i)
            print(moves[strategy][i])

            (x_dir, y_dir) = self.get_xy_from_direction(moves[strategy][i])

            if x == 0:
                x_dir = 1
            if y == 0:
                y_dir = 1
            if x == self.board_size:
                x_dir = -1
            if y == self.board_size:
                y_dir = -1

            x_red_plus = int(x / self.row_size + x_dir)
            y_red_plus = int(y / self.row_size + y_dir)

            x_red = int(x / self.row_size)
            y_red = int(y / self.row_size)

            direction = self.get_direction(x_dir, y_dir)
            n_direction = self.get_direction(-x_dir, -y_dir)

        return x_dir, y_dir

    def game(self):

        # game board initialization
        self.gen_board()
        self.clear_game_outlines()

        # game board copy
        game_board_cpy = pygame.Surface.copy(self.game_board)

        self.game_board_update(self.game_board,
                               self.board_size / 2, self.board_size / 2)

        statistics = Statistics(self.opponent, self.difficulty,
                                self.player1_colour, self.player2_colour)

        statistics.draw_static_statistics(self.surface)
        pygame.display.update()

        # drawing circles and lines
        (x, y) = (int(self.board_size / 2), int(self.board_size / 2))

        (x_dir, y_dir) = (0, 0)

        # which player now moves and additional flag
        player = 1
        clickable = True

        self.gen_visited()

        while True:
            if self.goal_width / 2 >= abs(self.board_size / 2 - x):
                if y == 0:
                    winner = Turn.PLAYER1
                    break
                elif y == self.board_size:
                    winner = Turn.PLAYER2
                    break

            if self.check_block(x, y):
                if player == 0:
                    winner = Turn.PLAYER1
                else:
                    winner = Turn.PLAYER2
                break

            pygame.time.delay(30)

            # cpu move
            if player == 0 and self.opponent == Opponent.CPU:

                time.sleep(0.6)

                if self.difficulty == CPULevel.EASY:
                    cpu_move = self.cpu_easy(x, y)
                elif self.difficulty == CPULevel.MEDIUM:
                    cpu_move = self.cpu_medium(x, y)
                else:  # maybe hard
                    cpu_move = self.cpu_maybe_hard(x, y)

                self.move_sound.play()

                x_dir = cpu_move[0]
                y_dir = cpu_move[1]

                direction = self.get_direction(x_dir, y_dir)
                n_direction = self.get_direction(-x_dir, -y_dir)

                self.draw_outline(player, x, y, x_dir, y_dir)

                self.increment_player_moves(statistics, player)

                x_red_plus = int(x / self.row_size + x_dir)
                y_red_plus = int(y / self.row_size + y_dir)

                x_red = int(x / self.row_size)
                y_red = int(y / self.row_size)

                self.visited[n_direction][x_red_plus][y_red_plus] = True
                self.visited[direction][x_red][y_red] = True

                (x, y) = (x + x_dir * self.row_size, y + y_dir * self.row_size)

                x_red = int(x / self.row_size)
                y_red = int(y / self.row_size)

                if x == 0 or y == 0 or x == self.board_size \
                        or y == self.board_size:
                    self.visited[0][x_red][y_red] = True
                elif not self.visited[0][x_red][y_red]:
                    player = 1 - player
                    statistics.change_player()

                    x_red = int(x / self.row_size)
                    y_red = int(y / self.row_size)

                    self.visited[0][x_red][y_red] = True

                # saving moves on board

                self.game_board_update(game_board_cpy, x, y)

                game_board_cpy.blit(self.game_outlines, (0, 0))

                statistics.draw_statistics(self.surface)

                pygame.display.update()

                # clickable = True
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN \
                        and event.key == pygame.K_ESCAPE:
                    self.toggle_music(True)
                    self.gen_visited()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    self.toggle_music(not self.music)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.increase_volume()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    self.decrease_volume()

                if pygame.mouse.get_pressed() == (1, 0, 0) and clickable:
                    direction = self.get_direction(x_dir, y_dir)
                    n_direction = self.get_direction(-x_dir, -y_dir)

                    x_red_plus = int(x / self.row_size + x_dir)
                    y_red_plus = int(y / self.row_size + y_dir)

                    x_red = int(x / self.row_size)
                    y_red = int(y / self.row_size)

                    if self.visited[n_direction][x_red_plus][y_red_plus]:
                        continue
                    elif self.visited[direction][x_red][y_red]:
                        continue

                    self.move_sound.play()

                    x_red_plus = int(x / self.row_size + x_dir)
                    y_red_plus = int(y / self.row_size + y_dir)

                    x_red = int(x / self.row_size)
                    y_red = int(y / self.row_size)

                    self.increment_player_moves(statistics, player)
                    self.visited[n_direction][x_red_plus][y_red_plus] = True
                    self.visited[direction][x_red][y_red] = True

                    (x, y) = (x + x_dir * self.row_size,
                              y + y_dir * self.row_size)

                    x_red = int(x / self.row_size)
                    y_red = int(y / self.row_size)

                    if x == 0 or y == 0 or x == self.board_size \
                            or y == self.board_size:
                        self.visited[0][x_red][y_red] = True
                    elif not self.visited[0][x_red][y_red]:
                        player = 1 - player
                        statistics.change_player()
                        self.visited[0][x_red][y_red] = True

                    # saving moves on board
                    game_board_cpy.blit(self.game_outlines, (0, 0))
                    clickable = False

            (x_n, y_n) = pygame.mouse.get_pos()

            x_n = self.translate_position(x_n)
            y_n = self.translate_position(y_n)

            clickable = True
            if x_n == 0 or y_n == 0 or x_n == self.board_size \
                    or y_n == self.board_size:
                x_dir = 0
                y_dir = 0
                clickable = False
            elif abs(x_n - x) > self.row_size or abs(y_n - y) > self.row_size:
                clickable = False
            elif x_n - x != 0 and y_n - y != 0:
                x_dir = (x_n - x) / abs(x_n - x)
                y_dir = (y_n - y) / abs(y_n - y)
                if abs((x_n - x) / (y_n - y)) > 2:
                    y_dir = 0
                if abs((x_n - x) / (y_n - y)) < 1 / 2:
                    x_dir = 0
                if x == 0:
                    x_dir = 1
                if y == 0:
                    y_dir = 1
                if x == self.board_size:
                    x_dir = -1
                if y == self.board_size:
                    y_dir = -1

                self.draw_outline(player, x, y, x_dir, y_dir)
                self.game_board_update(game_board_cpy, x, y)

            statistics.draw_statistics(self.surface)

            pygame.display.update()

        # drawing statistics after game is over

        self.toggle_music(False)
        if self.music_effects is True:
            self.winning_music.play()

        text = self.font_50.render('GAME', False, BLACK)
        self.surface.blit(text, (104, 10))

        text = self.font_50.render('OVER', False, BLACK)
        self.surface.blit(text, (550, 10))

        self.surface.fill(WHITE, (778, 568, 264, 44))
        self.surface.fill(WHITE, (778, 183, 264, 44))

        # who won
        if winner == Turn.PLAYER1:
            pygame.draw.rect(self.surface, self.player1_colour,
                             (780, 570, 260, 40), 3)
            move = self.font_24.render("WINNER!", False, BLACK)
            self.surface.blit(move, (853, 573))

        else:
            pygame.draw.rect(self.surface, self.player2_colour,
                             (780, 185, 260, 40), 3)
            move = self.font_24.render("WINNER!", False, BLACK)
            self.surface.blit(move, (853, 188))

        pygame.display.update()

        while True:

            pygame.time.delay(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN \
                        and event.key == pygame.K_ESCAPE:
                    self.toggle_music(True)
                    return

    # changes opponent type
    def change_opponent(self, c):
        if c == Opponent.HUMAN:
            self.opponent = Opponent.HUMAN
        else:
            self.opponent = Opponent.CPU

    # changes cpu level
    def change_cpu_level(self, c):
        if c == CPULevel.EASY:
            self.difficulty = CPULevel.EASY

        elif c == CPULevel.MEDIUM:
            self.difficulty = CPULevel.MEDIUM

        elif c == CPULevel.HARD:
            self.difficulty = CPULevel.HARD

        elif c == CPULevel.HARDER:
            self.difficulty = CPULevel.HARDER

    def change_player1_color(self, c):
        if c == GREEN:
            self.player1_colour = GREEN
        elif c == RED:
            self.player1_colour = RED

        elif c == BLUE:
            self.player1_colour = BLUE

        elif c == YELLOW:
            self.player1_colour = YELLOW

        elif c == ORANGE:
            self.player1_colour = ORANGE

    def change_player2_color(self, c):
        if c == GREEN:
            self.player2_colour = GREEN
        elif c == RED:
            self.player2_colour = RED

        elif c == BLUE:
            self.player2_colour = BLUE

        elif c == YELLOW:
            self.player2_colour = YELLOW

        elif c == ORANGE:
            self.player2_colour = ORANGE

    def toggle_music(self, c):
        if c:
            if self.music is False:
                self.music = True
                pygame.mixer_music.unpause()
        else:
            if self.music is True:
                self.music = False
                pygame.mixer_music.pause()

    def toggle_music_effects(self, c):
        if c:
            if self.music_effects is False:
                self.music_effects = True
        else:
            if self.music_effects is True:
                self.music_effects = False

    def change_volume(self, c):
        pygame.mixer_music.set_volume(c)
        self.volume = c

    def decrease_volume(self):
        if self.volume > 0.0:
            self.volume -= 0.2
        pygame.mixer_music.set_volume(self.volume)

    def increase_volume(self):
        if self.volume < 1.0:
            self.volume += 0.2
        pygame.mixer_music.set_volume(self.volume)

    def change_board_size(self, c):
        self.board_rows = c
        self.row_size = self.board_size / self.board_rows
        self.goal_width = 2 * self.row_size
        self.visited = [[[False for _ in range(0, self.board_rows + 1)]
                         for _ in range(0, self.board_rows + 1)]
                        for _ in range(0, 10)]


def main():
    random.seed()
    paper_ball = Game()
    paper_ball.run()


if __name__ == '__main__':
    main()
