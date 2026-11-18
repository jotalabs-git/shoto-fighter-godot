"""Storyboard in character space: +X forward, -Y toward camera, +Z up."""
from math import cos, pi, sin

# A duration at 60 Hz and an editable pose. Missing coordinates use the stance.
STANCE = {
    "hips": (-.05, 0, 1.27), "neck": (.04, 0, 1.97), "head": (.08, 0, 2.62),
    "shoulder_near": (.02, -.31, 1.85), "elbow_near": (.11, -.42, 1.47),
    "hand_near": (.48, -.48, 1.72),
    "shoulder_far": (.05, .31, 1.83), "elbow_far": (.19, .37, 1.49),
    "hand_far": (.43, .30, 1.64),
    "knee_near": (.20, -.16, .73), "foot_near": (.24, -.19, .15),
    "knee_far": (-.33, .18, .70), "foot_far": (-.47, .21, .15),
}
BONES = {
    "pelvis": ("hips", "neck", None), "head": ("neck", "head", "pelvis"),
    "bicep_near": ("shoulder_near", "elbow_near", "pelvis"),
    "forearm_near": ("elbow_near", "hand_near", "bicep_near"),
    "fist_near": ("hand_near", None, "forearm_near"),
    "bicep_far": ("shoulder_far", "elbow_far", "pelvis"),
    "forearm_far": ("elbow_far", "hand_far", "bicep_far"),
    "fist_far": ("hand_far", None, "forearm_far"),
    "thigh_near": ("hips_near", "knee_near", "pelvis"),
    "shin_near": ("knee_near", "foot_near", "thigh_near"),
    "boot_near": ("foot_near", None, "shin_near"),
    "thigh_far": ("hips_far", "knee_far", "pelvis"),
    "shin_far": ("knee_far", "foot_far", "thigh_far"),
    "boot_far": ("foot_far", None, "shin_far"),
    "instrument": ("hips", "neck", "pelvis"),
}

CROUCH = {
    "hips": (-.30, 0, .74), "neck": (.18, 0, 1.30), "head": (.34, 0, 1.78),
    "shoulder_near": (.10, -.31, 1.25), "elbow_near": (.13, -.49, .93),
    "hand_near": (.52, -.48, 1.1), "shoulder_far": (.12, .31, 1.23),
    "elbow_far": (.21, .36, .86), "hand_far": (.50, .32, 1.01),
    "knee_near": (.40, -.20, .46), "foot_near": (.23, -.22, .15),
    "knee_far": (-.35, .20, .48), "foot_far": (-.66, .22, .15),
}
HURT = {
    "neck": (-.34, 0, 1.91), "head": (-.63, 0, 2.5),
    "shoulder_near": (-.28, -.31, 1.81), "elbow_near": (-.43, -.49, 1.47),
    "hand_near": (-.60, -.67, 1.68), "shoulder_far": (-.25, .31, 1.78),
    "elbow_far": (.08, .43, 1.48), "hand_far": (.38, .48, 1.39),
}
FRONT = {
    "hips": (.02, 0, 1.22), "neck": (.22, 0, 1.90), "head": (.37, 0, 2.51),
    "shoulder_near": (.17, -.31, 1.80), "elbow_near": (.02, -.43, 1.57),
    "hand_near": (.44, -.49, 1.89), "shoulder_far": (.18, .31, 1.80),
    "elbow_far": (.060, .34, 1.58), "hand_far": (.591, .205, 1.976),
    "foot_near": (.45, -.19, .15), "knee_near": (.37, -.20, .68),
}
GUITAR_GUARD = {
    "hips": (-.23, .015, 1.20), "neck": (.008, -.025, 1.91), "head": (.232, -.045, 2.523),
    "shoulder_near": (.078, -.337, 1.786), "elbow_near": (.245, -.455, 1.641),
    "hand_near": (.476, -.477, 1.988),
    "shoulder_far": (-.123, .266, 1.813), "elbow_far": (.026, .342, 1.489),
    "hand_far": (.334, .286, 1.646),
    "knee_near": (.217, -.185, .682), "foot_near": (.373, -.213, .15),
    "knee_far": (-.333, .183, .696), "foot_far": (-.553, .220, .15),
}
OZZY_GUARD = {
    "hips": (-.12, 0, 1.20), "neck": (.11, -.038, 1.91), "head": (.238, -.073, 2.54),
    "shoulder_near": (.16, -.34, 1.78), "elbow_near": (.20, -.58, 1.51),
    "hand_near": (.501, -.58, 1.75),
    "shoulder_far": (-.02, .29, 1.82), "elbow_far": (.12, .44, 1.55),
    "hand_far": (.464, .38, 1.83),
    "knee_near": (.24, -.24, .70), "foot_near": (.424, -.272, .15),
    "knee_far": (-.32, .23, .69), "foot_far": (-.51, .252, .15),
}
BRUCE_GUARD = {
    "hips": (-.16, .012, 1.23), "neck": (.051, -.02, 1.93), "head": (.154, -.041, 2.56),
    "shoulder_near": (.077, -.33, 1.808), "elbow_near": (.172, -.48, 1.556),
    "hand_near": (.57, -.488, 1.879),
    "shoulder_far": (.018, .281, 1.831), "elbow_far": (.023, .407, 1.575),
    "hand_far": (.359, .299, 1.940),
    "knee_near": (.291, -.20, .72), "foot_near": (.425, -.214, .15),
    "knee_far": (-.39, .211, .70), "foot_far": (-.561, .253, .15),
}


