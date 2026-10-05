# AI Arena

AI Arena is a real-time Python simulation where autonomous AI agents interact, compete, and survive in a dynamic world.

> **Current version:** **v0.5.5**

## Screenshots

![AI Arena screenshot 1](https://github.com/user-attachments/assets/9d6f8119-4c7f-432b-b82a-f275d8a01f9b)

![AI Arena screenshot 2](https://github.com/user-attachments/assets/2a68af42-729c-48cc-b461-79f05915f306)

![AI Arena screenshot 3](https://github.com/user-attachments/assets/bf140268-d389-42b2-b6f2-261873a94da6)

## Features

- Autonomous AI agents
- Real-time simulation
- Dynamic world
- Agent interactions
- Agent personalities and behaviours
- Health, energy and hunger systems
- Combat and targeting
- Agent statistics and information
- Adjustable simulation speed
- Visualisation controls
- Performance-focused systems
- Single-file Windows `.exe` release

## How It Works

AI Arena places autonomous agents inside a simulated world and allows them to make decisions based on their surroundings and individual characteristics.

Agents can:

- Search for and interact with other agents
- Identify enemies and teammates
- Choose targets
- Chase or flee from other agents
- Attack opponents
- Manage health and energy
- Change between different states and behaviours
- Develop statistics such as kills, score and damage dealt

Different agents can have different personalities, which affects how they behave inside the arena.

## Agent Customisation

One of the main parts of AI Arena is experimenting with the agent code.

Feel free to edit the code of the agents to improve them or change their behaviours.

You can change the decision-making systems, personalities, priorities and other parts of the agent logic, then run the simulation and see what happens.

## Controls

AI Arena includes an in-game **Keybindings** menu.

| Key | Action |
|---|---|
| `G` | Toggle grid |
| `L` | Toggle agent labels |
| `H` | Toggle health bars |
| `E` | Toggle energy bars |
| `T` | Toggle target lines |
| `V` | Toggle vision |
| `R` | Toggle resources |
| `O` | Toggle obstacles |
| `F` | Toggle attack effects |
| `S` | Toggle spawn points |
| `↑ / ↓` | Change simulation speed |
| `← / →` | Cycle selected agent |
| `ESC` | Clear selection |

## Download

The latest Windows executable is available from the [GitHub Releases](https://github.com/Swimminggit121/AI-arena/releases) page.

The current release provides a single `AI-Arena.exe` file, so Windows users do not need to install Python to run the released application.

## Running From Source

### Requirements

- Python 3.14
- Windows, macOS or Linux
- The packages listed in `requirements.txt`

### Installation

Clone the repository:

```bash
git clone https://github.com/Swimminggit121/AI-arena.git
cd AI-arena
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Run AI Arena:

```bash
python main.py
```

## Project Structure

| File | Purpose |
|---|---|
| `main.py` | Starts the application and manages the main menu and simulation interface |
| `arena.py` | Draws and manages the visual arena |
| `agent.py` | Contains agent behaviour and decision-making systems |
| `world.py` | Contains the simulated world |
| `simulation.py` | Controls the simulation and updates the agents |
| `requirements.txt` | Lists the Python dependencies |

## Development

AI Arena is actively being developed.

Current development focuses on:

- Improving agent behaviour
- Expanding simulation systems
- Improving performance
- Adding more ways for agents to interact
- Improving the user interface
- Adding more customisation options

## Building

Windows releases are built using **GitHub Actions** and **PyInstaller**.

The release workflow builds a single Windows executable from `main.py` and publishes it to GitHub Releases when a version tag is pushed.

## Releases

Each significant version of AI Arena can be released separately so previous versions remain available.

See the [Releases](https://github.com/Swimminggit121/AI-arena/releases) page for available versions.

## Known Issues

AI Arena is still under development. Larger simulations may require more processing power, and agent behaviour may change as the simulation systems continue to be developed.

## Contributing

You can experiment with the source code and create your own changes to the agent behaviour and simulation systems.

If you make an interesting improvement, feel free to share it with the project.

## Credits

Created by **Swimminggit121**.

## Repository

[View the AI Arena source code on GitHub](https://github.com/Swimminggit121/AI-arena)
