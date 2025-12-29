class House:
    def __init__(self, id, number, area, floor, roomscount, street, buildingtype, servicetime):
        self.id = id
        self.number = number
        self.area = area
        self.floor = floor
        self.roomscount = roomscount
        self.street = street
        self.building_type = buildingtype
        self.service = servicetime
    
    def __str__(self):
        return (f"Квартира {self.number}: {self.roomscount} комн., "
                f"{self.area} м², {self.floor} этаж, ул. {self.street}, "
                f"{self.building_type}, срок экспл. {self.service} лет")


class HouseManager:
    def __init__(self):
        self.houses = []
    
    def add_house(self, house):
        self.houses.append(house)
    
    def get_apartments_by_rooms(self, target_rooms):
        result = []
        for house in self.houses:
            if house.roomscount == target_rooms:
                result.append(house)
        return result
    
    def get_apartments_on_floors(self, target_rooms, min_floor, max_floor):
        result = []
        for house in self.houses:
            if (house.roomscount == target_rooms and 
                min_floor <= house.floor <= max_floor):
                result.append(house)
        return result
    
    def get_apartments_by_min_area(self, min_area):
        result = []
        for house in self.houses:
            if house.area > min_area:
                result.append(house)
        return result
    
    def display_houses(self, houses_list, title):
        print(f"\n{title}:")
        if not houses_list:
            print("Квартиры не найдены")
            return
        
        for house in houses_list:
            print(house)
        print(f"Всего найдено: {len(houses_list)} квартир")


if __name__ == "__main__":
    manager = HouseManager()
    
    manager.add_house(House(1, 25, 45.5, 2, 1, "Ленина", "Панельный", 5))
    manager.add_house(House(2, 103, 75.2, 5, 2, "Советская", "Кирпичный", 8))
    manager.add_house(House(3, 58, 34.8, 1, 1, "Мира", "Панельный", 3))
    manager.add_house(House(4, 210, 92.5, 7, 3, "Центральная", "Монолитный", 12))
    manager.add_house(House(5, 76, 68.3, 3, 2, "Гагарина", "Кирпичный", 6))
    manager.add_house(House(6, 315, 120.7, 9, 4, "Ленина", "Монолитный", 15))
    manager.add_house(House(7, 42, 55.1, 2, 2, "Садовая", "Панельный", 4))
    manager.add_house(House(8, 129, 83.6, 6, 3, "Пушкина", "Кирпичный", 9))
    manager.add_house(House(9, 87, 48.9, 4, 1, "Молодежная", "Панельный", 7))
    manager.add_house(House(10, 234, 105.4, 8, 4, "Ленина", "Монолитный", 14))
    manager.add_house(House(11, 63, 72.8, 3, 3, "Советская", "Кирпичный", 8))
    manager.add_house(House(12, 181, 96.2, 10, 3, "Центральная", "Монолитный", 16))
    manager.add_house(House(13, 29, 39.7, 1, 1, "Гагарина", "Панельный", 2))
    manager.add_house(House(14, 152, 88.4, 5, 3, "Пушкина", "Кирпичный", 11))
    manager.add_house(House(15, 94, 62.5, 4, 2, "Садовая", "Панельный", 6))

    two_room_apartments = manager.get_apartments_by_rooms(2)
    manager.display_houses(two_room_apartments, "Квартиры с 2 комнатами")
    

    three_room_in_range = manager.get_apartments_on_floors(3, 5, 15)
    manager.display_houses(three_room_in_range, "Квартиры с 3 комнатами на этажах 5-15")
    
    large_apartments = manager.get_apartments_by_min_area(50)
    manager.display_houses(large_apartments, "Квартиры площадью более 50 м²")