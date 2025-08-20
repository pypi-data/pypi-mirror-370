import asyncio

from decentnet.modules.ipc.block_share_pub import Publisher

pub = Publisher()
asyncio.run(pub.publish_message("sPfmcfxCvmMx3cwjdQWRvb2fEzoFHvDK2OGH2doUTYY=", b"hello"))
