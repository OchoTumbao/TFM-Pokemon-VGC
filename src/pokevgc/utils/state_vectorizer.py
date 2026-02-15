"""
State vectorizer for creating numerical representations of game states.

This module provides utilities to convert a game state into a numerical vector
representation that only includes information the current player knows.
Unknown information (like opponent's exact move sets) is excluded.
"""

import numpy as np
from vgc2.battle_engine.game_state import State
from vgc2.battle_engine.modifiers import (
    Weather, Terrain, Status, Type, Stat, Category
)
from vgc2.battle_engine.pokemon import BattlingPokemon


class StateVectorizer:
    """
    Converts game states to numerical vectors containing only visible information.
    
    The vector includes:
    - Weather and terrain conditions
    - Side conditions (reflect, light screen, tailwind, hazards)
    - Active Pokemon stats and status
    - Visible Pokemon reserve information
    - Type matchups against known opponent types
    """
    
    def __init__(self, n_active: int = 2, n_reserve: int = 4):
        """
        Initialize the vectorizer with team configuration.
        
        Args:
            n_active: Number of active Pokemon per team (typically 2 for doubles)
            n_reserve: Maximum number of reserve Pokemon per team
        """
        self.n_active = n_active
        self.n_reserve = n_reserve
        self.n_types = len(Type)
        self.n_stats = 6  # HP, ATK, DEF, SPA, SPD, SPE
        self.n_status = len(Status)
        
        self._calculate_vector_size()
    
    def _calculate_vector_size(self) -> int:
        """Calculate the total size of the state vector."""
        # Global conditions
        global_size = 2  # weather + terrain + trickroom (one-hot or continuous)
        
        # Per side conditions  
        side_condition_size = 4  # reflect, light screen, tailwind, stealth rock
        per_side_size = side_condition_size
        
        # Per Pokemon in active team
        pokemon_stat_size = (
            1 +  # HP (normalized)
            1 +  # Max HP
            (self.n_stats - 1) +  # Stats (ATK, DEF, SPA, SPD, SPE - excludes HP)
            8 +  # Boosts (stat stages)
            self.n_status +  # Status (one-hot)
            2 * self.n_types +  # Types (one-hot for each of 2 types)
            1    # Protect status
        )
        
        active_size = self.n_active * pokemon_stat_size
        
        # Per Pokemon in reserve
        reserve_pokemon_size = (
            1 +  # HP (normalized)
            1 +  # Max HP
            1    # Fainted status
        )
        reserve_size = self.n_reserve * reserve_pokemon_size
        
        self.vector_size = global_size + 2 * (per_side_size + active_size + reserve_size)
        return self.vector_size
    
    def get_vector_size(self) -> int:
        """Get the total size of the vectorized state."""
        return self.vector_size
    
    def vectorize(self, state: State, player_side_idx: int) -> np.ndarray:
        """
        Convert a game state to a numerical vector from the given player's perspective.
        
        Args:
            state: The current game state
            player_side_idx: The index of the player (0 or 1)
        
        Returns:
            A numpy array representing the state vector
        """
        vector_parts = []
        
        # Global conditions (visible to both players)
        vector_parts.extend(self._encode_global_conditions(state))
        
        # Player's own side (fully known)
        vector_parts.extend(self._encode_side(state.sides[player_side_idx], visible=True))
        
        # Opponent's side (only observable information)
        opponent_idx = 1 - player_side_idx
        vector_parts.extend(self._encode_side(state.sides[opponent_idx], visible=False))
        
        return np.array(vector_parts, dtype=np.float32)
    
    def _encode_global_conditions(self, state: State) -> list[float]:
        """Encode global battlefield conditions."""
        features = []
        
        # Weather (one-hot encoding)
        weather_vector = self._encode_weather(state.weather)
        features.extend(weather_vector)
        
        # Terrain (one-hot encoding)
        terrain_vector = self._encode_terrain(state.field)
        features.extend(terrain_vector)
        
        # Trick Room
        features.append(1.0 if state.trickroom else 0.0)
        
        return features
    
    def _encode_weather(self, weather: Weather) -> list[float]:
        """Encode weather condition as one-hot or categorical."""
        weathers = [w for w in Weather]
        vector = [0.0] * len(weathers)
        if weather in weathers:
            vector[weathers.index(weather)] = 1.0
        return vector
    
    def _encode_terrain(self, terrain: Terrain) -> list[float]:
        """Encode terrain condition as one-hot or categorical."""
        terrains = [t for t in Terrain]
        vector = [0.0] * len(terrains)
        if terrain in terrains:
            vector[terrains.index(terrain)] = 1.0
        return vector
    
    def _encode_side(self, side, visible: bool = True) -> list[float]:
        """
        Encode a side's information.
        
        Args:
            side: The Side object
            visible: Whether we know all details (player's own side) or only observable info
        """
        features = []
        
        # Side conditions
        features.append(1.0 if side.conditions.reflect else 0.0)
        features.append(1.0 if side.conditions.lightscreen else 0.0)
        features.append(1.0 if side.conditions.tailwind else 0.0)
        features.append(1.0 if side.conditions.stealth_rock else 0.0)
        
        # Active Pokemon
        for i in range(self.n_active):
            if i < len(side.team.active):
                features.extend(self._encode_pokemon(side.team.active[i], visible=visible))
            else:
                # Padding for missing active slots
                features.extend(self._encode_pokemon(None, visible=visible))
        
        # Reserve Pokemon
        for i in range(self.n_reserve):
            if i < len(side.team.reserve):
                features.extend(self._encode_reserve_pokemon(side.team.reserve[i], visible=visible))
            else:
                # Padding for missing reserve slots
                features.extend(self._encode_reserve_pokemon(None, visible=visible))
        
        return features
    
    def _encode_pokemon(self, pokemon: BattlingPokemon | None, visible: bool = True) -> list[float]:
        """
        Encode a Pokemon's state.
        
        Args:
            pokemon: The BattlingPokemon or None for padding
            visible: Whether we know detailed information (only for player's own team)
        """
        features = []
        
        if pokemon is None:
            # Padding vector - must match the size when pokemon is not None
            padding_size = (
                1 +  # HP normalized
                1 +  # Max HP
                (self.n_stats - 1) +  # Stats (ATK, DEF, SPA, SPD, SPE - excludes HP)
                8 +  # Boosts (exactly 8 stat stage boosts)
                self.n_status +  # Status
                2 * self.n_types +  # Types (dual types - fixed!)
                1    # Protect
            )
            return [0.0] * padding_size
        
        # Current HP (normalized 0-1)
        max_hp = pokemon.constants.stats[Stat.MAX_HP]
        current_hp = pokemon.hp
        features.append(current_hp / max_hp if max_hp > 0 else 0.0)
        
        # Max HP (absolute value, might normalize later)
        features.append(float(max_hp))
        
        if visible:
            # Only include if this is the player's own Pokemon
            # Base stats (excluding HP which is handled above)
            for stat_idx in [Stat.ATTACK, Stat.DEFENSE, Stat.SPECIAL_ATTACK, 
                            Stat.SPECIAL_DEFENSE, Stat.SPEED]:
                features.append(float(pokemon.constants.stats[stat_idx]))
            
            # Stat boosts (stages) - always exactly 8 boosts
            boosts = pokemon.boosts[1:] if hasattr(pokemon, 'boosts') else []
            for i in range(8):
                if i < len(boosts):
                    features.append(float(boosts[i]))
                else:
                    features.append(0.0)
        else:
            # Opponent's Pokemon: we don't know base stats, only infer from visible info
            # Add placeholder stats (could be replaced with inferred values)
            for _ in range(self.n_stats - 1):  # -1 because HP is separate
                features.append(0.0)
            
            # Boosts are visible to both players - always exactly 8
            boosts = pokemon.boosts[1:] if hasattr(pokemon, 'boosts') else []
            for i in range(8):
                if i < len(boosts):
                    features.append(float(boosts[i]))
                else:
                    features.append(0.0)
        
        # Status condition (one-hot encoding)
        status_vector = self._encode_status(pokemon.status)
        features.extend(status_vector)
        
        # Types (one-hot encoding for both primary and secondary types)
        type_vector = self._encode_types(pokemon.types)
        features.extend(type_vector)
        
        # Protect status
        features.append(1.0 if pokemon.protect else 0.0)
        
        return features
    
    def _encode_reserve_pokemon(self, pokemon: BattlingPokemon | None, visible: bool = True) -> list[float]:
        """
        Encode a reserve Pokemon's state (limited information).
        
        Args:
            pokemon: The BattlingPokemon or None for padding
            visible: Whether we know detailed information
        """
        features = []
        
        if pokemon is None:
            # Padding vector
            return [0.0, 0.0, 0.0]
        
        # Current HP (normalized)
        max_hp = pokemon.constants.stats[Stat.MAX_HP]
        current_hp = pokemon.hp
        features.append(current_hp / max_hp if max_hp > 0 else 0.0)
        
        # Max HP
        features.append(float(max_hp))
        
        # Fainted status
        features.append(1.0 if pokemon.fainted() else 0.0)
        
        return features
    
    def _encode_status(self, status: Status) -> list[float]:
        """Encode Pokemon status condition as one-hot vector."""
        statuses = [s for s in Status]
        vector = [0.0] * len(statuses)
        if status in statuses:
            vector[statuses.index(status)] = 1.0
        return vector
    
    def _encode_types(self, types: list[Type]) -> list[float]:
        """
        Encode Pokemon types as one-hot vectors for both primary and secondary type slots.
        
        Always encodes exactly 2 type slots:
        - If Pokemon has 1 type: primary=encoded, secondary=all zeros
        - If Pokemon has 2 types: primary=encoded, secondary=encoded
        - If Pokemon has no types: both slots are all zeros
        
        This ensures consistent vector size regardless of how many actual types the Pokemon has.
        """
        type_list = [t for t in Type]
        vector = [0.0] * (len(type_list) * 2)
        
        # Always encode primary type (slot 0)
        if types and len(types) > 0 and types[0] in type_list:
            vector[type_list.index(types[0])] = 1.0
        # If no primary type, slot 0 is all zeros
        
        # Always encode secondary type (slot 1)  
        if types and len(types) > 1 and types[1] in type_list:
            vector[len(type_list) + type_list.index(types[1])] = 1.0
        # If no secondary type or Pokemon only has 1 type, slot 1 is all zeros
        
        return vector


def vectorize_state(state: State, player_side_idx: int, 
                   n_active: int = 2, n_reserve: int = 4) -> np.ndarray:
    """
    Convenience function to vectorize a state.
    
    Args:
        state: The game state to vectorize
        player_side_idx: Which player's perspective (0 or 1)
        n_active: Number of active Pokemon (default 2 for VGC doubles)
        n_reserve: Maximum number of reserve Pokemon
    
    Returns:
        Numpy array of the state vector
    """
    vectorizer = StateVectorizer(n_active=n_active, n_reserve=n_reserve)
    return vectorizer.vectorize(state, player_side_idx)
