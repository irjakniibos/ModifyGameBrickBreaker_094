import tkinter as tk
import random
import math

# Basic game object class
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item
 
    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

# Ball movement class
class Ball(GameObject):
    def __init__(self, canvas, x, y, game_instance):
        self.radius = 10
        self.direction = [1, -1]  # ball movement direction (horizontal, vertical)
        self.speed = 5  # Ball speed
        self.game = game_instance  # Reference to game instance
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#6A5ACD')  # Slate blue ball
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # Ball bounce on left or right screen
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Ball bounce on top of screen
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit(self.game)
            if isinstance(game_object, PowerUp):
                game_object.activate(self)

# Paddle controlled by player
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#4169E1')  # Royal blue paddle
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

# Destructible brick class
class Brick(GameObject):
    COLORS = {1: '#9370DB', 2: '#7B68EE', 3: '#6A5ACD'}  # Purple shades
    SCORES = {1: 10, 2: 20, 3: 30}  # Score for each brick type

    def __init__(self, canvas, x, y, hits, game_instance):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.game = game_instance  # Store reference to game instance
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)
        self.canvas = canvas
        self.x = x
        self.y = y
        self.score = Brick.SCORES[hits]

    def hit(self, game_instance=None):
        self.hits -= 1
        if self.hits == 0:
            # Use the game instance passed or previously stored
            game = game_instance or self.game
            game.update_score(self.score)
            
            self.create_explosion()
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])

    def create_explosion(self):
        # Explosion animation
        for i in range(10):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 30)
            dx = distance * math.cos(angle)
            dy = distance * math.sin(angle)
            
            # Explosion particle colors
            colors = ['#FF6347', '#FFD700', '#FF4500', '#FF8C00']
            color = random.choice(colors)
            
            particle = self.canvas.create_oval(
                self.x + dx - 3, 
                self.y + dy - 3, 
                self.x + dx + 3, 
                self.y + dy + 3, 
                fill=color
            )
            
            # Animate particle
            self.animate_particle(particle, dx, dy)

    def animate_particle(self, particle, dx, dy):
        def move_particle():
            nonlocal dx, dy
            self.canvas.move(particle, dx, dy)
            dx *= 0.9  # Gradual slowdown
            dy *= 0.9
            
            # Fade out
            current_color = self.canvas.itemcget(particle, 'fill')
            r, g, b = self.hex_to_rgb(current_color)
            alpha = max(0, int(float(self.canvas.itemcget(particle, 'tags').split()[-1] or 1.0) - 0.1) * 10)
            new_color = self.rgb_to_hex(r, g, b, alpha)
            self.canvas.itemconfig(particle, fill=new_color, tags=str(alpha))
            
            if alpha > 0:
                self.canvas.after(50, move_particle)
            else:
                self.canvas.delete(particle)

        self.canvas.after(50, move_particle)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, r, g, b, alpha=1.0):
        r = max(0, min(255, int(r * alpha)))
        g = max(0, min(255, int(g * alpha)))
        b = max(0, min(255, int(b * alpha)))
        return f'#{r:02x}{g:02x}{b:02x}'

# Power-up class
class PowerUp(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 20
        self.height = 20
        self.effect = random.choice(['expand', 'extra_ball'])  # Random effect
        item = canvas.create_oval(x - self.width / 2, y - self.height / 2,
                                  x + self.width / 2, y + self.height / 2,
                                  fill='#32CD32', tags='powerup')  # Lime green
        super(PowerUp, self).__init__(canvas, item)

    def activate(self, ball):
        if self.effect == 'expand':
            paddle_coords = ball.canvas.find_withtag('paddle')
            ball.canvas.coords(paddle_coords, -40, 20, 120, 40)
        elif self.effect == 'extra_ball':
            new_ball = Ball(ball.canvas, ball.get_position()[0] + 20, ball.get_position()[1] + 20, ball.game)
            new_ball.update()

# Main game class
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.score = 0  # Add score tracking
        self.canvas = tk.Canvas(self, bg='#E6E6FA',  # Lavender background
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        # Adding bricks with different durability
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.score_text = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.update_score_text()
        self.text = self.draw_text(300, 200, 'Press Space to Start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310, self)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits, self)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Arial', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def update_score_text(self):
        text = 'Score: %s' % self.score
        if self.score_text is None:
            self.score_text = self.draw_text(540, 20, text, 15)
        else:
            self.canvas.itemconfig(self.score_text, text=text)

    def update_score(self, points):
        self.score += points
        self.update_score_text()

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(300, 200, f'Congratulations! You Won!\nFinal Score: {self.score}')
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, f'Game Over! Try Again!\nFinal Score: {self.score}')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker Challenge')
    game = Game(root)
    root.mainloop()