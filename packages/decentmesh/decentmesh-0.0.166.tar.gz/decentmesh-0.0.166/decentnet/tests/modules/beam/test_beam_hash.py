import unittest

from decentnet.modules.comm.beam import Beam


class TestBeamHash(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This method is called before tests in an individual class are run
        pass

    def test_create_beam_hash_length(self):
        # Test that the hash length is correct for blake2b (default is 64 characters long)
        beam_hash = Beam.create_beam_hash(21112)
        self.assertEqual(len(beam_hash), 16,
                         "The hash should be 128 characters long for the default blake2b.")


if __name__ == '__main__':
    unittest.main()
