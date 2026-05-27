register_name = []


def menu():
    print(
        "Введіть дію яку хочете виконати \n 1. Новий вірш \n Переглянути свої вірші \n опублікувати вірш \n вірші інших людей")


def name():
    global register_name
    name_input = input("Введіть бажаний нінейм")  # 1. Змінено назву змінної на name_input, щоб не видалялась сама функція name()
    if name_input not in register_name:
        register_name.append(name_input)
        print("Імя успішно додано")
        print(register_name)
        menu()
        return True  # 2. Додано сигнал успіху
    else:
        print("Цей нікнейм вже зайнятий!")
        print(register_name)
        return False  # 2. Додано сигнал помилки


# Звідси прибрано перший виклик name(), щоб не питало двічі

while True:
    if name() == True:  # Перевіряємо, чи успішна реєстрація
        # menu() прибрано звідси, бо воно вже викликається всередині твоєї функції name() вище
        break
