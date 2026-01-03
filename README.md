## Tumba-Yola
### Index
- [Tumba-Yola](#tumba-yola)
- [What this project is](#what-this-project-is)
- [Download & Play](#download--play)
- [How to Play](#how-to-play)
- [Visual + audio feedback](#visual--audio-feedback)
- [Architecture](#architecture)
- [Room management](#room-management)
- [Network protocol](#network-protocol)
- [Running from source](#running-from-source)
- [Credits](#credits)
  
Multiplayer tropical game inspired by Battleship built with Python and Pygame, using a dedicated client/server architecture. The server is hosted on Oracle Cloud, so players can download the client and play immediately with no local server setup needed.
> The word: **Yola** refers to a small boat (a slang/common term in some Spanish-speaking coastal contexts).

> The word: **Tumba** refers to “knock down” or “take down”in this game context, sink the enemy ship.

![Vídeo sin título ‐ Hecho con Clipchamp (2)](https://github.com/user-attachments/assets/1cb993be-c3b8-48c5-9ebe-76c950c5c5da)

### What this project is
- **Genre**: Turn-based, 1v1 game
- **Tech**: Python, sockets, threading, Pygame (UI/audio)
- **Networking**: Text protocol over TCP (newline-delimited UTF‑8)
- **Hosting**: Always-on server (Oracle Cloud)

### Download & Play
1. Open this repository’s **Releases** page.
2. Download `client.zip` from the **latest release**.
3. Extract the zip and run `client.exe`.

The client is preconfigured to connect to the always-on server by default:
- **Server IP**: `150.136.155.41`
- **Port**: `55555`

### How to Play
- **Boards**: Each player has a 10×10 grid. 
- **Ships**: Each match spawns 4 ships, placed randomly every time you play:
  - Ship-1 length: **3**
  - Ship-2 length: **4**
  - Ship-3 length: **5**
  - Ship-4 length: **6**
- **Turns**: Players alternate turns. On your turn, you select a cell on the opponent grid to attack.
- **Hit / Miss**:
  - A **hit** means your attack landed on an enemy ship cell.
  - A **miss** means the attacked cell was water.
- **Win condition**: You win after hitting all 18 enemy ship cells.

https://github.com/user-attachments/assets/4e26e561-39f5-4f58-9006-cab9d79cc75f

<img width="750" height="1688" alt="Captura de pantalla 2026-01-03 003107" src="https://github.com/user-attachments/assets/5b987d00-96b9-4be6-a38a-13b3fd883902" />

### Visual + audio feedback
- **Interactive sprites**: Ships render with sprite segments, and change appearance when damaged.
- **Shot markers**:
  - **Red inflatable** marker = Hit
  - **Orange inflatable** marker = Miss
- **Sound effects**: Hover, hit, and miss SFX.
- **Background music**: In-game music playback.

<img width="750" height="1617" alt="Captura de pantalla 2026-01-03 003215" src="https://github.com/user-attachments/assets/30ec2f1d-9fef-4e8e-ad06-d71103438f6d" />


### Architecture 
- **`client.py`**: Pygame client (UI rendering, input handling, audio, non-blocking network polling).
- **`server.py`**: TCP server handling connections, matchmaking, and game updates.
- **`Utilities/`**: Shared gameplay and server-side utilities (game state, room management, sprite processing, etc.).

### Room management
The server supports **multiple simultaneous matches** by grouping players into independent rooms:
- **Matchmaking**: FIFO queue of waiting rooms.
- **Isolation**: Each room has its own game state and its own lock.
- **Lifecycle**: When the 2 players leave, the room is cleaned up.

### Network protocol

All messages are **newline-delimited UTF-8 text**.

**Format:** `<type>|<payload>\n`

| Direction | Type | Payload format | Meaning / when sent |
|----------|------|----------------|----------------------|
| `Server → Client` | `ack` | `You are player: <0/1>` | Sent immediately on connection; tells client its `player_id`. |
| `Server → Client` | `room` | `<room_id>` | Sent after `ack`; tells which room the client joined. |
| `Server → Client` | `status` | `<WAITING\|OK>` | `WAITING` = waiting for opponent; `OK` = room is full. |
| `Server → Client` | `fleet` | `<json>` | Ship placement for this player’s board. |
| `Server → Client` | `matrix` | `<collapsed_matrix>` | Board update. Rows separated by `;`, cells by `,`. Values: `0` = empty, `1` = ship, `2` = miss, `3` = hit. |
| `Server → Client` | `turn` | `<0/1>` | Announces whose turn it is. |
| `Server → Client` | `update` | `<hit\|miss>\|<r>,<c>` | Sent to attacker after a valid attack; reports outcome and coordinates. |
| `Server → Client` | `win` | `You won` | Sent to the winner when all opponent ship cells are destroyed. |
| `Server → Client` | `error` | `<message>` | Sent on invalid input/actions (bad format, invalid coordinates, not your turn, etc.). |
| `Client → Server` | `attack` | `<r>,<c>` | Attack a cell on opponent board. |

### Running from source
If you want to run the client from Python instead of the packaged `.exe`:

```bash
pip install -r requirements.txt
python client.py
```

To run a server locally (for testing), use:

```bash
python server.py
```



### Credits
- **Music**: AlkaKrab (`https://alkakrab.itch.io/`)
- **Font**: Google Fonts — *Jersey 10* (`https://fonts.google.com/share?selection.family=Jersey+10`)
