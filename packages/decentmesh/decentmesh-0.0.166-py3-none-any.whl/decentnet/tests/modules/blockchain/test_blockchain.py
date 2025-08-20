import asyncio
import os
import random
import unittest
from random import randint as ri

import rich

from decentnet.consensus.block_sizing import HASH_LEN
from decentnet.consensus.blockchain_params import BlockchainParams
from decentnet.consensus.compress_params import COMPRESSION_LEVEL_LZ4
from decentnet.modules.blockchain.blockchain import Blockchain
from decentnet.modules.pow.difficulty import Difficulty


class BlockchainTests(unittest.TestCase):
    def test_init(self):
        blockchain: Blockchain = Blockchain("some_msg")
        asyncio.run(blockchain.finish_blockchain_init())
        seed = blockchain.chain[0]
        print(f"Succeed {seed.compute_hash().value_as_hex()}")

    def test_insertion(self):
        blockchain: Blockchain = Blockchain("some_msg")
        asyncio.run(blockchain.finish_blockchain_init())

        try:
            b = blockchain.template_next_block(b"aqweqe", BlockchainParams.low_diff_argon)
            b.mine()
            self.assertTrue(asyncio.run(blockchain.insert(b)))
        except Exception as ex:
            self.fail(f"Thrown {ex}")
        self.assertEqual(len(blockchain.chain), 2)

    def test_insertion_long(self):
        next_diff = Difficulty(1, 8, 1, 8, HASH_LEN, COMPRESSION_LEVEL_LZ4)
        blockchain: Blockchain = Blockchain("some_msg", next_difficulty=next_diff)
        asyncio.run(blockchain.finish_blockchain_init())

        b_len = int(os.getenv("TEST_BLOCKS", 5000))

        for i in range(b_len):
            print(f"Mining {i}/{b_len} Block")
            testdata = random.randbytes(8)
            try:
                b = blockchain.template_next_block(testdata, next_diff)
                b.mine()
                self.assertTrue(asyncio.run(blockchain.insert(b)))
            except Exception as ex:
                self.fail(f"Thrown {ex}")
        self.assertEqual(len(blockchain), b_len + 1)

    def test_insertion_short_diff_dynamic(self):
        rich.print("[red]This test can take hours to run[/red]")
        blockchain: Blockchain = Blockchain("veeery long test")
        asyncio.run(blockchain.finish_blockchain_init())

        b_len = int(os.getenv("TEST_BLOCKS", 500))

        for i in range(b_len):
            testdata = random.randbytes(random.randint(1, 5000))
            diff = Difficulty(ri(1, 8), BlockchainParams.low_diff_sha256.m_cost,
                              BlockchainParams.low_diff_sha256.p_cost, ri(1, 10),
                              BlockchainParams.low_diff_sha256.hash_len_chars, COMPRESSION_LEVEL_LZ4)

            blockchain.difficulty = diff
            b = blockchain.template_next_block(testdata, diff)
            b.mine()

            self.assertTrue(asyncio.run(blockchain.insert(b)))

        self.assertEqual(len(blockchain), b_len + 1)

    def test_insertion_very_long_intensive(self):
        rich.print("[red]This test can take hours to run[/red]")
        blockchain: Blockchain = Blockchain("veeery long test")
        asyncio.run(blockchain.finish_blockchain_init())

        b_len = int(os.getenv("TEST_BLOCKS", 5000))

        for i in range(b_len):
            testdata = random.randbytes(random.randint(1, 5000))
            diff = Difficulty(ri(1, 8), BlockchainParams.low_diff_sha256.m_cost,
                              BlockchainParams.low_diff_sha256.p_cost, ri(1, 10),
                              BlockchainParams.low_diff_sha256.hash_len_chars, COMPRESSION_LEVEL_LZ4)

            blockchain.difficulty = diff
            b = blockchain.template_next_block(testdata, diff)
            b.mine()

            self.assertTrue(asyncio.run(blockchain.insert(b)))

        self.assertEqual(len(blockchain), b_len + 1)


if __name__ == '__main__':
    unittest.main()
