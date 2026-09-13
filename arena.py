import tkinter as tk


class Arena:
    def __init__(self, root, simulation):
        self.root = root
        self.simulation = simulation

        self.canvas = tk.Canvas(
            root,
            width=simulation.world.width,
            height=simulation.world.height,
            background="#101216",
            highlightthickness=0
        )

        self.canvas.pack(
            padx=20,
            pady=(20, 10)
        )

    def draw(self):
        self.canvas.delete("all")

        self.draw_grid()
        self.draw_agents()

    def draw_grid(self):
        spacing = 50

        for x in range(0, self.simulation.world.width + 1, spacing):
            self.canvas.create_line(
                x,
                0,
                x,
                self.simulation.world.height,
                fill="#1b1e24"
            )

        for y in range(0, self.simulation.world.height + 1, spacing):
            self.canvas.create_line(
                0,
                y,
                self.simulation.world.width,
                y,
                fill="#1b1e24"
            )

    def draw_agents(self):
        for agent in self.simulation.agents:
            if not agent.alive:
                continue

            x = agent.x
            y = agent.y
            size = agent.size

            self.canvas.create_oval(
                x - size,
                y - size,
                x + size,
                y + size,
                fill="#4da6ff",
                outline="#ffffff",
                width=1
            )

            self.canvas.create_text(
                x,
                y - size - 10,
                text=f"#{agent.agent_id}",
                fill="#ffffff",
                font=("Arial", 9, "bold")
            )