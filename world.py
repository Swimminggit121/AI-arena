class World:
    def __init__(self, width=900, height=600):
        self.width = width
        self.height = height

        self.tick = 0

    def update(self, agents):
        """Update every agent and advance the simulation."""

        for agent in agents:
            agent.update(self)

        self.tick += 1

    def reset(self):
        self.tick = 0