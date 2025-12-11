# DataWalk_1.2.3.py — All theme options removed, back to Panda3D default GUI look
# Run: python DataWalk_1.2.3.py

# To make executable:
# Install pyinstaller: pip install pyinstaller
# Run: pyinstaller --onefile DataWalk_1.2.3.py
# The exe will be in dist folder.

# Quick tip for installation issues:
# 1. Make sure you're in the venv (source ~/vdm_env/bin/activate)
# 2. Install ALL the missing Python packages inside the venv:
#    pip install ..this list needs to be corrected for the needed dependencies to help users auto-fix their install..
# 3. Go to your script folder (with quotes because of spaces):
#    cd "--your--file--location"
# 4. Run: python DataWalk_1.2.3.py
# To find your kill: ps aux | grep python
# Kill top running: kill -9 PID#
# Kill run-away intances (PID keeps chaning but all stable PIDs of grep list must be killed first): pkill -f DataWalk_1.2.3.py

import sys
import os
import math
import colorsys
import json
import time
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectDialog, YesNoDialog
from panda3d.core import (
    AmbientLight, DirectionalLight, Vec3, Vec4, TextNode,
    TransparencyAttrib, CardMaker, GeomVertexFormat, GeomVertexData,
    Geom, GeomTriangles, GeomNode, GeomVertexWriter, LineSegs,
    CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode,
    CollisionSphere, BitMask32, Lens, WindowProperties
)
from direct.task import Task
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DirectEntry, DirectSlider, DirectScrolledFrame, DirectCheckButton
from direct.gui import DirectGuiGlobals as DGG

if platform.system() == 'Windows':
    import winreg

