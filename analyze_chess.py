#!/usr/bin/env python3
"""
Takes a saved PGN or move JSON file and runs full analysis with IQ estimation and mistake breakdown.
"""

import sys
import os
import json
import argparse
import time
from pathlib import Path

from chess_engine.board import Board
from chess_engine.move import Move
from analysis.analyzer import Analyzer
from analysis.evaluation import Evaluation
from analysis.mistake_detector import MistakeDetector
from iq.iq_model import IQModel
from utils.logger import setup_logger
from utils.config import load_config


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chess Game Analyzer')
    parser.add_argument('input_file', type=str, help='Path to PGN or JSON file to analyze')
    parser.add_argument('-o', '--output', type=str, help='Path to save analysis results (default: input_file_analysis.json)')
    parser.add_argument('-d', '--depth', type=int, default=15, help='Analysis depth (higher is more accurate but slower)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress console output')
    parser.add_argument('--no-iq', action='store_true', help='Skip IQ calculation')
    parser.add_argument('--critical-only', action='store_true', help='Only analyze critical positions')
    parser.add_argument('--format', choices=['json', 'text', 'html'], default='json', help='Output format')
    parser.add_argument('--compare', type=str, help='Compare analysis with another player or engine')
    return parser.parse_args()


def determine_file_type(file_path):
    """Determine if the input file is PGN or JSON."""
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.pgn':
        return 'pgn'
    elif ext.lower() == '.json':
        return 'json'
    else:
        # Try to detect by content
        try:
            with open(file_path, 'r') as f:
                content = f.read(100)  # Read first 100 chars
                if content.strip().startswith('['):
                    return 'pgn'
                elif content.strip().startswith('{'):
                    return 'json'
        except Exception:
            pass
        
        # Default to PGN if can't determine
        return 'pgn'


def load_game_from_file(file_path, file_type):
    """Load a chess game from a file."""
    analyzer = Analyzer()
    
    if file_type == 'pgn':
        return analyzer.load_game_from_pgn(file_path)
    else:  # JSON
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check if it's our format or a generic move list
            if 'moves' in data:
                moves = data['moves']
            else:
                moves = data  # Assume it's a direct list of moves
            
            # Create a new board and apply moves
            board = Board()
            for i, move_str in enumerate(moves):
                color = "white" if i % 2 == 0 else "black"
                move = Move.from_algebraic(move_str, board, color)
                if move:
                    board.make_move(move)
                else:
                    raise ValueError(f"Invalid move: {move_str} at position {i+1}")
            
            return board
        except Exception as e:
            raise ValueError(f"Failed to parse JSON file: {e}")


def analyze_game(board, args, logger):
    """Analyze the chess game and generate a report."""
    analyzer = Analyzer(depth=args.depth)
    iq_model = IQModel()
    
    logger.info("Starting analysis...")
    start_time = time.time()
    
    # Generate basic analysis
    if not args.quiet:
        print("Analyzing moves and calculating accuracy...")
    
    analysis_result = analyzer.generate_analysis_report(
        board, 
        critical_only=args.critical_only
    )
    
    # Calculate IQ if not disabled
    if not args.no_iq:
        if not args.quiet:
            print("Calculating Chess IQ scores...")
        
        white_iq = iq_model.calculate_iq(
            analysis_result["white_accuracy"],
            analysis_result["white_mistakes"]
        )
        
        black_iq = iq_model.calculate_iq(
            analysis_result["black_accuracy"],
            analysis_result["black_mistakes"]
        )
        
        analysis_result["white_iq"] = white_iq
        analysis_result["black_iq"] = black_iq
    
    # Add game metadata
    analysis_result["total_moves"] = len(board.move_history)
    analysis_result["analysis_depth"] = args.depth
    analysis_result["analysis_time"] = time.time() - start_time
    
    # Add comparison if requested
    if args.compare:
        if not args.quiet:
            print(f"Comparing with {args.compare}...")
        comparison = analyzer.compare_with_reference(board, args.compare)
        analysis_result["comparison"] = comparison
    
    logger.info(f"Analysis completed in {analysis_result['analysis_time']:.2f} seconds")
    return analysis_result


