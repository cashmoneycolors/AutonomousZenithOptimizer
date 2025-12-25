import unittest

from python_modules import realtime_pricefeed as rtp
from python_modules.electricity_cost_manager import get_cost_for_rig, calculate_net_profit


class TestRealtimePricefeedAndPower(unittest.TestCase):
    def test_pricefeed_status(self):
        status = rtp.get_status()
        self.assertIn('active_exchanges', status)
        self.assertIn('monitoring_active', status)

    def test_cost_for_rig(self):
        rig = {'id': 'TEST_GPU', 'power_consumption': 500, 'hash_rate': 100}
        cost = get_cost_for_rig(rig)
        self.assertGreaterEqual(cost['kwh_per_hour'], 0)
        self.assertIn('cost_per_kwh', cost)

    def test_calculate_net_profit(self):
        rig = {'id': 'TEST_NEG', 'power_consumption': 500, 'profit_per_day': 0}
        result = calculate_net_profit(rig, hours=1)
        self.assertIn('net_profit', result)


if __name__ == '__main__':
    unittest.main()
