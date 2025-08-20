import pytest
from backupchan_presets import Presets, Preset

def test_preset_from_dict():
    json_preset = {
        "location": "/dev/null",
        "target_id": "deadbeef-dead-beef-dead-beefdeadbeef"
    }

    preset = Preset.from_dict(json_preset)
    assert preset.location == json_preset["location"]
    assert preset.target_id == json_preset["target_id"]

def test_add_preset():
    presets = Presets()
    presets.add("test", "/t/e/s/t", "00000000-0000-0000-0000-000000000000")
    assert presets["test"]

def test_remove_preset():
    presets = Presets()
    presets.add("a", "/t/e/s/t", "a")
    presets.remove("a")

    with pytest.raises(KeyError):
        presets["a"]

def test_load(tmp_path):
    config_path = tmp_path / "presets.json"
    presets = Presets(str(config_path))
    presets.add("testing", "/baba/bobo", "fffffff")
    presets.save()

    new_presets = Presets(str(config_path))
    new_presets.load()
    assert new_presets["testing"] == presets["testing"]

def test_iterate():
    presets = Presets()
    presets.add("testing", "/a", "aaa")
    for preset_name in presets:
        assert preset_name == "testing"
        break

def test_len():
    presets = Presets()
    presets.add("", "", "")
    assert len(presets) == 1