def stance_for(character):
    gestures = {"guitarist": GUITAR_GUARD, "frontman": FRONT, "ozzy": OZZY_GUARD, "bruce": BRUCE_GUARD}
    return dict(STANCE, **gestures[character])


def shifted(pose, dz):
    result = {name: (x, y, z + dz) for name, (x, y, z) in pose.items() if name != "rolls"}
    if "rolls" in pose:
        result["rolls"] = pose["rolls"]
    return result


def cycle(base, count, period, stride, run=False):
    frames = []
    for index in range(count):
        phase = index * 2 * pi / count
        sway = cos(phase)
        bounce = (.06 if run else .028) * sin(2 * phase)
        pose = shifted(base, bounce)
        if run:
            pose.update({"neck": (.32, 0, 1.90 + bounce), "head": (.53, 0, 2.50 + bounce)})
        for side, depth, phase in (("near", -.19, phase), ("far", .21, phase + pi)):
            x = stride * cos(phase)
            lift = max(0, sin(phase)) * (.37 if run else .23)
            pose[f"foot_{side}"] = (x, depth, .15 + lift)
            pose[f"knee_{side}"] = (x * .64 + .13, depth, .72 + lift * .62)
        pose["elbow_near"] = (.10 - .19 * sway, -.43, 1.57 + bounce)
        pose["hand_near"] = (.39 - .36 * sway, -.54, 1.68 + .08 * sway + bounce)
        frames.append((period, pose))
    return frames


