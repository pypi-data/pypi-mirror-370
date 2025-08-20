import asyncio
import unittest

from decentnet.modules.forwarding.flow_net import FlowNetwork


class TestFlowNetwork(unittest.TestCase):

    def test_add_edge(self):
        fn = FlowNetwork(False)
        asyncio.run(fn.add_edge('A', 'B', 10, _save_to_db=False))
        self.assertTrue(fn.graph.has_edge('A', 'B'), "Edge A -> B should exist")
        self.assertEqual(fn.graph['A']['B']['capacity'], 10,
                         "Edge A -> B should have a capacity of 10")

    def test_rm_edge(self):
        fn = FlowNetwork(False)
        asyncio.run(fn.add_edge('A', 'B', 10, _save_to_db=False))
        self.assertTrue(fn.graph.has_edge('A', 'B'), "Edge A -> B should exist before removal")

        asyncio.run(fn.rm_edge('A', 'B', _save_to_db=False))
        self.assertFalse(fn.graph.has_edge('A', 'B'), "Edge A -> B should not exist after removal")

        # Attempt to remove a non-existent edge
        result = asyncio.run(fn.rm_edge('C', 'D', _save_to_db=False))
        self.assertFalse(result, "Removing a non-existent edge should return False")

    def test_get_path(self):
        fn = FlowNetwork(False)
        asyncio.run(fn.add_edge('A', 'B', 10, _save_to_db=False))
        asyncio.run(fn.add_edge('B', 'C', 5, _save_to_db=False))

        path, max_flow = fn.get_path('A', 'C')
        self.assertEqual(path, ['A', 'B', 'C'], "Path A -> C should be found")
        self.assertEqual(max_flow, 5, "Max flow A -> C should be 5")
        self.assertEqual(fn.graph['B']['C']['capacity'], 0,
                         "Capacity B -> C should be updated to 0")
        path, max_flow = fn.get_path('B', 'A')
        # Test backwards
        self.assertEqual(path, ['B', 'A'], "Path B -> A")

    def test_add_edge_with_not_known(self):
        fn = FlowNetwork(False)
        result = asyncio.run(fn.add_edge('S', 'B', 10))
        self.assertFalse(result, "Adding edge with 'S' should fail")
        self.assertTrue(fn.graph.has_node('S'),
                        "'S' node should not be added")



if __name__ == '__main__':
    unittest.main()
