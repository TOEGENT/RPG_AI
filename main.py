from gui import gui
from game_logic import *

# Получаем данные от GUI
name, type_class, player_stats = gui()

# Создаём игрока в зависимости от класса
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
        inventory=[],
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
        inventory=[],
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
        inventory=[],
    )
else:
    raise ValueError("Неизвестный класс персонажа")

# Создаём дракона
dragon = Mob(
    name="Дракон",
    hp=500,
    defence=100,
    damage=20,
    luck=20,
    max_weight=1000,
    max_health=1000,
)

# Предметы для мира
health_bottle = HealthBottle(
    name="Зелье здоровья",
    weight=5,
    description="Обычная бутылка зелья",
    owner=None,
    hp=25,
)
armor = Armor(
    name="Защитные доспехи",
    weight=50,
    description="Доспехи рыцаря 17-го века",
    owner=None,
    defence=50,
)
magic_sword = Weapon(
    name="Волшебный меч",
    weight=20,
    description="Сияет как солнце",
    owner=None,
    damage=100,
)

# Инициализация мира
game_world = World(
    player=player,
    combat_mobs=[dragon],
    exploration_mobs=[dragon],
    trade_mobs=[],
    exploration_items=[health_bottle, armor, magic_sword],
    events=[],
)

# Основной игровой цикл
current_situation = game_world.generate_situation(Exploration)

while current_situation is not None:
    action_result = current_situation.process_input()
    
    if action_result == "quit":
        print("Вы покинули игру.")
        break
    elif action_result == "defeat":
        print("Вы проиграли!")
        break
    elif isinstance(action_result, Situation):  # продолжение игры
        current_situation = action_result
    elif action_result == "victory":
        print("Поздравляем! Вы победили дракона!")
        # Добавляем трофей в инвентарь
        game_world.player.inventory.append(magic_sword)
        magic_sword.owner = game_world.player.name
        print(f"Вы получили: {magic_sword.name}!")
        break
    else:
        # Обработка неизвестного результата
        print("Неизвестное действие.")
        break
