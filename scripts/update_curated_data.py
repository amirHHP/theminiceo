#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
update_curated_data.py
Generates an expanded, high-depth curated_books_data.py covering 115+ flagship books
with exact slug matches, avoiding collisions, with authentic Persian titles,
verified authors, executive summaries, frameworks, 2026 relevance, and audiences.
"""

import os
import json

CURATED_DATA_PATH = "scripts/curated_books_data.py"

# We will load the original CURATED_BOOKS, fix key matches, and add the new 60+ books.
from scripts.curated_books_data import CURATED_BOOKS as ORIGINAL_CURATED

# Define exact slug mappings for original 58 books to prevent ANY collision
SLUG_MAPPINGS = {
    "continuous_discovery_habits": ["continuous-discovery-habits-discover-products-that-create-customer"],
    "the_mom_test": ["the-mom-test-rob-fitzpatrick"],
    "hooked": ["hooked-how-to-build-habit-forming-products-by-nir-eyal-ryan-hoover"],
    "empowered": ["empowered-ordinary-people-extraordinary-products-by-marty-cagan"],
    "zero_to_one": ["zero-to-one-peter-thiel"],
    "sprint": ["sprint-how-to-solve-big-problem-chayon-shaah-book-series-by-jake"],
    "cracking_the_pm_interview": ["cracking-the-pm-interview-how-to-land-a-product-manager-job-in-technology"],
    "cracking_the_pm_career": ["cracking-the-pm-career-by-jackie-bavaro-careercup-llc"],
    "team_topologies": ["team-topologies-organizing-business-and-technology-teams-for-fast"],
    "atomic_habits": ["atomic-habits-clear-james-2018"],
    "thinking_fast_and_slow": ["thinking-fast-and-slow-daniel-kahneman"],
    "good_strategy_bad_strategy": ["good-strategy-bad-st-by-richard-rumelt", "good-strategy-bad-strategy"],
    "the_crux": ["the-crux-how-leaders-become-strategists"],
    "high_output_management": ["high-output-management-andrew-s-grove"],
    "user_story_mapping": ["user-story-mapping-discover-the-whole-story-build-the-right-product"],
    "shape_up": ["shape-up"],
    "obviously_awesome": ["obviously-awesome-how-to-nail-product-positioning-so-customers-get"],
    "the_cold_start_problem": ["the-cold-start-problem-how-to-start-and-scale-network-effects-by"],
    "the_design_of_everyday_things": ["the-design-of-everyday-things-don-norman"],
    "dont_make_me_think": ["dont-make-me-think-3rd-edition-revisited-pearson-education-20131"],
    "measure_what_matters": ["measure-what-mattersjohn-doerr"],
    "the_hard_thing_about_hard_things": ["the-hard-thing-about-hard-things-ben-horowitz"],
    "nudge": ["nudge-improving-decisions-about-health-wealth-and-happiness"],
    "working_backwards": ["working-backwards-insights-stories-and-secrets-from-inside-amazon"],
    "radical_candor": ["radical-candor"],
    "extreme_ownership": ["extreme-ownership-how-u-s-navy-seals-lead-and-win-jocko-willink"],
    "never_split_the_difference": ["never-split-the-difference-negotiating-as-if-your-life-depended"],
    "the_psychology_of_money": ["the-psychology-of-money-timeless-lessons-on-wealth-greed-and-happiness"],
    "blue_ocean_strategy": ["blue-ocean-strategy-how-to-create-uncontested-market-space-and-make"],
    "essentialism": ["essentialism-the-disciplined-pursuit-of-less-mckeown-greg"],
    "building_a_second_brain": ["building-a-second-brain"],
    "co_intelligence": ["co-intelligence-living-and-working-with-ai-ethan-mollick-2024"],
    "the_coming_wave": ["the-coming-wave-technology-power-and-the-twenty-first-centurys"],
    "getting_things_done": ["getting-things-done-the-art-of-stress-free-productivity-david-allen"],
    "the_pyramid_principle": ["the-pyramid-principle-barbara-minto"],
    "value_proposition_design": ["value-proposition-design-how-to-create-products-and-services-customers"],
    "business_model_generation": ["1-business-model-generation-a-handbook-for-visionaries-game-changers"],
    "running_lean": ["running-lean-iterate-from-plan-a-to-a-plan-that-works-3rd-edition"],
    "the_great_mental_models": ["the-great-mental-models-volume-1-general-thinking-concepts-by-beaubien"],
    "just_enough_research": ["just-enough-research-by-fox-rosehall-erikazeldmaneditor-jeffrey"],
    "laws_of_ux": ["laws-of-ux-design-principles-for-persuasive-and-ethical-products"],
    "the_right_it": ["the-right-it-why-so-many-ideas-fail-and-how-to-make-sure-yours-succeed"],
    "shoe_dog": ["shoe-dog-a-memoir-by-the-creator-of-nike-knight-phil-2016"],
    "no_rules_rules": ["no-rules-rules-by-reed-hastings-erin-meyer-hastings-reed-meyer"],
    "principles": ["principles-ray-dalio-2017"],
    "crossing_the_chasm": ["crossing-the-chasm-3rd-edition-marketing-and-selling-disruptive"],
    "the_innovators_dilemma": ["the-innovators-dilemma-when-new-technologies-cause-great-firms-to"],
    "competing_against_luck": ["competing-against-luck-the-story-of-innovation-and-customer-choice"],
    "the_making_of_a_manager": ["the-making-of-a-manager-julie-zhuo"],
    "actionable_gamification": ["actionable-gamificationyu-kai-chon"],
    "platform_revolution": ["platform-revolution-how-networked-markets-are-transforming-the-economy"],
    "buyology": ["buyology-martin-lindstrom-2008"],
    "so_good_they_cant_ignore_you": ["so-good-they-cant-ignore-you-why-skills-trump-passion-in-the-quest"],
    "solving_product_design_exercises": ["solving-product-design-exercises"],
    "product_direction": ["product-direction-how-to-build-successful-products-at-scale-with"],
    "product_led_growth": ["product-led-growth-how-to-build-a-product-that-sells-itself-by-wes"],
    "googles_agents_companion": ["googles-agents-companion"],
    "the_art_of_prompt_engineering": ["the-art-of-prompt-engineering-for-multimodel-ai-harmonizing-text", "prompt-engineering"]
}

print(f"Loaded {len(SLUG_MAPPINGS)} base mappings.")
