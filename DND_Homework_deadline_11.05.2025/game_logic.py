from random import choices
from textwrap import dedent

from goofy_user_protection import safe_input, closest_match
from abc import abstractmethod
from usefull_things import show_stats


class Item:
    def __init__(self, name: str, weight, description: str, owner=None):
        self.name = name
        self.description = description
        self.owner = owner
        self.weight = weight

    def get_description(self):
        print(
            dedent(
                f"""
            ОПИСАНИЕ ПРЕДМЕТА {self.name}
            {self.description}
            """
            )
        )

    def use(self, log=False):
        print("В бою этот предмет не получится использовать!")


class HealthBottle(Item):
    def __init__(self, name, weight, description, owner, hp):

        super().__init__(name=name, weight=weight, description=description, owner=owner)
        self.hp = hp

    def use(self, log=False):
        if self.owner.hp + self.hp > self.owner.max_health:
            self.owner.hp = self.owner.max_health
            if log:
                print(
                    f"{self.name} восстановило здоровье до максимума {self.owner.max_health}"
                )
        else:
            self.owner.hp += self.hp
            if log:
                print(f"{self.name} восстановило здоровье до {self.owner.hp}")


class Armor(Item):
    def __init__(self, name, weight, description, owner, defence):

        super().__init__(name=name, weight=weight, description=description, owner=owner)
        self.defence = defence

    def use(self, log=False):
        if self.owner.inventory.equipped_armor == None:
            self.owner.defence += self.defence
            if log:
                print(f"{self.name} было успешно экипировано!")
        else:
            if log:
                print(f"Снимите одежду прежде чем одевать новую!")

    def unuse(self, log=False):
        if self.owner.inventory.equipped_armor != None:
            self.owner.defence -= self.defence
            if isinstance(self.owner, Warrior):
                self.owner.defence -= self.defence * 2
            elif isinstance(self.owner, Wizard):
                self.owner.defence -= self.defence // 2
                self.owner.luck *= 2
            else:
                self.owner.defence -= self.defence // 2
            self.owner.inventory.equipped_armor = None
            if log:
                print(f"{self.name} было успешно снято!")
        else:
            if log:
                print(f"Экипируйте одежду прежде чем снимать!")


class Weapon(Item):
    def __init__(self, name, damage, weight, description, owner):

        super().__init__(name=name, weight=weight, description=description, owner=owner)
        self.damage = damage

    def use(self, log=False):
        if self.owner.inventory.equipped_armor == None:
            self.owner.damage += self.damage
            self.owner.inventory.equipped_weapon = self
            if log:
                print(f"{self.name} было успешно надето!")
        else:
            if log:
                print(f"уберите оружие прежде чем брать новое!")

    def unuse(self, log=False):
        if self.owner.inventory.equipped_armor != None:
            self.owner.damage -= self.damage
            self.owner.inventory.equipped_armor = None
            if log:
                print(f"{self.name} было успешно убрано!")
        else:
            if log:
                print(f"Возьмите оружие прежде чем убирать!")


class Inventory:
    def __init__(self, owner, items: list):
        self.owner = owner
        self.items = items
        self.equipped_armor = None
        self.equipped_weapon = None

    def show_items(self):
        if self.items == []:
            print("Инвентарь пуст!")
        else:
            print(
                f"ИНВЕНТАРЬ ИГРОКА {self.owner.name} (для выбора предмета напишите '/использовать 'название'')"
            )
            for item in self.items:
                print(f"- {item.name}")
            if self.equipped_armor:
                print(
                    f"Надето: {self.equipped_armor.name} (+{self.equipped_armor.defence} защиты)"
                )
            if self.equipped_weapon:
                print(
                    f"В руках: {self.equipped_weapon.name} (+{self.equipped_weapon.damage} наносимого урона)"
                )

    def add_item(self, item: Item):
        self.items.append(item)
        item.owner = self.owner


class Mob:
    def __init__(self, name, hp, defence, damage, luck, max_weight, max_health):
        self.max_health = max_health
        self.name = name
        self.hp = hp
        self.defence = defence
        self.damage = damage
        self.luck = luck
        self.inventory = Inventory(self, [])
        self.max_weight = max_weight

    def attack(self, other, log=False):
        damage = choices(
            [self.damage * (100 / other.defence), 0],
            [self.luck / 100, 1 - self.luck / 100],
        )[0]
        other.hp -= damage
        if log:
            if damage != 0:
                print(f"{self.name} нанёс {damage} урона!")
            else:
                print(f"{self.name} промахнулся!")

    def stats(self):
        return dedent(
            f"""
                СТАТУС ГЕРОЯ {self.name}:
                - {self.hp} здоровья
                - {self.defence} защиты
                - {self.damage} наносимого урона противникам
                - {self.luck} удачи
                """
        )

    def get_inventory(self):
        return self.inventory.show_items()


