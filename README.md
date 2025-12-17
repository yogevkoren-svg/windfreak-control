# RF Generator Control Script (Windfreak SynthHD)

This repository contains a Python script for controlling a Windfreak SynthHD RF generator.
The script is used to generate RF pulse sequences for experimental testing of the device,
including frequency sweeps and on/off timing control.

The setup and sequence are intended for biological viability experiments and related
bench tests.

---

## Requirements

- Python 3.8 or newer
- Windfreak Python library (`windfreak`)
- USB connection to the Windfreak SynthHD device

---

## Operating System Notes

### Linux
- The device typically appears as `/dev/ttyACM0` (or similar).
- You may need to allow user access to the device:
  ```bash
  sudo chown $USER:$USER /dev/ttyACM0
