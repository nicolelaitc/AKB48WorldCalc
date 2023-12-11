from itertools import combinations
from src.enum_app import *
from flask import flash
from src.helpers import log_app_data
import math


def calculation(cards: list[any], data: dict) -> (list[any], dict, str):
    # add weighting total to all the cards
    weighted_cards = add_weighting(data, cards)

    # Sort the cardbank
    sorted_cards = sorted(weighted_cards, key=lambda card: card["total"], reverse=True)
    log_app_data("sorted_cards", sorted_cards)

    # Filter cards by stage
    qualified_cards, qualified_cards_indice = filter_cards_by_stage(
        sorted_cards, data["stage"]
    )
    log_app_data("qualified_cards", qualified_cards)

    # Verify if there are enough cards
    if len(qualified_cards) < 8:
        return (
            None,
            None,
            "You need to have at least 8 eligible cards to run the simulator!",
        )

    # Generate unique combinations
    deck_in_card_indices = generate_unique_combinations(
        qualified_cards, qualified_cards_indice
    )

    best_cards, best_supports = [], []
    best_stat = empty_stat()
    flash_msg = ""

    for _ in deck_in_card_indices:
        current_cards, current_support = [], []
        for i in range(4):
            card = qualified_cards[i].copy()
            current_cards.append(card)
            card = qualified_cards[i + 4].copy()
            current_support.append(card)

        current_stat = empty_stat()
        log_app_data("current_cards_initialised", current_cards)
        log_app_data("current_support_initialised", current_support)

        current_stat["weighted_total"] = sum(
            [card["weighted_total"] for card in current_cards]
        )
        current_stat["total_min"] = data["production"] + current_stat["weighted_total"]
        current_stat["today_bonus"] = sum(
            [card["today_bonus"] for card in current_cards]
        )
        log_app_data("current_stat after adding total", current_stat)

        # power ranking and same team bonus
        if all(card["team"] == current_cards[0]["team"] for card in current_cards):
            (
                current_stat["team_bonus"],
                current_stat["power_ranking_bonus"],
            ) = calculate_team_bonuses(current_cards, data["opponent"])
            current_stat["total_min"] += (
                current_stat["team_bonus"] + current_stat["power_ranking_bonus"]
            )
        log_app_data("current_stat after team bonus", current_stat)
        log_app_data("current_card after team bonus", current_cards)
        # same theme bonus
        if all(card["theme"] == current_cards[0]["theme"] for card in current_cards):
            current_stat["theme_bonus"] = int(current_stat["total_min"] * 0.05)
            current_stat["total_min"] += current_stat["theme_bonus"]
        log_app_data("current_stat after theme bonus", current_stat)
        log_app_data("current_card after theme bonus", current_cards)

        # check team skill
        for card in current_cards:
            if card["skill_target"] == SkillTargets.Her_Team:
                team = card["team"]
                attribute = card["skill_type"]
                attribute_bonus_rate = card["skill_rate"] / 100
                card["skill_total"] += sum(
                    [
                        c[attribute] * attribute_bonus_rate
                        for c in current_cards
                        # not the same card but the same team
                        if c["member"] != card["member"] and c["team"] == team
                    ]
                )
        log_app_data("current_card after team skill", current_cards)
        # support
        for card in current_support:
            current_stat["support_total"] += card["support_total"]
        for play_card in current_cards:
            for support_card in current_support:
                if support_card["member"] == play_card["member"]:
                    skill = support_card["cheer_skill"]
                    current_stat["support_total"] += int(
                        play_card[skill] * (support_card["cheer_rate"] / 100)
                    )

        current_stat["total_min"] += current_stat["support_total"]

        current_stat["skill_total"] = sum(card["skill_total"] for card in current_cards)
        current_stat["total_max"] = (
            current_stat["total_min"] + current_stat["skill_total"]
        )
        log_app_data("current_stat after support", current_stat)
        log_app_data("current_card after support", current_cards)
        log_app_data("current_support", current_support)
        # check who is the best leader (skill will always be activated)
        leader_skill_total = 0
        current_stat["leader"] = current_cards[0]["member"]
        for card in current_cards:
            if card["skill_total"] > leader_skill_total:
                leader_skill_total = card["skill_total"]
                current_stat["leader"] = card["member"]

        current_stat["total_min"] += leader_skill_total
        log_app_data("current_stat after leader", current_stat)

        # compare with the current best
        if (current_stat["total_max"] > best_stat["total_max"]) and (
            (current_stat["total_min"] > best_stat["total_min"])
            or (current_stat["total_min"] >= data["target"])
        ):
            best_stat.update(current_stat)
            best_cards.clear()
            for card in current_cards:
                d2 = card.copy()
                best_cards.append(d2)
            for card in current_support:
                d2 = card.copy()
                best_supports.append(d2)

    if best_stat["total_max"] < data["target"]:
        flash_msg = "Can't find any winning outcome! Here is the best possible result."
    elif (
        best_stat["total_max"] > data["target"]
        and best_stat["total_min"] < data["target"]
    ):
        flash_msg = "You may pass the level but you will need some luck! Here is the best possible result."
    elif (best_stat["total_min"]) >= data["target"]:
        flash_msg = (
            "You have very high chance to pass the level! Here is the best result."
        )
    else:
        flash_msg = "error"
        print(best_stat, data, best_cards)
        best_cards, best_stat = None, None

    log_app_data("best_stat", best_stat)
    log_app_data("best_cards", best_cards)
    log_app_data("best_supports", best_supports)
    return best_cards, best_stat, best_supports, flash_msg


