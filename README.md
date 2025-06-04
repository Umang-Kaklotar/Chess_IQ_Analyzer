# Chess IQ Analyzer

A sophisticated chess application that combines gameplay with advanced performance analytics and IQ assessment.


## Overview

Chess IQ Analyzer is a comprehensive chess platform that not only allows you to play chess but also analyzes your gameplay, calculates a Chess IQ score based on your performance, and provides personalized improvement suggestions. The application tracks your progress over time, helping you become a better chess player through data-driven insights.

## Key Features

- **Complete Chess Game**: Full-featured chess implementation with all standard rules
  - Legal move validation and highlighting
  - Special moves (castling, en passant, promotion)
  - Game state tracking (check, checkmate, stalemate)
  - Time controls with configurable settings

- **AI Opponent**: Play against a computer opponent with adjustable difficulty levels (1-5)
  - Minimax algorithm with alpha-beta pruning
  - Different playing styles at various difficulty settings

- **Performance Analysis**:
  - Move accuracy scoring compared to optimal engine moves
  - Mistake categorization (blunders, mistakes, inaccuracies, good moves)
  - Critical position identification
  - Post-game analysis reports

- **Chess IQ Calculation**:
  - Proprietary algorithm to assess chess skill level
  - IQ score based on move quality, pattern recognition, and tactical awareness
  - Progressive tracking to show improvement over time

- **Statistics and Progress Tracking**:
  - Detailed performance metrics
  - Win/loss/draw statistics
  - Accuracy trends
  - Mistake distribution analysis
  - Visual charts and graphs

- **Improvement Recommendations**:
  - Personalized suggestions based on gameplay patterns
  - Identified weakness areas
  - Opening repertoire suggestions
  - Tactical and strategic advice

- **PGN Analysis Tool**:
  - Standalone analyzer for PGN chess game files
  - Multiple output formats (JSON, text, HTML)
  - Comparative analysis options

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Umang-Kaklotar/Chess_IQ_Analyzer.git
cd chess_iq_analyzer
```

### Step 2: Create and Activate a Virtual Environment (Recommended)

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

The project requires the following dependencies:
- pygame==2.5.2
- numpy==1.26.3
- matplotlib==3.8.2
- pytest==7.4.3

Install them using:

```bash
pip install -r requirements.txt
```

### Step 4: Install the Package in Development Mode

```bash
pip install -e .
```

## Usage

### Starting the Game

Launch the application with default settings:

```bash
python main.py
```

Or if installed as a package:

```bash
chess-iq
```

### Command Line Options

```
usage: main.py [-h] [--ai] [--difficulty {1,2,3,4,5}] [--time-control TIME_CONTROL] [--no-analysis] [--load-pgn LOAD_PGN]

Chess IQ Analyzer

optional arguments:
  -h, --help            show this help message and exit
  --ai                  Play against AI
  --difficulty {1,2,3,4,5}
                        AI difficulty level (1-5)
  --time-control TIME_CONTROL
                        Time control in minutes+increment format (e.g., 10+5)
  --no-analysis         Skip post-game analysis
  --load-pgn LOAD_PGN   Load game from PGN file
```

### Example Commands

Play against AI at difficulty level 3 with 5 minutes + 3 seconds increment:
```bash
python main.py --ai --difficulty 3 --time-control 5+3
```

Human vs. human game with 10 minutes per side:
```bash
python main.py --time-control 10+0
```

Analyze an existing PGN file:
```bash
python analyze_chess.py my_game.pgn --depth 20 --format html
```

## Gameplay Guide

### Basic Controls

- **Making Moves**: Click on a piece to select it, then click on a highlighted square to move
- **Game Controls**: Use the buttons in the interface to:
  - Start a new game
  - Resign the current game
  - View statistics
  - Access settings
  - View analysis

### Special Moves

- **Castling**: Select the king and click two squares towards the rook
- **En Passant**: Select your pawn and click on the diagonal square behind the opponent's pawn
- **Promotion**: When a pawn reaches the last rank, a dialog appears to choose the promotion piece

### Game End Conditions

- **Checkmate**: When a king is in check with no legal moves
- **Stalemate**: When a player has no legal moves but is not in check
- **Time Out**: When a player's clock reaches zero
- **Insufficient Material**: When neither player has enough pieces to checkmate
- **Threefold Repetition**: When the same position occurs three times
- **Fifty-Move Rule**: When no capture or pawn move has occurred in the last 50 moves
- **Resignation**: When a player voluntarily concedes the game

## Analysis Features

### Post-Game Analysis

After each game, Chess IQ Analyzer provides:

1. **Accuracy Score**: Percentage of moves matching or close to engine recommendations
2. **Mistake Breakdown**: Quantitative analysis of move quality
   - Blunders: Serious mistakes that significantly change the position evaluation
   - Mistakes: Errors that negatively impact position but are less severe
   - Inaccuracies: Suboptimal moves that slightly worsen the position
   - Good Moves: Moves that maintain or improve the position
3. **Critical Positions**: Key moments where the game outcome could have changed
4. **Chess IQ Score**: Assessment of chess skill based on performance metrics

### Chess IQ Calculation

The Chess IQ score is calculated using:

- Move accuracy compared to engine analysis
- Pattern recognition in similar positions
- Tactical awareness and calculation ability
- Strategic understanding of positions
- Time management efficiency
- Performance consistency

### Standalone Analysis Tool

The `analyze_chess.py` script provides detailed analysis of PGN files:

```
usage: analyze_chess.py [-h] [-o OUTPUT] [-d DEPTH] [-q] [--no-iq] [--critical-only] [--format {json,text,html}] [--compare COMPARE] input_file

