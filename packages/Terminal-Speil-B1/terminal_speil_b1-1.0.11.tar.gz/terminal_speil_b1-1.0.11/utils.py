import datetime
import random
import sys
import json
import os
from game_data import *


def get_valid_input(prompt, valid_options, case_sensitive=False):
    """Get valid input from user with error handling"""
    while True:
        choice = input(prompt).strip()
        if not case_sensitive:
            choice = choice.lower()
        if choice in valid_options:
            return choice
        print(f"Please choose from: {', '.join(valid_options)}")

def confirm_purchase(item, price):
    """Confirm purchase with user"""
    if price > 0:
        return get_valid_input(f"Buy {item.title()} for {price} gold? (y/n): ", ['y', 'n']) == 'y'
    else:
        return get_valid_input(f"Take {item.title()} and gain {abs(price)} gold? (y/n): ", ['y', 'n']) == 'y'

def show_atmosphere(time_of_day, weather):
    """Display atmospheric description"""
    if time_of_day == "morning":
        print(" The morning sun casts long shadows across the cobblestones. Birds chirp in the distance.")
    elif time_of_day == "afternoon":
        print(" The afternoon sun beats down warmly. The village bustles with activity.")
    elif time_of_day == "evening":
        print(" The evening air carries the scent of cooking fires. Lanterns begin to flicker on.")
    elif time_of_day == "night":
        print(" The night is quiet except for distant tavern laughter. Stars twinkle overhead.")
    # Weather description
    weather_descriptions = {
        "clear": "The sky is clear and bright.",
        "cloudy": "Gray clouds gather overhead, casting shadows.",
        "rainy": "Light rain patters on the rooftops and cobblestones.",
        "foggy": "A thick fog rolls through the streets, muffling sounds."
    }
    print(weather_descriptions[weather])


def show_main_menu(gold, cart_size, days_passed, german_arrival_day, quests_completed):
    """Display main menu with clear formatting"""
    days_left = german_arrival_day - days_passed
    
    print(f"\n{'='*20} MAIN MENU {'='*20}")
    print(f" Gold: {gold}")
    print(f" Items: {cart_size}")
    print(f" Day: {days_passed + 1}")
    print(f" German Arrival: {days_left} days")
    print(f" Quests Completed: {quests_completed}")
    print("-" * 48)
    print("i.   Check Inventory")
    print("s.   Visit Shops")
    print("b.   Battle Germanic Tribes")
    if days_passed >= 3:
        print("r.   Raid German Camp")
    print("save.  Save Game")
    print("q.   Quit Game")
    print("="*48)

def show_inventory(gold, cart, completed_quests):
    """Display detailed inventory"""
    print(f"\n{'='*20} INVENTORY {'='*20}")
    print(f" Gold: {gold}")
    print("-" * 44)
    
    if not cart:
        print(" No items in inventory")
    else:
        print(" Current Items:")
        for i, item in enumerate(cart, 1):
            description = ITEM_DESCRIPTIONS.get(item, "A mysterious item")
            print(f"  {i}. {item.title()}")
            print(f"     └─ {description}")
    
    print("-" * 44)
    print(f" Completed Quests: {len(completed_quests)}")
    if completed_quests:
        print("Recent completions:")
        for quest in completed_quests[-3:]:  # Show last 3
            print(f"  • {quest.title()}")
    
    print("="*44)
    input("Press Enter to continue...")

def advance_time(current_time):
    """Advance time of day"""
    time_sequence = ["morning", "afternoon", "evening", "night"]
    current_index = time_sequence.index(current_time)
    return time_sequence[(current_index + 1) % 4]

def save_game(player_name, gold, cart, completed_quests, days_passed, time_of_day, weather, german_arrival_day):
    """Save game state to file"""
    save_data = {
        'player_name': player_name,
        'gold': gold,
        'cart': cart,
        'completed_quests': completed_quests,
        'days_passed': days_passed,
        'time_of_day': time_of_day,
        'weather': weather,
        'german_arrival_day': german_arrival_day,
        'timestamp': str(datetime.datetime.now())
    }
    
    try:
        with open('savegame.json', 'w') as f:
            json.dump(save_data, f, indent=2)
        print("  Game saved successfully!")
    except Exception as e:
        print(f"  Error saving game: {e}")

