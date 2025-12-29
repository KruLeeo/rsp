class Gemstone:
    def __init__(self, name, weight, transparency, price):
        self.name = name
        self.weight = weight
        self.transparency = transparency
        self.price = price
    
    def __str__(self):
        return f"{self.name}: {self.weight} карат, прозрачность: {self.transparency}%, цена: ${self.price}"


class GemstoneCollection:
    def __init__(self):
        self.gemstones = []
    
    def add_gemstone(self, gemstone):
        self.gemstones.append(gemstone)
    
    def display_collection(self):
        if not self.gemstones:
            print("Коллекция пуста")
            return
        
        for i, gemstone in enumerate(self.gemstones, 1):
            print(f"{i}. {gemstone}")
    
    def calculate_total_weight(self):
        return sum(gemstone.weight for gemstone in self.gemstones)
    
    def calculate_total_value(self):
        return sum(gemstone.price for gemstone in self.gemstones)
    
    def sort_by_value(self):
        self.gemstones.sort(key=lambda x: x.price, reverse=True)
    
    def sort_by_transparency(self):
        self.gemstones.sort(key=lambda x: x.transparency, reverse=True)
    
    def find_by_transparency_range(self, min_transparency, max_transparency):
        result = []
        for gemstone in self.gemstones:
            if min_transparency <= gemstone.transparency <= max_transparency:
                result.append(gemstone)
        return result
    
    def find_by_weight_range(self, min_weight, max_weight):
        result = []
        for gemstone in self.gemstones:
            if min_weight <= gemstone.weight <= max_weight:
                result.append(gemstone)
        return result


def main():
    collection = GemstoneCollection()
    
    collection.add_gemstone(Gemstone("Алмаз", 2.5, 99, 15000))
    collection.add_gemstone(Gemstone("Рубин", 1.8, 85, 8000))
    collection.add_gemstone(Gemstone("Изумруд", 3.2, 90, 12000))
    collection.add_gemstone(Gemstone("Сапфир", 2.1, 88, 9500))
    collection.add_gemstone(Gemstone("Аметист", 4.0, 75, 3000))
    collection.add_gemstone(Gemstone("Топаз", 3.5, 82, 4500))
    collection.add_gemstone(Gemstone("Гранат", 2.8, 78, 2800))
    collection.add_gemstone(Gemstone("Опал", 4.2, 65, 3500))
    collection.add_gemstone(Gemstone("Аквамарин", 3.0, 89, 6200))
    collection.add_gemstone(Gemstone("Цитрин", 5.1, 72, 1800))
    collection.add_gemstone(Gemstone("Турмалин", 2.3, 86, 5100))
    collection.add_gemstone(Gemstone("Жемчуг", 6.0, 60, 7500))
    collection.add_gemstone(Gemstone("Лазурит", 4.5, 55, 2200))
    collection.add_gemstone(Gemstone("Малахит", 7.2, 45, 1500))
    collection.add_gemstone(Gemstone("Бирюза", 3.8, 58, 3200))
    
    print(" Вся коллекция ")
    collection.display_collection()
    
    print(f"\n Общий вес: {collection.calculate_total_weight()} карат ")
    print(f" Общая стоимость: ${collection.calculate_total_value()} ")
    
    print("\n Сортировка по стоимости ")
    collection.sort_by_value()
    collection.display_collection()
    
    print("\n Сортировка по прозрачности ")
    collection.sort_by_transparency()
    collection.display_collection()
    
    print("\n Поиск камней с выбранной прозрачностью ")
    transparent_gems = collection.find_by_transparency_range(80, 95)
    for gem in transparent_gems:
        print(gem)
    
    print("\n Поиск камней с выбранным весом ")
    weight_gems = collection.find_by_weight_range(2.0, 3.0)
    for gem in weight_gems:
        print(gem)


if __name__ == "__main__":
    main()