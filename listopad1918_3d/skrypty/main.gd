extends Node
## Tymczasowy szkielet (test potoku CI).

const Autotest = preload("res://skrypty/autotest.gd")


func _ready() -> void:
	var args := OS.get_cmdline_user_args() + OS.get_cmdline_args()
	if "--autotest" in args:
		var t = Autotest.new()
		var kod: int = await t.uruchom(null)
		get_tree().quit(kod)
