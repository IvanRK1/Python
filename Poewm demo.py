register_name = []
the_poem_book = {}
def menu(new_poem):
    print("Вибери дію:"
          "\n 1. Новий вірш"
          "\n 2. Мої вірші"
          "\n 3. Вірші комьюніті"
          "\n 4. Повторна реєстрація")
    choice = int(input("Укажи свій вибір: "))
    if choice == 1:
        new_poem(menu)
    elif choice == 2:
        search_poem()
def new_poem(menu):
    name_poem = input("Введи назву вірша:")
    con_poem = input("Введи текст вірша:")
    print(con_poem, "\n Чудовий вірш!")
    if name_poem not in the_poem_book:
        the_poem_book[name_poem] = con_poem
        menu(new_poem)
    else:
        print("Помилка! Така назва вже існує! Введіть дані повторно")
        new_poem(menu)

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
    name = input("Введіть нікнейм")
    if name not in register_name:
        register_name.append(name)
        print(register_name)
        return True

    else:
        print("Помилка")
        print((register_name))
while True:
    if name_menu():
     menu(new_poem)
     break