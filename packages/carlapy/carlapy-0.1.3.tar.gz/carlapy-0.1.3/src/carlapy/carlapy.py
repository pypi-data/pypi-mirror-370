import warnings
warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API",
    category=UserWarning
)

import io
import math
import random
import sys
import time
import carla
import click
import typer
from typing import Optional, Annotated
from . import utils, carla_utils, carla_game
import numpy as np
from pathlib import Path
import autonomous_proto
from rosbags.rosbag2 import Writer
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.stores.ros2_humble import (
    std_msgs__msg__UInt8MultiArray as UInt8MultiArray,
    std_msgs__msg__MultiArrayLayout as MultiArrayLayout,
    std_msgs__msg__MultiArrayDimension as MultiArrayDimension,
)

client: carla.Client = carla.Client('127.0.0.1', 2000)
app = typer.Typer(invoke_without_command=True)

@app.callback()
def main_callback(
        ctx: typer.Context,
        host: Annotated[str, typer.Option(help='CARLA host')] = '127.0.0.1',
        port: Annotated[int, typer.Option(help='CARLA port')] = 2000,
        timeout: Annotated[float, typer.Option(help='CARLA timeout')] = 1.0,
):
    global client
    client = carla.Client(host, port)
    client.set_timeout(timeout)
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())

@app.command(name='print_actors', help='Print actors tree containing pattern')
def print_actors(pattern: Annotated[str, typer.Argument(help='pattern match the role_name or type_id')] = 'vehicle'):
    global client
    client.get_world().wait_for_tick()
    actors = client.get_world().get_actors()
    carla_utils.print_actors_tree(actors, pattern)

@app.command(name='print_actor', help='Print actor specified by actor id or role_name')
def print_actor(
        actor_id: Annotated[str, typer.Argument(help='Actor id or role_name')],
        loop: Annotated[bool, typer.Option(help='Loop mode')] = False,
):
    global client
    client.get_world().wait_for_tick()
    actor = carla_utils.get_actor(actor_id, client)
    if actor is None:
        print('Actor not found')
        return
    if not loop:
        carla_utils.print_actor(actor, client)
        return
    utils.set_stdout_nonblocking()
    while True:
        snapshot = client.get_world().wait_for_tick()
        origin_stdout = sys.stdout
        buffer = io.StringIO()
        sys.stdout = buffer
        sys.stdout.write("\x1b[H\x1b[2J\x1b[3J")
        sys.stdout.flush()
        print('CARLA Frame: ', snapshot.frame)
        carla_utils.print_actor(actor,
                                client,
                                print_parent = False,
                                print_sons = False,
                                print_attributes = False,
                                print_location = True,
                                print_rotation = True,
                                print_move = True,
                                print_boundbox = False,
                                print_vehicle_wheel = True,
                                print_vehicle_control = False,
                                print_vehicle_physics = False,
                                )
        sys.stdout = origin_stdout
        sys.stdout.write(buffer.getvalue())

@app.command(name='destroy_actor', help='Destroy actor with the id')
def destroy_actor(actor_id: Annotated[str, typer.Argument(help='The actor id or role_name of the actor to destroy.')]):
    global client
    client.get_world().wait_for_tick()
    carla_utils.destroy_actor(actor_id, client)

@app.command(name='available_maps', help='Print available maps')
def available_maps():
    global client
    client.get_world().wait_for_tick()
    print(*client.get_available_maps(), sep='\n')
    current_map = client.get_world().get_map()
    print()
    print('Current Map: ', current_map)

@app.command(name='change_map', help='Change map')
def change_map(map_name: Annotated[str, typer.Argument(help='The new map name.')] = None):
    global client
    client.set_timeout(10)
    client.get_world().wait_for_tick()
    current_map = client.get_world().get_map()
    print('Current Map:', current_map)
    if map_name is not None:
        client.load_world_if_different(map_name, False)
        print('Change map to:', map_name)
        return
    maps = client.get_available_maps()
    for i, m in enumerate(maps):
        print('{}:'.format(i), m)
    while True:
        index = input('index of map: ')
        try:
            index = int(index)
            if 0 <= index < len(maps):
                break
        except ValueError:
            pass
    client.load_world_if_different(maps[index], False)
    print('Change map to:', maps[index])