class Wizard(Mob):
    def __init__(self, name, hp, defence, damage, luck, stats, max_weight, max_health):
        super().__init__(
            name=name,
            hp=hp,
            defence=defence,
            damage=damage,
            luck=luck,
            max_weight=max_weight,
            max_health=max_health,
        )

        self.wisdom = stats[0]
        self.concentration = stats[1]
        self.intuition = stats[2]

    def stats(self):
        return dedent(
            f"""
                СТАТУС ГЕРОЯ {self.name}:
                - {self.hp} здоровья
                - {self.defence} защиты
                - {self.damage} наносимого урона противникам
                - {self.luck} удачи
                - {self.wisdom} мудрости
                - {self.concentration} концентрации
                - {self.intuition} интуиции
                """
        )


class Warrior(Mob):
    def __init__(
        self, name, hp, defence, damage, luck, stats: list, max_weight, max_health
    ):
        super().__init__(
            name=name,
            hp=hp,
            defence=defence,
            damage=damage,
            luck=luck,
            max_weight=max_weight,
            max_health=max_health,
        )
        self.power = stats[0]
        self.durability = stats[1]
        self.spirit = stats[2]

    def stats(self):
        return dedent(
            f"""
                СТАТУС ГЕРОЯ {self.name}:
                - {self.hp} здоровья
                - {self.defence} защиты
                - {self.damage} наносимого урона противникам
                - {self.luck} удачи
                - {self.power} силы
                - {self.durability} прочности
                - {self.spirit} духа
                """
        )


class Archer(Mob):
    def __init__(
        self, name, hp, defence, damage, luck, stats: list, max_weight, max_health
    ):
        super().__init__(
            name=name,
            hp=hp,
            defence=defence,
            damage=damage,
            luck=luck,
            max_weight=max_weight,
            max_health=max_health,
        )
        self.dexterity = stats[0]
        self.vision = stats[1]
        self.stamina = stats[2]

    def stats(self):
        return dedent(
            f"""
                СТАТУС ГЕРОЯ {self.name}:
                - {self.hp} здоровья
                - {self.defence} защиты
                - {self.damage} наносимого урона противникам
                - {self.luck} удачи
                - {self.dexterity} ловкости
                - {self.vision} зрения
                - {self.stamina} выносливости
                """
        )


class World:
    def __init__(
        self,
        player,
        combat_mobs,
        exploration_mobs,
        trade_mobs,
        exploration_items,
        events,
    ):
        self.player = player
        self.combat_mobs = combat_mobs
        self.exploration_mobs = exploration_mobs
        self.exploration_items = exploration_items
        self.events = events
        self.trade_mobs = trade_mobs

    def generate_situation(self, situation, **kwargs):
        if situation == Exploration:
            return situation(
                player=self.player,
                mobs=self.exploration_mobs,
                events=self.events,
                world=self,
                items=self.exploration_items,
            )
        if situation == Combat:
            return situation(
                player=self.player, mobs=self.combat_mobs, world=self, **kwargs
            )


class Situation:
    def __init__(self, player: Mob, mobs: list, world: World):
        self.player = player
        self.mobs = mobs
        self.world = world
        self.commands = ["/инвентарь", "/осмотреться", "/атаковать", "/использовать"]

    @abstractmethod
    def process_input(self):
        pass


class Exploration(Situation):
    def __init__(self, player: Mob, mobs: list, events: list, items: list, world):
        super().__init__(player=player, mobs=mobs, world=world)
        self.items = items
        self.events = events
        self.commands = [
            "/инвентарь",
            "/осмотреться",
            "/атаковать",
            "/использовать",
            "/взять",
        ]

    def process_input(self):
        player_input = safe_input(
            f"Доступные команды: {self.commands}.\n '/использовать' и '/взять' ожидают что после команды через '--' будет написан предмет \n--> "
        )

        self.subject = None
        if len(player_input.split("--")) < 2:
            player_input = closest_match(player_input, self.commands)
        else:
            player_input_list = player_input.split("--")
            player_input = closest_match(player_input_list[0], self.commands)
            mobs_names = [mob.name for mob in self.mobs]
            items_names = [item.name for item in self.items]
            inventory_names = [item.name for item in self.player.inventory.items]

            subject_names = items_names + mobs_names + inventory_names

            subject_name = closest_match(player_input_list[1], subject_names)
            if subject_name is None:
                print("Не удалось распознать объект.")
                return self.process_input()
            if subject_name in mobs_names:
                self.subject = self.mobs[mobs_names.index(subject_name)]
            elif subject_name in inventory_names:
                self.subject = self.player.inventory.items[
                    inventory_names.index(subject_name)
                ]
            else:
                self.subject = self.items[items_names.index(subject_name)]
        if player_input == "/инвентарь":
            self.player.get_inventory()
            return self.process_input()
        if player_input == "/осмотреться":
            print("Вокруг вас:")
            for event in self.events + self.mobs + self.items:
                print(event.name)
            print(self.player.stats())
            return self.process_input()
        if player_input == "/атаковать" and self.subject != None:
            combat_situation = self.world.generate_situation(Combat, enemy=self.subject)
            return combat_situation

        if player_input == "/взять" and self.subject:

            if self.subject in self.items:
                self.player.inventory.add_item(self.subject)
                self.items.remove(self.subject)
                print(f"Вы успешно подобрали {self.subject.name}!")
            else:
                print(f"Вы не можете взять {self.subject.name}!")

        if player_input == "/использовать":
            if self.subject in self.player.inventory.items:
                self.subject.use(log=True)
                return self.process_input()
            else:
                print(f"Предмета {self.subject.name} у вас нет!")
                return self.process_input()

        return self.process_input()


