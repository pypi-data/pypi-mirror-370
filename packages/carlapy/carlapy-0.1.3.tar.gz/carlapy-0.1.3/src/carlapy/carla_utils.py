import math
import time
import carla


def get_actors(client: carla.Client) -> carla.ActorList:
    return client.get_world().get_actors()

def get_actor(actor_id, client: carla.Client) -> carla.Actor | None:
    if actor_id is None:
        return None
    try:
        actor_id = int(actor_id)
    except ValueError:
        pass
    try:
        if isinstance(actor_id, int):
            return client.get_world().get_actor(actor_id)
        if len(actor_id) == 0:
            return None
        actors = get_actors(client)
        for actor in actors:
            if actor.attributes.get('role_name', '') == actor_id:
                return actor
            if actor.type_id == actor_id:
                return actor
    except RuntimeError:
        pass
    return None

def is_vehicle(actor: carla.Actor) -> bool:
    return 'vehicle' in actor.type_id

def is_sensor(actor: carla.Actor) -> bool:
    return 'sensor' in actor.type_id

def print_simple_actor(actor: carla.Actor, prefix: str = '', max_len = 0):
    print(prefix, f"Actor(id={actor.id}, role_name={actor.attributes.get('role_name', 'None'):<{max_len}}, type={actor.type_id})", sep='')

def print_actor_basic(
        actor: carla.Actor,
        client: carla.Client,
        prefix: str = '',
        print_parent: bool = True,
        print_sons: bool = True,
        print_attributes: bool = True,
        print_location: bool = True,
        print_rotation: bool = True,
):
    actors = get_actors(client)
    max_len = max([len(a.attributes.get('role_name', '')) for a in actors])
    print_simple_actor(actor, prefix=prefix, max_len=max_len)
    if print_parent and actor.parent is not None:
        print_actor_basic(actor.parent,
                          client,
                          prefix + 'Parent: ',
                          print_parent = False,
                          print_sons = is_vehicle(actor.parent),
                          print_attributes = False,
                          print_location = False,
                          print_rotation = False,
                          )
    if print_sons:
        for a in actors:
            if a.parent is None or a.parent.id != actor.id:
                continue
            print_actor_basic(a,
                              client,
                              prefix + 'Son: ',
                              print_parent = False,
                              print_sons = False,
                              print_attributes = False,
                              print_location = False,
                              print_rotation = False,
                              )
    if print_attributes:
        print(prefix + 'Attributes:')
        max_len = max(len(attr) for attr in actor.attributes)
        for attr in actor.attributes:
            print(' ' * (len(prefix) + 4), f"{attr:<{max_len}}", ': ', actor.attributes[attr], sep='')
    if print_location:
        print(prefix, 'Transform: ', actor.get_location(), sep='')
    if print_rotation:
        print(prefix, 'Transform: ', actor.get_transform().rotation, sep='')

def print_actor_move(actor: carla.Actor, prefix: str = ''):
    print(prefix, 'Velocity       : ', actor.get_velocity(), sep='')
    print(prefix, 'Acceleration   : ', actor.get_acceleration(), sep='')
    print(prefix, 'AngularVelocity: ', actor.get_angular_velocity(), sep='')

def print_actor_boundbox(actor: carla.Actor, prefix: str = ''):
    bb = actor.bounding_box
    print(prefix, 'BoundingBox Location: ', bb.location, sep='')
    print(prefix, 'BoundingBox Extent  : ', bb.extent, sep='')
    print(prefix, 'BoundingBox Rotation: ', bb.rotation, sep='')

def print_actor_vehicle_wheel(actor: carla.Actor, prefix: str = ''):
    if not is_vehicle(actor):
        return
    vehicle: carla.Vehicle = actor
    print(prefix, 'FL_Wheel: ', vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.FL_Wheel), sep='')
    print(prefix, 'FR_Wheel: ', vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.FR_Wheel), sep='')

def print_actor_vehicle_control(actor: carla.Actor, prefix: str = ''):
    if not is_vehicle(actor):
        return
    vehicle: carla.Vehicle = actor
    control = vehicle.get_control()
    print(prefix, 'Control Throttle  : ', control.throttle, sep='')
    print(prefix, 'Control Brake     : ', control.brake, sep='')
    print(prefix, 'Control Steer     : ', control.steer, sep='')
    print(prefix, 'Control Reverse   : ', control.reverse, sep='')
    print(prefix, 'Control HandBrake : ', control.hand_brake, sep='')
    print(prefix, 'Control Gear      : ', control.gear, sep='')
    print(prefix, 'Control ManualGear: ', control.manual_gear_shift, sep='')

