"""
Chess opening recognition and analysis.
Detects known chess openings and compares user moves with opening theory.
"""

class OpeningRecognizer:
    """
    Recognizes chess openings from move sequences and compares with opening theory.
    Provides information about opening quality and deviation from theory.
    """
    
    def __init__(self):
        """Initialize the opening recognizer with a database of common openings."""
        # Dictionary of opening sequences and their names
        self.openings = self._init_openings()
        
        # Dictionary of opening variations and their moves
        self.opening_variations = self._init_opening_variations()
        
        # Dictionary of opening evaluations
        self.opening_evaluations = self._init_opening_evaluations()
    
    def _init_openings(self):
        """Initialize the opening database with common openings."""
        # Format: sequence of moves -> opening name
        return {
            "e2e4 e7e5": "King's Pawn Opening",
            "e2e4 e7e5 g1f3": "King's Knight Opening",
            "e2e4 e7e5 g1f3 b8c6": "Two Knights Defense",
            "e2e4 e7e5 g1f3 b8c6 f1c4": "Italian Game",
            "e2e4 e7e5 g1f3 b8c6 f1b5": "Ruy Lopez",
            "e2e4 e7e5 f2f4": "King's Gambit",
            "e2e4 e7e5 f2f4 e5f4": "King's Gambit Accepted",
            "e2e4 e7e5 f2f4 d7d5": "Falkbeer Counter-Gambit",
            "e2e4 c7c5": "Sicilian Defense",
            "e2e4 c7c5 g1f3": "Open Sicilian",
            "e2e4 c7c5 g1f3 d7d6": "Sicilian Defense, Classical Variation",
            "e2e4 c7c5 g1f3 b8c6": "Sicilian Defense, Old Sicilian",
            "e2e4 c7c5 g1f3 e7e6": "Sicilian Defense, French Variation",
            "e2e4 c7c5 b1c3": "Sicilian Defense, Closed Variation",
            "e2e4 e7e6": "French Defense",
            "e2e4 e7e6 d2d4": "French Defense, Normal Variation",
            "e2e4 e7e6 d2d4 d7d5": "French Defense, Classical Variation",
            "e2e4 c7c6": "Caro-Kann Defense",
            "e2e4 c7c6 d2d4": "Caro-Kann Defense, Main Line",
            "e2e4 c7c6 d2d4 d7d5": "Caro-Kann Defense, Classical Variation",
            "e2e4 d7d5": "Scandinavian Defense",
            "e2e4 d7d5 e4d5 d8d5": "Scandinavian Defense, Queen Recapture",
            "e2e4 d7d5 e4d5 g8f6": "Scandinavian Defense, Modern Variation",
            "e2e4 g8f6": "Alekhine's Defense",
            "e2e4 d7d6": "Pirc Defense",
            "d2d4 d7d5": "Queen's Pawn Opening",
            "d2d4 d7d5 c2c4": "Queen's Gambit",
            "d2d4 d7d5 c2c4 e7e6": "Queen's Gambit Declined",
            "d2d4 d7d5 c2c4 c7c6": "Slav Defense",
            "d2d4 d7d5 c2c4 d5c4": "Queen's Gambit Accepted",
            "d2d4 g8f6": "Indian Defense",
            "d2d4 g8f6 c2c4 e7e6": "Queen's Indian Defense",
            "d2d4 g8f6 c2c4 g7g6": "King's Indian Defense",
            "d2d4 g8f6 c2c4 e7e6 g1f3 b7b6": "Queen's Indian Defense",
            "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7": "King's Indian Defense, Main Line",
            "d2d4 g8f6 c2c4 c7c5": "Benoni Defense",
            "d2d4 f7f5": "Dutch Defense",
            "c2c4": "English Opening",
            "c2c4 e7e5": "English Opening, Reversed Sicilian",
            "c2c4 c7c5": "English Opening, Symmetrical Variation",
            "g1f3": "Réti Opening",
            "g1f3 d7d5 c2c4": "Réti Opening, King's Indian Attack",
            "b2b3": "Larsen's Opening",
            "f2f4": "Bird's Opening"
        }
    
    def _init_opening_variations(self):
        """Initialize database of opening variations with recommended moves."""
        # Format: opening name -> {move number -> {player color -> recommended moves}}
        return {
            "Sicilian Defense": {
                3: {"white": ["g1f3", "b1c3", "c2c3"]},
                3: {"black": ["d7d6", "b8c6", "e7e6", "g7g6"]}
            },
            "French Defense": {
                3: {"white": ["d2d4", "b1c3", "e4e5"]},
                3: {"black": ["d7d5"]}
            },
            "Ruy Lopez": {
                4: {"white": ["c2c3", "d2d4", "b1c3"]},
                4: {"black": ["g8f6", "f8c5", "f8e7", "a7a6"]}
            },
            "Queen's Gambit": {
                3: {"white": ["b1c3", "g1f3"]},
                3: {"black": ["e7e6", "c7c6", "d5c4"]}
            },
            "King's Indian Defense": {
                3: {"white": ["b1c3", "g1f3"]},
                3: {"black": ["f8g7", "d7d6"]}
            }
        }
    
    def _init_opening_evaluations(self):
        """Initialize evaluations for common openings."""
        # Format: opening name -> evaluation in centipawns (positive for white advantage)
        return {
            "King's Pawn Opening": 15,
            "Queen's Pawn Opening": 10,
            "Sicilian Defense": -5,
            "French Defense": 0,
            "Caro-Kann Defense": 5,
            "Ruy Lopez": 20,
            "Italian Game": 15,
            "Queen's Gambit": 15,
            "Queen's Gambit Declined": 5,
            "Queen's Gambit Accepted": 0,
            "King's Indian Defense": 0,
            "English Opening": 5,
            "Réti Opening": 5
        }
    
    def recognize_opening(self, moves):
        """
        Recognize the opening from a sequence of moves.
        
        Args:
            moves (list): List of moves in algebraic notation
            
        Returns:
            dict: Opening information including name, theory, and evaluation
        """
        # Convert moves to a string for lookup
        move_str = " ".join(moves)
        
        # Find the longest matching sequence
        matching_opening = None
        max_length = 0
        
        for sequence, opening_name in self.openings.items():
            if move_str.startswith(sequence) and len(sequence) > max_length:
                matching_opening = opening_name
                max_length = len(sequence)
        
        if matching_opening:
            # Get theory information
            theory = self._get_opening_theory(matching_opening)
            
            # Get evaluation
            evaluation = self.opening_evaluations.get(matching_opening, 0)
            
            # Check if there are recommended next moves
            next_moves = self._get_next_recommended_moves(matching_opening, len(moves))
            
            return {
                'name': matching_opening,
                'moves': len(moves),
                'theory': theory,
                'evaluation': evaluation,
                'next_moves': next_moves,
                'is_mainline': self._is_mainline(moves, matching_opening)
            }
        else:
            return {
                'name': "Unknown Opening",
                'moves': len(moves),
                'theory': None,
                'evaluation': 0,
                'next_moves': [],
                'is_mainline': False
            }
    
    def _get_opening_theory(self, opening_name):
        """
        Get theory information for an opening.
        
        Args:
            opening_name (str): Name of the opening
            
        Returns:
            dict: Opening theory information
        """
        # Opening theories with detailed information
        theories = {
            "King's Pawn Opening": {
                'description': "The King's Pawn Opening is one of the most popular chess openings, beginning with 1.e4. It immediately stakes a claim in the center and opens lines for the queen and king's bishop.",
                'strengths': "Quick development, control of the center, open lines for pieces",
                'weaknesses': "The e4 pawn can become a target",
                'famous_games': ["Kasparov vs. Topalov, 1999", "Morphy vs. Duke of Brunswick and Count Isouard, 1858"],
                'key_ideas': ["Develop pieces quickly", "Control the center", "Castle early"],
                'typical_plans': ["Kingside attack", "Central pawn break"]
            },
            "Queen's Gambit": {
                'description': "The Queen's Gambit is one of the oldest known chess openings. It begins with 1.d4 d5 2.c4 and offers a pawn sacrifice for quick development and central control.",
                'strengths': "Strong center control, good development opportunities",
                'weaknesses': "Can lead to closed positions with less tactical opportunities",
                'famous_games': ["Kasparov vs. Karpov, World Championship 1985", "Capablanca vs. Alekhine, World Championship 1927"],
                'key_ideas': ["Control the center with pawns", "Develop pieces harmoniously", "Create pressure on the queenside"],
                'typical_plans': ["Minority attack on the queenside", "Central pawn break with e4"]
            },
            "Sicilian Defense": {
                'description': "The Sicilian Defense is the most popular response to 1.e4. Black immediately fights for the center with a flank pawn, leading to asymmetrical positions.",
                'strengths': "Creates imbalance, fights for central control",
                'weaknesses': "Can lead to complex positions requiring precise knowledge",
                'famous_games': ["Fischer vs. Spassky, World Championship 1972, Game 6", "Kasparov vs. Topalov, Wijk aan Zee 1999"],
                'key_ideas': ["Counter-attack in the center", "Pressure on the d4 square", "Queenside expansion"],
                'typical_plans': ["Queenside pawn majority push", "Kingside attack with opposite-side castling"]
            },
            "French Defense": {
                'description': "The French Defense begins with 1.e4 e6 and is characterized by a solid but somewhat cramped position for Black. It leads to asymmetrical pawn structures.",
                'strengths': "Solid pawn structure, good defensive properties",
                'weaknesses': "The light-squared bishop can be difficult to develop",
                'famous_games': ["Kasparov vs. Karpov, World Championship 1984, Game 16", "Tal vs. Botvinnik, World Championship 1960"],
                'key_ideas': ["Counter-attack in the center with ...c5", "Pressure on White's center"],
                'typical_plans': ["Queenside expansion", "Kingside pawn storm after castling"]
            },
            "Ruy Lopez": {
                'description': "The Ruy Lopez (Spanish Opening) is one of the oldest and most respected openings, beginning with 1.e4 e5 2.Nf3 Nc6 3.Bb5. It puts pressure on Black's knight and prepares for castling.",
                'strengths': "Solid development, good control of the center",
                'weaknesses': "The bishop on b5 can be targeted",
                'famous_games': ["Kasparov vs. Karpov, World Championship 1990", "Fischer vs. Spassky, World Championship 1972, Game 1"],
                'key_ideas': ["Pressure on the e5 pawn", "Control of the center", "Kingside castling"],
                'typical_plans': ["Kingside attack", "Central pawn break with d4"]
            }
        }
        
        # Return theory information if available, otherwise return generic information
        return theories.get(opening_name, {
            'description': f"The {opening_name} is a chess opening that leads to positions with unique strategic characteristics.",
            'strengths': "Varies depending on the specific variation",
            'weaknesses': "Varies depending on the specific variation",
            'famous_games': [],
            'key_ideas': ["Develop pieces", "Control the center", "Ensure king safety"],
            'typical_plans': ["Depends on the specific position"]
        })
    
    def _get_next_recommended_moves(self, opening_name, move_count):
        """
        Get recommended next moves for an opening.
        
        Args:
            opening_name (str): Name of the opening
            move_count (int): Number of moves played so far
            
        Returns:
            list: Recommended next moves
        """
        # Calculate the move number and player color
        move_number = (move_count // 2) + 1
        player_color = "white" if move_count % 2 == 0 else "black"
        
        # Check if there are recommended moves for this opening at this point
        variations = self.opening_variations.get(opening_name, {})
        moves_for_number = variations.get(move_number, {})
        recommended_moves = moves_for_number.get(player_color, [])
        
        return recommended_moves
    
    def _is_mainline(self, moves, opening_name):
        """
        Check if the moves follow the main line of the opening.
        
        Args:
            moves (list): List of moves in algebraic notation
            opening_name (str): Name of the opening
            
        Returns:
            bool: True if moves follow the main line, False otherwise
        """
        # This is a simplified implementation
        # In a real implementation, you would check against a database of main lines
        
        # For now, just check if the opening is recognized
        return opening_name != "Unknown Opening"
    
    def analyze_opening_play(self, moves):
        """
        Analyze how well the opening was played compared to theory.
        
        Args:
            moves (list): List of moves in algebraic notation
            
        Returns:
            dict: Analysis of opening play
        """
        # Recognize the opening
        opening_info = self.recognize_opening(moves)
        
        # Initialize analysis results
        analysis = {
            'opening': opening_info['name'],
            'accuracy': 100,  # Start with perfect accuracy
            'deviations': [],
            'improvement_suggestions': [],
            'theory_moves': 0
        }
        
        # Count how many moves follow theory
        theory_moves = 0
        
        # Check each move against theory
        for i, move in enumerate(moves):
            move_number = (i // 2) + 1
            player_color = "white" if i % 2 == 0 else "black"
            
            # Get recommended moves for this position
            variations = self.opening_variations.get(opening_info['name'], {})
            moves_for_number = variations.get(move_number, {})
            recommended_moves = moves_for_number.get(player_color, [])
            
            # Check if the move follows theory
            if recommended_moves and move not in recommended_moves:
                # This move deviates from theory
                analysis['accuracy'] -= 10  # Reduce accuracy score
                
                deviation = {
                    'move_number': move_number,
                    'player': player_color,
                    'played': move,
                    'recommended': recommended_moves,
                    'explanation': f"Instead of {move}, theory recommends {', '.join(recommended_moves)}"
                }
                
                analysis['deviations'].append(deviation)
                
                # Add improvement suggestion
                suggestion = f"Move {move_number}: Consider {', '.join(recommended_moves)} instead of {move}"
                analysis['improvement_suggestions'].append(suggestion)
            else:
                # Move follows theory or there's no specific recommendation
                theory_moves += 1
        
        # Update theory moves count
        analysis['theory_moves'] = theory_moves
        
        # Ensure accuracy is between 0 and 100
        analysis['accuracy'] = max(0, min(100, analysis['accuracy']))
        
        return analysis
    
    def get_opening_statistics(self, opening_name):
        """
        Get statistics about an opening.
        
        Args:
            opening_name (str): Name of the opening
            
        Returns:
            dict: Opening statistics
        """
        # This would fetch statistics from a database
        # For now, return placeholder statistics
        
        # Some example statistics
        statistics = {
            "Sicilian Defense": {
                'popularity': "Very High",
                'win_rate_white': 52.3,
                'win_rate_black': 47.7,
                'draw_rate': 30.5,
                'average_game_length': 38,
                'common_players': ["Kasparov", "Fischer", "Carlsen"]
            },
            "French Defense": {
                'popularity': "High",
                'win_rate_white': 54.1,
                'win_rate_black': 45.9,
                'draw_rate': 28.7,
                'average_game_length': 40,
                'common_players': ["Karpov", "Petrosian", "Botvinnik"]
            },
            "Ruy Lopez": {
                'popularity': "Very High",
                'win_rate_white': 55.8,
                'win_rate_black': 44.2,
                'draw_rate': 32.1,
                'average_game_length': 42,
                'common_players': ["Capablanca", "Fischer", "Anand"]
            }
        }
        
        return statistics.get(opening_name, {
            'popularity': "Unknown",
            'win_rate_white': 50.0,
            'win_rate_black': 50.0,
            'draw_rate': 30.0,
            'average_game_length': 40,
            'common_players': []
        })
