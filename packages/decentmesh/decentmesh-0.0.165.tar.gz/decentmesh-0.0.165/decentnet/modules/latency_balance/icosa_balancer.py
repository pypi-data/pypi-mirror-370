import numpy as np


class IcosaBalancer:
    IN_LATENCY_TARGET = 50.0
    OUT_LATENCY_TARGET = 50.0
    BYTE_SIZE_TARGET = 1500.0
    TOLERANCE_LATENCY = 0.05  # 5% tolerance for latencies
    TOLERANCE_BYTE_SIZE = 0.1  # 10% tolerance for byte size
    MAX_ITERATIONS = 50

    @staticmethod
    def balance_client_latencies(clients):
        data_matrix = np.array([[client['in_latency'], client['out_latency'], client['byte_size']]
                                for client in clients.values()])

        targets = np.array([IcosaBalancer.IN_LATENCY_TARGET, IcosaBalancer.OUT_LATENCY_TARGET,
                            IcosaBalancer.BYTE_SIZE_TARGET])
        tolerances = np.array([IcosaBalancer.TOLERANCE_LATENCY * IcosaBalancer.IN_LATENCY_TARGET,
                               IcosaBalancer.TOLERANCE_LATENCY * IcosaBalancer.OUT_LATENCY_TARGET,
                               IcosaBalancer.TOLERANCE_BYTE_SIZE * IcosaBalancer.BYTE_SIZE_TARGET])

        adjustments_matrix = np.zeros_like(data_matrix)

        for iteration in range(IcosaBalancer.MAX_ITERATIONS):
            adjustments_made = False

            # Calculate current values with adjustments
            final_values = data_matrix + adjustments_matrix
            deviations = final_values - targets
            abs_deviations = np.abs(deviations)

            # Check if each metric is within tolerance for each client
            within_tolerance = abs_deviations <= tolerances

            # If all values are within tolerance, stop adjusting
            if within_tolerance.all():
                break

            # Adjust extreme values
            for i in range(data_matrix.shape[0]):
                for j in range(3):  # For in_latency, out_latency, byte_size
                    if not within_tolerance[i, j]:  # Adjust only if outside tolerance
                        adjustment_step = -0.1 * deviations[i, j]  # Incremental step towards target
                        adjustments_matrix[i, j] += adjustment_step
                        adjustments_made = True

            # Stop if no adjustments were made in an iteration
            if not adjustments_made:
                break

        # Map final adjustments to each client
        client_ids = list(clients.keys())
        adjustments = {client_ids[i]: {
            'in_latency_adjustment': adjustments_matrix[i, 0],
            'out_latency_adjustment': adjustments_matrix[i, 1],
            'byte_size_adjustment': adjustments_matrix[i, 2]
        } for i in range(len(client_ids))}

        return adjustments
