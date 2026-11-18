"""Editable clay presenter and three short stage performances."""
import json
from math import cos, pi, sin, tau as TAU

import bpy
from mathutils import Vector

from garment_surface import GarmentSurface
from model import Sculpt, angled_face, blend, clay_line, merge_clay
from poses import STANCE, joint_positions

HEAD = "head"
BODY = "pelvis"


def sculpt_face(s):
    l = s.lump
    merge_clay(s, "Presenter · face", [
        l("Oval skull", HEAD, "skin", (-.021, 0, 2.539), (.288, .256, .336)),
        l("High cheekbones", HEAD, "skin", (.131, 0, 2.401), (.197, .248, .181), 8),
        l("Tapered chin", HEAD, "skin", (.149, 0, 2.232), (.169, .152, .133), -10),
        l("Bridge", HEAD, "skin", (.281, 0, 2.472), (.075, .059, .122), 18),
        l("Nose", HEAD, "skin", (.333, -.005, 2.403), (.077, .073, .054), 10),
        *[l("Cheek plane", HEAD, "skin", (.165, sign * .153, 2.402), (.135, .099, .079), -14)
          for sign in (-1, 1)],
    ], "skin", HEAD, voxel=.009)
    for sign in (-1, 1):
        yaw = sign * 27
        angled_face(s, "Smoky eye shadow", "shadow", (.258, sign * .158, 2.530), (.041, .095, .049), yaw)
        angled_face(s, "Almond lash line", "lash", (.272, sign * .149, 2.518), (.042, .086, .033), yaw)
        angled_face(s, "Ivory sclera", "white", (.285, sign * .151, 2.513), (.034, .073, .022), yaw)
        angled_face(s, "Brown iris", "iris", (.311, sign * .148, 2.511), (.019, .028, .023), yaw)
        angled_face(s, "Pupil", "lash", (.327, sign * .151, 2.511), (.011, .015, .015), yaw)
        l("Eye sparkle", HEAD, "white", (.335, sign * .147, 2.519), (.007, .006, .006))
        clay_line(s, "Sculpted winged eyeliner", HEAD, "lash", [
            (.312, sign * .090, 2.523, .28), (.332, sign * .134, 2.535, .82),
            (.295, sign * .199, 2.544, 1), (.257, sign * .238, 2.563, .25),
        ], .013)
        clay_line(s, "Expressive eyebrow", HEAD, "lash", [
            (.282, sign * .064, 2.569, .65), (.281, sign * .127, 2.598 + (sign < 0) * .013, 1),
            (.255, sign * .183, 2.601, .82), (.208, sign * .229, 2.576, .21),
        ], .022)
        l("Gold earring", HEAD, "metal", (-.041, sign * .273, 2.302), (.023, .024, .025))
        l("Weighted earring drop", HEAD, "gem", (-.042, sign * .281, 2.256), (.021, .018, .037))
    clay_line(s, "Satin upper lip", HEAD, "lip", [
        (.283, -.103, 2.316, .19), (.310, -.059, 2.301, .62), (.315, -.025, 2.311, .78),
        (.319, .002, 2.298, .52), (.313, .024, 2.306, .84), (.283, .095, 2.303, .22),
    ], .017)
    clay_line(s, "Satin lower lip", HEAD, "lip", [
        (.301, -.075, 2.295, .34), (.318, -.024, 2.276, .90),
        (.314, .033, 2.273, 1), (.291, .082, 2.292, .21),
    ], .021)
    clay_line(s, "Asymmetric smile line", HEAD, "mouth", [
        (.288, -.102, 2.316, .27), (.322, -.045, 2.295, .86),
        (.327, .021, 2.291, 1), (.289, .102, 2.300, .29),
    ], .009)
    l("Neck", HEAD, "skin", (.043, 0, 2.048), (.142, .145, .171), -8)


