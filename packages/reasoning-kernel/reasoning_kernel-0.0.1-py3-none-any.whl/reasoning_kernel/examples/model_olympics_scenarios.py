"""
Model Olympics Scenarios - Sports vignettes for testing MSA reasoning
Based on the evaluation dataset from research paper 2507.12547
"""

from typing import Any, Dict, List


# Sports scenarios that test novel causal reasoning with arbitrary variables
MODEL_OLYMPICS_SCENARIOS = [
    {
        "id": "basketball_shooting",
        "title": "Basketball Shooting Performance",
        "scenario": """
        In a basketball game, player Sarah has been practicing a new shooting technique. 
        In the first quarter, she made 3 out of 5 shots from the three-point line. 
        The crowd noise level was moderate (6/10), and the lighting was slightly dim due to a malfunctioning bulb.
        Her usual shooting percentage from three-point range is 40%.
        
        In the second quarter, the lighting was fixed and the crowd became much louder (8/10) due to an exciting play.
        How likely is Sarah to make her next three-point shot in the second quarter?
        """,
        "novel_variables": ["crowd_noise", "lighting_quality", "shooting_technique_adaptation"],
        "causal_structure": "crowd_noise -> concentration -> shooting_accuracy, lighting -> visual_clarity -> shooting_accuracy",
        "expected_reasoning": "Must consider how environmental factors affect shooting performance through psychological and physical mechanisms"
    },
    
    {
        "id": "soccer_penalty_pressure", 
        "title": "Soccer Penalty Under Pressure",
        "scenario": """
        In a crucial soccer match, goalkeeper Maria has saved 2 out of the last 6 penalty kicks she faced.
        The upcoming penalty kick is in the 89th minute with the score tied 1-1.
        The penalty taker, Alex, usually scores 75% of penalty kicks but has never faced Maria before.
        The home crowd is extremely loud and hostile toward Alex.
        Maria has been jumping early on penalties (a risky strategy) in the last 3 attempts.
        
        What is the probability that Alex will score this penalty kick?
        """,
        "novel_variables": ["game_pressure", "crowd_hostility", "goalkeeper_strategy_adaptation", "mutual_unfamiliarity"],
        "causal_structure": "pressure -> anxiety -> performance, crowd -> distraction -> accuracy, strategy -> predictability -> save_probability",
        "expected_reasoning": "Must balance historical performance with situational factors and psychological pressure"
    },
    
    {
        "id": "tennis_surface_adaptation",
        "title": "Tennis Surface Adaptation",
        "scenario": """
        Tennis player Kim has been training on hard courts for the past 6 months and has won 12 out of 15 matches.
        Now she's playing her first clay court tournament. In her opening match, she won the first set 6-4 
        but lost the second set 3-6. Her movement seemed awkward and she made several sliding errors.
        Clay courts typically slow down the ball by 15% compared to hard courts, and Kim's aggressive playing style
        usually relies on quick, powerful shots.
        
        In the deciding third set, how likely is Kim to win if she adapts her strategy?
        """,
        "novel_variables": ["surface_adaptation_rate", "strategy_flexibility", "movement_adjustment", "ball_speed_change"],
        "causal_structure": "surface_change -> movement_difficulty -> error_rate, strategy_adaptation -> shot_selection -> point_win_probability",
        "expected_reasoning": "Must model learning/adaptation over time and strategic adjustments to new conditions"
    },
    
    {
        "id": "swimming_lane_assignment", 
        "title": "Swimming Lane Assignment Effect",
        "scenario": """
        In a 100m freestyle race, swimmer David has posted a personal best time this season of 48.2 seconds.
        He has been assigned to lane 2 (traditionally a less favorable lane) while his main rival Emma is in lane 4 (center lane).
        David tends to perform better when he can see other swimmers (he's a reactive swimmer), but lane 2 limits his peripheral vision.
        The pool has been recently renovated with new lane ropes that create less turbulence.
        In his last 3 races from outer lanes, David's times were 0.3 seconds slower than his season average.
        
        What time is David likely to swim in this race?
        """,
        "novel_variables": ["lane_position_effect", "swimmer_visual_strategy", "pool_turbulence", "competitive_psychology"],
        "causal_structure": "lane_position -> visibility -> pacing_strategy -> performance, turbulence -> swimming_efficiency -> time",
        "expected_reasoning": "Must consider both physical (turbulence) and psychological (visibility, competition) factors on performance"
    },
    
    {
        "id": "volleyball_rotation_disruption",
        "title": "Volleyball Rotation Disruption", 
        "scenario": """
        In volleyball, Team Alpha has been running their standard 6-2 rotation and has won 8 out of 12 sets today.
        Their star setter, Jordan, just injured their ankle and must be substituted.
        The backup setter, Riley, has only played 20% of the season and uses a different setting style (faster tempo).
        The team's outside hitter, Sam, has practiced with Riley but their timing is still developing.
        Team Alpha is currently ahead 2-1 in sets, and this is the deciding set tied at 15-15.
        
        How likely is Team Alpha to win the set with the substitution?
        """,
        "novel_variables": ["player_substitution_disruption", "timing_adjustment", "team_chemistry", "pressure_situation"],
        "causal_structure": "substitution -> team_chemistry_disruption -> performance, timing_mismatch -> error_rate -> point_loss",
        "expected_reasoning": "Must model team dynamics, adaptation time, and how disruption affects performance under pressure"
    }
]

def get_scenario_by_id(scenario_id: str) -> Dict[str, Any]:
    """Get a specific Model Olympics scenario by ID"""
    for scenario in MODEL_OLYMPICS_SCENARIOS:
        if scenario["id"] == scenario_id:
            return scenario
    return {}

def get_all_scenarios() -> List[Dict[str, Any]]:
    """Get all Model Olympics scenarios"""
    return MODEL_OLYMPICS_SCENARIOS

def get_scenarios_by_sport(sport: str) -> List[Dict[str, Any]]:
    """Get scenarios for a specific sport"""
    sport_keywords = {
        "basketball": ["basketball"],
        "soccer": ["soccer", "football"],
        "tennis": ["tennis"],
        "swimming": ["swimming"],
        "volleyball": ["volleyball"]
    }
    
    keywords = sport_keywords.get(sport.lower(), [sport.lower()])
    matching_scenarios = []
    
    for scenario in MODEL_OLYMPICS_SCENARIOS:
        scenario_text = (scenario["title"] + " " + scenario["scenario"]).lower()
        if any(keyword in scenario_text for keyword in keywords):
            matching_scenarios.append(scenario)
    
    return matching_scenarios

def create_custom_scenario(title: str, scenario_text: str, novel_variables: List[str], 
                         causal_structure: str, expected_reasoning: str) -> Dict[str, Any]:
    """Create a custom Model Olympics-style scenario"""
    return {
        "id": f"custom_{title.lower().replace(' ', '_')}",
        "title": title,
        "scenario": scenario_text,
        "novel_variables": novel_variables,
        "causal_structure": causal_structure,
        "expected_reasoning": expected_reasoning
    }