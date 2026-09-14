import math
import time
import tkinter as tk


class Arena:
    VERSION = "0.4.0"

    TEAM_COLORS = [
        "#4da6ff",
        "#ff5c5c",
        "#55cc88",
        "#c77dff",
        "#ffb347",
        "#4dd0e1",
        "#ff79c6",
        "#d4e157",
    ]

    PERSONALITY_COLORS = {
        "aggressive": "#ff5c5c",
        "defensive": "#4da6ff",
        "explorer": "#55cc88",
        "balanced": "#c77dff",
    }

    STATE_COLORS = {
        "idle": "#8b949e",
        "wandering": "#4da6ff",
        "exploring": "#55cc88",
        "investigating": "#ffb347",
        "chasing": "#ff5c5c",
        "fleeing": "#c77dff",
        "resting": "#8b949e",
        "dead": "#44484f",
    }

    def __init__(self, root, simulation):
        self.root = root
        self.simulation = simulation

        self.canvas_width = simulation.world.width
        self.canvas_height = simulation.world.height

        self.background = "#101216"
        self.grid_color = "#1b1e24"
        self.grid_major_color = "#252a32"
        self.border_color = "#343a44"

        self.selected_agent = None
        self.hovered_agent = None

        self.show_grid = True
        self.show_labels = True
        self.show_health = True
        self.show_energy = True
        self.show_targets = True
        self.show_vision = False
        self.show_resources = True
        self.show_obstacles = True
        self.show_effects = True
        self.show_spawn_points = False

        self.grid_spacing = 50

        self.mouse_x = None
        self.mouse_y = None

        self.last_draw_time = time.perf_counter()
        self.frame_times = []
        self.frames = 0

        self.attack_effects = []
        self.selection_pulse = 0.0

        self._bind_events()

        self.canvas = tk.Canvas(
            root,
            width=self.canvas_width,
            height=self.canvas_height,
            background=self.background,
            highlightthickness=0,
            bd=0,
        )

        self.canvas.pack(
            padx=20,
            pady=(20, 10),
        )

        self._create_context_menu()

    def _bind_events(self):
        self.root.bind(
            "<KeyPress-g>",
            lambda event: self.toggle_grid(),
        )

        self.root.bind(
            "<KeyPress-l>",
            lambda event: self.toggle_labels(),
        )

        self.root.bind(
            "<KeyPress-h>",
            lambda event: self.toggle_health(),
        )

        self.root.bind(
            "<KeyPress-e>",
            lambda event: self.toggle_energy(),
        )

        self.root.bind(
            "<KeyPress-t>",
            lambda event: self.toggle_targets(),
        )

        self.root.bind(
            "<KeyPress-v>",
            lambda event: self.toggle_vision(),
        )

        self.root.bind(
            "<KeyPress-r>",
            lambda event: self.toggle_resources(),
        )

        self.root.bind(
            "<KeyPress-o>",
            lambda event: self.toggle_obstacles(),
        )

        self.root.bind(
            "<KeyPress-f>",
            lambda event: self.toggle_effects(),
        )

        self.root.bind(
            "<KeyPress-s>",
            lambda event: self.toggle_spawn_points(),
        )

        self.root.bind(
            "<Escape>",
            lambda event: self.clear_selection(),
        )

    def _create_context_menu(self):
        self.context_menu = tk.Menu(
            self.root,
            tearoff=0,
            background="#171a20",
            foreground="#ffffff",
            activebackground="#282f3a",
            activeforeground="#ffffff",
        )

        self.context_menu.add_command(
            label="Clear selection",
            command=self.clear_selection,
        )

        self.context_menu.add_separator()

        self.context_menu.add_command(
            label="Toggle grid",
            command=self.toggle_grid,
        )

        self.context_menu.add_command(
            label="Toggle labels",
            command=self.toggle_labels,
        )

        self.context_menu.add_command(
            label="Toggle health",
            command=self.toggle_health,
        )

        self.context_menu.add_command(
            label="Toggle energy",
            command=self.toggle_energy,
        )

        self.context_menu.add_command(
            label="Toggle targets",
            command=self.toggle_targets,
        )

        self.context_menu.add_command(
            label="Toggle vision",
            command=self.toggle_vision,
        )

    def draw(self):
        if not hasattr(self, "canvas"):
            return

        start_time = time.perf_counter()

        self.canvas.delete("all")

        self._update_effects()

        self.draw_background()
        self.draw_grid()
        self.draw_obstacles()
        self.draw_resources()
        self.draw_spawn_points()
        self.draw_targets()
        self.draw_vision()
        self.draw_agents()
        self.draw_effects()
        self.draw_selection()
        self.draw_hover()
        self.draw_world_border()

        elapsed = time.perf_counter() - start_time

        self.frame_times.append(elapsed)

        if len(self.frame_times) > 60:
            self.frame_times.pop(0)

        self.frames += 1

        self.last_draw_time = time.perf_counter()

    def draw_background(self):
        self.canvas.create_rectangle(
            0,
            0,
            self.canvas_width,
            self.canvas_height,
            fill=self.background,
            outline="",
        )

        self.canvas.create_rectangle(
            0,
            0,
            self.canvas_width,
            self.canvas_height,
            fill="",
            outline="#15181d",
            width=1,
        )

    def draw_grid(self):
        if not self.show_grid:
            return

        spacing = self.grid_spacing

        for x in range(0, self.canvas_width + 1, spacing):
            if x % (spacing * 2) == 0:
                color = self.grid_major_color
            else:
                color = self.grid_color

            self.canvas.create_line(
                x,
                0,
                x,
                self.canvas_height,
                fill=color,
                width=1,
            )

        for y in range(0, self.canvas_height + 1, spacing):
            if y % (spacing * 2) == 0:
                color = self.grid_major_color
            else:
                color = self.grid_color

            self.canvas.create_line(
                0,
                y,
                self.canvas_width,
                y,
                fill=color,
                width=1,
            )

        for x in range(0, self.canvas_width + 1, spacing * 2):
            self.canvas.create_text(
                x + 4,
                10,
                text=str(x),
                fill="#3d434d",
                anchor="nw",
                font=("Arial", 7),
            )

        for y in range(0, self.canvas_height + 1, spacing * 2):
            self.canvas.create_text(
                5,
                y + 3,
                text=str(y),
                fill="#3d434d",
                anchor="nw",
                font=("Arial", 7),
            )

    def draw_world_border(self):
        self.canvas.create_rectangle(
            1,
            1,
            self.canvas_width - 1,
            self.canvas_height - 1,
            outline=self.border_color,
            width=2,
        )

    def draw_obstacles(self):
        if not self.show_obstacles:
            return

        world = self.simulation.world

        obstacles = getattr(
            world,
            "obstacles",
            [],
        )

        for obstacle in obstacles:
            if obstacle is None:
                continue

            left = self._get_value(
                obstacle,
                "x",
                0,
            )

            top = self._get_value(
                obstacle,
                "y",
                0,
            )

            width = self._get_value(
                obstacle,
                "width",
                20,
            )

            height = self._get_value(
                obstacle,
                "height",
                20,
            )

            right = left + width
            bottom = top + height

            self.canvas.create_rectangle(
                left,
                top,
                right,
                bottom,
                fill="#1d2229",
                outline="#3a414b",
                width=1,
            )

            diagonal = 10

            current = left - height

            while current < right:
                x1 = max(left, current)
                y1 = max(top, top + left - current)

                x2 = min(right, current + height)
                y2 = min(bottom, top + right - current)

                self.canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="#272d35",
                    width=1,
                )

                current += diagonal

    def draw_resources(self):
        if not self.show_resources:
            return

        world = self.simulation.world

        resources = getattr(
            world,
            "resources",
            [],
        )

        for resource in resources:
            if resource is None:
                continue

            active = self._get_value(
                resource,
                "active",
                True,
            )

            if callable(active):
                try:
                    active = active()
                except Exception:
                    active = True

            if not active:
                continue

            x = self._get_value(
                resource,
                "x",
                0,
            )

            y = self._get_value(
                resource,
                "y",
                0,
            )

            amount = self._get_value(
                resource,
                "amount",
                0,
            )

            resource_type = str(
                self._get_value(
                    resource,
                    "resource_type",
                    self._get_value(
                        resource,
                        "type",
                        "resource",
                    ),
                )
            ).lower()

            radius = 5

            if resource_type == "food":
                fill = "#55cc88"
                symbol = "+"
            elif resource_type == "water":
                fill = "#4da6ff"
                symbol = "~"
            elif resource_type == "energy":
                fill = "#ffb347"
                symbol = "*"
            else:
                fill = "#c77dff"
                symbol = "?"

            if amount > 0:
                radius += min(
                    4,
                    amount / 25,
                )

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=fill,
                outline="#ffffff",
                width=1,
            )

            self.canvas.create_text(
                x,
                y,
                text=symbol,
                fill="#101216",
                font=("Arial", 7, "bold"),
            )

    def draw_spawn_points(self):
        if not self.show_spawn_points:
            return

        for agent in self.simulation.agents:
            x = self._get_value(
                agent,
                "spawn_x",
                None,
            )

            y = self._get_value(
                agent,
                "spawn_y",
                None,
            )

            if x is None or y is None:
                continue

            size = 7

            self.canvas.create_rectangle(
                x - size,
                y - size,
                x + size,
                y + size,
                outline="#555d68",
                dash=(2, 3),
            )

            self.canvas.create_line(
                x - 4,
                y,
                x + 4,
                y,
                fill="#555d68",
            )

            self.canvas.create_line(
                x,
                y - 4,
                x,
                y + 4,
                fill="#555d68",
            )

    def draw_targets(self):
        if not self.show_targets:
            return

        for agent in self.simulation.agents:
            if not getattr(agent, "alive", True):
                continue

            target = getattr(
                agent,
                "target",
                None,
            )

            if target is None:
                continue

            if not getattr(target, "alive", True):
                continue

            if target is agent:
                continue

            x1 = self._get_value(
                agent,
                "x",
                0,
            )

            y1 = self._get_value(
                agent,
                "y",
                0,
            )

            x2 = self._get_value(
                target,
                "x",
                0,
            )

            y2 = self._get_value(
                target,
                "y",
                0,
            )

            color = self._get_target_color(
                agent
            )

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=color,
                width=1,
                dash=(4, 5),
            )

            self.canvas.create_oval(
                x2 - 3,
                y2 - 3,
                x2 + 3,
                y2 + 3,
                outline=color,
                width=1,
            )

    def draw_vision(self):
        if not self.show_vision:
            return

        for agent in self.simulation.agents:
            if not getattr(agent, "alive", True):
                continue

            vision = self._get_value(
                agent,
                "vision_range",
                self._get_value(
                    agent,
                    "vision",
                    0,
                ),
            )

            if vision <= 0:
                continue

            x = self._get_value(
                agent,
                "x",
                0,
            )

            y = self._get_value(
                agent,
                "y",
                0,
            )

            color = self._get_agent_color(
                agent
            )

            self.canvas.create_oval(
                x - vision,
                y - vision,
                x + vision,
                y + vision,
                outline=color,
                width=1,
                dash=(2, 5),
            )

    def draw_agents(self):
        agents = self.simulation.agents

        for agent in agents:
            if getattr(agent, "alive", True):
                self.draw_alive_agent(agent)
            else:
                self.draw_dead_agent(agent)

    def draw_alive_agent(self, agent):
        x = self._get_value(
            agent,
            "x",
            0,
        )

        y = self._get_value(
            agent,
            "y",
            0,
        )

        size = self._get_value(
            agent,
            "size",
            10,
        )

        color = self._get_agent_color(
            agent
        )

        state = str(
            self._get_value(
                agent,
                "state",
                "idle",
            )
        ).lower()

        state_color = self.STATE_COLORS.get(
            state,
            color,
        )

        selected = (
            self.selected_agent is agent
        )

        hovered = (
            self.hovered_agent is agent
        )

        if selected:
            pulse = (
                math.sin(
                    time.perf_counter() * 5
                )
                + 1
            ) / 2

            outer = size + 7 + pulse * 2

            self.canvas.create_oval(
                x - outer,
                y - outer,
                x + outer,
                y + outer,
                outline="#ffffff",
                width=2,
            )

        elif hovered:
            outer = size + 5

            self.canvas.create_oval(
                x - outer,
                y - outer,
                x + outer,
                y + outer,
                outline="#777f8c",
                width=1,
            )

        self._draw_direction_indicator(
            agent,
            x,
            y,
            size,
            color,
        )

        self.canvas.create_oval(
            x - size,
            y - size,
            x + size,
            y + size,
            fill=color,
            outline="#ffffff" if selected else state_color,
            width=2 if selected else 1,
        )

        inner_size = max(
            2,
            size * 0.45,
        )

        self.canvas.create_oval(
            x - inner_size,
            y - inner_size,
            x + inner_size,
            y + inner_size,
            fill="#101216",
            outline="",
        )

        self.canvas.create_oval(
            x - 2,
            y - 2,
            x + 2,
            y + 2,
            fill="#ffffff",
            outline="",
        )

        if self.show_health:
            self.draw_health_bar(
                agent,
                x,
                y,
                size,
            )

        if self.show_energy:
            self.draw_energy_bar(
                agent,
                x,
                y,
                size,
            )

        if self.show_labels:
            self.draw_agent_label(
                agent,
                x,
                y,
                size,
                state_color,
            )

    def draw_dead_agent(self, agent):
        x = self._get_value(
            agent,
            "x",
            0,
        )

        y = self._get_value(
            agent,
            "y",
            0,
        )

        size = self._get_value(
            agent,
            "size",
            10,
        )

        radius = max(
            size * 0.8,
            7,
        )

        self.canvas.create_line(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill="#555b64",
            width=2,
        )

        self.canvas.create_line(
            x + radius,
            y - radius,
            x - radius,
            y + radius,
            fill="#555b64",
            width=2,
        )

        if self.show_labels:
            agent_id = self._get_value(
                agent,
                "agent_id",
                "?",
            )

            self.canvas.create_text(
                x,
                y + radius + 10,
                text=f"#{agent_id} DEAD",
                fill="#555b64",
                font=("Arial", 7, "bold"),
            )

    def _draw_direction_indicator(
        self,
        agent,
        x,
        y,
        size,
        color,
    ):
        dx = self._get_value(
            agent,
            "dx",
            None,
        )

        dy = self._get_value(
            agent,
            "dy",
            None,
        )

        if dx is None or dy is None:
            direction = self._get_value(
                agent,
                "direction",
                None,
            )

            if direction is None:
                return

            try:
                angle = float(direction)

                if abs(angle) > math.pi * 2:
                    angle = math.radians(angle)

                dx = math.cos(angle)
                dy = math.sin(angle)

            except Exception:
                return

        magnitude = math.sqrt(
            dx * dx + dy * dy
        )

        if magnitude < 0.001:
            return

        dx /= magnitude
        dy /= magnitude

        length = size + 6

        self.canvas.create_line(
            x,
            y,
            x + dx * length,
            y + dy * length,
            fill="#ffffff",
            width=1,
        )

    def draw_health_bar(
        self,
        agent,
        x,
        y,
        size,
    ):
        health = self._get_value(
            agent,
            "health",
            0,
        )

        max_health = self._get_value(
            agent,
            "max_health",
            100,
        )

        ratio = self._safe_ratio(
            health,
            max_health,
        )

        width = max(
            24,
            size * 2.8,
        )

        height = 4

        left = x - width / 2
        top = y + size + 5

        self.canvas.create_rectangle(
            left,
            top,
            left + width,
            top + height,
            fill="#252a31",
            outline="",
        )

        if ratio > 0:
            if ratio > 0.6:
                fill = "#55cc88"
            elif ratio > 0.3:
                fill = "#ffb347"
            else:
                fill = "#ff5c5c"

            self.canvas.create_rectangle(
                left,
                top,
                left + width * ratio,
                top + height,
                fill=fill,
                outline="",
            )

    def draw_energy_bar(
        self,
        agent,
        x,
        y,
        size,
    ):
        energy = self._get_value(
            agent,
            "energy",
            0,
        )

        max_energy = self._get_value(
            agent,
            "max_energy",
            100,
        )

        ratio = self._safe_ratio(
            energy,
            max_energy,
        )

        width = max(
            24,
            size * 2.8,
        )

        height = 3

        left = x - width / 2
        top = y + size + 10

        self.canvas.create_rectangle(
            left,
            top,
            left + width,
            top + height,
            fill="#252a31",
            outline="",
        )

        if ratio > 0:
            self.canvas.create_rectangle(
                left,
                top,
                left + width * ratio,
                top + height,
                fill="#4da6ff",
                outline="",
            )

    def draw_agent_label(
        self,
        agent,
        x,
        y,
        size,
        state_color,
    ):
        agent_id = self._get_value(
            agent,
            "agent_id",
            "?",
        )

        personality = str(
            self._get_value(
                agent,
                "personality",
                "",
            )
        ).lower()

        team = self._get_value(
            agent,
            "team",
            None,
        )

        name = self._get_value(
            agent,
            "name",
            None,
        )

        if name:
            label = str(name)
        else:
            label = f"#{agent_id}"

        self.canvas.create_text(
            x,
            y - size - 11,
            text=label,
            fill="#ffffff",
            font=("Arial", 8, "bold"),
        )

        if personality:
            self.canvas.create_text(
                x,
                y - size - 22,
                text=personality.upper(),
                fill=self.PERSONALITY_COLORS.get(
                    personality,
                    state_color,
                ),
                font=("Arial", 6),
            )

        if team is not None:
            self.canvas.create_text(
                x,
                y + size + 16,
                text=f"T{team}",
                fill=self._get_team_color(
                    team
                ),
                font=("Arial", 6, "bold"),
            )

    def draw_selection(self):
        agent = self.selected_agent

        if agent is None:
            return

        if not getattr(agent, "alive", True):
            return

        x = self._get_value(
            agent,
            "x",
            0,
        )

        y = self._get_value(
            agent,
            "y",
            0,
        )

        size = self._get_value(
            agent,
            "size",
            10,
        )

        self.canvas.create_oval(
            x - size - 5,
            y - size - 5,
            x + size + 5,
            y + size + 5,
            outline="#ffffff",
            width=2,
            dash=(3, 3),
        )

        self.draw_selected_agent_info(
            agent
        )

    def draw_selected_agent_info(
        self,
        agent,
    ):
        panel_width = 205
        panel_height = 190

        left = self.canvas_width - panel_width - 15
        top = 15

        self.canvas.create_rectangle(
            left,
            top,
            left + panel_width,
            top + panel_height,
            fill="#15191f",
            outline="#343a44",
            width=1,
        )

        agent_id = self._get_value(
            agent,
            "agent_id",
            "?",
        )

        personality = self._get_value(
            agent,
            "personality",
            "unknown",
        )

        state = self._get_value(
            agent,
            "state",
            "unknown",
        )

        team = self._get_value(
            agent,
            "team",
            "none",
        )

        health = self._get_value(
            agent,
            "health",
            0,
        )

        energy = self._get_value(
            agent,
            "energy",
            0,
        )

        hunger = self._get_value(
            agent,
            "hunger",
            0,
        )

        score = self._get_value(
            agent,
            "score",
            0,
        )

        kills = self._get_value(
            agent,
            "kills",
            0,
        )

        attacks = self._get_value(
            agent,
            "attacks",
            0,
        )

        damage = self._get_value(
            agent,
            "damage_dealt",
            0,
        )

        survival = self._get_value(
            agent,
            "survival_ticks",
            0,
        )

        lines = [
            (
                f"AGENT #{agent_id}",
                "#ffffff",
                True,
            ),
            (
                f"Personality: {personality}",
                "#9ba3af",
                False,
            ),
            (
                f"State: {state}",
                self.STATE_COLORS.get(
                    str(state).lower(),
                    "#9ba3af",
                ),
                False,
            ),
            (
                f"Team: {team}",
                self._get_team_color(team),
                False,
            ),
            (
                f"Health: {self._format_number(health)}",
                "#ffffff",
                False,
            ),
            (
                f"Energy: {self._format_number(energy)}",
                "#ffffff",
                False,
            ),
            (
                f"Hunger: {self._format_number(hunger)}",
                "#ffffff",
                False,
            ),
            (
                f"Score: {self._format_number(score)}",
                "#ffffff",
                False,
            ),
            (
                f"Kills: {kills}",
                "#ffffff",
                False,
            ),
            (
                f"Attacks: {attacks}",
                "#ffffff",
                False,
            ),
            (
                f"Damage: {self._format_number(damage)}",
                "#ffffff",
                False,
            ),
            (
                f"Survival: {survival}",
                "#ffffff",
                False,
            ),
        ]

        y = top + 14

        for text, color, bold in lines:
            self.canvas.create_text(
                left + 10,
                y,
                text=text,
                fill=color,
                anchor="w",
                font=(
                    "Arial",
                    9 if bold else 8,
                    "bold" if bold else "normal",
                ),
            )

            y += 14

    def draw_hover(self):
        agent = self.hovered_agent

        if agent is None:
            return

        if agent is self.selected_agent:
            return

        if not getattr(agent, "alive", True):
            return

        x = self._get_value(
            agent,
            "x",
            0,
        )

        y = self._get_value(
            agent,
            "y",
            0,
        )

        size = self._get_value(
            agent,
            "size",
            10,
        )

        agent_id = self._get_value(
            agent,
            "agent_id",
            "?",
        )

        personality = self._get_value(
            agent,
            "personality",
            "unknown",
        )

        text = (
            f"#{agent_id}  "
            f"{str(personality).upper()}"
        )

        self.canvas.create_rectangle(
            x + size + 7,
            y - 18,
            x + size + 7 + len(text) * 6.5,
            y - 2,
            fill="#171b21",
            outline="#343a44",
        )

        self.canvas.create_text(
            x + size + 11,
            y - 10,
            text=text,
            fill="#ffffff",
            anchor="w",
            font=("Arial", 7),
        )

    def draw_effects(self):
        if not self.show_effects:
            return

        current = time.perf_counter()

        for effect in self.attack_effects:
            start_x = effect["start_x"]
            start_y = effect["start_y"]
            end_x = effect["end_x"]
            end_y = effect["end_y"]

            remaining = (
                effect["expires"]
                - current
            )

            duration = effect["duration"]

            ratio = self._safe_ratio(
                remaining,
                duration,
            )

            if ratio <= 0:
                continue

            self.canvas.create_line(
                start_x,
                start_y,
                end_x,
                end_y,
                fill="#ff5c5c",
                width=max(
                    1,
                    int(1 + ratio * 3),
                ),
            )

            radius = 3 + ratio * 4

            self.canvas.create_oval(
                end_x - radius,
                end_y - radius,
                end_x + radius,
                end_y + radius,
                outline="#ffb347",
                width=1,
            )

    def _update_effects(self):
        now = time.perf_counter()

        self.attack_effects = [
            effect
            for effect in self.attack_effects
            if effect["expires"] > now
        ]

        self._detect_attacks()

    def _detect_attacks(self):
        for agent in self.simulation.agents:
            attacks = self._get_value(
                agent,
                "successful_attacks",
                None,
            )

            if attacks is None:
                continue

        return

    def _get_agent_color(self, agent):
        team = self._get_value(
            agent,
            "team",
            None,
        )

        if team is not None:
            try:
                team_index = int(team)

                return self.TEAM_COLORS[
                    team_index
                    % len(self.TEAM_COLORS)
                ]

            except Exception:
                pass

        personality = str(
            self._get_value(
                agent,
                "personality",
                "",
            )
        ).lower()

        return self.PERSONALITY_COLORS.get(
            personality,
            "#4da6ff",
        )

    def _get_target_color(self, agent):
        personality = str(
            self._get_value(
                agent,
                "personality",
                "",
            )
        ).lower()

        if personality == "aggressive":
            return "#ff5c5c"

        if personality == "defensive":
            return "#4da6ff"

        if personality == "explorer":
            return "#55cc88"

        return "#777f8c"

    def _get_team_color(self, team):
        try:
            index = int(team)

            return self.TEAM_COLORS[
                index % len(self.TEAM_COLORS)
            ]

        except Exception:
            return "#8b949e"

    def _get_value(
        self,
        obj,
        name,
        default,
    ):
        try:
            value = getattr(
                obj,
                name,
                default,
            )

            if callable(value):
                try:
                    return value()
                except TypeError:
                    return default

            return value

        except Exception:
            return default

    def _safe_ratio(
        self,
        value,
        maximum,
    ):
        try:
            value = float(value)
            maximum = float(maximum)

            if maximum <= 0:
                return 0.0

            return max(
                0.0,
                min(
                    1.0,
                    value / maximum,
                ),
            )

        except Exception:
            return 0.0

    def _format_number(
        self,
        value,
    ):
        try:
            number = float(value)

            if number.is_integer():
                return str(
                    int(number)
                )

            return f"{number:.1f}"

        except Exception:
            return str(value)

    def find_agent_at(
        self,
        x,
        y,
    ):
        closest = None
        closest_distance = float("inf")

        for agent in self.simulation.agents:
            if not getattr(
                agent,
                "alive",
                True,
            ):
                continue

            ax = self._get_value(
                agent,
                "x",
                0,
            )

            ay = self._get_value(
                agent,
                "y",
                0,
            )

            size = self._get_value(
                agent,
                "size",
                10,
            )

            distance = math.sqrt(
                (x - ax) ** 2
                + (y - ay) ** 2
            )

            if distance <= size + 5:
                if distance < closest_distance:
                    closest = agent
                    closest_distance = distance

        return closest

    def select_agent(
        self,
        agent,
    ):
        self.selected_agent = agent

    def clear_selection(self):
        self.selected_agent = None

    def on_canvas_click(
        self,
        event,
    ):
        agent = self.find_agent_at(
            event.x,
            event.y,
        )

        if agent is None:
            self.clear_selection()
        else:
            self.select_agent(agent)

    def on_canvas_motion(
        self,
        event,
    ):
        self.mouse_x = event.x
        self.mouse_y = event.y

        self.hovered_agent = (
            self.find_agent_at(
                event.x,
                event.y,
            )
        )

    def on_canvas_leave(
        self,
        event,
    ):
        self.mouse_x = None
        self.mouse_y = None
        self.hovered_agent = None

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.draw()

    def toggle_labels(self):
        self.show_labels = not self.show_labels
        self.draw()

    def toggle_health(self):
        self.show_health = not self.show_health
        self.draw()

    def toggle_energy(self):
        self.show_energy = not self.show_energy
        self.draw()

    def toggle_targets(self):
        self.show_targets = not self.show_targets
        self.draw()

    def toggle_vision(self):
        self.show_vision = not self.show_vision
        self.draw()

    def toggle_resources(self):
        self.show_resources = not self.show_resources
        self.draw()

    def toggle_obstacles(self):
        self.show_obstacles = not self.show_obstacles
        self.draw()

    def toggle_effects(self):
        self.show_effects = not self.show_effects
        self.draw()

    def toggle_spawn_points(self):
        self.show_spawn_points = not self.show_spawn_points
        self.draw()

    def set_grid_spacing(
        self,
        spacing,
    ):
        try:
            spacing = int(spacing)

            if spacing < 10:
                spacing = 10

            if spacing > 200:
                spacing = 200

            self.grid_spacing = spacing

        except Exception:
            return

        self.draw()

    def set_show_all(
        self,
        value,
    ):
        self.show_grid = value
        self.show_labels = value
        self.show_health = value
        self.show_energy = value
        self.show_targets = value
        self.show_vision = value
        self.show_resources = value
        self.show_obstacles = value
        self.show_effects = value
        self.show_spawn_points = value

        self.draw()

    def get_fps(self):
        if not self.frame_times:
            return 0.0

        average = (
            sum(self.frame_times)
            / len(self.frame_times)
        )

        if average <= 0:
            return 0.0

        return 1.0 / average

    def get_render_statistics(self):
        return {
            "version": self.VERSION,
            "frames": self.frames,
            "fps": self.get_fps(),
            "agents": len(
                self.simulation.agents
            ),
            "selected_agent": (
                getattr(
                    self.selected_agent,
                    "agent_id",
                    None,
                )
                if self.selected_agent
                else None
            ),
            "show_grid": self.show_grid,
            "show_labels": self.show_labels,
            "show_health": self.show_health,
            "show_energy": self.show_energy,
            "show_targets": self.show_targets,
            "show_vision": self.show_vision,
            "show_resources": self.show_resources,
            "show_obstacles": self.show_obstacles,
            "show_effects": self.show_effects,
        }

    def get_selected_agent(self):
        return self.selected_agent

    def get_hovered_agent(self):
        return self.hovered_agent

    def add_attack_effect(
        self,
        attacker,
        target,
        duration=0.15,
    ):
        if attacker is None:
            return

        if target is None:
            return

        start_x = self._get_value(
            attacker,
            "x",
            0,
        )

        start_y = self._get_value(
            attacker,
            "y",
            0,
        )

        end_x = self._get_value(
            target,
            "x",
            0,
        )

        end_y = self._get_value(
            target,
            "y",
            0,
        )

        self.attack_effects.append(
            {
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration,
                "expires": (
                    time.perf_counter()
                    + duration
                ),
            }
        )

    def resize(
        self,
        width,
        height,
    ):
        try:
            width = int(width)
            height = int(height)

        except Exception:
            return

        if width < 100:
            width = 100

        if height < 100:
            height = 100

        self.canvas_width = width
        self.canvas_height = height

        self.canvas.config(
            width=width,
            height=height,
        )

        self.draw()

    def world_to_canvas(
        self,
        x,
        y,
    ):
        return x, y

    def canvas_to_world(
        self,
        x,
        y,
    ):
        return x, y

    def center_on_agent(
        self,
        agent,
    ):
        if agent is None:
            return

        x = self._get_value(
            agent,
            "x",
            self.canvas_width / 2,
        )

        y = self._get_value(
            agent,
            "y",
            self.canvas_height / 2,
        )

        self.mouse_x = x
        self.mouse_y = y

        self.select_agent(agent)

    def select_best_agent(self):
        agents = [
            agent
            for agent in self.simulation.agents
            if getattr(
                agent,
                "alive",
                True,
            )
        ]

        if not agents:
            self.clear_selection()
            return

        best = max(
            agents,
            key=lambda agent: self._get_value(
                agent,
                "score",
                0,
            ),
        )

        self.select_agent(best)

    def select_lowest_health_agent(self):
        agents = [
            agent
            for agent in self.simulation.agents
            if getattr(
                agent,
                "alive",
                True,
            )
        ]

        if not agents:
            self.clear_selection()
            return

        weakest = min(
            agents,
            key=lambda agent: self._get_value(
                agent,
                "health",
                0,
            ),
        )

        self.select_agent(weakest)

    def select_most_aggressive_agent(self):
        agents = [
            agent
            for agent in self.simulation.agents
            if getattr(
                agent,
                "alive",
                True,
            )
        ]

        if not agents:
            self.clear_selection()
            return

        aggressive = max(
            agents,
            key=lambda agent: self._get_value(
                agent,
                "attacks",
                0,
            ),
        )

        self.select_agent(aggressive)

    def select_longest_survivor(self):
        agents = list(
            self.simulation.agents
        )

        if not agents:
            self.clear_selection()
            return

        survivor = max(
            agents,
            key=lambda agent: self._get_value(
                agent,
                "survival_ticks",
                0,
            ),
        )

        self.select_agent(survivor)

    def cycle_selection(self):
        agents = [
            agent
            for agent in self.simulation.agents
            if getattr(
                agent,
                "alive",
                True,
            )
        ]

        if not agents:
            self.clear_selection()
            return

        if self.selected_agent not in agents:
            self.selected_agent = agents[0]
            return

        index = agents.index(
            self.selected_agent
        )

        index += 1

        if index >= len(agents):
            index = 0

        self.selected_agent = agents[index]

    def get_alive_count(self):
        return sum(
            1
            for agent in self.simulation.agents
            if getattr(
                agent,
                "alive",
                True,
            )
        )

    def get_dead_count(self):
        return sum(
            1
            for agent in self.simulation.agents
            if not getattr(
                agent,
                "alive",
                True,
            )
        )

    def get_state_counts(self):
        counts = {}

        for agent in self.simulation.agents:
            state = str(
                self._get_value(
                    agent,
                    "state",
                    "unknown",
                )
            ).lower()

            counts[state] = (
                counts.get(state, 0)
                + 1
            )

        return counts

    def get_team_counts(self):
        counts = {}

        for agent in self.simulation.agents:
            team = self._get_value(
                agent,
                "team",
                None,
            )

            key = (
                str(team)
                if team is not None
                else "none"
            )

            counts[key] = (
                counts.get(key, 0)
                + 1
            )

        return counts

    def get_personality_counts(self):
        counts = {}

        for agent in self.simulation.agents:
            personality = str(
                self._get_value(
                    agent,
                    "personality",
                    "unknown",
                )
            ).lower()

            counts[personality] = (
                counts.get(
                    personality,
                    0,
                )
                + 1
            )

        return counts

    def get_average_health(self):
        agents = list(
            self.simulation.agents
        )

        if not agents:
            return 0.0

        total = sum(
            float(
                self._get_value(
                    agent,
                    "health",
                    0,
                )
            )
            for agent in agents
        )

        return total / len(agents)

    def get_average_energy(self):
        agents = list(
            self.simulation.agents
        )

        if not agents:
            return 0.0

        total = sum(
            float(
                self._get_value(
                    agent,
                    "energy",
                    0,
                )
            )
            for agent in agents
        )

        return total / len(agents)

    def get_arena_summary(self):
        return {
            "version": self.VERSION,
            "width": self.canvas_width,
            "height": self.canvas_height,
            "agents": len(
                self.simulation.agents
            ),
            "alive": self.get_alive_count(),
            "dead": self.get_dead_count(),
            "average_health": (
                self.get_average_health()
            ),
            "average_energy": (
                self.get_average_energy()
            ),
            "states": self.get_state_counts(),
            "teams": self.get_team_counts(),
            "personalities": (
                self.get_personality_counts()
            ),
            "render": (
                self.get_render_statistics()
            ),
        }

    def destroy(self):
        try:
            self.canvas.destroy()
        except Exception:
            pass

        self.selected_agent = None
        self.hovered_agent = None
        self.attack_effects.clear()

    def __repr__(self):
        return (
            f"<Arena "
            f"version={self.VERSION!r} "
            f"agents={len(self.simulation.agents)} "
            f"selected="
            f"{getattr(self.selected_agent, 'agent_id', None)!r}>"
        )