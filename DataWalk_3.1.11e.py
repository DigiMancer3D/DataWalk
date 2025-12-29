# DataWalk.11.py
# Run: python DataWalk.11.py
# To make executable:
# Install pyinstaller: pip install pyinstaller
# Run: pyinstaller --onefile DataWalk.11.py
# The exe will be in dist folder.
# Quick tip for installation issues:
# 1. Make sure you're in the venv (source ~/vdm_env/bin/activate)
# 2. Install ALL the missing Python packages inside the venv:
# pip install panda3d tkinter pyinstaller
# 3. Go to your script folder (with quotes because of spaces):
# cd "/media/z0m8i3d/Black_Stone/Documents/Visual DriveMapper (VDM)"
# 4. Run: python DataWalk.11.py
# To find your kill: ps aux | grep python
# Kill top running: kill -9 PID#
# Kill run-away intances (PID keeps chaning but all stable PIDs of grep list must be killed first): pkill -f DataWalk.11.py
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
    CollisionSphere, BitMask32, Lens, WindowProperties, Plane, CollisionPlane, Point3, PointLight, LColor, CollisionBox, KeyboardButton
)
from direct.interval.IntervalGlobal import Sequence, LerpColorInterval, Func, LerpPosInterval
from direct.task import Task
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DirectEntry, DirectSlider, DirectScrolledFrame, DirectCheckButton
from direct.gui import DirectGuiGlobals as DGG
if platform.system() == 'Windows':
    import winreg
try:
    import psutil
except ImportError:
    psutil = None
