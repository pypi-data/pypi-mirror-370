import numpy as np
from matplotlib import pyplot as plt

from decentnet.modules.latency_balance.icosa_balancer import IcosaBalancer

np.random.seed(9595)
num_clients = 1000
clients_data = {
    f"client_{i}": {
        "in_latency": np.random.uniform(1, 500),
        "out_latency": np.random.uniform(1, 150),
        "byte_size": np.random.uniform(150, 60000)
    }
    for i in range(num_clients)
}

# Add extreme values for testing
clients_data["extreme_client_in"] = {"in_latency": 1.0, "out_latency": 100.0, "byte_size": 9600.0}
clients_data["extreme_client_out"] = {"in_latency": 1.0, "out_latency": 300.0, "byte_size": 9700.0}
clients_data["extreme_client_byte_size"] = {"in_latency": 1.0, "out_latency": 1.0, "byte_size": 3000.0}

# Perform balancing adjustments
adjustments = IcosaBalancer.balance_client_latencies(clients_data)

# Apply adjustments
adjusted_in_latency = [clients_data[client]["in_latency"] + adjustments[client]["in_latency_adjustment"]
                       for client in clients_data]
adjusted_out_latency = [clients_data[client]["out_latency"] + adjustments[client]["out_latency_adjustment"]
                        for client in clients_data]
adjusted_byte_size = [clients_data[client]["byte_size"] + adjustments[client]["byte_size_adjustment"]
                      for client in clients_data]

# Original values
original_in_latency = [client["in_latency"] for client in clients_data.values()]
original_out_latency = [client["out_latency"] for client in clients_data.values()]
original_byte_size = [client["byte_size"] for client in clients_data.values()]

# Plot histograms for before and after adjustment
fig, axs = plt.subplots(3, 2, figsize=(12, 12))
fig.suptitle("Histograms of Latency and Byte Size Values Before and After Adjustment")

# Plot in_latency
axs[0, 0].hist(original_in_latency, bins=20, alpha=0.7, color='blue')
axs[0, 0].set_title("In Latency (Before Adjustment)")
axs[0, 1].hist(adjusted_in_latency, bins=20, alpha=0.7, color='green')
axs[0, 1].set_title("In Latency (After Adjustment)")

# Plot out_latency
axs[1, 0].hist(original_out_latency, bins=20, alpha=0.7, color='blue')
axs[1, 0].set_title("Out Latency (Before Adjustment)")
axs[1, 1].hist(adjusted_out_latency, bins=20, alpha=0.7, color='green')
axs[1, 1].set_title("Out Latency (After Adjustment)")

# Plot byte_size
axs[2, 0].hist(original_byte_size, bins=20, alpha=0.7, color='blue')
axs[2, 0].set_title("Byte Size (Before Adjustment)")
axs[2, 1].hist(adjusted_byte_size, bins=20, alpha=0.7, color='green')
axs[2, 1].set_title("Byte Size (After Adjustment)")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
