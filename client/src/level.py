import asyncio
import os
import threading
import time
from pathlib import Path

import pygame
import websockets
from camera import Camera
from components.breakable_tile import Breakable_tile
from components.spikes import Spike
from components.text import Text
from connection import update_data
from constants import TILE_H, TILE_W
from exit_door import Exit_door
from other_player import OtherPlayer
from player import Player
from pytmx import util_pygame
from tiles import Tile
from utils.background import Background

other_player = {}
msg = {}
msg_timer = 10
msg_rec_time = 0  # time at which the msg is received


def update_other_player_data(data):
    global msg
    global msg_rec_time
    global other_player

    if data == []:
        print("No Data Received")
        return
    x, y, is_dead, anim = data[0]

    w_w, w_h = pygame.display.get_window_size()
    # if he was revived !
    if other_player.is_dead and not is_dead:
        msg = Text(
            "Other Player Respawned !",
            w_w - 700,
            100,
            10,
            10,
            pygame.display.get_surface(),
            False,
            24,
            pygame.Color(0, 255, 0),
        )
        msg_rec_time = time.time()

    # if he was kileld
    elif not other_player.is_dead and is_dead:
        msg = Text(
            "Other Player has died !",
            w_w - 700,
            100,
            10,
            10,
            pygame.display.get_surface(),
            False,
            24,
            pygame.Color(255, 0, 0),
        )
        msg_rec_time = time.time()

    other_player.rect.x = x
    other_player.rect.y = y
    other_player.is_dead = is_dead
    if anim == other_player.prev_animation:
        return
    else:
        # the `anim` name already contains the "_inverted" string if it is required
        other_player.spritesheet.select_animation(anim, noreset=True)
        # if we simply reassign the name the current_animantion_len is not reassigned


async def tick(player):
    async with websockets.connect("ws://localhost:8765") as ws:
        anim = player.spritesheet.selected_animation
        await update_data(
            ws,
            [player.rect.x, player.rect.y, player.is_dead, anim],
            update_other_player_data,
        )


