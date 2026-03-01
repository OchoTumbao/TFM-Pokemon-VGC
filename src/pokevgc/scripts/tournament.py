"""
Tournament script for round-robin battles between multiple agents.

Runs battles between all agent pairs and logs results to CSV.
Each agent battles every other agent a configurable number of times.

Outputs:
- Dataset file: Combined state-action pairs from all battles
- Stats file: Tournament results (win/loss records)

Example usage:
    python tournament.py config/tournament_config.yaml
"""

import argparse
import sys
import csv
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple
import yaml
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from vgc2.agent.battle import GreedyBattlePolicy, RandomBattlePolicy, TreeSearchBattlePolicy
from vgc2.battle_engine import BattleEngine, State, StateView, TeamView
from vgc2.battle_engine.game_state import get_battle_teams
from vgc2.competition.match import label_teams
from vgc2.util.generator import gen_team

from battle_logger import run_battle_and_log, BattleLogConfig


AGENT_MAP = {
    "GreedyBattlePolicy": GreedyBattlePolicy,
    "RandomBattlePolicy": RandomBattlePolicy,
    "TreeSearchBattlePolicy": TreeSearchBattlePolicy,
}


@dataclass
class TournamentConfig:
    """Configuration for tournament."""
    agents: List[str]
    battles_per_matchup: int = 1
    n_active: int = 2
    team_size: int = 4
    n_moves: int = 4
    stats_file: str = "tournament_stats.csv"
    dataset_file: str = "tournament_dataset.csv"
    verbose: bool = False
    seed: int = 42  # Fixed seed for reproducibility
    log_actions: bool = False  # Optional: log individual actions


def load_config(config_file: str) -> TournamentConfig:
    """Load configuration from YAML file."""
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    tournament = config_dict.get("tournament", {})
    return TournamentConfig(
        agents=tournament.get("agents", []),
        battles_per_matchup=tournament.get("battles_per_matchup", 1),
        n_active=tournament.get("n_active", 2),
        team_size=tournament.get("team_size", 4),
        n_moves=tournament.get("n_moves", 4),
        stats_file=tournament.get("stats_file", "tournament_stats.csv"),
        dataset_file=tournament.get("dataset_file", "tournament_dataset.csv"),
        verbose=tournament.get("verbose", False),
        seed=tournament.get("seed", 42),
        log_actions=tournament.get("log_actions", False)
    )


def get_agent(agent_name: str):
    """Instantiate an agent from its name."""
    if agent_name not in AGENT_MAP:
        raise ValueError(f"Unknown agent: {agent_name}. Available: {list(AGENT_MAP.keys())}")
    return AGENT_MAP[agent_name]()


def run_battle(agent1, agent2, n_active: int, team_size: int, n_moves: int) -> Tuple[int, int]:
    """
    Run a single battle between two agents.
    
    Returns:
        Tuple of (winner, num_turns)
    """
    team = gen_team(team_size, n_moves), gen_team(team_size, n_moves)
    label_teams(team)
    
    team_view = TeamView(team[0]), TeamView(team[1])
    state = State(get_battle_teams(team, n_active))
    state_view = StateView(state, 0, team_view), StateView(state, 1, team_view)
    
    engine = BattleEngine(state, debug=False)
    
    while not engine.finished():
        decision_p0 = agent1.decision(state_view[0], team_view[1])
        decision_p1 = agent2.decision(state_view[1], team_view[0])
        engine.run_turn((decision_p0, decision_p1))
    
    return engine.winning_side, engine.state.turn


