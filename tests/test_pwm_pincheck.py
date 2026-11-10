from contextlib import redirect_stderr, redirect_stdout
import io
import unittest

from pwm_pincheck import main, pwm_channel


class PinCheckTests(unittest.TestCase):
    def invoke(self, *args):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = main(list(args))
        return result, stdout.getvalue(), stderr.getvalue()

    def test_rp2040_slice_and_channel_table(self):
        first_bank = [(n, ch) for n in range(8) for ch in ("A", "B")]
        expected = first_bank + first_bank[:14]
        self.assertEqual([pwm_channel(pin) for pin in range(30)], expected)

    def test_same_slice_different_channels_are_distinct(self):
        status, stdout, stderr = self.invoke("--board", "pico", "GP0", "gp1", "2")
        self.assertEqual(status, 0)
        self.assertIn("No PWM channel conflicts", stdout)
        self.assertEqual(stderr, "")

    def test_alias_and_duplicate_pin_are_errors(self):
        cases = [
            (("0", "16", "2"), "PWM0A"),
            (("29", "13"), "PWM6B"),
            (("5", "5"), "PWM2B"),
        ]
        for pins, channel in cases:
            with self.subTest(pins=pins):
                status, _, stderr = self.invoke(*pins)
                self.assertEqual(status, 1)
                self.assertIn(f"share {channel}", stderr)

    def test_pico_headers_exclude_internal_pins(self):
        for board in ("pico", "pico-w"):
            for pin in ("23", "24", "25", "29"):
                with self.subTest(board=board, pin=pin):
                    status, _, stderr = self.invoke("--board", board, pin)
                    self.assertEqual(status, 1)
                    self.assertIn("not exposed", stderr)
            self.assertEqual(self.invoke("--board", board, "22", "26", "28")[0], 0)
        self.assertEqual(self.invoke("29")[0], 0)

    def test_aquiles_bench_assignment(self):
        pins = ("--board", "pico", "0", "2", "4", "6", "8", "10")
        self.assertEqual(self.invoke(*pins)[0], 0)
        status, _, stderr = self.invoke(*pins, "--header-pin", "29")
        self.assertEqual(status, 1)
        self.assertEqual(stderr, "GP29 is not exposed on the pico header.\n")

    def test_auxiliary_pin_only_checks_header_exposure(self):
        self.assertEqual(self.invoke("--board", "pico", "0", "--header-pin", "16")[0], 0)

    def test_invalid_arguments_are_usage_errors(self):
        invalid = [
            (), ("-1",), ("30",), ("pwm",), ("--board", "pico-2-w", "1"),
            ("0", "--header-pin", "16"),
        ]
        for args in invalid:
            with self.subTest(args=args), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    main(list(args))
                self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