def load_game():
    """Load game state from file"""
    try:
        with open('savegame.json', 'r') as f:
            save_data = json.load(f)
        print("  Game loaded successfully!")
        return save_data
    except Exception as e:
        print(f"  Error loading game: {e}")
        return None

def handle_death_alternatives(cart, player_name):
    """Handle death with healing alternatives"""
    print(f"\n  Sir {player_name} has fallen in battle!")
    print("But wait...")
    
    # Check for healing potion
    if 'healing potion' in cart:
        choice = get_valid_input("Use healing potion to revive? (y/n): ", ['y', 'n'])
        if choice == 'y':
            cart.remove('healing potion')
            print("  The healing potion restores you to life!")
            print("You barely escaped death... but you live to fight another day.")
            return True
    
    # Check for mage
    if 'mage' in cart:
        choice = get_valid_input("Have your mage cast revival magic? (y/n): ", ['y', 'n'])
        if choice == 'y':
            print(" Your mage weaves powerful magic, pulling your soul back from the brink!")
            print("'Death is but a doorway, and I hold the key!' declares your mage.")
            return True
    
    # Check for grim reaper
    if 'grim reaper' in cart:
        choice = get_valid_input("Ask the Grim Reaper to spare you? (y/n): ", ['y', 'n'])
        if choice == 'y':
            print("  The Grim Reaper looks upon you with hollow eyes...")
            print("'You amuse me, mortal. I shall grant you... one more chance.'")
            print("Death himself has given you another chance!")
            return True
    
    # No alternatives available
    print("  With no way to cheat death, your adventure ends here...")
    print("DEATH ENDING: Your heroic attempt will be remembered in village songs.")
    return False

def handle_german_raid(cart, player_name):
    """Handle raiding the German camp"""
    print(f"\n{'='*20} GERMAN CAMP RAID {'='*20}")
    print("You sneak through the forest toward the German encampment...")
    print("Firelight flickers between the trees ahead.")
    
    approach = get_valid_input(
        "How do you approach? (stealth/direct/distraction): ", 
        ['stealth', 'direct', 'distraction']
    )
    
    success_chance = 0.6  # Base 60% success
    
    # Modify chances based on items
    if 'black knight' in cart:
        success_chance += 0.2
        print("The Black Knight's armor gleams in the moonlight, inspiring confidence!")
    if 'mage' in cart:
        success_chance += 0.15
        print("Your mage weaves concealment spells around your party!")
    if 'grim reaper' in cart:
        success_chance += 0.25
        print("Death itself walks beside you - the Germans sense supernatural dread!")
    
    # Approach modifiers
    if approach == 'stealth':
        success_chance += 0.1
        print("You move like shadows through the forest...")
    elif approach == 'direct':
        success_chance -= 0.1
        print("You charge boldly toward their camp!")
    else:  # distraction
        print("You create noise on the far side of camp to draw guards away...")
    
    if random.random() < success_chance:
        print(" SUCCESS! You successfully raid the German supply wagons!")
        print("You steal their siege weapons and scatter their horses!")
        print("The confused Germans will need time to regroup.")
        return 'victory'
    else:
        print("The raid goes wrong! German sentries spot you!")
        print("You're overwhelmed by enemy warriors!")
        return 'death'

def handle_final_battle(cart, player_name, completed_quests, days_passed):
    """Handle the final battle sequence"""
    print(f"\n{'='*15} FINAL BATTLE {'='*15}")
    print("The Germanic warband storms toward the village gates!")
    print("This is your moment of truth, Sir {player_name}!")
    
    # Determine ending based on preparation
    battle_power = calculate_battle_power(cart, completed_quests, days_passed)
    
    if battle_power >= 10:
        return epic_victory_ending(cart, player_name, battle_power)
    elif battle_power >= 7:
        return heroic_victory_ending(cart, player_name, battle_power)
    elif battle_power >= 4:
        return close_victory_ending(cart, player_name, battle_power)
    else:
        return tragic_ending(cart, player_name, battle_power)

