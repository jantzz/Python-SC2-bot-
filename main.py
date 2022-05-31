# github page for the library being used:https://github.com/Dentosal/python-sc2
# documentation for sc2 library: https://github.com/Dentosal/python-sc2/wiki
import random as rand
import sc2 as sc
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, SCV, SUPPLYDEPOT, REFINERY, BARRACKS, MARINE, REAPER, HELLION, FACTORY, ORBITALCOMMAND

# add timing

class BigBoy(sc.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        #await self.send_scout()

        if self.supply_workers < 40:
            await self.build_workers()

        await self.build_supplydepo()

        await self.build_barracks()

        if self.units(BARRACKS).exists:
            await self.train_marines()
            await self.build_vespene()
            await self.expand()
            await self.build_factory()

        await self.attack()
    
    #scouting with worker
    #async def send_scout(self):
     #   worker = self.units(SCV).ready
      #  if worker.exists:
       #     await worker.move(self.enemy_start_locations)

    #building workers
    async def build_workers(self):
        for cc in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV):
                await self.do(cc.train(SCV))


    #building supply depots 
    async def build_supplydepo(self):
        ccs = self.units(COMMANDCENTER).ready
        if  ccs.exists:
            if self.supply_used == 14 and not self.already_pending(SUPPLYDEPOT) and self.can_afford(SUPPLYDEPOT):
                await self.build(SUPPLYDEPOT, near = ccs.first)
            elif self.supply_left < 5 and not self.already_pending(SUPPLYDEPOT):
                if self.can_afford(SUPPLYDEPOT):
                    await self.build(SUPPLYDEPOT, near = ccs.first)

    #building barracks
    async def build_barracks(self):
        ccs = self.units(COMMANDCENTER).ready
        if ccs.exists:
            if self.supply_used == 15 or self.supply_used == 66: 
                if self.supply_used == 66 and self.units(BARRACKS) <= 3: 
                    if not self.already_pending(BARRACKS) and self.can_afford(BARRACKS):
                        await self.build(BARRACKS, near = ccs.first)
                if not self.already_pending(BARRACKS) and self.can_afford(BARRACKS):
                    await self.build(BARRACKS, near = ccs.first)

    #training marines 
    async def train_marines(self):
        if self.supply_army <= 20:
            for br in self.units(BARRACKS).ready.noqueue:
                await self.do(br.train(MARINE))

    #training reapers
    async def train_reaper(self):
        if self.supply_used == 19:
            for br in self.units(BARRACKS).ready.noqueue:
                await self.do(br.train(REAPER))

    #building refineries 
    async def build_vespene(self):
        for ccs in self.units(COMMANDCENTER).ready: 
            vesp = self.state.vespene_geyser.closer_than(10.0, ccs)
            for v in vesp: 
                if not self.can_afford(REFINERY):
                    break
                worker = self.select_build_worker(v.position)
                if worker is None:
                    break
                if not self.units(REFINERY).closer_than(1.0, v).exists:
                    await self.do(worker.build(REFINERY, v)) 

    #building a factory
    async def build_factory(self):
            ccs = self.units(COMMANDCENTER).ready
            if ccs.exists:
                if self.supply_used >= 20 and not self.already_pending(FACTORY) and self.can_afford(FACTORY):
                    await self.build(FACTORY, near = ccs.first)

    #expanding 
    async def expand(self):
        if self.units(COMMANDCENTER).amount < 2 and self.can_afford(COMMANDCENTER):
            await self.expand_now()

    #attacking with units 
    async def attack(self):
        if self.units(MARINE).amount > 14:
            for u in self.units(MARINE).idle:
                await self.do(u.attack(self.find_enemy(self.state)))
        elif self.units(MARINE).amount > 9:
            if len(self.known_enemy_units) > 0:
                for u in self.units(MARINE).idle:
                    await self.do(u.attack(rand.choice(self.known_enemy_units)))

    #finding enemy units
    def find_enemy(self, state):
        if len(self.known_enemy_units) > 0:
            return rand.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0: 
            return rand.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, BigBoy()), 
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)
