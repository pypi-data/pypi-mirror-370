import unittest

from synth_crunch.interface import SynthMiner


class SynthMinerTest(unittest.TestCase):

    def test_cannot_instanciate_directly(self):
        with self.assertRaises(TypeError) as context:
            SynthMiner()  # type: ignore

    def test_cannot_instanciate_without_implementing_required_method(self):
        class MyMiner(SynthMiner):
            pass

        with self.assertRaises(TypeError) as context:
            MyMiner()  # type: ignore
