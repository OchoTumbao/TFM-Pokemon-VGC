"""
Action vectorizer for creating numerical representations of battle actions.

This module provides utilities to convert battle actions (moves or switches) 
into numerical vector representations that can be fed into neural networks.
"""

import numpy as np
from vgc2.battle_engine.pokemon import BattlingPokemon
from vgc2.battle_engine.move import BattlingMove, Move
from vgc2.battle_engine.modifiers import Type, Category, Stat, Status, Weather, Terrain
from vgc2.battle_engine import BattleRuleParam
from vgc2.battle_engine.damage_calculator import type_effectiveness_modifier


class ActionVectorizer:
    """
    Converts battle actions into numerical vectors with unified representation.
    
    Every action (move or switch) produces a vector with consistent semantic meaning:
    - Action type flag (move=1, switch=0)
    - Target/Incoming Pokemon info (consistent positions regardless of action)
    - Move properties (zeros for switch actions)
    - Type effectiveness (for moves)
    
    This ensures ML models can learn transferable features across action types.
    """
    
    def __init__(self, params: BattleRuleParam = BattleRuleParam(), 
                 n_active: int = 2, n_reserve: int = 4):
        """
        Initialize the action vectorizer.
        
        Args:
            params: Battle rule parameters for damage calculations
            n_active: Number of active Pokémon per team
            n_reserve: Maximum number of reserve Pokémon
        """
        self.params = params
        self.n_active = n_active
        self.n_reserve = n_reserve
        self.n_types = len(Type)
        self.n_categories = len(Category)
        self.n_status = len(Status)
        self.n_stats = 6  # HP, ATK, DEF, SPA, SPD, SPE
        
        self._calculate_vector_size()
    
    def _calculate_vector_size(self) -> int:
        """Calculate the total size of the unified action vector."""
        # Unified structure for all actions
        self.vector_size = (
            1 +  # Action type flag (1=move, 0=switch)
            # Target/Incoming Pokemon info (consistent positions)
            1 +  # HP (normalized)
            1 +  # Max HP
            1 +  # Fainted status
            2 * self.n_types +  # Types (one-hot for each of 2 types)
            self.n_status +  # Status condition (one-hot)
            # Move properties (zeros for switch actions)
            self.n_types +  # Move type (one-hot)
            1 +  # Base power (normalized)
            1 +  # Accuracy
            1 +  # PP remaining (normalized)
            1 +  # Priority
            self.n_categories +  # Category (one-hot)
            1 +  # Effect probability
            # Move effects (boolean flags) - zeros for switch actions
            1 +  # Force switch
            1 +  # Self switch
            1 +  # Ignore evasion
            1 +  # Protect
            8 +  # Stat boosts (one for each stat)
            1 +  # Self boosts flag
            1 +  # Heal amount
            1 +  # Recoil amount
            1 +  # Weather change
            1 +  # Terrain change
            1 +  # Trick room toggle
            1 +  # Type change
            1 +  # Reflect toggle
            1 +  # Light screen toggle
            1 +  # Tailwind toggle
            1 +  # Hazard
            1 +  # Status condition effect
            1 +  # Disable flag
            1 +  # Target index
            3    # Type effectiveness [neutral, super_effective, resistant]
        )
        return self.vector_size
    
    def get_vector_size(self) -> int:
        """Get the total size of the action vector."""
        return self.vector_size
    
    def vectorize_move_action(self, move: BattlingMove, target: BattlingPokemon, 
                             target_index: int, max_pp: int = 20) -> np.ndarray:
        """
        Convert a move action to a unified vector representation.
        
        Args:
            move: The BattlingMove to vectorize
            target: The target BattlingPokemon
            target_index: Index of the target (0 or 1 in doubles)
            max_pp: Maximum PP for normalization
        
        Returns:
            A numpy array representing the move action with consistent semantic meaning
        """
        vector = np.zeros(self.vector_size, dtype=np.float32)
        idx = 0
        
        # Action type flag
        vector[idx] = 1.0  # Is move action
        idx += 1
        
        # Target Pokemon info (consistent positions for all actions)
        max_hp = target.constants.stats[Stat.MAX_HP]
        vector[idx] = target.hp / max_hp if max_hp > 0 else 0.0  # HP normalized
        idx += 1
        
        vector[idx] = float(max_hp)  # Max HP
        idx += 1
        
        vector[idx] = 1.0 if target.fainted() else 0.0  # Fainted status
        idx += 1
        
        # Target types (one-hot for both primary and secondary)
        type_vector = self._encode_pokemon_types(target.types)
        vector[idx:idx + 2 * self.n_types] = type_vector
        idx += 2 * self.n_types
        
        # Target status (one-hot)
        status_vector = self._encode_status(target.status)
        vector[idx:idx + self.n_status] = status_vector
        idx += self.n_status
        
        # Move properties
        move_type_vector = self._encode_type(move.constants.pkm_type)
        vector[idx:idx + self.n_types] = move_type_vector
        idx += self.n_types
        
        # Base power (normalized 0-1, max 250)
        vector[idx] = move.constants.base_power / 250.0
        idx += 1
        
        # Accuracy (0-1)
        vector[idx] = move.constants.accuracy
        idx += 1
        
        # PP remaining (normalized)
        vector[idx] = move.pp / max_pp if max_pp > 0 else 0.0
        idx += 1
        
        # Priority
        vector[idx] = float(move.constants.priority)
        idx += 1
        
        # Category (one-hot)
        category_vector = self._encode_category(move.constants.category)
        vector[idx:idx + self.n_categories] = category_vector
        idx += self.n_categories
        
        # Effect probability
        vector[idx] = move.constants.effect_prob
        idx += 1
        
        # Move effects (boolean flags)
        vector[idx] = 1.0 if move.constants.force_switch else 0.0
        idx += 1
        
        vector[idx] = 1.0 if move.constants.self_switch else 0.0
        idx += 1
        
        vector[idx] = 1.0 if move.constants.ignore_evasion else 0.0
        idx += 1
        
        vector[idx] = 1.0 if move.constants.protect else 0.0
        idx += 1
        
        # Stat boosts (all 8 indices)
        for boost in move.constants.boosts:
            vector[idx] = float(boost) / 2.0  # Normalize to roughly -3 to +3
            idx += 1
        
        # Self boosts flag
        vector[idx] = 1.0 if move.constants.self_boosts else 0.0
        idx += 1
        
        # Heal amount (normalized 0-1)
        vector[idx] = move.constants.heal
        idx += 1
        
        # Recoil amount (normalized 0-1)
        vector[idx] = move.constants.recoil
        idx += 1
        
        # Weather change
        vector[idx] = 1.0 if move.constants.weather_start != Weather.CLEAR else 0.0
        idx += 1
        
        # Terrain change
        vector[idx] = 1.0 if move.constants.field_start != Terrain.NONE else 0.0
        idx += 1
        
        # Trick room toggle
        vector[idx] = 1.0 if move.constants.toggle_trickroom else 0.0
        idx += 1
        
        # Type change
        vector[idx] = 1.0 if move.constants.change_type else 0.0
        idx += 1
        
        # Reflect toggle
        vector[idx] = 1.0 if move.constants.toggle_reflect else 0.0
        idx += 1
        
        # Light screen toggle
        vector[idx] = 1.0 if move.constants.toggle_lightscreen else 0.0
        idx += 1
        
        # Tailwind toggle
        vector[idx] = 1.0 if move.constants.toggle_tailwind else 0.0
        idx += 1
        
        # Hazard (stealth rock, spikes, etc)
        from vgc2.battle_engine.modifiers import Hazard
        vector[idx] = 1.0 if move.constants.hazard != Hazard.NONE else 0.0
        idx += 1
        
        # Status condition
        vector[idx] = 1.0 if move.constants.status != Status.NONE else 0.0
        idx += 1
        
        # Disable flag
        vector[idx] = 1.0 if move.constants.disable else 0.0
        idx += 1
        
        # Target index
        vector[idx] = float(target_index)
        idx += 1
        
        # Type effectiveness against target
        effectiveness_vector = self._encode_effectiveness(
            move.constants.pkm_type, 
            target.types
        )
        vector[idx:idx + 3] = effectiveness_vector
        
        return vector
    
    def vectorize_switch_action(self, incoming_pokemon: BattlingPokemon, 
                               reserve_index: int) -> np.ndarray:
        """
        Convert a switch action to a unified vector representation.
        
        The vector has the same semantic structure as move actions - only the
        action type flag and move properties differ.
        
        Args:
            incoming_pokemon: The BattlingPokemon being switched in
            reserve_index: Index in the reserve team
        
        Returns:
            A numpy array representing the switch action with consistent semantic meaning
        """
        vector = np.zeros(self.vector_size, dtype=np.float32)
        idx = 0
        
        # Action type flag
        vector[idx] = 0.0  # Not a move action (it's a switch)
        idx += 1
        
        # Incoming Pokemon info (at same positions as target Pokemon for moves)
        max_hp = incoming_pokemon.constants.stats[Stat.MAX_HP]
        vector[idx] = incoming_pokemon.hp / max_hp if max_hp > 0 else 0.0  # HP normalized
        idx += 1
        
        vector[idx] = float(max_hp)  # Max HP
        idx += 1
        
        vector[idx] = 1.0 if incoming_pokemon.fainted() else 0.0  # Fainted status
        idx += 1
        
        # Incoming Pokemon types (one-hot for both)
        type_vector = self._encode_pokemon_types(incoming_pokemon.types)
        vector[idx:idx + 2 * self.n_types] = type_vector
        idx += 2 * self.n_types
        
        # Incoming Pokemon status (one-hot)
        status_vector = self._encode_status(incoming_pokemon.status)
        vector[idx:idx + self.n_status] = status_vector
        idx += self.n_status
        
        # Move properties are all zeros for switch actions (semantically consistent)
        # The rest of the vector (move type, power, accuracy, effects, etc.) remains zeros
        # This is intentional - it maintains consistent semantic meaning across positions
        
        return vector
    
    def _encode_type(self, pkm_type: Type) -> np.ndarray:
        """Encode a Pokémon type as one-hot vector."""
        type_list = list(Type)
        vector = np.zeros(len(type_list), dtype=np.float32)
        if pkm_type in type_list:
            vector[type_list.index(pkm_type)] = 1.0
        return vector
    
    def _encode_pokemon_types(self, types: list[Type]) -> np.ndarray:
        """Encode Pokémon types as one-hot vectors for both primary and secondary types."""
        type_list = list(Type)
        vector = np.zeros(len(type_list) * 2, dtype=np.float32)
        
        # Encode primary type
        if types and len(types) > 0 and types[0] in type_list:
            vector[type_list.index(types[0])] = 1.0
        
        # Encode secondary type
        if types and len(types) > 1 and types[1] in type_list:
            vector[len(type_list) + type_list.index(types[1])] = 1.0
        
        return vector
    
    def _encode_category(self, category: Category) -> np.ndarray:
        """Encode a move category as one-hot vector."""
        category_list = list(Category)
        vector = np.zeros(len(category_list), dtype=np.float32)
        if category in category_list:
            vector[category_list.index(category)] = 1.0
        return vector
    
    def _encode_status(self, status: Status) -> np.ndarray:
        """Encode a Pokémon status as one-hot vector."""
        status_list = list(Status)
        vector = np.zeros(len(status_list), dtype=np.float32)
        if status in status_list:
            vector[status_list.index(status)] = 1.0
        return vector
    
    def _encode_effectiveness(self, move_type: Type, target_types: list[Type]) -> np.ndarray:
        """
        Encode type effectiveness against target.
        
        Returns a 3-element vector: [neutral, super_effective, resistant]
        
        Args:
            move_type: The attacking move's type
            target_types: List of target Pokémon types
        
        Returns:
            One-hot encoded effectiveness category
        """
        modifier = type_effectiveness_modifier(self.params, move_type, target_types)
        
        # Categorize effectiveness
        # Super effective: 2x or more
        # Neutral: 1x
        # Resistant: 0.5x or less
        vector = np.zeros(3, dtype=np.float32)
        
        if modifier >= 2.0:
            vector[1] = 1.0  # Super effective
        elif modifier <= 0.5:
            vector[2] = 1.0  # Resistant
        else:
            vector[0] = 1.0  # Neutral
        
        return vector


def vectorize_move(move: BattlingMove, target: BattlingPokemon, target_index: int,
                  params: BattleRuleParam = BattleRuleParam(),
                  max_pp: int = 20) -> np.ndarray:
    """
    Convenience function to vectorize a move action.
    
    Args:
        move: The BattlingMove
        target: The target BattlingPokemon
        target_index: Index of target (0 or 1)
        params: Battle rule parameters
        max_pp: Maximum PP for normalization
    
    Returns:
        Numpy array of the action vector
    """
    vectorizer = ActionVectorizer(params=params)
    return vectorizer.vectorize_move_action(move, target, target_index, max_pp)


def vectorize_switch(incoming_pokemon: BattlingPokemon, reserve_index: int,
                    params: BattleRuleParam = BattleRuleParam()) -> np.ndarray:
    """
    Convenience function to vectorize a switch action.
    
    Args:
        incoming_pokemon: The BattlingPokemon entering battle
        reserve_index: Its index in the reserve team
        params: Battle rule parameters
    
    Returns:
        Numpy array of the action vector
    """
    vectorizer = ActionVectorizer(params=params)
    return vectorizer.vectorize_switch_action(incoming_pokemon, reserve_index)
