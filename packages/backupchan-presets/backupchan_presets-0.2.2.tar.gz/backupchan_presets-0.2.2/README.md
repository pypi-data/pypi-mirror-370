# Backup-chan presets

This is a library for creating presets for backups. A preset allows to define the destination target and what file on the system to upload, under a unique name.

## Installing

```bash
# The easy way
pip install backupchan-presets

# Installing from source
git clone https://github.com/Backupchan/presets.git backupchan-presets
cd backupchan-presets
pip install .
```

## Testing

```
pytest
```

## Example usage

```python
from backupchan_presets import Presets
from backupchan import API

api = API("host", 8000, "api-key")

# Create a new preset.
presets = Presets()
presets.add("myPreset", "00000000-0000-0000-0000-000000", "/home/me/Documents/stuff")
presets.save() # Save it into the configuration file.
presets["myPreset"].upload(api, False)

# Or load existing presets from a file.
presets.load()
presets["anotherPreset"].upload(api, False)
```