def sculpt_hair(s):
    # A continuous cap sets the hairline. The rolls build volume over that cap.
    columns, rings = 64, 24

    def crown_point(yaw, progress):
        front = (1 + cos(yaw)) * .5
        hairline = 2.39 - 1.37 * front ** 1.9 + .11 * sin(yaw) * front
        angle = progress * hairline
        roll = sin(angle) * (1 + .016 * cos(5 * yaw + angle))
        return (-.041 + .343 * roll * cos(yaw),
                .010 + .291 * roll * sin(yaw),
                2.551 + .385 * cos(angle))

    verts = [crown_point(0, 0)]
    for row in range(1, rings + 1):
        verts.extend(crown_point(TAU * col / columns, row / rings) for col in range(columns))
    faces = [(0, 1 + col, 1 + (col + 1) % columns) for col in range(columns)]
    for row in range(rings - 1):
        start = 1 + row * columns
        for col in range(columns):
            a, b = start + col, start + (col + 1) % columns
            faces.append((a, a + columns, b + columns, b))
    faces.append(tuple(reversed(range(len(verts) - columns, len(verts)))))
    mesh = bpy.data.meshes.new("Continuous crown")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    crown = bpy.data.objects.new("Continuous crown", mesh)
    bpy.context.collection.objects.link(crown)

    locks = [s.bind(crown, "Continuous crown", HEAD, "hair"),
             s.lump("Nape", HEAD, "hair", (-.244, .006, 2.395), (.217, .256, .329), 9)]
    sweep = [
        (.009, .058, 2.900, .44), (.138, -.060, 2.864, .98),
        (.161, -.205, 2.770, 1), (.070, -.284, 2.627, .85),
        (-.066, -.309, 2.477, .37),
    ]
    locks.append(clay_line(s, "Side-swept fringe", HEAD, "hair", sweep, .078))
    for sign in (-1, 1):
        front_lock = [
            (.060, sign * .138, 2.822, .09), (.036, sign * .215, 2.777, .63),
            (-.007, sign * .273, 2.661, .97),
            (-.072, sign * .300, 2.471, 1), (-.145, sign * .310, 2.289, .93),
            (-.246, sign * .319, 2.106, .87), (-.277, sign * .281, 1.946 + sign * .046, .58),
            (-.229, sign * .257, 1.828 + sign * .065, .16),
        ]
        back_lock = [
            (-.170, sign * .091, 2.822, .10), (-.246, sign * .121, 2.749, .62),
            (-.323, sign * .172, 2.539, 1),
            (-.362, sign * .214, 2.307, 1.05), (-.337, sign * .242, 2.135, .91),
            (-.373, sign * .191, 1.979 + sign * .060, .60),
            (-.434, sign * .144, 1.848 + sign * .055, .17),
        ]
        locks.extend([clay_line(s, "Long face-framing wave", HEAD, "hair", front_lock, .105),
                      clay_line(s, "Long nape wave", HEAD, "hair", back_lock, .115)])
    merge_clay(s, "Single sculpted head of hair", locks, "hair", HEAD, voxel=.008)
    for yaw in (-1.19, -.86, .88):
        clay_line(s, "Swept crown groove", HEAD, "hair_ridge", [
            (*crown_point(yaw + drift, progress), width)
            for progress, drift, width in ((.10, .38, .12), (.24, .27, .36),
                                           (.39, .13, .52), (.55, 0, .45), (.68, -.10, .14))
        ], .012)
    for sign in (-1, 1):
        for shift in (0.0, .045):
            clay_line(s, "Clay strand ridge", HEAD, "hair_ridge", [
                (.031 - shift, sign * .227, 2.837, .18),
                (.022 - shift, sign * .346, 2.666, .84),
                (-.074 - shift, sign * .399, 2.465, 1),
                (-.146 - shift, sign * .402, 2.280, 1),
                (-.247 - shift, sign * .402, 2.106, .80),
                (-.275 - shift, sign * .329, 1.949 + sign * .047, .47),
                (-.233 - shift, sign * .263, 1.845 + sign * .063, .12),
            ], .016)


