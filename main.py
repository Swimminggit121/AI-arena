import tkinter as tk

from simulation import Simulation
from arena import Arena


class AIArena:
    def __init__(self, root):
        self.root = root

        self.root.title("AI Arena")
        self.root.geometry("980x760")
        self.root.minsize(980, 760)
        self.root.configure(background="#0b0d10")

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

        title.pack(side="left")

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
            font=("Arial", 10, "bold")
        )

        self.start_button.pack(side="left")

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
            font=("Arial", 10, "bold")
        )

        reset_button.pack(
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
        self.arena.draw()

        self.tick_label.config(
            text=f"Tick: {self.simulation.world.tick}"
        )

    def update_loop(self):
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