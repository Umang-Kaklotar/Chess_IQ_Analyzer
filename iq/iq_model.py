"""
IQ model for mapping chess performance to IQ scores.
Maps player performance metrics like accuracy and mistake rate to an estimated chess IQ score and knowledge level.
"""

import math
import numpy as np

class IQModel:
    """
    Maps chess performance metrics to IQ scores and knowledge levels.
    Uses a weighted model that considers accuracy, mistakes, blunders, 
    best moves, and other performance indicators.
    """
    
    def __init__(self):
        """Initialize the IQ model with weights and scaling factors."""
        # Base IQ score (average human IQ)
        self.base_iq = 100
        
        # Weights for different performance metrics
        self.accuracy_weight = 0.45
        self.mistake_weight = 0.15
        self.blunder_weight = 0.20
        self.best_move_weight = 0.10
        self.centipawn_loss_weight = 0.10
        
        # Scaling factors
        self.accuracy_scale = 60      # Maximum IQ points from accuracy
        self.mistake_scale = -5       # IQ points per mistake
        self.blunder_scale = -10      # IQ points per blunder
        self.best_move_scale = 2      # IQ points per best move
        self.centipawn_loss_scale = -0.05  # IQ points per centipawn loss
        
        # Knowledge level thresholds
        self.knowledge_levels = [
            {"name": "Novice", "min_iq": 0, "max_iq": 79, "elo_estimate": "< 800"},
            {"name": "Beginner", "min_iq": 80, "max_iq": 99, "elo_estimate": "800-1200"},
            {"name": "Intermediate", "min_iq": 100, "max_iq": 119, "elo_estimate": "1200-1600"},
            {"name": "Advanced", "min_iq": 120, "max_iq": 139, "elo_estimate": "1600-1900"},
            {"name": "Expert", "min_iq": 140, "max_iq": 159, "elo_estimate": "1900-2200"},
            {"name": "Master", "min_iq": 160, "max_iq": 179, "elo_estimate": "2200-2400"},
            {"name": "Grandmaster", "min_iq": 180, "max_iq": 200, "elo_estimate": "> 2400"}
        ]
        
        # Skill areas for assessment
        self.skill_areas = [
            "Tactical Awareness",
            "Strategic Planning",
            "Opening Knowledge",
            "Endgame Technique",
            "Calculation Ability",
            "Pattern Recognition",
            "Decision Making",
            "Time Management"
        ]
    
    def calculate_iq(self, accuracy, mistake_count, blunder_count, best_move_count, move_count, avg_centipawn_loss=None):
        """
        Calculate chess IQ based on performance metrics.
        
        Args:
            accuracy (float): Move accuracy percentage (0-100)
            mistake_count (int): Number of mistakes
            blunder_count (int): Number of blunders
            best_move_count (int): Number of best moves played
            move_count (int): Total number of moves
            avg_centipawn_loss (float, optional): Average centipawn loss per move
            
        Returns:
            int: Chess IQ score
        """
        # Normalize counts by total moves
        if move_count > 0:
            mistake_rate = mistake_count / move_count
            blunder_rate = blunder_count / move_count
            best_move_rate = best_move_count / move_count
        else:
            mistake_rate = blunder_rate = best_move_rate = 0
        
        # Calculate IQ components
        accuracy_component = (accuracy / 100) * self.accuracy_scale
        mistake_component = mistake_rate * self.mistake_scale
        blunder_component = blunder_rate * self.blunder_scale
        best_move_component = best_move_rate * self.best_move_scale
        
        # Calculate centipawn loss component if provided
        centipawn_loss_component = 0
        if avg_centipawn_loss is not None:
            # Cap the centipawn loss to avoid extreme penalties
            capped_loss = min(avg_centipawn_loss, 200)
            centipawn_loss_component = capped_loss * self.centipawn_loss_scale
        
        # Calculate weighted sum
        iq_adjustment = (
            accuracy_component * self.accuracy_weight +
            mistake_component * self.mistake_weight +
            blunder_component * self.blunder_weight +
            best_move_component * self.best_move_weight +
            centipawn_loss_component * self.centipawn_loss_weight
        )
        
        # Apply adjustment to base IQ
        chess_iq = self.base_iq + iq_adjustment
        
        # Apply a sigmoid function to smooth extreme values
        chess_iq = self._sigmoid_transform(chess_iq)
        
        # Ensure IQ is within reasonable bounds
        chess_iq = max(70, min(200, chess_iq))
        
        return round(chess_iq)
    
    def _sigmoid_transform(self, value, center=100, steepness=0.05):
        """
        Apply a sigmoid transformation to smooth extreme values.
        
        Args:
            value (float): Input value
            center (float): Center of the sigmoid curve
            steepness (float): Steepness of the curve
            
        Returns:
            float: Transformed value
        """
        # Shift the value to be centered around 0
        shifted = value - center
        
        # Apply sigmoid transformation
        sigmoid = 1 / (1 + math.exp(-steepness * shifted))
        
        # Scale back to IQ range and center around the base IQ
        return center + (sigmoid - 0.5) * 200
    
    def get_knowledge_level(self, iq_score):
        """
        Get the knowledge level for an IQ score.
        
        Args:
            iq_score (int): Chess IQ score
            
        Returns:
            dict: Knowledge level information
        """
        for level in self.knowledge_levels:
            if level["min_iq"] <= iq_score <= level["max_iq"]:
                return level
        
        # Fallback if no matching level is found
        return self.knowledge_levels[0]
    
    def get_percentile(self, iq_score):
        """
        Get the percentile for an IQ score using a normal distribution.
        
        Args:
            iq_score (int): Chess IQ score
            
        Returns:
            float: Percentile (0-100)
        """
        # Standard IQ distribution has mean 100 and standard deviation 15
        z_score = (iq_score - 100) / 15
        
        # Calculate percentile using the cumulative distribution function
        percentile = 100 * (0.5 * (1 + math.erf(z_score / math.sqrt(2))))
        
        return round(percentile, 1)
    
    def estimate_elo(self, iq_score):
        """
        Estimate Elo rating based on chess IQ.
        
        Args:
            iq_score (int): Chess IQ score
            
        Returns:
            int: Estimated Elo rating
        """
        # Simple linear mapping from IQ to Elo
        # This is a rough approximation
        if iq_score < 80:
            return 800
        elif iq_score < 100:
            return 800 + (iq_score - 80) * 20  # 800-1200
        elif iq_score < 120:
            return 1200 + (iq_score - 100) * 20  # 1200-1600
        elif iq_score < 140:
            return 1600 + (iq_score - 120) * 15  # 1600-1900
        elif iq_score < 160:
            return 1900 + (iq_score - 140) * 15  # 1900-2200
        elif iq_score < 180:
            return 2200 + (iq_score - 160) * 10  # 2200-2400
        else:
            return 2400 + (iq_score - 180) * 10  # 2400+
    
    def assess_skill_areas(self, performance_data):
        """
        Assess player's skill in different chess areas.
        
        Args:
            performance_data (dict): Player performance data
            
        Returns:
            dict: Skill assessments by area
        """
        skill_assessments = {}
        
        # Tactical Awareness
        tactical_score = self._calculate_tactical_score(
            performance_data.get('blunder_count', 0),
            performance_data.get('missed_tactics', 0),
            performance_data.get('move_count', 1)
        )
        skill_assessments["Tactical Awareness"] = tactical_score
        
        # Strategic Planning
        strategic_score = self._calculate_strategic_score(
            performance_data.get('positional_accuracy', 0),
            performance_data.get('long_term_plans', 0)
        )
        skill_assessments["Strategic Planning"] = strategic_score
        
        # Opening Knowledge
        opening_score = self._calculate_opening_score(
            performance_data.get('opening_accuracy', 0),
            performance_data.get('theory_moves', 0),
            performance_data.get('opening_mistakes', 0)
        )
        skill_assessments["Opening Knowledge"] = opening_score
        
        # Endgame Technique
        endgame_score = self._calculate_endgame_score(
            performance_data.get('endgame_accuracy', 0),
            performance_data.get('endgame_mistakes', 0)
        )
        skill_assessments["Endgame Technique"] = endgame_score
        
        # Calculation Ability
        calculation_score = self._calculate_calculation_score(
            performance_data.get('accuracy', 0),
            performance_data.get('complex_positions_accuracy', 0)
        )
        skill_assessments["Calculation Ability"] = calculation_score
        
        # Pattern Recognition
        pattern_score = self._calculate_pattern_score(
            performance_data.get('tactical_motifs_found', 0),
            performance_data.get('pattern_based_moves', 0)
        )
        skill_assessments["Pattern Recognition"] = pattern_score
        
        # Decision Making
        decision_score = self._calculate_decision_score(
            performance_data.get('critical_position_accuracy', 0),
            performance_data.get('decision_consistency', 0)
        )
        skill_assessments["Decision Making"] = decision_score
        
        # Time Management
        time_score = self._calculate_time_score(
            performance_data.get('time_pressure_mistakes', 0),
            performance_data.get('average_move_time', 0)
        )
        skill_assessments["Time Management"] = time_score
        
        return skill_assessments
    
    def _calculate_tactical_score(self, blunder_count, missed_tactics, move_count):
        """Calculate tactical awareness score."""
        # Default values if data is missing
        if 'missed_tactics' not in locals() or missed_tactics is None:
            missed_tactics = blunder_count // 2
        
        # Normalize by move count
        blunder_rate = blunder_count / max(1, move_count)
        missed_tactics_rate = missed_tactics / max(1, move_count)
        
        # Calculate score (0-100)
        score = 100 - (blunder_rate * 200) - (missed_tactics_rate * 150)
        return max(0, min(100, score))
    
    def _calculate_strategic_score(self, positional_accuracy, long_term_plans):
        """Calculate strategic planning score."""
        # Default values if data is missing
        if positional_accuracy is None:
            positional_accuracy = 50
        if long_term_plans is None:
            long_term_plans = 0
        
        # Calculate score (0-100)
        score = positional_accuracy * 0.7 + min(long_term_plans * 10, 30)
        return max(0, min(100, score))
    
    def _calculate_opening_score(self, opening_accuracy, theory_moves, opening_mistakes):
        """Calculate opening knowledge score."""
        # Default values if data is missing
        if opening_accuracy is None:
            opening_accuracy = 50
        if theory_moves is None:
            theory_moves = 0
        if opening_mistakes is None:
            opening_mistakes = 0
        
        # Calculate score (0-100)
        score = opening_accuracy * 0.6 + min(theory_moves * 5, 30) - (opening_mistakes * 10)
        return max(0, min(100, score))
    
    def _calculate_endgame_score(self, endgame_accuracy, endgame_mistakes):
        """Calculate endgame technique score."""
        # Default values if data is missing
        if endgame_accuracy is None:
            endgame_accuracy = 50
        if endgame_mistakes is None:
            endgame_mistakes = 0
        
        # Calculate score (0-100)
        score = endgame_accuracy * 0.8 - (endgame_mistakes * 15)
        return max(0, min(100, score))
    
    def _calculate_calculation_score(self, accuracy, complex_positions_accuracy):
        """Calculate calculation ability score."""
        # Default values if data is missing
        if accuracy is None:
            accuracy = 50
        if complex_positions_accuracy is None:
            complex_positions_accuracy = accuracy * 0.8
        
        # Calculate score (0-100)
        score = accuracy * 0.4 + complex_positions_accuracy * 0.6
        return max(0, min(100, score))
    
    def _calculate_pattern_score(self, tactical_motifs_found, pattern_based_moves):
        """Calculate pattern recognition score."""
        # Default values if data is missing
        if tactical_motifs_found is None:
            tactical_motifs_found = 0
        if pattern_based_moves is None:
            pattern_based_moves = 0
        
        # Calculate score (0-100)
        score = min(tactical_motifs_found * 15, 60) + min(pattern_based_moves * 10, 40)
        return max(0, min(100, score))
    
    def _calculate_decision_score(self, critical_position_accuracy, decision_consistency):
        """Calculate decision making score."""
        # Default values if data is missing
        if critical_position_accuracy is None:
            critical_position_accuracy = 50
        if decision_consistency is None:
            decision_consistency = 50
        
        # Calculate score (0-100)
        score = critical_position_accuracy * 0.6 + decision_consistency * 0.4
        return max(0, min(100, score))
    
    def _calculate_time_score(self, time_pressure_mistakes, average_move_time):
        """Calculate time management score."""
        # Default values if data is missing
        if time_pressure_mistakes is None:
            time_pressure_mistakes = 0
        if average_move_time is None:
            average_move_time = 30
        
        # Calculate score (0-100)
        time_efficiency = min(100, max(0, 100 - abs(average_move_time - 30) * 2))
        mistake_penalty = min(time_pressure_mistakes * 15, 70)
        
        score = time_efficiency * 0.7 - mistake_penalty
        return max(0, min(100, score))
    
    def get_improvement_suggestions(self, performance_data):
        """
        Get suggestions for improving chess IQ based on performance data.
        
        Args:
            performance_data (dict): Player performance data
            
        Returns:
            list: Improvement suggestions
        """
        suggestions = []
        
        # Assess skill areas
        skill_assessments = self.assess_skill_areas(performance_data)
        
        # Find weakest areas (up to 3)
        weak_areas = sorted(skill_assessments.items(), key=lambda x: x[1])[:3]
        
        # Generate suggestions for each weak area
        for area, score in weak_areas:
            if area == "Tactical Awareness" and score < 70:
                suggestions.append({
                    'area': 'Tactical Awareness',
                    'score': score,
                    'suggestion': 'Work on recognizing tactical patterns and calculating variations.',
                    'exercises': ['Tactics puzzles', 'Checkmate patterns', 'Pin and fork exercises']
                })
            
            elif area == "Strategic Planning" and score < 70:
                suggestions.append({
                    'area': 'Strategic Planning',
                    'score': score,
                    'suggestion': 'Develop your understanding of long-term positional concepts.',
                    'exercises': ['Study annotated master games', 'Positional exercises', 'Pawn structure analysis']
                })
            
            elif area == "Opening Knowledge" and score < 70:
                suggestions.append({
                    'area': 'Opening Knowledge',
                    'score': score,
                    'suggestion': 'Learn key principles and common variations in your openings.',
                    'exercises': ['Opening study', 'Opening repertoire development', 'Theory review']
                })
            
            elif area == "Endgame Technique" and score < 70:
                suggestions.append({
                    'area': 'Endgame Technique',
                    'score': score,
                    'suggestion': 'Study fundamental endgame positions and principles.',
                    'exercises': ['Basic endgame drills', 'King and pawn endings', 'Rook endgame practice']
                })
            
            elif area == "Calculation Ability" and score < 70:
                suggestions.append({
                    'area': 'Calculation Ability',
                    'score': score,
                    'suggestion': 'Practice calculating variations accurately and efficiently.',
                    'exercises': ['Visualization exercises', 'Calculation training', 'Complex position analysis']
                })
            
            elif area == "Pattern Recognition" and score < 70:
                suggestions.append({
                    'area': 'Pattern Recognition',
                    'score': score,
                    'suggestion': 'Improve your ability to recognize common patterns and motifs.',
                    'exercises': ['Tactical motif training', 'Pattern recognition drills', 'Middlegame themes']
                })
            
            elif area == "Decision Making" and score < 70:
                suggestions.append({
                    'area': 'Decision Making',
                    'score': score,
                    'suggestion': 'Work on evaluating positions and making sound decisions.',
                    'exercises': ['Candidate move exercises', 'Critical position analysis', 'Decision trees']
                })
            
            elif area == "Time Management" and score < 70:
                suggestions.append({
                    'area': 'Time Management',
                    'score': score,
                    'suggestion': 'Improve your time usage during games.',
                    'exercises': ['Blitz practice', 'Time allocation drills', 'Decision speed training']
                })
        
        # Add general suggestions if needed
        if len(suggestions) < 2:
            suggestions.append({
                'area': 'General Improvement',
                'score': None,
                'suggestion': 'Continue practicing and analyzing your games regularly.',
                'exercises': ['Post-game analysis', 'Study master games', 'Solve puzzles daily']
            })
        
        return suggestions