@app.command(name='available_bp', help='Print available blueprints')
def available_bp(pattern: Annotated[Optional[str], typer.Option(help="pattern match the blueprint type")] = '*'):
    global client
    client.get_world().wait_for_tick()
    if not pattern.startswith('*'):
        pattern = '*' + pattern
    if not pattern.endswith('*'):
        pattern = pattern + '*'
    print(*client.get_world().get_blueprint_library().filter(pattern), sep='\n')

@app.command(name='print_settings', help='Print current settings')
def print_settings():
    global client
    client.get_world().wait_for_tick()
    settings = client.get_world().get_settings()
    carla_utils.print_settings(settings)

@app.command(name='move', help='Move target to ...')
def move(
        actor_id: Annotated[str, typer.Argument(help='id of the actor to be move')] = 'spectator',
        to: Annotated[str, typer.Option(help='id of the actor move to')] = None,
        x: Annotated[float, typer.Option()] = None,
        y: Annotated[float, typer.Option()] = None,
        z: Annotated[float, typer.Option()] = None,
        roll: Annotated[float, typer.Option(help='degree')] = None,
        pitch: Annotated[float, typer.Option(help='degree')] = None,
        yaw: Annotated[float, typer.Option(help='degree')] = None,
):
    global client
    client.get_world().wait_for_tick()
    carla_utils.move_to(client, actor_id, to, x, y, z, roll, pitch, yaw)

@app.command(name='spy', help='Spy the specified actor')
def spy(actor_id: Annotated[str, typer.Argument(help='id of target actor')] = 'hero'):
    global client
    client.get_world().wait_for_tick()
    cg = carla_game.GUI(actor_id, client)
    cg.run()

@app.command(name='follow', help='Follow the spectator to actor')
def follow(
        actor_id: Annotated[str, typer.Argument(help='id of target actor')] = 'hero',
        x: Annotated[float, typer.Option()] = None,
        y: Annotated[float, typer.Option()] = None,
        z: Annotated[float, typer.Option()] = None,
        roll: Annotated[float, typer.Option(help='degree')] = None,
        pitch: Annotated[float, typer.Option(help='degree')] = None,
        yaw: Annotated[float, typer.Option(help='degree')] = None,
):
    global client
    client.get_world().wait_for_tick()
    actor = carla_utils.get_actor(actor_id, client)
    if actor is None or not actor.is_alive:
        print('Actor not found')
        return
    dummy_bp = carla_utils.get_blueprint('sensor.other.collision', client)
    dummy_bp.set_attribute('role_name', 'dummy_follow')
    dummy_transform = carla_utils.get_transform(x, y, z, roll, pitch, yaw)
    if dummy_transform is None and math.isfinite(actor.bounding_box.location.x):
        dummy_transform = carla.Transform(
            carla.Location(x=-actor.bounding_box.extent.x * 1.88, z=actor.bounding_box.extent.z * 3.76),
            carla.Rotation(pitch=-20)
        )
    dummy = carla_utils.spawn_actor(client, dummy_bp, dummy_transform, actor, carla.AttachmentType.Rigid)
    def stop():
        if dummy is not None and dummy.is_alive:
            dummy.destroy()
    world = client.get_world()
    world.wait_for_tick(1)
    spectator = world.get_spectator()
    try:
        while dummy.is_alive:
            world.wait_for_tick(1)
            spectator.set_transform(dummy.get_transform())
    except KeyboardInterrupt:
        stop()
    except RuntimeError:
        stop()
    finally:
        stop()

