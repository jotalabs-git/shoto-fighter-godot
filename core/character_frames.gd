class_name CharacterFrames
extends RefCounted

## Lee animaciones desde assets/characters/<id>/manifest.json.
## Si un personaje aún no tiene arte completo, usa Kung Fu Man como
## respaldo temporal sin afectar las reglas de combate.
##
## Formato compatible con assets/kfm/manifest.json; el ancla axis
## mantiene los pies en el origen del Fighter.
static var _frames_cache: Dictionary = {}
static var _axis_cache: Dictionary = {}

static func get_frames(character_id: String) -> SpriteFrames:
	var folder := _asset_folder(character_id)
	if folder == "":
		return KfmFrames.get_frames()
	if _frames_cache.has(folder):
		return _frames_cache[folder]
	var built := _build(folder)
	if built == null:
		return KfmFrames.get_frames()
	_frames_cache[folder] = built
	return built

static func get_axis(character_id: String) -> Vector2:
	var folder := _asset_folder(character_id)
	if folder == "":
		KfmFrames.get_frames()
		return KfmFrames.axis
	if not _axis_cache.has(folder):
		get_frames(character_id)
	if _axis_cache.has(folder):
		return _axis_cache[folder]
	KfmFrames.get_frames()
	return KfmFrames.axis

static func has_custom_art(character_id: String) -> bool:
	return _asset_folder(character_id) != ""

static func _asset_folder(character_id: String) -> String:
	# Solo los IDs registrados y con manifiesto pueden cargar arte.
	var folder := CharacterRegistry.asset_folder(character_id)
	if folder == "":
		return ""
	if not FileAccess.file_exists(folder + "/manifest.json"):
		return ""
	return folder

static func _build(folder: String) -> SpriteFrames:
	var file := FileAccess.open(folder + "/manifest.json", FileAccess.READ)
	if file == null:
		return null
	var data = JSON.parse_string(file.get_as_text())
	if not (data is Dictionary):
		return null
	if not data.has("axis") or not data.has("anims"):
		return null
	var ax = data["axis"]
	var animations = data["anims"]
	if not (ax is Array) or ax.size() != 2 or not (animations is Dictionary):
		return null
	if not animations.has("idle"):
		return null
	var frames := SpriteFrames.new()
	if frames.has_animation("default"):
		frames.remove_animation("default")
	for anim in animations:
		var info = animations[anim]
		if not (info is Dictionary) or not info.has("frames") or not info.has("durs"):
			return null
		var count := int(info["frames"])
		var durations = info["durs"]
		if count < 1 or not (durations is Array) or durations.size() != count:
			return null
		frames.add_animation(anim)
		frames.set_animation_loop(anim, bool(info.get("loop", false)))
		frames.set_animation_speed(anim, 60.0)
		for i in range(count):
			var path := "%s/%s/%03d.png" % [folder, anim, i]
			var tex := load(path) as Texture2D
			if tex == null:
				return null
			frames.add_frame(anim, tex, maxf(float(durations[i]), 0.001))
	# Requerimos idle para no dejar personajes invisibles. El Fighter puede
	# sustituir otras animaciones ausentes por idle.
	if frames.get_frame_count("idle") == 0:
		return null
	_axis_cache[folder] = Vector2(float(ax[0]), float(ax[1]))
	return frames
