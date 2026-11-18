"""Additional continuous performances. The PNG catalog stays independent."""
from math import cos, pi, radians, sin

from poses import CROUCH, HURT, actions, fallen, kick, shifted, stance_for


GAIT_TRAVEL = {"walk_fwd": 2.20, "walk_back": 1.72, "run": 2.55, "run_back": 2.30}
FALL_CLIPS = {"thrown_air", "knockdown", "knockdown_low", "ko_fall"}
PUNCHES = {
    "stand_lp": (4, 3, 7, 1.20, 2.08, .11, False),
    "stand_mp": (6, 3, 12, 1.36, 2.02, .23, True),
    "stand_hp": (9, 4, 18, 1.48, 2.16, .37, False),
    "crouch_lp": (4, 3, 6, 1.14, 1.49, .10, False),
    "crouch_mp": (6, 3, 11, 1.24, 1.67, .22, False),
    "crouch_hp": (8, 4, 16, 1.28, 1.97, .33, True),
    "jump_lp": (4, 6, 4, 1.13, 1.82, .10, False),
    "jump_mp": (6, 5, 4, 1.26, 1.76, .24, True),
    "jump_hp": (8, 4, 6, 1.36, 1.64, .35, False),
}
KICKS = {"stand_lk", "stand_mk", "stand_hk", "crouch_lk", "crouch_mk", "crouch_hk",
         "jump_lk", "jump_mk", "jump_hk", "knee"}
ARTICULATED_ARMS = (PUNCHES.keys() | KICKS | GAIT_TRAVEL.keys()
                    | {"idle", "crouch", "crouch_enter", "crouch_exit", "guard", "guard_crouch",
                       "block_high", "block_low", "jump_start", "jump", "fall_air", "land",
                       "palm", "upper"})


