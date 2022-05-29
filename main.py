# github page:https://github.com/Dentosal/python-sc2
# documentation: https://github.com/Dentosal/python-sc2/wiki
import sc2 as sc
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, SCV

class Bot(sc.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
    
    async def build_workers(self):
        for cc in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV) and self.supply_left > 3:
                await self.do(cc.train(SCV))
