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
        "attacking",
        "dead",
    ]

    PERSONALITIES = [
        "aggressive",
        "defensive",
        "explorer",
        "balanced",
    ]

    TEAMS = [
        "red",
        "blue",
    ]

    def __init__(
        self,
        agent_id,
        x,
        y,
        size=14,
        personality=None,
        team=None,
    ):
        self.agent_id = agent_id
        self.id = agent_id

        self.x = float(x)
        self.y = float(y)

        self.size = size

        self.personality = (
            personality
            if personality in self.PERSONALITIES
            else random.choice(
                self.PERSONALITIES
            )
        )

        if team in self.TEAMS:
            self.team = team
        else:
            self.team = self.TEAMS[
                agent_id % len(self.TEAMS)
            ]

        self.alive = True

        self.health = 100.0
        self.max_health = 100.0

        self.energy = random.uniform(
            75.0,
            100.0,
        )
        self.max_energy = 100.0

        self.hunger = random.uniform(
            0.0,
            20.0,
        )
        self.max_hunger = 100.0

        self.age = 0
        self.max_age = random.randint(
            25000,
            40000,
        )

        self.speed = random.uniform(
            1.5,
            3.0,
        )

        self.acceleration = random.uniform(
            0.05,
            0.15,
        )

        self.max_speed = (
            self.speed
            + random.uniform(
                0.5,
                1.5,
            )
        )

        self.direction = random.uniform(
            0,
            math.tau,
        )

        self.turn_speed = random.uniform(
            0.03,
            0.12,
        )

        self.direction_timer = random.randint(
            10,
            40,
        )

        self.vision_range = random.uniform(
            130.0,
            180.0,
        )

        self.hearing_range = random.uniform(
            80.0,
            140.0,
        )

        self.memory = []
        self.memory_limit = 20

        self.target = None
        self.last_target = None

        self.state = "wandering"
        self.previous_state = "wandering"

        self.state_timer = random.randint(
            20,
            60,
        )

        self.decision_timer = 0

        self.decision_interval = random.randint(
            5,
            15,
        )

        self.wander_target = None
        self.wander_timer = 0

        self.investigation_target = None
        self.investigation_timer = 0

        self.flee_timer = 0
        self.rest_timer = 0

        self.threat_level = 0.0

        self.curiosity = random.uniform(
            0.2,
            1.0,
        )

        self.aggression = random.uniform(
            0.2,
            1.0,
        )

        self.caution = random.uniform(
            0.2,
            1.0,
        )

        self.bravery = random.uniform(
            0.2,
            1.0,
        )

        self.intelligence = random.uniform(
            0.2,
            1.0,
        )

        self.stubbornness = random.uniform(
            0.1,
            0.8,
        )

        self.randomness = random.uniform(
            0.1,
            0.6,
        )

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
        self.score = 0

        self.events = []
        self.event_limit = 50

    def log_event(self, message):
        event = {
            "tick": self.steps,
            "message": str(message),
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
            dx * dx
            + dy * dy
        )

    def distance_to_point(self, x, y):
        dx = x - self.x
        dy = y - self.y

        return math.sqrt(
            dx * dx
            + dy * dy
        )

    def angle_to(self, other):
        if other is None:
            return self.direction

        return math.atan2(
            other.y - self.y,
            other.x - self.x,
        )

    def is_alive(self):
        return (
            self.alive
            and self.state != "dead"
            and self.health > 0
        )

    def is_enemy(self, other):
        if other is None:
            return False

        if other is self:
            return False

        return (
            self.team != getattr(
                other,
                "team",
                None,
            )
        )

    def is_teammate(self, other):
        if other is None:
            return False

        if other is self:
            return False

        return (
            self.team
            == getattr(
                other,
                "team",
                None,
            )
        )

    def get_team(self):
        return self.team

    def set_team(self, team):
        if team not in self.TEAMS:
            return False

        self.team = team

        return True

    def get_health_percent(self):
        if self.max_health <= 0:
            return 0.0

        return (
            self.health
            / self.max_health
        )

    def get_energy_percent(self):
        if self.max_energy <= 0:
            return 0.0

        return (
            self.energy
            / self.max_energy
        )

    def get_combat_strength(self):
        health_factor = (
            self.get_health_percent()
        )

        energy_factor = (
            self.get_energy_percent()
        )

        personality_factor = (
            self.aggression * 0.4
            + self.bravery * 0.25
            + self.intelligence * 0.2
            + health_factor * 0.15
        )

        return (
            personality_factor
            * (
                0.5
                + energy_factor * 0.5
            )
        )

    def find_nearest_enemy(self, agents):
        nearest = None
        nearest_distance = float("inf")

        for other in agents:
            if other is self:
                continue

            if not getattr(
                other,
                "is_alive",
                lambda: False,
            )():
                continue

            if not self.is_enemy(other):
                continue

            distance = self.distance_to(
                other
            )

            if distance < nearest_distance:
                nearest = other
                nearest_distance = distance

        return nearest

    def find_nearest_teammate(self, agents):
        nearest = None
        nearest_distance = float("inf")

        for other in agents:
            if other is self:
                continue

            if not getattr(
                other,
                "is_alive",
                lambda: False,
            )():
                continue

            if not self.is_teammate(other):
                continue

            distance = self.distance_to(
                other
            )

            if distance < nearest_distance:
                nearest = other
                nearest_distance = distance

        return nearest

    def find_nearest_low_health_enemy(
        self,
        agents,
    ):
        best_target = None
        best_score = float("-inf")

        for other in agents:
            if other is self:
                continue

            if not getattr(
                other,
                "is_alive",
                lambda: False,
            )():
                continue

            if not self.is_enemy(other):
                continue

            distance = self.distance_to(
                other
            )

            if distance > self.vision_range:
                continue

            health_percent = (
                getattr(
                    other,
                    "health",
                    100,
                )
                / max(
                    getattr(
                        other,
                        "max_health",
                        100,
                    ),
                    1,
                )
            )

            distance_factor = max(
                0.0,
                1.0
                - (
                    distance
                    / max(
                        self.vision_range,
                        1,
                    )
                ),
            )

            score = (
                (1.0 - health_percent)
                * 0.65
                + distance_factor
                * 0.35
            )

            if score > best_score:
                best_score = score
                best_target = other

        return best_target

    def choose_target(self, agents):
        if not agents:
            return None

        enemies = []

        for other in agents:
            if other is self:
                continue

            if not getattr(
                other,
                "is_alive",
                lambda: False,
            )():
                continue

            if not self.is_enemy(other):
                continue

            distance = self.distance_to(
                other
            )

            if distance <= self.vision_range:
                enemies.append(
                    (
                        other,
                        distance,
                    )
                )

        if not enemies:
            return None

        if self.personality == "aggressive":
            enemies.sort(
                key=lambda item: item[1]
            )

            return enemies[0][0]

        if self.personality == "defensive":
            enemies.sort(
                key=lambda item: getattr(
                    item[0],
                    "health",
                    100,
                )
            )

            return enemies[0][0]

        if self.personality == "explorer":
            if random.random() < 0.35:
                return random.choice(
                    enemies
                )[0]

            enemies.sort(
                key=lambda item: item[1]
            )

            return enemies[0][0]

        low_health_target = (
            self.find_nearest_low_health_enemy(
                agents
            )
        )

        if (
            low_health_target is not None
            and random.random() < 0.7
        ):
            return low_health_target

        enemies.sort(
            key=lambda item: item[1]
        )

        return enemies[0][0]

    def should_attack(self, target):
        if target is None:
            return False

        if not self.is_alive():
            return False

        if not self.is_enemy(target):
            return False

        distance = self.distance_to(
            target
        )

        attack_range = getattr(
            self,
            "attack_range",
            35.0,
        )

        if distance > attack_range:
            return False

        health_percent = (
            self.get_health_percent()
        )

        if (
            self.personality
            == "defensive"
        ):
            return (
                self.bravery > 0.45
                and health_percent > 0.35
            )

        if (
            self.personality
            == "aggressive"
        ):
            return (
                self.aggression > 0.35
            )

        if (
            self.personality
            == "explorer"
        ):
            return (
                self.bravery > 0.65
                and health_percent > 0.55
            )

        return (
            self.bravery > 0.4
            and health_percent > 0.3
        )

    def should_flee(self, target):
        if target is None:
            return False

        if not self.is_alive():
            return False

        if not self.is_enemy(target):
            return False

        health_percent = (
            self.get_health_percent()
        )

        target_health_percent = (
            getattr(
                target,
                "health",
                100,
            )
            / max(
                getattr(
                    target,
                    "max_health",
                    100,
                ),
                1,
            )
        )

        if health_percent < 0.2:
            return True

        if (
            self.personality
            == "defensive"
            and health_percent < 0.4
        ):
            return True

        if (
            self.personality
            == "explorer"
            and health_percent < 0.3
            and target_health_percent
            > health_percent
        ):
            return True

        if (
            self.personality
            == "aggressive"
            and health_percent < 0.12
        ):
            return True

        return False

    def take_damage(
        self,
        amount,
        attacker=None,
    ):
        if not self.is_alive():
            return 0.0

        amount = max(
            0.0,
            float(amount),
        )

        old_health = self.health

        self.health = max(
            0.0,
            self.health - amount,
        )

        actual_damage = (
            old_health
            - self.health
        )

        self.damage_taken += (
            actual_damage
        )

        if attacker is not None:
            try:
                attacker.damage_dealt += (
                    actual_damage
                )
            except Exception:
                pass

        self.threat_level = min(
            1.0,
            self.threat_level
            + 0.2,
        )

        self.times_threatened += 1

        self.log_event(
            f"Took {actual_damage:.1f} damage"
        )

        if self.health <= 0:
            self.die(attacker)

        return actual_damage

    def die(self, killer=None):
        if self.state == "dead":
            return

        self.health = 0.0
        self.alive = False
        self.state = "dead"

        self.target = None

        self.log_event(
            "Agent eliminated"
        )

        if killer is not None:
            try:
                killer.kills += 1
                killer.score += 100
            except Exception:
                pass

    def heal(self, amount):
        if not self.is_alive():
            return 0.0

        amount = max(
            0.0,
            float(amount),
        )

        old_health = self.health

        self.health = min(
            self.max_health,
            self.health + amount,
        )

        return (
            self.health
            - old_health
        )

    def change_state(self, new_state):
        if new_state not in self.STATES:
            return False

        if self.state == new_state:
            return True

        self.previous_state = self.state
        self.state = new_state

        self.state_changes += 1

        self.log_event(
            f"State changed to {new_state}"
        )

        return True

    def update(self, world):
        if not self.is_alive():
            return

        self.steps += 1
        self.age += 1

        self.energy = max(
            0.0,
            self.energy - 0.03,
        )

        self.hunger = min(
            self.max_hunger,
            self.hunger + 0.025,
        )

        self.state_timer -= 1
        self.decision_timer -= 1
        self.direction_timer -= 1

        agents = getattr(
            world,
            "agents",
            [],
        )

        if not isinstance(
            agents,
            (list, tuple),
        ):
            agents = []

        if self.decision_timer <= 0:
            self.make_decision(
                world,
                agents,
            )

            self.decision_timer = (
                self.decision_interval
            )

        self.move(world)

        if self.age >= self.max_age:
            self.die()

    def make_decision(
        self,
        world,
        agents,
    ):
        if not self.is_alive():
            return

        self.decisions_made += 1

        enemy = self.find_nearest_enemy(
            agents
        )

        if enemy is not None:
            distance = self.distance_to(
                enemy
            )

            if self.should_flee(enemy):
                self.target = enemy
                self.last_target = enemy
                self.times_fled += 1
                self.change_state(
                    "fleeing"
                )
                return

            if self.should_attack(enemy):
                self.target = enemy
                self.last_target = enemy
                self.times_chased += 1

                if distance <= getattr(
                    self,
                    "attack_range",
                    35.0,
                ):
                    self.change_state(
                        "attacking"
                    )
                else:
                    self.change_state(
                        "chasing"
                    )

                return

        self.target = None

        if self.energy < 20:
            self.times_resting += 1
            self.change_state(
                "resting"
            )
            return

        if (
            self.hunger > 80
            and random.random() < 0.4
        ):
            self.change_state(
                "investigating"
            )
            return

        if (
            self.personality
            == "explorer"
        ):
            self.change_state(
                "exploring"
            )
            return

        if random.random() < 0.2:
            self.change_state(
                "idle"
            )
        else:
            self.change_state(
                "wandering"
            )

    def move(self, world):
        if not self.is_alive():
            return

        old_x = self.x
        old_y = self.y

        if self.state == "fleeing":
            if self.target is not None:
                angle = self.angle_to(
                    self.target
                ) + math.pi

                self.direction = angle

        elif (
            self.state == "chasing"
            or self.state == "attacking"
        ):
            if self.target is not None:
                self.direction = (
                    self.angle_to(
                        self.target
                    )
                )

        elif self.direction_timer <= 0:
            self.direction += random.uniform(
                -self.turn_speed,
                self.turn_speed,
            )

            self.direction_timer = (
                random.randint(
                    10,
                    40,
                )
            )

        if self.state == "resting":
            self.energy = min(
                self.max_energy,
                self.energy + 0.2,
            )

            if self.energy > 80:
                self.change_state(
                    "wandering"
                )

            return

        if self.state == "idle":
            return

        current_speed = self.speed

        if self.state == "fleeing":
            current_speed *= 1.25

        elif self.state == "chasing":
            current_speed *= 1.1

        elif self.state == "attacking":
            current_speed *= 0.4

        self.x += (
            math.cos(self.direction)
            * current_speed
        )

        self.y += (
            math.sin(self.direction)
            * current_speed
        )

        width = getattr(
            world,
            "width",
            900,
        )

        height = getattr(
            world,
            "height",
            600,
        )

        self.x = max(
            self.size,
            min(
                width - self.size,
                self.x,
            ),
        )

        self.y = max(
            self.size,
            min(
                height - self.size,
                self.y,
            ),
        )

        distance = math.sqrt(
            (self.x - old_x) ** 2
            + (self.y - old_y) ** 2
        )

        self.distance_travelled += (
            distance
        )

        self.energy = max(
            0.0,
            self.energy
            - distance * 0.01,
        )

    def get_status(self):
        return {
            "id": self.agent_id,
            "team": self.team,
            "personality": self.personality,
            "state": self.state,
            "alive": self.is_alive(),
            "health": self.health,
            "max_health": self.max_health,
            "energy": self.energy,
            "max_energy": self.max_energy,
            "hunger": self.hunger,
            "age": self.age,
            "score": self.score,
            "kills": self.kills,
            "damage_taken": self.damage_taken,
            "damage_dealt": self.damage_dealt,
            "distance_travelled": self.distance_travelled,
            "decisions": self.decisions_made,
        }

    def __repr__(self):
        return (
            f"<Agent "
            f"{self.agent_id} "
            f"{self.team} "
            f"{self.personality} "
            f"HP={self.health:.1f} "
            f"state={self.state}>"
        )