def print_actor_vehicle_physics(actor: carla.Actor, prefix: str = ''):
    if not is_vehicle(actor):
        return
    vehicle: carla.Vehicle = actor
    physics = vehicle.get_physics_control()
    print(prefix, 'Vehicle Physics:', sep='')
    p = ' ' * (len(prefix) + 4)
    pp = ' ' * (len(prefix) + 8)
    print(p, 'moi             : ', physics.moi, sep='')
    print(p, 'mass            : ', physics.mass, sep='')
    print(p, 'max rpm         : ', physics.max_rpm, sep='')
    print(p, 'final_ratio     : ', physics.final_ratio, sep='')
    print(p, 'center_of_mass  : ', physics.center_of_mass, sep='')
    print(p, 'clutch_strength : ', physics.clutch_strength, sep='')
    print(p, 'use_gear_autobox: ', physics.use_gear_autobox, sep='')
    print(p, 'gear_switch_time: ', physics.gear_switch_time, sep='')
    print(p, 'drag_coefficient: ', physics.drag_coefficient, sep='')
    print(p, 'use_sweep_wheel_collision                   : ', physics.use_sweep_wheel_collision, sep='')
    print(p, 'damping_rate_full_throttle                  : ', physics.damping_rate_full_throttle, sep='')
    print(p, 'damping_rate_zero_throttle_clutch_engaged   : ', physics.damping_rate_zero_throttle_clutch_engaged, sep='')
    print(p, 'damping_rate_zero_throttle_clutch_disengaged: ', physics.damping_rate_zero_throttle_clutch_disengaged, sep='')
    print(p, 'Torque Curve:', sep='')
    for curve in physics.torque_curve:
        print(pp, curve, sep='')
    print(p, 'Forward Gears:', sep='')
    for gear in physics.forward_gears:
        print(pp, gear, sep='')
    print(p, 'Steering Curve:', sep='')
    for curve in physics.steering_curve:
        print(pp, curve, sep='')
    print(p, 'Wheel:', sep='')
    for i, wheel in enumerate(physics.wheels):
        print(pp, i, ': tire_friction       : ', wheel.tire_friction, sep='')
        print(pp, i, ': damping_rate        : ', wheel.damping_rate, sep='')
        print(pp, i, ': max_steer_angle     : ', wheel.max_steer_angle, sep='')
        print(pp, i, ': radius              : ', wheel.radius, sep='')
        print(pp, i, ': max_brake_torque    : ', wheel.max_brake_torque, sep='')
        print(pp, i, ': max_handbrake_torque: ', wheel.max_handbrake_torque, sep='')
        print(pp, i, ': position            : ', wheel.position, sep='')
        print(pp, i, ': long_stiff_value    : ', wheel.long_stiff_value, sep='')
        print(pp, i, ': lat_stiff_max_load  : ', wheel.lat_stiff_max_load, sep='')
        print(pp, i, ': lat_stiff_value     : ', wheel.lat_stiff_value, sep='')
        print()

def print_actor(
        actor: carla.Actor,
        client: carla.Client,
        prefix: str = '',
        print_parent: bool = True,
        print_sons: bool = True,
        print_attributes: bool = True,
        print_location: bool = True,
        print_rotation: bool = True,
        print_move: bool = True,
        print_boundbox: bool = True,
        print_vehicle_wheel: bool = True,
        print_vehicle_control: bool = True,
        print_vehicle_physics: bool = True,
):
    print_actor_basic(actor, client, prefix, print_parent, print_sons, print_attributes, print_location, print_rotation)
    if print_move:
        print()
        print_actor_move(actor, prefix)
    if print_boundbox and math.isfinite(actor.bounding_box.location.x):
        print()
        print_actor_boundbox(actor, prefix)
    if print_vehicle_wheel and is_vehicle(actor):
        print()
        print_actor_vehicle_wheel(actor, prefix)
    if print_vehicle_control and is_vehicle(actor):
        print()
        print_actor_vehicle_control(actor, prefix)
    if print_vehicle_physics and is_vehicle(actor):
        print()
        print_actor_vehicle_physics(actor, prefix)

