from gui import gui
from game_logic import *

name, type_class, player_stats = gui()

if type_class == "маг":
    player = Wizard(
        name=name,
        hp=50,
        defence=50,
        damage=5,
        luck=75,
        stats=[int(i) for i in str(player_stats)],
        max_weight=50,
        max_health=50,
    )
elif type_class == "воин":
    player = Warrior(
        name=name,
        hp=100,
        defence=100,
        damage=10,
        luck=50,
        stats=[int(i) for i in str(player_stats)],
        max_weight=100,
        max_health=100,
    )
elif type_class == "лучник":
    player = Archer(
        name=name,
        hp=75,
        defence=60,
        damage=7,
        luck=60,
        stats=[int(i) for i in str(player_stats)],
        max_weight=70,
        max_health=75,
    )
Dragon = Mob(
    name="Дракон",
    hp=500,
    defence=100,
    damage=20,
    luck=20,
    max_weight=1000,
    max_health=1000,
)

game_world = World(
    player=player,
    combat_mobs=[Dragon],
    exploration_mobs=[Dragon],
    trade_mobs=[],
    exploration_items=[
        HealthBottle(
            name="Зелье здоровья",
            weight=5,
            description="Обычная бутылка зелья",
            owner=None,
            hp=25,
        ),
        Armor(
            name="Защитные доспехи",
            weight=50,
            description="Доспехи рыцаря 17-го века",
            owner=None,
            defence=50,
        ),
        Weapon(
            name="Волшебный меч",
            weight=20,
            description="Сияет как солнце",
            owner=None,
            damage=100,
        ),
    ],
    events=[],
)

explore_session = game_world.generate_situation(Exploration)
action = explore_session.process_input()
while True:
    if action == 0:
        print("Вы проиграли!")
    else:
        print("Вы победили!")
        action = action.process_input()