class DataWalk(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.background_color = (0.01, 0.01, 0.04, 1)
        self.setBackgroundColor(*self.background_color)
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
        self.delete_dialog = None
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
        self.keys = {"forward": 0, "backward": 0, "left": 0, "right": 0, "pause_z": 0, "jump": 0}
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
            "pause": ["p", "escape"],
            "index": ["i"],
            "wt_toggle": ["t"],
            "bt_toggle": ["b"],
            "screen_toggle": ["u"],
            "beacon_toggle": ["k"],
            "beacon_list": ["l"],
            "jump": ["space"],
            "hidden_toggle": ["n"],
            "context": ["mouse3"],
            "pause_z": ["z"],
            "menu_prev": ["6"],
            "menu_next": ["7"]
        }
        self.sizes = {}
        self.player_height = 5
        self.z_multiplier = 1.7
        self.z_speed = self.move_speed * self.z_multiplier
        self.ambient_light_color = (0.45, 0.5, 0.7, 1)
        self.dir_light_color = (1.0, 0.95, 0.9, 1)
        self.dir_light_hpr = (30, -60, 0)
        self.window_orb_color = (1, 1, 0.4, 0.95)
        self.star_color = (1, 1, 1, 0.92)
        self.ground_color = (0.03, 0.14, 0.03, 1)
        self.title_text_color = (0, 1, 1, 1)
        self.path_text_color = (0.7, 1, 1, 1)
        self.target_text_color = (1, 0.7, 1, 1)
        self.other_hud_color = (0.8, 0.3, 0.3, 1)
        self.respawn_color = (1, 0.5, 0, 1)
        self.glow_color = None
        self.glow_intensity = 0.5
        self.respawn_point = None
        self.custom_colors = {}
        self.show_folders = True
        self.show_files = True
        self.show_hidden = False
        self.show_objects = True
        self.menus = []
        self.colors_changed = False
        self.scene_changed = False
        self.selected = [] # Added for select/deselect
        self.select_all = False
        self.clipboard = []
        self.clip_op = None
        self.color_picker_dialog = None
        self.dir_picker_frame = None
        self.dialog_open = False
        self.ground_menu = None
        self.pause_z = False
        self.tutorial_text = True
        self.announcement_queue = []
        self.announcement_active = False
        self.just_toggled_pause_z = False
        self.player_glow_color = (0, 0, 1, 0.8)
        self.player_highlight = False
        self.player_light = None
        self.player_selected = False
        self.jumping = False
        self.up_pitch_threshold = 14
        self.down_pitch_threshold = -14
        self.load_config()
        if psutil:
            mem_gb = psutil.virtual_memory().total / (1024 ** 3)
            if mem_gb < 4:
                self.spacing = 60
                self.max_height = 100
                self.move_speed = 40
        if len(sys.argv) > 1:
            self.root_dir = os.path.abspath(sys.argv[1])
            self.last_location = self.root_dir
        self.disableMouse()
        self.camera.setPos(0, -130, 22)
        self.camera.setHpr(0, 0, 0)
        self.cTrav = CollisionTraverser()
        self.handler = CollisionHandlerQueue()
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.camera.attachNewNode(self.picker_node)
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.picker_node.setFromCollideMask(BitMask32.bit(0))
        self.picker_node.setIntoCollideMask(BitMask32.allOff())
        self.cTrav.addCollider(self.picker_np, self.handler)
        self.alight = AmbientLight('alight')
        self.alight.setColor(Vec4(*self.ambient_light_color))
        self.render.setLight(self.render.attachNewNode(self.alight))
        self.dlight = DirectionalLight('dlight')
        self.dlight.setColor(Vec4(*self.dir_light_color))
        self.dlnp = self.render.attachNewNode(self.dlight)
        self.dlnp.setHpr(*self.dir_light_hpr)
        self.render.setLight(self.dlnp)
        self.bind_keys()
        self.title_text = TextNode('title')
        self.update_title_text()
        self.title_text.setAlign(TextNode.ACenter)
        self.title_text.setWordwrap(40.0)
        self.title_np = aspect2d.attachNewNode(self.title_text)
        self.title_np.setScale(0.07)
        self.title_np.setPos(0, 0, 0.92)
        self.title_text.setTextColor(*self.title_text_color)
        self.path_text = TextNode('path')
        self.path_text.setText("Location: /")
        self.path_text.setAlign(TextNode.ALeft)
        self.path_text.setWordwrap(30.0)
        self.path_np = aspect2d.attachNewNode(self.path_text)
        self.path_np.setScale(0.05)
        self.path_np.setPos(-1.6, 0, -0.9)
        self.path_text.setTextColor(*self.path_text_color)
        self.target_text = TextNode('target')
        self.target_text.setText("")
        self.target_text.setAlign(TextNode.ARight)
        self.target_text.setWordwrap(12.0)
        self.target_np = aspect2d.attachNewNode(self.target_text)
        self.target_np.setScale(0.05)
        self.target_np.setPos(1.6, 0, -0.91)
        self.target_text.setTextColor(*self.target_text_color)
        self.aim_text = TextNode('aim')
        self.aim_text.setText("")
        self.aim_text.setAlign(TextNode.ACenter)
        self.aim_np = aspect2d.attachNewNode(self.aim_text)
        self.aim_np.setScale(0.05)
        self.aim_np.setPos(0, 0, -0.95)
        self.aim_text.setTextColor(1,1,1,1)
        self.keys_text = TextNode('keys')
        self.keys_text.setText("")
        self.keys_text.setAlign(TextNode.ACenter)
        self.keys_np = aspect2d.attachNewNode(self.keys_text)
        self.keys_np.setScale(0.05)
        self.keys_np.setPos(0, 0, -0.9)
        self.keys_text.setTextColor(1,1,1,1)
        self.accept("aspect_ratio_changed", self.update_hud_positions)
        self.update_hud_positions()
        self.player_glow = self.render.attachNewNode("player_glow")
        self.make_sphere(self.player_glow, 5, self.player_glow_color)
        self.player_glow.setZ(0.5)
        self.player_glow.setPythonTag("vdm", True)
        self.player_glow.setPythonTag("type", "player_glow")
        self.player_glow.setCollideMask(BitMask32.bit(0))
        self.set_path(self.root_dir)
        self.taskMgr.add(self.update_camera, "camera_task")
        self.taskMgr.doMethodLater(0.1, self.ask_load_last, 'ask_load')
        self.taskMgr.doMethodLater(0.2, self.check_initial_key_states, 'check_keys')
    def check_initial_key_states(self, task):
        if self.mouseWatcherNode.is_button_down(KeyboardButton.ascii_key('z')):
            self.toggle_pause_z()
        if self.mouseWatcherNode.is_button_down(KeyboardButton.ascii_key('n')):
            self.toggle_hidden_files()
        if self.mouseWatcherNode.is_button_down(KeyboardButton.ascii_key('t')):
            self.toggle_window_titles()
        if self.mouseWatcherNode.is_button_down(KeyboardButton.ascii_key('b')):
            self.toggle_building_titles()
        return Task.done
    def update_title_text(self):
        base_text = "DataWalk ([P]ause | [I]ndex | [L]ist | [N]ight | [T]itles | [B]uildings | [PgeUP] Accend | [PgeDN] Descend | [Z] Toggle | [w/s/a/d] Movement | [mouse] Camera) Enjoy Responsibly"
        if not self.tutorial_text:
            base_text = "DataWalk -- Enjoy Responsibly"
        self.title_text.setText(base_text)
    def announce(self, text):
        self.announcement_queue.append(text)
        if not self.announcement_active:
            self.process_announcement()
    def process_announcement(self):
        if self.announcement_queue:
            text = self.announcement_queue.pop(0)
            self.announcement_active = True
            self.title_text.setText(text)
            self.title_text.setTextColor(*self.title_text_color[:3], 1)
            seq = Sequence()
            seq.append(LerpColorInterval(self.title_np, 2.3, LColor(*self.title_text_color[:3], 0), startColor=LColor(*self.title_text_color[:3], 1)))
            seq.append(Func(self.update_title_text))
            seq.append(Func(self.set_announcement_done))
            seq.start()
        else:
            self.announcement_active = False
    def set_announcement_done(self):
        self.announcement_active = False
        self.process_announcement()
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
        self.screen_mode = self.config_data.get('screen_mode', 2)
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
        self.player_height = self.config_data.get('player_height', 5)
        self.z_multiplier = self.config_data.get('z_multiplier', 1.7)
        self.z_speed = self.move_speed * self.z_multiplier
        self.background_color = tuple(self.config_data.get('background_color', [0.01, 0.01, 0.04, 1]))
        self.building_color = tuple(self.config_data.get('building_color', [0.15, 0.35, 0.95, 0.88]))
        self.ambient_light_color = tuple(self.config_data.get('ambient_light_color', [0.45, 0.5, 0.7, 1]))
        self.dir_light_color = tuple(self.config_data.get('dir_light_color', [1.0, 0.95, 0.9, 1]))
        self.dir_light_hpr = tuple(self.config_data.get('dir_light_hpr', [30, -60, 0]))
        self.window_orb_color = tuple(self.config_data.get('window_orb_color', [1, 1, 0.4, 0.95]))
        self.star_color = tuple(self.config_data.get('star_color', [1, 1, 1, 0.92]))
        self.ground_color = tuple(self.config_data.get('ground_color', [0.03, 0.14, 0.03, 1]))
        self.title_text_color = tuple(self.config_data.get('title_text_color', [0, 1, 1, 1]))
        self.path_text_color = tuple(self.config_data.get('path_text_color', [0.7, 1, 1, 1]))
        self.target_text_color = tuple(self.config_data.get('target_text_color', [1, 0.7, 1, 1]))
        self.other_hud_color = tuple(self.config_data.get('other_hud_color', [0.8, 0.3, 0.3, 1]))
        self.respawn_color = tuple(self.config_data.get('respawn_color', [1, 0.5, 0, 1]))
        self.glow_color = self.config_data.get('glow_color', None)
        self.glow_intensity = self.config_data.get('glow_intensity', 0.5)
        self.respawn_point = self.config_data.get('respawn_point', None)
        self.custom_colors = self.config_data.get('custom_colors', {})
        self.show_folders = self.config_data.get('show_folders', True)
        self.show_files = self.config_data.get('show_files', True)
        self.show_objects = self.config_data.get('show_objects', True)
        self.pause_z = self.config_data.get('pause_z', False)
        self.tutorial_text = self.config_data.get('tutorial_text', True)
        self.player_glow_color = tuple(self.config_data.get('player_glow_color', [0, 0, 1, 0.8]))
        self.select_all = self.config_data.get('select_all', False)
        self.player_selected = self.config_data.get('player_selected', False)
        self.up_pitch_threshold = self.config_data.get('up_pitch_threshold', 14)
        self.down_pitch_threshold = self.config_data.get('down_pitch_threshold', -14)
        self.setBackgroundColor(*self.background_color)
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
                pass
        elif system == 'Linux':
            try:
                desktop_file = os.path.expanduser('~/.local/share/applications/datawalk.desktop')
                if val:
                    if self.original_default is None:
                        proc = subprocess.Popen(['xdg-mime', 'query', 'default', 'inode/directory'], stdout=subprocess.PIPE)
                        self.original_default = proc.communicate()[0].decode().strip()
                    with open(desktop_file, 'w') as f:
                        f.write('[Desktop Entry]\nType=Application\nName=DataWalk\nExec=python {0} %U\nMimeType=inode/directory;\n'.format(os.path.abspath(__file__)))
                    subprocess.call(['xdg-mime', 'default', 'datawalk.desktop', 'inode/directory'])
                else:
                    if self.original_default:
                        subprocess.call(['xdg-mime', 'default', self.original_default, 'inode/directory'])
                    if os.path.exists(desktop_file):
                        os.remove(desktop_file)
            except Exception as e:
                pass
        elif system == 'Darwin':
            pass
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
        self.config_data['player_height'] = self.player_height
        self.config_data['z_multiplier'] = self.z_multiplier
        self.config_data['background_color'] = list(self.background_color)
        self.config_data['building_color'] = list(self.building_color)
        self.config_data['ambient_light_color'] = list(self.ambient_light_color)
        self.config_data['dir_light_color'] = list(self.dir_light_color)
        self.config_data['dir_light_hpr'] = list(self.dir_light_hpr)
        self.config_data['window_orb_color'] = list(self.window_orb_color)
        self.config_data['star_color'] = list(self.star_color)
        self.config_data['ground_color'] = list(self.ground_color)
        self.config_data['title_text_color'] = list(self.title_text_color)
        self.config_data['path_text_color'] = list(self.path_text_color)
        self.config_data['target_text_color'] = list(self.target_text_color)
        self.config_data['other_hud_color'] = list(self.other_hud_color)
        self.config_data['respawn_color'] = list(self.respawn_color)
        self.config_data['glow_color'] = self.glow_color
        self.config_data['glow_intensity'] = self.glow_intensity
        self.config_data['respawn_point'] = self.respawn_point
        self.config_data['custom_colors'] = self.custom_colors
        self.config_data['show_folders'] = self.show_folders
        self.config_data['show_files'] = self.show_files
        self.config_data['show_objects'] = self.show_objects
        self.config_data['pause_z'] = self.pause_z
        self.config_data['tutorial_text'] = self.tutorial_text
        self.config_data['player_glow_color'] = list(self.player_glow_color)
        self.config_data['select_all'] = self.select_all
        self.config_data['player_selected'] = self.player_selected
        self.config_data['up_pitch_threshold'] = self.up_pitch_threshold
        self.config_data['down_pitch_threshold'] = self.down_pitch_threshold
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f, indent=4)
    def set_root_dir(self, dir_path):
        if dir_path:
            new_root = os.path.abspath(dir_path)
            if new_root != self.root_dir:
                self.root_dir = new_root
                self.save_config()
                if not self.current_path.startswith(self.root_dir):
                    self.set_path(self.root_dir)
                if hasattr(self, 'home_label') and self.home_label:
                    self.home_label['text'] = self.root_dir
    def reset_root_dir(self):
        self.root_dir = "/"
        self.save_config()
        if not self.current_path.startswith(self.root_dir):
            self.set_path(self.root_dir)
        if hasattr(self, 'home_label') and self.home_label:
            self.home_label['text'] = self.root_dir
    def show_dir_picker(self, callback, start_dir=None):
        if start_dir is None:
            start_dir = self.root_dir
        self.current_pick_dir = start_dir
        aspect = self.getAspectRatio()
        self.saved_hpr = self.camera.getHpr()
        self.in_menu = True
        base.enableMouse()
        self.dir_picker_frame = DirectFrame(frameSize=(-1.0, 1.0, -0.8, 0.8), pos=(aspect - 1.0, 0, 0.4), sortOrder=70)
        self.dir_picker_frame.setBin('background', 0)
        self.dir_picker_frame.bind(DGG.B1PRESS, self.start_drag, ['dir_picker'])
        self.dir_picker_frame.bind(DGG.B1RELEASE, self.stop_drag, ['dir_picker'])
        self.dir_label = DirectLabel(parent=self.dir_picker_frame, text=self.current_pick_dir, pos=(0, 0, 0.7), scale=0.07, text_align=TextNode.ACenter)
        DirectButton(parent=self.dir_picker_frame, text="..", command=self.pick_up, pos=(-0.6, 0, 0.6), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.dir_picker_frame, text="Select", command=lambda: (callback(self.current_pick_dir), self.close_dir_picker()), pos=(0, 0, 0.6), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.dir_picker_frame, text="Cancel", command=self.close_dir_picker, pos=(0.6, 0, 0.6), scale=0.1, relief=DGG.RAISED)
        self.dir_scrolled = DirectScrolledFrame(parent=self.dir_picker_frame,
            canvasSize=(-0.9, 0.9, -10, 0),
            frameSize=(-0.9, 0.9, -0.5, 0.5),
            pos=(0, 0, 0),
            scrollBarWidth=0.05)
        self.refresh_pick_list()
    def refresh_pick_list(self):
        try:
            entries = sorted([e for e in os.listdir(self.current_pick_dir) if os.path.isdir(os.path.join(self.current_pick_dir, e))])
        except:
            entries = []
        canvas = self.dir_scrolled.getCanvas()
        for child in canvas.getChildren():
            child.removeNode()
        y_pos = -0.1
        for name in entries:
            DirectButton(parent=canvas, text=name, command=self.pick_enter, extraArgs=[name],
                         pos=(0, 0, y_pos), scale=0.07, frameColor=(0,0,0,0))
            y_pos -= 0.1
        self.dir_scrolled['canvasSize'] = (-0.9, 0.9, y_pos - 0.1, 0)
        self.dir_label['text'] = self.current_pick_dir
    def pick_enter(self, name):
        self.current_pick_dir = os.path.join(self.current_pick_dir, name)
        self.refresh_pick_list()
    def pick_up(self):
        if self.current_pick_dir != "/":
            self.current_pick_dir = os.path.dirname(self.current_pick_dir)
            self.refresh_pick_list()
    def close_dir_picker(self):
        if self.dir_picker_frame:
            self.dir_picker_frame.destroy()
            self.dir_picker_frame = None
        self.in_menu = False
        base.disableMouse()
        self.camera.setHpr(self.saved_hpr)
    def ask_load_last(self, task):
        if self.last_location:
            self.show_load_dialog()
        return Task.done
    def show_load_dialog(self):
        aspect = self.getAspectRatio()
        self.saved_hpr = self.camera.getHpr()
        self.in_menu = True
        base.enableMouse()
        self.load_dialog = DirectDialog(dialogName="loadDialog", text=f"Load last location?\n{self.last_location}", buttonTextList=['Yes', 'No'], buttonValueList=[1, 0], command=self.load_dialog_callback, pos=(-aspect/2 + 0.4, 0, -0.5), sortOrder=60)
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
        self.camera.setHpr(self.saved_hpr)
    def userExit(self):
        self.last_camera_pos = list(self.camera.getPos())
        self.last_camera_hpr = list(self.camera.getHpr())
        self.show_save_dialog()
    def show_save_dialog(self):
        aspect = self.getAspectRatio()
        self.saved_hpr = self.camera.getHpr()
        self.in_menu = True
        base.enableMouse()
        self.save_dialog = DirectDialog(dialogName="saveDialog", text="Save last location?", buttonTextList=['Yes', 'No'], buttonValueList=[1, 0], command=self.save_dialog_callback, pos=(-aspect/2 + 0.4, 0, -0.5), sortOrder=60)
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
        self.camera.setHpr(self.saved_hpr)
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
                    if action in ["forward", "backward", "left", "right", "jump"]:
                        self.accept(key.lower(), self.set_key, [action, 1])
                        self.accept(key.upper(), self.set_key, [action, 1])
                        self.accept(key.lower() + "-up", self.set_key, [action, 0])
                        self.accept(key.upper() + "-up", self.set_key, [action, 0])
                    elif action in ["ascend", "descend"]:
                        self.accept(key.lower(), getattr(self, action))
                        self.accept(key.upper(), getattr(self, action))
                    elif action == "interact":
                        if key == "mouse1":
                            self.accept(key, self.handle_mouse_click)
                        else:
                            self.accept(key.lower(), self.interact)
                            self.accept(key.upper(), self.interact)
                    elif action == "pause":
                        self.accept(key.lower(), self.toggle_pause)
                        self.accept(key.upper(), self.toggle_pause)
                    elif action == "index":
                        self.accept(key.lower(), self.toggle_index)
                        self.accept(key.upper(), self.toggle_index)
                    elif action == "wt_toggle":
                        self.accept(key.lower(), self.toggle_window_titles)
                        self.accept(key.upper(), self.toggle_window_titles)
                    elif action == "bt_toggle":
                        self.accept(key.lower(), self.toggle_building_titles)
                        self.accept(key.upper(), self.toggle_building_titles)
                    elif action == "screen_toggle":
                        self.accept(key.lower(), self.toggle_screen)
                        self.accept(key.upper(), self.toggle_screen)
                    elif action == "beacon_toggle":
                        self.accept(key.lower(), self.toggle_beacon)
                        self.accept(key.upper(), self.toggle_beacon)
                    elif action == "beacon_list":
                        self.accept(key.lower(), self.toggle_beacon_list)
                        self.accept(key.upper(), self.toggle_beacon_list)
                    elif action == "hidden_toggle":
                        self.accept(key.lower(), self.toggle_hidden_files)
                        self.accept(key.upper(), self.toggle_hidden_files)
                    elif action == "context":
                        self.accept(key, self.handle_context)
                    elif action == "pause_z":
                        self.accept(key.lower(), self.toggle_pause_z)
                        self.accept(key.upper(), self.toggle_pause_z)
                    elif action == "menu_prev":
                        self.accept(key.lower(), self.menu_prev)
                        self.accept(key.upper(), self.menu_prev)
                    elif action == "menu_next":
                        self.accept(key.lower(), self.menu_next)
                        self.accept(key.upper(), self.menu_next)
    def toggle_pause_z(self):
        self.pause_z = not self.pause_z
        self.just_toggled_pause_z = True
        self.save_config()
    def menu_prev(self):
        if self.menus:
            menu = self.menus[-1]
            menu['highlighted'] = (menu['highlighted'] - 1) % len(menu['options'])
            self.update_menu_highlight(menu)
    def menu_next(self):
        if self.menus:
            menu = self.menus[-1]
            menu['highlighted'] = (menu['highlighted'] + 1) % len(menu['options'])
            self.update_menu_highlight(menu)
    def update_menu_highlight(self, menu):
        for i, opt in enumerate(menu['options']):
            if i == menu['highlighted']:
                opt['np'].setColorScale(1.5, 1.5, 1.5, 1)
            else:
                opt['np'].setColorScale(1, 1, 1, 1)
    def set_key(self, key, value):
        self.keys[key] = value
    def ascend(self):
        self.camera.setZ(self.camera.getZ() + self.fly_step)
    def descend(self):
        self.camera.setZ(max(self.player_height, self.camera.getZ() - self.fly_step))
    def start_spring_jump(self):
        self.jumping = True
        dist = self.fly_step * 4 / 3
        current_pos = self.camera.getPos()
        seq = Sequence(
            LerpPosInterval(self.camera, 0.5, Point3(current_pos.x, current_pos.y, current_pos.z + dist), blendType='easeOut'),
            Func(self.set_jumping_false)
        )
        seq.start()
    def set_jumping_false(self):
        self.jumping = False
    def handle_mouse_click(self):
        if not self.selected_node or self.in_menu:
            return
        typ = self.selected_node.getPythonTag("type")
        if typ == "menu_option":
            self.execute_menu_option(self.selected_node)
            return
        if self.click_task:
            self.taskMgr.remove(self.click_task)
            self.click_task = None
            if typ == "player_glow":
                self.toggle_select_all()
            else:
                self.open_selected()
        else:
            self.click_task = self.taskMgr.doMethodLater(0.3, self.perform_single_interact, 'single_interact')
    def perform_single_interact(self, task):
        self.click_task = None
        if self.selected_node:
            typ = self.selected_node.getPythonTag("type")
            if typ == "player_glow":
                self.toggle_player_highlight()
            else:
                self.interact()
        return Task.done
    def interact(self):
        if not self.selected_node:
            return
        typ = self.selected_node.getPythonTag("type")
        if typ == "player_glow":
            return
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
        if typ == "player_glow":
            path = self.current_path
        elif typ in ["building", "file_orb", "star_dir", "star"]:
            path = self.selected_node.getPythonTag("full_path")
        else:
            return
        if os.path.isdir(path) and typ != "player_glow":
            self.interact()
        else:
            try:
                if platform.system() == 'Windows':
                    os.startfile(path)
                elif platform.system() == 'Linux':
                    subprocess.call(['xdg-open', path])
                elif platform.system() == 'Darwin':
                    subprocess.call(['open', path])
            except Exception as e:
                pass
    def toggle_pause(self):
        if self.pause_frame:
            self.resume_pause()
        else:
            self.pause_game()
    def pause_game(self):
        self.saved_hpr = self.camera.getHpr()
        self.in_menu = True
        base.enableMouse()
        self.colors_changed = False
        self.scene_changed = False
        self.pause_frame = DirectFrame(frameSize=(-1.3, 1.3, -0.9, 0.9), pos=(0, 0, 0), sortOrder=50)
        self.pause_frame.setBin('background', 0)
        self.pause_frame.bind(DGG.B1PRESS, self.start_drag, ['pause'])
        self.pause_frame.bind(DGG.B1RELEASE, self.stop_drag, ['pause'])
        DirectButton(parent=self.pause_frame, text="Exit DataWalk", command=self.userExit, pos=(0, 0, 0.8), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.pause_frame, text="Return to Explorer", command=self.resume_pause, pos=(0, 0, 0.7), scale=0.1, relief=DGG.RAISED)
        DirectLabel(parent=self.pause_frame, text="Set as Default Explorer:", pos=(-0.8, 0, 0.6), scale=0.07, text_align=TextNode.ALeft)
        self.default_cb = DirectCheckButton(parent=self.pause_frame, scale=0.07, pos=(0.2, 0, 0.6), indicatorValue=self.is_default, command=self.toggle_default_explorer)
        DirectLabel(parent=self.pause_frame, text="Tutorial Text:", pos=(-0.8, 0, 0.5), scale=0.07, text_align=TextNode.ALeft)
        self.tutorial_cb = DirectCheckButton(parent=self.pause_frame, scale=0.07, pos=(0.2, 0, 0.5), indicatorValue=self.tutorial_text, command=self.set_tutorial_text)
        DirectLabel(parent=self.pause_frame, text="Player Select:", pos=(-0.8, 0, 0.4), scale=0.07, text_align=TextNode.ALeft)
        self.player_select_cb = DirectCheckButton(parent=self.pause_frame, scale=0.07, pos=(0.2, 0, 0.4), indicatorValue=self.player_selected, command=self.set_player_selected)
        DirectLabel(parent=self.pause_frame, text="Select All:", pos=(-0.8, 0, 0.3), scale=0.07, text_align=TextNode.ALeft)
        self.select_all_cb = DirectCheckButton(parent=self.pause_frame, scale=0.07, pos=(0.2, 0, 0.3), indicatorValue=self.select_all, command=self.set_select_all)
        self.scrolled_frame = DirectScrolledFrame(parent=self.pause_frame,
            canvasSize=(-1.2, 1.2, -3, 0),
            frameSize=(-1.2, 1.2, -0.7, 0.7),
            pos=(0, 0, 0),
            scrollBarWidth=0.05)
        canvas = self.scrolled_frame.getCanvas()
        y_pos = -0.2
        DirectLabel(parent=canvas, text="Field of View:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.fov_value_label = DirectLabel(parent=canvas, text=str(int(self.fov)), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.fov_slider = DirectSlider(parent=canvas, range=(30, 120), value=self.fov, pos=(0, 0, y_pos), scale=1.0, command=self.update_fov)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Move Speed:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.speed_value_label = DirectLabel(parent=canvas, text=str(int(self.move_speed)), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.speed_slider = DirectSlider(parent=canvas, range=(20, 100), value=self.move_speed, pos=(0, 0, y_pos), scale=1.0, command=self.update_speed)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Fly Distance:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.fly_value_label = DirectLabel(parent=canvas, text=str(int(self.fly_step)), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.fly_slider = DirectSlider(parent=canvas, range=(20, 100), value=self.fly_step, pos=(0, 0, y_pos), scale=1.0, command=self.update_fly_step)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Max Building Height:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.height_value_label = DirectLabel(parent=canvas, text=str(int(self.max_height)), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.height_slider = DirectSlider(parent=canvas, range=(50, 200), value=self.max_height, pos=(0, 0, y_pos), scale=1.0, command=self.update_max_height)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Cluster Spacing:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.spacing_value_label = DirectLabel(parent=canvas, text=str(int(self.spacing)), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.spacing_slider = DirectSlider(parent=canvas, range=(50, 150), value=self.spacing, pos=(0, 0, y_pos), scale=1.0, command=self.update_spacing)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Player Height:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.player_height_value_label = DirectLabel(parent=canvas, text=str(int(self.player_height)), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.player_height_slider = DirectSlider(parent=canvas, range=(5, 13), value=self.player_height, pos=(0, 0, y_pos), scale=1.0, command=self.update_player_height)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Z-Axis Speed:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.z_multiplier_value_label = DirectLabel(parent=canvas, text=f"{self.z_multiplier:.1f}", pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.z_multiplier_slider = DirectSlider(parent=canvas, range=(1.3, 6.9), value=self.z_multiplier, pos=(0, 0, y_pos), scale=1.0, command=self.update_z_multiplier)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Pause Z-Axis:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.pause_z_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.pause_z, command=self.set_pause_z)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Up Pitch Threshold:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.up_pitch_value_label = DirectLabel(parent=canvas, text=str(int(self.up_pitch_threshold)), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.up_pitch_slider = DirectSlider(parent=canvas, range=(-89, 89), value=self.up_pitch_threshold, pos=(0, 0, y_pos), scale=1.0, command=self.update_up_pitch)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Down Pitch Threshold:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.down_pitch_value_label = DirectLabel(parent=canvas, text=str(int(self.down_pitch_threshold)), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.down_pitch_slider = DirectSlider(parent=canvas, range=(-89, 89), value=self.down_pitch_threshold, pos=(0, 0, y_pos), scale=1.0, command=self.update_down_pitch)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Screen Size:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.normal_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(-0.5, 0, y_pos), indicatorValue=self.screen_mode == 0, command=self.set_screen_normal)
        DirectLabel(parent=canvas, text="Normal", pos=(-0.3, 0, y_pos), scale=0.07)
        self.doubled_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.0, 0, y_pos), indicatorValue=self.screen_mode == 1, command=self.set_screen_doubled)
        DirectLabel(parent=canvas, text="Doubled", pos=(0.2, 0, y_pos), scale=0.07)
        self.full_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.5, 0, y_pos), indicatorValue=self.screen_mode == 2, command=self.set_screen_full)
        DirectLabel(parent=canvas, text="Fullscreen", pos=(0.7, 0, y_pos), scale=0.07)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Building Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.building_color_btn = DirectLabel(parent=canvas, frameColor=self.building_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.building_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.building_color, self.set_building_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Background Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.background_color_btn = DirectLabel(parent=canvas, frameColor=self.background_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.background_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.background_color, self.set_background_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Ambient Light Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.ambient_light_color_btn = DirectLabel(parent=canvas, frameColor=self.ambient_light_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.ambient_light_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.ambient_light_color, self.set_ambient_light_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Directional Light Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.dir_light_color_btn = DirectLabel(parent=canvas, frameColor=self.dir_light_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.dir_light_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.dir_light_color, self.set_dir_light_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Directional Light H:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.dir_h_value_label = DirectLabel(parent=canvas, text=str(int(self.dir_light_hpr[0])), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.dir_h_slider = DirectSlider(parent=canvas, range=(-180, 180), value=self.dir_light_hpr[0], pos=(0, 0, y_pos), scale=1.0, command=self.update_dir_h)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Directional Light P:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.dir_p_value_label = DirectLabel(parent=canvas, text=str(int(self.dir_light_hpr[1])), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.dir_p_slider = DirectSlider(parent=canvas, range=(-180, 180), value=self.dir_light_hpr[1], pos=(0, 0, y_pos), scale=1.0, command=self.update_dir_p)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Directional Light R:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.dir_r_value_label = DirectLabel(parent=canvas, text=str(int(self.dir_light_hpr[2])), pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.dir_r_slider = DirectSlider(parent=canvas, range=(-180, 180), value=self.dir_light_hpr[2], pos=(0, 0, y_pos), scale=1.0, command=self.update_dir_r)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Window-Orb Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.window_orb_color_btn = DirectLabel(parent=canvas, frameColor=self.window_orb_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.window_orb_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.window_orb_color, self.set_window_orb_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Star Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.star_color_btn = DirectLabel(parent=canvas, frameColor=self.star_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.star_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.star_color, self.set_star_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Ground Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.ground_color_btn = DirectLabel(parent=canvas, frameColor=self.ground_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.ground_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.ground_color, self.set_ground_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Title Text Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.title_text_color_btn = DirectLabel(parent=canvas, frameColor=self.title_text_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.title_text_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.title_text_color, self.set_title_text_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Path Text Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.path_text_color_btn = DirectLabel(parent=canvas, frameColor=self.path_text_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.path_text_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.path_text_color, self.set_path_text_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Target Text Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.target_text_color_btn = DirectLabel(parent=canvas, frameColor=self.target_text_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.target_text_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.target_text_color, self.set_target_text_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Other HUD Text Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.other_hud_color_btn = DirectLabel(parent=canvas, frameColor=self.other_hud_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.other_hud_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.other_hud_color, self.set_other_hud_color))
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Respawn Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.respawn_color_btn = DirectLabel(parent=canvas, frameColor=self.respawn_color, frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
        self.respawn_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker(self.respawn_color, self.set_respawn_color))
        DirectButton(parent=canvas, text="Default", command=self.reset_respawn_color, pos=(1.0, 0, y_pos), scale=0.07)
        y_pos -= 0.15
        glow_text = "Dynamic" if self.glow_color is None else "Custom"
        DirectLabel(parent=canvas, text="Town Glow Color:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        if self.glow_color is None:
            DirectLabel(parent=canvas, text="Dynamic", pos=(0.8, 0, y_pos), scale=0.07)
        else:
            self.glow_color_btn = DirectLabel(parent=canvas, frameColor=(self.glow_color[0], self.glow_color[1], self.glow_color[2], 1), frameSize=(-0.1, 0.1, -0.05, 0.05), relief=DGG.RIDGE, pos=(0.8, 0, y_pos))
            self.glow_color_btn.bind(DGG.B1PRESS, lambda x: self.show_color_picker((self.glow_color[0], self.glow_color[1], self.glow_color[2], 1), self.set_glow_color))
        DirectButton(parent=canvas, text="Default", command=self.reset_glow_color, pos=(1.0, 0, y_pos), scale=0.07)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Glow Intensity:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.glow_intensity_value_label = DirectLabel(parent=canvas, text=f"{self.glow_intensity:.1f}", pos=(0.8, 0, y_pos), scale=0.07)
        y_pos -= 0.1
        self.glow_intensity_slider = DirectSlider(parent=canvas, range=(0.0, 1.0), value=self.glow_intensity, pos=(0, 0, y_pos), scale=1.0, command=self.update_glow_intensity)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Show Window Titles:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.window_titles_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_window_titles, command=self.set_window_titles)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Show Building Titles:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.building_titles_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_building_titles, command=self.set_building_titles)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Show Hidden Files:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.hidden_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_hidden, command=self.set_hidden_files)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Show Folders:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.folders_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_folders, command=self.set_show_folders)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Show Files:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.files_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_files, command=self.set_show_files)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Show Objects:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.objects_cb = DirectCheckButton(parent=canvas, scale=0.07, pos=(0.2, 0, y_pos), indicatorValue=self.show_objects, command=self.set_show_objects)
        y_pos -= 0.15
        DirectLabel(parent=canvas, text="Movement Offset:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        DirectButton(parent=canvas, text="+", command=self.increase_offset, pos=(0.2, 0, y_pos), scale=0.07, relief=DGG.RAISED)
        DirectButton(parent=canvas, text="Default Offset", command=self.reset_offset, pos=(0.4, 0, y_pos), scale=0.07, relief=DGG.RAISED)
        DirectButton(parent=canvas, text="-", command=self.decrease_offset, pos=(0.8, 0, y_pos), scale=0.07, relief=DGG.RAISED)
        self.offset_label = DirectLabel(parent=canvas, text=str(self.movement_offset), pos=(1.0, 0, y_pos), scale=0.07)
        y_pos -= 0.15
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
        DirectLabel(parent=canvas, text="Home Directory:", pos=(-1.1, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        self.home_label = DirectLabel(parent=canvas, text=self.root_dir, pos=(-0.5, 0, y_pos), scale=0.07, text_align=TextNode.ALeft)
        DirectButton(parent=canvas, text="Change", command=lambda: self.show_dir_picker(self.set_root_dir), pos=(0.5, 0, y_pos), scale=0.07, relief=DGG.RAISED)
        DirectButton(parent=canvas, text="Reset", command=self.reset_root_dir, pos=(0.8, 0, y_pos), scale=0.07, relief=DGG.RAISED)
        y_pos -= 0.15
        self.scrolled_frame['canvasSize'] = (-1.2, 1.2, y_pos - 0.2, 0)
    def set_tutorial_text(self, val):
        self.tutorial_text = val
        self.update_title_text()
        self.save_config()
    def resume_pause(self):
        self.in_menu = False
        base.disableMouse()
        self.camera.setHpr(self.saved_hpr)
        self.pause_frame.destroy()
        self.pause_frame = None
        if self.colors_changed or self.scene_changed:
            saved_pos = self.camera.getPos()
            saved_hpr = self.camera.getHpr()
            self.load_path(self.current_path)
            self.camera.setPos(saved_pos)
            self.camera.setHpr(saved_hpr)
            self.colors_changed = False
            self.scene_changed = False
    def set_window_titles(self, val):
        self.show_window_titles = val
        self.update_labels_visibility()
        self.save_config()
    def set_building_titles(self, val):
        self.show_building_titles = val
        self.update_labels_visibility()
        self.save_config()
    def set_hidden_files(self, val):
        self.show_hidden = val
        self.save_config()
        self.scene_changed = True
    def toggle_hidden_files(self):
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
            if self.show_window_titles:
                label.show()
            else:
                label.hide()
        for label in self.building_labels:
            if self.show_building_titles:
                label.show()
            else:
                label.hide()
    def toggle_index(self):
        if self.index_frame:
            self.resume_index()
        else:
            self.show_index()
    def show_index(self):
        self.saved_hpr = self.camera.getHpr()
        self.in_menu = True
        base.enableMouse()
        self.index_frame = DirectFrame(frameSize=(-1.3, 1.3, -0.9, 0.9), pos=(0, 0, 0), sortOrder=50)
        self.index_frame.setBin('background', 0)
        self.index_frame.bind(DGG.B1PRESS, self.start_drag, ['index'])
        self.index_frame.bind(DGG.B1RELEASE, self.stop_drag, ['index'])
        DirectButton(parent=self.index_frame, text="Return to Explorer", command=self.resume_index, pos=(0, 0, 0.8), scale=0.1, relief=DGG.RAISED)
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
        if mode == 0:
            self.entries.sort(key=lambda e: e['name'].lower(), reverse=False)
        elif mode == 1:
            self.entries.sort(key=lambda e: e['mod_time'], reverse=True)
        elif mode == 2:
            self.entries.sort(key=lambda e: e['mod_time'], reverse=False)
        elif mode == 3:
            self.entries.sort(key=lambda e: e['size'], reverse=False)
        elif mode == 4:
            total_size = sum(e['size'] for e in self.entries)
            self.entries.sort(key=lambda e: (e['size'] / total_size if total_size > 0 else 0), reverse=True)
        elif mode == 5:
            self.entries.sort(key=lambda e: e['name'].lower(), reverse=True)
        positions = self.hex_positions(len(self.entries), spacing=self.spacing)
        for i, entry in enumerate(self.entries):
            x, y = positions[i]
            z = 0
            entry['node'].setPos(x, y, z)
    def handle_index_click(self, name):
        now = globalClock.getRealTime()
        if name in self.last_index_click and now - self.last_index_click[name] < 0.3:
            if name in self.index_click_task:
                self.taskMgr.remove(self.index_click_task[name])
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
        self.camera.setHpr(self.saved_hpr)
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
        self.fov_value_label['text'] = str(int(self.fov))
        self.save_config()
    def update_speed(self):
        self.move_speed = self.speed_slider['value']
        self.z_speed = self.move_speed * self.z_multiplier
        self.speed_value_label['text'] = str(int(self.move_speed))
        self.save_config()
    def update_fly_step(self):
        self.fly_step = self.fly_slider['value']
        self.fly_value_label['text'] = str(int(self.fly_step))
        self.save_config()
    def update_max_height(self):
        self.max_height = self.height_slider['value']
        self.height_value_label['text'] = str(int(self.max_height))
        self.save_config()
    def update_spacing(self):
        self.spacing = self.spacing_slider['value']
        self.spacing_value_label['text'] = str(int(self.spacing))
        self.save_config()
    def update_player_height(self):
        self.player_height = self.player_height_slider['value']
        self.player_height_value_label['text'] = str(int(self.player_height))
        self.save_config()
    def update_z_multiplier(self):
        self.z_multiplier = self.z_multiplier_slider['value']
        self.z_speed = self.move_speed * self.z_multiplier
        self.z_multiplier_value_label['text'] = f"{self.z_multiplier:.1f}"
        self.save_config()
    def set_pause_z(self, val):
        self.pause_z = val
        self.just_toggled_pause_z = True
        self.save_config()
    def update_up_pitch(self):
        self.up_pitch_threshold = self.up_pitch_slider['value']
        self.up_pitch_value_label['text'] = str(int(self.up_pitch_threshold))
        self.save_config()
    def update_down_pitch(self):
        self.down_pitch_threshold = self.down_pitch_slider['value']
        self.down_pitch_value_label['text'] = str(int(self.down_pitch_threshold))
        self.save_config()
    def set_screen_normal(self, val):
        if val:
            self.screen_mode = 0
            self.doubled_cb['indicatorValue'] = 0
            self.doubled_cb.setIndicatorValue()
            self.full_cb['indicatorValue'] = 0
            self.full_cb.setIndicatorValue()
            self.set_screen_mode(self.screen_mode)
            self.save_config()
    def set_screen_doubled(self, val):
        if val:
            self.screen_mode = 1
            self.normal_cb['indicatorValue'] = 0
            self.normal_cb.setIndicatorValue()
            self.full_cb['indicatorValue'] = 0
            self.full_cb.setIndicatorValue()
            self.set_screen_mode(self.screen_mode)
            self.save_config()
    def set_screen_full(self, val):
        if val:
            self.screen_mode = 2
            self.normal_cb['indicatorValue'] = 0
            self.normal_cb.setIndicatorValue()
            self.doubled_cb['indicatorValue'] = 0
            self.doubled_cb.setIndicatorValue()
            self.set_screen_mode(self.screen_mode)
            self.save_config()
    def toggle_screen(self):
        self.screen_mode = (self.screen_mode + 1) % 3
        self.set_screen_mode(self.screen_mode)
        self.save_config()
    def set_screen_mode(self, mode):
        props = WindowProperties()
        props.setSize(self.screen_modes[mode][0], self.screen_modes[mode][1])
        props.setFullscreen(mode == 2)
        self.win.requestProperties(props)
    def show_color_picker(self, current_color, callback):
        aspect = self.getAspectRatio()
        self.dialog_open = True
        base.enableMouse()
        if self.color_picker_dialog:
            self.color_picker_dialog.destroy()
        self.color_picker_dialog = DirectFrame(frameSize=(-0.6, 0.6, -0.4, 0.4), pos=(-aspect + 0.6, 0, 0.5), relief=DGG.RIDGE, sortOrder=100)
        self.color_picker_dialog.setBin('gui-popup', 100)
        r, g, b, a = current_color
        self.preview_label = DirectLabel(parent=self.color_picker_dialog, frameColor=LColor(r, g, b, a), frameSize=(-0.1, 0.1, -0.1, 0.1), pos=(0, 0, 0.25))
        DirectLabel(parent=self.color_picker_dialog, text="Red:", pos=(-0.5, 0, 0.1), scale=0.07)
        self.r_slider = DirectSlider(parent=self.color_picker_dialog, range=(0, 1), value=r, pos=(0, 0, 0.1), scale=0.5, command=self.update_preview_color)
        DirectLabel(parent=self.color_picker_dialog, text="Green:", pos=(-0.5, 0, 0.0), scale=0.07)
        self.g_slider = DirectSlider(parent=self.color_picker_dialog, range=(0, 1), value=g, pos=(0, 0, 0.0), scale=0.5, command=self.update_preview_color)
        DirectLabel(parent=self.color_picker_dialog, text="Blue:", pos=(-0.5, 0, -0.1), scale=0.07)
        self.b_slider = DirectSlider(parent=self.color_picker_dialog, range=(0, 1), value=b, pos=(0, 0, -0.1), scale=0.5, command=self.update_preview_color)
        DirectLabel(parent=self.color_picker_dialog, text="Alpha:", pos=(-0.5, 0, -0.2), scale=0.07)
        self.a_slider = DirectSlider(parent=self.color_picker_dialog, range=(0, 1), value=a, pos=(0, 0, -0.2), scale=0.5, command=self.update_preview_color)
        DirectButton(parent=self.color_picker_dialog, text="OK", command=lambda: self.apply_color(callback), pos=(-0.3, 0, -0.3), scale=0.07)
        DirectButton(parent=self.color_picker_dialog, text="Cancel", command=self.close_color_picker, pos=(0.3, 0, -0.3), scale=0.07)
        self.color_callback = callback
    def update_preview_color(self):
        r = self.r_slider['value']
        g = self.g_slider['value']
        b = self.b_slider['value']
        a = self.a_slider['value']
        self.preview_label['frameColor'] = (r, g, b, a)
    def apply_color(self, callback):
        r = self.r_slider['value']
        g = self.g_slider['value']
        b = self.b_slider['value']
        a = self.a_slider['value']
        callback((r, g, b, a))
        self.close_color_picker()
        self.colors_changed = True
        saved_pos = self.camera.getPos()
        saved_hpr = self.camera.getHpr()
        self.load_path(self.current_path)
        self.camera.setPos(saved_pos)
        self.camera.setHpr(saved_hpr)
    def close_color_picker(self):
        if self.color_picker_dialog:
            self.color_picker_dialog.destroy()
            self.color_picker_dialog = None
        self.dialog_open = False
        if not self.in_menu:
            base.disableMouse()
    def set_building_color(self, color):
        self.building_color = color
        if hasattr(self, 'building_color_btn'):
            self.building_color_btn['frameColor'] = color
        self.colors_changed = True
        self.save_config()
    def set_background_color(self, color):
        self.background_color = color
        if hasattr(self, 'background_color_btn'):
            self.background_color_btn['frameColor'] = color
        self.setBackgroundColor(*color)
        self.colors_changed = True
        self.save_config()
    def set_ambient_light_color(self, color):
        self.ambient_light_color = color
        if hasattr(self, 'ambient_light_color_btn'):
            self.ambient_light_color_btn['frameColor'] = color
        self.alight.setColor(Vec4(*color))
        self.colors_changed = True
        self.save_config()
    def set_dir_light_color(self, color):
        self.dir_light_color = color
        if hasattr(self, 'dir_light_color_btn'):
            self.dir_light_color_btn['frameColor'] = color
        self.dlight.setColor(Vec4(*color))
        self.colors_changed = True
        self.save_config()
    def update_dir_h(self):
        self.dir_light_hpr = (self.dir_h_slider['value'], self.dir_light_hpr[1], self.dir_light_hpr[2])
        self.dir_h_value_label['text'] = str(int(self.dir_light_hpr[0]))
        self.dlnp.setHpr(*self.dir_light_hpr)
        self.save_config()
    def update_dir_p(self):
        self.dir_light_hpr = (self.dir_light_hpr[0], self.dir_p_slider['value'], self.dir_light_hpr[2])
        self.dir_p_value_label['text'] = str(int(self.dir_light_hpr[1]))
        self.dlnp.setHpr(*self.dir_light_hpr)
        self.save_config()
    def update_dir_r(self):
        self.dir_light_hpr = (self.dir_light_hpr[0], self.dir_light_hpr[1], self.dir_r_slider['value'])
        self.dir_r_value_label['text'] = str(int(self.dir_light_hpr[2]))
        self.dlnp.setHpr(*self.dir_light_hpr)
        self.save_config()
    def set_window_orb_color(self, color):
        self.window_orb_color = color
        if hasattr(self, 'window_orb_color_btn'):
            self.window_orb_color_btn['frameColor'] = color
        self.colors_changed = True
        self.save_config()
    def set_star_color(self, color):
        self.star_color = color
        if hasattr(self, 'star_color_btn'):
            self.star_color_btn['frameColor'] = color
        self.colors_changed = True
        self.save_config()
    def set_ground_color(self, color):
        self.ground_color = color
        if hasattr(self, 'ground_color_btn'):
            self.ground_color_btn['frameColor'] = color
        self.colors_changed = True
        self.save_config()
    def set_title_text_color(self, color):
        self.title_text_color = color
        if hasattr(self, 'title_text_color_btn'):
            self.title_text_color_btn['frameColor'] = color
        self.title_text.setTextColor(*color)
        self.colors_changed = True
        self.save_config()
    def set_path_text_color(self, color):
        self.path_text_color = color
        if hasattr(self, 'path_text_color_btn'):
            self.path_text_color_btn['frameColor'] = color
        self.path_text.setTextColor(*color)
        self.colors_changed = True
        self.save_config()
    def set_target_text_color(self, color):
        self.target_text_color = color
        if hasattr(self, 'target_text_color_btn'):
            self.target_text_color_btn['frameColor'] = color
        self.target_text.setTextColor(*color)
        self.colors_changed = True
        self.save_config()
    def set_other_hud_color(self, color):
        self.other_hud_color = color
        if hasattr(self, 'other_hud_color_btn'):
            self.other_hud_color_btn['frameColor'] = color
        self.colors_changed = True
        self.save_config()
    def set_respawn_color(self, color):
        self.respawn_color = color
        if hasattr(self, 'respawn_color_btn'):
            self.respawn_color_btn['frameColor'] = color
        self.colors_changed = True
        self.save_config()
    def reset_respawn_color(self):
        self.respawn_color = (1, 0.5, 0, 1)
        if hasattr(self, 'respawn_color_btn'):
            self.respawn_color_btn['frameColor'] = self.respawn_color
        self.colors_changed = True
        self.save_config()
    def set_glow_color(self, color):
        self.glow_color = (color[0], color[1], color[2])
        self.colors_changed = True
        self.save_config()
    def reset_glow_color(self):
        self.glow_color = None
        self.colors_changed = True
        self.save_config()
    def update_glow_intensity(self):
        self.glow_intensity = self.glow_intensity_slider['value']
        self.glow_intensity_value_label['text'] = f"{self.glow_intensity:.1f}"
        self.colors_changed = True
        self.save_config()
    def set_player_glow_color(self, color):
        self.player_glow_color = color
        self.player_glow.getChild(0).setColor(*color)
        self.colors_changed = True
        self.save_config()
    def toggle_player_highlight(self):
        self.player_highlight = not self.player_highlight
        if self.player_highlight:
            if not self.player_light:
                pl = PointLight('player_light')
                pl.setColor(Vec4(1, 1, 1, 1))
                self.player_light = self.camera.attachNewNode(pl)
                self.render.setLight(self.player_light)
        else:
            if self.player_light:
                self.render.clearLight(self.player_light)
                self.player_light.removeNode()
                self.player_light = None
    def set_player_selected(self, val):
        self.player_selected = val
        self.update_player_selected()
        self.save_config()
    def update_player_selected(self):
        if self.player_selected:
            if self.current_path not in self.selected:
                self.selected.append(self.current_path)
                node = self.find_node_for_path(self.current_path)
                if node:
                    self.add_select_glow(node)
        else:
            if self.current_path in self.selected:
                self.selected.remove(self.current_path)
                node = self.find_node_for_path(self.current_path)
                if node:
                    self.remove_select_glow(node)
    def toggle_select_all(self):
        self.select_all = not self.select_all
        self.set_select_all(self.select_all)
    def set_select_all(self, val):
        self.select_all = val
        if self.pause_frame:
            self.select_all_cb['indicatorValue'] = val
            self.select_all_cb.setIndicatorValue()
        if self.select_all:
            for entry in self.entries:
                path = entry['full_path']
                if path not in self.selected:
                    self.selected.append(path)
                self.add_select_glow(entry['node'])
        else:
            for entry in self.entries:
                path = entry['full_path']
                if path in self.selected:
                    self.selected.remove(path)
                self.remove_select_glow(entry['node'])
        self.save_config()
    def add_select_glow(self, node):
        if node:
            glow_np = node.find("**/select_glow")
            if not glow_np:
                glow = node.attachNewNode("select_glow")
                self.make_sphere(glow, 5, self.player_glow_color)
                glow.setZ(0.5)
    def remove_select_glow(self, node):
        if node:
            glow_np = node.find("**/select_glow")
            if glow_np:
                glow_np.removeNode()
    def find_node_for_path(self, path):
        for entry in self.entries:
            if entry['full_path'] == path:
                return entry['node']
        return None
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
        self.saved_hpr = self.camera.getHpr()
        self.in_menu = True
        base.enableMouse()
        self.beacon_frame = DirectFrame(frameSize=(-1.3, 1.3, -0.9, 0.9), pos=(0, 0, 0), sortOrder=50)
        self.beacon_frame.setBin('background', 0)
        self.beacon_frame.bind(DGG.B1PRESS, self.start_drag, ['beacon'])
        self.beacon_frame.bind(DGG.B1RELEASE, self.stop_drag, ['beacon'])
        DirectButton(parent=self.beacon_frame, text="Return to Explorer", command=self.resume_beacon, pos=(0, 0, 0.9), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.beacon_frame, text="+List", command=lambda: self.show_dir_picker(self.add_beacon_dir), pos=(-0.6, 0, 0.75), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.beacon_frame, text="Refresh", command=self.refresh_beacons, pos=(-0.2, 0, 0.75), scale=0.1, relief=DGG.RAISED)
        DirectButton(parent=self.beacon_frame, text="-List", command=self.remove_selected_beacon, pos=(0.2, 0, 0.75), scale=0.1, relief=DGG.RAISED)
        self.beacon_scrolled = DirectScrolledFrame(parent=self.beacon_frame,
            canvasSize=(-1.2, 1.2, -len(self.beacons)*0.1 - 0.2, 0),
            frameSize=(-1.2, 1.2, -0.7, 0.7),
            pos=(0, 0, -0.05),
            scrollBarWidth=0.05)
        self.update_beacon_list()
    def add_beacon_dir(self, dir_path):
        if dir_path and dir_path not in self.beacons:
            self.beacons.append(dir_path)
            self.save_config()
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
        self.camera.setHpr(self.saved_hpr)
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
            elif frame_name == 'dir_picker':
                self.dragging_frame = self.dir_picker_frame
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
    def handle_context(self):
        if self.in_menu:
            return
        if self.selected_node:
            typ = self.selected_node.getPythonTag("type")
            if typ == "menu_option":
                self.execute_menu_option(self.selected_node)
                return
            if typ in ["building", "star_dir"]:
                self.show_context_folder(self.selected_node)
            elif typ in ["file_orb", "star"]:
                self.show_context_file(self.selected_node)
            elif typ in ["ground", "exit_ground"]:
                self.show_context_ground(self.selected_node)
            elif typ == "player_glow":
                self.show_context_shadow(self.selected_node)
        else:
            self.toggle_pause()
    def show_context_folder(self, node):
        path = node.getPythonTag("full_path")
        options = [
            {"title": "Color", "action": lambda: self.show_color_picker(self.custom_colors.get(path, self.building_color), lambda c: self.set_object_color(path, c))},
            {"title": "Enter", "action": self.interact},
            {"title": "Open in OS", "action": lambda: self.open_selected()},
            {"title": "Copy", "action": self.copy_path},
            {"title": "Cut", "action": self.cut_path},
            {"title": "Delete", "action": lambda: self.delete_path(path)},
            {"title": "Add Beacon" if path not in self.beacons else "Remove Beacon", "action": self.toggle_beacon},
            {"title": "Select" if path not in self.selected else "Deselect", "action": lambda: self.toggle_select(path)},
            {"title": "Close", "action": lambda: self.close_menu(node)}
        ]
        self.create_context_menu(node, options)
    def show_context_file(self, node):
        path = node.getPythonTag("full_path")
        options = [
            {"title": "Color", "action": lambda: self.show_color_picker(self.custom_colors.get(path, (1,1,1,0.92)), lambda c: self.set_object_color(path, c))},
            {"title": "Open in OS", "action": lambda: self.open_selected()},
            {"title": "Copy", "action": self.copy_path},
            {"title": "Cut", "action": self.cut_path},
            {"title": "Delete", "action": lambda: self.delete_path(path)},
            {"title": "Add Beacon" if path not in self.beacons else "Remove Beacon", "action": self.toggle_beacon},
            {"title": "Select" if path not in self.selected else "Deselect", "action": lambda: self.toggle_select(path)},
            {"title": "Close", "action": lambda: self.close_menu(node)}
        ]
        self.create_context_menu(node, options)
    def show_context_ground(self, node):
        options = [
            {"title": "Color", "action": lambda: self.show_color_picker(self.ground_color, self.set_ground_color)},
            {"title": "Open location in OS", "action": lambda: self.open_selected()},
            {"title": "Add Beacon" if self.current_path not in self.beacons else "Remove Beacon", "action": self.toggle_beacon},
            {"title": "Make Respawn Point" if self.current_path != self.respawn_point else "Reset to Default", "action": self.toggle_respawn_point},
            {"title": "Go Back" if self.history else None, "action": self.interact},
            {"title": "Go Home", "action": lambda: self.set_path(self.root_dir)},
            {"title": "Find Center", "action": self.find_center},
            {"title": "Exit DataWalk", "action": self.userExit},
            {"title": "Mute Folders", "action": lambda: self.toggle_show("folders")},
            {"title": "Mute Files", "action": lambda: self.toggle_show("files")},
            {"title": "Mute Hidden", "action": lambda: self.toggle_show("hidden")},
            {"title": "Mute Objects", "action": lambda: self.toggle_show("objects")},
        ]
        if self.selected:
            options += [
                {"title": "Copy Selected", "action": self.copy_selected},
                {"title": "Cut Selected", "action": self.cut_selected},
                {"title": "Delete Selected", "action": self.delete_selected},
            ]
        if self.clipboard:
            options += [
                {"title": "Paste", "action": self.paste_clipboard},
            ]
        options += [
            {"title": "Close", "action": self.close_ground_menu}
        ]
        options = [opt for opt in options if opt["title"] is not None]
        self.show_ground_menu(options)
    def show_ground_menu(self, options):
        if self.ground_menu:
            self.close_ground_menu()
        self.in_menu = True
        base.enableMouse()
        self.ground_menu = DirectFrame(frameSize=(-1.0, 1.0, -0.8, 0.8), pos=(0, 0, 0), frameColor=(0, 0, 0, 0.8))
        self.ground_menu.setBin('background', 0)
        self.ground_scrolled = DirectScrolledFrame(parent=self.ground_menu,
            canvasSize=(-0.9, 0.9, -len(options)*0.1 - 0.2, 0),
            frameSize=(-0.9, 0.9, -0.7, 0.7),
            pos=(0, 0, 0),
            scrollBarWidth=0.05)
        canvas = self.ground_scrolled.getCanvas()
        y_pos = -0.1
        for opt in options:
            btn = DirectButton(parent=canvas, text=opt["title"], command=opt["action"], pos=(0, 0, y_pos), scale=0.07, text_fg=self.path_text_color, frameColor=(0,0,0,0))
            y_pos -= 0.1
        self.ground_scrolled['canvasSize'] = (-0.9, 0.9, y_pos - 0.1, 0)
    def close_ground_menu(self):
        if self.ground_menu:
            self.ground_menu.destroy()
            self.ground_menu = None
        self.in_menu = False
        base.disableMouse()
    def show_context_shadow(self, node):
        options = [
            {"title": "Color", "action": lambda: self.show_color_picker(self.player_glow_color, self.set_player_glow_color)},
            {"title": "Settings", "action": self.toggle_pause},
            {"title": "Beacons", "action": self.toggle_beacon_list},
            {"title": "Index", "action": self.toggle_index},
            {"title": "Go Back" if self.history else None, "action": self.interact},
            {"title": "Go Home", "action": lambda: self.set_path(self.root_dir)},
            {"title": "Find Center", "action": self.find_center},
            {"title": "Exit DataWalk", "action": self.userExit},
            {"title": "Mute Folders", "action": lambda: self.toggle_show("folders")},
            {"title": "Mute Files", "action": lambda: self.toggle_show("files")},
            {"title": "Mute Hidden", "action": lambda: self.toggle_show("hidden")},
            {"title": "Mute Objects", "action": lambda: self.toggle_show("objects")},
            {"title": "Close", "action": lambda: self.close_menu(node)}
        ]
        options = [opt for opt in options if opt["title"] is not None]
        self.create_context_menu(node, options)
    def create_context_menu(self, node, options):
        if len(self.menus) >= 3:
            self.close_menu(self.menus[0]['node'])
        menu_node = node.attachNewNode("menu")
        menu = {'node': node, 'menu_node': menu_node, 'options': [], 'highlighted': 0}
        num_options = len(options)
        radius = 80
        for i, opt in enumerate(options):
            label = TextNode("menu_opt")
            label.setText(opt["title"])
            label.setAlign(TextNode.ACenter)
            label.setWordwrap(len(opt["title"]) / 2 + 1)
            np = menu_node.attachNewNode(label)
            np.setName(opt["title"])
            angle = 2 * math.pi * i / num_options
            np.setPos(math.cos(angle) * radius, math.sin(angle) * radius, 0)
            np.setScale(15)
            np.setBillboardPointEye()
            width = label.getWidth() * 15
            height = label.getHeight() * 15
            coll_node = CollisionNode('menu_coll')
            coll_radius = math.sqrt((width/2)**2 + (height/2)**2) + 10
            coll_node.addSolid(CollisionSphere(0, 0, 0, coll_radius))
            coll_np = np.attachNewNode(coll_node)
            coll_np.setCollideMask(BitMask32.bit(0))
            coll_np.setPythonTag("vdm", True)
            coll_np.setPythonTag("type", "menu_option")
            coll_np.setPythonTag("action", opt["action"])
            menu['options'].append({"np": np, "action": opt["action"]})
        self.menus.append(menu)
        self.update_menu_highlight(menu)
    def close_menu(self, node):
        for menu in self.menus:
            if menu['node'] == node:
                menu['menu_node'].removeNode()
                self.menus.remove(menu)
                break
    def execute_menu_option(self, node):
        action = node.getPythonTag("action")
        if action:
            action()
        parent = node.getParent().getParent()
        self.close_menu(parent.getParent())
    def set_object_color(self, path, color):
        self.custom_colors[path] = color
        self.colors_changed = True
        self.save_config()
    def copy_path(self):
        # Placeholder for copy, perhaps to system clipboard
        pass
    def cut_path(self):
        # Placeholder for cut
        pass
    def delete_path(self, path):
        aspect = self.getAspectRatio()
        self.dialog_open = True
        base.enableMouse()
        self.delete_dialog = YesNoDialog(text="Delete?", command=lambda val: self.do_delete(val, path), pos=(aspect/2 - 0.4, 0, -0.5), sortOrder=60)
        self.delete_dialog.show()
    def do_delete(self, val, path):
        if val:
            if os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.load_path(self.current_path)
        if self.delete_dialog:
            self.delete_dialog.destroy()
            self.delete_dialog = None
        self.dialog_open = False
        if not self.in_menu:
            base.disableMouse()
    def delete_selected(self):
        aspect = self.getAspectRatio()
        self.dialog_open = True
        base.enableMouse()
        self.delete_dialog = YesNoDialog(text="Delete selected?", command=self.do_delete_selected, pos=(aspect/2 - 0.4, 0, -0.5), sortOrder=60)
        self.delete_dialog.show()
    def do_delete_selected(self, val):
        if val:
            import shutil
            for path in list(self.selected):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.selected.remove(path)
            self.load_path(self.current_path)
        if self.delete_dialog:
            self.delete_dialog.destroy()
            self.delete_dialog = None
        self.dialog_open = False
        if not self.in_menu:
            base.disableMouse()
    def copy_selected(self):
        self.clipboard = list(self.selected)
        self.clip_op = 'copy'
    def cut_selected(self):
        self.clipboard = list(self.selected)
        self.clip_op = 'cut'
    def paste_clipboard(self):
        import shutil
        if self.clip_op == 'copy':
            for p in self.clipboard:
                dest = os.path.join(self.current_path, os.path.basename(p))
                if os.path.isdir(p):
                    shutil.copytree(p, dest)
                else:
                    shutil.copy(p, dest)
        elif self.clip_op == 'cut':
            for p in self.clipboard:
                dest = os.path.join(self.current_path, os.path.basename(p))
                shutil.move(p, dest)
        self.clipboard = []
        self.clip_op = None
        self.load_path(self.current_path)
    def toggle_select(self, path):
        if path in self.selected:
            self.selected.remove(path)
            node = self.find_node_for_path(path)
            if node:
                self.remove_select_glow(node)
        else:
            self.selected.append(path)
            node = self.find_node_for_path(path)
            if node:
                self.add_select_glow(node)
    def toggle_respawn_point(self):
        if self.current_path == self.respawn_point:
            self.respawn_point = None
        else:
            self.respawn_point = self.current_path
        self.save_config()
        self.colors_changed = True
    def find_center(self):
        self.camera.setPos(0, -130, 22)
        self.camera.setHpr(0, 0, 0)
    def toggle_show(self, typ):
        if typ == "folders":
            self.show_folders = not self.show_folders
        elif typ == "files":
            self.show_files = not self.show_files
        elif typ == "hidden":
            self.show_hidden = not self.show_hidden
        elif typ == "objects":
            self.show_objects = not self.show_objects
        self.scene_changed = True
        self.save_config()
    def set_show_folders(self, val):
        self.show_folders = val
        self.scene_changed = True
        self.save_config()
    def set_show_files(self, val):
        self.show_files = val
        self.scene_changed = True
        self.save_config()
    def set_show_objects(self, val):
        self.show_objects = val
        self.scene_changed = True
        self.save_config()
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
                    self.history.append((current, Vec3(0, -130, 22), Vec3(0, 0, 0)))
            self.current_path = path
            self.load_path(self.current_path)
        else:
            self.history = []
            self.current_path = self.root_dir
            self.load_path(self.root_dir)
    def load_path(self, path, initial=False):
        self.current_path = os.path.abspath(path)
        self.path_text.setText(f"Location: {self.current_path}")
        self.buildings = {}
        self.file_orbs = {}
        self.entries = []
        self.window_labels = []
        self.building_labels = []
        for child in self.render.getChildren():
            if child.hasPythonTag("vdm") and child != self.player_glow:
                child.removeNode()
        ground = self.create_ground()
        if self.history:
            ground.setColor(0.9, 0.18, 0.18, 1)
            ground.setPythonTag("type", "exit_ground")
        else:
            ground.setPythonTag("type", "ground")
        if self.current_path == self.respawn_point:
            self.add_respawn_ring(ground)
        self.add_town_square_outline(ground)
        self.add_glow(ground)
        try:
            entries = os.listdir(path)
            non_hidden = [e for e in entries if not e.startswith('.')]
            hidden = [e for e in entries if e.startswith('.')]
        except Exception as e:
            non_hidden = []
            hidden = []
        if not non_hidden and not (self.show_hidden and hidden):
            self.create_empty()
            if not initial:
                self.announce(os.path.basename(path))
            return
        max_radius = 0
        temp_entries = []
        for name in non_hidden:
            full_path = os.path.join(path, name)
            if os.path.isdir(full_path):
                total_size = self.get_size(full_path)
                try:
                    sub = [f for f in os.listdir(full_path) if not f.startswith('.')]
                    num_items = len(sub)
                    average_size = total_size / max(1, num_items)
                except:
                    num_items = 2
                    average_size = 0
                base_width = 30 + min(70, math.sqrt(total_size / 1024.0) * 2)
                base_depth = 30 + min(70, math.sqrt(average_size / 1024.0) * 2)
                r = math.sqrt((base_width / 2) ** 2 + (base_depth / 2) ** 2)
                max_radius = max(max_radius, r)
                temp_entries.append({'name': name, 'full_path': full_path, 'type': 'dir', 'base_width': base_width, 'base_depth': base_depth})
            else:
                size = os.path.getsize(full_path) if os.access(full_path, os.R_OK) else 1024
                radius = 8 + min(size / 1e6 * 22, 28)
                max_radius = max(max_radius, radius)
                temp_entries.append({'name': name, 'full_path': full_path, 'type': 'file', 'size': size})
        min_spacing = 2 * max_radius + 20
        num = len(non_hidden)
        if num > 0:
            spacing_from_density = self.spacing * (3 / math.sqrt(num + 2))
        else:
            spacing_from_density = self.spacing * 3
        effective_spacing = max(spacing_from_density, min_spacing)
        positions = self.hex_positions(num, effective_spacing)
        town_center = self.create_town_center(0, 0, path)
        for i, temp in enumerate(temp_entries):
            name = temp['name']
            full_path = temp['full_path']
            x, y = positions[i]
            if temp['type'] == 'dir':
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
                if not self.show_folders:
                    building.hide()
            else:
                size = temp['size']
                orb = self.create_file_orb(x, y, 0, name, full_path, size)
                if not self.show_files:
                    orb.hide()
        if self.show_hidden:
            hidden_positions = self.hex_positions(len(hidden), spacing=self.spacing * 1.5)
            for i, name in enumerate(hidden):
                full_path = os.path.join(path, name)
                hx, hy = hidden_positions[i]
                hz = self.max_height + 50 + (i % 5) * 10
                star = self.create_star(hx, hy, hz, name, full_path)
                if not self.show_hidden:
                    star.hide()
        for name in non_hidden:
            full_path = os.path.join(self.current_path, name)
            if name in self.buildings:
                node = self.buildings[name]
                typ = 'dir'
                size = 0
            elif name in self.file_orbs:
                node = self.file_orbs[name]
                typ = 'file'
                size = self.get_size(full_path)
            else:
                continue
            try:
                mod_time = os.path.getmtime(full_path)
            except:
                mod_time = 0
            self.entries.append({'name': name, 'full_path': full_path, 'node': node, 'type': typ, 'mod_time': mod_time, 'size': size})
        self.entries.append({'name': 'Town Center', 'full_path': path, 'node': town_center, 'type': 'town_center', 'mod_time': 0, 'size': 0})
        self.apply_sort()
        self.update_labels_visibility()
        self.update_label_positions()
        self.update_player_selected()
        if self.select_all:
            self.set_select_all(True)
        if not initial:
            self.announce(os.path.basename(path))
    def create_town_center(self, x, y, path):
        name = os.path.basename(path) or "Root"
        building = self.render.attachNewNode("town_center")
        building.setPos(x, y, 0)
        building.setPythonTag("vdm", True)
        building.setPythonTag("full_path", path)
        building.setPythonTag("type", "town_center")
        building.setPythonTag("height", 0)
        label = TextNode("label")
        label.setText(name)
        label.setAlign(TextNode.ACenter)
        label.setWordwrap(2.5)
        label.setShadow(0.05, 0.05)
        label.setShadowColor(0, 0, 0, 1)
        np = building.attachNewNode(label)
        np.setPos(0, 0, 5)
        np.setScale(20)
        np.setBillboardPointEye()
        label.setTextColor(1, 1, 1, 1)
        np.hide()
        self.building_labels.append(np)
        return building
    def hex_positions(self, count, spacing):
        positions = []
        if count == 0:
            return positions
        positions.append((0, 0))
        pos_count = 1
        layer = 1
        while pos_count < count:
            for side in range(6):
                for step in range(layer):
                    angle = math.radians(60 * side)
                    dx = math.cos(angle) * spacing * layer
                    dy = math.sin(angle) * spacing * layer
                    offset = step * spacing
                    off_angle = angle + math.radians(60)
                    ox = math.cos(off_angle) * offset
                    oy = math.sin(off_angle) * offset
                    positions.append((dx + ox, dy + oy))
                    pos_count += 1
                    if pos_count >= count:
                        return positions
            layer += 1
        return positions
    def create_ground(self):
        ground = self.render.attachNewNode("ground")
        ground.setPythonTag("vdm", True)
        ground.setCollideMask(BitMask32.bit(0))
        coll_node = CollisionNode('ground_coll')
        coll_plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        coll_node.addSolid(coll_plane)
        coll_node.setFromCollideMask(BitMask32.allOff())
        coll_node.setIntoCollideMask(BitMask32.bit(0))
        ground.attachNewNode(coll_node)
        return ground
    def add_town_square_outline(self, ground):
        lines = LineSegs()
        lines.setThickness(10)
        lines.setColor(0, 1, 0, 1) # Green for town square
        segs = 50
        radius = 100 * (4/3) # 1/3 larger
        rot_offset = math.radians(90)
        for i in range(segs):
            angle = 2 * math.pi * i / segs + rot_offset
            lines.moveTo(math.cos(angle) * radius, math.sin(angle) * radius, 0.1)
            next_angle = 2 * math.pi * (i + 1) / segs + rot_offset
            lines.drawTo(math.cos(next_angle) * radius, math.sin(next_angle) * radius, 0.1)
        ground.attachNewNode(lines.create())
    def add_respawn_ring(self, ground):
        lines = LineSegs()
        lines.setThickness(5)
        lines.setColor(*self.respawn_color)
        segs = 50
        radius = 50
        for i in range(segs):
            angle = 2 * math.pi * i / segs
            lines.moveTo(math.cos(angle) * radius, math.sin(angle) * radius, 0.1)
            next_angle = 2 * math.pi * (i + 1) / segs
            lines.drawTo(math.cos(next_angle) * radius, math.sin(next_angle) * radius, 0.1)
        ground.attachNewNode(lines.create())
    def add_glow(self, ground):
        if self.glow_color is None:
            hue = (hash(self.current_path) % 360) / 360.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.8)
        else:
            r, g, b = self.glow_color
        pl = PointLight('glow')
        pl.setColor(Vec4(r * self.glow_intensity, g * self.glow_intensity, b * self.glow_intensity, 1))
        pl.setAttenuation(Vec3(0, 0, 0.001))
        plnp = ground.attachNewNode(pl)
        plnp.setPos(0, 0, -10)
        self.render.setLight(plnp)
    def create_building(self, x, y, name, path, file_count, dir_count, files):
        total_size = self.get_size(path)
        num_items = file_count + dir_count
        average_size = total_size / max(1, num_items)
        base_width = 30 + min(70, math.sqrt(total_size / 1024.0) * 2)
        base_depth = 30 + min(70, math.sqrt(average_size / 1024.0) * 2)
        height = min(32 + dir_count * 13, self.max_height)
        building = self.render.attachNewNode("building")
        building.setPos(x, y, 0)
        building.setPythonTag("vdm", True)
        building.setPythonTag("full_path", path)
        building.setPythonTag("type", "building")
        building.setPythonTag("height", height)
        color = self.custom_colors.get(path, self.building_color)
        cube = self.make_cube(building, base_width, base_depth, height, color)
        cube.setCollideMask(BitMask32.bit(0))
        windows_per_side = max(1, (file_count + 3) // 4)
        for side in range(4):
            rot = math.radians(side * 90)
            half_size = (base_width / 2 - 8) if side % 2 == 0 else (base_depth / 2 - 8)
            wx = math.cos(rot) * half_size
            wy = math.sin(rot) * half_size
            for i in range(windows_per_side):
                wz = 14 + i * (height - 28) / max(1, windows_per_side - 1) if windows_per_side > 1 else height / 2
                win = building.attachNewNode("window")
                win.setPos(wx, wy, wz)
                self.make_sphere(win, 6.5, self.window_orb_color)
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
        color = self.custom_colors.get(path, (r, g, b, 0.92))
        radius = 8 + min(size / 1e6 * 22, 28)
        self.make_sphere(orb, radius, color)
        coll_node = CollisionNode('orb_coll')
        coll_node.addSolid(CollisionSphere(0, 0, 0, radius * 1.1))
        coll_node.setFromCollideMask(BitMask32.allOff())
        coll_node.setIntoCollideMask(BitMask32.bit(0))
        orb.attachNewNode(coll_node)
        return orb
    def create_star(self, x, y, z, name, path):
        orb = self.render.attachNewNode("star")
        orb.setPos(x, y, z)
        orb.setPythonTag("vdm", True)
        orb.setPythonTag("full_path", path)
        if os.path.isdir(path):
            orb.setPythonTag("type", "star_dir")
        else:
            orb.setPythonTag("type", "star")
        color = self.custom_colors.get(path, self.star_color)
        radius = 4
        self.make_sphere(orb, radius, color)
        coll_node = CollisionNode('star_coll')
        coll_node.addSolid(CollisionSphere(0, 0, 0, radius * 1.1))
        coll_node.setFromCollideMask(BitMask32.allOff())
        coll_node.setIntoCollideMask(BitMask32.bit(0))
        orb.attachNewNode(coll_node)
        return orb
    def create_empty(self):
        txt = TextNode("empty")
        txt.setText("Empty Directory — Click Red Floor to Exit")
        np = self.render.attachNewNode(txt)
        np.setPos(0, 0, 50)
        np.setScale(22)
        txt.setTextColor(*self.other_hud_color)
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
            for root, _, files in os.walk(path, onerror=lambda err: None):
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
        center_ray = CollisionRay()
        center_ray.setFromLens(self.cam.node(), 0, 0)
        center_handler = CollisionHandlerQueue()
        center_node = CollisionNode('centerRay')
        center_np = self.camera.attachNewNode(center_node)
        center_node.addSolid(center_ray)
        center_node.setFromCollideMask(BitMask32.bit(0))
        center_node.setIntoCollideMask(BitMask32.allOff())
        self.cTrav.addCollider(center_np, center_handler)
        self.cTrav.traverse(self.render)
        z_delta = 0
        pitch = self.camera.getP()
        hit_pos = None
        if center_handler.getNumEntries() > 0:
            center_handler.sortEntries()
            entry = center_handler.getEntry(0)
            hit_pos = entry.getSurfacePoint(self.render)
            hit_node = entry.getIntoNodePath()
            while hit_node and not hit_node.hasPythonTag("vdm"):
                hit_node = hit_node.getParent()
            if hit_node and hit_node.hasPythonTag("type"):
                typ = hit_node.getPythonTag("type")
                if typ in ["exit_ground", "ground"]:
                    dist = math.sqrt((hit_pos.x - self.camera.getX())**2 + (hit_pos.y - self.camera.getY())**2)
                    if self.camera.getZ() > 0.001:
                        angle = math.degrees(math.atan(dist / self.camera.getZ()))
                    else:
                        angle = 90
                    if pitch <= self.down_pitch_threshold:
                        z_delta = -self.z_speed * dt
        if pitch >= self.up_pitch_threshold:
            z_delta = self.z_speed * dt
        if not self.pause_z:
            if self.just_toggled_pause_z and z_delta <0:
                z_delta = 0
            self.camera.setZ(max(self.player_height, self.camera.getZ() + z_delta))
        self.just_toggled_pause_z = False
        center_np.removeNode()
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
                center_ray.setFromLens(self.cam.node(), 0, 0)
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
                dir_vec = self.camera.getQuat().getForward()
                dir_vec.z = 0
                if dir_vec.lengthSquared() == 0:
                    dir_vec = Vec3(0, 1, 0)
                else:
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
        if self.keys["jump"]:
            if self.pause_z:
                if not self.jumping:
                    self.start_spring_jump()
            else:
                self.camera.setZ(self.camera.getZ() + self.z_speed * 4 / 3 * dt)
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
            if self.mouseWatcherNode.hasMouse():
                mpos = self.mouseWatcherNode.getMouse()
                self.picker_ray.setFromLens(self.cam.node(), mpos.getX(), mpos.getY())
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
        if self.selected_node != self.previous_selected:
            if self.previous_selected:
                typ_prev = self.previous_selected.getPythonTag("type")
                if typ_prev == "menu_option":
                    self.previous_selected.getParent().setColorScale(1, 1, 1, 1)
                else:
                    self.previous_selected.setColorScale(1, 1, 1, 1)
            if self.selected_node:
                typ = self.selected_node.getPythonTag("type")
                if typ != "player_glow":
                    if typ == "menu_option":
                        self.selected_node.getParent().setColorScale(2.3, 1.9, 1.2, 1)
                    else:
                        self.selected_node.setColorScale(2.3, 1.9, 1.2, 1)
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
                elif typ == "player_glow":
                    self.target_text.setText("Current Directory")
                elif typ == "menu_option":
                    self.target_text.setText(self.selected_node.getParent().getName())
                else:
                    self.target_text.setText("")
            else:
                self.target_text.setText("")
            self.previous_selected = self.selected_node
        new_label_at_top = self.camera.getZ() >= 70
        if new_label_at_top != self.label_at_top:
            self.label_at_top = new_label_at_top
            self.update_label_positions()
        self.player_glow.setX(self.camera.getX())
        self.player_glow.setY(self.camera.getY())
        center = Point3(0, 0, 0)
        dist = (self.camera.getPos() - center).length()
        hsv = colorsys.rgb_to_hsv(*self.background_color[:3])
        beacon_color_full = (1,1,1,1) if hsv[2] < 0.5 else (0,0,0,1)
        beacon_color_dim = (beacon_color_full[0]*0.3, beacon_color_full[1]*0.3, beacon_color_full[2]*0.3, beacon_color_full[3]*0.5)
        if dist > 300:
            if not hasattr(self, 'town_beacon') or self.town_beacon.isHidden():
                self.town_beacon = self.render.attachNewNode("town_beacon")
                lines = LineSegs()
                lines.setThickness(5)
                lines.setColor(*beacon_color_full)
                lines.moveTo(0,0,0)
                lines.drawTo(0,0,1000)
                self.town_beacon.attachNewNode(lines.create())
            self.town_beacon.getChild(0).setColor(*beacon_color_full)
            self.town_beacon.show()
        elif dist > 50:
            if not hasattr(self, 'town_beacon') or self.town_beacon.isHidden():
                self.town_beacon = self.render.attachNewNode("town_beacon")
                lines = LineSegs()
                lines.setThickness(5)
                lines.setColor(*beacon_color_dim)
                lines.moveTo(0,0,0)
                lines.drawTo(0,0,1000)
                self.town_beacon.attachNewNode(lines.create())
            self.town_beacon.getChild(0).setColor(*beacon_color_dim)
            self.town_beacon.show()
        else:
            if hasattr(self, 'town_beacon'):
                self.town_beacon.hide()
        if hit_pos:
            self.aim_text.setText(f" {hit_pos} ")
        else:
            self.aim_text.setText("Pointer: Sky")
        active_keys = []
        if self.keys["forward"]: active_keys.append("W")
        if self.keys["backward"]: active_keys.append("S")
        if self.keys["left"]: active_keys.append("A")
        if self.keys["right"]: active_keys.append("D")
        active_keys = active_keys[:4]
        self.keys_text.setText("Keys: " + " ".join(active_keys))
        return Task.cont
    def update_label_positions(self):
        for np in self.building_labels:
            building = np.getParent()
            height = building.getPythonTag("height")
            np.setZ(height + 28 if self.label_at_top else 5)
app = DataWalk()
app.run()
