# DataWalk: 3D Interactive File Explorer 🚀🌌

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/) [![Panda3D](https://img.shields.io/badge/Panda3D-1.10%2B-orange?logo=panda)](https://www.panda3d.org/) [![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://opensource.org/licenses/GPL-3.0)

**Welcome to DataWalk** – where your file system transforms into a breathtaking 3D metropolis! 🏙️✨ Imagine soaring through a digital skyline: directories rise as majestic **buildings** with glowing windows revealing file names, regular files sparkle as colorful **orbs** scattered like jewels, and hidden files twinkle as ethereal **stars** above the horizon. Built with Panda3D (now featuring the default GUI look for a clean, native feel), this immersive explorer lets you *fly*, *walk* & *interact* with your data to *discover* the hidden architecture of your drives like never before.

This is the **public beta release (v1.2.5)**! We've squashed major bugs and stabilized the core mechanics, visualization, and interactions. It's ready for your feedback as we blueprint the next phase: deeper file ops, QoL polish, and even more cosmic features! 🌠

## 🌟 Key Features (What It Does Today)

DataWalk turns file navigation into an adventure. Here's what's powering the beta:

- **Immersive 3D Navigation** 🛩️  
  Fly or Walk freely in first-person mode: WASD for movement, mouse for look-around, Page Up/Down for altitude. Hexagonal layouts prevent overlap, creating organic city blocks. With a unique look down for a red carpet to click to go back when you are in a *building*.

- **Visual File System Cityscape** 🏛️  
  - **Directories as Buildings**: Towering structures where height curves based on approximate folder size. Windows (*) on facades show file counts and names.  
  - **Files as Glowing Orbs**: Colored spheres (hue from filename hash) sized by file; double click to open with your OS default app.  
  - **Hidden Files as Stars**: Dotfiles (e.g., `.gitignore`) & extensionless-files (e.g., `Readme`) appear as twinkling stars hovering above. *Toggle visibility within the settings menu.*  
  - **Special Handling**: Empty dirs get subtle markers; "files-as-dirs" (like zips or archives) render as buildings too.

- **Smart Interactions** 🖱️  
  - Left-click (or `E`) to enter directories or select files.  
  - Double Left-Click to launch the selected file externally.  
  - Mouse ray-casting highlights targets with HUD info (current path, name).  
  - History stack for seamless back-navigation via the red exit carpet.

- **Dynamic HUD & Labels** 📊  
  Real-time path display, target info, and help tips. Toggle building titles (`B`), window labels (`T`) for clutter-free transversing.

- **Configuration & Customization** ⚙️  
  Pause menu (right-click or `Mouse3`) unlocks sliders for FOV, movement speeds, building heights, cluster spacing, and more. Rebind keys, cycle screen modes (`U`: windowed → double-size → fullscreen). Saves to `DataWalk.udata` JSON.

- **Teleport & Bookmarks** ⚡  
  - **Index List** (`I`): Searchable roster of all loaded buildings, click to teleport to the front door.  
  - **Beacons** (`K` to mark/demark, `L` to list): Quick-jump to favorite dirs with add/remove buttons in the Beacons menu.

- **Performance & Polish** 🚀  
  Efficient loading for sub-paths under your chosen root (default: `/`). Mouse confinement, lighting/shadows, and low-poly geometry for smooth flight.

| Quick Controls Overview | |
|------------------------|-|
| **Movement** | WASD (forward/back/strafe), Page Up/Down (fly up/down) |
| **Interact** | Left-click / `E` (enter/select), `Space` / Double Left-Click (open file) |
| **Menus** | Right-click (pause), `I` (index), `L` (beacons) |
| **Toggles** | `B` (building titles), `T` (window titles), `N` (hidden stars), `U` (screen mode) |
| **Exit** | `Escape` (save & quit) |

*Pro Tip*: Start with a small root dir to test – the beta shines on organized folders like `~/Documents`!

## 🔮 Upcoming Upgrades (Roadmap Teasers)

We're not stopping at beta – here's the cosmic wishlist to level up DataWalk into a full-fledged data odyssey:

- **Belt/Inventory Clipboard System** 📦  
  A HUD "belt" for multi-select copy/cut/paste ops across world & zones. Drag files between buildings like a interdimensional courier!

- **Full File Showcasing** ⭐  
  Expand orb visibility to all zones/worlds (beyond current partial rendering). Keep hidden files as majestic stars, but make 'em searchable and spotlightable.

- **Hidden Folders as Tunnels** 🕳️  
  Reimagine concealed dirs (those starting with `.`, `!`, `$` or ending in `.*`, `.`, `*`; or folders with extensions like `folder.path`/`folder.app`) as mysterious **tunnels** burrowing through the cityscape – enter to explore shadowy sub-realms, contrasting the upright buildings.

- **System Integration** 🔗  
  Set DataWalk as your default folder explorer via the pause menu checkbox.

- **QoL & Explorer Enhancements** ✨  
  More file types for modern file explorer actions (e.g., media previews), VR mode hooks, and network directory discovery seen as clouds.

Got ideas? Fork, PR, or ping in issues! Your input shapes the skyline. 🌃

## 💻 Installation & Setup

### Prerequisites (All Platforms)
- **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/). Ensure it's added to your PATH during installation.
- **Panda3D**: The core rendering engine. Install via:
  ```
  pip install panda3d
  ```
  *Note: No other external dependencies – keeps it lightweight! Tkinter (for file dialogs) is included with standard Python installs.*

We recommend using a virtual environment (venv) for isolation:
```
python -m venv vdm_env
# On Linux/macOS:
source vdm_env/bin/activate
# On Windows:
vdm_env\Scripts\activate
```
Then install Panda3D inside the venv.

### Quick Start (All Platforms)
1. Clone the repo:
   ```
   git clone https://github.com/DigiMancer3D/DataWalk.git
   cd DataWalk
   ```
2. Run the app:
   ```
   python DataWalk_1.2.5.py
   ```
   - On first launch, select a root directory (e.g., your home folder or `~/Documents`).
   - Config auto-saves to `DataWalk.udata`; tweak settings in the pause menu.

### Platform-Specific Setup

#### Windows
- **Installation Tips**:
  - If paths have spaces, use quotes: `cd "C:\Path\To\DataWalk"`.
  - Ensure Python is in PATH (check via `python --version` in Command Prompt).
  - For GUI issues, install Visual C++ Redistributable from [Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe).
- **Creating Executable** (Standalone .exe):
  ```
  pip install pyinstaller
  pyinstaller --onefile DataWalk_1.2.5.py
  ```
  The .exe will be in the `dist` folder – run it directly, no Python needed!
- **Killing Stuck Processes**:
  - Open Task Manager (Ctrl+Shift+Esc), find `python.exe` or `DataWalk_1.2.5.exe`, and end task.
  - Or via Command Prompt: `taskkill /f /im python.exe` (kills all Python processes – use cautiously).

#### macOS
- **Installation Tips**:
  - Install via Homebrew for ease: `brew install python@3.12` (or use python.org installer).
  - For GUI rendering, install XQuartz: Download from [xquartz.org](https://www.xquartz.org/) and restart your Mac.
  - Paths with spaces: Use quotes in Terminal, e.g., `cd "/Users/YourName/Documents/DataWalk"`.
- **Creating Executable**:
  ```
  pip install pyinstaller
  pyinstaller --onefile --windowed DataWalk_1.2.5.py
  ```
  (Add `--windowed` to hide console.) Find the .app in `dist`.
- **Killing Stuck Processes**:
  - In Terminal: `ps aux | grep python` to find PID, then `kill -9 <PID>`.
  - Or: `pkill -f DataWalk_1.2.5.py` (kills matching processes).

#### Linux (e.g., Ubuntu/Kubuntu)
- **Installation Tips**:
  - Install Python if needed: `sudo apt update && sudo apt install python3.8 python3-pip python3-venv`.
  - Activate venv as shown in Prerequisites.
  - For paths with spaces: `cd "/path/to/DataWalk"`.
- **Creating Executable**:
  ```
  pip install pyinstaller
  pyinstaller --onefile DataWalk_1.2.5.py
  ```
  Executable in `dist` folder.
- **Killing Stuck Processes**:
  - Find PID: `ps aux | grep python`.
  - Kill specific: `kill -9 <PID>`.
  - Kill all matching: `pkill -f DataWalk_1.2.5.py` (kill stable PIDs first if instances are runaway).

### General Troubleshooting
- **Missing Packages**: If pip complains, run `pip install --upgrade pip` then reinstall Panda3D.
- **Permission Errors**: Use `sudo` sparingly; prefer venv.
- **Beta Quirks**: Check console output for errors. Report issues with OS/Python version.
- **Verbose Mode**: Future flag `--verbose` for debug logs.

## 📸 Screenshots & Demo

*(Beta visuals incoming, imagine customizable directory cities!)*  

- **City Overview**: A sprawling hex-grid of buildings, orbs dotting streets, stars winking overhead.  
- **Deep Dive**: Entering a building spawns a sub-city; red carpet for quick escapes.  
- **Pause Menu**: Sliders, toggles, and key rebinds at your fingertips.

*(Submit your flight screenshots for the gallery!)*

## 🤝 Contributing & Feedback

This beta's your playground – bug hunts, feature votes, or wild suggestions welcome!  
- Star/Fork the repo.  
- Open issues for bugs (include OS/Python version).  
- Join the [discussion](https://github.com/DigiMancer3D/DataWalk/discussions) for roadmap vibes.

DataWalk is licensed under the GNU General Public License v3.0 (GPL-3.0) – see the [LICENSE](LICENSE) file for details.

Built with strange needs in mind (making cleaning up my drives more fun) by [DigiMancer3D](https://github.com/DigiMancer3D) for data wanderers everywhere.

**Fly high, explore deep. The data awaits!** 🦅📂

---

*Version 1.2.5 – Stable Beta | Last Updated: December 2025*
