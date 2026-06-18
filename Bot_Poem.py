import os

# Глобальні змінні програми
the_poem_book = {}
current_user = ""

# Налаштування файлу паролів
PASSWORDS_FILE = "passwords.txt"


def clear_screen():
    """Очищує термінал, створюючи ефект 'нового вікна'"""
    os.system('cls' if os.name == 'nt' else 'clear')


def auth_menu():
    """Екран реєстрації та входу з паролем"""
    global current_user
    clear_screen()
    print("=== ЛАСКАВО ПРОСИМО ДО ПОЕТИЧНОГО БЛОКНОТА ===")

    name = input("Введіть нікнейм: ").strip()
    if not name:
        print("Нікнейм не може бути порожнім!")
        input("\nНатисни Enter, щоб спробувати знову...")
        return False

    password = input("Введіть пароль: ").strip()

    # Перевіряємо, чи існує база паролів
    user_exists = False
    correct_password = False

    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    saved_user, saved_pass = line.strip().split(":", 1)
                    if saved_user == name:
                        user_exists = True
                        if saved_pass == password:
                            correct_password = True
                        break

    if user_exists:
        if correct_password:
            print(f"\nВхід успішний! Вітаємо назад, {name}.")
        else:
            print("\nПомилка! Неправильний пароль для цього акаунта.")
            input("\nНатисни Enter...")
            return False
    else:
        # Якщо користувача немає — реєструємо його
        with open(PASSWORDS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{name}:{password}\n")
        print(f"\nСтворено новий акаунт для {name}!")

    # Створюємо файл для віршів користувача, якщо його немає
    user_file = f"{name}.txt"
    if not os.path.exists(user_file):
        with open(user_file, "w", encoding="utf-8") as f:
            pass

    # Завантажуємо вірші цього користувача в пам'ять
    current_user = name
    the_poem_book.clear()

    with open(user_file, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                title, text = line.strip().split(":", 1)
                # Замінюємо технічний символ назад на перенос рядка
                the_poem_book[title] = text.replace("\\n", "\n")

    input("\nНатисни Enter, щоб увійти в меню...")
    return True


def new_poem():
    """Екран створення нового вірша"""
    clear_screen()
    print(f"=== СТВОРЕННЯ ВІРША (Автор: {current_user}) ===")

    name_poem = input("Введи назву вірша: ").strip()
    if not name_poem:
        print("Назва не може бути порожньою!")
        input("\nНатисни Enter...")
        return

    if name_poem in the_poem_book:
        print("Помилка! Вірш з такою назвою вже існує.")
        input("\nНатисни Enter...")
        return

    print("Введи текст вірша (якщо хочеш зробити перенос рядка, пиши \\n):")
    con_poem = input("Текст: ")

    # 1. Записуємо в оперативну пам'ять
    the_poem_book[name_poem] = con_poem

    # 2. Одразу зберігаємо на диск (замінюємо реальні переноси на технічні)
    saved_text = con_poem.replace("\n", "\\n")
    with open(f"{current_user}.txt", "a", encoding="utf-8") as f:
        f.write(f"{name_poem}:{saved_text}\n")

    print("\nЧудовий вірш! Успішно збережено на комп'ютер.")
    input("\nНатисни Enter, щоб повернутися в меню...")


def search_poem():
    """Екран перегляду та читання віршів"""
    while True:
        clear_screen()
        titles = list(the_poem_book.keys())
        print(f"=== МОЇ ВІРШІ (Всього: {len(titles)}) ===")

        if not titles:
            print("У тебе ще немає доданих віршів!")
            print("\n0. Повернутися у меню")
        else:
            for i, title in enumerate(titles, 1):
                print(f"{i}. {title}")
            print("\n0. Повернутися у меню")

        choice = input("\nТвій вибір: ").strip()

        if choice == "0":
            return  # Вихід з функції читання назад у меню

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(titles):
                # ЕФЕКТ НОВОГО ВІКНА: очищуємо екран для читання конкретного вірша
                clear_screen()
                chosen_title = titles[index]
                print(f"=== ВІКНО ЧИТАННЯ: {chosen_title} ===")
                print(the_poem_book[chosen_title])
                print("=========================================")
                input("\nНатисни Enter, щоб закрити вірш...")
            else:
                print("Помилка! Такого номера немає.")
                input("Натисни Enter...")
        else:
            print("Помилка! Введіть число.")
            input("Натисни Enter...")


def main_menu():
    """Головне меню програми"""
    while True:
        clear_screen()
        print(f"=== ГОЛОВНЕ МЕНЮ (Користувач: {current_user}) ===")
        print("1. Новий вірш")
        print("2. Мої вірші")
        print("3. Вірші ком'юніті (В розробці)")
        print("4. Змінити акаунт / Вихід")

        choice = input("\nУкажи свій вибір: ").strip()

        if choice == "1":
            new_poem()
        elif choice == "2":
            search_poem()
        elif choice == "4":
            print("\nВихід з акаунта...")
            break
        else:
            print("Неправильний вибір, спробуй ще раз.")
            input("Натисни Enter...")


# --- ГОЛОВНИЙ ДВИГУН ПРОГРАМИ ---
while True:
    if auth_menu():
        main_menu()