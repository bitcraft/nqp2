from scripts.scenes.combat.elements.troupe import Troupe


class EnemyCombatantsGenerator:
    def __init__(self, game):
        self.game = game
        self.enemy_troupe: Troupe = Troupe(game, "enemy")

    def generate(self):
        # lots of temp stuff here for now
        map_size = self.game.combat.terrain.pixel_size
        rng = self.game.rng

        enemy_count = 2

        # generate positions
        positions = []
        for i in range(enemy_count):
            # choose a random spot on the right side of the map
            pos = [rng.random() * map_size[0] // 2 + map_size[0] // 2, rng.random() * map_size[1]]
            positions.append(pos)

        # generate units
        ids = self.enemy_troupe.generate_units(enemy_count)

        # assign positions and add to combat
        for id_ in ids:
            unit = self.enemy_troupe.units[id_]

            unit.pos = positions.pop(0)
            self.game.combat.units.add_unit_to_combat(unit)
