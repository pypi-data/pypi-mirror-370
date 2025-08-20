import numpy as np
import joblib
import os
from .utils import (
    allocate_resources,
    coin_flip,
    resource_bar,
    log_battle_data,
    calculate_strength,
    reinforce_units
)

# Dynamically resolve the paths to the model and scaler
model_path = os.path.join(os.path.dirname(__file__), 'models', 'optimized_battle_model.pkl')
scaler_path = os.path.join(os.path.dirname(__file__), 'models', 'scaler.pkl')

# Load the pre-trained battle model and scaler with error handling
try:
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("Model and scaler loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading model or scaler: {e}")
    raise

class Battle:
    def __init__(self, interactive=True):
        if interactive:
            self.user_role = coin_flip()
        else:
            self.user_role = 'attacker'  # Default role for non-interactive mode
        
        self.model_role = 'defender' if self.user_role == 'attacker' else 'attacker'
        self.user_resources = allocate_resources(self.user_role)
        self.model_resources = allocate_resources(self.model_role)
        self.day = 1

    def get_ai_deploy_ratio(self):
        """
        Runs the ML model to get the strategic deployment ratio for the 'model' player.
        """
        model_input = np.array([[self.user_resources['units'], self.user_resources['tanks'], 
                                 self.user_resources['drones'], self.user_resources['artillery'], 
                                 self.user_resources['air_support'],
                                 self.model_resources['units'], self.model_resources['tanks'], 
                                 self.model_resources['drones'], self.model_resources['artillery'], 
                                 self.model_resources['air_support']]])
        scaled_input = scaler.transform(model_input)
        model_decision = model.predict(scaled_input)[0]
        return 0.7 if model_decision == 0 else 0.4

    def get_model_deployment(self):
        """Gets the deployment for the 'model' player."""
        deploy_ratio = self.get_ai_deploy_ratio()
        return {k: int(v * deploy_ratio) for k, v in self.model_resources.items()}

    def get_user_ai_deployment(self):
        """Gets the deployment for the 'user' player in CVC mode."""
        deploy_ratio = self.get_ai_deploy_ratio()
        return {k: int(v * deploy_ratio) for k, v in self.user_resources.items()}

    def run_battle_day(self, user_deployed):
        model_deployed = self.get_model_deployment()
        
        for key in user_deployed:
            self.user_resources[key] -= user_deployed[key]
        for key in model_deployed:
            self.model_resources[key] -= model_deployed[key]

        user_strength = calculate_strength(user_deployed)
        model_strength = calculate_strength(model_deployed)

        if user_strength > model_strength:
            outcome = 'User Wins Day'
            damage = int((user_strength - model_strength) * 0.1)
            self.model_resources['units'] -= max(0, damage)
        elif model_strength > user_strength:
            outcome = 'Model Wins Day'
            damage = int((model_strength - user_strength) * 0.1)
            self.user_resources['units'] -= max(0, damage)
        else:
            outcome = 'Stalemate'

        log_battle_data(self.day, user_deployed, model_deployed, self.user_resources, self.model_resources, outcome)
        return outcome, user_deployed, model_deployed

    def advance_day(self):
        self.day += 1
        if self.day > 1:
            reinforce_units(self.user_resources)
            reinforce_units(self.model_resources)

    def is_game_over(self):
        return self.user_resources['units'] <= 0 or self.model_resources['units'] <= 0 or self.day > 10

    def get_winner(self):
        if self.user_resources['units'] <= 0:
            return "The model wins!"
        elif self.model_resources['units'] <= 0:
            return "You win!"
        else:
            return "The battle ends in a stalemate."

def start_cli_game():
    """Starts the command-line interface version of the game."""
    print("Welcome to the Battle Simulation!")
    battle = Battle()
    print(f"\nYou are the {battle.user_role}. Your resources: {battle.user_resources}")
    print(f"The model is the {battle.model_role}. Model's resources: {battle.model_resources}")

    while not battle.is_game_over():
        print(f"\n--- Day {battle.day} ---")
        print("\nYour resources to deploy:")
        print(resource_bar("Units", battle.user_resources['units'], 6000))
        # ... (rest of the CLI-specific code)
        try:
            user_deployed = {
                'units': min(int(input("How many units? ")), battle.user_resources['units']),
                'tanks': min(int(input("How many tanks? ")), battle.user_resources['tanks']),
                'drones': min(int(input("How many drones? ")), battle.user_resources['drones']),
                'artillery': min(int(input("How many artillery? ")), battle.user_resources['artillery']),
                'air_support': min(int(input("How many air support? ")), battle.user_resources['air_support'])
            }
        except ValueError:
            print("Invalid input! Please enter numbers only.")
            continue

        outcome, user_deployed_info, model_deployed_info = battle.run_battle_day(user_deployed)
        
        print(f"\nYou deployed: {user_deployed_info}")
        print(f"Model deployed: {model_deployed_info}")
        print(f"Outcome: {outcome}")

        print("\nRemaining Resources after today's battle:")
        print(resource_bar("Your Units", battle.user_resources['units'], 6000))
        print(resource_bar("Model's Units", battle.model_resources['units'], 6000))
        
        battle.advance_day()

    print(f"\n--- Game Over ---")
    print(battle.get_winner())

if __name__ == "__main__":
    start_cli_game()
