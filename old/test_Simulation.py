from unittest import TestCase


class TestSimulation(TestCase):
    def test_run(self):
        from Simulation import Simulation
        Simulation("test_param.json").run()
