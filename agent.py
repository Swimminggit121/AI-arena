import random
import math


class Agent:
    STATES = [
        "idle",
        "wandering",
        "exploring",
        "investigating",
        "chasing",
        "fleeing",
        "resting",
        "dead",
    ]

    PERSONALITIES = [
        "aggressive",
        "defensive",
        "explorer",
        "balanced",
    ]

    def __init__(self, agent_id, x, y, size=14, personality=None):
        self.agent_id = agent_id

        self.x = float(x)
        self.y = float(y)

        self.size = size

        self.personality = (
            personality
            if personality in self.PERSONALITIES
            else random.choice(self.PERSONALITIES)
        )

        self.alive = True

        self.health = 100.0
        self.max_health = 100.0

        self.energy = random.uniform(75.0, 100.0)
        self.max_energy = 100.0

        self.hunger = random.uniform(0.0, 20.0)
        self.max_hunger = 100.0

        self.age = 0
        self.max_age = random.randint(25000, 40000)

        self.speed = random.uniform(1.5, 3.0)

        self.acceleration = random.uniform(0.05, 0.15)

        self.max_speed = self.speed + random.uniform(0.5, 1.5)

        self.direction = random.uniform(0, math.tau)

        self.turn_speed = random.uniform(0.03, 0.12)

        self.direction_timer = random.randint(10, 40)

        self.vision_range = random.uniform(130.0, 180.0)

        self.hearing_range = random.uniform(80.0, 140.0)

        self.memory = []

        self.memory_limit = 20

        self.target = None

        self.last_target = None

        self.state = "wandering"

        self.previous_state = "wandering"

        self.state_timer = random.randint(20, 60)

        self.decision_timer = 0

        self.decision_interval = random.randint(5, 15)

        self.wander_target = None

        self.wander_timer = 0

        self.investigation_target = None

        self.investigation_timer = 0

        self.flee_timer = 0

        self.rest_timer = 0

        self.threat_level = 0.0

        self.curiosity = random.uniform(0.2, 1.0)

        self.aggression = random.uniform(0.2, 1.0)

        self.caution = random.uniform(0.2, 1.0)

        self.bravery = random.uniform(0.2, 1.0)

        self.intelligence = random.uniform(0.2, 1.0)

        self.stubbornness = random.uniform(0.1, 0.8)

        self.randomness = random.uniform(0.1, 0.6)

        self.steps = 0

        self.distance_travelled = 0.0

        self.decisions_made = 0

        self.state_changes = 0

        self.times_seen = 0

        self.times_threatened = 0

        self.times_fled = 0

        self.times_chased = 0

        self.times_resting = 0

        self.times_investigated = 0

        self.damage_taken = 0.0

        self.damage_dealt = 0.0

        self.kills = 0

        self.events = []

        self.event_limit = 50

    def log_event(self, message):
        event = {
            "tick": self.steps,
            "message": message,
        }

        self.events.append(event)

        if len(self.events) > self.event_limit:
            self.events.pop(0)

    def distance_to(self, other):
        if other is None:
            return float("inf")

        dx = other.x - self.x
        dy = other.y - self.y

        return math.sqrt(
            dx * dx + dy * dy
        )

    def distance_to_point(self, x, y):
        dx = x - self.x
        dy = y - self.y

        return math.sqrt(
            dx * dx + dy * dy
        )

    def angle_to(self, other):
        if other is None:
            return self.direction

        return math.atan2(
            other.y - self.y,
            other.x - self.x
        )

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= math.tau

        while angle < -math.pi:
            angle += math.tau

        return angle

    def turn_towards(self, angle):
        difference = self.normalize_angle(
            angle - self.direction
        )

        if abs(difference) <= self.turn_speed:
            self.direction = angle
            return

        if difference > 0:
            self.direction += self.turn_speed
        else:
            self.direction -= self.turn_speed

        self.direction %= math.tau

    def set_state(self, new_state):
        if new_state not in self.STATES:
            return

        if new_state == self.state:
            return

        self.previous_state = self.state
        self.state = new_state

        self.state_changes += 1

        self.state_timer = random.randint(20, 60)

        if new_state == "fleeing":
            self.times_fled += 1

        elif new_state == "chasing":
            self.times_chased += 1

        elif new_state == "resting":
            self.times_resting += 1

        elif new_state == "investigating":
            self.times_investigated += 1

        self.log_event(
            f"State changed: {self.previous_state} -> {new_state}"
        )

    def look(self, world):
        visible_agents = []

        closest_agent = None
        closest_distance = float("inf")

        strongest_threat = None
        strongest_threat_value = 0.0

        for other in world.agents:
            if other is self:
                continue

            if not other.alive:
                continue

            distance = self.distance_to(other)

            if distance <= self.vision_range:
                visible_agents.append(other)

                self.times_seen += 1

                if distance < closest_distance:
                    closest_distance = distance
                    closest_agent = other

                threat = self.evaluate_threat(other, distance)

                if threat > strongest_threat_value:
                    strongest_threat_value = threat
                    strongest_threat = other

        self.memory = visible_agents[:self.memory_limit]

        self.threat_level = strongest_threat_value

        if strongest_threat is not None:
            self.target = strongest_threat

        elif closest_agent is not None:
            self.target = closest_agent

        else:
            self.target = None

    def evaluate_threat(self, other, distance):
        threat = 0.0

        health_difference = (
            other.health - self.health
        )

        if health_difference > 0:
            threat += 0.25

        if other.aggression > self.aggression:
            threat += 0.25

        if other.speed > self.speed:
            threat += 0.1

        if distance < self.vision_range * 0.35:
            threat += 0.25

        if other.personality == "aggressive":
            threat += 0.2

        if self.personality == "aggressive":
            threat *= 0.6

        elif self.personality == "defensive":
            threat *= 1.25

        return max(0.0, min(1.0, threat))

    def choose_action(self):
        self.decision_timer -= 1

        if self.decision_timer > 0:
            return self.state

        self.decision_timer = self.decision_interval

        self.decisions_made += 1

        if self.energy < 15:
            self.set_state("resting")
            return "rest"

        if self.health < 25:
            if self.bravery < 0.5:
                self.set_state("fleeing")
                return "flee"

        if self.threat_level > 0.65:
            if self.bravery < 0.45:
                self.set_state("fleeing")
                return "flee"

        if self.target is not None:
            if self.personality == "aggressive":
                self.set_state("chasing")
                return "chase"

            if self.personality == "defensive":
                if self.threat_level > 0.5:
                    self.set_state("fleeing")
                    return "flee"

                self.set_state("investigating")
                return "investigate"

            if self.personality == "explorer":
                if self.curiosity > 0.6:
                    self.set_state("investigating")
                    return "investigate"

            if self.personality == "balanced":
                if self.threat_level > 0.55:
                    self.set_state("fleeing")
                    return "flee"

                if self.aggression > 0.65:
                    self.set_state("chasing")
                    return "chase"

        if self.hunger > 75:
            self.set_state("exploring")
            return "explore"

        if random.random() < self.randomness:
            self.set_state("wandering")
            return "wander"

        self.set_state("exploring")

        return "explore"

    def update(self, world):
        if not self.alive:
            return

        self.steps += 1

        self.age += 1

        self.state_timer -= 1

        self.update_needs()

        self.look(world)

        action = self.choose_action()

        if action == "move":
            self.move(world)

        elif action == "wander":
            self.wander(world)

        elif action == "explore":
            self.explore(world)

        elif action == "investigate":
            self.investigate(world)

        elif action == "chase":
            self.chase(world)

        elif action == "flee":
            self.flee(world)

        elif action == "rest":
            self.rest()

        self.update_energy()

        self.check_survival()

    def update_needs(self):
        self.hunger += 0.015

        if self.hunger > self.max_hunger:
            self.hunger = self.max_hunger

    def update_energy(self):
        movement_cost = 0.015

        if self.state == "chasing":
            movement_cost = 0.04

        elif self.state == "fleeing":
            movement_cost = 0.06

        elif self.state == "exploring":
            movement_cost = 0.025

        elif self.state == "resting":
            movement_cost = -0.08

        self.energy -= movement_cost

        self.energy = max(
            0.0,
            min(self.max_energy, self.energy)
        )

    def check_survival(self):
        if self.health <= 0:
            self.die("health reached zero")
            return

        if self.energy <= 0:
            self.health -= 0.05

        if self.hunger >= self.max_hunger:
            self.health -= 0.02

        if self.age >= self.max_age:
            self.die("reached maximum age")

    def die(self, reason="unknown"):
        if not self.alive:
            return

        self.alive = False
        self.health = 0

        self.set_state("dead")

        self.log_event(
            f"Died: {reason}"
        )

    def wander(self, world):
        self.wander_timer -= 1

        if (
            self.wander_target is None
            or self.wander_timer <= 0
        ):
            margin = 80

            self.wander_target = (
                random.uniform(
                    margin,
                    world.width - margin
                ),
                random.uniform(
                    margin,
                    world.height - margin
                ),
            )

            self.wander_timer = random.randint(
                40,
                120
            )

        target_x, target_y = self.wander_target

        angle = math.atan2(
            target_y - self.y,
            target_x - self.x
        )

        self.turn_towards(angle)

        self.move(world)

    def explore(self, world):
        if self.target is not None:
            distance = self.distance_to(
                self.target
            )

            if distance < self.vision_range:
                self.investigate(world)
                return

        if self.wander_target is None:
            margin = 50

            self.wander_target = (
                random.uniform(
                    margin,
                    world.width - margin
                ),
                random.uniform(
                    margin,
                    world.height - margin
                ),
            )

            self.wander_timer = random.randint(
                60,
                150
            )

        self.wander(world)

    def investigate(self, world):
        if self.target is None:
            self.set_state("exploring")
            self.explore(world)
            return

        if not self.target.alive:
            self.target = None
            self.set_state("exploring")
            return

        angle = self.angle_to(
            self.target
        )

        self.turn_towards(angle)

        distance = self.distance_to(
            self.target
        )

        if distance > self.size * 3:
            self.move(world)

        else:
            self.set_state("idle")

    def chase(self, world):
        if self.target is None:
            self.set_state("exploring")
            return

        if not self.target.alive:
            self.target = None
            self.set_state("exploring")
            return

        angle = self.angle_to(
            self.target
        )

        self.turn_towards(angle)

        self.speed = min(
            self.max_speed,
            self.speed + self.acceleration
        )

        self.move(world)

    def flee(self, world):
        if self.target is None:
            self.set_state("exploring")
            return

        if not self.target.alive:
            self.target = None
            self.set_state("exploring")
            return

        angle = self.angle_to(
            self.target
        )

        flee_angle = angle + math.pi

        self.turn_towards(
            flee_angle
        )

        self.speed = min(
            self.max_speed,
            self.speed + self.acceleration * 1.5
        )

        self.move(world)

        self.flee_timer += 1

        if self.flee_timer > 100:
            self.flee_timer = 0
            self.set_state("wandering")

    def rest(self):
        self.speed *= 0.95

        if self.speed < 0.1:
            self.speed = 0.1

        self.energy += 0.15

        if self.energy > self.max_energy:
            self.energy = self.max_energy

        if self.energy > 70:
            self.set_state("wandering")

    def move(self, world):
        old_x = self.x
        old_y = self.y

        new_x = (
            self.x
            + math.cos(self.direction)
            * self.speed
        )

        new_y = (
            self.y
            + math.sin(self.direction)
            * self.speed
        )

        bounced = False

        if new_x - self.size < 0:
            new_x = self.size

            self.direction = (
                math.pi - self.direction
            )

            bounced = True

        elif new_x + self.size > world.width:
            new_x = (
                world.width
                - self.size
            )

            self.direction = (
                math.pi - self.direction
            )

            bounced = True

        if new_y - self.size < 0:
            new_y = self.size

            self.direction = (
                -self.direction
            )

            bounced = True

        elif new_y + self.size > world.height:
            new_y = (
                world.height
                - self.size
            )

            self.direction = (
                -self.direction
            )

            bounced = True

        self.x = new_x
        self.y = new_y

        distance_moved = math.sqrt(
            (self.x - old_x) ** 2
            + (self.y - old_y) ** 2
        )

        self.distance_travelled += (
            distance_moved
        )

        if bounced:
            self.direction %= math.tau

    def get_status(self):
        return {
            "id": self.agent_id,
            "alive": self.alive,
            "health": round(self.health, 1),
            "energy": round(self.energy, 1),
            "hunger": round(self.hunger, 1),
            "age": self.age,
            "state": self.state,
            "personality": self.personality,
            "speed": round(self.speed, 2),
            "vision": round(self.vision_range, 1),
            "memory_size": len(self.memory),
            "target": (
                self.target.agent_id
                if self.target is not None
                else None
            ),
            "steps": self.steps,
            "distance": round(
                self.distance_travelled,
                1
            ),
        }

    def get_recent_events(self, count=10):
        if count <= 0:
            return []

        return self.events[-count:]

    def is_low_health(self):
        return (
            self.health
            <= self.max_health * 0.25
        )

    def is_low_energy(self):
        return (
            self.energy
            <= self.max_energy * 0.2
        )

    def is_hungry(self):
        return (
            self.hunger
            >= self.max_hunger * 0.7
        )

    def get_health_ratio(self):
        if self.max_health <= 0:
            return 0

        return (
            self.health
            / self.max_health
        )

    def get_energy_ratio(self):
        if self.max_energy <= 0:
            return 0

        return (
            self.energy
            / self.max_energy
        )

    def get_hunger_ratio(self):
        if self.max_hunger <= 0:
            return 0

        return (
            self.hunger
            / self.max_hunger
        )

    def reset_target(self):
        self.target = None
        self.investigation_target = None

    def clear_memory(self):
        self.memory.clear()

    def remember(self, item):
        if item in self.memory:
            return

        self.memory.append(item)

        if len(self.memory) > self.memory_limit:
            self.memory.pop(0)

    def get_nearest_agent(self):
        if not self.memory:
            return None

        nearest = None
        nearest_distance = float("inf")

        for agent in self.memory:
            distance = self.distance_to(agent)

            if distance < nearest_distance:
                nearest = agent
                nearest_distance = distance

        return nearest

    def get_strongest_threat(self):
        strongest = None
        strongest_value = 0.0

        for agent in self.memory:
            distance = self.distance_to(agent)

            threat = self.evaluate_threat(
                agent,
                distance
            )

            if threat > strongest_value:
                strongest_value = threat
                strongest = agent

        return strongest

    def get_state_color(self):
        colors = {
            "idle": "#888888",
            "wandering": "#4da6ff",
            "exploring": "#55cc88",
            "investigating": "#d6c85a",
            "chasing": "#ff884d",
            "fleeing": "#ff4d6d",
            "resting": "#aa88ff",
            "dead": "#444444",
        }

        return colors.get(
            self.state,
            "#ffffff"
        )

    def get_personality_color(self):
        colors = {
            "aggressive": "#ff5555",
            "defensive": "#5588ff",
            "explorer": "#55cc88",
            "balanced": "#cccccc",
        }

        return colors.get(
            self.personality,
            "#ffffff"
        )

    def __repr__(self):
        return (
            f"Agent("
            f"id={self.agent_id}, "
            f"state={self.state}, "
            f"personality={self.personality}, "
            f"health={self.health:.1f}, "
            f"energy={self.energy:.1f}, "
            f"x={self.x:.1f}, "
            f"y={self.y:.1f}"
            f")"
        )