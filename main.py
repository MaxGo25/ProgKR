import sys
from warehouse import Warehouse, Item, StorageZone

def show_menu():
    print("\n" + "="*45)
    print("  📦  INVENTORY MANAGER v1.0 ")
    print("="*45)
    print("1. Показати всі товари на складі")
    print("2. Додати новий товар")
    print("3. Пошук та редагування товару (через with)")
    print("4. Сортування товарів за ціною")
    print("5. Фільтрація (тільки Холодильна зона)")
    print("6. Зберегти поточний стан бази даних")
    print("7. Експортувати звіт у форматі CSV")
    print("0. Вихід із програми")
    print("="*45)

if __name__ == "__main__":
    manager = Warehouse()
    manager.load_config()
    manager.load_system_state()
    print(f"Ласкаво просимо до системи: {manager.config.get('warehouse_name')}")
    
    while True:
        show_menu()
        try:
            choice = input("Оберіть дію (0-7): ").strip()
            
            match choice:
                case "1":
                    manager.display_all()
                
                case "2":
                    print("\n--- ДОДАВАННЯ НОВОГО ТОВАРУ ---")
                    name = input("Введіть назву товару: ").strip()
                    if not name:
                        raise ValueError("Назва товару не може бути порожньою!")
                    
                    price = float(input("Введіть ціну товару (грн): "))
                    if price < 0:
                        raise ValueError("Ціна не може бути від'ємною!")
                    
                    print("Оберіть зону зберігання: 1 - COLD, 2 - DRY, 3 - SECURE")
                    zone_choice = input("Ваш вибір: ").strip()
                    if zone_choice == "1":
                        zone = StorageZone.COLD
                    elif zone_choice == "2":
                        zone = StorageZone.DRY
                    elif zone_choice == "3":
                        zone = StorageZone.SECURE
                    else:
                        raise ValueError("Обрано неіснуючу зону зберігання! Доступні лише 1, 2 або 3.")
                    
                    new_item = Item(name, price, zone)
                    manager.add_item(new_item)
                
                case "3":
                    query = input("\nВведіть назву товару для пошуку: ").strip()
                    found = manager.search_item(query)
                    
                    if not found:
                        print("[Info] Товарів з такою назвою не знайдено.")
                    else:
                        print("\nЗнайдені товари:")
                        for idx, item in enumerate(found):
                            print(f"[{idx}] {item}")
                        
                        edit_choice = input("\nВведіть номер товару для редагування (або Enter для відміни): ").strip()
                        if edit_choice.isdigit() and int(edit_choice) < len(found):
                            target_item = found[int(edit_choice)]
                            
                            try:
                                with target_item as editor:
                                    new_price_str = input(f"Введіть нову ціну (поточна {editor.price}): ").strip()
                                    if new_price_str:
                                        editor.price = float(new_price_str)
                            except ValueError as e:
                                print(f"❌ [Помилка валідації]: {e}")
                        else:
                            print("[Info] Редагування скасовано.")

                case "4":
                    manager.sort_items_by_price()
                    
                case "5":
                    manager.filter_cold_zone()

                case "6":
                    manager.save_system_state()
                
                case "7":
                    manager.export_inventory_report()
                
                case "0":
                    print("\nЗавершення роботи системи...")
                    manager.save_system_state()
                    sys.exit(0)
                
                case _:
                    print("[Warning] Невідома команда! Оберіть пункт від 0 до 7.")
                    
        except ValueError as e:
            print(f"\n ❌  [Помилка введення даних]: {e}")
            print(" 🛡️  Система не впала. Будь ласка, будьте уважні під час введення і спробуйте ще раз.")
        except Exception as e:
            print(f"\n ⚠️  [Критична помилка]: {e}")
