from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, GAP_SIZE, PostCombatState, RewardType, SceneType
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Optional

    from scripts.core.game import Game

__all__ = ["PostCombatUI"]


################ TO DO LIST ##################


class PostCombatUI(UI):
    """
    Represent the UI of the RewardScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_reward: Optional[Unit] = None

        self.stats_max_width = 5

        self.set_instruction_text("Choose your rewards.")

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.game.input.states["right"]:
            if self.selected_ui_row == 0:
                self.selected_ui_col += 1
            self.game.input.states["right"] = False
        if self.game.input.states["left"]:
            if self.selected_ui_row == 0:
                self.selected_ui_col -= 1
            self.game.input.states["left"] = False

        if not self.game.combat.end_data:
            end_data_length = 1
        else:
            end_data_length = len(self.game.combat.end_data)

        self.selected_ui_col = self.selected_ui_col % end_data_length
        if self.selected_ui_col < self.stats_scroll:
            self.stats_scroll = self.selected_ui_col
        if self.selected_ui_col >= self.stats_scroll + self.stats_max_width:
            self.stats_scroll = self.selected_ui_col - self.stats_max_width + 1

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False
            self.selected_ui_row -= 1
        if self.game.input.states["down"]:
            self.game.input.states["down"] = False
            self.selected_ui_row += 1
        self.selected_ui_row = self.selected_ui_row % 2

        if self.game.post_combat.state == PostCombatState.VICTORY:
            self.handle_victory_input()
        elif self.game.post_combat.state == PostCombatState.DEFEAT:
            self.handle_defeat_input()
        elif self.game.post_combat.state == PostCombatState.BOSS_VICTORY:
            self.handle_boss_victory_input()

    def render(self, surface: pygame.surface):
        combat_data = self.game.combat.end_data
        create_font = self.game.assets.create_font

        empty_font = create_font(FontType.DEFAULT, "")

        unit_width = 120
        if combat_data is not None:
            for i, unit in enumerate(combat_data):
                x = unit_width * (i - self.stats_scroll) + unit_width // 2
                if (i < self.stats_scroll) or (i >= self.stats_scroll + self.stats_max_width):
                    continue
                y = self.game.window.base_resolution[1] // 2 + 40
                if self.selected_ui_row == 0:
                    if self.selected_ui_col == i:
                        surface.blit(self.game.assets.ui["select_arrow"], (x - 6, y - 14))
                unit_img = self.game.assets.unit_animations[unit[0]]["icon"][0]
                surface.blit(unit_img, (x - unit_img.get_width() // 2, y))
                y += unit_img.get_height() + 4
                font = create_font(FontType.DEFAULT, unit[0], (x - empty_font.get_text_width(unit[0]) // 2, y))
                font.render(surface)
                y += 13
                for i, v in enumerate([unit[1], unit[2], unit[3], unit[5]]):
                    v = str(v)
                    if i != 3:
                        font = create_font(FontType.DEFAULT, v, (x, y + 4))
                        font.render(surface)
                        img = self.game.assets.images["stats"][("dmg_dealt@16x16", "kills@16x16", "defence@16x16")[i]]
                        surface.blit(img, (x - img.get_width() - 2, y))
                    else:
                        font = create_font(FontType.DEFAULT, v, (x - empty_font.get_text_width(v) // 2, y))
                        font.render(surface)
                    y += 18
                for i in range(unit[4]):
                    x_offset = -unit[4] * 10 + i * 20
                    surface.blit(self.game.assets.images["stats"]["health@16x16"], (x + x_offset, y))

        if self.selected_ui_row == 1:
            surface.blit(
                self.game.assets.ui["select_arrow"],
                (self.game.window.base_resolution[0] - 20, self.game.window.base_resolution[1] - 30),
            )

        if self.game.post_combat.state == PostCombatState.VICTORY:

            reward_type = self.game.post_combat.reward_type
            if reward_type == RewardType.UNIT:
                pass
                # self._render_unit_rewards(surface)

            elif reward_type == RewardType.ACTION:
                pass

            elif reward_type == RewardType.UPGRADE:
                pass

            else:
                # reward_type == RewardType.RESOURCE
                pass

            # show core info
            self.draw_instruction(surface)

        elif self.game.post_combat.state == PostCombatState.DEFEAT:
            self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()
        state = self.game.post_combat.state

        self.selected_ui_row = 0
        self.selected_ui_col = 0
        self.stats_scroll = 0

        if self.game.post_combat.state == PostCombatState.VICTORY:
            self._rebuild_victory_ui()
        elif state == PostCombatState.DEFEAT:
            self._rebuild_defeat_ui()
        elif state == PostCombatState.BOSS_VICTORY:
            self._rebuild_boss_victory_ui()

        self.rebuild_resource_elements()

    def _rebuild_victory_ui(self):
        window_width = self.game.window.width
        window_height = self.game.window.height
        create_font = self.game.assets.create_font

        start_x = 20
        start_y = 40
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)

        # draw header
        text = "Victory"
        font = create_font(FontType.POSITIVE, text)
        current_x = (window_width // 2) - font.width
        current_y = start_y
        frame = Frame((current_x, current_y), font=font, is_selectable=False)
        self.elements["header"] = frame

        # draw gold reward
        current_y += 50
        gold_icon = self.game.assets.get_image("stats", "gold", icon_size)
        gold_reward = str(self.game.post_combat.gold_reward)
        frame = Frame(
            (current_x, current_y),
            image=gold_icon,
            font=create_font(FontType.DEFAULT, gold_reward),
            is_selectable=False,
        )
        self.elements["gold_reward"] = frame

        # draw exit button
        self.add_exit_button()

    def _rebuild_defeat_ui(self):
        create_font = self.game.assets.create_font

        start_x = 20
        start_y = 40
        window_width = self.game.window.width
        window_height = self.game.window.height

        self.set_instruction_text("Return to the main menu")

        # draw header
        text = "Defeat"
        font = create_font(FontType.NEGATIVE, text)
        current_x = (window_width // 2) - font.width
        current_y = start_y
        frame = Frame((current_x, current_y), font=font, is_selectable=False)
        self.elements["header"] = frame

        # draw lost morale
        current_y = window_height // 2
        morale = self.game.memory.morale

        if morale <= 0:
            # game over
            text = "Your forces, like your ambitions, lie in ruin."
            font = create_font(FontType.DISABLED, text)
            current_x = (window_width // 2) - (font.width // 2)
            frame = Frame((current_x, current_y), font=font, is_selectable=False)
            self.elements["morale"] = frame

            # draw exit button
            self.add_exit_button("Abandon hope")
        else:
            # lose morale
            morale_image = self.game.assets.get_image("stats", "morale")
            frame = Frame(
                (current_x, current_y),
                image=morale_image,
                font=create_font(FontType.NEGATIVE, str("-1")),
                is_selectable=False,
            )
            self.elements["morale"] = frame

            # draw exit button
            self.add_exit_button()

    def _render_unit_rewards(self, surface: pygame.surface):
        pass
        # # FIXME - this no longer works
        # reward_units = list(self.game.reward.troupe_rewards.units.values())
        # default_font = self.default_font
        # disabled_font = self.disabled_font
        # warning_font = self.warning_font
        # positive_font = self.positive_font
        # stats = ["type", "health", "defence", "attack", "range", "attack_speed", "move_speed", "ammo", "count"]
        #
        # # positions
        # start_x = 20
        # start_y = 40
        # font_height = 12
        # window_width = self.game.window.width
        # window_height = self.game.window.height
        # col_width = int((window_width - (start_x * 2)) / len(stats))
        #
        # # victory message
        # positive_font.render("Victory!", surface, (start_x, start_y))
        #
        # # gold reward
        # current_y = start_y + (font_height * 2)
        # gold_reward = self.game.reward.gold_reward
        # default_font.render(f"{gold_reward} gold scavenged from the dead.", surface, (start_x, current_y))
        #
        # # instruction
        # current_y = window_height // 2
        # warning_font.render(f"Choose one of the following rewards.", surface, (start_x, current_y))
        #
        # # draw headers
        # current_y = current_y + (font_height * 2)
        # col_count = 0
        # for stat in stats:
        #     col_x = start_x + (col_width * col_count)
        #     default_font.render(stat, surface, (col_x, current_y))
        #
        #     col_count += 1
        #
        # # draw unit info
        # row_count = 0
        # for unit in reward_units:
        #     active_font = default_font
        #
        #     option_y = current_y + ((font_height + GAP_SIZE) * (row_count + 1))  # + 1 due to headers
        #
        #     # draw stats
        #     col_count = 0
        #     for stat in stats:
        #         col_x = start_x + (col_width * col_count)
        #
        #         text = str(getattr(unit, stat))
        #         active_font.render(text, surface, (col_x, option_y))
        #
        #         col_count += 1
        #
        #     # draw selector
        #     if row_count == self.selected_row:
        #         # note the selected unit
        #         self.selected_reward = unit
        #
        #         pygame.draw.line(
        #             surface,
        #             (255, 255, 255),
        #             (start_x, option_y + font_height),
        #             (start_x + active_font.width(unit.type), option_y + font_height),
        #         )
        #
        #     row_count += 1

    def handle_victory_input(self):
        if self.selected_ui_row == 1:
            if self.game.input.states["select"]:
                self.game.input.states["select"] = False

                # there's only 1 thing to select so we know it is the exit button
                self.game.change_scene(SceneType.OVERWORLD)

    def handle_defeat_input(self):
        if self.selected_ui_row == 1:
            if self.game.input.states["select"]:
                self.game.input.states["select"] = False

                # there's only 1 thing to select so we know it is the exit button - but exit to what?
                morale = self.game.memory.morale
                if morale <= 0:
                    # game over
                    self.game.run_setup.reset()
                    self.game.change_scene(SceneType.MAIN_MENU)
                else:
                    # bakc to overworld
                    self.game.change_scene(SceneType.OVERWORLD)

    def handle_boss_victory_input(self):
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # there's only 1 thing to select so we know it is the exit button
            self.game.change_scene(SceneType.MAIN_MENU)

    def _rebuild_boss_victory_ui(self):
        start_y = 40
        window_width = self.game.window.width

        # draw header
        header_text = "Victory"
        header_font = self.game.assets.create_font(FontType.DEFAULT, header_text)
        current_x = (window_width // 2) - header_font.width
        current_y = start_y
        frame = Frame((current_x, current_y), font=header_font, is_selectable=False)
        self.elements["header"] = frame

        # draw victory message
        current_y += 50
        text = "That's all there is. You've beaten the boss, so why not try another commander?"
        victory_font = self.game.assets.create_font(FontType.POSITIVE, text)
        frame = Frame(
            (current_x, current_y),
            font=victory_font,
            is_selectable=False,
        )
        self.elements["info"] = frame

        # draw exit button
        self.add_exit_button()