def punch(startup, active, recovery, x, z, base, windup=.2, reach_far=False):
    side = "far" if reach_far else "near"
    depth = .29 if reach_far else -.56
    shoulder = base[f"shoulder_{side}"]
    anticipation = dict(base, **{
        f"elbow_{side}": (shoulder[0] - windup, depth, shoulder[2] - .26),
        f"hand_{side}": (shoulder[0] + .07, depth, shoulder[2] - .02),
    })
    hit = dict(base, **{
        f"shoulder_{side}": (shoulder[0] + .25, shoulder[1], shoulder[2] - .02),
        f"elbow_{side}": (x * .57, depth, z - .07),
        f"hand_{side}": (x, depth, z),
    })
    retract = dict(base, **{
        f"elbow_{side}": (x * .22, depth, z - .25),
        f"hand_{side}": (x * .63, depth, z + .06),
    })
    return [(startup, anticipation), (active, hit), (recovery // 2, retract),
            (recovery - recovery // 2, base)]


def kick(startup, active, recovery, x, z, base):
    chamber = dict(base, knee_near=(.63, -.23, z + .22), foot_near=(.14, -.23, z - .15),
                   hand_near=(.41, -.56, base["neck"][2] - .05))
    hit = dict(base, neck=(-.24, 0, base["neck"][2]), head=(-.40, 0, base["head"][2]),
               knee_near=(x * .54, -.22, (z + base["hips"][2]) / 2),
               foot_near=(x, -.22, z), boot_near=(.32, 0, .08 if z > .7 else .02))
    settle = dict(base, foot_near=(.52, -.21, .27), knee_near=(.32, -.22, .73))
    return [(startup, chamber), (active, hit), (3, chamber), (3, settle), (recovery - 6, base)]


def fallen(vocalist):
    pose = {
        "hips": (-.35, 0, .37), "neck": (-.94, 0, .40), "head": (-1.52, 0, .43),
        "shoulder_near": (-.88, -.31, .41), "elbow_near": (-.52, -.49, .29),
        "hand_near": (-.23, -.63, .22), "shoulder_far": (-.86, .31, .42),
        "elbow_far": (-.65, .43, .60), "hand_far": (-.29, .43, .68),
        "knee_near": (.29, -.18, .42), "foot_near": (.81, -.20, .18),
        "knee_far": (.21, .18, .60), "foot_far": (.69, .19, .45),
        "boot_near": (.07, 0, .31)
    }
    # The hair and the bottom of the guitar extend below the hip in this pose.
    # Lift the body, while keeping the trailing boot in contact with the floor.
    result = shifted({key: point for key, point in pose.items() if key != "boot_near"}, .29)
    result["foot_near"] = pose["foot_near"]
    result["boot_near"] = pose["boot_near"]
    if vocalist:
        result = {key: (x + .21, y, z) if key != "boot_near" else (x, y, z)
                  for key, (x, y, z) in result.items()}
    return result


def actions(character, full):
    vocalist = character == "frontman"
    base = stance_for(character)
    bob = shifted(base, .04 if vocalist else .025)
    for key in ("foot_near", "foot_far"):
        bob[key] = base[key]
    recoil = dict(base, **HURT)
    light = punch(4, 3, 7, 1.29, 2.10, base)
    result = {
        "idle": [(7, base), (6, bob), (7, base), (6, shifted(bob, -.032))],
        "walk_fwd": cycle(base, 8, 3, .62),
        "stand_lp": light,
        "hurt": [(4, recoil), (4, dict(recoil, head=(-.43, 0, 2.51))), (4, base)],
    }
    result["idle"][-1][1].update({key: base[key] for key in ("foot_near", "foot_far")})
    if vocalist:
        bob["hand_far"] = (.603, .178, 2.048)
        result["idle"] = [(5, base), (4, bob), (5, base), (4, result["idle"][-1][1])]
    elif character == "ozzy":
        open_guard = dict(bob, head=(.252, -.092, 2.542), hand_near=(.54, -.63, 1.81),
                          hand_far=(.507, .43, 1.86))
        result["idle"] = [(9, base), (8, open_guard), (7, base), (7, result["idle"][-1][1])]
    elif character == "bruce":
        bob["hand_near"] = (.562, -.503, 1.938)
        bob["hand_far"] = (.392, .294, 1.953)
        result["idle"] = [(6, base), (6, bob), (6, base), (5, result["idle"][-1][1])]
    else:
        bob["hand_near"] = (.505, -.498, 2.032)
        downbeat = result["idle"][-1][1]
        downbeat["head"] = (.260, -.049, 2.498)
        downbeat["hand_near"] = (.447, -.471, 1.948)
    if not full:
        return result

    crouch = dict(base, **CROUCH)
    jump = dict(base, knee_near=(.50, -.20, .96), foot_near=(.03, -.21, .55),
                knee_far=(-.32, .19, .71), foot_far=(-.63, .22, .52),
                hand_near=(.53, -.52, 2.00))
    guard = dict(base, elbow_near=(.46, -.52, 1.50), hand_near=(.66, -.50, 2.06),
                 elbow_far=(.47, .27, 1.56), hand_far=(.65, .22, 2.23))
    down = fallen(vocalist)
    result.update({
        "walk_back": list(reversed(cycle(base, 8, 3, .53))),
        "run": cycle(base, 6, 3, .77, run=True),
        "crouch": [(1, crouch)],
        "jump": [(3, dict(crouch, head=(.16, 0, 2.05), neck=(.10, 0, 1.57))),
                 (5, base), (10, jump), (9, dict(jump, foot_far=(-.63, .22, .31))), (10, base)],
        "stand_mp": punch(6, 3, 12, 1.48, 2.04, base, .38, True),
        "stand_hp": punch(9, 4, 18, 1.64, 2.19, base, .47),
        "stand_lk": kick(5, 3, 8, 1.30, 1.12, base),
        "stand_mk": kick(7, 4, 14, 1.59, 1.31, base),
        "stand_hk": kick(11, 4, 20, 1.75, 1.50, base),
        "crouch_lp": punch(4, 3, 6, 1.23, 1.51, crouch),
        "crouch_mp": punch(6, 3, 11, 1.34, 1.76, crouch, .35),
        "crouch_lk": kick(5, 2, 7, 1.19, .38, crouch),
        "crouch_hk": kick(9, 3, 22, 1.60, .29, crouch),
        "guard": [(1, guard)],
        "guard_crouch": [(1, dict(crouch, elbow_near=(.48, -.52, .94),
                                 hand_near=(.63, -.51, 1.45), hand_far=(.66, .19, 1.58)))],
        "hurt_low": [(5, dict(crouch, head=(-.05, 0, 1.74))), (5, crouch)],
        "knockdown": [(3, recoil), (3, shifted(down, .36)), (4, shifted(down, .13)), (30, down)],
        "getup": [(8, down), (8, shifted(crouch, -.10)), (8, crouch), (8, base)],
        "throw": [(3, guard), (5, dict(base, hand_near=(1.11, -.53, 1.86), hand_far=(1.14, .23, 1.89),
                                     elbow_near=(.55, -.48, 1.68), elbow_far=(.54, .33, 1.66))),
                  (8, dict(base, head=(-.20, 0, 2.53), hand_near=(-.53, -.64, 2.13), hand_far=(.22, .29, 2.34),
                           elbow_near=(-.35, -.52, 1.75))), (6, crouch), (7, base)],
        "palm": [(5, dict(base, hand_near=(.17, -.60, 1.38))),
                 (6, dict(base, hand_near=(.66, -.60, 1.59) if not vocalist else (.47, .15, 2.02))),
                 (5, dict(base, hand_near=(1.28, -.57, 1.69), elbow_near=(.73, -.51, 1.64),
                           hand_far=(.65, .22, 2.12) if vocalist else (.42, .23, 1.56))),
                 (9, dict(base, hand_near=(.87, -.60, 1.67))), (18, base)],
        "upper": [(4, dict(crouch, hand_near=(.27, -.50, 1.08))),
                  (6, dict(jump, elbow_near=(.70, -.49, 2.09), hand_near=(.91, -.47, 2.97))),
                  (7, dict(jump, elbow_near=(.51, -.49, 2.17), hand_near=(.57, -.49, 2.73))),
                  (8, crouch), (10, base)],
        "knee": [(6, dict(base, knee_near=(.47, -.20, 1.09), foot_near=(.11, -.22, .61))),
                 (5, dict(jump, hand_near=(.22, -.64, 1.45))),
                 (4, dict(jump, knee_near=(1.09, -.22, 1.35), foot_near=(.58, -.26, .96))),
                 (4, dict(jump, knee_far=(.98, .14, 1.29), foot_far=(.53, .16, .91))),
                 (5, jump), (7, base)],
    })
    if vocalist:
        result["palm"][2] = (5, dict(base, neck=(.37, 0, 1.91), head=(.56, 0, 2.47),
                                   hand_near=(1.13, -.42, 1.70), elbow_near=(.69, -.47, 1.63),
                                   elbow_far=(.38, .33, 1.68), hand_far=(.56, .10, 2.18)))
    else:
        result["palm"][2] = (5, dict(base, hand_near=(1.03, -.51, 1.72), elbow_near=(.61, -.48, 1.63),
                                   hand_far=(1.09, .23, 1.75), elbow_far=(.64, .30, 1.65)))
    return result


def joint_positions(pose):
    joints = dict(STANCE, **pose)
    for side, depth in (("near", -.15), ("far", .15)):
        x, y, z = joints["hips"]
        joints[f"hips_{side}"] = (x, y + depth, z)
    return joints


def points(joints, name):
    start, end, _ = BONES[name]
    root = joints[start]
    if end is None:
        direction = joints.get(name, (.26, 0, 0))
        end = tuple(a + b for a, b in zip(root, direction))
    else:
        end = joints[end]
    return root, end
