import random
import time

from agent import Agent
from world import World


class Simulation:
    """
    Main controller for AI Arena.

    Handles:
    - Agent creation
    - Simulation timing
    - AI decision cycles
    - Combat
    - Resources
    - Scoring
    - Rankings
    - Teams
    - Rounds
    - Statistics
    - Events
    - Winners
    """

    VERSION = "0.3.0"

    def __init__(
        self,
        width=900,
        height=600,
        agent_count=3
    ):
        self.width = width
        self.height = height

        self.agent_count = max(
            1,
            int(agent_count)
        )

        self.world = World(
            width,
            height
        )

        self.agents = []

        self.running = False
        self.paused = False
        self.finished = False

        self.round_number = 1
        self.round_ticks = 0
        self.total_ticks = 0

        self.maximum_round_ticks = 10000

        self.speed_multiplier = 1.0

        self.start_time = None
        self.last_update_time = None
        self.elapsed_real_time = 0.0

        self.winner = None
        self.winner_reason = None

        self.team_mode = False
        self.team_count = 2

        self.combat_enabled = True
        self.resources_enabled = True

        self.round_history = []
        self.event_history = []

        self.population_history = []
        self.score_history = []

        self.total_decisions = 0
        self.total_attacks = 0
        self.total_damage = 0.0
        self.total_kills = 0
        self.total_deaths = 0

        self.best_agent = None
        self.best_score = 0.0

        self.last_rank_update = 0

        self.rank_update_interval = 10

        self.event_limit = 500

        self.reset()

    def create_agents(self):
        """
        Create the starting population.
        """

        self.agents.clear()

        personalities = [
            "aggressive",
            "defensive",
            "explorer",
            "balanced",
        ]

        for index in range(
            self.agent_count
        ):
            margin = 60

            x = random.uniform(
                margin,
                self.world.width - margin
            )

            y = random.uniform(
                margin,
                self.world.height - margin
            )

            personality = (
                personalities[
                    index
                    % len(personalities)
                ]
            )

            agent = Agent(
                agent_id=index + 1,
                x=x,
                y=y,
                personality=personality
            )

            self.configure_agent(
                agent,
                index
            )

            self.agents.append(
                agent
            )

        self.world.agents = self.agents

    def configure_agent(
        self,
        agent,
        index
    ):
        """
        Add simulation-specific properties
        to an Agent.

        Keeping these properties here means
        the Agent class can concentrate on
        behaviour while Simulation handles
        arena-specific scoring and combat.
        """

        agent.team = self.get_team_for_agent(
            index
        )

        agent.score = 0.0

        agent.rank = index + 1

        agent.attacks = 0

        agent.successful_attacks = 0

        agent.kills = 0

        agent.damage_dealt = 0.0

        agent.damage_taken = 0.0

        agent.resources_collected = 0.0

        agent.survival_ticks = 0

        agent.combat_experience = 0.0

        agent.exploration_score = 0.0

        agent.combat_score = 0.0

        agent.survival_score = 0.0

        agent.behaviour_score = 0.0

        agent.last_action = "spawn"

        agent.last_decision = "spawn"

        agent.attack_cooldown = 0

        agent.attack_range = random.uniform(
            28.0,
            42.0
        )

        agent.attack_damage = random.uniform(
            4.0,
            9.0
        )

        agent.attack_accuracy = random.uniform(
            0.65,
            0.95
        )

        agent.defence = random.uniform(
            0.05,
            0.35
        )

        agent.resource_priority = random.uniform(
            0.3,
            1.0
        )

        agent.spawn_x = agent.x
        agent.spawn_y = agent.y

    def get_team_for_agent(
        self,
        index
    ):
        """
        Determine which team an agent belongs to.
        """

        if not self.team_mode:
            return index + 1

        return (
            index
            % self.team_count
        ) + 1

    def reset(self):
        """
        Reset the entire simulation.
        """

        self.running = False
        self.paused = False
        self.finished = False

        self.round_number = 1
        self.round_ticks = 0
        self.total_ticks = 0

        self.start_time = None
        self.last_update_time = None
        self.elapsed_real_time = 0.0

        self.winner = None
        self.winner_reason = None

        self.round_history.clear()
        self.event_history.clear()

        self.population_history.clear()
        self.score_history.clear()

        self.total_decisions = 0
        self.total_attacks = 0
        self.total_damage = 0.0
        self.total_kills = 0
        self.total_deaths = 0

        self.best_agent = None
        self.best_score = 0.0

        self.last_rank_update = 0

        self.world.reset()

        self.create_agents()

        self.log_event(
            "Simulation reset"
        )

    def start(self):
        """
        Start or resume the simulation.
        """

        if self.finished:
            return

        self.running = True
        self.paused = False

        now = time.time()

        if self.start_time is None:
            self.start_time = now

        self.last_update_time = now

        self.log_event(
            "Simulation started"
        )

    def stop(self):
        """
        Pause the simulation.
        """

        if not self.running:
            return

        self.running = False
        self.paused = True

        self.log_event(
            "Simulation paused"
        )

    def toggle(self):
        """
        Toggle simulation state.
        """

        if self.running:
            self.stop()
        else:
            self.start()

    def update(self):
        """
        Advance the simulation.

        The UI calls this repeatedly.
        """

        if not self.running:
            return

        if self.finished:
            self.running = False
            return

        now = time.time()

        if self.last_update_time is not None:
            self.elapsed_real_time += (
                now
                - self.last_update_time
            )

        self.last_update_time = now

        updates = max(
            1,
            int(self.speed_multiplier)
        )

        for _ in range(updates):
            if not self.running:
                break

            if self.finished:
                break

            self.update_tick()

    def update_tick(self):
        """
        Process one complete simulation tick.
        """

        self.total_ticks += 1
        self.round_ticks += 1

        self.world.update(
            self.agents
        )

        self.run_ai_phase()

        if self.combat_enabled:
            self.run_combat_phase()

        if self.resources_enabled:
            self.run_resource_phase()

        self.update_survival()

        self.update_scores()

        self.update_rankings()

        self.record_history()

        self.check_deaths()

        self.check_winner()

        self.check_round_timeout()

    def run_ai_phase(self):
        """
        Let each living agent make decisions.
        """

        for agent in self.agents:
            if not agent.alive:
                continue

            previous_state = (
                agent.state
            )

            try:
                action = agent.choose_action()
            except Exception as error:
                action = "wander"

                self.log_event(
                    f"Agent #{agent.agent_id} "
                    f"AI error: {error}"
                )

            agent.last_action = action
            agent.last_decision = action

            if previous_state != agent.state:
                agent.behaviour_score += 0.1

            self.total_decisions += 1

    def run_combat_phase(self):
        """
        Find combat opportunities.
        """

        living_agents = [
            agent
            for agent in self.agents
            if agent.alive
        ]

        for attacker in living_agents:
            if not attacker.alive:
                continue

            if attacker.attack_cooldown > 0:
                attacker.attack_cooldown -= 1

            target = self.find_combat_target(
                attacker
            )

            if target is None:
                continue

            distance = self.distance_between(
                attacker,
                target
            )

            if distance > attacker.attack_range:
                continue

            if attacker.attack_cooldown > 0:
                continue

            self.attack(
                attacker,
                target
            )

    def find_combat_target(
        self,
        attacker
    ):
        """
        Find the best nearby enemy.
        """

        candidates = []

        for other in self.agents:
            if other is attacker:
                continue

            if not other.alive:
                continue

            if self.team_mode:
                if (
                    getattr(
                        attacker,
                        "team",
                        None
                    )
                    ==
                    getattr(
                        other,
                        "team",
                        None
                    )
                ):
                    continue

            distance = self.distance_between(
                attacker,
                other
            )

            if distance > attacker.vision_range:
                continue

            candidates.append(
                (
                    distance,
                    other
                )
            )

        if not candidates:
            return None

        if attacker.personality == "aggressive":
            candidates.sort(
                key=lambda item: (
                    item[1].health,
                    item[0]
                )
            )

        elif attacker.personality == "defensive":
            candidates.sort(
                key=lambda item: (
                    -item[1].health,
                    item[0]
                )
            )

        elif attacker.personality == "explorer":
            candidates.sort(
                key=lambda item: (
                    item[0],
                    -item[1].health
                )
            )

        else:
            candidates.sort(
                key=lambda item: (
                    item[0],
                    item[1].health
                )
            )

        return candidates[0][1]

    def attack(
        self,
        attacker,
        target
    ):
        """
        Execute an attack.
        """

        if not attacker.alive:
            return

        if not target.alive:
            return

        attacker.attacks += 1

        attacker.attack_cooldown = random.randint(
            8,
            18
        )

        self.total_attacks += 1

        distance = self.distance_between(
            attacker,
            target
        )

        distance_factor = max(
            0.4,
            1.0
            - (
                distance
                / attacker.attack_range
            )
            * 0.35
        )

        chance = (
            attacker.attack_accuracy
            * distance_factor
        )

        if random.random() > chance:
            self.log_event(
                f"Agent #{attacker.agent_id} "
                f"missed Agent #{target.agent_id}"
            )

            return

        personality_modifier = 1.0

        if attacker.personality == "aggressive":
            personality_modifier = 1.25

        elif attacker.personality == "defensive":
            personality_modifier = 0.85

        elif attacker.personality == "explorer":
            personality_modifier = 0.9

        damage = (
            attacker.attack_damage
            * personality_modifier
        )

        target_defence = getattr(
            target,
            "defence",
            0.0
        )

        damage *= (
            1.0
            - target_defence
        )

        damage *= random.uniform(
            0.8,
            1.2
        )

        damage = max(
            0.1,
            damage
        )

        target.health -= damage

        attacker.damage_dealt += damage

        target.damage_taken += damage

        attacker.successful_attacks += 1

        attacker.combat_experience += (
            damage * 0.05
        )

        attacker.combat_score += (
            damage * 0.5
        )

        self.total_damage += damage

        self.log_event(
            f"Agent #{attacker.agent_id} "
            f"hit Agent #{target.agent_id} "
            f"for {damage:.1f}"
        )

        if target.health <= 0:
            self.kill_agent(
                attacker,
                target
            )

    def kill_agent(
        self,
        attacker,
        target
    ):
        """
        Eliminate an agent and award points.
        """

        if not target.alive:
            return

        target.die(
            f"killed by Agent #{attacker.agent_id}"
        )

        attacker.kills += 1

        attacker.score += 100.0

        attacker.combat_score += 100.0

        attacker.combat_experience += 10.0

        self.total_kills += 1
        self.total_deaths += 1

        self.log_event(
            f"Agent #{attacker.agent_id} "
            f"eliminated Agent #{target.agent_id}"
        )

    def run_resource_phase(self):
        """
        Handle agents collecting resources.
        """

        for agent in self.agents:
            if not agent.alive:
                continue

            resource = self.find_best_resource(
                agent
            )

            if resource is None:
                continue

            distance = resource.distance_to(
                agent.x,
                agent.y
            )

            collection_range = (
                agent.size
                + resource.radius
                + 8
            )

            if distance > collection_range:
                continue

            consumed = self.world.consume_resource(
                agent,
                resource,
                amount=5
            )

            if consumed <= 0:
                continue

            agent.resources_collected += consumed

            agent.score += (
                consumed * 0.5
            )

            agent.exploration_score += (
                consumed * 0.1
            )

    def find_best_resource(
        self,
        agent
    ):
        """
        Choose the resource that best matches
        the agent's current needs.
        """

        best = None
        best_value = -float("inf")

        for resource in self.world.resources:
            if not resource.active:
                continue

            distance = resource.distance_to(
                agent.x,
                agent.y
            )

            if distance > agent.vision_range:
                continue

            value = (
                resource.get_ratio()
                * agent.resource_priority
            )

            if resource.resource_type == "food":
                if agent.hunger > 50:
                    value += (
                        agent.hunger / 100
                    )

            elif resource.resource_type == "energy":
                if agent.energy < 50:
                    value += (
                        1
                        - agent.energy / 100
                    )

            elif resource.resource_type == "water":
                if agent.energy < 30:
                    value += 0.3

            value -= (
                distance
                / max(
                    1,
                    agent.vision_range
                )
            )

            if value > best_value:
                best_value = value
                best = resource

        return best

    def update_survival(self):
        """
        Award survival points to living agents.
        """

        for agent in self.agents:
            if not agent.alive:
                continue

            agent.survival_ticks += 1

            agent.survival_score += 0.01

            agent.score += 0.01

    def update_scores(self):
        """
        Calculate each agent's overall score.
        """

        for agent in self.agents:
            score = 0.0

            score += (
                agent.survival_score
            )

            score += (
                agent.combat_score
            )

            score += (
                agent.exploration_score
            )

            score += (
                agent.behaviour_score
            )

            score += (
                agent.kills * 50
            )

            score += (
                agent.resources_collected
                * 0.25
            )

            score -= (
                agent.damage_taken
                * 0.05
            )

            if agent.alive:
                score += 10

            agent.score = max(
                0.0,
                score
            )

    def update_rankings(self):
        """
        Rank agents by score.
        """

        if (
            self.total_ticks
            - self.last_rank_update
            < self.rank_update_interval
        ):
            return

        self.last_rank_update = (
            self.total_ticks
        )

        ranked = sorted(
            self.agents,
            key=lambda agent: (
                agent.score,
                agent.alive
            ),
            reverse=True
        )

        for rank, agent in enumerate(
            ranked,
            start=1
        ):
            agent.rank = rank

        if ranked:
            self.best_agent = ranked[0]
            self.best_score = (
                ranked[0].score
            )

    def record_history(self):
        """
        Store historical simulation data.
        """

        population = self.get_population()

        self.population_history.append(
            population
        )

        self.score_history.append(
            self.get_total_score()
        )

        if len(
            self.population_history
        ) > 1000:
            self.population_history.pop(0)

        if len(
            self.score_history
        ) > 1000:
            self.score_history.pop(0)

    def check_deaths(self):
        """
        Detect newly dead agents.
        """

        for agent in self.agents:
            if (
                not agent.alive
                and not getattr(
                    agent,
                    "_death_registered",
                    False
                )
            ):
                agent._death_registered = True

                self.log_event(
                    f"Agent #{agent.agent_id} "
                    f"is dead"
                )

    def check_winner(self):
        """
        Determine whether the round has ended.
        """

        alive = self.alive_agents()

        if len(alive) == 0:
            self.finish_round(
                None,
                "total elimination"
            )

            return

        if len(alive) == 1:
            self.finish_round(
                alive[0],
                "last agent standing"
            )

            return

        if self.team_mode:
            alive_teams = set(
                getattr(
                    agent,
                    "team",
                    None
                )
                for agent in alive
            )

            if len(alive_teams) == 1:
                winning_team = next(
                    iter(alive_teams)
                )

                team_agents = [
                    agent
                    for agent in alive
                    if agent.team
                    == winning_team
                ]

                if team_agents:
                    winner = max(
                        team_agents,
                        key=lambda agent:
                        agent.score
                    )

                    self.finish_round(
                        winner,
                        f"team {winning_team} victory"
                    )

    def check_round_timeout(self):
        """
        End a round if it runs too long.
        """

        if (
            self.round_ticks
            < self.maximum_round_ticks
        ):
            return

        alive = self.alive_agents()

        if not alive:
            winner = None
        else:
            winner = max(
                alive,
                key=lambda agent:
                agent.score
            )

        self.finish_round(
            winner,
            "round time limit"
        )

    def finish_round(
        self,
        winner,
        reason
    ):
        """
        Record the result of a round.
        """

        if self.finished:
            return

        self.winner = winner
        self.winner_reason = reason

        result = {
            "round": self.round_number,
            "ticks": self.round_ticks,
            "winner": (
                winner.agent_id
                if winner is not None
                else None
            ),
            "reason": reason,
            "population": self.get_population(),
            "score": (
                winner.score
                if winner is not None
                else 0.0
            ),
        }

        self.round_history.append(
            result
        )

        if winner is not None:
            self.log_event(
                f"Round winner: "
                f"Agent #{winner.agent_id} "
                f"({reason})"
            )
        else:
            self.log_event(
                f"Round ended: {reason}"
            )

        self.finished = True
        self.running = False

    def start_new_round(self):
        """
        Start another round without creating
        a completely new Simulation object.
        """

        self.round_number += 1

        self.round_ticks = 0

        self.finished = False

        self.running = False

        self.winner = None
        self.winner_reason = None

        self.total_deaths = 0

        self.world.reset()

        self.create_agents()

        self.log_event(
            f"Round {self.round_number} started"
        )

    def set_speed(
        self,
        multiplier
    ):
        """
        Set simulation speed.
        """

        try:
            multiplier = float(
                multiplier
            )
        except (
            TypeError,
            ValueError
        ):
            return

        self.speed_multiplier = max(
            0.1,
            min(
                100.0,
                multiplier
            )
        )

        self.log_event(
            f"Simulation speed: "
            f"{self.speed_multiplier}x"
        )

    def increase_speed(self):
        """
        Increase simulation speed.
        """

        levels = [
            0.5,
            1.0,
            2.0,
            4.0,
            8.0,
            16.0,
            32.0,
            64.0,
            100.0,
        ]

        current = self.speed_multiplier

        for level in levels:
            if level > current:
                self.set_speed(level)
                return

        self.set_speed(
            levels[-1]
        )

    def decrease_speed(self):
        """
        Decrease simulation speed.
        """

        levels = [
            0.5,
            1.0,
            2.0,
            4.0,
            8.0,
            16.0,
            32.0,
            64.0,
            100.0,
        ]

        current = self.speed_multiplier

        previous = levels[0]

        for level in levels:
            if level >= current:
                self.set_speed(previous)
                return

            previous = level

        self.set_speed(
            levels[0]
        )

    def enable_team_mode(
        self,
        team_count=2
    ):
        """
        Enable team-based simulation.
        """

        self.team_mode = True

        self.team_count = max(
            2,
            int(team_count)
        )

        for index, agent in enumerate(
            self.agents
        ):
            agent.team = (
                index
                % self.team_count
            ) + 1

        self.log_event(
            f"Team mode enabled "
            f"({self.team_count} teams)"
        )

    def disable_team_mode(self):
        """
        Disable team mode.
        """

        self.team_mode = False

        for index, agent in enumerate(
            self.agents
        ):
            agent.team = index + 1

        self.log_event(
            "Team mode disabled"
        )

    def add_agent(
        self,
        personality=None
    ):
        """
        Dynamically add an agent.
        """

        new_id = 1

        if self.agents:
            new_id = max(
                agent.agent_id
                for agent in self.agents
            ) + 1

        margin = 60

        x = random.uniform(
            margin,
            self.world.width - margin
        )

        y = random.uniform(
            margin,
            self.world.height - margin
        )

        agent = Agent(
            agent_id=new_id,
            x=x,
            y=y,
            personality=personality
        )

        self.configure_agent(
            agent,
            len(self.agents)
        )

        self.agents.append(
            agent
        )

        self.world.agents = self.agents

        self.agent_count = len(
            self.agents
        )

        self.log_event(
            f"Agent #{new_id} "
            f"joined the arena"
        )

        return agent

    def remove_agent(
        self,
        agent
    ):
        """
        Remove an agent from the arena.
        """

        if agent not in self.agents:
            return False

        self.agents.remove(
            agent
        )

        self.agent_count = len(
            self.agents
        )

        self.world.agents = self.agents

        self.log_event(
            f"Agent #{agent.agent_id} "
            f"removed"
        )

        return True

    def alive_agents(self):
        """
        Return living agents.
        """

        return [
            agent
            for agent in self.agents
            if agent.alive
        ]

    def dead_agents(self):
        """
        Return dead agents.
        """

        return [
            agent
            for agent in self.agents
            if not agent.alive
        ]

    def get_population(self):
        """
        Return current living population.
        """

        return len(
            self.alive_agents()
        )

    def get_total_score(self):
        """
        Return combined agent score.
        """

        return sum(
            agent.score
            for agent in self.agents
        )

    def get_average_score(self):
        """
        Return average agent score.
        """

        if not self.agents:
            return 0.0

        return (
            self.get_total_score()
            / len(self.agents)
        )

    def get_average_health(self):
        """
        Return average health of living agents.
        """

        alive = self.alive_agents()

        if not alive:
            return 0.0

        return (
            sum(
                agent.health
                for agent in alive
            )
            / len(alive)
        )

    def get_average_energy(self):
        """
        Return average energy.
        """

        alive = self.alive_agents()

        if not alive:
            return 0.0

        return (
            sum(
                agent.energy
                for agent in alive
            )
            / len(alive)
        )

    def get_average_hunger(self):
        """
        Return average hunger.
        """

        alive = self.alive_agents()

        if not alive:
            return 0.0

        return (
            sum(
                agent.hunger
                for agent in alive
            )
            / len(alive)
        )

    def get_leaderboard(self):
        """
        Return agents ordered by score.
        """

        return sorted(
            self.agents,
            key=lambda agent: (
                agent.score,
                agent.alive
            ),
            reverse=True
        )

    def get_team_scores(self):
        """
        Return total score for each team.
        """

        scores = {}

        for agent in self.agents:
            team = getattr(
                agent,
                "team",
                None
            )

            if team not in scores:
                scores[team] = 0.0

            scores[team] += agent.score

        return scores

    def get_team_population(self):
        """
        Return living population by team.
        """

        populations = {}

        for agent in self.alive_agents():
            team = getattr(
                agent,
                "team",
                None
            )

            if team not in populations:
                populations[team] = 0

            populations[team] += 1

        return populations

    def get_best_agent(self):
        """
        Return the highest-scoring agent.
        """

        if not self.agents:
            return None

        return max(
            self.agents,
            key=lambda agent:
            agent.score
        )

    def get_worst_agent(self):
        """
        Return the lowest-scoring agent.
        """

        if not self.agents:
            return None

        return min(
            self.agents,
            key=lambda agent:
            agent.score
        )

    def get_most_aggressive(self):
        """
        Find the agent with the highest
        aggression attribute.
        """

        if not self.agents:
            return None

        return max(
            self.agents,
            key=lambda agent:
            agent.aggression
        )

    def get_longest_survivor(self):
        """
        Find the agent that has survived
        the longest.
        """

        if not self.agents:
            return None

        return max(
            self.agents,
            key=lambda agent:
            agent.survival_ticks
        )

    def get_most_damaging_agent(self):
        """
        Find the agent that dealt the most damage.
        """

        if not self.agents:
            return None

        return max(
            self.agents,
            key=lambda agent:
            agent.damage_dealt
        )

    def get_most_resourceful_agent(self):
        """
        Find the agent that collected the most
        resources.
        """

        if not self.agents:
            return None

        return max(
            self.agents,
            key=lambda agent:
            agent.resources_collected
        )

    def get_simulation_time(self):
        """
        Return real-world elapsed simulation time.
        """

        if self.start_time is None:
            return 0.0

        if self.running:
            return (
                time.time()
                - self.start_time
            )

        return self.elapsed_real_time

    def distance_between(
        self,
        first,
        second
    ):
        """
        Calculate distance between two agents.
        """

        dx = (
            second.x
            - first.x
        )

        dy = (
            second.y
            - first.y
        )

        return (
            dx * dx
            + dy * dy
        ) ** 0.5

    def log_event(
        self,
        message
    ):
        """
        Record a simulation event.
        """

        event = {
            "tick": self.total_ticks,
            "round": self.round_number,
            "message": str(message),
        }

        self.event_history.append(
            event
        )

        if len(
            self.event_history
        ) > self.event_limit:
            self.event_history.pop(0)

    def get_recent_events(
        self,
        count=20
    ):
        """
        Return the most recent events.
        """

        if count <= 0:
            return []

        return self.event_history[
            -count:
        ]

    def clear_events(self):
        """
        Clear simulation event history.
        """

        self.event_history.clear()

    def get_population_history(self):
        """
        Return a copy of population history.
        """

        return list(
            self.population_history
        )

    def get_score_history(self):
        """
        Return a copy of score history.
        """

        return list(
            self.score_history
        )

    def get_status(self):
        """
        Return a complete simulation status.
        """

        best = self.get_best_agent()

        return {
            "version": self.VERSION,
            "running": self.running,
            "paused": self.paused,
            "finished": self.finished,
            "round": self.round_number,
            "tick": self.total_ticks,
            "round_ticks": self.round_ticks,
            "population": self.get_population(),
            "agents": len(self.agents),
            "dead": len(
                self.dead_agents()
            ),
            "speed": self.speed_multiplier,
            "team_mode": self.team_mode,
            "teams": self.team_count,
            "combat": self.combat_enabled,
            "resources": self.resources_enabled,
            "attacks": self.total_attacks,
            "damage": round(
                self.total_damage,
                1
            ),
            "kills": self.total_kills,
            "decisions": self.total_decisions,
            "average_health": round(
                self.get_average_health(),
                1
            ),
            "average_energy": round(
                self.get_average_energy(),
                1
            ),
            "average_hunger": round(
                self.get_average_hunger(),
                1
            ),
            "best_agent": (
                best.agent_id
                if best is not None
                else None
            ),
            "best_score": round(
                self.best_score,
                1
            ),
            "winner": (
                self.winner.agent_id
                if self.winner is not None
                else None
            ),
            "winner_reason":
                self.winner_reason,
        }

    def get_agent_status(
        self,
        agent
    ):
        """
        Return detailed information about
        one agent.
        """

        return {
            "id": agent.agent_id,
            "alive": agent.alive,
            "team": getattr(
                agent,
                "team",
                None
            ),
            "personality": agent.personality,
            "state": agent.state,
            "action": getattr(
                agent,
                "last_action",
                None
            ),
            "rank": agent.rank,
            "score": round(
                agent.score,
                2
            ),
            "health": round(
                agent.health,
                1
            ),
            "energy": round(
                agent.energy,
                1
            ),
            "hunger": round(
                agent.hunger,
                1
            ),
            "kills": agent.kills,
            "attacks": agent.attacks,
            "damage_dealt": round(
                agent.damage_dealt,
                1
            ),
            "damage_taken": round(
                agent.damage_taken,
                1
            ),
            "resources": round(
                agent.resources_collected,
                1
            ),
            "survival_ticks":
                agent.survival_ticks,
            "x": round(
                agent.x,
                1
            ),
            "y": round(
                agent.y,
                1
            ),
        }

    def export_results(self):
        """
        Return all important simulation results
        in a serialisable dictionary.
        """

        return {
            "simulation": {
                "version": self.VERSION,
                "round": self.round_number,
                "total_ticks": self.total_ticks,
                "finished": self.finished,
                "winner": (
                    self.winner.agent_id
                    if self.winner
                    else None
                ),
                "winner_reason":
                    self.winner_reason,
            },
            "statistics": {
                "population":
                    self.get_population(),
                "deaths":
                    self.total_deaths,
                "kills":
                    self.total_kills,
                "attacks":
                    self.total_attacks,
                "damage":
                    self.total_damage,
                "decisions":
                    self.total_decisions,
                "total_score":
                    self.get_total_score(),
                "average_score":
                    self.get_average_score(),
            },
            "agents": [
                self.get_agent_status(agent)
                for agent in self.agents
            ],
            "teams":
                self.get_team_scores(),
            "round_history":
                list(self.round_history),
        }

    def __repr__(self):
        return (
            f"Simulation("
            f"version={self.VERSION}, "
            f"tick={self.total_ticks}, "
            f"population="
            f"{self.get_population()}, "
            f"running="
            f"{self.running}"
            f")"
        )