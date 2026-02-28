from vgc2.agent.battle import GreedyBattlePolicy, RandomBattlePolicy
from vgc2.battle_engine import BattleEngine, State, StateView, TeamView
from vgc2.battle_engine.game_state import get_battle_teams
from vgc2.competition.match import run_battle, label_teams
from vgc2.net.stream import GodotClient
from vgc2.util.generator import gen_team
import numpy as np
from pathlib import Path
import sys
import csv
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.state_vectorizer import vectorize_state
from utils.action_vectorizer import ActionVectorizer


def run_battle_with_logging(engine: BattleEngine, agent, team_view, state_view, 
                            client=None, log_file="battle_log.csv"):
    """
    Run a battle and log state-action pairs to a CSV file.
    
    Each row in the log contains: [state_vector | action_vector]
    """
    action_vectorizer = ActionVectorizer()
    logged_data = []
    
    while not engine.finished():
        # Get the state vectors before actions are taken
        state_vec_p0 = vectorize_state(engine.state, 0)
        state_vec_p1 = vectorize_state(engine.state, 1)
        
        # Get decisions from agents (these are the actions)
        decision_p0 = agent[0].decision(state_view[0], team_view[1])
        decision_p1 = agent[1].decision(state_view[1], team_view[0])
        
        # Convert decisions to action vectors
        # Each decision is a list of tuples (one per active Pokemon)
        for choice in decision_p0:
            action_vec_p0 = _decision_to_action_vector(engine.state, choice, 0, action_vectorizer)
            logged_data.append(np.concatenate([state_vec_p0, action_vec_p0]))
        
        for choice in decision_p1:
            action_vec_p1 = _decision_to_action_vector(engine.state, choice, 1, action_vectorizer)
            logged_data.append(np.concatenate([state_vec_p1, action_vec_p1]))
        
        # Execute the turn
        engine.run_turn((decision_p0, decision_p1))
        engine.render(client)
    
    print(f"Battle finished. Total logged entries: {len(logged_data)}")
    
    # Debug: Check if all logged entries have the same length
    if logged_data:
        lengths = [len(entry) for entry in logged_data]
        print(f"Entry lengths - min: {min(lengths)}, max: {max(lengths)}, unique: {set(lengths)}")
        
        # Print first few entries
        for i, length in enumerate(lengths[:5]):
            print(f"  Entry {i}: length {length}")
    
    # Save the logged data as CSV
    logged_array = np.array(logged_data, dtype=np.float32)
    with open(log_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in logged_array:
            writer.writerow(row)
    
    print(f"Battle log saved to {log_file} with shape {logged_array.shape}")
    
    return engine.winning_side


def _decision_to_action_vector(state: State, decision, player_side: int, 
                               vectorizer: ActionVectorizer) -> np.ndarray:
    """
    Convert a decision tuple to an action vector.
    
    Decision format: (move_idx, target_idx) for move actions or (-1, pokemon_idx) for switches
    """
    move_idx, target_pokemon_idx = decision
    
    print(f"move_idx: {move_idx}, target_pokemon_idx: {target_pokemon_idx}")
    
    if move_idx == -1:
        # Switch action
        side = state.sides[player_side]
        incoming_pokemon = side.team.reserve[target_pokemon_idx]
        return vectorizer.vectorize_switch_action(incoming_pokemon, target_pokemon_idx)
    else:
        # Move action
        side = state.sides[player_side]
        active_pokemon = side.team.active[0]  # Assuming single active for simplicity
        move = active_pokemon.battling_moves[move_idx]
        
        # Get target Pokemon
        opponent_side = state.sides[1 - player_side]
        target_pokemon = opponent_side.team.active[target_pokemon_idx]
        
        return vectorizer.vectorize_move_action(move, target_pokemon, target_pokemon_idx)


def main():
    n_active = 2
    team_size = 4
    n_moves = 4
    team = gen_team(team_size, n_moves), gen_team(team_size, n_moves)
    label_teams(team)
    team_view = TeamView(team[0]), TeamView(team[1])
    state = State(get_battle_teams(team, n_active))
    state_view = StateView(state, 0, team_view), StateView(state, 1, team_view)
    engine = BattleEngine(state, debug=True)
    agent = GreedyBattlePolicy(), RandomBattlePolicy()  # TreeSearchBattlePolicy(n_moves)
    print("~ Team 0 ~")
    print(team[0])
    print("~ Team 1 ~")
    print(team[1])
    winner = run_battle_with_logging(engine, agent, team_view, state_view, GodotClient(), 
                                     log_file="battle_log.csv")
    print("Side " + str(winner) + " wins!")


if __name__ == '__main__':
    main()