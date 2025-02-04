from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, GAP_SIZE, SceneType, TrainingState
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel
from scripts.ui_elements.unit_stats_frame import UnitStatsFrame

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple

    from scripts.core.game import Game

__all__ = ["TrainingUI"]


class TrainingUI(UI):
    """
    Represent the UI of the TrainingScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_unit: Optional[Unit] = None
        self.selected_upgrade: Optional[Dict] = None
        self.stat_frame: Optional[UnitStatsFrame] = None
        self.stat_frame_pos: Tuple[int, int] = (0, 0)

        self.set_instruction_text("Choose an upgrade to buy.")

    def update(self, delta_time: float):
        super().update(delta_time)

        # generic input
        # view troupe
        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

        # panel specific input
        if self.current_panel == self.panels["upgrades"]:
            self.handle_select_upgrade_input()

        elif self.current_panel == self.panels["units"]:
            self.handle_choose_unit_input()

        elif self.current_panel == self.panels["exit"]:
            if self.game.input.states["select"]:
                self.game.input.states["select"] = False

                self.selected_unit = None
                self.selected_upgrade = None

                self.game.change_scene(SceneType.OVERWORLD)

    def render(self, surface: pygame.surface):

        # show core info
        self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        scene = self.game.training
        create_font = self.game.assets.create_font

        start_x = 20
        start_y = 40
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)

        # draw upgrades
        current_x = start_x
        current_y = start_y
        panel_list = []
        for selection_counter, upgrade in enumerate(scene.upgrades_offered):
            # check if available
            if scene.upgrades_available[upgrade["type"]]:
                text = f"{upgrade['stat']} +{upgrade['mod_amount']}"
                font_type = FontType.DEFAULT
                is_selectable = True

                # check can afford
                upgrade_cost = self.game.training.calculate_upgrade_cost(upgrade["tier"])
                can_afford = self.game.memory.gold > upgrade_cost
                if can_afford:
                    gold_font_type = FontType.DEFAULT
                else:
                    gold_font_type = FontType.NEGATIVE

                # draw gold cost
                gold_icon = self.game.assets.get_image("stats", "gold", icon_size)
                frame = Frame(
                    (current_x, current_y),
                    image=gold_icon,
                    font=create_font(gold_font_type, str(upgrade_cost)),
                    is_selectable=False,
                )
                self.elements["cost" + str(selection_counter)] = frame

            else:
                text = f"Sold out"
                font_type = FontType.DISABLED
                is_selectable = False

            # draw upgrade icon and details
            upgrade_x = current_x + 50
            stat_icon = self.game.assets.get_image("stats", upgrade["stat"], icon_size)
            frame = Frame(
                (upgrade_x, current_y), image=stat_icon, font=create_font(font_type, text), is_selectable=is_selectable
            )
            # capture frame
            self.elements[upgrade["type"] + str(selection_counter)] = frame
            panel_list.append(frame)

            # highlight selected upgrade
            if self.selected_upgrade is None:
                self.selected_upgrade = upgrade["type"]
            if upgrade["type"] == self.selected_upgrade:
                frame.is_selected = True

            # increment
            current_y += icon_height + GAP_SIZE

        panel = Panel(panel_list, True)
        self.add_panel(panel, "upgrades")

        # draw list of units
        current_x += 150
        current_y = start_y + 20  # add an offset
        panel_list = []
        for selection_counter, unit in enumerate(self.game.memory.player_troupe.units.values()):
            unit_icon = self.game.assets.unit_animations[unit.type]["icon"][0]
            frame = Frame(
                (current_x, current_y),
                image=unit_icon,
                font=create_font(FontType.DEFAULT, str(unit.type)),
                is_selectable=True,
            )
            frame.add_tier_background(unit.tier)

            # register frame
            self.elements[f"{unit.id}"] = frame
            panel_list.append(frame)

            # highlight selected unit
            if self.selected_unit is None:
                self.selected_unit = unit
            if unit.type == self.selected_unit:
                frame.is_selected = True

            # increment
            current_y += icon_height + GAP_SIZE

        panel = Panel(panel_list, False)
        self.add_panel(panel, "units")

        # draw stat frame
        current_x += 100
        frame = UnitStatsFrame(self.game, (current_x, start_y + 20), self.selected_unit)
        self.elements["stat_frame"] = frame
        frame.is_active = False

        # draw exit button
        self.add_exit_button()

        self.rebuild_resource_elements()

    def refresh_info(self):
        elements = self.elements

        if self.selected_unit is not None:
            elements["stat_frame"].set_unit(self.selected_unit)

    def handle_select_upgrade_input(self):
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            selected_index = self.current_panel.selected_index
            upgrade = self.game.training.upgrades_offered[selected_index]

            # check upgrade is available - this is a defensive check; you shouldnt be able to select a sold upgrade
            if self.game.training.upgrades_available[upgrade["type"]]:

                # select the upgrade
                self.selected_upgrade = upgrade

                # move to next panel
                self.select_panel("units")

                # show unit stat frame
                self.elements["stat_frame"].is_active = True

                # update state
                self.game.training.state = TrainingState.CHOOSE_TARGET_UNIT

                # update info
                self.selected_unit = list(self.game.memory.player_troupe.units.values())[selected_index]
                self.refresh_info()

                # update instruction
                self.set_instruction_text(f"Choose a unit to apply {self.selected_upgrade['type']} to.")

        # go to exit
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            self.select_panel("exit")

        if self.game.input.states["down"]:
            self.game.input.states["down"] = False

            self.current_panel.select_next_element()

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False

            self.current_panel.select_previous_element()

    def handle_choose_unit_input(self):

        # choose a unit
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False
            upgrade = self.selected_upgrade

            # do we have info needed
            if self.selected_unit is not None and upgrade is not None:

                if self.attempt_upgrade_unit():

                    # confirm to user
                    self.set_instruction_text(f"{self.selected_unit.type} upgraded with {upgrade['type']}.", True)

                    # change state
                    self.game.training.state = TrainingState.CHOOSE_UPGRADE

                    # reset values to choose another upgrade
                    self.selected_unit = None
                    self.rebuild_ui()

                    # check if anything left available
                    if True in self.game.training.upgrades_available.values():
                        self.set_instruction_text("Choose an upgrade to buy.")
                    else:
                        self.set_instruction_text("All sold out. Time to move on.")

                        self.select_panel("exit")

                else:
                    upgrade_cost = self.game.training.calculate_upgrade_cost(upgrade["tier"])
                    self.set_instruction_text(
                        f"You can't afford the {upgrade_cost} gold to purchase " f"  {upgrade['type']}.", True
                    )

        # return to upgrade select
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            self.selected_unit = None

            # change panel
            self.select_panel("upgrades")

            # hide stat panel
            self.elements["stat_frame"].is_active = False

            self.refresh_info()

            # change state
            self.game.training.state = TrainingState.CHOOSE_UPGRADE

            self.set_instruction_text("Choose an upgrade to buy.")

        if self.game.input.states["down"]:
            self.game.input.states["down"] = False

            self.current_panel.select_next_element()
            self.selected_unit = list(self.game.memory.player_troupe.units.values())[self.current_panel.selected_index]
            self.refresh_info()  # for stat panel

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False

            self.current_panel.select_previous_element()
            self.selected_unit = list(self.game.memory.player_troupe.units.values())[self.current_panel.selected_index]
            self.refresh_info()  # for stat panel

    def attempt_upgrade_unit(self) -> bool:
        """
        Attempt to upgrade the unit. Returns true is successful.
        """
        # can we afford
        id_ = self.selected_unit.id
        upgrade = self.selected_upgrade
        upgrade_cost = self.game.training.calculate_upgrade_cost(upgrade["tier"])
        if upgrade_cost <= self.game.memory.gold:

            # pay for the upgrade and execute it
            self.game.memory.amend_gold(-upgrade_cost)  # remove gold cost
            self.game.memory.player_troupe.upgrade_unit(id_, upgrade["type"])

            #  update upgrade availability and refresh UI
            self.game.training.upgrades_available[upgrade["type"]] = False

            success = True
        else:
            success = False

        return success