def costume(s):
    l = s.lump
    torso = merge_clay(s, "Presenter · torso", [
        l("Shoulder line", BODY, "skin", (-.021, 0, 1.831), (.213, .310, .218), -5),
        l("Rib cage", BODY, "skin", (-.035, 0, 1.681), (.214, .263, .259), -7),
        l("Waist contour", BODY, "skin", (-.034, 0, 1.455), (.175, .212, .204), -5),
        l("Flare to high hip", BODY, "skin", (-.056, 0, 1.355), (.190, .244, .152), -7),
        l("Rounded hips", BODY, "skin", (-.067, 0, 1.291), (.196, .266, .159), -7),
        l("Upper chest", BODY, "skin", (.154, 0, 1.798), (.194, .271, .193), -8),
    ], "skin", BODY, voxel=.012)
    torso_front = GarmentSurface(torso, 0, 1)
    for sign in (-1, 1):
        y = sign * .167
        cup = merge_clay(s, "Shaped stage top cup", [
            l("Rounded cup", BODY, "costume", (.243, y, 1.728), (.258, .195, .196), -12),
            l("Upper cup contour", BODY, "costume", (.222, y, 1.811), (.217, .173, .148), -13),
        ], "costume", BODY, voxel=.010)
        cup_front = GarmentSurface(cup, 0, 1)
        clay_line(s, "Halter strap", BODY, "trim", [
            (*cup_front.point(sign * .207, 1.865, .004), .71),
            (*cup_front.point(sign * .184, 1.918, .002), .84),
            (*torso_front.point(sign * .131, 1.970, .007), 1),
            (*torso_front.point(sign * .095, 2.005, .004), .81),
            (.032, sign * .092, 2.009, .65),
        ], .018)
        clay_line(s, "Cabaret satin piping", BODY, "trim", [
            (*cup_front.point(sign * .076, 1.676, .003), .75),
            (*cup_front.point(sign * .139, 1.630, .007), 1),
            (*cup_front.point(sign * .216, 1.627, .007), 1),
            (*cup_front.point(sign * .272, 1.662, .004), .82),
            (*cup_front.point(sign * .296, 1.747, .003), .37),
        ], .014)
        for j, height in enumerate((1.683, 1.730, 1.779)):
            for i, dy in enumerate((-.078, -.044, -.007, .032, .070)):
                z = height + abs(dy + .004) * .52 - dy * sign * .14
                l("Cabaret sequin", BODY, ("accent", "gem", "metal")[(i + j) % 3],
                  cup_front.point(y + dy, z, .002), (.011, .013, .011))
    l("Jeweled center clasp", BODY, "metal", (.371, 0, 1.699), (.047, .032, .047), -13)
    l("Center garnet", BODY, "accent", (.415, 0, 1.707), (.013, .020, .029), -13)
    clay_line(s, "Fine gold choker", BODY, "metal", [
        (.072, -.095, 2.046, .73), (.165, -.072, 2.039, 1), (.190, 0, 2.027, 1.08),
        (.165, .072, 2.039, 1), (.072, .095, 2.046, .73),
    ], .011)
    clay_line(s, "Wide halter back band", BODY, "costume", [
        (.275, -.314, 1.658, .94), (.012, -.257, 1.638, 1), (-.211, -.148, 1.633, 1),
        (-.251, 0, 1.637, 1), (-.211, .148, 1.633, 1), (.012, .257, 1.638, 1), (.275, .314, 1.658, .94),
    ], .033)

    joints = joint_positions(STANCE)
    seams = [
        l("Stage shorts hip", BODY, "costume", (-.065, 0, 1.242), (.236, .328, .155), -7),
        l("Shaped high waist", BODY, "costume", (-.044, 0, 1.329), (.210, .292, .103), -9),
    ]
    for side in ("near", "far"):
        hip, knee = [Vector(joints[f"{j}_{side}"]) for j in ("hips", "knee")]
        seams.append(s.tube("Fitted leg of stage shorts", f"thigh_{side}", "costume", hip,
                            hip.lerp(knee, .33), (.179, .169), .078))

    def shorts_weights(v):
        thigh = 1 - blend(v.z, 1.041, 1.294)
        far = blend(v.y, -.091, .091)
        return {BODY: 1 - thigh, "thigh_near": thigh * (1 - far), "thigh_far": thigh * far}

    shorts = merge_clay(s, "Weighted stage shorts", seams, "costume", weights=shorts_weights, voxel=.012)
    front = GarmentSurface(shorts, 0, 1)
    front.applique(s, "Sculpted asymmetric waistband", "trim", [
        (-.264, 1.341), (-.153, 1.368), (0, 1.351), (.152, 1.327), (.264, 1.334),
        (.262, 1.304), (.152, 1.290), (0, 1.311), (-.154, 1.332), (-.264, 1.313),
    ], .002, weights=shorts_weights)