@app.command(name='pose_debug', help='Pose debug')
def pose_debug():
    global client
    client.get_world().wait_for_tick()
    spectator = carla_utils.get_actor('spectator', client)
    gnss_bp = carla_utils.get_blueprint('sensor.other.gnss', client)
    imu_bp = carla_utils.get_blueprint('sensor.other.imu', client)
    gnss: carla.Sensor = carla_utils.spawn_actor(client, gnss_bp, parent=spectator)
    imu: carla.Sensor = carla_utils.spawn_actor(client, imu_bp, parent=spectator)
    data = {'gnss': None, 'imu': None}
    gnss.listen(lambda e: data.update({'gnss': e}))
    imu.listen(lambda e: data.update({'imu': e}))
    try:
        while True:
            client.get_world().wait_for_tick()
            gnss_data: carla.GnssMeasurement = data['gnss']
            imu_data: carla.IMUMeasurement = data['imu']
            if gnss_data is None or imu_data is None:
                continue
            print('Gnss:')
            print('  Frame  :', gnss_data.frame)
            print('  lat    :', gnss_data.latitude)
            print('  lon    :', gnss_data.longitude)
            print('  alt    :', gnss_data.altitude)
            print('  X      :', gnss_data.transform.location.x)
            print('  Y      :', gnss_data.transform.location.y)
            print('  Z      :', gnss_data.transform.location.z)
            print('  roll   :', gnss_data.transform.rotation.roll)
            print('  pitch  :', gnss_data.transform.rotation.pitch)
            print('  yaw    :', gnss_data.transform.rotation.yaw)
            print('Imu:')
            print('  Frame  :', imu_data.frame)
            print('  compass:', math.degrees(imu_data.compass))
            print('  gyro.x :', imu_data.gyroscope.x)
            print('  gyro.y :', imu_data.gyroscope.y)
            print('  gyro.z :', imu_data.gyroscope.z)
            print('  acc.x  :', imu_data.accelerometer.x)
            print('  acc.y  :', imu_data.accelerometer.y)
            print('  acc.z  :', imu_data.accelerometer.z)
            print()
    finally:
        gnss.stop()
        imu.stop()
        carla_utils.destroy_actor(gnss.id, client)
        carla_utils.destroy_actor(imu.id, client)

@app.command(name='spawn_points', help='Print available spawn points')
def spawn_points():
    global client
    client.get_world().wait_for_tick()
    print(*client.get_world().get_map().get_spawn_points(), sep='\n')

@app.command(name='reset_to_spawn', help='Reset actor to spawn points')
def reset_to_spawn(actor_id: Annotated[str, typer.Argument(help='Actor id or role_name')] = 'hero'):
    global client
    client.get_world().wait_for_tick()
    actor = carla_utils.get_actor(actor_id, client)
    if actor is None:
        print('Actor {} not found'.format(actor_id))
        return
    points = client.get_world().get_map().get_spawn_points()
    if len(points) == 0:
        print('No spawn points')
        return
    for i, p in enumerate(points):
        print('{:>2d}. {}'.format(i, p))
    while True:
        index = input('index of spawn point: ')
        try:
            index = int(index)
            if 0 <= index < len(points):
                break
        except ValueError:
            pass
    actor.set_transform(points[index])
    client.get_world().get_spectator().set_transform(points[index])
    print('Reset actor to:', points[index])

@app.command(name='overlook', help='Overlook the whole map')
def overlook():
    global client
    client.get_world().wait_for_tick()
    waypoints = client.get_world().get_map().generate_waypoints(1)
    x_min = min(w.transform.location.x for w in waypoints)
    x_max = max(w.transform.location.x for w in waypoints)
    y_min = min(w.transform.location.y for w in waypoints)
    y_max = max(w.transform.location.y for w in waypoints)
    x_center = (x_max + x_min) / 2
    y_center = (y_max + y_min) / 2
    x_range = x_max - x_min
    y_range = y_max - y_min
    z = max(x_range, y_range)
    yaw = 0 if x_range < y_range else -90
    spectator = carla_utils.get_actor('spectator', client)
    spectator.set_transform(carla.Transform(carla.Location(x_center, y_center, z), carla.Rotation(pitch=-90, yaw=yaw)))
    print('x_min:', x_min)
    print('x_max:', x_max)
    print('x_center:', x_center)
    print('x_range:', x_range)
    print('y_min:', y_min)
    print('y_max:', y_max)
    print('y_center:', y_center)
    print('y_range:', y_range)
    print('z:', z)

