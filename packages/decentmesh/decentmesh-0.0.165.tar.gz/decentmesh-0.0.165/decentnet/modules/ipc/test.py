import asyncio

from decentnet.modules.ipc.block_share_sub import Subscriber

sub = Subscriber()
sub.subscribe("sPfmcfxCvmMx3cwjdQWRvb2fEzoFHvDK2OGH2doUTYY=")
print(asyncio.run(sub.consume()))
