# ⚔️ D&D Initiative Tracker

A lightweight desktop application for managing D&D 5e combat encounters. Built with Python and Tkinter — no external dependencies required.

---

## Features

- **Initiative order** — add combatants and sort them by initiative with one click
- **HP tracking** — manage current, maximum, and temporary HP with fast in-line controls
- **Armor Class** — visible at a glance on each combatant's card
- **Status conditions** — apply conditions with a round-based duration; they expire automatically as turns advance
- **Round counter** — tracks the current round and advances automatically
- **Combatant library** — save players and monsters for reuse across sessions, persisted locally in JSON
- **No install required** — pure Python standard library, runs anywhere Python is installed

---

## Requirements

- Python 3.11 or higher
- No external packages needed — Tkinter and JSON are included in the standard library

---

## Getting Started

Clone the repository:
```bash
git clone https://github.com/yourusername/dnd-initiative-tracker.git
cd dnd-initiative-tracker
```

Run the application:
```bash
python ui.py
```

---

## How to Use

1. Click **+ Aggiungi** to add a combatant (player, monster, or NPC)
2. Click **↕ Ordina Iniziativa** to sort the combat order
3. Click **Turno Successivo** (or press `Space`) to advance turns — conditions tick down automatically
4. Select any combatant to edit their stats, apply damage, healing, or conditions in the right panel
5. Save any combatant to the **Libreria** (left panel) to reload them in future sessions

---

## Project Structure

```
dnd-initiative-tracker/
├── ui.py          # Tkinter interface
├── tracker.py     # Core logic — Combattente and Combattimento classes
├── libreria.json  # Persistent combatant library (auto-generated)
└── README.md
```

---

## Screenshots

*Coming soon.*

---

## License

MIT License — see [LICENSE](LICENSE) for details.
