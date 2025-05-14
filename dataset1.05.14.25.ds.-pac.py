import curses
import random
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from collections import deque
from itertools import cycle

class Pacman:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = 14
        self.y = 23
        self.direction = KEY_LEFT
        self.next_direction = None
        self.lives = 3
        self.score = 0
        self.power_time = 0
        self.consecutive_ghosts = 0
        self.mouth_animation = cycle([0, 1, 2, 1])
        self.mouth_state = next(self.mouth_animation)

class Ghost:
    MODE_SCATTER = 0
    MODE_CHASE = 1
    MODE_FRIGHTENED = 2
    MODE_EATEN = 3

    def __init__(self, name, color, personality):
        self.name = name
        self.color = color
        self.personality = personality
        self.reset()
        
    def reset(self):
        self.x = 13
        self.y = 11
        self.dx = 0
        self.dy = 0
        self.target = (0, 0)
        self.mode = Ghost.MODE_SCATTER
        self.frightened_time = 0
        self.speed = 1
        self.home = (13, 11)
        self.exit_path = deque([(13, 11), (13, 10), (13, 9), (12, 9), (11, 9)])
        self.eye_direction = KEY_LEFT

class Game:
    LEVEL_TIMING = [
        (7, 20, 7, 20, 5, 20, 5, 9999),  # Level 1
        (7, 20, 7, 20, 5, 20, 5, 9999),  # Level 2-4
        (5, 20, 5, 20, 5, 20, 5, 9999),   # Level 5+
    ]
    FRUIT_SPAWN_AT = [70, 170]
    GHOST_SCORES = [200, 400, 800, 1600]
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.init_maze()
        self.level = 1
        self.init_game()
        self.mode_timer = deque()
        self.setup_mode_timing()
        self.fruit = None
        self.fruit_timer = 0
        self.dot_counter = 0
        self.ghost_speeds = [0.75, 0.85, 0.95, 1.05]
        self.frame_count = 0
        
    def init_maze(self):
        self.maze = [
            "#####################",
            "#........#.........#",
            "#o##.###.#.###.##o#",
            "#..................#",
            "#.##.#.#####.#.##.#",
            "#....#...#...#....#",
            "####.### # ###.####",
            "    #.#       #.#  ",
            "####.# ##=## #.####",
            "     .  # #  .     ",
            "####.# ##### #.####",
            "    #.#       #.#   ",
            "####.# ##### #.####",
            "#........#.........#",
            "#.##.###.#.###.##.#",
            "#o.#..... .....#.o#",
            "##.#.#.#####.#.#.##",
            "#....#...#...#....#",
            "#.######.#.######.#",
            "#..................#",
            "####################"
        ]
        self.tunnels = {(0, 9): (18, 9), (18, 9): (0, 9)}
        
    def init_game(self):
        self.pacman = Pacman()
        self.ghosts = [
            Ghost("Blinky", curses.COLOR_RED, "shadow"),
            Ghost("Pinky", curses.COLOR_MAGENTA, "ambusher"),
            Ghost("Inky", curses.COLOR_CYAN, "fickle"),
            Ghost("Clyde", curses.COLOR_YELLOW, "pokey")
        ]
        self.init_pellets()
        self.set_ghost_positions()
        
    def set_ghost_positions(self):
        positions = [(13, 11), (13, 12), (14, 11), (14, 12)]
        for ghost, pos in zip(self.ghosts, positions):
            ghost.x, ghost.y = pos
            
    def init_pellets(self):
        self.pellets = set()
        self.power_pellets = []
        for y, row in enumerate(self.maze):
            for x, char in enumerate(row):
                if char == '.':
                    self.pellets.add((x, y))
                elif char == 'o':
                    self.power_pellets.append((x, y))
        self.total_pellets = len(self.pellets)
                    
    def setup_mode_timing(self):
        level_index = min(self.level-1, len(self.LEVEL_TIMING)-1)
        timing = self.LEVEL_TIMING[level_index]
        self.mode_timer = deque([
            (Ghost.MODE_SCATTER, timing[0]),
            (Ghost.MODE_CHASE, timing[1]),
            (Ghost.MODE_SCATTER, timing[2]),
            (Ghost.MODE_CHASE, timing[3]),
            (Ghost.MODE_SCATTER, timing[4]),
            (Ghost.MODE_CHASE, timing[5]),
            (Ghost.MODE_SCATTER, timing[6]),
            (Ghost.MODE_CHASE, timing[7])
        ])

    def calculate_target(self, ghost):
        if ghost.mode == Ghost.MODE_EATEN:
            return ghost.home
            
        if ghost.mode == Ghost.MODE_SCATTER:
            return {
                "Blinky": (25, -3),
                "Pinky": (2, -3),
                "Inky": (27, 30),
                "Clyde": (0, 30)
            }[ghost.name]
            
        # Chase mode targeting
        if ghost.personality == "shadow":
            return (self.pacman.x, self.pacman.y)
            
        elif ghost.personality == "ambusher":
            dx, dy = {
                KEY_LEFT: (-4, 0),
                KEY_RIGHT: (4, 0),
                KEY_UP: (0, -4),
                KEY_DOWN: (0, 4)
            }.get(self.pacman.direction, (0, 0))
            target = (self.pacman.x + dx, self.pacman.y + dy)
            
            # Keep target in bounds
            return (max(1, min(target[0], len(self.maze[0])-2)), 
                    max(1, min(target[1], len(self.maze)-2)))
            
        elif ghost.personality == "fickle":
            blinky = self.ghosts[0]
            vector_x = self.pacman.x - blinky.x
            vector_y = self.pacman.y - blinky.y
            return (self.pacman.x + vector_x, self.pacman.y + vector_y)
            
        else:  # Clyde
            dist = abs(self.pacman.x - ghost.x) + abs(self.pacman.y - ghost.y)
            return (self.pacman.x, self.pacman.y) if dist > 8 else (0, 30)

    def move_ghost(self, ghost):
        if ghost.mode == Ghost.MODE_EATEN and (ghost.x, ghost.y) == ghost.home:
            ghost.mode = Ghost.MODE_SCATTER
            ghost.speed = self.ghost_speeds[min(self.level-1, 3)]

        if ghost.mode == Ghost.MODE_EATEN:
            target = ghost.home
        else:
            target = self.calculate_target(ghost)

        best_dir = None
        min_dist = float('inf')
        directions = []
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (dx, dy) == (-ghost.dx, -ghost.dy) and ghost.mode not in [Ghost.MODE_FRIGHTENED, Ghost.MODE_EATEN]:
                continue  # Prevent 180 turns
            
            new_x, new_y = self.move_entity(ghost.x, ghost.y, dx, dy)
            if (new_x, new_y) != (ghost.x, ghost.y):
                dist = (new_x - target[0])**2 + (new_y - target[1])**2
                directions.append((dx, dy, dist))
        
        if directions:
            if ghost.mode == Ghost.MODE_FRIGHTENED:
                best_dir = random.choice(directions)[:2]
            else:
                best_dir = min(directions, key=lambda x: x[2])[:2]
            
            ghost.dx, ghost.dy = best_dir
            new_x, new_y = self.move_entity(ghost.x, ghost.y, ghost.dx, ghost.dy)
            ghost.x, ghost.y = new_x
            ghost.eye_direction = ghost.dx, ghost.dy

    def move_pacman(self):
        if self.pacman.next_direction:
            dx, dy = self.get_direction_vector(self.pacman.next_direction)
            new_x, new_y = self.move_entity(self.pacman.x, self.pacman.y, dx, dy)
            if (new_x, new_y) != (self.pacman.x, self.pacman.y):
                self.pacman.direction = self.pacman.next_direction
                self.pacman.next_direction = None
                self.pacman.x, self.pacman.y = new_x
                return

        dx, dy = self.get_direction_vector(self.pacman.direction)
        new_x, new_y = self.move_entity(self.pacman.x, self.pacman.y, dx, dy)
        self.pacman.x, self.pacman.y = new_x

    def get_direction_vector(self, direction):
        return {
            KEY_LEFT: (-1, 0),
            KEY_RIGHT: (1, 0),
            KEY_UP: (0, -1),
            KEY_DOWN: (0, 1)
        }.get(direction, (0, 0))

    def check_collisions(self):
        # Pellet collection
        if (self.pacman.x, self.pacman.y) in self.pellets:
            self.pellets.remove((self.pacman.x, self.pacman.y))
            self.pacman.score += 10
            self.dot_counter += 1
            curses.beep()

        # Power pellet collection
        if (self.pacman.x, self.pacman.y) in self.power_pellets:
            self.power_pellets.remove((self.pacman.x, self.pacman.y))
            self.pacman.power_time = 30 * (2 if self.level >= 5 else 1)
            self.pacman.score += 50
            for ghost in self.ghosts:
                if ghost.mode != Ghost.MODE_EATEN:
                    ghost.mode = Ghost.MODE_FRIGHTENED
                    ghost.frightened_time = self.pacman.power_time
            curses.beep()

        # Ghost collisions
        for ghost in self.ghosts:
            if (ghost.x, ghost.y) == (self.pacman.x, self.pacman.y):
                if ghost.mode == Ghost.MODE_FRIGHTENED:
                    ghost.mode = Ghost.MODE_EATEN
                    self.pacman.score += self.GHOST_SCORES[self.pacman.consecutive_ghosts % 4]
                    self.pacman.consecutive_ghosts += 1
                    ghost.speed *= 2
                elif ghost.mode != Ghost.MODE_EATEN:
                    self.handle_death()
                    
    def handle_death(self):
        self.pacman.lives -= 1
        self.pacman.consecutive_ghosts = 0
        if self.pacman.lives > 0:
            self.init_game()
            curses.flash()
        else:
            self.game_over()

    def draw_all(self):
        # Draw maze
        for y, row in enumerate(self.maze):
            for x, char in enumerate(row):
                if char == '#':
                    self.stdscr.addch(y, x, '▓', curses.color_pair(3))
                elif char == '=':
                    self.stdscr.addch(y, x, '▤', curses.color_pair(3))

        # Draw pellets
        for x, y in self.pellets:
            self.stdscr.addch(y, x, '∙', curses.color_pair(4))

        # Draw power pellets
        for x, y in self.power_pellets:
            self.stdscr.addch(y, x, '●', curses.color_pair(4) | curses.A_BOLD)

        # Draw Pacman
        mouth = [' ', '▖', '▘', '▝', '▗'][self.pacman.mouth_state]
        self.stdscr.addch(self.pacman.y, self.pacman.x, mouth, 
                         curses.color_pair(1) | curses.A_BOLD)

        # Draw ghosts
        for ghost in self.ghosts:
            color = curses.color_pair(2)
            char = 'E'
            if ghost.mode == Ghost.MODE_FRIGHTENED:
                color = curses.color_pair(5) | (curses.A_BLINK if ghost.frightened_time < 4 else 0)
                char = '¤'
            elif ghost.mode == Ghost.MODE_EATEN:
                color = curses.color_pair(4)
                char = {'LEFT':'◀', 'RIGHT':'▶', 'UP':'▲', 'DOWN':'▼'}[ghost.eye_direction]
            else:
                color = curses.color_pair(ghost.color)
                char = ghost.name[0]
            
            self.stdscr.addch(ghost.y, ghost.x, char, color | curses.A_BOLD)

        # Draw HUD
        self.stdscr.addstr(22, 0, f"Score: {self.pacman.score}  Lives: {'♥'*self.pacman.lives}  Level: {self.level}")

    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_WHITE)

        while self.pacman.lives > 0:
            self.frame_count += 1
            self.stdscr.clear()
            
            # Animate Pacman mouth every 5 frames
            if self.frame_count % 5 == 0:
                self.pacman.mouth_state = next(self.pacman.mouth_animation)

            self.update_modes()
            self.handle_input()
            self.move_pacman()
            
            # Move ghosts at half speed when frightened
            for ghost in self.ghosts:
                if self.frame_count % (2 if ghost.mode == Ghost.MODE_FRIGHTENED else 1) == 0:
                    self.move_ghost(ghost)
            
            self.check_collisions()
            self.check_fruit()
            self.draw_all()
            
            self.stdscr.refresh()
            curses.napms(16 if self.level < 5 else 12)  # ~60 FPS

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: Game(stdscr).run())