Chess Game Analyzer

positional arguments:
  input_file            Path to PGN or JSON file to analyze

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to save analysis results (default: input_file_analysis.json)
  -d DEPTH, --depth DEPTH
                        Analysis depth (higher is more accurate but slower)
  -q, --quiet           Suppress console output
  --no-iq               Skip IQ calculation
  --critical-only       Only analyze critical positions
  --format {json,text,html}
                        Output format
  --compare COMPARE     Compare analysis with another player or engine
```

## Progress Tracking

### Statistics Dashboard

Access comprehensive statistics through the Stats view:

- **Chess IQ Progression**: Chart showing IQ changes over time
- **Accuracy Trends**: Visualization of move accuracy improvement
- **Win Rate Analysis**: Breakdown of game outcomes
- **Mistake Distribution**: Analysis of error types and frequencies
- **Time Usage**: Analysis of time management during games

### Improvement Suggestions

Based on your gameplay patterns, the system provides:

1. **Pattern Recognition**: Common mistakes you make
2. **Tactical Weaknesses**: Types of tactics you frequently miss
3. **Opening Repertoire**: Suggestions for openings that suit your style
4. **Endgame Skills**: Specific endgame techniques to study
5. **Time Management**: Advice on better clock usage

## Data Management

### Player Statistics

The application stores player statistics in JSON format in the `data` directory:

- **player_stats.json**: Contains IQ history, game statistics, and performance metrics
- **game_history.json**: Stores the history of played games
- **moves_input.json**: Records move data for analysis

### Resetting Statistics

To reset all statistics and start fresh:

```bash
# Manual method - empty the data files
echo "[]" > data/game_history.json
echo "[]" > data/moves_input.json

# Reset player stats to default values
cat > data/player_stats.json << EOF
{
  "games_played": 0,
  "wins": 0,
  "losses": 0,
  "draws": 0,
  "average_iq": 100,
  "average_accuracy": 0,
  "history": [],
  "games": {
    "total": 0,
    "wins": 0,
    "losses": 0,
    "draws": 0
  },
  "iq": {
    "current": 100,
    "history": []
  },
  "accuracy": {
    "average": 0,
    "history": []
  },
  "mistakes": {
    "blunders": 0,
    "mistakes": 0,
    "inaccuracies": 0,
    "good_moves": 0
  },
  "improvement_areas": []
}
EOF
```

## Project Structure

```
CHESS_IQ_ANALYZER/
├── assets/                      # Visual and audio assets
│   ├── pieces/                  # Chess piece images
│   └── screenshots/             # Documentation screenshots
│
├── data/                        # Game data storage
│   ├── moves_input.json         # Move data for analysis
│   ├── game_history.json        # History of played games
│   ├── player_stats.json        # IQ and performance statistics
│   └── config.json              # Application configuration
│
├── chess_engine/                # Core chess logic
│   ├── board.py                 # Board representation and state
│   ├── pieces.py                # Chess piece definitions
│   ├── move.py                  # Move generation and validation
│   ├── rules.py                 # Chess rules implementation
│   └── ai_minimax.py            # AI opponent implementation
│
├── analysis/                    # Game analysis components
│   ├── analyzer.py              # Main analysis engine
│   ├── evaluation.py            # Position evaluation
│   ├── mistake_detector.py      # Error identification
│   └── openings.py              # Opening recognition
│
├── iq/                          # IQ calculation system
│   ├── iq_model.py              # IQ scoring algorithm
│   └── progress_tracker.py      # Performance tracking
│
├── ui/                          # User interface
│   ├── game_ui.py               # Main game interface
│   ├── board_view.py            # Chess board visualization
│   ├── components.py            # UI components
│   └── stats_view.py            # Statistics display
│
├── utils/                       # Utility functions
│   ├── logger.py                # Logging system
│   ├── config.py                # Configuration management
│   └── file_handler.py          # File operations
│
├── logs/                        # Application logs
│
├── tests/                       # Unit tests
│   ├── test_board.py
│   ├── test_moves.py
│   ├── test_analysis.py
│   └── test_iq.py
│
├── main.py                      # Main entry point
├── analyze_chess.py             # Standalone analysis tool
├── requirements.txt             # Project dependencies
├── setup.py                     # Package installation
└── README.md                    # Project documentation
```

## Troubleshooting

### Common Issues

1. **Game won't start**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check if pygame is properly installed: `pip install pygame`
   - Verify Python version is 3.8 or higher: `python --version`

2. **Analysis is slow**:
   - Reduce analysis depth with the `--depth` parameter
   - Use `--critical-only` to analyze only important positions
   - Close other resource-intensive applications

3. **UI display issues**:
   - Update your graphics drivers
   - Try running with a different screen resolution
   - Check for pygame compatibility with your system

4. **Sound not working**:
   - Ensure sound files are present in the assets directory
   - Check system sound settings
   - Verify pygame mixer is properly initialized

5. **Indentation errors in code**:
   - Check for proper indentation in Python files, especially in chess_engine/board.py
   - Use a code editor that shows whitespace characters
   - Run `python -m pytest` to identify syntax issues


## Acknowledgments
- Inspired by chess analysis tools like [Lichess](https://lichess.org) and [Chess.com](https://www.chess.com)
