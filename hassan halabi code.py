import turtle
import time
import random

# Global variables
selected_difficulty = None
start_time = None
current_maze = []
player_position = [0, 0]
button_turtles = []
player = None
game_won = False
timer_started = False
timer_display = turtle.Turtle()
high_scores = {"Easy": None, "Medium": None, "Hard": None}

# === MAZE GENERATION FUNCTIONS ===

def generate_easy_maze(rows, cols):

    # Ensure odd dimensions for proper maze generation
    if rows % 2 == 0: rows += 1
    if cols % 2 == 0: cols += 1

    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    def carve(r, c):
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows and 0 < nc < cols and maze[nr][nc] == 1:
                maze[nr][nc] = 0
                maze[r + dr // 2][c + dc // 2] = 0
                carve(nr, nc)
                # Early termination sometimes to create simpler paths
                if random.random() < 0.4:
                    break

    # Start carving near the entrance to ensure connection
    start_row, start_col = 1, 1
    maze[start_row][start_col] = 0
    carve(start_row, start_col)

    # Ensure exit is reachable by carving a direct path if needed
    exit_row, exit_col = rows - 2, cols - 2
    if maze[exit_row][exit_col] == 1:
        # Connect exit to the nearest path
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if maze[exit_row + dr][exit_col + dc] == 0:
                maze[exit_row][exit_col] = 0
                break

    # Set entrance and exit
    maze[1][0] = 0  # Entrance
    maze[rows - 2][cols - 1] = 2  # Exit

    # Final check to ensure path exists
    if not is_path_available(maze, (1, 0), (rows - 2, cols - 1)):
        # If not, regenerate (recursion with limit to prevent stack overflow)
        return generate_easy_maze(rows, cols)

    return maze, [1, 0]


def generate_medium_maze(rows, cols):
    if rows % 2 == 0: rows += 1
    if cols % 2 == 0: cols += 1
    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    def carve(r, c):
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows and 0 < nc < cols and maze[nr][nc] == 1:
                maze[nr][nc] = 0
                maze[r + dr // 2][c + dc // 2] = 0
                carve(nr, nc)

    carve(1, 1)
    maze[1][0] = 0
    maze[rows - 2][cols - 1] = 2  # Red exit square
    return maze, [1, 0]


def generate_hard_maze(rows, cols):

    # Ensure odd dimensions
    if rows % 2 == 0: rows += 1
    if cols % 2 == 0: cols += 1

    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    def carve(r, c):
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows and 0 < nc < cols and maze[nr][nc] == 1:
                maze[nr][nc] = 0
                maze[r + dr // 2][c + dc // 2] = 0
                carve(nr, nc)

    # Start carving from multiple points to create complexity
    start_points = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
    for r, c in start_points:
        if maze[r][c] == 1:
            maze[r][c] = 0
            carve(r, c)

    # Add some loops but ensure solvability
    added_walls = 0
    for _ in range((rows * cols) // 8):  # Fewer loops than before
        r = random.randrange(1, rows - 1)
        c = random.randrange(1, cols - 1)
        if maze[r][c] == 1:
            # Only remove walls that don't completely block paths
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if maze[r + dr][c + dc] == 0:
                    neighbors.append((r + dr, c + dc))
            if len(neighbors) >= 2:
                # Check if removing this wall would create an unsolvable maze
                temp_maze = [row[:] for row in maze]
                temp_maze[r][c] = 0
                if is_path_available(temp_maze, (1, 0), (rows - 2, cols - 1)):
                    maze[r][c] = 0
                    added_walls += 1

    # Set entrance and exit
    maze[1][0] = 0  # Entrance
    maze[rows - 2][cols - 1] = 2  # Exit

    # Final check to ensure path exists
    if not is_path_available(maze, (1, 0), (rows - 2, cols - 1)):
        # If not, regenerate (recursion with limit to prevent stack overflow)
        return generate_hard_maze(rows, cols)

    return maze, [1, 0]


def is_path_available(maze, start, end):
    """BFS to check if path exists from start to end"""
    rows, cols = len(maze), len(maze[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    queue = [start]
    visited[start[0]][start[1]] = True

    while queue:
        r, c = queue.pop(0)

        # Check if we've reached the exit
        if (r, c) == end:
            return True

        # Check all four directions
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and
                    not visited[nr][nc] and maze[nr][nc] != 1):
                visited[nr][nc] = True
                queue.append((nr, nc))

    return False


# === DRAWING FUNCTIONS ===

def draw_square(t, x, y, color, size):
    t.penup()
    t.goto(x, y)
    t.setheading(0)
    t.fillcolor(color)
    t.begin_fill()
    for _ in range(4):
        t.forward(size)
        t.right(90)
    t.end_fill()


def draw_maze(maze, cell_size):
    turtle.tracer(0, 0)
    draw = turtle.Turtle()
    draw.speed(0)
    draw.hideturtle()

    start_x = -cell_size * len(maze[0]) // 2
    start_y = cell_size * len(maze) // 2

    for row in range(len(maze)):
        for col in range(len(maze[0])):
            x = start_x + col * cell_size
            y = start_y - row * cell_size
            if maze[row][col] == 1:  # Wall
                draw_square(draw, x, y, "gray", cell_size)
            elif maze[row][col] == 0:  # Path
                draw_square(draw, x, y, "white", cell_size)
            elif maze[row][col] == 2:  # Exit
                draw_square(draw, x, y, "red", cell_size)

    # Draw player start position (green square)
    start_x_player = start_x + player_position[1] * cell_size
    start_y_player = start_y - player_position[0] * cell_size
    draw_square(draw, start_x_player, start_y_player, "lightgreen", cell_size)
    turtle.tracer(1, 10)
    turtle.update()


# === PLAYER FUNCTIONS ===

def setup_player(cell_size):
    """Initialize the player turtle"""
    global player

    if player is not None:
        player.hideturtle()

    player = turtle.Turtle()
    player.shape("turtle")
    player.color("blue")
    player.penup()
    player.speed(1)

    start_x = -cell_size * len(current_maze[0]) // 2
    start_y = cell_size * len(current_maze) // 2
    player_x = start_x + (player_position[1] + 0.5) * cell_size
    player_y = start_y - (player_position[0] + 0.5) * cell_size

    player.goto(player_x, player_y)
    player.showturtle()


def move(d_row, d_col, cell_size):
    """Move player turtle"""
    global player_position, timer_started, start_time, game_won

    if game_won:  # Don't move after winning
        return

    new_row = player_position[0] + d_row
    new_col = player_position[1] + d_col

    if 0 <= new_row < len(current_maze) and 0 <= new_col < len(current_maze[0]):
        if current_maze[new_row][new_col] != 1:  # Not a wall
            if not timer_started:
                timer_started = True
                start_time = time.time()
                draw_timer()

            player_position = [new_row, new_col]

            # Calculate new position
            start_x = -cell_size * len(current_maze[0]) // 2
            start_y = cell_size * len(current_maze) // 2
            new_x = start_x + (new_col + 0.5) * cell_size
            new_y = start_y - (new_row + 0.5) * cell_size

            player.goto(new_x, new_y)

            if current_maze[new_row][new_col] == 2:  # Exit
                player_won()


def reset_player_position(cell_size):
    global player_position

    if selected_difficulty == "Easy":

        player_position = [1, 0]
    else:

        player_position = [1, 0]

    setup_player(cell_size)


# === UI FUNCTIONS ===

def create_button(label, x, y, color, command):
    """Create a clickable button"""
    btn = turtle.Turtle()
    btn.shape("square")
    btn.shapesize(stretch_wid=1.5, stretch_len=6)
    btn.color("black", color)
    btn.penup()
    btn.goto(x, y)
    btn.onclick(lambda x, y: command())

    label_turtle = turtle.Turtle()
    label_turtle.hideturtle()
    label_turtle.penup()
    label_turtle.color("black")
    label_turtle.goto(x, y - 10)
    label_turtle.write(label, align="center", font=("Arial", 12, "bold"))

    button_turtles.extend([btn, label_turtle])
    return btn


def clear_buttons():
    """Remove all buttons"""
    for btn in button_turtles:
        btn.hideturtle()
    button_turtles.clear()


def draw_timer():
    """Initialize timer display"""
    timer_display.hideturtle()
    timer_display.penup()
    timer_display.goto(0, 280)
    update_timer()


def update_timer():
    """Update the timer display"""
    if selected_difficulty and not game_won and timer_started:
        elapsed = int(time.time() - start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        timer_display.clear()
        timer_display.write(f"Time: {minutes}m {seconds}s",
                            align="center", font=("Arial", 14, "bold"))
        turtle.ontimer(update_timer, 1000)


def player_won():
    """Handle win condition"""
    global game_won, high_scores

    game_won = True
    turtle.onkey(None, "Up")
    turtle.onkey(None, "Down")
    turtle.onkey(None, "Left")
    turtle.onkey(None, "Right")

    elapsed = int(time.time() - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60

    # Update high score if this time is better
    if (high_scores[selected_difficulty] is None or
            elapsed < high_scores[selected_difficulty]):
        high_scores[selected_difficulty] = elapsed

    win = turtle.Turtle()
    win.hideturtle()
    win.penup()
    win.goto(0, 230)  # Positioned below timer
    win.color("green")
    win.write(f"Congratulations! You won in {minutes}m {seconds}s!",
              align="center", font=("Arial", 18, "bold"))

    # Victory spin
    for _ in range(12):
        player.right(30)

    # Add Play Again button while keeping existing buttons
    create_button("Play Again", 0, -180, "blue",
                  lambda: start_game(selected_difficulty))


def draw_high_score():
    """Display the current high score for the selected difficulty"""
    hs_turtle = turtle.Turtle()
    hs_turtle.hideturtle()
    hs_turtle.penup()
    hs_turtle.goto(300, 350)  # Top right corner

    if high_scores[selected_difficulty] is not None:
        minutes = high_scores[selected_difficulty] // 60
        seconds = high_scores[selected_difficulty] % 60
        hs_turtle.write(f"Best: {minutes}m {seconds}s",
                        align="right", font=("Arial", 12, "normal"))


# === GAME CONTROL FUNCTIONS ===

def start_game(difficulty):
    """Initialize or restart the game"""
    global current_maze, player_position, player, selected_difficulty
    global game_won, timer_started

    # Reset game state
    selected_difficulty = difficulty
    game_won = False
    timer_started = False

    # Clear previous elements
    if player is not None:
        player.hideturtle()
    turtle.clearscreen()
    turtle.bgcolor("white")
    turtle.title("Maze Game")

    # Set maze dimensions
    if difficulty == "Easy":
        rows, cols = 11, 11
        cell_size = 30
    elif difficulty == "Medium":
        rows, cols = 21, 21
        cell_size = 20
    else:  # Hard
        rows, cols = 31, 31
        cell_size = 15

    # Set window size
    turtle.setup(width=800, height=800)

    # Generate maze
    if difficulty == "Easy":
        current_maze, player_position = generate_easy_maze(rows, cols)
    elif difficulty == "Medium":
        current_maze, player_position = generate_medium_maze(rows, cols)
    else:
        current_maze, player_position = generate_hard_maze(rows, cols)

    # Draw game elements
    draw_maze(current_maze, cell_size)
    setup_player(cell_size)

    # Create control buttons
    maze_bottom = -cell_size * rows // 2

    # Restart button (top left)
    create_button("Restart", -350, 350, "orange",
                  lambda: reset_player_position(cell_size))

    # New Maze button
    create_button("New Maze", 0, maze_bottom - 50, "blue",
                  lambda: start_game(difficulty))

    # Difficulty switcher buttons
    other_diffs = [d for d in ["Easy", "Medium", "Hard"] if d != difficulty]
    colors = {"Easy": "lightgreen", "Medium": "gold", "Hard": "salmon"}
    for i, level in enumerate(other_diffs):
        x_pos = -100 + (i * 200)
        create_button(level, x_pos, maze_bottom - 100, colors[level],
                      lambda l=level: start_game(l))

    # Set up controls
    turtle.listen()
    turtle.onkey(lambda: move(-1, 0, cell_size), "Up")
    turtle.onkey(lambda: move(1, 0, cell_size), "Down")
    turtle.onkey(lambda: move(0, -1, cell_size), "Left")
    turtle.onkey(lambda: move(0, 1, cell_size), "Right")

    # Initialize timer
    draw_timer()
    draw_high_score()

def draw_main_menu():
    """Draw the main menu screen"""
    turtle.clearscreen()
    turtle.bgcolor("white")
    turtle.title("Maze Game")

    # Title
    title = turtle.Turtle()
    title.hideturtle()
    title.penup()
    title.goto(0, 100)
    title.write("Maze Game", align="center", font=("Arial", 36, "bold"))

    # Subtitle
    subtitle = turtle.Turtle()
    subtitle.hideturtle()
    subtitle.penup()
    subtitle.goto(0, 60)
    subtitle.write("Select Difficulty", align="center", font=("Arial", 18, "normal"))

    # Difficulty buttons
    create_button("Easy", 0, 0, "lightgreen", lambda: start_game("Easy"))
    create_button("Medium", 0, -60, "gold", lambda: start_game("Medium"))
    create_button("Hard", 0, -120, "salmon", lambda: start_game("Hard"))


# === START THE GAME ===
draw_main_menu()
turtle.mainloop()