def limbs(s):
    j = joint_positions(STANCE)
    l, t = s.lump, s.tube
    for side, sign in (("near", -1), ("far", 1)):
        shoulder, elbow, wrist = [Vector(j[f"{p}_{side}"]) for p in ("shoulder", "elbow", "hand")]
        hip, knee, foot = [Vector(j[f"{p}_{side}"]) for p in ("hips", "knee", "foot")]
        upper, lower, fist, thigh, shin, boot = [f"{p}_{side}" for p in ("bicep", "forearm", "fist", "thigh", "shin", "boot")]
        arm_axis = (elbow - shoulder).normalized()
        arm_bend = (arm_axis + (wrist - elbow).normalized()).normalized()
        leg_axis = (knee - hip).normalized()
        leg_bend = (leg_axis + (foot - knee).normalized()).normalized()

        def arm_weights(v):
            arm = blend((v - shoulder).dot(arm_axis), -.115, .110)
            forearm = blend((v - elbow).dot(arm_bend), -.083, .091)
            return {BODY: 1 - arm, upper: arm * (1 - forearm), lower: arm * forearm}

        def leg_weights(v):
            leg = blend((v - hip).dot(leg_axis), -.100, .157)
            calf = blend((v - knee).dot(leg_bend), -.102, .114)
            return {BODY: 1 - leg, thigh: leg * (1 - calf), shin: leg * calf}

        merge_clay(s, f"Skin arm · {side}", [
            l("Shoulder", upper, "skin", shoulder, (.115, .122, .133)),
            t("Upper arm", upper, "skin", shoulder, elbow, (.094, .103), .099),
            l("Rounded elbow", lower, "skin", elbow, (.082, .086, .089)),
            t("Forearm", lower, "skin", elbow, wrist, (.080, .089), .049),
        ], "skin", weights=arm_weights, voxel=.012)
        merge_clay(s, f"Skin leg · {side}", [
            l("Upper thigh", thigh, "skin", hip.lerp(knee, .19), (.159, .149, .236), sign * 8),
            t("Thigh", thigh, "skin", hip, knee, (.137, .142), .113),
            l("Knee", shin, "skin", knee, (.103, .109, .119)),
            t("Calf", shin, "skin", knee, foot, (.097, .110), .062),
        ], "skin", weights=leg_weights, voxel=.013)
        x, y, z = wrist
        fingers = []
        for i, spread in enumerate((-.049, -.015, .021, .055)):
            reach = (.138, .167, .161, .128)[i]
            fingers.append(clay_line(s, "Curled finger", fist, "skin", [
                (x + .046, y + spread * .65, z + .005, 1), (x + reach, y + spread, z + .025, .89),
                (x + reach + .006, y + spread, z - .019, .68),
            ], .025))
        merge_clay(s, f"Presenter hand · {side}", [
            l("Palm", fist, "skin", (x + .044, y, z), (.084, .081, .061)),
            l("Thumb", fist, "skin", (x + .071, y - sign * .065, z - .012), (.057, .034, .036), -15),
            *fingers,
        ], "skin", fist, voxel=.007)
        cuff = wrist.lerp(elbow, .15)
        t("Gold wrist cuff", lower, "metal", cuff, cuff.lerp(elbow, .088), (.095, .101), .014)
        x, y, _ = foot
        cuff = foot.lerp(knee, .67)
        t("Tall satin boot shaft", shin, "boots", foot.lerp(knee, .14), cuff, (.105, .119), .10)
        t("Boot collar", shin, "trim", cuff.lerp(foot, .022), cuff.lerp(foot, .088), (.113, .124), .029)
        l("Boot collar stud", shin, "metal", cuff + Vector((.047, sign * .111, -.026)), (.017, .013, .024))
        merge_clay(s, f"Heeled stage boot · {side}", [
            l("Fitted ankle", boot, "boots", (x - .014, y, .210), (.111, .109, .139), -12),
            l("Tapered toe", boot, "boots", (x + .142, y, .102), (.135, .090, .066), 12),
            t("Sloping vamp", boot, "boots", (x - .012, y, .171), (x + .141, y, .102), (.091, .061), .052),
        ], "boots", boot, voxel=.010)
        l("Platform under toe", boot, "lash", (x + .132, y, .048), (.150, .098, .036), 4)
        t("Sculpted heel", boot, "lash", (x - .071, y, .032), (x - .057, y, .158), (.048, .069), .023)


def build_presenter(rig, colors):
    s = Sculpt(rig, colors)
    sculpt_face(s)
    sculpt_hair(s)
    costume(s)
    limbs(s)
    for tag, roughness in (("skin", .73), ("hair", .63), ("lip", .48), ("boots", .50), ("costume", .57)):
        s.colors[tag].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness


