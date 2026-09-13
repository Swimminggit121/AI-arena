import random

from agent import Agent
from world import World


class Simulation:
    def __init__(self, width=900, height=600, agent_count=3):
        self.world = World(width, height)

        self.agent_count = agent_count
        self.agents = []

        self.running = False

        self.reset()

    def create_agents(self):
        """Create a fresh set of agents."""

        self.agents.clear()

        for i in range(self.agent_count):
            margin = 40

            x = random.uniform(
                margin,
                self.world.width - margin
            )

            y = random.uniform(
                margin,
                self.world.height - margin
            )

            agent = Agent(
                agent_id=i + 1,
                x=x,
                y=y
            )

            self.agents.append(agent)

    def reset(self):
        """Reset the entire simulation."""

        self.running = False
        self.world.reset()
        self.create_agents()

    def update(self):
        """Run one simulation tick."""

        if not self.running:
            return

        self.world.update(self.agents)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def toggle(self):
        self.running = not self.running

    def alive_agents(self):
        return [
            agent
            for agent in self.agents
            if agent.alive
        ]