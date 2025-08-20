import asyncio
import random
import string
import unittest

from decentnet.modules.forwarding.flow_net import FlowNetwork


def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


class TestFlowNetworkLargeScale(unittest.TestCase):
    @unittest.skip("Skipping this test, not going to do performance testing")
    def test_large_scale_network(self):
        fn = FlowNetwork(False)
        node_count = 100  # Adjust node_count and edge_count for desired scale
        edge_count = 500

        nodes = [generate_random_string(20) for _ in range(node_count)]

        # Adding nodes to the network - optional, since adding an edge would auto-create nodes
        # for node in nodes:
        #     fn.graph.add_node(node)

        # Adding a large number of edges
        for _ in range(edge_count):
            node_a = random.choice(nodes)
            node_b = random.choice(nodes)
            while node_b == node_a:
                node_b = random.choice(nodes)  # Ensure we don't create self-loops
            capacity = random.randint(1, 100)  # Random capacity for testing
            asyncio.run(fn.add_edge(node_a, node_b, capacity, _save_to_db=False))

        self.assertEqual(len(fn.graph.nodes), node_count,
                         f"Graph should have {node_count} nodes")
        self.assertTrue(len(fn.graph.edges) <= edge_count * 2,
                        f"Graph should have at most {edge_count * 2} edges")

        # Test path finding with a randomly selected source and sink
        source, sink = random.sample(nodes, 2)
        path, max_flow = fn.get_path(source, sink)
        self.assertIsInstance(path, list, "Path should be a list")
        self.assertIsInstance(max_flow, int, "Max flow should be an integer")
        self.assertTrue(max_flow >= 0, "Max flow should be non-negative")


if __name__ == '__main__':
    unittest.main()
