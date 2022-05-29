# github page for the library being used:https://github.com/Dentosal/python-sc2
# documentation for sc2 library: https://github.com/Dentosal/python-sc2/wiki
import random as rand
import sc2 as sc
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, SCV, SUPPLYDEPOT, REFINERY, BARRACKS, MARINE

class BigBoy(sc.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()

        if self.supply_workers > 16:
            await self.build_workers()

        await self.build_supplydepo()

        await self.build_barracks()

        if self.units(BARRACKS).exists:
            await self.train_marines()

        if self.units(BARRACKS).exists:
            await self.build_vespene()

        await self.attack()
    
    #scouting with worker
    async def send_scout(self):
        worker = self.units(SCV).ready
        if worker.exists:
            await worker.attack(self.enemy_start_locations)

    #building workers
    async def build_workers(self):
        for cc in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV) and self.supply_left <= 2:
                await self.do(cc.train(SCV))

    #building supply depots 
    async def build_supplydepo(self):
        if self.supply_left < 3 and not self.already_pending(SUPPLYDEPOT):
            ccs = self.units(COMMANDCENTER).ready
            if ccs.exists:
                if self.can_afford(SUPPLYDEPOT):
                    await self.build(SUPPLYDEPOT, near = ccs.first)

    #building barracks
    async def build_barracks(self):
        ccs = self.units(COMMANDCENTER).ready
        if ccs.exists:
            if not self.units(BARRACKS).exists:
                if self.can_afford(BARRACKS):
                    await self.build(BARRACKS, near = ccs.first)
    #training marines 
    async def train_marines(self):
        if self.supply_army <= 10:
            for br in self.units(BARRACKS).ready.noqueue:
                await self.do(br.train(MARINE))

    #building refineries 
    async def build_vespene(self):
        for ccs in self.units(COMMANDCENTER).ready: 
            vesp = self.state.vespene_geyser.closer_than(ccs, 15.0)
            for v in vesp: 
                if not self.can_afford(REFINERY):
                    break
                worker = self.select_build_worker(v.position)
                if worker is None:
                    break
                if self.units(REFINERY).closer_than(1.0, v).exists and self.supply_cap > 15:
                    await self.do(worker.build(REFINERY, v)) 

    #attacking with units 
    async def attack(self):
        if self.units(MARINE).amount > 9:
            if len(self.known_enemy_units) > 0:
                for u in self.units(MARINE).idle:
                    await self.do(u.attack(rand.choice(self.known_enemy_units)))
        elif self.units(MARINE).amount > 14:
            for u in self.units(MARINE).idle:
                await self.do(u.attack(self.find_enemy(self.state)))

    #finding enemy units
    def find_enemy(self, state):
        if len(self.known_enemy_units > 0):
            return rand.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures > 0): 
            return rand.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, BigBoy()), 
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)
