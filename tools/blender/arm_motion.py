"""Sample authored gestures and keep their two arm segments at fixed lengths."""
from math import sqrt

from mathutils import Vector

from poses import STANCE


UPPER_ARM = .43
FOREARM = .44


def _curve(previous, current, following, after, before_span, span, after_span, t):
    delta = (following - current) / span

    def tangent(neighbor):
        if neighbor * delta <= 0:
            return 0.0
        return 2 * neighbor * delta / (neighbor + delta) * span

    start = tangent((current - previous) / before_span)
    end = tangent((after - following) / after_span)
    return current + t * (start + t * (3 * (following - current) - 2 * start - end
                                      + t * (2 * (current - following) + start + end)))


def _between(previous, current, following, after, before_span, span, after_span, t):
    pose = {}
    names = (previous.keys() | current.keys() | following.keys() | after.keys()) - {"rolls"}
    for name in sorted(names):
        default = STANCE.get(name, (.26, 0, 0))
        points = (frame.get(name, default) for frame in (previous, current, following, after))
        pose[name] = tuple(_curve(*axis, before_span, span, after_span, t) for axis in zip(*points))
    rolls = [frame.get("rolls", {}) for frame in (previous, current, following, after)]
    pose["rolls"] = {
        name: _curve(*(frame.get(name, 0) for frame in rolls), before_span, span, after_span, t)
        for name in sorted(set().union(*rolls))
    }
    return pose


def _solve_arm(pose, side, vocalist):
    shoulder = Vector(pose[f"shoulder_{side}"])
    hint = Vector(pose[f"elbow_{side}"]) - shoulder
    target = Vector(pose[f"hand_{side}"]) - shoulder
    axis = target.normalized()
    distance = min(max(target.length, .22), UPPER_ARM + FOREARM - .012)
    pole = hint - hint.dot(axis) * axis
    # The elbow folds down and away from the ribs if the hint is nearly straight.
    if pole.length_squared < 1e-6:
        fallback = Vector((0, 1 if side == "far" else -1, -1))
        pole = fallback - fallback.dot(axis) * axis
    along = (UPPER_ARM ** 2 - FOREARM ** 2 + distance ** 2) / (2 * distance)
    elbow = shoulder + axis * along + pole.normalized() * sqrt(UPPER_ARM ** 2 - along ** 2)
    wrist = shoulder + axis * distance
    pose[f"elbow_{side}"] = tuple(elbow)
    pose[f"hand_{side}"] = tuple(wrist)
    if vocalist and side == "far":
        return
    # Roll the visible glove with the forearm. The mic hand keeps its authored grip.
    forward = (wrist - elbow).normalized()
    extension = max(0, (distance - .54) / (UPPER_ARM + FOREARM - .54))
    direction = Vector((1, 0, 0)).lerp(forward, .30 + .58 * extension)
    pose[f"fist_{side}"] = tuple(.26 * direction.normalized())


def sample_gesture(frames, loop, vocalist):
    poses = [pose for _, pose in frames]
    if loop:
        poses.append(poses[0])
    else:
        poses.append(poses[-1])
    durations = [duration for duration, _ in frames]
    for index, span in enumerate(durations):
        previous = index - 1 if index else (len(frames) - 1 if loop else 0)
        after = index + 2 if index + 2 < len(poses) else (1 if loop else index + 1)
        before_span = durations[previous]
        after_span = durations[(index + 1) % len(durations)] if loop or index + 1 < len(durations) else span
        for tick in range(span):
            pose = _between(poses[previous], poses[index], poses[index + 1], poses[after],
                            before_span, span, after_span, tick / span)
            for side in ("near", "far"):
                _solve_arm(pose, side, vocalist)
            yield pose