def print_actors_tree(actors: carla.ActorList, pattern: str = ''):
    root_ids: set[int] = set()
    pattern = pattern.strip('*')
    if pattern:
        for actor in actors:
            if pattern in actor.attributes.get('role_name', '') or pattern in actor.type_id:
                while actor.parent is not None:
                    actor = actors.find(actor.parent.id)
                root_ids.add(actor.id)
    if not pattern.startswith('*'):
        pattern = '*' + pattern
    if not pattern.endswith('*'):
        pattern = pattern + '*'
    for actor in actors.filter(pattern):
        while actor.parent is not None:
            actor = actors.find(actor.parent.id)
        root_ids.add(actor.id)
    max_len = max([len(a.attributes.get('role_name', '')) for a in actors])
    def print_tree(a: carla.Actor, prefix: str = ''):
        print_simple_actor(a, prefix, max_len)
        for actor in actors:
            if actor.parent is not None and actor.parent.id == a.id:
                print_tree(actor, prefix + ' ' * 4)
    for actor_id in root_ids:
        print_tree(actors.find(actor_id))

def destroy_actor(actor_id, client: carla.Client):
    try:
        while True:
            client.get_world().wait_for_tick()
            actor = get_actor(actor_id, client)
            if actor is None or not actor.is_alive:
                return
            actors = client.get_world().get_actors()
            for a in actors:
                if a.parent is not None and a.parent.id == actor.id and a.is_alive:
                    print('destroying son actor: ')
                    print_simple_actor(a)
                    a.destroy()
            print('destroying actor: ')
            print_simple_actor(actor)
            actor.destroy()
    except RuntimeError as e:
        print(e)
        print('check the actor {} status'.format(actor_id))
        pass

def print_settings(settings: carla.WorldSettings):
    print('synchronous_mode      : ', settings.synchronous_mode)
    print('no_rendering_mode     : ', settings.no_rendering_mode)
    print('fixed_delta_seconds   : ', settings.fixed_delta_seconds)
    print('substepping           : ', settings.substepping)
    print('max_substep_delta_time: ', settings.max_substep_delta_time)
    print('max_substeps          : ', settings.max_substeps)
    print('max_culling_distance  : ', settings.max_culling_distance)
    print('deterministic_ragdolls: ', settings.deterministic_ragdolls)
    print('tile_stream_distance  : ', settings.tile_stream_distance)
    print('actor_active_distance : ', settings.actor_active_distance)
    print('spectator_as_ego      : ', settings.spectator_as_ego)

def get_blueprint(pattern, client: carla.Client) -> carla.ActorBlueprint | None:
    if len(pattern) == 0:
        return None
    try:
        return client.get_world().get_blueprint_library().find(pattern)
    except RuntimeError:
        pass
    if not pattern.startswith('*'):
        pattern = '*' + pattern
    if not pattern.endswith('*'):
        pattern = pattern + '*'
    bps = client.get_world().get_blueprint_library().filter(pattern)
    if len(bps) == 0:
        return None
    return bps[0]

def spawn_actor(
        client: carla.Client,
        bp: carla.ActorBlueprint,
        transform: carla.Transform = None,
        parent: carla.Actor = None,
        attachment_type = carla.AttachmentType.Rigid
):
    if transform is None:
        loc = carla.Location()
        rot = carla.Rotation()
        transform = carla.Transform(loc, rot)
    if parent is None:
        return client.get_world().spawn_actor(bp, transform)
    return client.get_world().spawn_actor(bp, transform, parent, attachment_type)

def get_transform(x, y, z, roll, pitch, yaw) -> carla.Transform | None:
    if {x, y, z, roll, pitch, yaw} == {None}:
        return None
    x = 0 if x is None else x
    y = 0 if y is None else y
    z = 0 if z is None else z
    roll = 0 if roll is None else roll
    pitch = 0 if pitch is None else pitch
    yaw = 0 if yaw is None else yaw
    return carla.Transform(carla.Location(x, y, z), carla.Rotation(pitch, yaw, roll))

def move_to(
        client: carla.Client, actor_id: str = None, target_id: str = None,
        x: float = None, y: float = None, z: float = None,
        roll: float = None, pitch: float = None, yaw: float = None,
):
    client.get_world().wait_for_tick()
    actor = get_actor(actor_id, client)
    if actor is None:
        return
    target = get_actor(target_id, client)
    t = get_transform(x, y, z, roll, pitch, yaw)
    if target is None:
        if t is None:
            return
        actor.set_transform(t)
        return
    if t is None:
        actor.set_transform(target.get_transform())
        return
    dummy_bp = get_blueprint('sensor.other.collision', client)
    dummy_bp.set_attribute('role_name', 'dummy_for_move_to')
    dummy = spawn_actor(client, dummy_bp, t, target, carla.AttachmentType.Rigid)
    client.get_world().wait_for_tick()
    actor.set_transform(dummy.get_transform())
    dummy.destroy()
