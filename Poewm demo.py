import os
register_name = []
the_poem_book = {}
name = input("Введіть нікнейм")
def menu(new_poem):
    print("Вибери дію:"
          "\n 1. Новий вірш"
          "\n 2. Мої вірші"
          "\n 3. Вірші комьюніті"
          "\n 4. Повторна реєстрація")
    choice = int(input("Укажи свій вибір: "))
    if choice == 1:
        new_poem(menu, name)
    elif choice == 2:
        search_poem()
def new_poem(menu, name):
    name_poem = input("Введи назву вірша:")
    con_poem = input("Введи текст вірша:")
    print(con_poem, "\n Чудовий вірш!")
    if name_poem not in the_poem_book:
        the_poem_book[name_poem] = con_poem

        with open(f"{name}.txt", "a", encoding="utf-8") as f:
            f.write(f"{name_poem}:{con_poem}\n")

        return  # ЗАМІСТЬ menu(new_poem) пиши return
    else:
        print("Помилка! Така назва вже існує! Введіть дані повторно")

def search_poem():
    titles = list(the_poem_book.keys())
    while True:
        print("\n ---- ОБЕРИ ВІРШ ---- ")
        for i, title in enumerate(titles, 1):
         print(f"{i}. {title}")
        if not titles:
            print("У тебе ще немає доданих віршів!")
            input("\nНатисніть Enter, щоб повернутися...")
            menu(new_poem)
        print("0 Щоб повернутися у меню")
        choice =  input("Твій вибір:")
        if choice == 1:
            return
        elif choice == "0":
            menu(new_poem)
        elif choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(titles):
                chosen_title = titles[index]
                print(f"\n=== {chosen_title} ===")
                print(the_poem_book[chosen_title])
                print("======================")
                input("Натисни Enter щоб повернутися")
            else:
                print("Помилка! Такого номера немає")
        else:
            print("Помилка! Недійсне значення!")
def name_menu():
        user_file = f"{name}.txt"

        # Якщо файлу НЕМАЄ — створюємо його порожнім ОДИН РАЗ
        if not os.path.exists(user_file):
            with open(user_file, "w", encoding="utf-8") as f:
                pass

        the_poem_book.clear()

        # Читаємо файл користувача рядок за рядком
        with open(f"{name}.txt", "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    # Розділяємо рядок на назву та текст вірша
                    title, text = line.strip().split(":", 1)
                    the_poem_book[title] = text
                    return True
                else:
                   print("Помилка")
                   print((register_name))
if name_menu():
    while True:
        menu(new_poem)