def save_analysis_results(analysis_result, output_path, format_type):
    """Save analysis results to a file."""
    if format_type == 'json':
        with open(output_path, 'w') as f:
            json.dump(analysis_result, f, indent=2)
    elif format_type == 'text':
        with open(output_path, 'w') as f:
            f.write("Chess Game Analysis Report\n")
            f.write("=========================\n\n")
            f.write(f"Total Moves: {analysis_result['total_moves']}\n")
            f.write(f"Analysis Depth: {analysis_result['analysis_depth']}\n\n")
            
            f.write("Accuracy:\n")
            f.write(f"  White: {analysis_result['white_accuracy']:.2f}%\n")
            f.write(f"  Black: {analysis_result['black_accuracy']:.2f}%\n\n")
            
            if 'white_iq' in analysis_result:
                f.write("Chess IQ:\n")
                f.write(f"  White: {analysis_result['white_iq']}\n")
                f.write(f"  Black: {analysis_result['black_iq']}\n\n")
            
            f.write("Mistake Breakdown:\n")
            f.write("  White:\n")
            for category, count in analysis_result['white_mistakes'].items():
                f.write(f"    {category.capitalize()}: {count}\n")
            
            f.write("  Black:\n")
            for category, count in analysis_result['black_mistakes'].items():
                f.write(f"    {category.capitalize()}: {count}\n\n")
            
            if 'critical_positions' in analysis_result and analysis_result['critical_positions']:
                f.write("Critical Positions:\n")
                for pos in analysis_result['critical_positions']:
                    f.write(f"  Move {pos['move_number']}: {pos['description']}\n")
    elif format_type == 'html':
        # Create a simple HTML report
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Chess Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .stats {{ display: flex; justify-content: space-between; }}
        .stats-box {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; width: 45%; }}
        .mistakes {{ margin-top: 20px; }}
        .critical {{ margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .good {{ color: green; }}
        .inaccuracy {{ color: #cc7a00; }}
        .mistake {{ color: #cc0000; }}
        .blunder {{ color: #990000; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Chess Analysis Report</h1>
        <p>Total Moves: {analysis_result['total_moves']}</p>
        <p>Analysis Depth: {analysis_result['analysis_depth']}</p>
        
        <div class="stats">
            <div class="stats-box">
                <h2>White</h2>
                <p>Accuracy: {analysis_result['white_accuracy']:.2f}%</p>
                {f'<p>Chess IQ: {analysis_result["white_iq"]}</p>' if 'white_iq' in analysis_result else ''}
                <h3>Mistakes:</h3>
                <ul>
                    <li class="good">Good moves: {analysis_result['white_mistakes'].get('good', 0)}</li>
                    <li class="inaccuracy">Inaccuracies: {analysis_result['white_mistakes'].get('inaccuracy', 0)}</li>
                    <li class="mistake">Mistakes: {analysis_result['white_mistakes'].get('mistake', 0)}</li>
                    <li class="blunder">Blunders: {analysis_result['white_mistakes'].get('blunder', 0)}</li>
                </ul>
            </div>
            
            <div class="stats-box">
                <h2>Black</h2>
                <p>Accuracy: {analysis_result['black_accuracy']:.2f}%</p>
                {f'<p>Chess IQ: {analysis_result["black_iq"]}</p>' if 'black_iq' in analysis_result else ''}
                <h3>Mistakes:</h3>
                <ul>
                    <li class="good">Good moves: {analysis_result['black_mistakes'].get('good', 0)}</li>
                    <li class="inaccuracy">Inaccuracies: {analysis_result['black_mistakes'].get('inaccuracy', 0)}</li>
                    <li class="mistake">Mistakes: {analysis_result['black_mistakes'].get('mistake', 0)}</li>
                    <li class="blunder">Blunders: {analysis_result['black_mistakes'].get('blunder', 0)}</li>
                </ul>
            </div>
        </div>
        
        <div class="critical">
            <h2>Critical Positions</h2>
            <table>
                <tr>
                    <th>Move</th>
                    <th>Description</th>
                </tr>
                {''.join([f'<tr><td>{pos["move_number"]}</td><td>{pos["description"]}</td></tr>' for pos in analysis_result.get('critical_positions', [])])}
            </table>
        </div>
    </div>
</body>
</html>
"""
        with open(output_path, 'w') as f:
            f.write(html_content)


def print_analysis_summary(analysis_result):
    """Print a summary of the analysis to the console."""
    print("\n===== Chess Analysis Summary =====")
    print(f"Total Moves: {analysis_result['total_moves']}")
    
    print("\nAccuracy:")
    print(f"  White: {analysis_result['white_accuracy']:.2f}%")
    print(f"  Black: {analysis_result['black_accuracy']:.2f}%")
    
    if 'white_iq' in analysis_result:
        print("\nChess IQ:")
        print(f"  White: {analysis_result['white_iq']}")
        print(f"  Black: {analysis_result['black_iq']}")
    
    print("\nMistake Breakdown:")
    print("  White:")
    for category, count in analysis_result['white_mistakes'].items():
        print(f"    {category.capitalize()}: {count}")
    
    print("  Black:")
    for category, count in analysis_result['black_mistakes'].items():
        print(f"    {category.capitalize()}: {count}")
    
    if 'critical_positions' in analysis_result and analysis_result['critical_positions']:
        print("\nCritical Positions:")
        for pos in analysis_result['critical_positions'][:3]:  # Show only first 3
            print(f"  Move {pos['move_number']}: {pos['description']}")
        
        if len(analysis_result['critical_positions']) > 3:
            print(f"  ... and {len(analysis_result['critical_positions']) - 3} more")
    
    print(f"\nAnalysis completed in {analysis_result['analysis_time']:.2f} seconds")


def main():
    """Main function to analyze a chess game file."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    logger = setup_logger(quiet=args.quiet)
    
    try:
        # Determine file type
        file_type = determine_file_type(args.input_file)
        logger.info(f"Detected file type: {file_type}")
        
        # Load the game
        if not args.quiet:
            print(f"Loading game from {args.input_file}...")
        
        board = load_game_from_file(args.input_file, file_type)
        
        if not args.quiet:
            print(f"Loaded game with {len(board.move_history)} moves")
        
        # Analyze the game
        analysis_result = analyze_game(board, args, logger)
        
        # Determine output path
        if args.output:
            output_path = args.output
        else:
            base_name = os.path.splitext(args.input_file)[0]
            if args.format == 'json':
                output_path = f"{base_name}_analysis.json"
            elif args.format == 'text':
                output_path = f"{base_name}_analysis.txt"
            else:  # html
                output_path = f"{base_name}_analysis.html"
        
        # Save analysis results
        if not args.quiet:
            print(f"Saving analysis to {output_path}...")
        
        save_analysis_results(analysis_result, output_path, args.format)
        
        # Print summary to console
        if not args.quiet:
            print_analysis_summary(analysis_result)
            print(f"\nFull analysis saved to {output_path}")
        
        return 0
    
    except FileNotFoundError:
        logger.error(f"File not found: {args.input_file}")
        return 1
    except ValueError as e:
        logger.error(f"Error processing file: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