def boxing_punch(base, vocalist, spec):
    startup, active, recovery, x, z, power, rear = spec
    side = "far" if rear and not vocalist else "near"
    other = "near" if side == "far" else "far"
    depth = 1 if side == "far" else -1
    shoulder = base[f"shoulder_{side}"]
    neck = base["neck"]
    head = base["head"]
    hip = base["hips"]
    turn = .09 + power * .65
    lead = .13 + power * .62

    def drive(amount):
        pose = dict(base, hips=(hip[0] + .24 * lead * amount, *hip[1:]),
                    neck=(neck[0] + lead * amount, neck[1], neck[2] - .04 * amount),
                    head=(head[0] + .69 * lead * amount, head[1], head[2] - .055 * amount),
                    rolls={"pelvis": -depth * turn * amount, "instrument": -depth * turn * amount})
        for arm in (side, other):
            sx, sy, sz = base[f"shoulder_{arm}"]
            swing = turn * amount * (1 if arm == side else -1)
            pose[f"shoulder_{arm}"] = (sx + lead * amount + swing, sy - depth * .055 * amount, sz + swing * .14)
        hx, hy, hz = base[f"hand_{other}"]
        ex, ey, ez = base[f"elbow_{other}"]
        pose[f"hand_{other}"] = (hx + lead * amount * .64, hy, hz + .06 * amount)
        pose[f"elbow_{other}"] = (ex - turn * amount * .42, ey, ez + .05 * amount)
        return pose

    def arm(pose, wrist, elbow):
        pose[f"hand_{side}"] = wrist
        pose[f"elbow_{side}"] = elbow
        return pose

    load = arm(drive(-.49), (.35 - .58 * power, shoulder[1] + depth * .17, shoulder[2] + .09),
               (shoulder[0] - .20 - power * .46, shoulder[1] + depth * .19, shoulder[2] - .23))
    # Heavy strikes take a wider lane, then the wrist follows through the target.
    lane = shoulder[1] + depth * (.065 if power < .3 else .18)
    hit = arm(drive(1.0), (x, lane, z),
              (x * .65, lane + depth * .16, z - .17 + power * .23))
    through = arm(drive(.77), (x - .095, lane - depth * (.09 + power * .25), z - .035),
                  (x * .60, lane + depth * .14, z - .19))
    chamber = arm(drive(.28), (.49, shoulder[1] + depth * .18, shoulder[2] + .09),
                  (.22, shoulder[1] + depth * .19, shoulder[2] - .31))
    load_ticks = max(1, startup // 2)
    return [(load_ticks, base), (startup - load_ticks, load), (active, hit),
            (max(1, recovery // 3), through), (recovery - max(1, recovery // 3) - 1, chamber), (1, base)]


def gait(base, name, vocalist):
    running = name.startswith("run")
    reverse = -1 if name.endswith("back") else 1
    half = GAIT_TRAVEL[name] / 4
    frames = []
    for tick in range(24):
        phase = tick / 24
        pose = shifted(base, (.065 if running else .028) * sin(4 * pi * phase))
        if running:
            pose.update(neck=(.22 * reverse, 0, 1.86), head=(.37 * reverse, 0, 2.49))
        for index, (side, depth) in enumerate((("near", -.19), ("far", .21))):
            step = (phase + index * .5) % 1 * 2
            if step < 1:
                # Relative translation cancels the body's forward travel over a planted step.
                x, lift = half * (1 - 2 * step), 0.0
            else:
                swing = step - 1
                x = -half * cos(pi * swing)
                lift = (.39 if running else .23) * sin(pi * swing)
            pose[f"foot_{side}"] = (reverse * x, depth, .15 + lift)
            pose[f"knee_{side}"] = (.11 + reverse * x * .64, depth, .72 + lift * .73)
        sway = reverse * cos(2 * pi * phase)
        lag = reverse * cos(2 * pi * phase - .43)
        turn = .09 if running else .050
        pose["rolls"] = {"pelvis": turn * sway, "instrument": turn * sway}
        for side, direction in (("near", 1), ("far", -1)):
            gain = .23 if running else .10
            if vocalist and side == "far":
                gain = .035
            for joint, amount, wave in (("shoulder", turn * .38, sway), ("elbow", gain, sway),
                                        ("hand", gain * .81, lag)):
                key = f"{joint}_{side}"
                x, y, z = pose[key]
                pose[key] = (x + direction * amount * wave, y, z + direction * amount * .18 * wave)
        frames.append((1, pose))
    return frames


def balance_kick(frames, base, vocalist):
    motion = (.36, 1.0, .64, .27)
    result = []
    for index, (duration, pose) in enumerate(frames):
        amount = motion[min(index, len(motion) - 1)] if index < len(frames) - 1 else 0
        balanced = dict(pose, rolls={"pelvis": -.19 * amount, "instrument": -.19 * amount})
        for side in ("near", "far"):
            mic = vocalist and side == "far"
            gain = .14 if mic else 1.0
            direction = 1 if side == "near" else -1
            for joint, dx, dz in (("shoulder", -.08, .025), ("elbow", -.28, -.11), ("hand", -.26, -.14)):
                key = f"{joint}_{side}"
                x, y, z = base[key]
                balanced[key] = (x + dx * direction * gain * amount, y + direction * -.11 * gain * amount,
                                 z + dz * gain * amount)
        result.append((duration, balanced))
    return result


def performances(character):
    vocalist = character == "frontman"
    legacy = actions(character, True)
    idle = stance_for(character)
    crouch = dict(idle, **CROUCH)
    down = fallen(vocalist)
    if character != "guitarist":
        down = dict(down, hips=(-.17, 0, .16), neck=(-.76, 0, .255), head=(-1.33, 0, .39),
                    shoulder_near=(-.70, -.30, .30), shoulder_far=(-.69, .30, .35),
                    elbow_near=(-.51, -.56, .14), hand_near=(-.16, -.78, .15),
                    elbow_far=(-.40, .43, .40), hand_far=(-.19, .57, .58),
                    knee_near=(.38, -.22, .19), foot_near=(.91, -.27, .075),
                    knee_far=(.36, .25, .36), foot_far=(.82, .27, .13),
                    boot_near=(.26, 0, 0))
        if character == "bruce":
            down["head"] = (-1.33, 0, .49)
    else:
        # Roll onto the jacket with the guitar angled away from the floor.
        down = dict(down, hips=(-.35, 0, .24), neck=(-.94, -.15, .29), head=(-1.50, -.20, .49),
                    shoulder_near=(-.89, -.37, .29), shoulder_far=(-.89, .15, .49),
                    elbow_near=(-.62, -.57, .15), hand_near=(-.18, -.63, .17),
                    elbow_far=(-.69, .38, .44), hand_far=(-.28, .40, .43),
                    knee_near=(.24, -.25, .19), foot_near=(.78, -.26, .075),
                    knee_far=(.20, .22, .43), foot_far=(.66, .31, .075),
                    boot_near=(.26, 0, .07),
                    rolls={"pelvis": radians(-53), "instrument": radians(-65), "head": radians(-12)})
    air = dict(idle, knee_near=(.48, -.21, 1.01), foot_near=(.15, -.20, .52),
               knee_far=(-.29, .20, .79), foot_far=(-.63, .21, .44))
    compact = dict(air, head=(.26, 0, 2.45), hand_near=(.44, -.45, 1.98))
    punch_stances = {"stand": idle, "crouch": crouch, "jump": air}
    landing = dict(crouch, hips=(-.18, 0, .91), neck=(.20, 0, 1.47), head=(.31, 0, 2.02))
    grasp = dict(idle, neck=(.28, 0, 1.83), head=(.39, 0, 2.39),
                 shoulder_near=(.28, -.30, 1.74), shoulder_far=(.30, .29, 1.75),
                 elbow_near=(.69, -.35, 1.52), elbow_far=(.68, .34, 1.55),
                 hand_near=(1.06, -.27, 1.54), hand_far=(1.05, .25, 1.62),
                 knee_near=(.35, -.19, .61), hips=(.04, 0, 1.10))
    leverage = dict(grasp, hips=(.02, 0, 1.23), neck=(.36, 0, 1.94), head=(.40, 0, 2.52),
                    elbow_near=(.65, -.36, 1.76), elbow_far=(.69, .28, 1.81),
                    hand_near=(1.07, -.25, 2.01), hand_far=(1.03, .24, 1.92))
    release = dict(leverage, hand_near=(1.42, -.27, 1.85), hand_far=(1.37, .26, 1.76),
                   elbow_near=(.89, -.32, 1.79), elbow_far=(.89, .29, 1.72))
    restrained = dict(idle, neck=(-.18, 0, 1.88), head=(-.20, 0, 2.46),
                      shoulder_near=(-.15, -.31, 1.80), shoulder_far=(-.12, .31, 1.79),
                      hand_near=(.37, -.43, 1.93), elbow_near=(.1, -.46, 1.55),
                      hand_far=(.33, .38, 1.96), elbow_far=(.10, .41, 1.56))
    lifted = dict(restrained, neck=(-.19, 0, 1.91), head=(-.26, 0, 2.48),
                  knee_near=(.39, -.20, .89), foot_near=(.55, -.21, .37),
                  knee_far=(-.05, .20, .72), foot_far=(-.35, .22, .32),
                  hand_near=(.20, -.60, 1.85), hand_far=(.15, .49, 1.91))
    # Torso and head rotate on the way down. Bent legs extend as the body settles.
    impact = dict(down, knee_far=(.30, .18, .52), foot_far=(.74, .24, .30))
    airborne = dict(shifted(down, .32), hips=(-.24, 0, .72), neck=(-.71, 0, 1.10),
                    head=(-1.15, 0, 1.49), elbow_near=(-.56, -.48, .93),
                    hand_near=(-.31, -.54, 1.21), shoulder_near=(-.67, -.29, 1.03),
                    shoulder_far=(-.65, .28, 1.04), elbow_far=(-.28, .42, .91),
                    hand_far=(.06, .49, 1.24), knee_near=(.23, -.23, .74),
                    foot_near=(.60, -.29, .40))
    rise = dict(crouch, hand_near=(.63, -.48, .52), elbow_near=(.32, -.49, .85))
    block = dict(idle, hand_near=(.54, -.50, 2.15), elbow_near=(.38, -.50, 1.67),
                 hand_far=(.59, .23, 2.22), elbow_far=(.39, .30, 1.62))
    block_low = dict(crouch, hand_near=(.57, -.51, 1.47), hand_far=(.61, .26, 1.53))
    result = {
        **{name: gait(idle, name, vocalist) for name in GAIT_TRAVEL},
        **{name: boxing_punch(punch_stances[name.split("_")[0]], vocalist, spec) for name, spec in PUNCHES.items()},
        "crouch_enter": [(4, idle), (1, crouch)],
        "crouch_exit": [(4, crouch), (1, idle)],
        "jump_start": [(2, idle), (2, landing)],
        "jump": [(5, idle), (9, air), (8, compact)],
        "fall_air": [(5, compact), (10, dict(air, foot_near=(.27, -.20, .23)))],
        "land": [(2, air), (3, landing), (1, idle)],
        "crouch_mk": kick(7, 3, 14, 1.65, .51, crouch),
        "jump_lk": kick(5, 8, 8, 1.21, 1.46, compact),
        "jump_mk": kick(7, 5, 9, 1.55, 1.43, air),
        "jump_hk": kick(9, 4, 10, 1.68, 1.39, compact),
        "block_high": [(2, dict(block, neck=(-.17, 0, 1.86))), (4, block)],
        "block_low": [(2, dict(block_low, head=(.02, 0, 1.69))), (4, block_low)],
        "throw": [(4, idle), (4, grasp), (4, leverage), (4, release), (4, idle)],
        "grabbed_hold": [(3, idle), (5, restrained), (4, lifted), (1, lifted)],
        "thrown_air": [(4, lifted), (4, airborne), (3, impact), (2, down)],
        "knockdown": [(3, dict(idle, **HURT)), (3, airborne), (3, impact), (2, down)],
        "knockdown_low": [(3, crouch), (3, shifted(down, .19)), (3, impact), (2, down)],
        "down_hold": [(1, down), (1, down)],
        "getup": [(3, down), (4, rise), (4, landing), (2, idle)],
        "ko_fall": [(4, dict(idle, **HURT)), (5, airborne), (4, impact), (2, down)],
    }
    for name in sorted(KICKS):
        base = punch_stances.get(name.split("_")[0], idle)
        result[name] = balance_kick(result.get(name, legacy.get(name)), base, vocalist)
    for name in ("idle", "crouch", "guard", "guard_crouch", "palm", "upper"):
        result[name] = legacy[name]
    # Shift the uppercut with the shoulder. The glove travels in a short arc.
    for index, (dx, dz) in enumerate(((.00, .02), (.28, .32), (.19, .27))):
        duration, pose = result["upper"][index]
        sx, sy, sz = pose["shoulder_near"]
        nx, ny, nz = pose["neck"]
        result["upper"][index] = (duration, dict(pose, shoulder_near=(sx + dx, sy, sz + dz),
                                                  neck=(nx + dx * .5, ny, nz + dz * .7)))
    return result