class Combat(Situation):
    def __init__(self, player: Mob, mobs: list, enemy, world):
        super().__init__(player=player, mobs=mobs, world=world)
        self.commands = [
            "/инвентарь",
            "/атаковать",
            "/бежать",
            "/использовать",
            "/осмотреть",
        ]
        self.enemy = enemy
        self.is_subject_alive = True

    def process_input(self):
        if self.is_subject_alive:
            if self.enemy.hp <= 0:
                if self.enemy in self.world.combat_mobs:
                    self.world.combat_mobs.remove(self.enemy)
                if self.enemy in self.world.exploration_mobs:
                    self.world.exploration_mobs.remove(self.enemy)
                print(f"{self.enemy.name} был убит! Можете забрать его вещи.")
                self.items += self.enemy.inventory.items
                self.commands = [
                    "/инвентарь",
                    "/использовать",
                    "/взять",
                    "/осмотреть",
                    "/выйти из боя",
                ]
                self.is_subject_alive = False
                return self.process_input()
        if self.player.hp <= 0:
            print("Вы убиты!")
            return 0
        show_stats(self.player.stats(), self.enemy.stats())
        player_input = safe_input(
            f"Доступные команды: {self.commands}.\n '/использовать' и '/взять' ожидают что после команды через '--' будет написан предмет \n--> "
        )
        self.subject = None
        if len(player_input.split("--")) < 2:
            command = closest_match(player_input, self.commands)
        else:
            player_input_list = player_input.split("--")
            mobs_names = [mob.name for mob in self.mobs]
            inventory_names = [
                item.name for item in self.items + self.player.inventory.items
            ]
            subject_names = mobs_names + inventory_names
            subject_name = closest_match(player_input_list[1], subject_names)
            if subject_name is None:
                print("Не удалось распознать объект.")
                return self.process_input()
            if subject_name in mobs_names:
                self.subject = self.mobs[mobs_names.index(subject_name)]
            else:
                self.subject = self.player.inventory.items[
                    inventory_names.index(subject_name)
                ]
            command = closest_match(player_input.split("--")[0], self.commands)

        if command == "/инвентарь":
            self.player.get_inventory()
            return self.process_input()
        if command == "/атаковать":
            if self.enemy.hp >= 0:
                self.player.attack(self.enemy, log=True)
            if self.enemy.hp <= 0:
                if self.enemy in self.world.combat_mobs:
                    self.world.combat_mobs.remove(self.enemy)
                if self.enemy in self.world.exploration_mobs:
                    self.world.exploration_mobs.remove(self.enemy)
                print(f"{self.enemy.name} был убит! Можете забрать его вещи.")
                self.commands = [
                    "/инвентарь",
                    "/использовать",
                    "/взять",
                    "/осмотреть",
                    "/выйти из боя",
                ]
                return self.process_input()
            if self.player.hp >= 0:
                self.enemy.attack(self.player, log=True)

            return self.process_input()

        if command == "/бежать":
            total_luck = self.player.luck / 100
            for mob in self.mobs:
                total_luck *= mob.luck / 100
            action = choices([Exploration, None], [total_luck, 1 - total_luck])
            if action is Exploration:
                print("Вы сбежали!")

                explore_situation = self.world.generate_situation(Exploration)
                return explore_situation
            else:
                print("Побег неудался!")
                self.enemy.attack(self.player, log=True)
                return self.process_input()
        if command == "/использовать":
            if self.subject in self.player.inventory.items:
                self.subject.use(log=True)
                return self.process_input()
            else:
                print(f"Предмета {self.subject.name} у вас нет!")
                return self.process_input()

        if command == "/осмотреть":
            print(self.enemy.stats())
            return self.process_input()
        if command == "/выйти из боя" and "/выйти из боя" in self.commands:
            print("Вы вышли из боя")
            explore_situation = self.world.generate_situation(Exploration)
            return explore_situation
        return self.process_input()