def calculate_battle_power(cart, completed_quests, days_passed):
    """Calculate total battle effectiveness"""
    power = 0
    
    # Ally power
    ally_power = {
        'brian': 2, 'black knight': 3, 'grim reaper': 5, 'god': 6,
        'mage': 4, 'nordic': 3, 'biccus diccus': 4, 'raddragonore': 5
    }
    
    for ally in ally_power:
        if ally in cart:
            power += ally_power[ally]
    
    # Equipment power
    equipment_power = {
        'spear': 1, 'axe': 2, 'scythe': 3, 'catapult': 2,
        'body armor': 2, 'dragon': 4, 'wolf': 1
    }
    
    for equipment in equipment_power:
        if equipment in cart:
            power += equipment_power[equipment]
    
    # Quest bonus (preparation matters)
    power += len(completed_quests) // 3
    
    # Time bonus/penalty
    if days_passed < 5:
        power += 1  # Well prepared
    elif days_passed > 8:
        power -= 1  # Rushed
    
    return power

# Battle ending functions
def epic_victory_ending(cart, player_name, power):
    print(f"\n EPIC VICTORY! (Power: {power})")
    
    if 'god' in cart:
        print("GOD himself fights beside you!")
        print("Divine light blinds the German forces as heavenly power flows through you!")
    elif 'grim reaper' in cart:
        print("Death incarnate reaps the souls of your enemies!")
        print("The German warriors flee in supernatural terror!")
    elif 'raddragonore' in cart:
        print("Mythical dragons soar overhead, raining fire upon the invaders!")
    
    print(f"\nSir {player_name}, your legendary victory echoes across all kingdoms!")
    print("Tiffany rushes to your arms as the village celebrates your triumph!")
    print("You are crowned as the new Lord Protector of the realm!")
    print("\n LEGENDARY ENDING: Your name will be sung for generations! ✨")
    return True

def heroic_victory_ending(cart, player_name, power):
    print(f"\n HEROIC VICTORY! (Power: {power})")
    print("Your well-prepared forces clash with the Germans in epic battle!")
    print("Though the fight is fierce, your superior strategy wins the day!")
    print(f"\nSir {player_name}, you have saved the village and won Tiffany's heart!")
    print("The grateful villagers build a statue in your honor!")
    print("\n HEROIC ENDING: You are remembered as the village's greatest champion!")
    return True

def close_victory_ending(cart, player_name, power):
    print(f"\n NARROW VICTORY! (Power: {power})")
    print("The battle is desperate and bloody, with victory hanging by a thread!")
    print("Just when all seems lost, your determination turns the tide!")
    print(f"\nSir {player_name}, you barely saved the village, but at great cost...")
    print("Tiffany tends your wounds as the village slowly rebuilds.")
    print("\n SURVIVOR ENDING: You proved that courage conquers all!")
    return True

def tragic_ending(cart, player_name, power):
    print(f"\n  TRAGIC DEFEAT... (Power: {power})")
    print("Despite your brave efforts, you were simply not prepared enough...")
    print("The Germans overwhelm your meager forces!")
    
    # Check for death alternatives one last time
    death_handled = handle_death_alternatives(cart, player_name)
    if not death_handled:
        print(f"\nSir {player_name}'s valiant sacrifice will always be remembered...")
        print("Though the village falls, your courage inspired others to eventually fight back.")
        print("\n MARTYR ENDING: Your noble death sparked a rebellion that would free the land.")
    return True

def clear_terminal():
    """Clears the terminal screen."""
    if os.name == 'nt':  # Check if the operating system is Windows
        os.system('cls')
    else:  # Assume Unix-like system
        os.system('clear')

