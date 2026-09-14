import random
import math


class Resource:
    TYPES = [
        "food",
        "energy",
        "water",
    ]

    def __init__(self, resource_id, resource_type, x, y, amount=100):
        self.resource_id = resource_id
        self.resource_type = resource_type

        self.x = float(x)
        self.y = float(y)

        self.amount = float(amount)
        self.max_amount = float(amount)

        self.radius = random.uniform(8.0, 14.0)

        self.regeneration_rate = random.uniform(
            0.01,
            0.08
        )

        self.active = True

        self.age = 0

    def distance_to(self, x, y):
        dx = self.x - x
        dy = self.y - y

        return math.sqrt(
            dx * dx + dy * dy
        )

    def consume(self, amount):
        if not self.active:
            return 0.0

        amount_taken = min(
            amount,
            self.amount
        )

        self.amount -= amount_taken

        if self.amount <= 0:
            self.amount = 0
            self.active = False

        return amount_taken

    def regenerate(self):
        if self.amount < self.max_amount:
            self.amount += self.regeneration_rate

        if self.amount >= self.max_amount:
            self.amount = self.max_amount
            self.active = True

    def update(self):
        self.age += 1
        self.regenerate()

    def get_ratio(self):
        if self.max_amount <= 0:
            return 0.0

        return self.amount / self.max_amount

    def __repr__(self):
        return (
            f"Resource("
            f"id={self.resource_id}, "
            f"type={self.resource_type}, "
            f"amount={self.amount:.1f}, "
            f"x={self.x:.1f}, "
            f"y={self.y:.1f}"
            f")"
        )


class Obstacle:
    def __init__(
        self,
        obstacle_id,
        x,
        y,
        width,
        height
    ):
        self.obstacle_id = obstacle_id

        self.x = float(x)
        self.y = float(y)

        self.width = float(width)
        self.height = float(height)

        self.active = True

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.height

    def contains_point(self, x, y):
        return (
            self.left <= x <= self.right
            and
            self.top <= y <= self.bottom
        )

    def intersects_circle(self, x, y, radius):
        closest_x = max(
            self.left,
            min(x, self.right)
        )

        closest_y = max(
            self.top,
            min(y, self.bottom)
        )

        dx = x - closest_x
        dy = y - closest_y

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        return distance <= radius

    def __repr__(self):
        return (
            f"Obstacle("
            f"id={self.obstacle_id}, "
            f"x={self.x:.1f}, "
            f"y={self.y:.1f}, "
            f"width={self.width:.1f}, "
            f"height={self.height:.1f}"
            f")"
        )


