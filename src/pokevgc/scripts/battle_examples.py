"""
Example script showing how to use the configurable battle logger.

This script demonstrates how to:
1. Configure battle logging
2. Run multiple battles
3. Collect and save logs
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from vgc2.agent.battle import GreedyBattlePolicy, RandomBattlePolicy
from vgc2.battle_engine import BattleEngine, State, StateView, TeamView
from vgc2.battle_engine.game_state import get_battle_teams
from vgc2.competition.match import label_teams
from vgc2.net.stream import GodotClient
from vgc2.util.generator import gen_team

from battle_logger import run_battle_and_log, save_battle_log, BattleLogConfig


def run_single_battle_example():
    """Run a single battle with logging."""
    print("=== Single Battle Example ===\n")
    
    # Setup
    n_active = 2
    team_size = 4
    n_moves = 4
    
    team = gen_team(team_size, n_moves), gen_team(team_size, n_moves)
    label_teams(team)
    
    team_view = TeamView(team[0]), TeamView(team[1])
    state = State(get_battle_teams(team, n_active))
    state_view = StateView(state, 0, team_view), StateView(state, 1, team_view)
    
    engine = BattleEngine(state, debug=False)
    agent = GreedyBattlePolicy(), RandomBattlePolicy()
    
    # Configure logging
    config = BattleLogConfig(
        log_file="single_battle.csv",
        include_winner_label=True,
        include_debug=True,
        verbose_decisions=True
    )
    
    # Run battle and log
    winner, logged_data = run_battle_and_log(engine, agent, team_view, state_view, config)
    
    # Save logs
    save_battle_log(logged_data, config.log_file)
    
    print(f"Side {winner} wins!\n")
    return logged_data


def run_multiple_battles_example(num_battles: int = 3):
    """Run multiple battles and collect logs."""
    print(f"=== Multiple Battles Example ({num_battles} battles) ===\n")
    
    all_logged_data = []
    wins = [0, 0]
    
    for battle_num in range(1, num_battles + 1):
        print(f"\n--- Battle {battle_num}/{num_battles} ---")
        
        # Setup
        n_active = 2
        team_size = 4
        n_moves = 4
        
        team = gen_team(team_size, n_moves), gen_team(team_size, n_moves)
        label_teams(team)
        
        team_view = TeamView(team[0]), TeamView(team[1])
        state = State(get_battle_teams(team, n_active))
        state_view = StateView(state, 0, team_view), StateView(state, 1, team_view)
        
        engine = BattleEngine(state, debug=False)
        agent = GreedyBattlePolicy(), RandomBattlePolicy()
        
        # Configure logging
        config = BattleLogConfig(
            log_file=f"battle_{battle_num}.csv",
            include_winner_label=True,
            include_debug=True,
            verbose_decisions=False
        )
        
        # Run battle
        winner, logged_data = run_battle_and_log(engine, agent, team_view, state_view, config)
        all_logged_data.extend(logged_data)
        wins[winner] += 1
        
        print(f"Side {winner} wins!")
    
    # Combine all logs into single file
    import numpy as np
    import csv
    
    combined_array = np.array(all_logged_data, dtype=np.float32)
    with open("all_battles_combined.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in combined_array:
            writer.writerow(row)
    
    print(f"\n=== Summary ===")
    print(f"Total battles: {num_battles}")
    print(f"Player 0 wins: {wins[0]}")
    print(f"Player 1 wins: {wins[1]}")
    print(f"Combined log saved to all_battles_combined.csv with shape {combined_array.shape}")


def run_custom_agents_example():
    """Example with custom agent configuration."""
    print("=== Custom Agents Example ===\n")
    
    # You can swap agents here
    agent_configs = [
        ("GreedyBattlePolicy vs RandomBattlePolicy", GreedyBattlePolicy(), RandomBattlePolicy()),
        ("RandomBattlePolicy vs GreedyBattlePolicy", RandomBattlePolicy(), GreedyBattlePolicy()),
    ]
    
    for agent_name, agent0, agent1 in agent_configs:
        print(f"\n--- {agent_name} ---")
        
        # Setup
        n_active = 2
        team_size = 4
        n_moves = 4
        
        team = gen_team(team_size, n_moves), gen_team(team_size, n_moves)
        label_teams(team)
        
        team_view = TeamView(team[0]), TeamView(team[1])
        state = State(get_battle_teams(team, n_active))
        state_view = StateView(state, 0, team_view), StateView(state, 1, team_view)
        
        engine = BattleEngine(state, debug=False)
        agent = agent0, agent1
        
        config = BattleLogConfig(
            log_file=f"battle_{agent_name.replace(' ', '_')}.csv",
            include_winner_label=True,
            include_debug=True
        )
        
        winner, logged_data = run_battle_and_log(engine, agent, team_view, state_view, config)
        save_battle_log(logged_data, config.log_file)
        print(f"Side {winner} wins!")


if __name__ == '__main__':
    # Run examples
    run_single_battle_example()
    print("\n" + "="*50 + "\n")
    
    #run_multiple_battles_example(num_battles=3)
    #print("\n" + "="*50 + "\n")
    
    # Uncomment to test custom agents
    # run_custom_agents_example()