class Level:
    def __init__(self, surface):

        # PROPS OF LEVEL CLASS
        self.display_surface = surface
        self.has_loaded = False
        self.complete = False
        self.load_map()
        self.setup_level()
        self.init_all_entites()
        self.camera = Camera()

        # for switching scene after winning
        self.last_time = 0
        self.scene_switching_time = 5

        self.player_contact = True

        # Player VERTICAL TOUCH SFX
        self.landSFX = pygame.mixer.Sound(
            Path(__file__).resolve().parent.parent / "assets" / "Sounds" / "land.wav"
        )  # SFX when jump

        # initialised using the map | ? if i declare them here they arnt global ? wtf
        # self.tiles = pygame.sprite.Group()
        # self.player = pygame.sprite.GroupSingle()
        # self.spikes = pygame.sprite.Group()
        # self.breakable_tiles = pygame.sprite.Group()
        # self.exit_door = pygame.sprite.GroupSingle()
        # self.entities = [self.tiles, self.breakable_tiles]

    def reset(self):
        self.setup_level()
        self.background.reset()
        self.camera = Camera()

    def load_map(self):
        if os.getcwd().endswith("\\client\\src"):
            # changing cwd because all asset paths are set relative to ./Levels
            os.chdir("./Levels")

        self.tmx_data = util_pygame.load_pygame("./1.tmx")
        self.has_loaded = True

        # parallax background
        bg_layer_names = ["bg_0", "bg_1"]  # +bg_2
        bg_layers = [self.tmx_data.get_layer_by_name(i) for i in bg_layer_names]
        bg_layers_speeds = [layer.properties.get("speed") for layer in bg_layers]
        self.background = Background(bg_layers, bg_layers_speeds)
        # os.chdir("./..")  # reseting the cwd

    # CLASS METHOD TO IDENTIFY REQ TILES FOR LEVEL
    def setup_level(self):
        global other_player

        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        # Tile Layer 1
        tiles_layer = self.tmx_data.get_layer_by_name("Tile Layer 1")
        for x, y, surf in tiles_layer.tiles():
            # pos = (x * surf.get_width(), y * surf.get_height())  # 16 by 16 tiles
            pos = (x * TILE_W, y * TILE_H)  # 16 by 16 tiles
            tile = Tile(pos, surf, self.tiles)
            self.tiles.add(tile)

        # player_layer = self.tmx_data.get_layer_by_name("Player")
        # for obj in player_layer:
        obj = self.tmx_data.get_object_by_id(2)  # start point object
        pos = (obj.x, obj.y)
        path = obj.properties.get("spritesheet")
        p = Player(pos, path)
        self.player.add(p)
        # OtherPlayer
        other_player = OtherPlayer((0, 0), path)

    def init_all_entites(self):
        self.init_spikes()
        self.init_breakable_tiles()
        self.init_exit_door()

        self.entities = [self.spikes, self.breakable_tiles, self.exit_door]
        # init escape door

    def init_exit_door(self):
        self.exit_door = pygame.sprite.GroupSingle()
        obj = self.tmx_data.get_object_by_id(3)  # start point object
        pos = (obj.x * 2, obj.y * 2)
        print("pos is ", {"pos": pos})
        path = obj.properties.get("sprite")
        surf = pygame.image.load(path).convert_alpha()
        Exit_door(pos, surf, self.exit_door)

    def init_spikes(self):
        self.spikes = pygame.sprite.Group()
        spike_layer = self.tmx_data.get_layer_by_name("Spikes")
        for x, y, surf in spike_layer.tiles():
            pos = (x * TILE_W, y * TILE_H)
            Spike(pos, surf, self.spikes)

    def init_breakable_tiles(self):
        self.breakable_tiles = pygame.sprite.Group()
        breakable_tiles_layer = self.tmx_data.get_layer_by_name("Breakable Tiles")
        for x, y, surf in breakable_tiles_layer.tiles():
            pos = (x * TILE_W, y * TILE_H)
            Breakable_tile(pos, surf, self.breakable_tiles)

    # LEVEL CLASS METHOD - HORIZONTAL COLLISIONS
    def horizontal_movement_collision(self):

        # DECLARE PLAYER SPRITE
        # HANDLE PLAYER MOTION
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        # ITERATE THRU EVERY SPRITE
        # CHECK IF PLAYER RECT COLLIDES WITH SPRITE RECT
        # REQ CHECKING FOR LEFT OR RIGHT SURFACE COLLISION
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right

                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left

    # LEVEL CLASS METHOD - VERTICAL COLLISIONS
    def vertical_movement_collision(self):

        # DECLARE PLAYER SPRITE
        # APPLY GRAVITY i.e Y-AXIS MOVEMENT INIT to PLAYER SPRITE
        player = self.player.sprite
        player.apply_gravity()

        # ITERATE THRU EVERY SPRITE
        # CHECK IF PLAYER RECT COLLIDES WITH SPRITE RECT
        # REQ CHECKING FOR TOP OR BOTTOM SURFACE COLLISION
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.jump_limit = 0
                    player.in_air_after_jump = False
                    player.spritesheet.unlock_animation()

                    # PLAY SFX
                    if self.player_contact == True:
                        self.landSFX.play()
                        self.player_contact = False

                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

                    # PLAY SFX
                    if self.player_contact == True:
                        self.landSFX.play()
                        self.player_contact = False

            elif abs(player.direction.y) > 2:
                self.player_contact = True

    # CLASS METHOD FOR DEATH AND RESPAWN
    def death(self):
        player = self.player.sprite

        # TODO NOTIFY OTHER PLAYER OF DEATH
        # CONDITIONAL STATEMENT TO CHECK IF PLAYER IS OUT-OF-BOUNDS IN Y-AXIS
        if player.rect.y > 1500:
            return True

    def render(self):
        if self.complete:
            return
        # background
        self.background.render(self.display_surface)

        # drawing tiles relative to camera
        for tile in self.tiles.sprites():
            # tiles are looped rowwise
            if (
                tile.rect.x >= self.camera.pos.x - self.camera.offset
                and tile.rect.x < (self.camera.pos.x + self.camera.draw_distance.x)
            ):
                pos = pygame.Vector2(tile.rect.x, tile.rect.y)
                rel_pos = self.camera.get_relative_coors(pos)
                rel_rect = tile.image.get_rect(topleft=rel_pos)
                self.display_surface.blit(tile.image, rel_rect)

        # drawing player relative to camera
        player = self.player.sprite
        player.render(self.display_surface, self.camera)

        # rendering the other_player
        global other_player
        other_player.render(self.display_surface, self.camera)

        # Entities
        for grp in self.entities:
            for item in grp:
                item.render(self.display_surface, self.camera, self.player.sprite)

        # messages
        if msg_rec_time != 0:
            msg.render()

    def update(self, events_list):
        if self.player.sprite.has_won:
            if time.time() - self.last_time > self.scene_switching_time:
                self.complete = True
                return
        # if the player has won !
        w_w, w_h = pygame.display.get_window_size()
        global msg_rec_time
        global msg_timer
        global msg
        if self.player.sprite.has_won and not self.complete:
            # self.player.sprite.has_won = False
            self.last_time = time.time()
            self.timer_setup = True
            msg = Text(
                "You Won !",
                w_w / 2,
                w_h / 2,
                10,
                10,
                pygame.display.get_surface(),
                False,
                70,
                pygame.Color(0, 0, 255),
            )
            return

        # Background
        self.background.update(self.camera.pos.x)

        # Players
        other_player.update()
        self.player.update(events_list)
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.camera.follow_player(self.player.sprite)

        # Entities
        for grp in self.entities:
            for item in grp:
                # if item.type == "spike"
                item.update(events_list, self.player.sprite)

        # sending and receiving player positions
        self.thread = threading.Thread(
            target=asyncio.get_event_loop().run_until_complete,
            args=[tick(self.player.sprite)],
        )
        self.thread.daemon = True
        self.thread.start()

        if msg_rec_time != 0 and time.time() - msg_rec_time > msg_timer:
            msg.text = ""
            msg_rec_time = 0
