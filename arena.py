import tkinter as tk
from tkinter import ttk


VERSION = "0.5.2"


class Arena(tk.Frame):
    def __init__(self, parent, simulation, width=900, height=600):
        super().__init__(parent, bg="#111111")

        self.simulation = simulation
        self.width = width
        self.height = height

        self.show_targets = True
        self.show_health = True
        self.show_energy = True

        self.selected_agent = None
        self.last_state_signature = None

        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#151515",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_checkbutton(
            label="Show Targets",
            command=self.toggle_targets
        )
        self.context_menu.add_checkbutton(
            label="Show Health Bars",
            command=self.toggle_health
        )
        self.context_menu.add_checkbutton(
            label="Show Energy Bars",
            command=self.toggle_energy
        )

        self.canvas.bind("<Configure>", self.on_resize)

        self.render()

    # ---------------------------------------------------------
    # RESIZE
    # ---------------------------------------------------------

    def on_resize(self, event):
        if event.width > 100:
            self.width = event.width

        if event.height > 100:
            self.height = event.height

        self.render()

    # ---------------------------------------------------------
    # UPDATE / RENDER
    # ---------------------------------------------------------

    def render(self):
        self.canvas.delete("all")

        self.draw_background()
        self.draw_grid()
        self.draw_agents()
        self.draw_targets()
        self.draw_selected_agent()
        self.draw_overlay()

    def draw_background(self):
        self.canvas.configure(bg="#151515")

    def draw_grid(self):
        spacing = 50

        for x in range(0, self.width, spacing):
            self.canvas.create_line(
                x,
                0,
                x,
                self.height,
                fill="#202020"
            )

        for y in range(0, self.height, spacing):
            self.canvas.create_line(
                0,
                y,
                self.width,
                y,
                fill="#202020"
            )

    # ---------------------------------------------------------
    # AGENTS
    # ---------------------------------------------------------

    def draw_agents(self):
        agents = getattr(self.simulation, "agents", [])

        for agent in agents:
            if not getattr(agent, "alive", True):
                continue

            x = getattr(agent, "x", 0)
            y = getattr(agent, "y", 0)

            radius = getattr(agent, "radius", 10)

            color = self.get_agent_color(agent)

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline="#ffffff",
                width=1
            )

            # Agent ID
            agent_id = getattr(agent, "agent_id", None)

            if agent_id is None:
                agent_id = getattr(agent, "id", "?")

            self.canvas.create_text(
                x,
                y - radius - 9,
                text=str(agent_id),
                fill="#ffffff",
                font=("Segoe UI", 8, "bold")
            )

            # Health bar
            if self.show_health:
                self.draw_health_bar(agent, x, y, radius)

            # Energy bar
            if self.show_energy:
                self.draw_energy_bar(agent, x, y, radius)

    def get_agent_color(self, agent):
        team = getattr(agent, "team", "red")

        if isinstance(team, str):
            team = team.lower()

            if team == "red":
                return "#e06c75"

            if team == "blue":
                return "#5a9ee0"

        return "#bbbbbb"

    # ---------------------------------------------------------
    # HEALTH / ENERGY
    # ---------------------------------------------------------

    def draw_health_bar(self, agent, x, y, radius):
        health = getattr(agent, "health", 0)
        max_health = getattr(agent, "max_health", 100)

        if max_health <= 0:
            return

        percentage = max(0, min(1, health / max_health))

        bar_width = 28
        bar_height = 4

        left = x - bar_width / 2
        top = y + radius + 4

        self.canvas.create_rectangle(
            left,
            top,
            left + bar_width,
            top + bar_height,
            fill="#333333",
            outline=""
        )

        self.canvas.create_rectangle(
            left,
            top,
            left + bar_width * percentage,
            top + bar_height,
            fill="#6bcf73",
            outline=""
        )

    def draw_energy_bar(self, agent, x, y, radius):
        energy = getattr(agent, "energy", 0)
        max_energy = getattr(agent, "max_energy", 100)

        if max_energy <= 0:
            return

        percentage = max(0, min(1, energy / max_energy))

        bar_width = 28
        bar_height = 3

        left = x - bar_width / 2
        top = y + radius + 10

        self.canvas.create_rectangle(
            left,
            top,
            left + bar_width,
            top + bar_height,
            fill="#333333",
            outline=""
        )

        self.canvas.create_rectangle(
            left,
            top,
            left + bar_width * percentage,
            top + bar_height,
            fill="#d6b65a",
            outline=""
        )

    # ---------------------------------------------------------
    # TARGETS
    # ---------------------------------------------------------

    def draw_targets(self):
        if not self.show_targets:
            return

        agents = getattr(self.simulation, "agents", [])

        for agent in agents:
            if not getattr(agent, "alive", True):
                continue

            target = getattr(agent, "target", None)

            if target is None:
                continue

            if not getattr(target, "alive", True):
                continue

            x1 = getattr(agent, "x", 0)
            y1 = getattr(agent, "y", 0)

            x2 = getattr(target, "x", 0)
            y2 = getattr(target, "y", 0)

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="#555555",
                dash=(3, 5),
                width=1
            )

    # ---------------------------------------------------------
    # SELECTED AGENT
    # ---------------------------------------------------------

    def draw_selected_agent(self):
        if self.selected_agent is None:
            return

        agent = self.selected_agent

        if not getattr(agent, "alive", True):
            return

        x = getattr(agent, "x", 0)
        y = getattr(agent, "y", 0)
        radius = getattr(agent, "radius", 10)

        self.canvas.create_oval(
            x - radius - 5,
            y - radius - 5,
            x + radius + 5,
            y + radius + 5,
            outline="#ffffff",
            width=2
        )

        self.draw_agent_information(agent)

    def draw_agent_information(self, agent):
        panel_width = 230
        panel_height = 190

        x1 = 15
        y1 = 15
        x2 = x1 + panel_width
        y2 = y1 + panel_height

        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill="#1d1d1d",
            outline="#444444"
        )

        agent_id = getattr(agent, "agent_id", None)

        if agent_id is None:
            agent_id = getattr(agent, "id", "?")

        team = getattr(agent, "team", "unknown")
        personality = getattr(agent, "personality", "unknown")
        health = getattr(agent, "health", 0)
        energy = getattr(agent, "energy", 0)
        kills = getattr(agent, "kills", 0)
        score = getattr(agent, "score", 0)
        intelligence = getattr(agent, "intelligence", 0)
        aggression = getattr(agent, "aggression", 0)

        lines = [
            f"Agent {agent_id}",
            f"Team: {team}",
            f"State: {self.get_agent_state(agent)}",
            f"Personality: {personality}",
            f"Health: {health:.1f}",
            f"Energy: {energy:.1f}",
            f"Kills: {kills}",
            f"Score: {score:.1f}",
            f"Intelligence: {intelligence:.2f}",
            f"Aggression: {aggression:.2f}",
        ]

        for index, line in enumerate(lines):
            self.canvas.create_text(
                x1 + 12,
                y1 + 12 + index * 17,
                text=line,
                anchor="w",
                fill="#eeeeee",
                font=("Segoe UI", 9)
            )

    def get_agent_state(self, agent):
        if not getattr(agent, "alive", True):
            return "DEAD"

        state = getattr(agent, "state", None)

        if state is None:
            return "ACTIVE"

        if hasattr(state, "name"):
            return state.name

        return str(state)

    # ---------------------------------------------------------
    # OVERLAY
    # ---------------------------------------------------------

    def draw_overlay(self):
        stats = {}

        try:
            stats = self.simulation.get_statistics()
        except Exception:
            pass

        tick = stats.get(
            "tick",
            getattr(self.simulation, "tick", 0)
        )

        speed = stats.get(
            "speed",
            getattr(self.simulation, "speed", 1)
        )

        agents = stats.get(
            "agents",
            len(getattr(self.simulation, "agents", []))
        )

        performance = {}

        try:
            performance = self.simulation.get_performance()
        except Exception:
            pass

        fps = performance.get("fps", 0)

        text = (
            f"Agents: {agents}   "
            f"Tick: {tick}   "
            f"Speed: {speed:.2f}x   "
            f"FPS: {fps:.1f}"
        )

        self.canvas.create_rectangle(
            0,
            self.height - 32,
            self.width,
            self.height,
            fill="#1b1b1b",
            outline=""
        )

        self.canvas.create_text(
            12,
            self.height - 16,
            text=text,
            anchor="w",
            fill="#dddddd",
            font=("Segoe UI", 9)
        )

    # ---------------------------------------------------------
    # MOUSE
    # ---------------------------------------------------------

    def on_click(self, event):
        agent = self.get_agent_at_position(event.x, event.y)

        if agent is not None:
            self.selected_agent = agent
            self.render()
        else:
            self.selected_agent = None
            self.render()

    def get_agent_at_position(self, x, y):
        agents = getattr(self.simulation, "agents", [])

        closest = None
        closest_distance = float("inf")

        for agent in agents:
            if not getattr(agent, "alive", True):
                continue

            agent_x = getattr(agent, "x", 0)
            agent_y = getattr(agent, "y", 0)
            radius = getattr(agent, "radius", 10)

            distance = (
                (agent_x - x) ** 2 +
                (agent_y - y) ** 2
            ) ** 0.5

            if distance <= radius + 5 and distance < closest_distance:
                closest = agent
                closest_distance = distance

        return closest

    def on_right_click(self, event):
        try:
            self.context_menu.tk_popup(
                event.x_root,
                event.y_root
            )
        finally:
            self.context_menu.grab_release()

    # ---------------------------------------------------------
    # CONTEXT MENU
    # ---------------------------------------------------------

    def toggle_targets(self):
        self.show_targets = not self.show_targets
        self.render()

    def toggle_health(self):
        self.show_health = not self.show_health
        self.render()

    def toggle_energy(self):
        self.show_energy = not self.show_energy
        self.render()

    # ---------------------------------------------------------
    # SPEED
    # ---------------------------------------------------------

    def change_speed(self, direction):
        if direction > 0:
            self.simulation.increase_speed()
        else:
            self.simulation.decrease_speed()

        self.render()

    # ---------------------------------------------------------
    # STATE SIGNATURE
    # ---------------------------------------------------------

    def build_state_signature(self):
        agents = getattr(self.simulation, "agents", [])

        state = []

        for agent in agents:
            state.append(
                (
                    getattr(agent, "agent_id", getattr(agent, "id", None)),
                    round(getattr(agent, "x", 0), 1),
                    round(getattr(agent, "y", 0), 1),
                    getattr(agent, "team", None),
                    getattr(agent, "alive", True),
                    getattr(
                        getattr(agent, "target", None),
                        "agent_id",
                        None
                    )
                )
            )

        return tuple(state)

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(self):
        signature = self.build_state_signature()

        if signature != self.last_state_signature:
            self.render()
            self.last_state_signature = signature
        else:
            self.render()

        self.after(30, self.update)

    # ---------------------------------------------------------
    # START
    # ---------------------------------------------------------

    def start_updates(self):
        self.last_state_signature = None
        self.after(30, self.update)