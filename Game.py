import random


def kistku(money):
  while True:
   score_gamer =  random.randint(1, 12)
   score_computer = random.randint(1, 12)
   if score_computer > score_gamer:
      money -= 50
   elif score_computer < score_gamer:
      money += 50
   elif score_gamer == 12 and score_computer < 3:
       money += 500
   print("Ти програв 50 грошей:(" if score_computer > score_gamer else "Ти виграв 50 грошей!" if score_computer < score_gamer else "Нічия!" if score_gamer == 12 and score_computer < 3 else "ДЖЕКПОТ!!!!! Ти виграв 500 грошей")
   print( "У тебе:", score_gamer, "очок", "А у мене:", score_computer,)
   print("Твій баланс:", money)
   answer2 = input("1. Продовжити\n2. Вийти у меню")
   if answer2 == "1":
       kistku(money)
   elif answer2 == "2":
       main()
   return money

def main():
    money = 100
    while True:
     answer =   (input("----Меню---- \n 1.Почати гру\n 2.мій баланс\n 3.Закінчити гру"))
     if answer == "1":
        kistku(money)
     if answer == "3":
         print("Па! Зустрінемось наступного разу")
         break
     elif answer == "2":
         print("Твій баланс:", money)
     else:
         print("Не вірний варіант відповіді")

main()