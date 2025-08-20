import unittest

import numpy as np

from decentnet.modules.latency_balance.icosa_balancer import IcosaBalancer


class TestIcosaBalancer(unittest.TestCase):
    def test_balance_client_latencies(self):
        # Generate test data with a mix of regular and extreme values
        clients_data = {
            f"client_{i}": {
                "in_latency": np.random.uniform(50, 150),
                "out_latency": np.random.uniform(50, 150),
                "byte_size": np.random.uniform(1000, 2000)
            }
            for i in range(497)
        }

        # Add extreme values for testing
        clients_data["extreme_client_in"] = {"in_latency": 300.0, "out_latency": 100.0, "byte_size": 1600.0}
        clients_data["extreme_client_out"] = {"in_latency": 80.0, "out_latency": 300.0, "byte_size": 1700.0}
        clients_data["extreme_client_byte_size"] = {"in_latency": 70.0, "out_latency": 110.0,
                                                    "byte_size": 3000.0}

        # Run the balancer
        adjustments = IcosaBalancer.balance_client_latencies(clients_data)

        # Apply adjustments
        final_in_latencies = [
            clients_data[client]["in_latency"] + adjustments[client]["in_latency_adjustment"]
            for client in clients_data
        ]
        final_out_latencies = [
            clients_data[client]["out_latency"] + adjustments[client]["out_latency_adjustment"]
            for client in clients_data
        ]
        final_byte_sizes = [
            clients_data[client]["byte_size"] + adjustments[client]["byte_size_adjustment"]
            for client in clients_data
        ]

        # Check that final values are close to the target values
        for value in final_in_latencies:
            self.assertAlmostEqual(value, IcosaBalancer.IN_LATENCY_TARGET,
                                   delta=IcosaBalancer.TOLERANCE_LATENCY * IcosaBalancer.IN_LATENCY_TARGET)

        for value in final_out_latencies:
            self.assertAlmostEqual(value, IcosaBalancer.OUT_LATENCY_TARGET,
                                   delta=IcosaBalancer.TOLERANCE_LATENCY * IcosaBalancer.OUT_LATENCY_TARGET)

        for value in final_byte_sizes:
            self.assertAlmostEqual(value, IcosaBalancer.BYTE_SIZE_TARGET,
                                   delta=IcosaBalancer.TOLERANCE_BYTE_SIZE * IcosaBalancer.BYTE_SIZE_TARGET)


if __name__ == '__main__':
    unittest.main()