class DataWalk(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0.01, 0.01, 0.04, 1)

        # Confine mouse to window for better locking
        props = WindowProperties()
        props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(props)

        self.config_file = "DataWalk.udata"
        self.config_data = {}
        self.root_dir = "/"
        self.last_location = None
        self.last_camera_pos = None
        self.last_camera_hpr = None
        self.last_history = []
        self.is_default = False
        self.original_default = None
        self.beacons = []
        self.selected_beacon = None
        self.last_beacon_click = 0
        self.beacon_frame = None
        self.load_dialog = None
        self.save_dialog = None
        self.controls_enabled = True
        self.in_menu = False
        self.click_task = None

        self.current_path = "/"
        self.history = []
        self.move_speed = 55
        self.fly_step = 45
        self.max_height = 130
        self.spacing = 95
        self.fov = 60
        self.cam.node().getLens().setFov(self.fov)
        self.building_color = (0.15, 0.35, 0.95, 0.88)
        self.selected_node = None
        self.previous_selected = None
        self.pause_frame = None
        self.index_frame = None
        self.rebind_mode = False
        self.keys = {"forward": 0, "backward": 0, "left": 0, "right": 0}
        self.buildings = {}
        self.file_orbs = {}
        self.entries = []
        self.window_labels = []
        self.building_labels = []
        self.show_window_titles = False
        self.show_building_titles = True
        self.label_at_top = True
        self.screen_mode = 0
        self.movement_offset = 0
        self.display_width = self.pipe.getDisplayWidth()
        self.display_height = self.pipe.getDisplayHeight()
        self.default_win_size = (self.win.getXSize(), self.win.getYSize())
        self.screen_modes = [
            self.default_win_size,
            (self.default_win_size[0] * 2, self.default_win_size[1] * 2),
            (self.display_width, self.display_height)
        ]
        self.current_sort_mode = 0
        self.last_index_click = {}
        self.index_click_task = {}

        self.key_bindings = {
            "forward": ["w"],
            "backward": ["s"],
            "left": ["a"],
            "right": ["d"],
            "ascend": ["page_up"],
            "descend": ["page_down"],
            "interact": ["mouse1", "e"],
            "pause": ["mouse3"],
            "index": ["i"],
            "wt_toggle": ["t"],
            "bt_toggle": ["b"],
            "screen_toggle": ["u"],
            "beacon_toggle": ["k"],
            "beacon_list": ["l"],
            "open": ["space"],
            "hidden_toggle": ["n"]
        }

        self.sizes = {}

        self.load_config()

        if len(sys.argv) > 1:
            self.root_dir = os.path.abspath(sys.argv[1])
            self.last_location = self.root_dir

        self.disableMouse()
        self.camera.setPos(0, -130, 22)
        self.camera.lookAt(0, 0, 12)

        # Collision setup
        self.cTrav = CollisionTraverser()
        self.handler = CollisionHandlerQueue()
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.camera.attachNewNode(self.picker_node)
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.picker_node.setFromCollideMask(BitMask32.bit(0))
        self.picker_node.setIntoCollideMask(BitMask32.allOff())
        self.cTrav.addCollider(self.picker_np, self.handler)

        # Lighting
        alight = AmbientLight('alight')
        alight.setColor(Vec4(0.45, 0.5, 0.7, 1))
        self.render.setLight(self.render.attachNewNode(alight))

        dlight = DirectionalLight('dlight')
        dlight.setColor(Vec4(1.0, 0.95, 0.9, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(30, -60, 0)
        self.render.setLight(dlnp)

        # Bind keys
        self.bind_keys()

        # HUD
        self.title_text = TextNode('title')
        self.title_text.setText("DataWalk (Red Carpet => Back | LClick => [E]nter | RClick => [P]ause | [I]ndex | Window [T]itles | [B]uilding Titles | [U] Screen Toggle | [K] Beacon | [L]ist | [Space] Open)")
        self.title_text.setAlign(TextNode.ACenter)
        self.title_text.setWordwrap(40.0)
        self.title_np = aspect2d.attachNewNode(self.title_text)
        self.title_np.setScale(0.07)
        self.title_np.setPos(0, 0, 0.92)
        self.title_text.setTextColor(0, 1, 1, 1)

        self.path_text = TextNode('path')
        self.path_text.setText("Location: /")
        self.path_text.setAlign(TextNode.ALeft)
        self.path_text.setWordwrap(30.0)
        self.path_np = aspect2d.attachNewNode(self.path_text)
        self.path_np.setScale(0.05)
        self.path_np.setPos(-1.6, 0, -0.9)
        self.path_text.setTextColor(0.7, 1, 1, 1)

        self.target_text = TextNode('target')
        self.target_text.setText("")
        self.target_text.setAlign(TextNode.ARight)
        self.target_text.setWordwrap(12.0)
        self.target_np = aspect2d.attachNewNode(self.target_text)
        self.target_np.setScale(0.05)
        self.target_np.setPos(1.6, 0, -0.91)
        self.target_text.setTextColor(1, 0.7, 1, 1)

        self.accept("aspect_ratio_changed", self.update_hud_positions)
        self.update_hud_positions()

        self.set_path(self.root_dir)
        self.taskMgr.add(self.update_camera, "camera_task")
        self.taskMgr.doMethodLater(0.1, self.ask_load_last, 'ask_load')

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config_data = json.load(f)
        self.root_dir = self.config_data.get('root_dir', '/')
        self.move_speed = self.config_data.get('move_speed', 55)
        self.fly_step = self.config_data.get('fly_step', 45)
        self.max_height = self.config_data.get('max_height', 130)
        self.spacing = self.config_data.get('spacing', 95)
        self.fov = self.config_data.get('fov', 60)
        self.cam.node().getLens().setFov(self.fov)
        self.show_window_titles = self.config_data.get('show_window_titles', False)
        self.show_building_titles = self.config_data.get('show_building_titles', True)
        self.show_hidden = self.config_data.get('show_hidden', False)
        self.screen_mode = self.config_data.get('screen_mode', 0)
        self.movement_offset = self.config_data.get('movement_offset', 0)
        self.key_bindings = self.config_data.get('key_bindings', self.key_bindings)
        self.last_location = self.config_data.get('last_location', None)
        self.last_camera_pos = self.config_data.get('last_camera_pos', None)
        self.last_camera_hpr = self.config_data.get('last_camera_hpr', None)
        self.last_history = [(h[0], Vec3(*h[1]), Vec3(*h[2])) for h in self.config_data.get('last_history', []) if len(h) == 3]
        self.is_default = self.config_data.get('is_default', False)
        self.original_default = self.config_data.get('original_default', None)
        self.beacons = self.config_data.get('beacons', [])
        self.current_sort_mode = self.config_data.get('current_sort_mode', 0)
        self.save_config()

    def get_app_command(self):
        if getattr(sys, 'frozen', False):
            exe = sys.executable
            args = '"%1"'
        else:
            exe = sys.executable
            script = os.path.abspath(__file__)
            args = f'"{script}" "%1"'
        return f'"{exe}" {args}'

    def toggle_default_explorer(self, val):
        self.is_default = val
        system = platform.system()
        if system == 'Windows':
            try:
                key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'Folder\shell\open\command', 0, winreg.KEY_ALL_ACCESS)
                if val:
                    if self.original_default is None:
                        orig, _ = winreg.QueryValueEx(key, None)
                        self.original_default = orig
                    winreg.SetValueEx(key, None, 0, winreg.REG_SZ, self.get_app_command())
                else:
                    if self.original_default:
                        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, self.original_default)
                winreg.CloseKey(key)
            except Exception as e:
                print("Failed to set default:", e)
        elif system == 'Linux':
            try:
                desktop_file = os.path.expanduser('~/.local/share/applications/datawalk.desktop')
                if val:
                    if self.original_default is None:
                        proc = subprocess.Popen(['xdg-mime', 'query', 'default', 'inode/directory'], stdout=subprocess.PIPE)
                        self.original_default = proc.communicate()[0].decode().strip()
                    with open(desktop_file, 'w') as f:
                        f.write('[Desktop Entry]\n')
                        f.write('Type=Application\n')
                        f.write('Name=DataWalk\n')
                        f.write(f'Exec=python {os.path.abspath(__file__)} %U\n')
                        f.write('MimeType=inode/directory;\n')
                    subprocess.call(['xdg-mime', 'default', 'datawalk.desktop', 'inode/directory'])
                else:
                    if self.original_default:
                        subprocess.call(['xdg-mime', 'default', self.original_default, 'inode/directory'])
                    if os.path.exists(desktop_file):
                        os.remove(desktop_file)
            except Exception as e:
                print("Failed to set default:", e)
        elif system == 'Darwin':
            print("Setting default file explorer not supported on Mac.")
        self.save_config()

    def save_config(self):
        self.config_data['root_dir'] = self.root_dir
        self.config_data['move_speed'] = self.move_speed
        self.config_data['fly_step'] = self.fly_step
        self.config_data['max_height'] = self.max_height
        self.config_data['spacing'] = self.spacing
        self.config_data['fov'] = self.fov
        self.config_data['show_window_titles'] = self.show_window_titles
        self.config_data['show_building_titles'] = self.show_building_titles
        self.config_data['show_hidden'] = self.show_hidden
        self.config_data['screen_mode'] = self.screen_mode
        self.config_data['movement_offset'] = self.movement_offset
        self.config_data['key_bindings'] = self.key_bindings
        self.config_data['last_location'] = self.last_location
        self.config_data['last_camera_pos'] = list(self.camera.getPos()) if self.last_camera_pos is None else self.last_camera_pos
        self.config_data['last_camera_hpr'] = list(self.camera.getHpr()) if self.last_camera_hpr is None else self.last_camera_hpr
        self.config_data['last_history'] = [(p, list(pos), list(hpr)) for p, pos, hpr in self.history]
        self.config_data['is_default'] = self.is_default
        self.config_data['original_default'] = self.original_default
        self.config_data['beacons'] = self.beacons
        self.config_data['current_sort_mode'] = self.current_sort_mode
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f, indent=4)

    def set_root_dir(self):
        root = tk.Tk()
        root.withdraw()
        dir_path = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if dir_path:
            new_root = os.path.abspath(dir_path)
            if new_root != self.root_dir:
                self.root_dir = new_root
                self.save_config()
                # Reset to new root if current not under it
                if not self.current_path.startswith(self.root_dir):
                    self.set_path(self.root_dir)

    def ask_load_last(self, task):
        if self.last_location:
            self.show_load_dialog()
        return Task.done

    def show_load_dialog(self):
        self.in_menu = True
        base.enableMouse()
        self.load_dialog = DirectDialog(dialogName="loadDialog", text=f"Load last location?\n{self.last_location}", buttonTextList=['Yes', 'No'], buttonValueList=[1, 0], command=self.load_dialog_callback)

    def load_dialog_callback(self, val):
        if self.load_dialog:
            self.load_dialog.cleanup()
            self.load_dialog = None
        if val == 1:
            self.history = self.last_history
            self.set_path(self.last_location)
            if self.last_camera_pos:
                self.camera.setPos(Vec3(*self.last_camera_pos))
            if self.last_camera_hpr:
                self.camera.setHpr(Vec3(*self.last_camera_hpr))
        self.in_menu = False
        base.disableMouse()

    def userExit(self):
        self.last_camera_pos = list(self.camera.getPos())
        self.last_camera_hpr = list(self.camera.getHpr())
        self.show_save_dialog()

    def show_save_dialog(self):
        self.in_menu = True
        base.enableMouse()
        self.save_dialog = DirectDialog(dialogName="saveDialog", text="Save last location?", buttonTextList=['Yes', 'No'], buttonValueList=[1, 0], command=self.save_dialog_callback)

    def save_dialog_callback(self, val):
        if self.save_dialog:
            self.save_dialog.cleanup()
            self.save_dialog = None
        if val == 1:
            self.last_location = self.current_path
        else:
            self.last_location = None
            self.last_camera_pos = None
            self.last_camera_hpr = None
        self.save_config()
        self.in_menu = False
        base.disableMouse()
        ShowBase.userExit(self)

    def update_hud_positions(self):
        aspect = self.getAspectRatio()
        self.path_np.setX(-aspect + 0.1)
        self.path_np.setZ(-0.95)
        self.target_np.setX(aspect - 0.1)
        self.target_np.setZ(-0.91)
        self.path_text.setWordwrap((2 * aspect - 0.2) / 0.05)
        self.target_text.setWordwrap((aspect - 0.2) / 0.05)
        self.title_text.setWordwrap((2 * aspect) / 0.07)

    def bind_keys(self):
        self.ignoreAll()
        for action, keys in self.key_bindings.items():
            for key in keys:
                if key:
                    if action in ["forward", "backward", "left", "right"]:
                        self.accept(key, self.set_key, [action, 1])
                        self.accept(key + "-up", self.set_key, [action, 0])
                    elif action in ["ascend", "descend"]:
                        self.accept(key, getattr(self, action))
                    elif action == "interact":
                        if key == "mouse1":
                            self.accept(key, self.handle_mouse_click)
                        else:
                            self.accept(key, self.interact)
                    elif action == "pause":
                        self.accept(key, self.toggle_pause)
                    elif action == "index":
                        self.accept(key.upper(), self.toggle_index)
                        self.accept(key.lower(), self.toggle_index)
                    elif action == "wt_toggle":
                        self.accept(key.upper(), self.toggle_window_titles)
                        self.accept(key.lower(), self.toggle_window_titles)
                    elif action == "bt_toggle":
                        self.accept(key.upper(), self.toggle_building_titles)
                        self.accept(key.lower(), self.toggle_building_titles)
                    elif action == "screen_toggle":
                        self.accept(key.upper(), self.toggle_screen)
                        self.accept(key.lower(), self.toggle_screen)
                    elif action == "beacon_toggle":
                        self.accept(key.upper(), self.toggle_beacon)
                        self.accept(key.lower(), self.toggle_beacon)
                    elif action == "beacon_list":
                        self.accept(key.upper(), self.toggle_beacon_list)
                        self.accept(key.lower(), self.toggle_beacon_list)
                    elif action == "open":
                        self.accept(key, self.open_selected)
                    elif action == "hidden_toggle":
                        self.accept(key.upper(), self.toggle_hidden_stars)
                        self.accept(key.lower(), self.toggle_hidden_stars)
        self.accept("escape", self.userExit)

    def set_key(self, key, value):
        self.keys[key] = value

    def ascend(self):
        self.camera.setZ(self.camera.getZ() + self.fly_step)

    def descend(self):
        self.camera.setZ(max(15, self.camera.getZ() - self.fly_step))

    def handle_mouse_click(self):
        if not self.selected_node or self.in_menu:
            return
        if self.click_task:
            self.taskMgr.remove(self.click_task)
            self.click_task = None
            self.open_selected()
        else:
            self.click_task = self.taskMgr.doMethodLater(0.3, self.perform_single_interact, 'single_interact')

    def perform_single_interact(self, task):
        self.click_task = None
        if self.selected_node:
            self.interact()
        return Task.done

    def interact(self):
        if not self.selected_node:
            return
        typ = self.selected_node.getPythonTag("type")
        path = self.selected_node.getPythonTag("full_path") if typ in ["building", "file_orb", "star_dir", "star"] else None
        if typ == "exit_ground" and self.history:
            item = self.history.pop()
            self.current_path = item[0]
            self.load_path(self.current_path)
            self.camera.setPos(item[1])
            self.camera.setHpr(item[2])
        elif (typ == "building" or typ == "star_dir") and os.path.isdir(path):
            self.history.append((self.current_path, self.camera.getPos(), self.camera.getHpr()))
            self.current_path = path
            self.load_path(path)

    def open_selected(self):
        if not self.selected_node:
            return
        typ = self.selected_node.getPythonTag("type")
        if typ not in ["building", "file_orb", "star_dir", "star"]:
            return
        path = self.selected_node.getPythonTag("full_path")
        if os.path.isdir(path):
            self.interact()
            self.toggle_beacon()
        else:
            try:
                if platform.system() == 'Windows':
                    os.startfile(path)
                elif platform.system() == 'Linux':
                    subprocess.call(['xdg-open', path])
                elif platform.system() == 'Darwin':
                    subprocess.call(['open', path])
            except Exception as e:
                print("Failed to open:", e)

    def toggle_pause(self):
        if self.pause_frame:
            self.resume_pause()
        else:
            self.pause_game()

    def pause_game(self):
        self.in_menu = True
        base.enableMouse()
        self.pause_frame = DirectFrame(frameSize=(-1.3, 1.3, -0.9, 0.9), pos=(0, 0, 0))
        self.pause_frame.bind(DGG.B1PRESS, self.start_drag, ['pause'])
        self.pause_frame.bind(DGG.B1RELEASE, self.stop_drag, ['pause'])

        DirectButton(parent=self.pause_frame, text="Exit Game", command=self.userExit, pos=(0, 0, 0.8), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.pause_frame, text="Return to Explorer", command=self.resume_pause, pos=(0, 0, 0.7), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.pause_frame, text="Set Home Directory", command=self.set_root_dir, pos=(0, 0, 0.6), scale=0.1, relief=DGG.RAISED)

        DirectLabel(parent=self.pause_frame, text="Set as Default Explorer:", pos=(-0.8, 0, 0.5), scale=0.07, text_align=TextNode.ALeft)
        self.default_cb = DirectCheckButton(parent=self.pause_frame, scale=0.07, pos=(0.2, 0, 0.5), indicatorValue=self.is_default, command=self.toggle_default_explorer)

        self.scrolled_frame = DirectScrolledFrame(parent=self.pause_frame,
            canvasSize=(-1.2, 1.2, -3, 0),
            frameSize=(-1.2, 1.2, -0.7, 0.7),
            pos=(0, 0, 0),
            scrollBarWidth=0.05)
        canvas = self.scrolled_frame.getCanvas()

        y_pos = -0.2
        # FOV slider
        DirectLabel(parent=canvas, text="Field of View:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.fov_slider = DirectSlider(parent=canvas, range=(30, 120), value=self.fov, pos=(0.2, 0, y_pos), scale=0.8, command=self.update_fov)
        y_pos -= 0.15

        # Move speed
        DirectLabel(parent=canvas, text="Move Speed:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.speed_slider = DirectSlider(parent=canvas, range=(20, 100), value=self.move_speed, pos=(0.2, 0, y_pos), scale=0.8, command=self.update_speed)
        y_pos -= 0.15

        # Fly step
        DirectLabel(parent=canvas, text="Fly Distance:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.fly_slider = DirectSlider(parent=canvas, range=(20, 100), value=self.fly_step, pos=(0.2, 0, y_pos), scale=0.8, command=self.update_fly_step)
        y_pos -= 0.15

        # Max height
        DirectLabel(parent=canvas, text="Max Building Height:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.height_slider = DirectSlider(parent=canvas, range=(50, 200), value=self.max_height, pos=(0.2, 0, y_pos), scale=0.8, command=self.update_max_height)
        y_pos -= 0.15

        # Spacing
        DirectLabel(parent=canvas, text="Cluster Spacing:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.spacing_slider = DirectSlider(parent=canvas, range=(50, 150), value=self.spacing, pos=(0.2, 0, y_pos), scale=0.8, command=self.update_spacing)
        y_pos -= 0.15

        # Toggles
        DirectLabel(parent=canvas, text="Show Window Titles:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.window_titles_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_window_titles, command=self.set_window_titles)
        y_pos -= 0.15

        DirectLabel(parent=canvas, text="Show Building Titles:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.building_titles_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_building_titles, command=self.set_building_titles)
        y_pos -= 0.15

        DirectLabel(parent=canvas, text="Hidden Stars:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.hidden_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_hidden, command=self.set_hidden_stars)
        y_pos -= 0.15

        # Screen size
        DirectLabel(parent=canvas, text="Screen Size:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.screen_slider = DirectSlider(parent=canvas, range=(0, 2), value=self.screen_mode, pageSize=1, pos=(0.2, 0, y_pos), scale=0.8, command=self.update_screen_mode)
        y_pos -= 0.15

        # Movement offset
        DirectLabel(parent=canvas, text="Movement Offset:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        DirectButton(parent=canvas, text="+", command=self.increase_offset, pos=(0.2, 0, y_pos), scale=0.07, relief=DGG.RAISED)
        DirectButton(parent=canvas, text="Default Offset", command=self.reset_offset, pos=(0.4, 0, y_pos), scale=0.07, relief=DGG.RAISED)
        DirectButton(parent=canvas, text="-", command=self.decrease_offset, pos=(0.8, 0, y_pos), scale=0.07, relief=DGG.RAISED)
        self.offset_label = DirectLabel(parent=canvas, text=str(self.movement_offset), pos=(1.0, 0, y_pos), scale=0.07)
        y_pos -= 0.15

        # Key bindings
        actions = list(self.key_bindings.keys())
        for i, action in enumerate(actions):
            DirectLabel(parent=canvas, text=f"{action.capitalize()} Primary:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
            primary = self.key_bindings[action][0] if len(self.key_bindings[action]) > 0 else ""
            DirectEntry(parent=canvas, initialText=primary, pos=(0.2, 0, y_pos), scale=0.07,
                        command=lambda text, a=action, slot=0: self.update_binding(a, slot, text))
            y_pos -= 0.1
            DirectLabel(parent=canvas, text=f"{action.capitalize()} Secondary:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
            secondary = self.key_bindings[action][1] if len(self.key_bindings[action]) > 1 else ""
            DirectEntry(parent=canvas, initialText=secondary, pos=(0.2, 0, y_pos), scale=0.07,
                        command=lambda text, a=action, slot=1: self.update_binding(a, slot, text))
            y_pos -= 0.15

        self.scrolled_frame['canvasSize'] = (-1.2, 1.2, y_pos - 0.2, 0)

    def resume_pause(self):
        self.in_menu = False
        base.disableMouse()
        self.pause_frame.destroy()
        self.pause_frame = None

    def set_window_titles(self, val):
        self.show_window_titles = val
        self.update_labels_visibility()
        self.save_config()

    def set_building_titles(self, val):
        self.show_building_titles = val
        self.update_labels_visibility()
        self.save_config()

    def set_hidden_stars(self, val):
        self.show_hidden = val
        self.save_config()
        self.load_path(self.current_path)

    def toggle_hidden_stars(self):
        self.show_hidden = not self.show_hidden
        if self.pause_frame:
            self.hidden_cb['indicatorValue'] = self.show_hidden
            self.hidden_cb.setIndicatorValue()
        self.save_config()
        self.load_path(self.current_path)

    def toggle_window_titles(self):
        self.show_window_titles = not self.show_window_titles
        self.update_labels_visibility()
        self.save_config()

    def toggle_building_titles(self):
        self.show_building_titles = not self.show_building_titles
        self.update_labels_visibility()
        self.save_config()

    def update_labels_visibility(self):
        for label in self.window_labels:
            label.show() if self.show_window_titles else label.hide()
        for label in self.building_labels:
            label.show() if self.show_building_titles else label.hide()

    def toggle_index(self):
        if self.index_frame:
            self.resume_index()
        else:
            self.show_index()

    def show_index(self):
        self.in_menu = True
        base.enableMouse()
        self.index_frame = DirectFrame(frameSize=(-1.3, 1.3, -0.9, 0.9), pos=(0, 0, 0))
        self.index_frame.bind(DGG.B1PRESS, self.start_drag, ['index'])
        self.index_frame.bind(DGG.B1RELEASE, self.stop_drag, ['index'])

        DirectButton(parent=self.index_frame, text="Return to Explorer", command=self.resume_index, pos=(0, 0, 0.8), scale=0.1, relief=DGG.RAISED)

        # Footer for sorting buttons
        footer = DirectFrame(parent=self.index_frame, frameSize=(-1.2, 1.2, -0.15, 0), pos=(0, 0, -0.75), frameColor=(0, 0, 0, 0.5))
        button_texts = ['Name', 'Date Modified', 'Age', 'Size', 'Weight', 'Eman']
        for i, text in enumerate(button_texts):
            x_pos = -1.05 + i * 0.35
            DirectButton(parent=footer, text=text, scale=0.05, pos=(x_pos, 0, 0),
                         command=self.set_sort_mode, extraArgs=[i], relief=DGG.RAISED)

        self.scrolled_frame = DirectScrolledFrame(parent=self.index_frame,
            canvasSize=(-1.2, 1.2, -len(self.buildings)*0.1 - 0.2, 0),
            frameSize=(-1.2, 1.2, -0.7, 0.7),
            pos=(0, 0, 0),
            scrollBarWidth=0.05)

        self.last_index_click = {}
        self.index_click_task = {}
        self.refresh_index()

    def refresh_index(self):
        if not self.index_frame:
            return
        canvas = self.scrolled_frame.getCanvas()
        for child in canvas.getChildren():
            child.removeNode()

        dir_entries = [e for e in self.entries if e['type'] == 'dir']
        y_pos = -0.1
        for entry in dir_entries:
            name = entry['name']
            btn = DirectButton(parent=canvas, text=name, command=self.handle_index_click, extraArgs=[name],
                               pos=(0, 0, y_pos), scale=0.07, frameColor=(0,0,0,0))
            y_pos -= 0.1

        self.scrolled_frame['canvasSize'] = (-1.2, 1.2, y_pos - 0.1, 0)

    def set_sort_mode(self, mode):
        self.current_sort_mode = mode
        self.apply_sort()
        self.refresh_index()
        self.save_config()

    def apply_sort(self):
        if not self.entries:
            return
        mode = self.current_sort_mode
        if mode in [3, 4]:
            for entry in self.entries:
                if entry['size'] == 0:
                    entry['size'] = self.get_size(entry['full_path'])
        if mode == 0:  # Name A first
            self.entries.sort(key=lambda e: e['name'].lower(), reverse=False)
        elif mode == 1:  # Date Modified newest first
            self.entries.sort(key=lambda e: e['mod_time'], reverse=True)
        elif mode == 2:  # Age eldest first
            self.entries.sort(key=lambda e: e['mod_time'], reverse=False)
        elif mode == 3:  # Size smallest first
            self.entries.sort(key=lambda e: e['size'], reverse=False)
        elif mode == 4:  # Weight largest % first
            total_size = sum(e['size'] for e in self.entries)
            self.entries.sort(key=lambda e: (e['size'] / total_size if total_size > 0 else 0), reverse=True)
        elif mode == 5:  # Eman name Z first
            self.entries.sort(key=lambda e: e['name'].lower(), reverse=True)

        # Re-position nodes
        positions = self.hex_positions(len(self.entries), spacing=self.spacing)
        for i, entry in enumerate(self.entries):
            x, y = positions[i]
            z = 0 if entry['type'] == 'dir' else 20
            entry['node'].setPos(x, y, z)

    def handle_index_click(self, name):
        now = globalClock.getRealTime()
        if name in self.last_index_click and now - self.last_index_click[name] < 0.3:
            if name in self.index_click_task:
                self.taskMgr.remove(self.index_click_task[name])
            # Double click: open
            path = self.buildings[name].getPythonTag("full_path")
            if os.path.isdir(path):
                self.history.append((self.current_path, self.camera.getPos(), self.camera.getHpr()))
                self.current_path = path
                self.load_path(path)
            self.resume_index()
        else:
            self.last_index_click[name] = now
            task_name = 'index_single_' + name
            self.index_click_task[name] = self.taskMgr.doMethodLater(0.3, self.perform_single_index_click, task_name, extraArgs=[name])

    def perform_single_index_click(self, task, name):
        if name in self.index_click_task:
            del self.index_click_task[name]
        self.teleport_to(name)

    def resume_index(self):
        self.in_menu = False
        base.disableMouse()
        if self.index_frame:
            self.index_frame.destroy()
            self.index_frame = None

    def teleport_to(self, name):
        building = self.buildings[name]
        b_pos = building.getPos()
        self.camera.setPos(b_pos.x, b_pos.y - 60, 15)
        self.camera.lookAt(b_pos.x, b_pos.y, b_pos.z + 10)
        self.resume_index()

    def update_fov(self):
        self.fov = self.fov_slider['value']
        self.cam.node().getLens().setFov(self.fov)
        self.save_config()

    def update_speed(self):
        self.move_speed = self.speed_slider['value']
        self.save_config()

    def update_fly_step(self):
        self.fly_step = self.fly_slider['value']
        self.save_config()

    def update_max_height(self):
        self.max_height = self.height_slider['value']
        self.save_config()

    def update_spacing(self):
        self.spacing = self.spacing_slider['value']
        self.save_config()

    def update_screen_mode(self):
        self.screen_mode = int(self.screen_slider['value'])
        self.set_screen_mode(self.screen_mode)
        self.save_config()

    def toggle_screen(self):
        self.screen_mode = (self.screen_mode + 1) % 3
        self.set_screen_mode(self.screen_mode)
        if hasattr(self, 'screen_slider'):
            self.screen_slider['value'] = self.screen_mode
        self.save_config()

    def set_screen_mode(self, mode):
        props = WindowProperties()
        props.setSize(self.screen_modes[mode][0], self.screen_modes[mode][1])
        props.setFullscreen(mode == 2)
        self.win.requestProperties(props)

    def increase_offset(self):
        self.movement_offset += 5
        self.update_offset_label()
        self.save_config()

    def decrease_offset(self):
        self.movement_offset -= 5
        self.update_offset_label()
        self.save_config()

    def reset_offset(self):
        self.movement_offset = 0
        self.update_offset_label()
        self.save_config()

    def update_offset_label(self):
        self.offset_label['text'] = str(self.movement_offset)

    def update_binding(self, action, slot, text):
        while len(self.key_bindings[action]) <= slot:
            self.key_bindings[action].append("")
        self.key_bindings[action][slot] = text
        self.key_bindings[action] = [k for k in self.key_bindings[action] if k]
        if len(self.key_bindings[action]) > 2:
            self.key_bindings[action] = self.key_bindings[action][:2]
        self.bind_keys()
        self.save_config()

    def toggle_beacon(self):
        if self.current_path in self.beacons:
            self.beacons.remove(self.current_path)
        else:
            self.beacons.append(self.current_path)
        self.save_config()

    def toggle_beacon_list(self):
        if self.beacon_frame:
            self.resume_beacon()
        else:
            self.show_beacon_list()

    def show_beacon_list(self):
        self.in_menu = True
        base.enableMouse()
        self.beacon_frame = DirectFrame(frameSize=(-1.3, 1.3, -0.9, 0.9), pos=(0, 0, 0))
        self.beacon_frame.bind(DGG.B1PRESS, self.start_drag, ['beacon'])
        self.beacon_frame.bind(DGG.B1RELEASE, self.stop_drag, ['beacon'])

        DirectButton(parent=self.beacon_frame, text="Return to Explorer", command=self.resume_beacon, pos=(0, 0, 0.9), scale=0.1, relief=DGG.RAISED)

        DirectButton(parent=self.beacon_frame, text="+List", command=self.add_beacon_file, pos=(-0.6, 0, 0.75), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.beacon_frame, text="Refresh", command=self.refresh_beacons, pos=(-0.2, 0, 0.75), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.beacon_frame, text="-List", command=self.remove_selected_beacon, pos=(0.2, 0, 0.75), scale=0.1, relief=DGG.RAISED)

        self.beacon_scrolled = DirectScrolledFrame(parent=self.beacon_frame,
            canvasSize=(-1.2, 1.2, -len(self.beacons)*0.1 - 0.2, 0),
            frameSize=(-1.2, 1.2, -0.7, 0.7),
            pos=(0, 0, -0.05),
            scrollBarWidth=0.05)
        self.update_beacon_list()

    def update_beacon_list(self):
        canvas = self.beacon_scrolled.getCanvas()
        for child in canvas.getChildren():
            child.removeNode()
        y_pos = -0.1
        self.beacon_buttons = []
        for path in self.beacons:
            exists = os.path.exists(path) and os.path.isdir(path)
            text_fg = (1, 1, 1, 1) if exists else (0.5, 0.5, 0.5, 1)
            cmd = self.handle_beacon_click if exists else None
            btn = DirectButton(parent=canvas, text=path, command=cmd, extraArgs=[path],
                               pos=(0, 0, y_pos), scale=0.07, text_fg=text_fg, frameColor=(0,0,0,0))
            self.beacon_buttons.append(btn)
            y_pos -= 0.1
        self.beacon_scrolled['canvasSize'] = (-1.2, 1.2, y_pos - 0.1, 0)

    def handle_beacon_click(self, path):
        now = globalClock.getRealTime()
        if now - self.last_beacon_click < 0.3:
            self.teleport_to_beacon(path)
            self.resume_beacon()
        else:
            self.selected_beacon = path
            for btn in self.beacon_buttons:
                if btn['extraArgs'][0] == path:
                    btn['frameColor'] = (0.2, 0.2, 0.8, 0.5)
                else:
                    btn['frameColor'] = (0, 0, 0, 0)
        self.last_beacon_click = now

    def add_beacon_file(self):
        root = tk.Tk()
        root.withdraw()
        dir_path = filedialog.askdirectory()
        if dir_path and dir_path not in self.beacons:
            self.beacons.append(dir_path)
            self.save_config()
            self.update_beacon_list()

    def refresh_beacons(self):
        self.update_beacon_list()

    def remove_selected_beacon(self):
        if self.selected_beacon and self.selected_beacon in self.beacons:
            self.beacons.remove(self.selected_beacon)
            self.selected_beacon = None
            self.save_config()
            self.update_beacon_list()

    def teleport_to_beacon(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            self.set_path(path)

    def resume_beacon(self):
        self.in_menu = False
        base.disableMouse()
        self.beacon_frame.destroy()
        self.beacon_frame = None

    def start_drag(self, frame_name, extraArgs=[]):
        if self.mouseWatcherNode.hasMouse():
            self.drag_start_x = self.mouseWatcherNode.getMouseX()
            self.drag_start_y = self.mouseWatcherNode.getMouseY()
            if frame_name == 'pause':
                self.dragging_frame = self.pause_frame
            elif frame_name == 'index':
                self.dragging_frame = self.index_frame
            elif frame_name == 'beacon':
                self.dragging_frame = self.beacon_frame
            self.frame_start_pos = self.dragging_frame.getPos()
        self.taskMgr.add(self.drag_task, "drag_task")

    def stop_drag(self, frame_name, extraArgs=[]):
        self.taskMgr.remove("drag_task")

    def drag_task(self, task):
        if self.mouseWatcherNode.hasMouse():
            mx = self.mouseWatcherNode.getMouseX()
            my = self.mouseWatcherNode.getMouseY()
            dx = mx - self.drag_start_x
            dy = my - self.drag_start_y
            new_pos = self.frame_start_pos + Vec3(dx, 0, dy)
            self.dragging_frame.setPos(new_pos)
        return Task.cont

    def set_path(self, path):
        path = os.path.abspath(path)
        if path.startswith(self.root_dir):
            rel_path = path[len(self.root_dir):].lstrip(os.sep)
            parts = rel_path.split(os.sep)
            self.history = []
            current = self.root_dir
            for part in parts[:-1]:
                if part:
                    current = os.path.join(current, part)
                    self.history.append((current, Vec3(0, -130, 22), Vec3(0, 0, 0)))  # default if not saved
            self.current_path = path
            self.load_path(self.current_path)
        else:
            # If not under root, reset to root
            self.history = []
            self.current_path = self.root_dir
            self.load_path(self.root_dir)

    def load_path(self, path):
        print(f"Entering: {path}")
        self.current_path = os.path.abspath(path)
        self.path_text.setText(f"Location: {self.current_path}")

        self.buildings = {}
        self.file_orbs = {}
        self.entries = []
        self.window_labels = []
        self.building_labels = []

        for child in self.render.getChildren():
            if child.hasPythonTag("vdm"):
                child.removeNode()

        ground = self.create_ground()
        if self.history:
            ground.setColor(0.9, 0.18, 0.18, 0.78)
            ground.setPythonTag("type", "exit_ground")

        try:
            entries = os.listdir(path)
            non_hidden = [e for e in entries if not e.startswith('.')]
            hidden = [e for e in entries if e.startswith('.')]
        except Exception as e:
            print("Error reading dir:", e)
            non_hidden = []
            hidden = []

        if not non_hidden and not (self.show_hidden and hidden):
            self.create_empty()
            return

        positions = self.hex_positions(len(non_hidden), spacing=self.spacing)
        for i, name in enumerate(non_hidden):
            full_path = os.path.join(path, name)
            x, y = positions[i]

            if os.path.isdir(full_path):
                try:
                    sub = [f for f in os.listdir(full_path) if not f.startswith('.')]
                    file_count = sum(1 for f in sub if os.path.isfile(os.path.join(full_path, f)))
                    dir_count = len(sub) - file_count
                    files = [f for f in sub if os.path.isfile(os.path.join(full_path, f))]
                except:
                    file_count = dir_count = 1
                    files = []
                building = self.create_building(x, y, name, full_path, file_count, dir_count, files)
                self.buildings[name] = building
            else:
                size = os.path.getsize(full_path) if os.access(full_path, os.R_OK) else 1024
                self.create_file_orb(x, y, 20, name, full_path, size)

        if self.show_hidden:
            hidden_positions = self.hex_positions(len(hidden), spacing=self.spacing * 1.5)
            for i, name in enumerate(hidden):
                full_path = os.path.join(path, name)
                hx, hy = hidden_positions[i]
                hz = self.max_height + 50 + (i % 5) * 10
                self.create_star(hx, hy, hz, name, full_path)

        # Build entries list
        for name in non_hidden:
            full_path = os.path.join(self.current_path, name)
            if name in self.buildings:
                node = self.buildings[name]
                typ = 'dir'
                size = 0  # Lazy load for dirs
            elif name in self.file_orbs:
                node = self.file_orbs[name]
                typ = 'file'
                size = self.get_size(full_path)  # Fast for files
            else:
                continue
            try:
                mod_time = os.path.getmtime(full_path)
            except:
                mod_time = 0
            self.entries.append({'name': name, 'full_path': full_path, 'node': node, 'type': typ, 'mod_time': mod_time, 'size': size})

        self.apply_sort()
        self.update_labels_visibility()
        self.update_label_positions()

    def hex_positions(self, count, spacing):
        positions = []
        layer = 0
        while len(positions) < count:
            if layer == 0:
                positions.append((0, 0))
                layer += 1
                continue
            for side in range(6):
                for step in range(layer):
                    angle = math.radians(60 * side)
                    dx = math.cos(angle) * spacing * layer
                    dy = math.sin(angle) * spacing * layer
                    offset = step * spacing
                    off_angle = angle + math.radians(60 if side < 3 else -60)
                    ox = math.cos(off_angle) * offset
                    oy = math.sin(off_angle) * offset
                    positions.append((dx + ox, dy + oy))
                    if len(positions) >= count:
                        return positions
            layer += 1
        return positions

    def create_ground(self):
        cm = CardMaker("ground")
        cm.setFrame(-15000, 15000, -15000, 15000)
        ground = self.render.attachNewNode(cm.generate())
        ground.setP(-90)
        ground.setColor(0.03, 0.03, 0.14, 1)
        ground.setTransparency(TransparencyAttrib.MAlpha)
        ground.setAlphaScale(0.92)
        ground.setPythonTag("vdm", True)
        ground.setCollideMask(BitMask32.bit(0))
        return ground

    def create_building(self, x, y, name, path, file_count, dir_count, files):
        base_size = 50
        height = min(32 + dir_count * 13, self.max_height)

        building = self.render.attachNewNode("building")
        building.setPos(x, y, 0)
        building.setPythonTag("vdm", True)
        building.setPythonTag("full_path", path)
        building.setPythonTag("type", "building")
        building.setPythonTag("height", height)

        cube = self.make_cube(building, base_size, base_size, height, self.building_color)
        cube.setCollideMask(BitMask32.bit(0))

        windows_per_side = max(1, (file_count + 3) // 4)
        for side in range(4):
            rot = side * 90
            for i in range(windows_per_side):
                wx = math.cos(math.radians(rot)) * (base_size / 2 - 8)
                wy = math.sin(math.radians(rot)) * (base_size / 2 - 8)
                wz = 14 + i * (height - 28) / max(1, windows_per_side - 1) if windows_per_side > 1 else height / 2
                win = building.attachNewNode("window")
                win.setPos(wx, wy, wz)
                self.make_sphere(win, 6.5, (1, 1, 0.4, 0.95))

                if files:
                    file_idx = (side * windows_per_side + i) % len(files)
                    label = TextNode("win_label")
                    label.setText(files[file_idx])
                    label.setAlign(TextNode.ACenter)
                    label.setWordwrap(2.0)
                    label.setShadow(0.05, 0.05)
                    label.setShadowColor(0, 0, 0, 1)
                    np = win.attachNewNode(label)
                    np.setPos(0, 0, 0)
                    np.setScale(5)
                    np.setBillboardPointEye()
                    label.setTextColor(1, 0.8, 0.2, 1)
                    np.hide()
                    self.window_labels.append(np)

        label = TextNode("label")
        label.setText(name)
        label.setAlign(TextNode.ACenter)
        label.setWordwrap(2.5)
        label.setShadow(0.05, 0.05)
        label.setShadowColor(0, 0, 0, 1)
        np = building.attachNewNode(label)
        np.setPos(0, 0, height + 28 if self.label_at_top else 5)
        np.setScale(20)
        np.setBillboardPointEye()
        label.setTextColor(1, 1, 1, 1)
        np.hide()
        self.building_labels.append(np)

        return building

    def create_file_orb(self, x, y, z, name, path, size):
        orb = self.render.attachNewNode("orb")
        orb.setPos(x, y, z)
        orb.setPythonTag("vdm", True)
        orb.setPythonTag("full_path", path)
        orb.setPythonTag("type", "file_orb")
        self.file_orbs[name] = orb
        hue = (hash(name) % 360) / 360.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
        radius = 8 + min(size / 1e6 * 22, 28)
        self.make_sphere(orb, radius, (r, g, b, 0.92))

        coll_node = CollisionNode('orb_coll')
        coll_node.addSolid(CollisionSphere(0, 0, 0, radius * 1.1))
        coll_node.setFromCollideMask(BitMask32(0))
        coll_node.setIntoCollideMask(BitMask32.bit(0))
        orb.attachNewNode(coll_node)

    def create_star(self, x, y, z, name, path):
        orb = self.render.attachNewNode("star")
        orb.setPos(x, y, z)
        orb.setPythonTag("vdm", True)
        orb.setPythonTag("full_path", path)
        if os.path.isdir(path):
            orb.setPythonTag("type", "star_dir")
        else:
            orb.setPythonTag("type", "star")
        r, g, b = 1, 1, 1
        radius = 4
        self.make_sphere(orb, radius, (r, g, b, 0.92))

        coll_node = CollisionNode('star_coll')
        coll_node.addSolid(CollisionSphere(0, 0, 0, radius * 1.1))
        coll_node.setFromCollideMask(BitMask32(0))
        coll_node.setIntoCollideMask(BitMask32.bit(0))
        orb.attachNewNode(coll_node)

    def create_empty(self):
        txt = TextNode("empty")
        txt.setText("Empty Directory — Click Red Floor to Exit")
        np = self.render.attachNewNode(txt)
        np.setPos(0, 0, 50)
        np.setScale(22)
        txt.setTextColor(0.8, 0.3, 0.3, 1)
        np.setPythonTag("vdm", True)

    def make_cube(self, parent, width, depth, height, color):
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('cube', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_w = GeomVertexWriter(vdata, 'color')
        tris = GeomTriangles(Geom.UHStatic)

        hw, hd, hh = width/2, depth/2, height
        corners = [
            (-hw, -hd, 0), (hw, -hd, 0), (hw, hd, 0), (-hw, hd, 0),
            (-hw, -hd, hh), (hw, -hd, hh), (hw, hd, hh), (-hw, hd, hh)
        ]
        for x, y, z in corners:
            vertex.addData3f(x, y, z)
            color_w.addData4f(*color)

        faces = [(0,1,2),(0,2,3),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
                 (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
        for a, b, c in faces:
            tris.addVertices(a, b, c)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode('cube')
        node.addGeom(geom)
        cube = parent.attachNewNode(node)
        cube.setTransparency(TransparencyAttrib.MAlpha)
        return cube

    def make_sphere(self, parent, radius, color):
        lines = LineSegs()
        lines.setThickness(7)
        lines.setColor(*color)
        segs = 26
        for i in range(segs + 1):
            a = 2 * math.pi * i / segs
            ca, sa = math.cos(a), math.sin(a)
            lines.moveTo(radius * ca, 0, radius * sa)
            lines.drawTo(radius * -ca, 0, radius * -sa)
            lines.moveTo(0, radius * ca, radius * sa)
            lines.drawTo(0, radius * -ca, radius * -sa)
            lines.moveTo(radius * ca, radius * sa, 0)
            lines.drawTo(radius * -ca, radius * -sa, 0)
        parent.attachNewNode(lines.create())

    def get_size(self, path):
        if path in self.sizes:
            return self.sizes[path]
        if not os.path.exists(path):
            size = 0
        elif os.path.isfile(path):
            try:
                size = os.path.getsize(path)
            except:
                size = 0
        else:
            size = 0
            for root, dirs, files in os.walk(path, onerror=None):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        size += os.path.getsize(fp)
                    except:
                        pass
        self.sizes[path] = size
        return size

    def human_size(self, bytes_size):
        if bytes_size == 0:
            return "0 bytes"
        size = float(bytes_size)
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}".rstrip('0').rstrip('.')
            size /= 1024.0
        return f"{size:.1f} PB".rstrip('0').rstrip('.')

    def update_camera(self, task):
        if not self.controls_enabled:
            return Task.cont
        dt = globalClock.getDt()

        if self.in_menu:
            self.selected_node = None
            self.target_text.setText("")
            if self.previous_selected:
                self.previous_selected.setColorScale(1, 1, 1, 1)
                self.previous_selected = None

        move = Vec3(
            self.keys["right"] - self.keys["left"],
            self.keys["forward"] - self.keys["backward"],
            0
        )
        if move.lengthSquared() > 0:
            target_pos = None
            use_center = True
            if not self.in_menu and self.selected_node:
                typ = self.selected_node.getPythonTag("type")
                if typ in ["building", "file_orb", "star_dir", "star"]:
                    use_center = False
                    if self.handler.getNumEntries() > 0:
                        entry = self.handler.getEntry(0)
                        target_pos = entry.getSurfacePoint(self.render)

            if use_center and not self.in_menu:
                center_ray = CollisionRay()
                center_ray.setFromLens(self.camNode, 0, 0)
                center_handler = CollisionHandlerQueue()
                center_trav = CollisionTraverser()
                center_node = CollisionNode('centerRay')
                center_np = self.camera.attachNewNode(center_node)
                center_node.addSolid(center_ray)
                center_node.setFromCollideMask(BitMask32.bit(0))
                center_node.setIntoCollideMask(BitMask32.allOff())
                center_trav.addCollider(center_np, center_handler)
                center_trav.traverse(self.render)
                if center_handler.getNumEntries() > 0:
                    center_handler.sortEntries()
                    entry = center_handler.getEntry(0)
                    target_pos = entry.getSurfacePoint(self.render)
                center_np.removeNode()

            if target_pos is not None:
                cam_pos = self.camera.getPos()
                dir_vec = target_pos - cam_pos
                dir_vec.z = 0
                if dir_vec.lengthSquared() == 0:
                    dir_vec = self.camera.getQuat().getForward()
                    dir_vec.z = 0
                dir_vec.normalize()
                offset_rad = math.radians(self.movement_offset)
                cos_o = math.cos(offset_rad)
                sin_o = math.sin(offset_rad)
                fx = dir_vec.x * cos_o - dir_vec.y * sin_o
                fy = dir_vec.x * sin_o + dir_vec.y * cos_o
                forward = Vec3(fx, fy, 0)
                right = Vec3(forward.y, -forward.x, 0)
                move.normalize()
                delta_pos = forward * move.y + right * move.x
                self.camera.setPos(self.camera.getPos() + delta_pos * self.move_speed * dt)
            else:
                heading = math.radians(self.camera.getH() + self.movement_offset)
                forward = Vec3(math.sin(heading), math.cos(heading), 0)
                right = Vec3(math.cos(heading), -math.sin(heading), 0)
                move.normalize()
                self.camera.setPos(self.camera.getPos() + (forward * move.y + right * move.x) * self.move_speed * dt)

        if not self.in_menu:
            if self.mouseWatcherNode.hasMouse():
                mx = self.win.getPointer(0).getX()
                my = self.win.getPointer(0).getY()
                cx = self.win.getXSize() // 2
                cy = self.win.getYSize() // 2
                if (mx, my) != (cx, cy):
                    self.camera.setH(self.camera.getH() - (mx - cx) * 0.22)
                    delta_p = (my - cy) * 0.22
                    new_p = self.camera.getP() - delta_p
                    self.camera.setP(max(-89, min(89, new_p)))
                    self.win.movePointer(0, cx, cy)

            # Mouse picking
            if self.mouseWatcherNode.hasMouse():
                mpos = self.mouseWatcherNode.getMouse()
                self.picker_ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())
                self.cTrav.traverse(self.render)
                self.selected_node = None
                if self.handler.getNumEntries() > 0:
                    self.handler.sortEntries()
                    entry = self.handler.getEntry(0)
                    nodepath = entry.getIntoNodePath()
                    while nodepath and not nodepath.hasPythonTag("vdm"):
                        nodepath = nodepath.getParent()
                    if nodepath and nodepath.hasPythonTag("vdm"):
                        self.selected_node = nodepath

            # Highlight
            if self.selected_node != self.previous_selected:
                if self.previous_selected:
                    self.previous_selected.setColorScale(1, 1, 1, 1)
                if self.selected_node:
                    self.selected_node.setColorScale(2.3, 1.9, 1.2, 1)
                    typ = self.selected_node.getPythonTag("type")
                    if typ in ["building", "file_orb", "star_dir", "star"]:
                        path = self.selected_node.getPythonTag("full_path")
                        name = os.path.basename(path)
                        if path not in self.sizes:
                            self.sizes[path] = self.get_size(path)
                        size = self.sizes[path]
                        size_str = self.human_size(size)
                        self.target_text.setText(size_str + "\n" + name)
                    elif typ == "exit_ground":
                        self.target_text.setText("Exit")
                    else:
                        self.target_text.setText("")
                else:
                    self.target_text.setText("")
                self.previous_selected = self.selected_node

        # Dynamic label positions
        new_label_at_top = self.camera.getZ() >= 70
        if new_label_at_top != self.label_at_top:
            self.label_at_top = new_label_at_top
            self.update_label_positions()

        return Task.cont

    def update_label_positions(self):
        for np in self.building_labels:
            building = np.getParent()
            height = building.getPythonTag("height")
            np.setZ(height + 28 if self.label_at_top else 5)


# LAUNCH
app = DataWalk()
app.run()
