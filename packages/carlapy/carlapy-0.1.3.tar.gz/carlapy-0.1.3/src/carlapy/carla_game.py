"""
CarlaPy
S[pressed] + arrow keys: adjust view position relative to target
X[pressed] + arrow keys: adjust view pitch and yaw
T: change attachment type
"""

import math
import weakref
import carla
import threading
import numpy as np
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from . import carla_utils


class HelpText:
    def __init__(self, width, height):
        lines = __doc__.strip('\n').split('\n')
        font_size = 24
        line_space = 30
        padding_up = 30
        padding_down = 20
        padding_left = 20
        padding_right = 20
        try:
            font = pygame.font.SysFont("notomono", font_size)
        except RuntimeError:
            print('using default font')
            font = pygame.font.Font(None, font_size)
        text_width = max(font.render(line, True, (255, 255, 255)).get_width() for line in lines)
        text_height = line_space * (len(lines) - 1) + font_size
        text_surface = pygame.Surface((text_width, text_height))
        for i, line in enumerate(lines):
            text_surface.blit(font.render(line, True, (255, 255, 255)), (0, i * line_space))
        surface_dim = (padding_left + padding_right + text_width, padding_up + padding_down + text_height)
        self.surface = pygame.Surface(surface_dim)
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_surface, (padding_left, padding_up))
        self.surface.set_alpha(200)
        self.pos = (max((width - surface_dim[0]) // 2, 0), max((height - surface_dim[1]) // 2, 0))
        self.show = False

    def toggle(self):
        self.show = not self.show

    def render(self, target_surface):
        if self.show:
            target_surface.blit(self.surface, self.pos)

class SensorManager:
    def __init__(self,
                 parent: carla.Actor,
                 client: carla.Client,
                 view_width,
                 view_height,
                 sensor_update_event,
                 ):
        self.stop_event = threading.Event()
        self.parent = parent
        self.client = client
        self.view_width = view_width
        self.view_height = view_height
        self.sensor_update_event = sensor_update_event
        self.sensor_index = 0
        self.camera_rgb = {
            'pattern': 'sensor.camera.rgb',
            'desc': 'Camera RGB',
            'attributes': {
                'role_name': 'spy_spectator',
                'sensor_tick': 0.04,
                'image_size_x': self.view_width,
                'image_size_y': self.view_height,
                'fov': 90,
            },
            'color_converter': carla.ColorConverter.Raw,
        }
        self.sensors = [
            self.camera_rgb,
        ]
        self.sensor: carla.Sensor | None = None
        self.bp: carla.ActorBlueprint | None = None
        self.transform: carla.Transform = carla.Transform(carla.Location(), carla.Rotation())
        self.attachment: carla.AttachmentType = carla.AttachmentType.Rigid

        self.surface: pygame.Surface | None = None

    def stop(self):
        print('SensorManager: stop')
        self.stop_event.set()
        if self.sensor is not None and self.sensor.is_alive:
            if self.sensor.is_listening:
                self.sensor.stop()
            self.sensor.destroy()
            self.sensor = None

    def move(self, keys):
        if self.attachment != carla.AttachmentType.Rigid:
            print('current attachment type is {}'.format(self.attachment))
            print('move is only available for {}'.format(carla.AttachmentType.Rigid))
            return
        move = 0.1
        degree = 1
        if keys[pygame.K_LSHIFT]:
            move = 0.01
            degree = 0.1
        if keys[pygame.K_s]:
            if keys[pygame.K_UP]:
                self.transform.location.x += move
            if keys[pygame.K_DOWN]:
                self.transform.location.x -= move
            if keys[pygame.K_LEFT]:
                self.transform.location.y -= move
            if keys[pygame.K_RIGHT]:
                self.transform.location.y += move
            if keys[pygame.K_a]:
                self.transform.location.z += move
            if keys[pygame.K_d]:
                self.transform.location.z -= move
        if keys[pygame.K_x]:
            if keys[pygame.K_UP]:
                self.transform.rotation.pitch += degree
            if keys[pygame.K_DOWN]:
                self.transform.rotation.pitch -= degree
            if keys[pygame.K_LEFT]:
                self.transform.rotation.yaw -= degree
            if keys[pygame.K_RIGHT]:
                self.transform.rotation.yaw += degree
        self.sensor.set_transform(self.transform)
        print('Sensor move to:', self.transform)

    def spawn(self):
        if self.sensor is not None and self.sensor.is_alive:
            if self.sensor.is_listening:
                self.sensor.stop()
            self.sensor.destroy()
            self.sensor = None
        if self.sensor_index >= len(self.sensors):
            self.sensor_index = 0
        sensor_data = self.sensors[self.sensor_index]
        self.bp = carla_utils.get_blueprint(sensor_data['pattern'], self.client)
        attributes = sensor_data.get('attributes', {})
        for attr, value in attributes.items():
            self.bp.set_attribute(attr, str(value))
        if math.isfinite(self.parent.bounding_box.location.x):
            self.transform.location.x = -self.parent.bounding_box.extent.x * 1.88
            self.transform.location.z = self.parent.bounding_box.extent.z * 3.76
            self.transform.rotation.pitch = -20
        self.sensor = self.client.get_world().spawn_actor(self.bp, self.transform, self.parent, self.attachment)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda image: SensorManager.callback(weak_self, image))

    @staticmethod
    def callback(weak_self, image):
        self = weak_self()
        if not self:
            return
        if self.stop_event.is_set():
            return
        sensor_data = self.sensors[self.sensor_index]
        if sensor_data.get('color_converter', None) is not None:
            image.convert(sensor_data['color_converter'])
        if self.sensor_index == 0:
            array = np.frombuffer(image.raw_data, dtype=np.uint8)
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            pygame.event.post(pygame.event.Event(self.sensor_update_event))

class CarlaClient:
    def __init__(self, actor_id, client: carla.Client):
        self.client = client
        self.client.get_world().wait_for_tick()
        self.actor = carla_utils.get_actor(actor_id, self.client)
        if self.actor is None:
            raise RuntimeError('Actor {} not found'.format(actor_id))
        if not self.actor.is_alive:
            raise RuntimeError('Actor {} not alive'.format(actor_id))

    def gui_title(self):
        return f"Actor(id={self.actor.id}, role_name={self.actor.attributes.get('role_name', 'None')}, type={self.actor.type_id})"

class GUI:
    def __init__(self, actor_id, client: carla.Client):
        self.stop_event = threading.Event()
        self.logic_width = 800
        self.logic_height = 600
        pygame.init()
        pygame.key.set_repeat(300, 50)
        self.logic_surface = pygame.Surface((self.logic_width, self.logic_height))
        self.w = self.logic_width
        self.h = self.logic_height
        self.ratio = 1.
        self.display = None
        self.init_display()

        self.carla_client = CarlaClient(actor_id, client)
        pygame.display.set_caption(self.carla_client.gui_title())

        self.sensor_update_event = pygame.USEREVENT + 1
        self.sensor_manager = SensorManager(self.carla_client.actor,
                                            client,
                                            self.logic_width,
                                            self.logic_height,
                                            self.sensor_update_event,
                                            )
        self.sensor_manager.spawn()

        self.help_text = HelpText(self.logic_width, self.logic_height)

    def stop(self):
        print('GUI: stop')
        self.stop_event.set()
        self.sensor_manager.stop()

    def init_display(self):
        self.display = pygame.display.set_mode((self.w, self.h),
                                               pygame.DOUBLEBUF |
                                               pygame.HWSURFACE,
                                               )

    # def flip_display(self, surface, destination = (0, 0)):
    #     self.display.blit(surface, destination)
    #     pygame.display.flip()

    # def update_display(self):
    #     self.display.blit(pygame.transform.scale(self.logic_surface, (self.w, self.h)), (0, 0))
    #     pygame.display.flip()

    def resize_display(self, width, height):
        if width < self.w or height < self.h:
            self.ratio = min(width / self.w, height / self.h)
            self.w = int(self.w * self.ratio)
            self.h = int(self.h * self.ratio)
            self.init_display()
            # self.update_display()

    def run(self):
        try:
            while not self.stop_event.is_set():
                event = pygame.event.wait()
                match event.type:
                    case pygame.QUIT:
                        self.stop()
                        break
                    case pygame.VIDEORESIZE:
                        # self.resize_display(event.w, event.h)
                        pass
                    case self.sensor_update_event:
                        if self.sensor_manager.surface is not None:
                            self.display.blit(self.sensor_manager.surface, (0, 0))
                    case pygame.KEYDOWN:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_s] or keys[pygame.K_x]:
                            self.sensor_manager.move(keys)
                        if keys[pygame.K_h]:
                            self.help_text.toggle()
                self.help_text.render(self.display)
                pygame.display.flip()
        except RuntimeError as e:
            print(e)
            self.stop()
        except KeyboardInterrupt:
            self.stop()
