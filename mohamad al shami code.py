import turtle
import random
import time

# Maze settings
CELL_SIZE = 40
ROWS, COLS = 10, 10

# Directions: Up=0, Right=1, Down=2, Left=3
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# Maze data
maze = [[[1, 1, 1, 1] for _ in range(COLS)] for _ in range(ROWS)]
visited = [[False for _ in range(COLS)] for _ in range(ROWS)]

# Global state
player_x, player_y = 0, 0
start_time = time.time()
game_running = True
held_direction = None  # "up", "down", "left", "right", or None

# Setup screen
screen = turtle.Screen()
screen.setup(width=800, height=800)
screen.title("Maze Game - Find the Exit!")
screen.bgcolor("white")
screen.tracer(0)

# Drawer turtle
drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)
drawer.pensize(3)
drawer.penup()

# Player turtle
player = turtle.Turtle()
player.shape("turtle")
player.color("blue")
player.penup()
player.speed(3)
player.shapesize(stretch_wid=1, stretch_len=1)
player.showturtle()

# UI turtles
message_writer = turtle.Turtle()
message_writer.hideturtle()
message_writer.penup()

timer_writer = turtle.Turtle()
timer_writer.hideturtle()
timer_writer.penup()
timer_writer.goto(-40, 250)
timer_writer.color("black")

def carve_maze(x, y):
    visited[y][x] = True
    directions = list(enumerate(DIRS))
    random.shuffle(directions)

    for i, (dx, dy) in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and not visited[ny][nx]:
            maze[y][x][i] = 0
            maze[ny][nx][(i + 2) % 4] = 0
            carve_maze(nx, ny)

def draw_cell(x, y, walls):
    start_x = -COLS * CELL_SIZE // 2 + x * CELL_SIZE
    start_y = ROWS * CELL_SIZE // 2 - y * CELL_SIZE
    drawer.penup()
    drawer.goto(start_x, start_y)
    drawer.setheading(0)

    for i in range(4):
        if walls[i]:
            drawer.pendown()
        else:
            drawer.penup()
        drawer.forward(CELL_SIZE)
        drawer.right(90)

def draw_maze():
    drawer.clear()
    for y in range(ROWS):
        for x in range(COLS):
            draw_cell(x, y, maze[y][x])

    # Open entrance and exit
    drawer.penup()
    drawer.goto(-COLS * CELL_SIZE // 2, ROWS * CELL_SIZE // 2)
    drawer.setheading(270)
    drawer.pensize(10)
    drawer.pencolor("white")
    drawer.pendown()
    drawer.forward(CELL_SIZE)

    drawer.penup()
    drawer.goto(-COLS * CELL_SIZE // 2 + COLS * CELL_SIZE, -ROWS * CELL_SIZE // 2)
    drawer.setheading(90)
    drawer.pendown()
    drawer.forward(CELL_SIZE)

    drawer.pensize(3)
    drawer.pencolor("black")
    screen.update()

def grid_to_screen(x, y):
    px = -COLS * CELL_SIZE // 2 + x * CELL_SIZE + CELL_SIZE // 2
    py = ROWS * CELL_SIZE // 2 - y * CELL_SIZE - CELL_SIZE // 2
    return px, py

def update_player():
    px, py = grid_to_screen(player_x, player_y)
    player.goto(px, py)
    screen.update()

def can_move(x, y, direction):
    if x < 0 or x >= COLS or y < 0 or y >= ROWS:
        return False
    return maze[y][x][direction] == 0

def check_win():
    global game_running
    if player_x == COLS - 1 and player_y == ROWS - 1:
        game_running = False
        screen.title("🎉 You reached the exit! Congratulations! 🎉")
        message_writer.clear()
        message_writer.goto(0, -ROWS * CELL_SIZE // 1.5 - 30)
        message_writer.color("green")
        message_writer.write("🎉 You reached the exit! Congratulations! 🎉\nPress 'R' to restart", align="center", font=("Arial", 20, "bold"))

def update_timer():
    if game_running:
        elapsed = int(time.time() - start_time)
        timer_writer.clear()
        timer_writer.write(f"Time: {elapsed}s", font=("Arial", 16, "bold"))
        screen.ontimer(update_timer, 1000)

# --- Smooth movement ---

def move_if_holding():
    global player_x, player_y
    if not game_running:
        return

    moved = False
    if held_direction == "up" and can_move(player_x, player_y, 0):
        player_y -= 1
        moved = True
    elif held_direction == "right" and can_move(player_x, player_y, 1):
        player_x += 1
        moved = True
    elif held_direction == "down" and can_move(player_x, player_y, 2):
        player_y += 1
        moved = True
    elif held_direction == "left" and can_move(player_x, player_y, 3):
        player_x -= 1
        moved = True

    if moved:
        update_player()
        check_win()

    if held_direction:
        screen.ontimer(move_if_holding, 100)  # reduced delay for smoother movement

def hold_up():
    global held_direction
    held_direction = "up"
    move_if_holding()

def hold_right():
    global held_direction
    held_direction = "right"
    move_if_holding()

def hold_down():
    global held_direction
    held_direction = "down"
    move_if_holding()

def hold_left():
    global held_direction
    held_direction = "left"
    move_if_holding()

def release_key():
    global held_direction
    held_direction = None

def restart_game():
    global maze, visited, player_x, player_y, start_time, game_running

    message_writer.clear()
    timer_writer.clear()
    drawer.clear()

    maze = [[[1, 1, 1, 1] for _ in range(COLS)] for _ in range(ROWS)]
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    player_x, player_y = 0, 0
    game_running = True
    start_time = time.time()

    carve_maze(0, 0)
    draw_maze()
    update_player()
    screen.update()  # force immediate redraw
    update_timer()

def main():
    carve_maze(0, 0)
    draw_maze()
    update_player()
    update_timer()

    screen.listen()
    screen.onkeypress(hold_up, "w")
    screen.onkeypress(hold_right, "d")
    screen.onkeypress(hold_down, "s")
    screen.onkeypress(hold_left, "a")

    screen.onkeyrelease(release_key, "w")
    screen.onkeyrelease(release_key, "a")
    screen.onkeyrelease(release_key, "s")
    screen.onkeyrelease(release_key, "d")

    screen.onkey(restart_game, "r")

    screen.mainloop()

if __name__ == "__main__":
    main()