def handle_shop_selection(gold, cart, completed_quests, player_name):
    """Handle shop selection and purchases"""
    result = {
        'gold': gold,
        'cart': cart.copy(),
        'completed_quests': completed_quests.copy(),
        'game_ended': False
    }
    
    # Make copies of shop inventories so we can modify them
    shops = {
        'freelancers': FREELANCERS.copy(),
        'antiques': ANTIQUES.copy(),
        'pet_shop': PET_SHOP.copy(),
        'grocery': GROCERY.copy(),
        'botanical_nursery': BOTANICAL_NURSERY.copy(),
        'farmers_market': FARMERS_MARKET.copy()
    }
    
    shop_loop = True
    while shop_loop and not result['game_ended']:
        print(f"\n=== VILLAGE SHOPS ===")
        print("1. Freelancers")
        print("2. Antiques")
        print("3. Pet Shop")
        print("4. Grocery")
        print("5. Botanical Nursery")
        print("6. Farmers Market")
        print("7. Quest Board")
        print("back. Return to Main Menu")
        
        shop_choice = get_valid_input("Which shop? (1-7 or 'back'): ", ['1', '2', '3', '4', '5', '6', '7', 'back'])
        
        if shop_choice == 'back':
            shop_loop = False
            continue
            
        elif shop_choice == '1':
            # FREELANCERS SHOP
            freelancer_result = handle_freelancers_guild(result['gold'], result['cart'], shops['freelancers'], player_name)
            result.update(freelancer_result)
            if result['game_ended']:
                break
                
        elif shop_choice == '2':
            # ANTIQUE SHOP
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['antiques'], 
                "ANTIQUE SHOP", 
                "Dust motes dance in the filtered sunlight. Ancient treasures gleam mysteriously."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '3':
            # PET SHOP
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['pet_shop'],
                "PET SHOP",
                "The air fills with chirping, squeaking, and the rustle of small creatures."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '4':
            # GROCERY STORE
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['grocery'],
                "GROCERY",
                "The aroma of fresh bread and pungent cheese and aged wine fills your nostrils."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '5':
            # BOTANICAL NURSERY
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['botanical_nursery'],
                "BOTANICAL NURSERY",
                "Sweet floral scents and rich earth surround you."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '6':
            # FARMERS MARKET
            shop_result = handle_generic_shop(
                result['gold'], result['cart'], shops['farmers_market'],
                "FARMERS MARKET", 
                "Fresh produce is arranged in colorful displays."
            )
            result['gold'] = shop_result['gold']
            result['cart'] = shop_result['cart']
            
        elif shop_choice == '7':
            # QUEST BOARD
            quest_result = handle_quest_board(result['gold'], result['completed_quests'])
            result['gold'] = quest_result['gold']
            result['completed_quests'] = quest_result['completed_quests']
    
    return result

def handle_freelancers_guild(gold, cart, freelancers_shop, player_name):
    """Handle the freelancers guild with special battle mechanics"""
    result = {
        'gold': gold,
        'cart': cart.copy(),
        'game_ended': False
    }
    
    print("\n--- Entering Freelancers ---")
    print("\n=== FREELANCERS GUILD ===")
    print("The guild hall echoes with the sounds of sharpening weapons and hushed conversations.")
    
    if not freelancers_shop:
        print("The guild is empty! All freelancers are out on missions.")
        input("Press Enter to continue...")
        return result
    
    print("\nAvailable Freelancers:")
    for name, price in freelancers_shop.items():
        if price == 'dedication and hope':
            print(f"- {name.title()}: Requires dedication and hope")
        else:
            print(f"- {name.title()}: {price} gold")
    
    freelancer_options = list(freelancers_shop.keys()) + ['exit']
    freelancer_choice = get_valid_input("Select a freelancer or 'exit': ", freelancer_options)
    
    if freelancer_choice == 'exit':
        return result
    
    # Process freelancer choice
    price = freelancers_shop[freelancer_choice]
    
    # Handle special cases
    if freelancer_choice == 'minstrel':
        print(f"You hired the minstrel... but he killed and looted you!")
        print("YOU DIED! Thanks for playing.")
        result['game_ended'] = True
        return result
        
    elif freelancer_choice == 'ze germane':
        print(f"You hired ze germane... but he betrayed you immediately!")
        print("YOU DIED! Thanks for playing.")
        result['game_ended'] = True
        return result
        
    elif freelancer_choice == 'god':
        dedication_choice = get_valid_input("Do you have true dedication and hope in your heart? (yes/no): ", ['yes', 'no'])
        if dedication_choice == 'no':
            print("God sees through your lack of faith...")
            input("Press Enter to continue...")
            return result
        else:
            print("God recognizes your pure heart!")
            result['cart'].append(freelancer_choice)
            freelancers_shop.pop(freelancer_choice)
    
    else:
        # Normal purchase
        if isinstance(price, int) and result['gold'] >= price:
            confirm = get_valid_input(f"Hire {freelancer_choice.title()} for {price} gold? (y/n): ", ['y', 'n'])
            if confirm == 'y':
                result['gold'] -= price
                result['cart'].append(freelancer_choice)
                freelancers_shop.pop(freelancer_choice)
                print(f"You hired {freelancer_choice.title()}!")
        else:
            print("Not enough gold!")
            input("Press Enter to continue...")
            return result
    
    # Offer immediate battle option for hired freelancers
    if freelancer_choice in result['cart'] and freelancer_choice not in ['minstrel', 'ze germane']:
        battle_choice = get_valid_input("Ready for battle with your new ally? (yes/no/inventory): ", ['yes', 'no', 'inventory'])
        
        if battle_choice == 'inventory':
            show_inventory(result['gold'], result['cart'], [])
        elif battle_choice == 'yes':
            result['game_ended'] = handle_freelancer_battle(freelancer_choice, player_name)
    
    input("Press Enter to continue...")
    return result