@app.command(name='control_roadnet', help='Generate roadnet for control')
def control_roadnet(
        actor_id: Annotated[str, typer.Argument(help='Actor id or role_name')] = 'spectator',
        interval: Annotated[float, typer.Option] = 0.3,
        slow: Annotated[bool, typer.Option] = False,
        bag: Annotated[str, typer.Option(help='name of bag')] = None,
):
    global client
    client.get_world().wait_for_tick()
    debug = client.get_world().debug
    spectator = client.get_world().get_spectator()
    world_map = client.get_world().get_map()
    actor = carla_utils.get_actor(actor_id, client)
    if actor is None:
        print('Actor not found')
        return
    start_point = world_map.get_waypoint(actor.get_location())
    if start_point is None:
        print('start point not found')
        return
    roadnet = []

    colors = [
        carla.Color(255, 0, 0),
        carla.Color(0, 255, 0),
        carla.Color(0, 0, 255),
    ]
    colors_str = ['red', 'green', 'blue']

    def draw_point(p: carla.Waypoint, z = 1.0, size: float = 0.1, c = carla.Color(0, 0, 0), lifetime = 0):
        t = p.transform.location
        t.z += z
        debug.draw_point(t, size=size, color=c, life_time=lifetime)
    def get_line(s: carla.Waypoint):
        c = s
        points = [c]
        while True:
            w = c.next(interval)
            if len(w) != 1:
                return points
            c = w[0]
            points.append(c)
    def move(p: carla.Waypoint):
        draw_point(p, size=0.3)
        t = p.transform
        t.location.z += 2
        t.rotation.pitch = -20
        t.location.x -= 2 * math.cos(math.radians(t.rotation.yaw))
        t.location.y -= 2 * math.sin(math.radians(t.rotation.yaw))
        spectator.set_transform(t)
        if slow:
            input('press enter to add current point')
        else:
            time.sleep(0.02)

    try:
        while True:
            next_points = start_point.next(interval)
            if len(next_points) == 0 or len(next_points) > 2:
                print('next_points(roads) size:', len(next_points))
                break
            if len(next_points) == 1:
                move(next_points[0])
                start_point = next_points[0]
                roadnet.append(start_point)
                continue
            for i, point in enumerate(next_points):
                print('{}:'.format(i), colors_str[i])
                for p in get_line(point):
                    draw_point(p, z=1.2, c=colors[i], lifetime=10)

            index = input('index of selected: ')
            try:
                index = int(index)
                if 0 <= index < len(next_points):
                    move(next_points[index])
                    start_point = next_points[index]
                    roadnet.append(start_point)
            except ValueError:
                pass
            move(start_point)
    except KeyboardInterrupt:
        print('keyboard interrupt')

    print('collected roadnet points size:', len(roadnet))
    def get_interval(a: carla.Waypoint, b: carla.Waypoint):
        x = a.transform.location.x - b.transform.location.x
        y = a.transform.location.y - b.transform.location.y
        return math.sqrt(x * x + y * y)
    min_interval = min(get_interval(a, b) for a, b in zip(roadnet, roadnet[1:]))
    max_interval = max(get_interval(a, b) for a, b in zip(roadnet, roadnet[1:]))
    print('min_interval:', min_interval)
    print('max_interval:', max_interval)

    coordinates = [world_map.transform_to_geolocation(t.transform.location) for t in roadnet]
    navs = []
    nav = autonomous_proto.Navigation()
    nav.header.info.count = 0
    nav.header.info.module_name = autonomous_proto.MessageInfoModuleNameValue.undefined
    nav.header.info.topic_name = autonomous_proto.MessageInfoTopicNameValue.undefined
    for coordinate in coordinates:
        nav.header.info.count += 1
        nav.position.lat = coordinate.latitude
        nav.position.lon = coordinate.longitude
        nav.position.alt = coordinate.altitude
        navs.append(nav.SerializeToString())

    if bag is None or len(bag) == 0:
        bag = input('bag name: ')
    bag_path = Path(bag)
    with Writer(bag_path, version=8) as writer:
        type_store = get_typestore(Stores.ROS2_HUMBLE)
        topic = 'navigation'
        msg_type = UInt8MultiArray.__msgtype__
        connection = writer.add_connection(topic, msg_type, typestore=type_store)
        timestamp = int(time.time() * 1e9)
        for n in navs:
            timestamp += 20000000
            data = np.frombuffer(n, dtype=np.uint8)
            dims = [MultiArrayDimension(label='', size=data.size, stride=1)]
            layout = MultiArrayLayout(dim=dims, data_offset=0)
            message = UInt8MultiArray(layout=layout, data=data)
            writer.write(connection, timestamp, type_store.serialize_cdr(message, msg_type))


def main():
    try:
        app()
    except Exception as err:
        print(err)

# @app.command(name='test')
# def test():
#     global client
#     client.get_world().wait_for_tick()

if __name__ in "__main__":
    try:
        app()
    except RuntimeError as e:
        print(e)
