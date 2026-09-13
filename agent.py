import random
import math


class Agent:
    def __init__(self, agent_id, x, y, size=14):
        self.agent_id = agent_id
        self.x = x
        self.y = y

        self.size = size
        self.speed = random.uniform(1.5, 3.0)

        self.direction = random.uniform(0, math.tau)
        self.direction_timer = random.randint(10, 40)

        self.alive = True
        self.steps = 0

    def choose_action(self):
        self.direction_timer -= 1

        if self.direction_timer <= 0:
            self.direction = random.uniform(0, math.tau)
            self.direction_timer = random.randint(10, 40)

        return "move"

    def update(self, world):
        if not self.alive:
            return

        action = self.choose_action()

        if action == "move":
            self.move(world)

        self.steps += 1

    def move(self, world):
        new_x = self.x + math.cos(self.direction) * self.speed
        new_y = self.y + math.sin(self.direction) * self.speed

        if new_x - self.size < 0:
            new_x = self.size
            self.direction = math.pi - self.direction

        elif new_x + self.size > world.width:
            new_x = world.width - self.size
            self.direction = math.pi - self.direction

        if new_y - self.size < 0:
            new_y = self.size
            self.direction = -self.direction

        elif new_y + self.size > world.height:
            new_y = world.height - self.size
            self.direction = -self.direction

        self.x = new_x
        self.y = new_y