def run_tournament(config: TournamentConfig) -> Dict:
    """
    Run a round-robin tournament with battle logging.
    
    Returns:
        Dictionary with tournament statistics
    """
    if not config.agents:
        raise ValueError("No agents configured")
    
    # Set seed for reproducibility
    np.random.seed(config.seed)
    
    print(f"=== Pokemon VGC Tournament ===")
    print(f"Agents: {', '.join(config.agents)}")
    print(f"Battles per matchup: {config.battles_per_matchup}")
    print(f"Total matchups: {len(config.agents) * (len(config.agents) - 1) // 2}")
    print(f"Seed: {config.seed}")
    print(f"Action logging: {'enabled' if config.log_actions else 'disabled'}")
    print()
    
    # Initialize win tracking
    win_counts = {agent: 0 for agent in config.agents}
    battle_count = 0
    turn_counts = []
    all_logged_data = []
    
    # CSV rows for stats
    stats_rows = []
    
    # Round-robin tournament
    total_matchups = 0
    for i, agent1_name in enumerate(config.agents):
        for agent2_name in config.agents[i+1:]:
            total_matchups += 1
            agent1 = get_agent(agent1_name)
            agent2 = get_agent(agent2_name)
            
            matchup_wins = {agent1_name: 0, agent2_name: 0}
            matchup_turns = []
            
            print(f"Match {total_matchups}: {agent1_name} vs {agent2_name}")
            
            for battle_num in range(config.battles_per_matchup):
                # Setup battle
                team = gen_team(config.team_size, config.n_moves), gen_team(config.team_size, config.n_moves)
                label_teams(team)
                
                team_view = TeamView(team[0]), TeamView(team[1])
                state = State(get_battle_teams(team, config.n_active))
                state_view = StateView(state, 0, team_view), StateView(state, 1, team_view)
                
                engine = BattleEngine(state, debug=False)
                
                # Run battle with logging
                log_config = BattleLogConfig(
                    log_file="temp_battle.csv",
                    include_winner_label=True,
                    include_debug=False,
                    verbose_decisions=False,
                    client=None
                )
                
                winner_idx, logged_data = run_battle_and_log(engine, (agent1, agent2), 
                                                             team_view, state_view, log_config)
                
                battle_count += 1
                
                # Track turns - count the number of turns based on logged data
                # Each turn has 2 entries (one per player), so divide by 2
                num_turns = len(logged_data) // 2 if logged_data else 0
                
                # Only aggregate action logs if configured
                if config.log_actions:
                    all_logged_data.extend(logged_data)
                
                turn_counts.append(num_turns)
                
                # Determine winner name
                if winner_idx == 0:
                    winner_name = agent1_name
                else:
                    winner_name = agent2_name
                
                matchup_wins[winner_name] += 1
                win_counts[winner_name] += 1
                
                # Log stats row
                stats_rows.append({
                    'agent1': agent1_name,
                    'agent2': agent2_name,
                    'winner': winner_name,
                    'turns': num_turns
                })
                
                if config.verbose:
                    print(f"  Battle {battle_num + 1}/{config.battles_per_matchup}: "
                          f"{winner_name} wins in {num_turns} turns")
            
            print(f"  Result: {agent1_name} {matchup_wins[agent1_name]}-"
                  f"{matchup_wins[agent2_name]} {agent2_name}\n")
    
    # Save stats to CSV
    save_stats(stats_rows, config.stats_file)
    
    # Save dataset to CSV only if action logging is enabled
    if config.log_actions:
        save_dataset(all_logged_data, config.dataset_file)
    
    # Print summary
    print("\n=== Tournament Summary ===")
    print(f"Total battles: {battle_count}")
    print(f"Average turns per battle: {sum(turn_counts) / len(turn_counts):.1f}")
    if config.log_actions:
        print(f"Total dataset entries: {len(all_logged_data)}")
    print(f"\nAgent Rankings:")
    
    sorted_agents = sorted(win_counts.items(), key=lambda x: x[1], reverse=True)
    for rank, (agent_name, wins) in enumerate(sorted_agents, 1):
        print(f"  {rank}. {agent_name}: {wins} wins")
    
    print(f"\nStats saved to: {config.stats_file}")
    if config.log_actions:
        print(f"Dataset saved to: {config.dataset_file}")
    
    return {
        'total_battles': battle_count,
        'win_counts': win_counts,
        'average_turns': sum(turn_counts) / len(turn_counts) if turn_counts else 0,
        'total_entries': len(all_logged_data)
    }


def save_stats(stats_rows: List[Dict], output_file: str) -> None:
    """Save tournament stats to CSV file."""
    if not stats_rows:
        print("No stats to save")
        return
    
    fieldnames = ['agent1', 'agent2', 'winner', 'turns']
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stats_rows)


def save_dataset(logged_data: List[np.ndarray], output_file: str) -> None:
    """Save all battle logs to dataset CSV file."""
    if not logged_data:
        print("No dataset to save")
        return
    
    logged_array = np.array(logged_data, dtype=np.float32)
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in logged_array:
            writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run a round-robin tournament between VGC agents"
    )
    parser.add_argument(
        "config_file",
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "-s", "--stats",
        help="Stats output file path (overrides config)",
        default=None
    )
    parser.add_argument(
        "-d", "--dataset",
        help="Dataset output file path (overrides config)",
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config_file)
        if args.stats:
            config.stats_file = args.stats
        if args.dataset:
            config.dataset_file = args.dataset
        
        run_tournament(config)
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
