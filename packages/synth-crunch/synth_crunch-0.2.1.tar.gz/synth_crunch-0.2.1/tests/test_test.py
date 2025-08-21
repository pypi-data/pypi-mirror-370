import unittest
from typing import cast

from synth_crunch.interface import GenerateSimulationsOutput
from synth_crunch.test import SimulationFormatError, validate_output


class ValidateOutputTest(unittest.TestCase):

    def test_root_not_list(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=cast(GenerateSimulationsOutput, {}),
                num_simulations=0,
                expected_point_count=0
            )

        self.assertIn(
            "must return a list of simulations",
            str(context.exception),
        )

    def test_not_right_amount_of_simulations(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[], [], []],
                num_simulations=2,
                expected_point_count=0
            )

        self.assertEqual(
            "expected 2 simulations, got 3",
            str(context.exception),
        )

    def test_simulation_is_not_a_list(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=cast(GenerateSimulationsOutput, [[], {}]),
                num_simulations=2,
                expected_point_count=0
            )

        self.assertIn(
            "simulation at index 1 is not a list, got",
            str(context.exception),
        )

    def test_simulation_not_expected_number_of_point(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{}, {}, {}]],
                num_simulations=1,
                expected_point_count=2
            )

        self.assertEqual(
            "simulation at index 0 has 3 points, expected 2",
            str(context.exception),
        )

    def test_simulation_point_not_a_dict(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=cast(GenerateSimulationsOutput, [[[]]]),
                num_simulations=1,
                expected_point_count=1
            )

        self.assertIn(
            "point at index 0[0] is not a dict, got ",
            str(context.exception),
        )

    def test_simulation_point_not_the_right_keys(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{
                    "time": "",
                    "value": 100,
                }]],
                num_simulations=1,
                expected_point_count=1
            )

        self.assertIn(
            "point at index 0[0] has keys ",
            str(context.exception),
        )

    def test_simulation_point_time_is_not_a_string(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{
                    "time": True,
                    "price": 100,
                }]],
                num_simulations=1,
                expected_point_count=1
            )

        self.assertIn(
            "time at index 0[0] is not a string, got ",
            str(context.exception),
        )

    def test_simulation_point_time_is_not_iso_8601(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{
                    "time": "x",
                    "price": 100,
                }]],
                num_simulations=1,
                expected_point_count=1
            )

        self.assertIn(
            "time at index 0[0] is not a valid ISO 8601 string: ",
            str(context.exception),
        )

    def test_simulation_point_price_is_not_a_number(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{
                    "time": "2024-01-01T00:00:00",
                    "price": True,
                }]],
                num_simulations=1,
                expected_point_count=1
            )

        self.assertIn(
            "price at index 0[0] is not a number, got ",
            str(context.exception),
        )

        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{
                    "time": "2024-01-01T00:00:00",
                    "price": "x",
                }]],
                num_simulations=1,
                expected_point_count=1
            )

        self.assertIn(
            "price at index 0[0] is not a number, got ",
            str(context.exception),
        )

    def test_simulation_point_price_is_nan(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{
                    "time": "2024-01-01T00:00:00",
                    "price": float('nan'),
                }]],
                num_simulations=1,
                expected_point_count=1
            )

        self.assertEqual(
            "price at index 0[0] is nan",
            str(context.exception),
        )

    def test_simulation_point_price_is_inf(self):
        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{
                    "time": "2024-01-01T00:00:00",
                    "price": float('inf'),
                }]],
                num_simulations=1,
                expected_point_count=1
            )

        self.assertEqual(
            "price at index 0[0] is +inf",
            str(context.exception),
        )

        with self.assertRaises(SimulationFormatError) as context:
            validate_output(
                simulations=[[{
                    "time": "2024-01-01T00:00:00",
                    "price": -float('inf'),
                }]],
                num_simulations=1,
                expected_point_count=1
            )

        self.assertEqual(
            "price at index 0[0] is -inf",
            str(context.exception),
        )

    def test_valid(self):
        validate_output(
            simulations=[[{
                "time": "2024-01-01T00:00:00",
                "price": 123.45,
            }]],
            num_simulations=1,
            expected_point_count=1
        )
