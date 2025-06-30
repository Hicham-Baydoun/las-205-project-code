import turtle
import random
import time
import winsound
from collections import deque

cell_size = 20
initial_maze_width = 21
initial_maze_height = 21
maze_increment = 2
level = 0
screen_width_limit = int(1920 * 0.8)
screen_height_limit = int(1080 * 0.8)
max_maze_width = (screen_width_limit - 40) // cell_size
max_maze_height = (screen_height_limit - 40) // cell_size
pixels_per_second = (20 * 5280 * 100) / 3600
frame_interval = 0.01
pixels_per_frame = pixels_per_second * frame_interval
total_score = 20

def carve_main_path(width, height):
    grid = [[0] * width for _ in range(height)]
    start = (0, height // 2)
    goal  = (width - 1, height // 2)
    visited = {start}
    path = [start]
    grid[start[1]][start[0]] = 1
    while path:
        x, y = path[-1]
        if (x, y) == goal:
            break
        neighbors = []
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<width and 0<=ny<height and (nx,ny) not in visited:
                neighbors.append((nx,ny,dx//2,dy//2))
        if not neighbors:
            path.pop()
        else:
            nx,ny,wx,wy = random.choice(neighbors)
            grid[y+wy][x+wx] = 1
            grid[ny][nx]     = 1
            visited.add((nx,ny))
            path.append((nx,ny))
    return grid, path

def add_dead_end_branches(grid, main_path, width, height, max_branches_per_cell=3, branch_len=(3,8)):
    dirs = [(-2,0),(2,0),(0,-2),(0,2)]
    for cx,cy in main_path:
        for _ in range(random.randint(1, max_branches_per_cell)):
            dx,dy = random.choice(dirs)
            x,y   = cx,cy
            carve_list = []
            for _ in range(random.randint(*branch_len)):
                nx,ny = x+dx, y+dy
                wx,wy = x+dx//2, y+dy//2
                if not (0<=nx<width and 0<=ny<height):
                    break
                if grid[wy][wx]==0 and grid[ny][nx]==0:
                    carve_list += [(wy,wx),(ny,nx)]
                    x,y = nx,ny
                else:
                    break
            for ry,rx in carve_list:
                grid[ry][rx] = 1

def find_path(grid, start, goal):
    W,H = len(grid[0]), len(grid)
    q = deque([start])
    parent = {start:None}
    while q:
        x,y = q.popleft()
        if (x,y)==goal: break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx,ny = x+dx,y+dy
            if 0<=nx<W and 0<=ny<H and grid[ny][nx]==1 and (nx,ny) not in parent:
                parent[(nx,ny)] = (x,y)
                q.append((nx,ny))
    path,cur = [], goal
    while cur:
        path.append(cur)
        cur = parent[cur]
    return list(reversed(path))

def prune_wall_clusters(grid, max_adjacent=4):
    H,W = len(grid), len(grid[0])
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    changed = True
    while changed:
        changed = False
        for y in range(H):
            for x in range(W):
                if grid[y][x]!=0: continue
                nbrs = [(y+dy,x+dx) for dy,dx in deltas
                        if 0<=y+dy<H and 0<=x+dx<W and grid[y+dy][x+dx]==0]
                if len(nbrs)>max_adjacent:
                    ry,rx = random.choice(nbrs)
                    grid[ry][rx] = 1
                    changed = True

def highlight_path(t, path_cells, width, height):
    if not path_cells: return
    t.hideturtle(); t.penup(); t.color("limegreen"); t.pensize(3)
    sx = -width*cell_size//2; sy = height*cell_size//2
    
    def to_screen(x,y):
        return (sx + x*cell_size + cell_size//2,
                sy - y*cell_size - cell_size//2)
    t.goto(*to_screen(*path_cells[0])); t.pendown()
    for x,y in path_cells[1:]:
        t.goto(*to_screen(x,y))
    t.penup()

def is_in_bounds(x, y, width, height):
    return 0<=x<width and 0<=y<height

def draw_maze(t, grid, width, height):
    t.hideturtle(); t.penup(); t.pensize(2)
    sx = -width*cell_size//2; sy = height*cell_size//2
    for y in range(height):
        for x in range(width):
            if grid[y][x]==0:
                px,py = sx+x*cell_size, sy-y*cell_size
                t.goto(px,py); t.pendown()
                for _ in range(4):
                    t.forward(cell_size); t.right(90)
                t.penup()

def move_to_grid(t, gx, gy, width, height):
    sx = -width*cell_size//2 + gx*cell_size + cell_size//2
    sy =  height*cell_size//2 - gy*cell_size - cell_size//2
    t.goto(sx,sy)

def can_move(x, y, grid, width, height):
    return is_in_bounds(x,y,width,height) and grid[y][x]==1

def animate_move_to_grid(t, gx, gy, width, height):
    sx = -width*cell_size//2 + gx*cell_size + cell_size//2
    sy =  height*cell_size//2 - gy*cell_size - cell_size//2
    dx,dy = sx-t.xcor(), sy-t.ycor()
    dist = (dx*dx+dy*dy)**0.5
    steps = max(int(dist/pixels_per_frame),1)
    dx/=steps; dy/=steps
    for _ in range(steps):
        t.setx(t.xcor()+dx); t.sety(t.ycor()+dy)
        turtle.update(); time.sleep(frame_interval)

def main():
    global level, screen, total_score
    level += 1
    maze_width  = min(initial_maze_width  + level*maze_increment, max_maze_width)
    maze_height = min(initial_maze_height + level*maze_increment, max_maze_height)
    screen = turtle.Screen()
    screen.setup(width=maze_width*cell_size+40, height=maze_height*cell_size+80)
    screen.title(f"Turtle Maze — Level {level}")
    screen.bgcolor("white")
    screen.tracer(0,0)
    grid, main_path = carve_main_path(maze_width, maze_height)
    add_dead_end_branches(grid, main_path, maze_width, maze_height)
    prune_wall_clusters(grid, max_adjacent=4)
    start = (0, maze_height//2)
    goal  = (maze_width-1, maze_height//2)
    solution = find_path(grid, start, goal)
    ideal_moves = len(solution)-1
    game_score  = ideal_moves
    moves_taken = 0
    status_t    = turtle.Turtle(visible=False)
    status_t.penup()
    status_t.goto(-maze_width*cell_size//2+10, maze_height*cell_size//2+10)

    def update_status():
        status_t.clear()
        status_t.write(f"Total: {total_score}   Moves left: {game_score}",align="left", font=("Arial",14,"normal"))
    update_status()
    highlighter = turtle.Turtle()
    highlight_path(highlighter, solution, maze_width, maze_height)
    drawer = turtle.Turtle()
    draw_maze(drawer, grid, maze_width, maze_height)
    border = turtle.Turtle()
    border.hideturtle(); border.pensize(3); border.color("red"); border.penup()
    px,py = maze_width*cell_size, maze_height*cell_size
    border.goto(-px//2, py//2); border.pendown()
    for dx,dy in [(px,0),(0,-py),(-px,0),(0,py)]:
        border.goto(border.xcor()+dx, border.ycor()+dy)
    for label, xpos in [("Reset", -200), ("Easy", -100), ("Medium", 100), ("Hard", 200)]:
        btn = turtle.Turtle(visible=False)
        btn.penup()
        btn.goto(xpos, -maze_height * cell_size // 2 - 60)
        btn.write(label, align="center", font=("Arial", 14, "bold"))

    def stamp(shape, color, cell):
        t = turtle.Turtle(visible=False)
        t.penup(); t.shape(shape); t.color(color)
        move_to_grid(t, cell[0], cell[1], maze_width, maze_height)
        t.stamp()
    stamp("circle","green", start)
    stamp("square","red",   goal)
    screen.update()
    screen.tracer(1,10)
    player = turtle.Turtle("turtle")
    player.color("blue"); player.pensize(3)
    player.penup(); player.speed(0)
    player_x,player_y = start
    move_to_grid(player, player_x, player_y, maze_width, maze_height)
    player.pendown()
    message_drawn = False
    btn = turtle.Turtle(visible=False)
    btn.penup()
    btn.goto(0, -maze_height*cell_size//2 - 60)
    btn.write("Next Maze", align="center", font=("Arial",14,"bold"))

    def move(dx, dy, heading):
        nonlocal player_x, player_y, message_drawn, game_score, moves_taken
        global total_score
        nx,ny = player_x+dx, player_y+dy
        if can_move(nx,ny,grid,maze_width,maze_height):
            player.setheading(heading)
            player_x,player_y = nx,ny
            player.pendown()
            moves_taken += 1
            game_score  -= 1
            update_status()
            animate_move_to_grid(player, nx, ny, maze_width, maze_height)
            if (nx,ny)==goal and not message_drawn:
                winsound.PlaySound(None, winsound.SND_PURGE)
                if game_score==0:
                    total_score += 20
                elif game_score<0:
                    total_score -= -game_score
                if total_score >= 0:
                    winsound.PlaySound("drums-audiomass-output.wav", winsound.SND_ALIAS|winsound.SND_ASYNC)
                if total_score <= 0:
                    btn.clear()
                    box = turtle.Turtle(visible=False)
                    box.penup()
                    box.goto(-200, 80)
                    box.pendown()
                    box.pencolor("red")
                    box.fillcolor("white")
                    box.begin_fill()
                    for _ in range(2):
                        box.forward(400)
                        box.right(90)
                        box.forward(240)
                        box.right(90)
                    box.end_fill()
                    box.penup()
                    popup = turtle.Turtle(visible=False)
                    popup.penup()
                    popup.goto(0,  40)
                    popup.color("red")
                    popup.write("GAME OVER", align="center", font=("Arial",24,"bold"))
                    popup.color("black")
                    stats = [
                        f"Level reached: {level}",
                        f"Ideal moves  : {ideal_moves}",
                        f"Moves taken  : {moves_taken}",
                        f"Total Score  : {total_score}"
                    ]
                    y = 0
                    winsound.PlaySound(
                        "audiomass-output.wav",
                        winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
                    for line in stats:
                        popup.goto(0, y)
                        popup.write(line, align="center", font=("Arial",16,"normal"))
                        y -= 30

                    popup.goto(0, y - 20)
                    popup.color("blue")
                    popup.write("Play Again", align="center", font=("Arial",18,"bold"))
                else:
                    w = turtle.Turtle(visible=False)
                    w.penup()
                    w.color("green")
                    w.goto(0, -maze_height*cell_size//2 - 30)
                    if game_score == 0:
                        msg = f"Ideal used! +20 → Total: {total_score}"
                    else:
                        pen = -game_score
                        msg = f"Overshot {pen} moves. -{pen} → Total: {total_score}"
                    w.write(msg, align="center", font=("Arial",16,"bold"))
                message_drawn = True

    def game_loop():
        if flags["up"]:
            move(0, 1, 270)
        elif flags["down"]:
            move(0, -1, 90)
        elif flags["left"]:
            move(-1, 0, 180)
        elif flags["right"]:
            move(1, 0, 0)
        screen.ontimer(game_loop, int(frame_interval*1000))
    flags = {"up":False,"down":False,"left":False,"right":False}
    screen.listen()
    screen.onkeypress(lambda: flags.update(up=True),    "s")
    screen.onkeyrelease(lambda: flags.update(up=False), "s")
    screen.onkeypress(lambda: flags.update(down=True),  "w")
    screen.onkeyrelease(lambda: flags.update(down=False),"w")
    screen.onkeypress(lambda: flags.update(left=True),  "a")
    screen.onkeyrelease(lambda: flags.update(left=False),"a")
    screen.onkeypress(lambda: flags.update(right=True), "d")
    screen.onkeyrelease(lambda: flags.update(right=False),"d")

    def click_handler(x, y):
        global total_score, level
        if total_score > 0 and -60 < x < 60 and \
                -maze_height * cell_size // 2 - 80 < y < -maze_height * cell_size // 2 - 40:
            screen.clearscreen()
            main()
        if total_score <= 0 and abs(x) < 100 and -160 < y < -120:
            level = 0
            total_score = 20
            screen.clearscreen()
            main()
        if -220 < x < -180 and -maze_height * cell_size // 2 - 80 < y < -maze_height * cell_size // 2 - 40:
            screen.clearscreen()
            level -= 1
            main()
        if -120 < x < -80 and -maze_height * cell_size // 2 - 80 < y < -maze_height * cell_size // 2 - 40:
            level = 0
            total_score = 20
            screen.clearscreen()
            main()
        if 80 < x < 120 and -maze_height * cell_size // 2 - 80 < y < -maze_height * cell_size // 2 - 40:
            level = 9
            total_score = 20
            screen.clearscreen()
            main()
        if 180 < x < 220 and -maze_height * cell_size // 2 - 80 < y < -maze_height * cell_size // 2 - 40:
            level = 14
            total_score = 20
            screen.clearscreen()
            main()

    screen.onclick(click_handler)
    game_loop()
    turtle.done()

if __name__ == "__main__":
    main()
