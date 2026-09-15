import random
import time

from agent import Agent
from world import World


VERSION = "0.4.2"


class Simulation:
    def __init__(
        self,
        width=900,
        height=600,
        agent_count=3,
    ):
        self.width = width
        self.height = height
        self.agent_count = agent_count

        self.world = World(
            width=width,
            height=height,
        )

        self.running = False
        self.paused = False
        self.finished = False

        self.round_number = 1
        self.tick = 0
        self.round_ticks = 0
        self.maximum_round_ticks = 10000

        self.speed_multiplier = 1.0

        self.start_time = None
        self.last_update_time = time.perf_counter()

        self.winner = None
        self.winner_reason = None

        self.team_mode = False
        self.team_count = 2

        self.combat_enabled = True
        self.resources_enabled = True

        self.history = []
        self.round_history = []

        self.total_decisions = 0
        self.total_attacks = 0
        self.total_damage = 0
        self.total_kills = 0
        self.total_deaths = 0

        self.best_agent = None
        self.best_score = 0

        self.rank_update_interval = 15
        self.last_rank_update = 0

        self.event_log = []

        self.create_agents()

    def create_agents(self):
        self.world.agents.clear()

        personalities = [
            "aggressive",
            "defensive",
            "explorer",
        ]

        for index in range(self.agent_count):
            personality = personalities[index % len(personalities)]

            agent = Agent(
                index,
                x=random.uniform(
                    50,
                    self.width - 50,
                ),
                y=random.uniform(
                    50,
                    self.height - 50,
                ),
                personality=personality,
            )

            self.configure_agent(agent)

            self.world.agents.append(agent)

        self.assign_teams()

    def configure_agent(self, agent):
        if not hasattr(agent, "team"):
            agent.team = None

        if not hasattr(agent, "score"):
            agent.score = 0

        if not hasattr(agent, "rank"):
            agent.rank = 0

        if not hasattr(agent, "attacks"):
            agent.attacks = 0

        if not hasattr(agent, "successful_attacks"):
            agent.successful_attacks = 0

        if not hasattr(agent, "kills"):
            agent.kills = 0

        if not hasattr(agent, "damage_dealt"):
            agent.damage_dealt = 0

        if not hasattr(agent, "damage_taken"):
            agent.damage_taken = 0

        if not hasattr(agent, "resources_collected"):
            agent.resources_collected = 0

        if not hasattr(agent, "survival_ticks"):
            agent.survival_ticks = 0

        if not hasattr(agent, "combat_experience"):
            agent.combat_experience = 0

        if not hasattr(agent, "exploration_score"):
            agent.exploration_score = 0

        if not hasattr(agent, "combat_score"):
            agent.combat_score = 0

        if not hasattr(agent, "survival_score"):
            agent.survival_score = 0

        if not hasattr(agent, "behaviour_score"):
            agent.behaviour_score = 0

        if not hasattr(agent, "last_action"):
            agent.last_action = "idle"

        if not hasattr(agent, "last_decision"):
            agent.last_decision = "idle"

        if not hasattr(agent, "attack_cooldown"):
            agent.attack_cooldown = 0

        if not hasattr(agent, "attack_range"):
            agent.attack_range = 100

        if not hasattr(agent, "attack_damage"):
            agent.attack_damage = 10

        if not hasattr(agent, "attack_accuracy"):
            agent.attack_accuracy = 0.7

        if not hasattr(agent, "defence"):
            agent.defence = 0

        if not hasattr(agent, "resource_priority"):
            agent.resource_priority = 0.5

        agent.spawn_x = agent.x
        agent.spawn_y = agent.y

    def assign_teams(self):
        if not self.team_mode:
            for agent in self.world.agents:
                agent.team = None

            return

        for index, agent in enumerate(self.world.agents):
            agent.team = index % max(1, self.team_count)

    def configure_teams(self, enabled=True, team_count=2):
        self.team_mode = enabled
        self.team_count = max(2, team_count)

        self.assign_teams()

    def enable_team_mode(self, team_count=2):
        self.configure_teams(
            enabled=True,
            team_count=team_count,
        )

    def disable_team_mode(self):
        self.configure_teams(
            enabled=False,
            team_count=2,
        )

    def reset(self):
        self.running = False
        self.paused = False
        self.finished = False

        self.round_number = 1
        self.tick = 0
        self.round_ticks = 0

        self.speed_multiplier = 1.0

        self.start_time = None
        self.last_update_time = time.perf_counter()

        self.winner = None
        self.winner_reason = None

        self.history.clear()
        self.round_history.clear()
        self.event_log.clear()

        self.total_decisions = 0
        self.total_attacks = 0
        self.total_damage = 0
        self.total_kills = 0
        self.total_deaths = 0

        self.best_agent = None
        self.best_score = 0

        self.last_rank_update = 0

        try:
            self.world.reset()
        except TypeError:
            try:
                self.world.reset(self.world.agents)
            except Exception:
                pass

        self.create_agents()

    def start(self):
        if self.finished:
            self.reset()

        self.running = True
        self.paused = False

        if self.start_time is None:
            self.start_time = time.perf_counter()

        self.last_update_time = time.perf_counter()

    def stop(self):
        self.running = False
        self.paused = False

    def pause(self):
        self.paused = True

    def resume(self):
        if not self.finished:
            self.paused = False

    def toggle(self):
        if not self.running:
            self.start()
        elif self.paused:
            self.resume()
        else:
            self.pause()

    def update(self):
        if not self.running:
            return

        if self.paused:
            return

        if self.finished:
            return

        steps = max(
            1,
            int(self.speed_multiplier),
        )

        for _ in range(steps):
            if self.finished:
                break

            self.single_tick()

    def single_tick(self):
        self.tick += 1
        self.round_ticks += 1

        self.update_world()
        self.update_agents()
        self.update_combat()
        self.update_resources()

        self.update_survival()
        self.update_scores()

        if (
            self.tick - self.last_rank_update
            >= self.rank_update_interval
        ):
            self.update_rankings()
            self.last_rank_update = self.tick

        self.check_end_conditions()

        if self.tick % 30 == 0:
            self.record_history()

    def update_world(self):
        try:
            self.world.update()
        except TypeError:
            try:
                self.world.update(self.world.agents)
            except Exception:
                pass

    def update_agents(self):
        agents = self.world.agents

        for agent in agents:
            if not self.is_alive(agent):
                continue

            try:
                decision = agent.choose_action(self.world)
            except TypeError:
                try:
                    decision = agent.choose_action()
                except Exception:
                    decision = None

            if decision is not None:
                agent.last_decision = decision
                self.total_decisions += 1

            try:
                agent.update(self.world)
            except TypeError:
                try:
                    agent.update()
                except Exception:
                    self.basic_agent_update(agent)

            except Exception:
                self.basic_agent_update(agent)

            agent.survival_ticks += 1

    def basic_agent_update(self, agent):
        if hasattr(agent, "energy"):
            agent.energy = max(
                0,
                agent.energy - 0.02,
            )

        if hasattr(agent, "hunger"):
            agent.hunger = min(
                100,
                agent.hunger + 0.03,
            )

        state = getattr(
            agent,
            "state",
            "idle",
        )

        if state == "fleeing":
            self.move_agent_randomly(
                agent,
                multiplier=1.4,
            )

        elif state in (
            "wandering",
            "exploring",
        ):
            self.move_agent_randomly(
                agent,
                multiplier=1.0,
            )

    def move_agent_randomly(
        self,
        agent,
        multiplier=1.0,
    ):
        angle = random.uniform(
            0,
            6.283185307,
        )

        speed = getattr(
            agent,
            "max_speed",
            2.0,
        )

        distance = speed * multiplier

        agent.x += (
            random.uniform(-1, 1)
            * distance
        )

        agent.y += (
            random.uniform(-1, 1)
            * distance
        )

        agent.x = max(
            10,
            min(
                self.width - 10,
                agent.x,
            ),
        )

        agent.y = max(
            10,
            min(
                self.height - 10,
                agent.y,
            ),
        )

    def update_combat(self):
        if not self.combat_enabled:
            return

        agents = self.world.agents

        alive_agents = [
            agent
            for agent in agents
            if self.is_alive(agent)
        ]

        if len(alive_agents) < 2:
            return

        for attacker in alive_agents:
            if self.finished:
                break

            if getattr(
                attacker,
                "attack_cooldown",
                0,
            ) > 0:

                attacker.attack_cooldown = max(
                    0,
                    attacker.attack_cooldown - 1,
                )

                continue

            target = self.find_target(attacker)

            if target is None:
                continue

            if not self.can_attack(
                attacker,
                target,
            ):
                continue

            self.attack(
                attacker,
                target,
            )

    def find_target(self, attacker):
        candidates = []

        for target in self.world.agents:
            if target is attacker:
                continue

            if not self.is_alive(target):
                continue

            if (
                self.team_mode
                and getattr(
                    attacker,
                    "team",
                    None,
                )
                == getattr(
                    target,
                    "team",
                    None,
                )
            ):
                continue

            distance = self.distance(
                attacker,
                target,
            )

            candidates.append(
                (
                    distance,
                    target,
                )
            )

        if not candidates:
            return None

        personality = getattr(
            attacker,
            "personality",
            "balanced",
        )

        if personality == "aggressive":
            candidates.sort(
                key=lambda item: item[0]
            )

        elif personality == "defensive":
            candidates.sort(
                key=lambda item: (
                    item[0]
                    + getattr(
                        item[1],
                        "health",
                        100,
                    )
                    * 0.2
                )
            )

        elif personality == "explorer":
            if random.random() > 0.65:
                return None

            candidates.sort(
                key=lambda item: item[0]
            )

        else:
            candidates.sort(
                key=lambda item: item[0]
            )

        return candidates[0][1]

    def can_attack(
        self,
        attacker,
        target,
    ):
        distance = self.distance(
            attacker,
            target,
        )

        attack_range = getattr(
            attacker,
            "attack_range",
            100,
        )

        return distance <= attack_range

    def attack(
        self,
        attacker,
        target,
    ):
        self.total_attacks += 1

        attacker.attacks += 1

        accuracy = getattr(
            attacker,
            "attack_accuracy",
            0.7,
        )

        if random.random() > accuracy:
            attacker.attack_cooldown = 15
            attacker.last_action = "attack_miss"
            return

        base_damage = getattr(
            attacker,
            "attack_damage",
            10,
        )

        defence = getattr(
            target,
            "defence",
            0,
        )

        damage = max(
            1,
            base_damage - defence,
        )

        damage *= random.uniform(
            0.75,
            1.25,
        )

        damage = int(
            max(
                1,
                damage,
            )
        )

        target_health = getattr(
            target,
            "health",
            100,
        )

        target.health = max(
            0,
            target_health - damage,
        )

        attacker.successful_attacks += 1
        attacker.damage_dealt += damage

        target.damage_taken += damage

        attacker.combat_experience += damage
        attacker.combat_score += damage

        self.total_damage += damage

        attacker.last_action = "attack"
        target.last_action = "hit"

        attacker.attack_cooldown = 20

        if target.health <= 0:
            self.kill_agent(
                target,
                attacker,
            )

    def kill_agent(
        self,
        victim,
        killer=None,
    ):
        if not self.is_alive(victim):
            return

        try:
            victim.die()
        except Exception:
            victim.health = 0
            victim.state = "dead"

        self.total_deaths += 1

        if killer is not None:
            killer.kills += 1
            killer.score += 100
            self.total_kills += 1

            self.log_event(
                f"Agent {self.agent_id(killer)} "
                f"eliminated Agent {self.agent_id(victim)}"
            )

        else:
            self.log_event(
                f"Agent {self.agent_id(victim)} died"
            )

    def update_resources(self):
        if not self.resources_enabled:
            return

        resources = getattr(
            self.world,
            "resources",
            [],
        )

        if not resources:
            return

        for resource in resources:
            try:
                resource.update()
            except TypeError:
                try:
                    resource.update(self.world)
                except Exception:
                    pass

        for agent in self.world.agents:
            if not self.is_alive(agent):
                continue

            nearby = []

            for resource in resources:
                try:
                    if not getattr(
                        resource,
                        "active",
                        True,
                    ):
                        continue

                    distance = resource.distance_to(
                        agent.x,
                        agent.y,
                    )

                    nearby.append(
                        (
                            distance,
                            resource,
                        )
                    )

                except Exception:
                    continue

            if not nearby:
                continue

            nearby.sort(
                key=lambda item: item[0]
            )

            distance, resource = nearby[0]

            if distance > 25:
                continue

            amount = min(
                1,
                getattr(
                    resource,
                    "amount",
                    0,
                ),
            )

            if amount <= 0:
                continue

            try:
                consumed = self.world.consume_resource(
                    agent,
                    resource,
                    amount,
                )
            except TypeError:
                try:
                    consumed = resource.consume(
                        amount
                    )
                except Exception:
                    consumed = False

            if consumed:
                agent.resources_collected += amount
                agent.score += amount * 2

    def update_survival(self):
        for agent in self.world.agents:
            if not self.is_alive(agent):
                continue

            health = getattr(
                agent,
                "health",
                100,
            )

            energy = getattr(
                agent,
                "energy",
                100,
            )

            hunger = getattr(
                agent,
                "hunger",
                0,
            )

            if energy <= 0:
                agent.score -= 0.1

            if hunger >= 100:
                agent.score -= 0.2

            if health <= 0:
                self.kill_agent(agent)

    def update_scores(self):
        for agent in self.world.agents:
            if not self.is_alive(agent):
                continue

            survival_score = (
                agent.survival_ticks
                * 0.01
            )

            exploration_score = getattr(
                agent,
                "exploration_score",
                0,
            )

            combat_score = getattr(
                agent,
                "combat_score",
                0,
            )

            resource_score = (
                getattr(
                    agent,
                    "resources_collected",
                    0,
                )
                * 2
            )

            agent.survival_score = survival_score

            agent.behaviour_score = (
                exploration_score
                + combat_score
                + resource_score
            )

            agent.score = (
                agent.score
                + survival_score * 0.001
            )

            if agent.score > self.best_score:
                self.best_score = agent.score
                self.best_agent = agent

    def update_rankings(self):
        ranked = sorted(
            self.world.agents,
            key=lambda agent: getattr(
                agent,
                "score",
                0,
            ),
            reverse=True,
        )

        for index, agent in enumerate(
            ranked,
            start=1,
        ):
            agent.rank = index

    def check_end_conditions(self):
        alive = [
            agent
            for agent in self.world.agents
            if self.is_alive(agent)
        ]

        if len(alive) == 0:
            self.finish(
                None,
                "All agents eliminated",
            )
            return

        if self.team_mode:
            teams = {
                getattr(
                    agent,
                    "team",
                    None,
                )
                for agent in alive
            }

            if len(teams) == 1:
                winning_team = next(
                    iter(teams)
                )

                winner = max(
                    alive,
                    key=lambda agent: getattr(
                        agent,
                        "score",
                        0,
                    ),
                )

                self.finish(
                    winner,
                    f"Team {winning_team} wins",
                )

                return

        else:
            if len(alive) == 1:
                self.finish(
                    alive[0],
                    "Last agent standing",
                )
                return

        if (
            self.round_ticks
            >= self.maximum_round_ticks
        ):
            winner = max(
                alive,
                key=lambda agent: getattr(
                    agent,
                    "score",
                    0,
                ),
            )

            self.finish(
                winner,
                "Maximum round time reached",
            )

    def finish(
        self,
        winner,
        reason,
    ):
        self.finished = True
        self.running = False

        self.winner = winner
        self.winner_reason = reason

        if winner is not None:
            winner.score += 250
            self.best_agent = winner

        self.update_rankings()

        self.round_history.append(
            self.get_results()
        )

        if winner is not None:
            self.log_event(
                f"Agent {self.agent_id(winner)} wins: {reason}"
            )

        else:
            self.log_event(
                f"Simulation finished: {reason}"
            )

    def new_round(self):
        self.round_number += 1

        self.finished = False
        self.running = False
        self.paused = False

        self.tick = 0
        self.round_ticks = 0

        self.winner = None
        self.winner_reason = None

        self.create_agents()

    def add_agent(
        self,
        personality=None,
    ):
        if personality is None:
            personality = random.choice(
                [
                    "aggressive",
                    "defensive",
                    "explorer",
                    "balanced",
                ]
            )

        agent = Agent(
            len(self.world.agents),
            x=random.uniform(
                50,
                self.width - 50,
            ),
            y=random.uniform(
                50,
                self.height - 50,
            ),
            personality=personality,
        )

        self.configure_agent(agent)

        self.world.agents.append(agent)

        self.agent_count = len(
            self.world.agents
        )

        self.assign_teams()

        return agent

    def remove_agent(
        self,
        agent,
    ):
        if agent in self.world.agents:
            self.world.agents.remove(
                agent
            )

        self.agent_count = len(
            self.world.agents
        )

        self.assign_teams()

    def increase_speed(self):
        self.speed_multiplier = min(
            10.0,
            self.speed_multiplier + 0.5,
        )

    def decrease_speed(self):
        self.speed_multiplier = max(
            0.5,
            self.speed_multiplier - 0.5,
        )

    def set_speed(
        self,
        multiplier,
    ):
        self.speed_multiplier = max(
            0.1,
            min(
                20.0,
                float(multiplier),
            ),
        )

    def population(self):
        return sum(
            1
            for agent in self.world.agents
            if self.is_alive(agent)
        )

    def dead_population(self):
        return sum(
            1
            for agent in self.world.agents
            if not self.is_alive(agent)
        )

    def total_population(self):
        return len(
            self.world.agents
        )

    def average_health(self):
        alive = [
            agent
            for agent in self.world.agents
            if self.is_alive(agent)
        ]

        if not alive:
            return 0

        return sum(
            getattr(
                agent,
                "health",
                0,
            )
            for agent in alive
        ) / len(alive)

    def average_energy(self):
        alive = [
            agent
            for agent in self.world.agents
            if self.is_alive(agent)
        ]

        if not alive:
            return 0

        return sum(
            getattr(
                agent,
                "energy",
                0,
            )
            for agent in alive
        ) / len(alive)

    def average_hunger(self):
        alive = [
            agent
            for agent in self.world.agents
            if self.is_alive(agent)
        ]

        if not alive:
            return 0

        return sum(
            getattr(
                agent,
                "hunger",
                0,
            )
            for agent in alive
        ) / len(alive)

    def get_leaderboard(self):
        return sorted(
            self.world.agents,
            key=lambda agent: getattr(
                agent,
                "score",
                0,
            ),
            reverse=True,
        )

    def get_team_scores(self):
        scores = {}

        for agent in self.world.agents:
            team = getattr(
                agent,
                "team",
                None,
            )

            if team is None:
                continue

            scores.setdefault(
                team,
                0,
            )

            scores[team] += getattr(
                agent,
                "score",
                0,
            )

        return scores

    def get_team_population(self):
        populations = {}

        for agent in self.world.agents:
            if not self.is_alive(agent):
                continue

            team = getattr(
                agent,
                "team",
                None,
            )

            if team is None:
                continue

            populations.setdefault(
                team,
                0,
            )

            populations[team] += 1

        return populations

    def get_best_agent(self):
        agents = self.world.agents

        if not agents:
            return None

        return max(
            agents,
            key=lambda agent: getattr(
                agent,
                "score",
                0,
            ),
        )

    def get_worst_agent(self):
        agents = self.world.agents

        if not agents:
            return None

        return min(
            agents,
            key=lambda agent: getattr(
                agent,
                "score",
                0,
            ),
        )

    def get_most_aggressive(self):
        agents = self.world.agents

        if not agents:
            return None

        return max(
            agents,
            key=lambda agent: getattr(
                agent,
                "attacks",
                0,
            ),
        )

    def get_longest_survivor(self):
        agents = self.world.agents

        if not agents:
            return None

        return max(
            agents,
            key=lambda agent: getattr(
                agent,
                "survival_ticks",
                0,
            ),
        )

    def get_most_damaging(self):
        agents = self.world.agents

        if not agents:
            return None

        return max(
            agents,
            key=lambda agent: getattr(
                agent,
                "damage_dealt",
                0,
            ),
        )

    def get_most_resourceful(self):
        agents = self.world.agents

        if not agents:
            return None

        return max(
            agents,
            key=lambda agent: getattr(
                agent,
                "resources_collected",
                0,
            ),
        )

    def get_time_running(self):
        if self.start_time is None:
            return 0

        if self.finished:
            return time.perf_counter() - self.start_time

        return time.perf_counter() - self.start_time

    def distance(
        self,
        first,
        second,
    ):
        dx = (
            getattr(first, "x", 0)
            - getattr(second, "x", 0)
        )

        dy = (
            getattr(first, "y", 0)
            - getattr(second, "y", 0)
        )

        return (
            dx * dx + dy * dy
        ) ** 0.5

    def agent_id(
        self,
        agent,
    ):
        if hasattr(
            agent,
            "agent_id",
        ):
            return agent.agent_id

        if hasattr(
            agent,
            "id",
        ):
            return agent.id

        try:
            return self.world.agents.index(
                agent
            )
        except ValueError:
            return "?"

    def is_alive(
        self,
        agent,
    ):
        if getattr(
            agent,
            "health",
            0,
        ) <= 0:
            return False

        state = getattr(
            agent,
            "state",
            None,
        )

        if state == "dead":
            return False

        return True

    def log_event(
        self,
        message,
    ):
        self.event_log.append(
            {
                "tick": self.tick,
                "round": self.round_number,
                "message": message,
            }
        )

        if len(self.event_log) > 500:
            self.event_log = self.event_log[-500:]

    def record_history(self):
        alive = [
            agent
            for agent in self.world.agents
            if self.is_alive(agent)
        ]

        entry = {
            "tick": self.tick,
            "round": self.round_number,
            "population": len(alive),
            "total_population": len(
                self.world.agents
            ),
            "average_health": self.average_health(),
            "average_energy": self.average_energy(),
            "average_hunger": self.average_hunger(),
            "attacks": self.total_attacks,
            "damage": self.total_damage,
            "kills": self.total_kills,
            "deaths": self.total_deaths,
        }

        self.history.append(entry)

        if len(self.history) > 1000:
            self.history = self.history[-1000:]

    def get_results(self):
        leaderboard = self.get_leaderboard()

        return {
            "version": VERSION,
            "round": self.round_number,
            "tick": self.tick,
            "winner": (
                self.agent_id(self.winner)
                if self.winner is not None
                else None
            ),
            "winner_reason": self.winner_reason,
            "population": self.population(),
            "total_population": self.total_population(),
            "deaths": self.total_deaths,
            "kills": self.total_kills,
            "attacks": self.total_attacks,
            "damage": self.total_damage,
            "speed": self.speed_multiplier,
            "leaderboard": [
                {
                    "id": self.agent_id(agent),
                    "score": getattr(
                        agent,
                        "score",
                        0,
                    ),
                    "rank": getattr(
                        agent,
                        "rank",
                        0,
                    ),
                    "health": getattr(
                        agent,
                        "health",
                        0,
                    ),
                    "personality": getattr(
                        agent,
                        "personality",
                        "unknown",
                    ),
                    "team": getattr(
                        agent,
                        "team",
                        None,
                    ),
                    "kills": getattr(
                        agent,
                        "kills",
                        0,
                    ),
                    "damage": getattr(
                        agent,
                        "damage_dealt",
                        0,
                    ),
                }
                for agent in leaderboard
            ],
        }

    def get_status(self):
        return {
            "version": VERSION,
            "running": self.running,
            "paused": self.paused,
            "finished": self.finished,
            "tick": self.tick,
            "round": self.round_number,
            "round_ticks": self.round_ticks,
            "population": self.population(),
            "dead": self.dead_population(),
            "speed": self.speed_multiplier,
            "winner": (
                self.agent_id(self.winner)
                if self.winner is not None
                else None
            ),
            "winner_reason": self.winner_reason,
            "total_decisions": self.total_decisions,
            "total_attacks": self.total_attacks,
            "total_damage": self.total_damage,
            "total_kills": self.total_kills,
            "total_deaths": self.total_deaths,
        }

    def get_agent_status(
        self,
        agent,
    ):
        return {
            "id": self.agent_id(agent),
            "state": getattr(
                agent,
                "state",
                "unknown",
            ),
            "personality": getattr(
                agent,
                "personality",
                "unknown",
            ),
            "team": getattr(
                agent,
                "team",
                None,
            ),
            "health": getattr(
                agent,
                "health",
                0,
            ),
            "energy": getattr(
                agent,
                "energy",
                0,
            ),
            "hunger": getattr(
                agent,
                "hunger",
                0,
            ),
            "score": getattr(
                agent,
                "score",
                0,
            ),
            "rank": getattr(
                agent,
                "rank",
                0,
            ),
            "attacks": getattr(
                agent,
                "attacks",
                0,
            ),
            "kills": getattr(
                agent,
                "kills",
                0,
            ),
            "damage_dealt": getattr(
                agent,
                "damage_dealt",
                0,
            ),
            "damage_taken": getattr(
                agent,
                "damage_taken",
                0,
            ),
            "resources_collected": getattr(
                agent,
                "resources_collected",
                0,
            ),
            "survival_ticks": getattr(
                agent,
                "survival_ticks",
                0,
            ),
            "last_action": getattr(
                agent,
                "last_action",
                "unknown",
            ),
            "last_decision": getattr(
                agent,
                "last_decision",
                "unknown",
            ),
        }

    def get_event_log(
        self,
        limit=50,
    ):
        return self.event_log[
            -limit:
        ]

    def get_history(
        self,
        limit=100,
    ):
        return self.history[
            -limit:
        ]

    def get_population_by_personality(self):
        result = {}

        for agent in self.world.agents:
            personality = getattr(
                agent,
                "personality",
                "unknown",
            )

            result.setdefault(
                personality,
                0,
            )

            if self.is_alive(agent):
                result[personality] += 1

        return result

    def get_population_by_state(self):
        result = {}

        for agent in self.world.agents:
            state = getattr(
                agent,
                "state",
                "unknown",
            )

            result.setdefault(
                state,
                0,
            )

            if self.is_alive(agent):
                result[state] += 1

        return result

    def export_results(self):
        return {
            "version": VERSION,
            "simulation": self.get_status(),
            "results": self.get_results(),
            "history": self.history.copy(),
            "events": self.event_log.copy(),
        }

    def __repr__(self):
        return (
            f"<Simulation "
            f"v{VERSION} "
            f"tick={self.tick} "
            f"agents={self.total_population()} "
            f"alive={self.population()} "
            f"running={self.running}>"
        )