class World:
    def __init__(
        self,
        width=900,
        height=600
    ):
        self.width = width
        self.height = height

        self.tick = 0

        self.time = 0.0

        self.time_scale = 1.0

        self.day_length = 2400

        self.agents = []

        self.resources = []

        self.obstacles = []

        self.events = []

        self.event_limit = 200

        self.next_resource_id = 1

        self.next_obstacle_id = 1

        self.temperature = 20.0

        self.weather = "clear"

        self.weather_timer = random.randint(
            300,
            800
        )

        self.total_resources_spawned = 0

        self.total_resources_consumed = 0

        self.total_collisions = 0

        self.total_events = 0

        self.total_agent_distance = 0.0

        self.population_history = []

        self.average_health_history = []

        self.average_energy_history = []

        self.average_hunger_history = []

        self.generate_environment()

    def generate_environment(self):
        self.resources.clear()

        self.obstacles.clear()

        self.spawn_initial_resources()

        self.spawn_initial_obstacles()

    def spawn_initial_resources(self):
        resource_count = 18

        for _ in range(resource_count):
            self.spawn_resource()

    def spawn_initial_obstacles(self):
        obstacle_count = 5

        for _ in range(obstacle_count):
            self.spawn_obstacle()

    def random_position(self, margin=40):
        return (
            random.uniform(
                margin,
                self.width - margin
            ),
            random.uniform(
                margin,
                self.height - margin
            ),
        )

    def position_is_clear(
        self,
        x,
        y,
        radius=10
    ):
        for obstacle in self.obstacles:
            if obstacle.intersects_circle(
                x,
                y,
                radius
            ):
                return False

        return True

    def find_clear_position(
        self,
        margin=40,
        radius=10,
        attempts=100
    ):
        for _ in range(attempts):
            x, y = self.random_position(
                margin
            )

            if self.position_is_clear(
                x,
                y,
                radius
            ):
                return x, y

        return (
            self.width / 2,
            self.height / 2
        )

    def spawn_resource(
        self,
        resource_type=None,
        x=None,
        y=None,
        amount=None
    ):
        if resource_type is None:
            resource_type = random.choice(
                Resource.TYPES
            )

        if x is None or y is None:
            x, y = self.find_clear_position(
                margin=35,
                radius=12
            )

        if amount is None:
            amount = random.uniform(
                60,
                120
            )

        resource = Resource(
            resource_id=self.next_resource_id,
            resource_type=resource_type,
            x=x,
            y=y,
            amount=amount
        )

        self.resources.append(
            resource
        )

        self.next_resource_id += 1

        self.total_resources_spawned += 1

        self.log_event(
            f"Resource spawned: "
            f"{resource_type} "
            f"#{resource.resource_id}"
        )

        return resource

    def spawn_obstacle(
        self,
        x=None,
        y=None,
        width=None,
        height=None
    ):
        if width is None:
            width = random.uniform(
                40,
                100
            )

        if height is None:
            height = random.uniform(
                40,
                100
            )

        margin = 30

        if x is None:
            x = random.uniform(
                margin,
                self.width
                - width
                - margin
            )

        if y is None:
            y = random.uniform(
                margin,
                self.height
                - height
                - margin
            )

        obstacle = Obstacle(
            obstacle_id=self.next_obstacle_id,
            x=x,
            y=y,
            width=width,
            height=height
        )

        self.obstacles.append(
            obstacle
        )

        self.next_obstacle_id += 1

        self.log_event(
            f"Obstacle created "
            f"#{obstacle.obstacle_id}"
        )

        return obstacle

    def remove_resource(
        self,
        resource
    ):
        if resource in self.resources:
            self.resources.remove(
                resource
            )

    def remove_obstacle(
        self,
        obstacle
    ):
        if obstacle in self.obstacles:
            self.obstacles.remove(
                obstacle
            )

    def update(self, agents):
        self.agents = agents

        self.tick += 1

        self.time += (
            self.time_scale
        )

        self.update_environment()

        self.update_resources()

        self.check_agent_collisions()

        self.update_statistics()

        for agent in agents:
            agent.update(self)

        self.check_population_events()

    def update_environment(self):
        self.weather_timer -= 1

        if self.weather_timer <= 0:
            self.change_weather()

        self.update_temperature()

    def change_weather(self):
        weather_options = [
            "clear",
            "cloudy",
            "rain",
            "wind",
        ]

        old_weather = self.weather

        self.weather = random.choice(
            weather_options
        )

        self.weather_timer = random.randint(
            300,
            900
        )

        if self.weather != old_weather:
            self.log_event(
                f"Weather changed: "
                f"{old_weather} -> "
                f"{self.weather}"
            )

    def update_temperature(self):
        day_progress = (
            self.time
            % self.day_length
        ) / self.day_length

        temperature_cycle = math.sin(
            day_progress * math.tau
        )

        base_temperature = (
            20
            + temperature_cycle * 8
        )

        weather_modifier = 0

        if self.weather == "rain":
            weather_modifier = -3

        elif self.weather == "cloudy":
            weather_modifier = -1

        elif self.weather == "wind":
            weather_modifier = -2

        self.temperature = (
            base_temperature
            + weather_modifier
        )

    def update_resources(self):
        for resource in self.resources:
            resource.update()

    def check_agent_collisions(self):
        alive_agents = [
            agent
            for agent in self.agents
            if agent.alive
        ]

        for agent in alive_agents:
            self.check_obstacle_collision(
                agent
            )

        for i in range(
            len(alive_agents)
        ):
            first = alive_agents[i]

            for j in range(
                i + 1,
                len(alive_agents)
            ):
                second = alive_agents[j]

                distance = self.distance_between(
                    first,
                    second
                )

                minimum_distance = (
                    first.size
                    + second.size
                )

                if distance < minimum_distance:
                    self.resolve_agent_collision(
                        first,
                        second
                    )

    def check_obstacle_collision(
        self,
        agent
    ):
        for obstacle in self.obstacles:
            if obstacle.intersects_circle(
                agent.x,
                agent.y,
                agent.size
            ):
                self.total_collisions += 1

                self.push_agent_out_of_obstacle(
                    agent,
                    obstacle
                )

                agent.energy = max(
                    0,
                    agent.energy - 0.5
                )

    def push_agent_out_of_obstacle(
        self,
        agent,
        obstacle
    ):
        center_x = (
            obstacle.left
            + obstacle.width / 2
        )

        center_y = (
            obstacle.top
            + obstacle.height / 2
        )

        dx = agent.x - center_x
        dy = agent.y - center_y

        if abs(dx) > abs(dy):
            if dx >= 0:
                agent.x = (
                    obstacle.right
                    + agent.size
                )
            else:
                agent.x = (
                    obstacle.left
                    - agent.size
                )

        else:
            if dy >= 0:
                agent.y = (
                    obstacle.bottom
                    + agent.size
                )
            else:
                agent.y = (
                    obstacle.top
                    - agent.size
                )

        self.keep_agent_inside(
            agent
        )

    def resolve_agent_collision(
        self,
        first,
        second
    ):
        dx = second.x - first.x
        dy = second.y - first.y

        distance = math.sqrt(
            dx * dx
            + dy * dy
        )

        if distance == 0:
            angle = random.uniform(
                0,
                math.tau
            )

            dx = math.cos(angle)
            dy = math.sin(angle)

            distance = 1

        overlap = (
            first.size
            + second.size
            - distance
        )

        if overlap <= 0:
            return

        normal_x = dx / distance
        normal_y = dy / distance

        push = overlap / 2

        first.x -= (
            normal_x * push
        )

        first.y -= (
            normal_y * push
        )

        second.x += (
            normal_x * push
        )

        second.y += (
            normal_y * push
        )

        first.direction = (
            math.atan2(
                -normal_y,
                -normal_x
            )
        )

        second.direction = (
            math.atan2(
                normal_y,
                normal_x
            )
        )

        first.energy = max(
            0,
            first.energy - 0.1
        )

        second.energy = max(
            0,
            second.energy - 0.1
        )

        self.total_collisions += 1

        self.log_event(
            f"Agents collided: "
            f"#{first.agent_id} "
            f"and "
            f"#{second.agent_id}"
        )

    def keep_agent_inside(
        self,
        agent
    ):
        agent.x = max(
            agent.size,
            min(
                self.width - agent.size,
                agent.x
            )
        )

        agent.y = max(
            agent.size,
            min(
                self.height - agent.size,
                agent.y
            )
        )

    def distance_between(
        self,
        first,
        second
    ):
        dx = second.x - first.x
        dy = second.y - first.y

        return math.sqrt(
            dx * dx
            + dy * dy
        )

    def distance_to_point(
        self,
        agent,
        x,
        y
    ):
        dx = x - agent.x
        dy = y - agent.y

        return math.sqrt(
            dx * dx
            + dy * dy
        )

    def get_nearby_agents(
        self,
        agent,
        radius
    ):
        nearby = []

        for other in self.agents:
            if other is agent:
                continue

            if not other.alive:
                continue

            distance = self.distance_between(
                agent,
                other
            )

            if distance <= radius:
                nearby.append(
                    other
                )

        return nearby

    def get_nearby_resources(
        self,
        agent,
        radius,
        resource_type=None
    ):
        nearby = []

        for resource in self.resources:
            if not resource.active:
                continue

            if (
                resource_type is not None
                and
                resource.resource_type
                != resource_type
            ):
                continue

            distance = resource.distance_to(
                agent.x,
                agent.y
            )

            if distance <= radius:
                nearby.append(
                    resource
                )

        return nearby

    def get_nearest_resource(
        self,
        agent,
        resource_type=None
    ):
        nearest = None
        nearest_distance = float(
            "inf"
        )

        for resource in self.resources:
            if not resource.active:
                continue

            if (
                resource_type is not None
                and
                resource.resource_type
                != resource_type
            ):
                continue

            distance = resource.distance_to(
                agent.x,
                agent.y
            )

            if distance < nearest_distance:
                nearest = resource
                nearest_distance = distance

        return nearest

    def consume_resource(
        self,
        agent,
        resource,
        amount=10
    ):
        if resource not in self.resources:
            return 0.0

        distance = resource.distance_to(
            agent.x,
            agent.y
        )

        if distance > (
            agent.size
            + resource.radius
            + 5
        ):
            return 0.0

        consumed = resource.consume(
            amount
        )

        if consumed > 0:
            self.total_resources_consumed += (
                consumed
            )

            if resource.resource_type == "food":
                agent.hunger = max(
                    0,
                    agent.hunger
                    - consumed * 0.8
                )

            elif resource.resource_type == "energy":
                agent.energy = min(
                    agent.max_energy,
                    agent.energy
                    + consumed * 0.8
                )

            elif resource.resource_type == "water":
                agent.energy = min(
                    agent.max_energy,
                    agent.energy
                    + consumed * 0.3
                )

            self.log_event(
                f"Agent #{agent.agent_id} "
                f"consumed "
                f"{consumed:.1f} "
                f"units of "
                f"{resource.resource_type}"
            )

        return consumed

    def update_statistics(self):
        alive = [
            agent
            for agent in self.agents
            if agent.alive
        ]

        population = len(alive)

        self.population_history.append(
            population
        )

        if len(
            self.population_history
        ) > 500:
            self.population_history.pop(0)

        if population == 0:
            self.average_health_history.append(
                0
            )

            self.average_energy_history.append(
                0
            )

            self.average_hunger_history.append(
                0
            )

            return

        average_health = sum(
            agent.health
            for agent in alive
        ) / population

        average_energy = sum(
            agent.energy
            for agent in alive
        ) / population

        average_hunger = sum(
            agent.hunger
            for agent in alive
        ) / population

        self.average_health_history.append(
            average_health
        )

        self.average_energy_history.append(
            average_energy
        )

        self.average_hunger_history.append(
            average_hunger
        )

        if len(
            self.average_health_history
        ) > 500:
            self.average_health_history.pop(
                0
            )

            self.average_energy_history.pop(
                0
            )

            self.average_hunger_history.pop(
                0
            )

        self.total_agent_distance = sum(
            agent.distance_travelled
            for agent in alive
        )

    def check_population_events(self):
        if self.tick % 100 != 0:
            return

        alive_count = len(
            [
                agent
                for agent in self.agents
                if agent.alive
            ]
        )

        if alive_count == 0:
            self.log_event(
                "EXTINCTION: "
                "No agents remain."
            )

        elif alive_count == 1:
            self.log_event(
                "Only one agent remains."
            )

    def get_population(self):
        return len(
            [
                agent
                for agent in self.agents
                if agent.alive
            ]
        )

    def get_dead_count(self):
        return len(
            [
                agent
                for agent in self.agents
                if not agent.alive
            ]
        )

    def get_active_resources(self):
        return len(
            [
                resource
                for resource in self.resources
                if resource.active
            ]
        )

    def get_resource_count(
        self,
        resource_type=None
    ):
        if resource_type is None:
            return len(
                self.resources
            )

        return len(
            [
                resource
                for resource in self.resources
                if (
                    resource.resource_type
                    == resource_type
                )
            ]
        )

    def get_average_health(self):
        if not self.average_health_history:
            return 0.0

        return (
            self.average_health_history[-1]
        )

    def get_average_energy(self):
        if not self.average_energy_history:
            return 0.0

        return (
            self.average_energy_history[-1]
        )

    def get_average_hunger(self):
        if not self.average_hunger_history:
            return 0.0

        return (
            self.average_hunger_history[-1]
        )

    def get_time_of_day(self):
        progress = (
            self.time
            % self.day_length
        ) / self.day_length

        if progress < 0.25:
            return "morning"

        if progress < 0.5:
            return "afternoon"

        if progress < 0.75:
            return "evening"

        return "night"

    def get_environment_status(self):
        return {
            "tick": self.tick,
            "time": round(
                self.time,
                2
            ),
            "time_of_day":
                self.get_time_of_day(),
            "temperature":
                round(
                    self.temperature,
                    1
                ),
            "weather": self.weather,
            "population":
                self.get_population(),
            "dead":
                self.get_dead_count(),
            "resources":
                self.get_active_resources(),
            "obstacles":
                len(self.obstacles),
            "collisions":
                self.total_collisions,
            "events":
                self.total_events,
        }

    def log_event(self, message):
        event = {
            "tick": self.tick,
            "message": message,
        }

        self.events.append(event)

        self.total_events += 1

        if len(self.events) > self.event_limit:
            self.events.pop(0)

    def get_recent_events(self, count=20):
        if count <= 0:
            return []

        return self.events[-count:]

    def clear_events(self):
        self.events.clear()

    def reset(self):
        self.tick = 0

        self.time = 0.0

        self.temperature = 20.0

        self.weather = "clear"

        self.weather_timer = random.randint(
            300,
            800
        )

        self.events.clear()

        self.total_resources_spawned = 0

        self.total_resources_consumed = 0

        self.total_collisions = 0

        self.total_events = 0

        self.total_agent_distance = 0.0

        self.population_history.clear()

        self.average_health_history.clear()

        self.average_energy_history.clear()

        self.average_hunger_history.clear()

        self.next_resource_id = 1

        self.next_obstacle_id = 1

        self.generate_environment()

    def get_status(self):
        return {
            "width": self.width,
            "height": self.height,
            "tick": self.tick,
            "time": round(
                self.time,
                1
            ),
            "weather": self.weather,
            "temperature": round(
                self.temperature,
                1
            ),
            "population": self.get_population(),
            "resources": self.get_active_resources(),
            "obstacles": len(
                self.obstacles
            ),
            "collisions": self.total_collisions,
            "resources_consumed":
                round(
                    self.total_resources_consumed,
                    1
                ),
        }

    def __repr__(self):
        return (
            f"World("
            f"{self.width}x{self.height}, "
            f"tick={self.tick}, "
            f"population="
            f"{self.get_population()}, "
            f"resources="
            f"{self.get_active_resources()}, "
            f"weather="
            f"{self.weather}"
            f")"
        )