def handle_freelancer_battle(freelancer_name, player_name):
    """Handle immediate battle with hired freelancer"""
    print(f"\n=== BATTLE BEGINS ===")
    
    if freelancer_name == 'brian':
        print("You used Brian as a meatshield... using the element of surprise!")
        print("You defeated ze germanz! You're now the village king!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'black knight':
        print("The Black Knight dies heroically in battle, winning it!")
        print("You revive him with your healing potion.")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'grim reaper':
        print("The Grim Reaper uses 'GRIM EYES' ability...")
        print("""
         ___       ___
        (_o_)     (_o_)
      . |     /\\      |.
     (   )   /  \\     (  )
      \\  /           /  /
       \\............../
        \\_____________/
        """)
        print("REAPING...............")
        print("You defeated ze germanz and became village king!")
        print("With literal death by your side you are crowned!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'god':
        print("GOD APPRECIATES JUSTICE!")
        print("GOD used 'BRIGHT EYE' ability!")
        print("""
        _,.--~=~"~=~--.._  
    _.-"  / \\ !   ! / \\  "-._  
  ,"     / ,`  .---. `, \\    ". 
/.'   `~  |   /:::::\\   |  ~`   '.
\\`.  `~   |  \\:::::/   | ~`  ~ .'
    `.  `~  \\ ``~~~' ,` /   ~`.' 
      "-._   \\ / !   ! \\ /_.-"  
          "=~~.._  _..~~=`"        
        """)
        print("You received the blessing of god!")
        print("You, the son of god have started Terminality with your followers!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'mage':
        print("Your mage fights variantly,")
        print("MAGE USES STAFF OF UROPE,")
        print("""
          ____
         /----\\.    
            ((O)[=====\\--\\=====l
         \\----/.
          |----|
        """)
        print("You defeated ze germanz!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    elif freelancer_name == 'raddragonore':
        print("Bro, ya dat cool? damnn!")
        print("DRAGONORE SUMMONS HIS MYTHICAL CREATURES,")
        print("""
 
<>=======()          /|\\\\()==========<>_
    \\_/ | \\\\        //|\\   ______/ \\)
    \\_|  \\\\      // | \\_/
            \\|\\/|\\_   //  /\\/
            (.\\/.\)\\ \\_//  /
            //_/\\_\\/ /  |
            @@//-|=\\  \\  |
                \\_=\\_  \\ |
                \\==\\ \\|\\_ 
                __(\\===\\(  )\\l
            (((~) __(_/   |
                (((~) \\  /
                ______/ /
                '------'
        """)
        print("Yo enemies are ash bro,")
        print("You defeated ze germanz!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True
        
    else:
        print(f"{freelancer_name.title()} fights valiantly!")
        print("You defeated ze germanz!")
        print(f"Sir {player_name}, YOU WON! Thanks for playing!")
        return True

def handle_generic_shop(gold, cart, shop_inventory, shop_name, shop_description):
    """Handle generic shop purchases"""
    result = {
        'gold': gold,
        'cart': cart.copy()
    }
    
    print(f"\n--- Entering {shop_name} ---")
    print(f"\n=== {shop_name} ===")
    print(shop_description)
    
    if not shop_inventory:
        print("The shop is empty! Come back later.")
        input("Press Enter to continue...")
        return result
    
    print(f"\nAvailable items:")
    for item, price in shop_inventory.items():
        print(f"- {item.title()}: {price} gold")
    
    shop_options = list(shop_inventory.keys()) + ['exit']
    choice = get_valid_input("Select an item or 'exit': ", shop_options)
    
    if choice == 'exit':
        return result
    
    if choice in shop_inventory:
        price = shop_inventory[choice]
        
        if price > 0 and result['gold'] >= price:
            confirm = get_valid_input(f"Buy {choice} for {price} gold? (y/n): ", ['y', 'n'])
            if confirm == 'y':
                result['gold'] -= price
                result['cart'].append(choice)
                shop_inventory.pop(choice)
                print(f"You bought {choice} for {price} gold!")
                
                # Special messages
                if choice == 'magic beans':
                    print("These beans tingle with magical energy... they might grow into something amazing!")
                elif choice == 'newt':
                    print("The newt looks at you knowingly... something special about this one!")
                    
        elif price < 0:
            result['gold'] += abs(price)
            result['cart'].append(choice)
            shop_inventory.pop(choice)
            print(f"You took {choice} and gained {abs(price)} gold!")
        else:
            print("Not enough gold!")
    
    input("Press Enter to continue...")
    return result

def handle_quest_board(gold, completed_quests):
    """Handle quest board activities"""
    result = {
        'gold': gold,
        'completed_quests': completed_quests.copy()
    }
    
    print("\n--- Entering Quest Board ---")
    print("\n=== VILLAGE QUEST & BOUNTY BOARD ===")
    print("The wooden board creaks in the wind, covered with parchment notices.")
    
    print("\nAvailable Village Quests:")
    quest_choices = {}
    i = 1
    for quest, details in VILLAGE_QUESTS.items():
        if quest not in result['completed_quests']:
            quest_choices[str(i)] = quest
            print(f"{i}. {quest.title()} - {details['description']} [Reward: {details['reward']} gold]")
            i += 1

    print("\nBlacksmith Jobs:")
    for j, (job, details) in enumerate(BLACKSMITH_JOBS.items(), 1):
        if job not in result['completed_quests']:
            quest_choices[f"b{j}"] = job
            print(f"b{j}. {job.title()} - {details['description']} [Reward: {details['reward']} gold]")

    print("\nTavern Activities:")
    for k, (activity, details) in enumerate(TAVERN_ACTIVITIES.items(), 1):
        if activity not in result['completed_quests']:
            quest_choices[f"t{k}"] = activity
            print(f"t{k}. {activity.title()} - {details['description']} [Reward: {details['reward']} gold]")

    valid_choices = list(quest_choices.keys()) + ['r', 'back']
    quest_choice = get_valid_input("Choose a quest, 'r' for random adventure, or 'back': ", valid_choices)

    if quest_choice == 'back':
        pass
    elif quest_choice == 'r':
        # Random event
        event = random.choice(RANDOM_EVENTS)
        print(f"\n=== RANDOM ADVENTURE ===")
        print(f"{event['event']}")
        result['gold'] += event['gold']
        print(f"You gained {event['gold']} gold!")
    else:
        # Handle quest completion
        quest_name = quest_choices[quest_choice]
        
        # Determine quest type and reward
        if quest_name in VILLAGE_QUESTS:
            reward = VILLAGE_QUESTS[quest_name]['reward']
        elif quest_name in BLACKSMITH_JOBS:
            reward = BLACKSMITH_JOBS[quest_name]['reward']
        else:
            reward = TAVERN_ACTIVITIES[quest_name]['reward']
        
        print(f"\n=== {quest_name.upper()} ===")
        
        # Quest-specific adventures
        if quest_name == 'hunt wild boar':
            approach = get_valid_input("How do you approach the boar? (stealth/direct/trap): ", ['stealth', 'direct', 'trap'])
            if approach == 'stealth':
                print("You sneak up and take the boar by surprise! Clean kill!")
                reward += 25
            elif approach == 'direct':
                print("You charge head-on! Dangerous but heroic!")
            else:
                print("You set a clever trap! The boar walks right into it!")
                reward += 15
        
        elif quest_name == 'explore haunted ruins':
            approach = get_valid_input("How do you explore the ruins? (careful/bold/mystical): ", ['careful', 'bold', 'mystical'])
            if approach == 'careful':
                print("You carefully avoid the traps and find extra treasure!")
                reward += 50
            elif approach == 'bold':
                print("You boldly march through and face the dangers head-on!")
            else:
                print("You use mystical knowledge to commune with the spirits!")
                reward += 30
        
        # Complete the quest
        print(f"Quest completed! You earned {reward} gold!")
        result['gold'] += reward
        result['completed_quests'].append(quest_name)

    input("Press Enter to continue...")
    return result


