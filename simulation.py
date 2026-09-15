import random
import time

from agent import Agent
from world import World


VERSION = "0.5.0"


class Simulation:
    def __init__(
        self,
        width=900,
        height=600,
        agent_count=6,
    ):
        self.width = width
        self.height = height

        self.agent_count = agent_count

        self.world = World(
            width,
            height,
        )

        self.running = False
        self.paused = False
        self.finished = False

        self.tick = 0
        self.round = 1

        self.simulation_speed = 1.0

        self.min_speed = 0.25
        self.max_speed = 8.0

        self.base_tick_rate = 30.0

        self.tick_interval = (
            1.0 / self.base_tick_rate
        )

        self.accumulator = 0.0
        self.last_update_time = (
            time.perf_counter()
        )

        self.max_ticks_per_update = 5

        self.total_ticks = 0

        self.start_time = None
        self.elapsed_time = 0.0

        self.winner = None
        self.team_winner = None

        self.team_mode = True

        self.teams = [
            "red",
            "blue",
        ]

        self.team_scores = {
            "red": 0,
            "blue": 0,
        }

        self.team_kills = {
            "red": 0,
            "blue": 0,
        }

        self.team_damage = {
            "red": 0.0,
            "blue": 0.0,
        }

        self.combat_enabled = True
        self.resources_enabled = True

        self.history = []
        self.event_log = []

        self.total_attacks = 0
        self.total_damage = 0.0
        self.total_deaths = 0

        self.performance = {
            "fps": 0.0,
            "simulation_tps": 0.0,
            "last_update_ms": 0.0,
            "agent_update_ms": 0.0,
            "combat_ms": 0.0,
            "world_ms": 0.0,
            "total_ms": 0.0,
        }

        self._performance_time = (
            time.perf_counter()
        )

        self._performance_frames = 0
        self._performance_ticks = 0

        self._last_agent_count = -1
        self._last_alive_count = -1

        self.create_agents()

    def create_agents(self):
        self.agents = []

        personalities = [
            "aggressive",
            "defensive",
            "explorer",
            "balanced",
        ]

        for i in range(
            self.agent_count
        ):
            personality = personalities[
                i % len(personalities)
            ]

            if self.team_mode:
                team = self.teams[
                    i % len(self.teams)
                ]
            else:
                team = "neutral"

            agent = Agent(
                i,
                x=random.uniform(
                    50,
                    self.width - 50,
                ),
                y=random.uniform(
                    50,
                    self.height - 50,
                ),
                personality=personality,
                team=team
                if team in self.teams
                else None,
            )

            self.agents.append(
                agent
            )

        self.world.agents = (
            self.agents
        )

        self.assign_teams()

    def add_agent(
        self,
        personality="balanced",
        team=None,
        x=None,
        y=None,
    ):
        if x is None:
            x = random.uniform(
                50,
                self.width - 50,
            )

        if y is None:
            y = random.uniform(
                50,
                self.height - 50,
            )

        if self.team_mode:
            if team not in self.teams:
                team = self.get_smallest_team()
        else:
            team = None

        agent = Agent(
            len(self.world.agents),
            x=x,
            y=y,
            personality=personality,
            team=team,
        )

        self.world.agents.append(
            agent
        )

        self.agents = (
            self.world.agents
        )

        self.agent_count = len(
            self.world.agents
        )

        return agent

    def remove_agent(self, agent):
        if agent in self.world.agents:
            self.world.agents.remove(
                agent
            )

            self.agents = (
                self.world.agents
            )

            self.agent_count = len(
                self.world.agents
            )

    def start(self):
        if self.finished:
            return

        self.running = True
        self.paused = False

        self.last_update_time = (
            time.perf_counter()
        )

        if self.start_time is None:
            self.start_time = (
                time.perf_counter()
            )

        self.log_event(
            "Team warfare started"
        )

    def stop(self):
        self.running = False
        self.paused = True

        self.log_event(
            "Simulation paused"
        )

    def pause(self):
        self.stop()

    def resume(self):
        if self.finished:
            return

        self.running = True
        self.paused = False

        self.last_update_time = (
            time.perf_counter()
        )

        self.log_event(
            "Simulation resumed"
        )

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def reset(self):
        self.running = False
        self.paused = False
        self.finished = False

        self.tick = 0
        self.total_ticks = 0
        self.round = 1

        self.accumulator = 0.0

        self.start_time = None
        self.elapsed_time = 0.0

        self.winner = None
        self.team_winner = None

        self.team_scores = {
            "red": 0,
            "blue": 0,
        }

        self.team_kills = {
            "red": 0,
            "blue": 0,
        }

        self.team_damage = {
            "red": 0.0,
            "blue": 0.0,
        }

        self.history.clear()
        self.event_log.clear()

        self.total_attacks = 0
        self.total_damage = 0.0
        self.total_deaths = 0

        self.performance = {
            "fps": 0.0,
            "simulation_tps": 0.0,
            "last_update_ms": 0.0,
            "agent_update_ms": 0.0,
            "combat_ms": 0.0,
            "world_ms": 0.0,
            "total_ms": 0.0,
        }

        self._performance_time = (
            time.perf_counter()
        )

        self._performance_frames = 0
        self._performance_ticks = 0

        self.world.reset()

        self.create_agents()

        self.last_update_time = (
            time.perf_counter()
        )

        self.log_event(
            "Team warfare reset"
        )

    def set_speed(self, speed):
        speed = float(speed)

        speed = max(
            self.min_speed,
            min(
                self.max_speed,
                speed,
            ),
        )

        self.simulation_speed = speed

        return self.simulation_speed

    def increase_speed(self):
        new_speed = (
            self.simulation_speed * 2
        )

        if new_speed > self.max_speed:
            new_speed = self.max_speed

        self.simulation_speed = (
            new_speed
        )

        return self.simulation_speed

    def decrease_speed(self):
        new_speed = (
            self.simulation_speed / 2
        )

        if new_speed < self.min_speed:
            new_speed = self.min_speed

        self.simulation_speed = (
            new_speed
        )

        return self.simulation_speed

    def update(self):
        update_start = (
            time.perf_counter()
        )

        now = time.perf_counter()

        delta = (
            now
            - self.last_update_time
        )

        self.last_update_time = now

        if delta < 0:
            delta = 0

        if delta > 0.25:
            delta = 0.25

        self._performance_frames += 1

        if (
            self.running
            and not self.finished
        ):
            self.accumulator += (
                delta
                * self.simulation_speed
            )

            ticks_this_update = 0

            while (
                self.accumulator
                >= self.tick_interval
                and ticks_this_update
                < self.max_ticks_per_update
            ):
                self._run_tick()

                self.accumulator -= (
                    self.tick_interval
                )

                ticks_this_update += 1

            if (
                ticks_this_update
                >= self.max_ticks_per_update
            ):
                self.accumulator = min(
                    self.accumulator,
                    self.tick_interval,
                )

        self.update_elapsed_time()

        total_time = (
            time.perf_counter()
            - update_start
        )

        self.performance[
            "last_update_ms"
        ] = total_time * 1000

        self.performance[
            "total_ms"
        ] = total_time * 1000

        self.update_performance()

    def _run_tick(self):
        tick_start = (
            time.perf_counter()
        )

        self.tick += 1
        self.total_ticks += 1

        self._performance_ticks += 1

        alive_before = (
            self.get_alive_count()
        )

        agent_start = (
            time.perf_counter()
        )

        self.update_agents()

        agent_time = (
            time.perf_counter()
            - agent_start
        )

        self.performance[
            "agent_update_ms"
        ] = agent_time * 1000

        combat_start = (
            time.perf_counter()
        )

        if self.combat_enabled:
            self.process_combat()

        combat_time = (
            time.perf_counter()
            - combat_start
        )

        self.performance[
            "combat_ms"
        ] = combat_time * 1000

        world_start = (
            time.perf_counter()
        )

        if self.resources_enabled:
            self.update_resources()

        self.update_world()

        world_time = (
            time.perf_counter()
            - world_start
        )

        self.performance[
            "world_ms"
        ] = world_time * 1000

        self.update_statistics()

        alive_after = (
            self.get_alive_count()
        )

        if alive_after < alive_before:
            self.total_deaths += (
                alive_before
                - alive_after
            )

        self.check_finished()

        self.record_history()

        tick_time = (
            time.perf_counter()
            - tick_start
        )

        self.performance[
            "total_ms"
        ] = tick_time * 1000

    def update_agents(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            return

        if not agents:
            return

        for agent in agents:
            if not agent.is_alive():
                continue

            try:
                agent.update(
                    self.world
                )
            except Exception:
                continue

    def process_combat(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            return

        alive_agents = [
            agent
            for agent in agents
            if agent.is_alive()
        ]

        if len(alive_agents) < 2:
            return

        for attacker in alive_agents:
            target = getattr(
                attacker,
                "target",
                None,
            )

            if target is None:
                target = (
                    attacker.choose_target(
                        alive_agents
                    )
                )

                if target is not None:
                    attacker.target = (
                        target
                    )

            if target is None:
                continue

            if target is attacker:
                continue

            if not target.is_alive():
                attacker.target = None
                continue

            if not attacker.is_enemy(
                target
            ):
                attacker.target = None
                continue

            if not self.can_attack(
                attacker,
                target,
            ):
                continue

            if not attacker.should_attack(
                target
            ):
                continue

            damage = (
                self.calculate_damage(
                    attacker,
                    target,
                )
            )

            if damage <= 0:
                continue

            self.apply_damage(
                attacker,
                target,
                damage,
            )

    def can_attack(
        self,
        attacker,
        target,
    ):
        attack_range = getattr(
            attacker,
            "attack_range",
            35.0,
        )

        dx = (
            target.x
            - attacker.x
        )

        dy = (
            target.y
            - attacker.y
        )

        distance_squared = (
            dx * dx
            + dy * dy
        )

        return (
            distance_squared
            <= attack_range
            * attack_range
        )

    def calculate_damage(
        self,
        attacker,
        target,
    ):
        base_damage = random.uniform(
            4.0,
            9.0,
        )

        aggression = getattr(
            attacker,
            "aggression",
            0.5,
        )

        intelligence = getattr(
            attacker,
            "intelligence",
            0.5,
        )

        caution = getattr(
            target,
            "caution",
            0.5,
        )

        health_factor = (
            attacker.get_health_percent()
        )

        multiplier = (
            0.75
            + aggression * 0.5
            + intelligence * 0.25
            - caution * 0.2
            + health_factor * 0.15
        )

        damage = (
            base_damage
            * multiplier
        )

        return max(
            0.5,
            damage,
        )

    def apply_damage(
        self,
        attacker,
        target,
        damage,
    ):
        if not target.is_alive():
            return

        if not attacker.is_enemy(
            target
        ):
            return

        old_health = (
            target.health
        )

        actual_damage = (
            target.take_damage(
                damage,
                attacker,
            )
        )

        if actual_damage <= 0:
            return

        self.total_damage += (
            actual_damage
        )

        self.total_attacks += 1

        team = getattr(
            attacker,
            "team",
            None,
        )

        if team in self.team_damage:
            self.team_damage[
                team
            ] += actual_damage

        if target.health <= 0:
            self.handle_death(
                target,
                attacker,
            )

            attacker_name = getattr(
                attacker,
                "name",
                f"Agent {getattr(attacker, 'agent_id', '?')}",
            )

            target_name = getattr(
                target,
                "name",
                f"Agent {getattr(target, 'agent_id', '?')}",
            )

            self.log_event(
                f"{attacker_name} "
                f"({attacker.team}) "
                f"eliminated "
                f"{target_name} "
                f"({target.team})"
            )

        elif (
            self.total_attacks % 10
            == 0
        ):
            self.log_event(
                f"{attacker.team.upper()} "
                f"dealt "
                f"{actual_damage:.1f} "
                f"damage"
            )

    def handle_death(
        self,
        agent,
        killer=None,
    ):
        if agent.state == "dead":
            return

        agent.die(killer)

        self.total_deaths += 1

        if killer is not None:
            killer_team = getattr(
                killer,
                "team",
                None,
            )

            if killer_team in (
                self.team_kills
            ):
                self.team_kills[
                    killer_team
                ] += 1

                self.team_scores[
                    killer_team
                ] += 100

    def update_resources(self):
        resources = getattr(
            self.world,
            "resources",
            [],
        )

        if not isinstance(
            resources,
            (list, tuple),
        ):
            return

        for resource in resources:
            try:
                resource.update(
                    self.tick
                )
            except TypeError:
                try:
                    resource.update()
                except Exception:
                    continue
            except Exception:
                continue

    def update_world(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            agents = self.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            agents = []

        self.world.agents = agents

        try:
            self.world.update(
                agents
            )
        except TypeError:
            try:
                self.world.update(
                    list(agents)
                )
            except Exception:
                pass
        except Exception:
            pass

    def update_statistics(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            agents = []

        self._last_agent_count = (
            len(agents)
        )

        self._last_alive_count = (
            self.get_alive_count()
        )

        if hasattr(
            self.world,
            "statistics",
        ):
            try:
                self.world.statistics[
                    "ticks"
                ] = self.tick

                self.world.statistics[
                    "alive"
                ] = self.get_alive_count()

                self.world.statistics[
                    "deaths"
                ] = self.total_deaths

                self.world.statistics[
                    "damage"
                ] = self.total_damage

                self.world.statistics[
                    "red"
                ] = self.get_team_alive_count(
                    "red"
                )

                self.world.statistics[
                    "blue"
                ] = self.get_team_alive_count(
                    "blue"
                )

            except Exception:
                pass

    def update_elapsed_time(self):
        if self.start_time is None:
            self.elapsed_time = 0.0
            return

        self.elapsed_time = (
            time.perf_counter()
            - self.start_time
        )

    def update_performance(self):
        now = time.perf_counter()

        elapsed = (
            now
            - self._performance_time
        )

        if elapsed < 1.0:
            return

        self.performance[
            "fps"
        ] = (
            self._performance_frames
            / elapsed
        )

        self.performance[
            "simulation_tps"
        ] = (
            self._performance_ticks
            / elapsed
        )

        self._performance_frames = 0
        self._performance_ticks = 0

        self._performance_time = now

    def check_finished(self):
        if not self.team_mode:
            self.check_standard_finished()
            return

        red_alive = (
            self.get_team_alive_count(
                "red"
            )
        )

        blue_alive = (
            self.get_team_alive_count(
                "blue"
            )
        )

        if red_alive > 0 and blue_alive > 0:
            return

        if red_alive > 0:
            self.finish_team(
                "red"
            )
            return

        if blue_alive > 0:
            self.finish_team(
                "blue"
            )
            return

        self.finished = True
        self.running = False
        self.paused = False
        self.team_winner = None
        self.winner = None

        self.log_event(
            "Both teams were eliminated"
        )

    def check_standard_finished(self):
        alive_agents = (
            self.get_alive_agents()
        )

        if len(alive_agents) > 1:
            return

        if len(alive_agents) == 1:
            self.winner = (
                alive_agents[0]
            )
        else:
            self.winner = None

        self.finished = True
        self.running = False
        self.paused = False

    def finish_team(self, team):
        self.team_winner = team

        self.finished = True
        self.running = False
        self.paused = False

        winner_agents = (
            self.get_team_agents(
                team
            )
        )

        if winner_agents:
            winner_agents.sort(
                key=lambda agent: (
                    getattr(
                        agent,
                        "score",
                        0,
                    )
                    + getattr(
                        agent,
                        "kills",
                        0,
                    )
                    * 100
                ),
                reverse=True,
            )

            self.winner = (
                winner_agents[0]
            )

        self.log_event(
            f"{team.upper()} TEAM WINS"
        )

    def record_history(self):
        if self.tick % 30 != 0:
            return

        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            agents = []

        snapshot = {
            "tick": self.tick,
            "alive": self.get_alive_count(),
            "agents": len(agents),
            "red": self.get_team_alive_count(
                "red"
            ),
            "blue": self.get_team_alive_count(
                "blue"
            ),
            "red_score": self.team_scores[
                "red"
            ],
            "blue_score": self.team_scores[
                "blue"
            ],
            "red_kills": self.team_kills[
                "red"
            ],
            "blue_kills": self.team_kills[
                "blue"
            ],
            "damage": self.total_damage,
            "attacks": self.total_attacks,
            "deaths": self.total_deaths,
        }

        self.history.append(
            snapshot
        )

        if len(self.history) > 1000:
            self.history.pop(0)

    def log_event(self, message):
        entry = {
            "tick": self.tick,
            "time": self.elapsed_time,
            "message": str(message),
        }

        self.event_log.append(
            entry
        )

        if len(self.event_log) > 500:
            self.event_log.pop(0)

    def get_alive_agents(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            return []

        return [
            agent
            for agent in agents
            if agent.is_alive()
        ]

    def get_alive_count(self):
        return len(
            self.get_alive_agents()
        )

    def get_dead_count(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            return 0

        return (
            len(agents)
            - self.get_alive_count()
        )

    def get_agent_count(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            return 0

        return len(agents)

    def get_team_agents(self, team):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            return []

        return [
            agent
            for agent in agents
            if getattr(
                agent,
                "team",
                None,
            ) == team
        ]

    def get_team_alive_agents(
        self,
        team,
    ):
        return [
            agent
            for agent in self.get_team_agents(
                team
            )
            if agent.is_alive()
        ]

    def get_team_alive_count(
        self,
        team,
    ):
        return len(
            self.get_team_alive_agents(
                team
            )
        )

    def get_team_counts(self):
        return {
            "red": self.get_team_alive_count(
                "red"
            ),
            "blue": self.get_team_alive_count(
                "blue"
            ),
        }

    def get_team_total_counts(self):
        return {
            "red": len(
                self.get_team_agents(
                    "red"
                )
            ),
            "blue": len(
                self.get_team_agents(
                    "blue"
                )
            ),
        }

    def get_smallest_team(self):
        counts = (
            self.get_team_total_counts()
        )

        if counts["red"] <= counts[
            "blue"
        ]:
            return "red"

        return "blue"

    def assign_teams(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            return

        red_count = 0
        blue_count = 0

        for agent in agents:
            if red_count <= blue_count:
                agent.set_team(
                    "red"
                )
                red_count += 1
            else:
                agent.set_team(
                    "blue"
                )
                blue_count += 1

    def set_team_mode(
        self,
        enabled=True,
    ):
        self.team_mode = bool(
            enabled
        )

        if self.team_mode:
            self.assign_teams()

    def get_team_score(self, team):
        return self.team_scores.get(
            team,
            0,
        )

    def get_team_kills(self, team):
        return self.team_kills.get(
            team,
            0,
        )

    def get_team_damage(self, team):
        return self.team_damage.get(
            team,
            0.0,
        )

    def get_rankings(self):
        agents = self.world.agents

        if not isinstance(
            agents,
            (list, tuple),
        ):
            return []

        agents = list(agents)

        def score(agent):
            return (
                getattr(
                    agent,
                    "score",
                    0,
                )
                + getattr(
                    agent,
                    "kills",
                    0,
                ) * 100
                + getattr(
                    agent,
                    "health",
                    0,
                )
            )

        agents.sort(
            key=score,
            reverse=True,
        )

        return agents

    def get_team_rankings(self, team):
        agents = self.get_team_agents(
            team
        )

        return sorted(
            agents,
            key=lambda agent: (
                getattr(
                    agent,
                    "score",
                    0,
                )
                + getattr(
                    agent,
                    "kills",
                    0,
                ) * 100
            ),
            reverse=True,
        )

    def get_team_winner(self):
        return self.team_winner

    def get_winner(self):
        return self.winner

    def get_speed(self):
        return self.simulation_speed

    def get_fps(self):
        return self.performance[
            "fps"
        ]

    def get_simulation_tps(self):
        return self.performance[
            "simulation_tps"
        ]

    def get_performance(self):
        return dict(
            self.performance
        )

    def get_statistics(self):
        return {
            "version": VERSION,
            "tick": self.tick,
            "round": self.round,
            "running": self.running,
            "paused": self.paused,
            "finished": self.finished,
            "speed": self.simulation_speed,
            "agents": self.get_agent_count(),
            "alive": self.get_alive_count(),
            "dead": self.get_dead_count(),
            "red_alive": self.get_team_alive_count(
                "red"
            ),
            "blue_alive": self.get_team_alive_count(
                "blue"
            ),
            "red_score": self.team_scores[
                "red"
            ],
            "blue_score": self.team_scores[
                "blue"
            ],
            "red_kills": self.team_kills[
                "red"
            ],
            "blue_kills": self.team_kills[
                "blue"
            ],
            "red_damage": self.team_damage[
                "red"
            ],
            "blue_damage": self.team_damage[
                "blue"
            ],
            "attacks": self.total_attacks,
            "damage": self.total_damage,
            "deaths": self.total_deaths,
            "elapsed_time": self.elapsed_time,
            "fps": self.get_fps(),
            "simulation_tps": self.get_simulation_tps(),
        }

    def export_results(self):
        return {
            "version": VERSION,
            "tick": self.tick,
            "round": self.round,
            "winner": (
                getattr(
                    self.winner,
                    "name",
                    None,
                )
                if self.winner
                else None
            ),
            "team_winner": (
                self.team_winner
            ),
            "agents": self.get_agent_count(),
            "alive": self.get_alive_count(),
            "dead": self.get_dead_count(),
            "red_alive": self.get_team_alive_count(
                "red"
            ),
            "blue_alive": self.get_team_alive_count(
                "blue"
            ),
            "red_score": self.team_scores[
                "red"
            ],
            "blue_score": self.team_scores[
                "blue"
            ],
            "red_kills": self.team_kills[
                "red"
            ],
            "blue_kills": self.team_kills[
                "blue"
            ],
            "red_damage": self.team_damage[
                "red"
            ],
            "blue_damage": self.team_damage[
                "blue"
            ],
            "attacks": self.total_attacks,
            "damage": self.total_damage,
            "deaths": self.total_deaths,
            "elapsed_time": self.elapsed_time,
            "history": list(
                self.history
            ),
        }

    def get_event_log(self):
        return list(
            self.event_log
        )

    def clear_event_log(self):
        self.event_log.clear()

    def get_version(self):
        return VERSION

    def __repr__(self):
        return (
            f"<Simulation "
            f"v{VERSION} "
            f"tick={self.tick} "
            f"agents={self.get_agent_count()} "
            f"alive={self.get_alive_count()} "
            f"red={self.get_team_alive_count('red')} "
            f"blue={self.get_team_alive_count('blue')} "
            f"speed={self.simulation_speed}x>"
        )