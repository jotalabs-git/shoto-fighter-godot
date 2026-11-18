class_name Sfx
extends Node

## Banco original sintetizado al iniciar, sin assets/licencias externas.
## Sonidos polifónicos (un solo player cortaría el sonido anterior).
## Puede sustituirse cada evento por un WAV/OGG propio desde assets/audio/.
const SAMPLE_RATE := 22050
const MAX_VOICES := 12

var _players: Array[AudioStreamPlayer] = []
var _bank: Dictionary = {}
var _next_player := 0
var _variation := 0
var _effort_counter := 0

func _ready() -> void:
	for i in MAX_VOICES:
		var player := AudioStreamPlayer.new()
		player.name = "Voice%d" % i
		add_child(player)
		_players.append(player)
	_build_bank()

func play_attack(fighter: Fighter, move: MoveData) -> void:
	var kind := "kick" if SoundProfile.impact_key(move).contains("_kick_") else "punch"
	_play("swing_" + kind, -13.0)
	_effort_counter += 1
	if move != null and (move.damage >= 55 or move.is_special or _effort_counter % 3 == 0):
		play_voice(fighter.character_id, "effort_" + SoundProfile.attack_weight(move))

func play_impact(_attacker: Fighter, defender: Fighter, move: MoveData, blocked: bool = false) -> void:
	_play(SoundProfile.impact_key(move, blocked), -3.5 if not blocked else -8.0)
	if defender != null and not blocked:
		# La reacción vocal se reproduce al conectar, no por cada tick del ataque.
		play_voice(defender.character_id, "hurt")

func play_grab(fighter: Fighter) -> void:
	_play("grab", -8.0)
	play_voice(fighter.character_id, "effort_heavy")

func play_fall(character_id: String) -> void:
	_play("fall", -2.0)
	play_voice(character_id, "hurt")

func play_block() -> void:
	_play("block", -8.0)

func play_hit() -> void:
	# Compatibilidad con llamadas antiguas.
	_play("hit_punch_medium", -4.0)

func play_ko() -> void:
	_play("ko", -1.0)

func play_voice(character_id: String, action: String) -> void:
	var who := SoundProfile.fighter_voice(character_id)
	_play("voice_" + who + "_" + action, -10.0)

func _play(key: String, volume: float = 0.0) -> void:
	if _players.is_empty():
		return
	var sample: AudioStream = _bank.get(key)
	if sample == null:
		return
	# Buscar una voz libre primero, luego robar la más antigua si hay saturación.
	var player: AudioStreamPlayer = null
	for p in _players:
		if not p.playing:
			player = p
			break
	if player == null:
		player = _players[_next_player]
		_next_player = (_next_player + 1) % _players.size()
	player.stop()
	player.stream = sample
	player.volume_db = volume
	_variation += 1
	# Variación muy pequeña: evita el efecto de repetición mecánica.
	player.pitch_scale = 1.0 + float((_variation % 5) - 2) * 0.018
	player.play()

func _build_bank() -> void:
	_register("swing_punch", 360.0, 0.080, 0.86, 0.20, 101)
	_register("swing_kick", 210.0, 0.13, 0.90, 0.20, 102)
	_register("hit_punch_light", 230.0, 0.100, 0.72, 0.48, 111)
	_register("hit_punch_medium", 155.0, 0.145, 0.71, 0.60, 112)
	_register("hit_punch_heavy", 95.0, 0.225, 0.74, 0.84, 113)
	_register("hit_kick_light", 210.0, 0.115, 0.69, 0.50, 121)
	_register("hit_kick_medium", 140.0, 0.165, 0.73, 0.66, 122)
	_register("hit_kick_heavy", 79.0, 0.260, 0.77, 0.88, 123)
	_register("hit_sweep", 78.0, 0.230, 0.76, 0.85, 124)
	_register("hit_energy", 320.0, 0.250, 0.42, 0.75, 125)
	_register("block", 430.0, 0.105, 0.83, 0.42, 130)
	_register("grab", 145.0, 0.105, 0.92, 0.39, 131)
	_register("fall", 64.0, 0.310, 0.75, 0.95, 132)
	_register("ko", 52.0, 0.510, 0.55, 0.95, 133)
	for who in ["guitarist", "frontman", "neutral"]:
		var base := 155.0 if who == "guitarist" else 113.0 if who == "frontman" else 137.0
		var seed := 211 if who == "guitarist" else 311 if who == "frontman" else 411
		_register("voice_" + who + "_effort_light", base * 1.15, 0.150, 0.25, 0.50, seed, true)
		_register("voice_" + who + "_effort_heavy", base, 0.290, 0.35, 0.68, seed + 1, true)
		_register("voice_" + who + "_hurt", base * 0.83, 0.235, 0.42, 0.63, seed + 2, true)

func _register(key: String, frequency: float, duration: float, noise: float, weight: float, seed: int, voiced: bool = false) -> void:
	var custom := "res://assets/audio/" + key + ".ogg"
	if ResourceLoader.exists(custom):
		var stream := load(custom) as AudioStream
		if stream != null:
			_bank[key] = stream
			return
	_bank[key] = _synthesize(frequency, duration, noise, weight, seed, voiced)

static func _synthesize(freq: float, dur: float, noise_amount: float, weight: float, seed: int, voiced: bool) -> AudioStreamWAV:
	var count := maxi(1, int(float(SAMPLE_RATE) * dur))
	var data := PackedByteArray()
	data.resize(count * 2)
	var phase := 0.0
	var filtered_noise := 0.0
	var rng := seed
	for i in count:
		var t := float(i) / float(SAMPLE_RATE)
		var progress := t / dur
		var attack := minf(t * (95.0 if voiced else 260.0), 1.0)
		var envelope := attack * pow(maxf(1.0 - progress, 0.0), 2.0 if voiced else 2.6)
		# Ruido filtrado / golpe de aire: textura y ataque percusivo.
		rng = (rng * 1103515245 + 12345) & 0x7fffffff
		var white := float(rng) / 1073741823.5 - 1.0
		filtered_noise = lerpf(filtered_noise, white, 0.27 if voiced else 0.49)
		var curve := 1.3 - 0.67 * progress
		if voiced:
			# Síntesis vocal estilizada: armónicos con caída de afinación.
			# No pretende reemplazar una voz humana grabada.
			curve = 1.20 - 0.38 * progress + 0.018 * sin(t * 42.0)
		phase += TAU * freq * curve / float(SAMPLE_RATE)
		var body := sin(phase) * 0.68 + sin(phase * 2.0) * 0.23 + sin(phase * 3.0) * 0.09
		var transient := white * pow(maxf(1.0 - progress * 6.0, 0.0), 2.0)
		var sample := ((1.0 - noise_amount) * body + noise_amount * filtered_noise + transient * (0.12 if voiced else 0.35)) * envelope * weight
		data.encode_s16(i * 2, int(clampf(sample, -0.98, 0.98) * 32767.0))
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = SAMPLE_RATE
	wav.stereo = false
	wav.data = data
	return wav
