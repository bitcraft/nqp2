from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import CombatState, SceneType
from scripts.core.utility import offset

if TYPE_CHECKING:
    pass

__all__ = ["CombatUI"]


class CombatUI(UI):
    def __init__(self, game):
        super().__init__(game)

        # position relative to terrain
        self.place_target = [0, 0]
        self.selected_col = 0

    def update(self, delta_time: float):
        super().update(delta_time)

        target_pos = self.game.combat.get_team_center("player")
        if not target_pos:
            target_pos = [0, 0]
        else:
            target_pos[0] -= self.game.window.base_resolution[0] // 2
            target_pos[1] -= self.game.window.base_resolution[1] // 2

        self.game.combat.camera.pos[0] += (
            (target_pos[0] - self.game.combat.camera.pos[0]) / 10 * (self.game.window.dt * 60)
        )
        self.game.combat.camera.pos[1] += (
            (target_pos[1] - self.game.combat.camera.pos[1]) / 10 * (self.game.window.dt * 60)
        )

        cards = self.game.combat.hand.cards

        if self.game.combat.state in [CombatState.UNIT_CHOOSE_CARD, CombatState.ACTION_CHOOSE_CARD]:

            if self.game.input.states["left"]:
                self.game.input.states["left"] = False

                self.selected_col -= 1
                if self.selected_col < 0:
                    self.selected_col = len(cards) - 1

            if self.game.input.states["right"]:
                self.game.input.states["right"] = False

                self.selected_col += 1
                if self.selected_col > len(cards) - 1:
                    self.selected_col = 0

            if self.game.input.states["select"]:

                # transition to appropriate mode
                if self.game.combat.state == CombatState.UNIT_CHOOSE_CARD:
                    # can only use a card if there are cards in your hand and point limit not hit
                    unit = cards[self.selected_col].unit
                    leadership = self.game.memory.leadership
                    leadership_remaining = leadership - self.game.combat.leadership_points_spent
                    if len(cards) and leadership_remaining >= unit.tier:
                        self.game.combat.state = CombatState.UNIT_SELECT_TARGET
                else:
                    # determine action target mode
                    target_type = self.game.combat.actions[cards[self.selected_col].type](self.game).target_type
                    if target_type == "free":
                        self.game.combat.state = CombatState.ACTION_SELECT_TARGET_FREE

                self.place_target = [
                    self.game.combat.terrain.pixel_size[0] // 2,
                    self.game.combat.terrain.pixel_size[1] // 2,
                ]

            if self.game.input.states["cancel"]:
                if self.game.combat.state == CombatState.UNIT_CHOOSE_CARD:
                    pass

                self.game.combat.state = CombatState.WATCH

        elif self.game.combat.state in [CombatState.UNIT_SELECT_TARGET, CombatState.ACTION_SELECT_TARGET_FREE]:
            directions = {
                "right": (1, 0),
                "left": (-1, 0),
                "up": (0, -1),
                "down": (0, 1),
            }

            move_amount = [0, 0]

            # add up direction movement
            for direction in directions:
                if self.game.input.states["hold_" + direction]:
                    offset(move_amount, directions[direction], self.game.window.dt * 75)

            self.place_target = offset(self.place_target, move_amount)

            if self.game.input.states["select"]:
                # hand will contain the hand for whichever deck is in use
                if self.game.combat.state == CombatState.UNIT_SELECT_TARGET:
                    unit = cards[self.selected_col].unit
                    unit.pos = self.place_target.copy()
                    self.game.combat.leadership_points_spent += unit.tier
                    self.game.combat.units.add_unit_to_combat(unit)

                    logging.info(f"Placed {unit.type}({unit.id}) at {unit.pos}.")
                else:
                    action = self.game.combat.actions[cards[self.selected_col].type](self.game)
                    action.use(self.place_target.copy())

                cards.pop(self.selected_col)

            if self.game.input.states["cancel"] or self.game.input.states["select"]:
                # transition to appropriate state
                if self.game.combat.state == CombatState.UNIT_SELECT_TARGET:
                    self.game.combat.state = CombatState.UNIT_CHOOSE_CARD
                else:
                    self.game.combat.state = CombatState.ACTION_CHOOSE_CARD

        elif self.game.combat.state == CombatState.WATCH:
            if self.game.input.states["cancel"]:
                self.game.combat.state = CombatState.ACTION_CHOOSE_CARD
                self.game.combat.start_action_phase()

        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

    def render(self, surface: pygame.Surface):

        self.draw_instruction(surface)
        self.draw_elements(surface)

        # draw selector
        if self.game.combat.state in [CombatState.UNIT_SELECT_TARGET, CombatState.ACTION_SELECT_TARGET_FREE]:
            pygame.draw.circle(surface, (255, 255, 255), self.game.combat.camera.render_offset(self.place_target), 8, 1)

        cards = self.game.combat.hand.cards

        if self.game.combat.state != CombatState.WATCH:
            start_pos = self.game.window.display.get_width() // 2 - (len(cards) - 1) * 30

            for i, card in enumerate(cards):
                height_offset = 0
                if self.selected_col == i:
                    height_offset = -12

                elif self.game.combat.state in [CombatState.UNIT_SELECT_TARGET, CombatState.ACTION_SELECT_TARGET_FREE]:
                    height_offset += 12

                card.render(surface, (start_pos + i * 60 - 25, 300 + height_offset))

    def rebuild_ui(self):
        super().rebuild_ui()

        warning_font = self.warning_font

        # render status text
        status = "None"
        if self.game.combat.state in [CombatState.UNIT_SELECT_TARGET, CombatState.ACTION_SELECT_TARGET_FREE]:
            status = "select a target location"
        elif self.game.combat.state == CombatState.UNIT_CHOOSE_CARD:
            status = "select a unit or press X to end unit placement"
        elif self.game.combat.state == CombatState.ACTION_CHOOSE_CARD:
            status = "select an action or press X to watch"
        elif self.game.combat.state == CombatState.WATCH:
            status = "press X to use an action"
        self.set_instruction_text(status)
