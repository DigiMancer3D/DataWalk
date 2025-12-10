# DataWalk: 3D Interactive File Explorer 🚀🌌

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/) [![Panda3D](https://img.shields.io/badge/Panda3D-1.10%2B-orange?logo=panda)](https://www.panda3d.org/) 

**Welcome to DataWalk**, Where your file system transforms into a breathtaking 3D metropolis! 🏙️✨ Imagine soaring through a digital skyline: directories rise as majestic **buildings** with glowing windows revealing file names, regular files sparkle as colorful **orbs** scattered like jewels, and hidden files twinkle as ethereal **stars** above the horizon. Built with Panda3D, this immersive explorer lets you *fly*, *walk* & *interact* with your data to *discover* the hidden architecture of your drives like never before.

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

1. **Prerequisites**:  
   - Python 3.8+  
   - Panda3D (rendering engine): `pip install panda3d`  

2. **Run It**:  
   ```bash
   git clone https://github.com/DigiMancer3D/DataWalk.git
   cd DataWalk
   python DataWalk_1.2.5.py
   ``` 
   - Config auto-saves.

3. **Troubleshooting**:  
   - Windows/Linux: Ensure Python in PATH.  
   - macOS: May need XQuartz for GUI.  
   - Beta quirks? Let us know!


TIPS for Installation (Linux [Kubuntu] based but may help others):

1. Make sure you're in the venv: ```source ~/vdm_env/bin/activate```
2. Install ALL the missing Python packages inside the venv:
   ```pip install --list--not--known--yet--```
3. Go to your script folder (with quotes because of spaces):
   ```cd "--location--not--shown--here--find--this--on--your--machine--"```
4. Run: ```python DataWalk_1.2.5.py```


TIPS for Killing (Linux [Kubuntu] based but may help others):

1. To find your kill: ```ps aux | grep python```
2. Kill top running: ```kill -9 --PID#--```
3. Kill run-away intances (PID keeps chaning but all stable PIDs of grep list must be killed first): ```pkill -f python```


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

Built with strange needs in mind (making cleaning up my drives more fun) by [DigiMancer3D](https://github.com/DigiMancer3D) for data wanderers everywhere.

**Fly high, explore deep. The data awaits!** 🦅📂

---

*Version 1.2.5 – Stable Beta | Last Updated: Dec 2025*

---
