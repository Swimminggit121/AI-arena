import tkinter as tk

from simulation import Simulation
from arena import Arena


VERSION = "0.4.3"


class AIArena:
    def __init__(self, root):
        self.root = root

        self.root.title("AI Arena")
        self.root.geometry("980x760")
        self.root.minsize(980, 760)
        self.root.configure(background="#0b0d10")

        self.simulation = None
        self.arena = None

        self.show_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.arena = None

    def create_button(
        self,
        parent,
        text,
        command,
        width=24
    ):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            background="#1c2129",
            foreground="#ffffff",
            activebackground="#282f3a",
            activeforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            width=width,
            pady=12,
            font=("Arial", 11, "bold"),
            cursor="hand2"
        )

        button.pack(
            pady=7
        )

        return button

    def show_menu(self):
        self.clear_screen()

        menu = tk.Frame(
            self.root,
            background="#0b0d10"
        )

        menu.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        title = tk.Label(
            menu,
            text="AI ARENA",
            background="#0b0d10",
            foreground="#ffffff",
            font=("Arial", 32, "bold")
        )

        title.pack(
            pady=(0, 5)
        )

        subtitle = tk.Label(
            menu,
            text="Autonomous agents. One arena.",
            background="#0b0d10",
            foreground="#777d87",
            font=("Arial", 11)
        )

        subtitle.pack(
            pady=(0, 30)
        )

        self.create_button(
            menu,
            "START",
            self.start_game
        )

        self.create_button(
            menu,
            "KEYBINDINGS",
            self.show_keybindings
        )

        self.create_button(
            menu,
            "QUIT",
            self.root.destroy
        )

        version = tk.Label(
            menu,
            text=f"V{VERSION}",
            background="#0b0d10",
            foreground="#555b64",
            font=("Arial", 9)
        )

        version.pack(
            pady=(25, 0)
        )

    def show_keybindings(self):
        self.clear_screen()

        container = tk.Frame(
            self.root,
            background="#0b0d10"
        )

        container.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        title = tk.Label(
            container,
            text="KEYBINDINGS",
            background="#0b0d10",
            foreground="#ffffff",
            font=("Arial", 24, "bold")
        )

        title.pack(
            pady=(0, 25)
        )

        bindings = [
            ("G", "Toggle grid"),
            ("L", "Toggle agent labels"),
            ("H", "Toggle health bars"),
            ("E", "Toggle energy bars"),
            ("T", "Toggle target lines"),
            ("V", "Toggle vision"),
            ("R", "Toggle resources"),
            ("O", "Toggle obstacles"),
            ("F", "Toggle attack effects"),
            ("S", "Toggle spawn points"),
            ("↑ / ↓", "Change simulation speed"),
            ("← / →", "Cycle selected agent"),
            ("ESC", "Clear selection"),
        ]

        table = tk.Frame(
            container,
            background="#0b0d10"
        )

        table.pack()

        for key, description in bindings:
            row = tk.Frame(
                table,
                background="#0b0d10"
            )

            row.pack(
                fill="x",
                pady=4
            )

            key_label = tk.Label(
                row,
                text=key,
                background="#1c2129",
                foreground="#ffffff",
                width=10,
                font=("Arial", 10, "bold"),
                padx=5,
                pady=5
            )

            key_label.pack(
                side="left"
            )

            description_label = tk.Label(
                row,
                text=description,
                background="#0b0d10",
                foreground="#a0a5ad",
                width=28,
                anchor="w",
                font=("Arial", 10),
                padx=12
            )

            description_label.pack(
                side="left"
            )

        self.create_button(
            container,
            "BACK",
            self.show_menu,
            width=24
        )

    def start_game(self):
        self.clear_screen()

        self.simulation = Simulation(
            width=900,
            height=600,
            agent_count=3
        )

        self.create_header()

        self.arena = Arena(
            self.root,
            self.simulation
        )

        self.create_controls()

        self.update_loop()

    def create_header(self):
        header = tk.Frame(
            self.root,
            background="#0b0d10"
        )

        header.pack(
            fill="x",
            padx=20,
            pady=(15, 0)
        )

        title = tk.Label(
            header,
            text="AI ARENA",
            background="#0b0d10",
            foreground="#ffffff",
            font=("Arial", 22, "bold")
        )

        title.pack(
            side="left"
        )

        self.status_label = tk.Label(
            header,
            text="STOPPED",
            background="#0b0d10",
            foreground="#888888",
            font=("Arial", 10, "bold")
        )

        self.status_label.pack(
            side="right",
            pady=5
        )

    def create_controls(self):
        controls = tk.Frame(
            self.root,
            background="#0b0d10"
        )

        controls.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.start_button = tk.Button(
            controls,
            text="START",
            command=self.toggle_simulation,
            background="#1c2129",
            foreground="#ffffff",
            activebackground="#282f3a",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=8,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )

        self.start_button.pack(
            side="left"
        )

        reset_button = tk.Button(
            controls,
            text="RESET",
            command=self.reset_simulation,
            background="#1c2129",
            foreground="#ffffff",
            activebackground="#282f3a",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=8,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )

        reset_button.pack(
            side="left",
            padx=(10, 0)
        )

        menu_button = tk.Button(
            controls,
            text="MENU",
            command=self.show_menu,
            background="#1c2129",
            foreground="#ffffff",
            activebackground="#282f3a",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=8,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )

        menu_button.pack(
            side="left",
            padx=(10, 0)
        )

        self.tick_label = tk.Label(
            controls,
            text="Tick: 0",
            background="#0b0d10",
            foreground="#888888",
            font=("Arial", 10)
        )

        self.tick_label.pack(
            side="right"
        )

    def toggle_simulation(self):
        if self.simulation.running:
            self.simulation.stop()

            self.start_button.config(
                text="START"
            )

            self.status_label.config(
                text="STOPPED",
                foreground="#888888"
            )

        else:
            self.simulation.start()

            self.start_button.config(
                text="PAUSE"
            )

            self.status_label.config(
                text="RUNNING",
                foreground="#55cc88"
            )

    def reset_simulation(self):
        self.simulation.reset()

        self.start_button.config(
            text="START"
        )

        self.status_label.config(
            text="STOPPED",
            foreground="#888888"
        )

        self.update_display()

    def update_display(self):
        if self.arena is not None:
            self.arena.draw()

        if self.simulation is not None:
            self.tick_label.config(
                text=f"Tick: {self.simulation.world.tick}"
            )

    def update_loop(self):
        if self.arena is None or self.simulation is None:
            return

        self.simulation.update()
        self.update_display()

        self.root.after(
            30,
            self.update_loop
        )


def main():
    root = tk.Tk()

    app = AIArena(root)

    root.mainloop()


if __name__ == "__main__":
    main()