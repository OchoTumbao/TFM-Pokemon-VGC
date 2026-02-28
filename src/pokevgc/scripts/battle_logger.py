"""
Configurable battle logger for generating training datasets.

This module provides utilities to run battles and log state-action pairs
with outcome labels for supervised learning.

Usage:
    from battle_logger import run_battle_and_log, save_battle_log, BattleLogConfig
    
    config = BattleLogConfig(log_file="my_battle.csv", include_winner_label=True)
    winner, logged_data = run_battle_and_log(engine, agent, team_view, state_view, config)
    save_battle_log(logged_data, config.log_file)
"""

import numpy as np
import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from vgc2.battle_engine import BattleEngine, StateView, TeamView
from vgc2.battle_engine.game_state import State
from utils.state_vectorizer import vectorize_state
from utils.action_vectorizer import ActionVectorizer


@dataclass
class BattleLogConfig:
    """Configuration for battle logging."""
    log_file: str = "battle_log.csv"
    include_winner_label: bool = True
    include_debug: bool = False
    verbose_decisions: bool = False
    client: Optional[object] = None  # GodotClient or None


def run_battle_and_log(engine: BattleEngine, 
                       agent: Tuple,
                       team_view: Tuple[TeamView, TeamView],
                       state_view: Tuple[StateView, StateView],
                       config: BattleLogConfig) -> Tuple[int, List[np.ndarray]]:
    """
    Run a battle and log state-action pairs.
    
    Args:
        engine: BattleEngine instance with initialized state
        agent: Tuple of (agent0, agent1) - agents that make decisions
        team_view: Tuple of (TeamView0, TeamView1)
        state_view: Tuple of (StateView0, StateView1)
        config: BattleLogConfig with logging configuration
    
    Returns:
        Tuple of (winner_side, logged_data)
        - winner_side: 0 or 1 indicating the winner
        - logged_data: List of numpy arrays, each containing [state_vector | action_vector | label]
    """
    action_vectorizer = ActionVectorizer()
    logged_data = []
    turn_count = 0
    
    while not engine.finished():
        turn_count += 1
        
        # Get the state vectors before actions are taken
        state_vec_p0 = vectorize_state(engine.state, 0)
        state_vec_p1 = vectorize_state(engine.state, 1)
        
        # Get decisions from agents
        decision_p0 = agent[0].decision(state_view[0], team_view[1])
        decision_p1 = agent[1].decision(state_view[1], team_view[0])
        
        # Convert decisions to action vectors and log
        for idx, choice in enumerate(decision_p0):
            action_vec_p0 = _decision_to_action_vector(engine.state, choice, 0, action_vectorizer)
            # Add agent index (0.0 for player 0) as placeholder for winner label
            entry = np.concatenate([state_vec_p0, action_vec_p0, [0.0]])
            logged_data.append(entry)
            
            if config.verbose_decisions:
                move_idx, target_idx = choice
                print(f"Turn {turn_count}, Player 0, Active {idx}: move_idx={move_idx}, target={target_idx}")
        
        for idx, choice in enumerate(decision_p1):
            action_vec_p1 = _decision_to_action_vector(engine.state, choice, 1, action_vectorizer)
            # Add agent index (1.0 for player 1) as placeholder for winner label
            entry = np.concatenate([state_vec_p1, action_vec_p1, [1.0]])
            logged_data.append(entry)
            
            if config.verbose_decisions:
                move_idx, target_idx = choice
                print(f"Turn {turn_count}, Player 1, Active {idx}: move_idx={move_idx}, target={target_idx}")
        
        # Execute the turn
        engine.run_turn((decision_p0, decision_p1))
        if config.client:
            engine.render(config.client)
    
    winner = engine.winning_side
    
    # Replace agent index with winner label (1 if agent won, 0 if lost)
    if config.include_winner_label:
        for i in range(len(logged_data)):
            agent_idx = int(logged_data[i][-1])  # Get the agent index we stored
            label = 1.0 if agent_idx == winner else 0.0
            logged_data[i][-1] = label
    
    if config.include_debug:
        print(f"\n=== Battle Summary ===")
        print(f"Battle finished. Total turns: {turn_count}")
        print(f"Total logged entries: {len(logged_data)}")
        print(f"Winner: Player {winner}")
        if logged_data:
            lengths = [len(entry) for entry in logged_data]
            print(f"Entry shape: {len(logged_data[0])} features")
            print(f"Entry lengths - min: {min(lengths)}, max: {max(lengths)}, unique: {set(lengths)}")
    
    return winner, logged_data


def save_battle_log(logged_data: List[np.ndarray], log_file: str, append: bool = False) -> None:
    """
    Save logged battle data to CSV file.
    
    Args:
        logged_data: List of numpy arrays to save
        log_file: Output CSV file path
        append: If True, append to existing file; if False, overwrite
    """
    logged_array = np.array(logged_data, dtype=np.float32)
    
    mode = 'a' if append else 'w'
    with open(log_file, mode, newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in logged_array:
            writer.writerow(row)
    
    print(f"Battle log {'appended to' if append else 'saved to'} {log_file} with shape {logged_array.shape}")


def append_battle_logs(log_files: List[str], output_file: str) -> None:
    """
    Combine multiple battle log files into a single file.
    
    Args:
        log_files: List of CSV file paths to combine
        output_file: Output combined CSV file path
    """
    combined_data = []
    
    for log_file in log_files:
        data = np.loadtxt(log_file, delimiter=',', dtype=np.float32)
        combined_data.append(data)
    
    combined_array = np.vstack(combined_data)
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in combined_array:
            writer.writerow(row)
    
    print(f"Combined {len(log_files)} log files into {output_file} with shape {combined_array.shape}")


def _decision_to_action_vector(state: State, decision, player_side: int, 
                               vectorizer: ActionVectorizer) -> np.ndarray:
    """
    Convert a decision tuple to an action vector.
    
    Decision format: (move_idx, target_idx) for move actions or (-1, pokemon_idx) for switches
    
    Args:
        state: Current game state
        decision: Tuple of (move_idx, target_pokemon_idx)
        player_side: Which player (0 or 1)
        vectorizer: ActionVectorizer instance
    
    Returns:
        Numpy array representing the action vector
    """
    move_idx, target_pokemon_idx = decision
    
    if move_idx == -1:
        # Switch action
        side = state.sides[player_side]
        incoming_pokemon = side.team.reserve[target_pokemon_idx]
        return vectorizer.vectorize_switch_action(incoming_pokemon, target_pokemon_idx)
    else:
        # Move action
        side = state.sides[player_side]
        active_pokemon = side.team.active[0]  # First active pokemon
        move = active_pokemon.battling_moves[move_idx]
        
        # Get target Pokemon
        opponent_side = state.sides[1 - player_side]
        target_pokemon = opponent_side.team.active[target_pokemon_idx]
        
        return vectorizer.vectorize_move_action(move, target_pokemon, target_pokemon_idx)