def add_weighting(data: dict, cardbank: list[any]) -> list[any]:
    for card in cardbank:
        card["support_total"] = 0
        for attribute in data["attributes_weighting"]:
            support_add = math.floor(
                math.floor(card[attribute] * 0.1)
                * (1 + data["attributes_weighting"][attribute])
            )
            card["support_total"] += support_add
            weighting_add = round(
                data["attributes_weighting"][attribute] * card[attribute]
            )
            card[attribute] += weighting_add

        card["weighted_total"] = (
            card["singing"] + card["dancing"] + card["variety"] + card["style"]
        )

        if (
            data["stage"] != "VS"
            and data["stage"] != "SP"
            and (
                card["team"] == data["today_target_team"]
                or data["today_target_team"] == "all"
            )
        ):
            if data["today_skill"] == "all":
                for attribute in data["attributes_weighting"]:
                    v = card[attribute] * (data["today_bonus_rate"])
                    card[attribute] += v
                    card["supprt_total"] += 0.1 * v

            else:
                v = card[data["today_skill"]] * data["today_bonus_rate"]
                card[data["today_skill"]] += v
                card["support_total"] += 0.1 * v

        card["today_bonus"] = (
            card["singing"]
            + card["dancing"]
            + card["variety"]
            + card["style"]
            - card["weighted_total"]
        )
        card["total"] += card["today_bonus"]

        skill_attribute = card["skill_type"]
        skill_bonus_rate = int(card["skill_rate"]) / 100
        skill_bonus_amount = int(card[skill_attribute]) * skill_bonus_rate
        if SkillTargets.from_display_name(card["skill_target"]) == SkillTargets.Herself:
            card[skill_attribute] += skill_bonus_amount
            card["skill_total"] = skill_bonus_amount
        else:
            card["skill_total"] = 0

    return cardbank


def filter_cards_by_stage(sorted_cards, stage):
    """
    Filters cards by the specified stage unless stage is 'Main', 'VS', or 'SP'.
    Now includes all qualified cards without limiting to the top X.

    :param sorted_cards: List of sorted card dictionaries.
    :param stage: The stage to filter by.
    :return: Tuple of filtered card indices and cards.
    """
    filtered_cards = []
    filtered_indices = []
    stage_story_dict = {
        "A": "TeamA Story",
        "K": "TeamK Story",
        "B": "TeamB Story",
        "4": "Team4 Story",
        "8": "Team8 Story",
    }

    if stage not in ["Main Story", "VS", "SP"]:
        for index, card in enumerate(sorted_cards):
            if stage_story_dict[card["team"]] == stage:
                filtered_cards.append(card)
                filtered_indices.append(index)
        return filtered_cards, filtered_indices
    else:
        return sorted_cards, [i for i in range(len(sorted_cards))]


def generate_unique_combinations(filtered_cards, filtered_indices):
    """
    Generates all unique combinations of 8 cards from the filtered list.

    :param filtered_indices: List of indices of filtered cards.
    :param filtered_cards: List of filtered card dictionaries.
    :return: List of valid combinations of card indices.
    """
    all_combinations = list(combinations(filtered_indices, 8))
    valid_combinations = []

    for combo in all_combinations:
        if len(set(combo)) == 8:
            members = [filtered_cards[i]["member"] for i in combo]
            if len(set(members)) == 8:
                valid_combinations.append(combo)

    return valid_combinations


def calculate_team_bonuses(current_cards, opponent):
    """
    Calculates team and power ranking bonuses for the current set of cards.

    :param current_cards: List of card dictionaries.
    :param opponent: The opposing team.
    :param power_ranking: List of teams in order of their power ranking.
    :return: Tuple of team bonus and power ranking bonus.
    """

    power_ranking = ["TeamA", "TeamK", "TeamB", "Team4", "Team8"]

    team_bonus, power_ranking_bonus = 0, 0
    total_stat = sum(card["total"] for card in current_cards)

    # Check if all cards are from the same team

    team_bonus = int(total_stat * 0.05)

    # Calculate power ranking bonus
    if opponent != "No":
        current_team_index = power_ranking.index(current_cards[0]["team"])
        opponent_index = power_ranking.index(opponent)

        # Check for adjacent ranking for bonus or penalty
        if opponent_index == (current_team_index + 1) % len(power_ranking):
            power_ranking_bonus = int(total_stat * 0.2)
        elif opponent_index == (current_team_index - 1) % len(power_ranking):
            power_ranking_bonus = int(total_stat * -0.2)

    return team_bonus, power_ranking_bonus


def empty_stat():
    return {
        "weighted_total": 0,
        "total_max": 0,
        "total_min": 0,
        "team_bonus": 0,
        "power_ranking_bonus": 0,
        "theme_bonus": 0,
        "leader": 0,
        "support_total": 0,
        "skill_total": 0,
        "today_bonus": 0,
    }
