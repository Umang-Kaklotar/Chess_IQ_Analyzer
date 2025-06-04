from ui.game_ui import GameUI

# Create a GameUI instance
ui = GameUI()

# Check if display_board method exists
print("Has display_board:", hasattr(ui, "display_board"))

# List all methods
print("\nAll methods:")
methods = [method for method in dir(ui) if callable(getattr(ui, method)) and not method.startswith("__")]
for method in methods:
    print(f"- {method}")