BASE = dict(STANCE, hips=(-.075, 0, 1.237), neck=(.035, 0, 1.948), head=(.108, -.045, 2.577),
            shoulder_near=(.05, -.302, 1.815), shoulder_far=(.04, .305, 1.805),
            elbow_near=(.030, -.410, 1.411), hand_near=(.096, -.437, 1.168),
            elbow_far=(.353, .386, 1.660), hand_far=(.527, .285, 1.982),
            knee_near=(.13, -.15, .727), foot_near=(.29, -.18, .15),
            knee_far=(-.18, .17, .70), foot_far=(-.31, .18, .15))


def stage_poses():
    walk = []
    for i in range(32):
        phase = i / 32
        swing = cos(2 * pi * phase)
        wave = sin(2 * pi * phase)
        lift = .018 * cos(4 * pi * phase)
        pose = dict(BASE, hips=(-.075 - .019 * swing, .068 * wave, 1.237 + lift),
                    neck=(.035 + .028 * swing, -.026 * wave, 1.948 + lift),
                    head=(.108 + .015 * swing, -.050 - .038 * wave, 2.577 + lift * .57),
                    shoulder_near=(.055 + .073 * swing, -.310, 1.820 + lift),
                    shoulder_far=(.036 - .061 * swing, .307, 1.804 + lift),
                    elbow_near=(.026 + .149 * swing, -.413, 1.415 + lift),
                    hand_near=(.088 + .173 * cos(2 * pi * phase - .36), -.445, 1.205 + lift),
                    hand_far=(.524, .286, 1.978 + lift * .5),
                    rolls={"pelvis": .137 * swing, "head": -.072 * swing})
        for offset, side, sign in ((0, "near", -1), (.5, "far", 1)):
            p = (phase + offset) % 1 * 2
            x = .295 * (1 - 2 * p) if p <= 1 else -.295 * cos(pi * (p - 1))
            step = .155 * sin(pi * (p - 1)) if p > 1 else 0
            pose[f"foot_{side}"] = (x, sign * .121, .15 + step)
            pose[f"knee_{side}"] = (x * .71 + .105, sign * (.152 - .08 * step), .72 + step * .70)
            pose[f"boot_{side}"] = (.26, 0, .16 * step)
        walk.append((1, pose))
    plant = dict(BASE, hips=(-.101, -.074, 1.237), neck=(.047, -.029, 1.941),
                 head=(.106, -.046, 2.564), foot_near=(.24, -.051, .15),
                 foot_far=(-.23, .147, .15), knee_near=(.225, -.080, .714),
                 knee_far=(-.174, .117, .719), rolls={"pelvis": .096, "head": -.080})
    greeting = dict(plant, shoulder_near=(.039, -.321, 1.798), shoulder_far=(.074, .296, 1.869),
                    elbow_far=(.167, .483, 2.001), hand_far=(.190, .570, 2.393),
                    elbow_near=(.011, -.543, 1.502), hand_near=(.090, -.343, 1.386),
                    head=(.091, -.133, 2.556), rolls={"pelvis": .155, "head": -.139})
    turn = dict(greeting, hips=(-.089, -.091, 1.237), neck=(.050, -.011, 1.949),
                hand_far=(.162, .601, 2.436), head=(.127, -.025, 2.554),
                rolls={"pelvis": .176, "head": -.025})
    settle = dict(greeting, hand_far=(.177, .584, 2.408), head=(.117, -.089, 2.559),
                  rolls={"pelvis": .130, "head": -.100})
    step_pose = walk[0][1]
    return {"presenter_walk": (walk, True),
            "presenter_show": ([(7, step_pose), (12, plant), (14, greeting), (18, turn), (15, settle),
                                (12, plant), (6, step_pose)], False),
            "idle": ([(18, plant), (18, dict(plant, head=(.109, -.091, 2.562)))], True)}


def add_presenter_actions(rig, key_pose):
    rig.animation_data_create()
    data = {}
    for name, (poses, loop) in stage_poses().items():
        action = bpy.data.actions.new(name)
        action.use_fake_user = True
        action.use_frame_range = True
        rig.animation_data.action = action
        frame = 1
        for duration, pose in poses:
            key_pose(rig, pose, frame)
            frame += duration
        key_pose(rig, poses[0 if loop else -1][1], frame)
        action.frame_start, action.frame_end = 1, frame
        action.use_cyclic = loop
        data[name] = {"ticks": frame - 1, "loop": loop}
    scene = bpy.context.scene
    scene["presenter_catalog"] = json.dumps(data)
    rig.animation_data.action = bpy.data.actions["presenter_show"]
    scene.frame_end = data["presenter_show"]["ticks"] + 1
    scene.frame_set(1)
