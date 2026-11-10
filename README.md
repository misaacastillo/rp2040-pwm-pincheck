# RP2040 PWM Pin Check

Check a motor-control or other PWM pin assignment before wiring a Raspberry Pi
Pico or Pico W. This dependency-free Python CLI prints each GPIO's PWM slice
and compare channel, flags aliases, and can check which pins reach the board
header. It runs on a computer without the Pico SDK or a connected board.

## Quick start

Use Python 3.10 or newer.

```sh
git clone --branch v0.1.0 --depth 1 https://github.com/misaacastillo/rp2040-pwm-pincheck.git
cd rp2040-pwm-pincheck
python3 pwm_pincheck.py --board pico GP0 GP1 GP2
```

The three pins have distinct compare channels. GP0 and GP1 use separate
channels of slice 0, so they can have independent duty values and share the
slice's counter and frequency.

```sh
python3 pwm_pincheck.py --board pico GP0 GP16 GP2
```

GP0 and GP16 both map to PWM0A. A write through either GPIO's PWM channel changes
the same compare value. This is the pin combination used in the
[SimpleFOC 3-PWM report](https://github.com/simplefoc/Arduino-FOC/issues/589).

Enter chip GPIO numbers such as `GP16`. Connector positions use a separate numbering scheme.
The default `--board rp2040` checks chip GPIOs 0–29. Use `--board pico` or
`--board pico-w` to check the board header, which exposes GP0–GP22 and GP26–GP28.
Use `--header-pin` for an auxiliary pin such as a gate-enable or direction
signal. It checks exposure for that pin while leaving it out of PWM alias analysis.

| Exit code | Meaning |
| --- | --- |
| `0` | No PWM alias or board-header conflict found. |
| `1` | An alias, repeated PWM pin, or pin unavailable on the selected header was found. |
| `2` | The command or GPIO argument is invalid. |

## Aquiles bench assignment

The historical DRV8301 bench sketch from Aquiles uses six PWM signals on GP0,
GP2, GP4, GP6, GP8, and GP10, plus an enable signal on GP29.

```sh
python3 pwm_pincheck.py --board pico 0 2 4 6 8 10 --header-pin 29
```

The six PWM channels are distinct. The board check reports that GP29 is
unavailable on the standard Pico header. This is a static check of the
published assignment. The separate GP0/GP16 example above is a synthetic
SimpleFOC reproduction.

Aquiles is a team project credited to IMPA TRQ. These examples cite the
[original RP2040 PWM experiment](https://github.com/ZaCoso/Aquiles_Project/commit/d3c6e3ffc45a179c7de4edb4eb7603dd17b6b4ed)
and the [DRV8301 bench commit](https://github.com/ZaCoso/Aquiles_Project/commit/5b8298c65b6035a3fc9f9f743b9faa0661b8fea4)
attributed to Misael Castillo. The [Aquiles license](https://github.com/ZaCoso/Aquiles_Project/blob/a3d2e4bdd83270054a9b82539448bb7960d39b9d/LICENSE)
remains with that project.

## Tests and scope

```sh
python3 -m unittest discover -s tests -v
```

The tests cover all 30 chip GPIO mappings, distinct channels within a slice,
aliases, repeated GPIOs, invalid arguments, board pin exposure, and the
historical Aquiles assignment. GitHub Actions runs the same command.

This tool covers RP2040 pin mapping and the Pico and Pico W headers. PWM
frequency, dead time, voltage, and motor or gate-driver operation require
separate validation. Pico 2 boards use a different chip and need their own
mapping.

## References

- [Pico SDK PWM mapping](https://github.com/raspberrypi/pico-sdk/blob/2.2.0/src/rp2_common/hardware_pwm/include/hardware/pwm.h#L87-L135)
- [RP2040 datasheet, PWM GPIO mapping](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=523)
- [Pico pinout](https://pip-assets.raspberrypi.com/categories/610-raspberry-pi-pico/documents/RP-008309-DS-1-Pico-R3-A4-Pinout.pdf?disposition=inline)
- [Pico W pinout](https://pip-assets.raspberrypi.com/categories/686-raspberry-pi-pico-w/documents/RP-008315-DS-1-PicoW-A4-Pinout.pdf)

The tool and tests use the [MIT License](LICENSE).
