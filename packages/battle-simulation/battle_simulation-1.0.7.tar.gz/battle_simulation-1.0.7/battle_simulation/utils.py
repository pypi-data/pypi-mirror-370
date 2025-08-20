import random
import csv
import os

def allocate_resources(role):
    return {
        'units': random.randint(3000, 6000),
        'tanks': random.randint(30, 100),
        'drones': random.randint(20, 60),
        'artillery': random.randint(30, 80),
        'air_support': random.randint(50, 100),
        'terrain_advantage': random.uniform(0, 2) if role == 'defender' else 0
    }

def coin_flip():
    """Randomly assigns a role of 'attacker' or 'defender'."""
    return random.choice(['attacker', 'defender'])

def resource_bar(label, value, max_value, bar_length=50):
    """
    Creates a progress bar to visualize remaining resources.
    """
    filled_length = int(bar_length * value / max_value)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    return f"{label}: |{bar}| {value}/{max_value}"


def log_battle_data(day, user_deployed, model_deployed, user_resources, model_resources, outcome):
    data_dir = "new_training_data"
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, 'battle_results.csv')

    data = {
        'Day': day,
        'User_Units_Deployed': user_deployed['units'],
        'User_Tanks_Deployed': user_deployed['tanks'],
        'User_Drones_Deployed': user_deployed['drones'],
        'User_Artillery_Deployed': user_deployed['artillery'],
        'User_AirSupport_Deployed': user_deployed['air_support'],
        'Model_Units_Deployed': model_deployed['units'],
        'Model_Tanks_Deployed': model_deployed['tanks'],
        'Model_Drones_Deployed': model_deployed['drones'],
        'Model_Artillery_Deployed': model_deployed['artillery'],
        'Model_AirSupport_Deployed': model_deployed['air_support'],
        'User_Remaining_Units': user_resources['units'],
        'Model_Remaining_Units': model_resources['units'],
        'Outcome': outcome
    }

    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def calculate_strength(resources):
    base_strength = (
        resources['units'] +
        resources['tanks'] * 5 +
        resources['artillery'] * 4 +
        resources['drones'] * 7 +
        resources['air_support'] * 6
    )
    return base_strength * (1 + resources.get('terrain_advantage', 0))

def reinforce_units(military_unit):
    additional_units = int(calculate_strength(military_unit) * 0.05)
    military_unit['units'] += additional_units
    print(f"Reinforcements: +{additional_units} units (Total: {military_unit['units']})")
