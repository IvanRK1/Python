import pygame
import random

pygame.init()
dis = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

# Кольори
white = (255, 255, 255)
green = (0, 130, 0)
wgreen = (0, 50, 0)
red = (213, 50, 80)
bgreen = (0, 85, 0)
gray = (70, 70, 70)
# Початкові координати та рух
x1 = 300
y1 = 200
x_change = 0
y_change = 0

# Їжа
foodx = random.randrange(0, 600, 10)
foody = random.randrange(0, 400, 10)

snake_list = []
lenght_of_snake = 1
while True:
    # 1. ОЧИЩЕННЯ ЕКРАНА
    dis.fill(gray)
    pygame.display.set_caption("Змійка версія 0.0")

    # 2. ВИХІД, КЕРУВАННЯ ТА СМЕРТЬ(ВРІЗАННЯ В БОРДЕР)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                y_change, x_change = -10, 0
            elif event.key == pygame.K_DOWN:
                y_change, x_change = 10, 0
            elif event.key == pygame.K_LEFT:
                y_change, x_change = 0, -10
            elif event.key == pygame.K_RIGHT:
                y_change, x_change = 0, 10
    if x1 >= 600 or x1 < 0 or y1 >= 400 or y1 < 0:
     pygame.quit()
     quit()

    # 3. РУХ
    x1 += x_change
    y1 += y_change

    # 4. ЛОГІКА ТІЛА
    snake_head = [x1, y1]
    snake_list.append(snake_head)

    if len(snake_list) > lenght_of_snake:
        del snake_list[0]

    # 5. ПЕРЕВІРКА НА СМЕРТЬ (Врізання в себе)
    for x in snake_list[:-1]:
        if x == snake_head:
            pygame.quit()
            quit()

    # 6. ПЕРЕВІРКА ДОТИКУ ДО ЇЖІ
    if x1 == foodx and y1 == foody:
        foodx = random.randrange(0, 600, 10)
        foody = random.randrange(0, 400, 10)
        lenght_of_snake += 1

    # 7. МАЛЮВАННЯ
    # Яблуко
    pygame.draw.rect(dis, red, [foodx, foody, 20, 20])

    #Змійка
    for x in snake_list:
        pygame.draw.rect(dis, bgreen, [x1, y1, 20, 20])
        for segment in snake_list[:-1]:  # Беремо все, крім останнього
         pygame.draw.rect(dis, wgreen, [segment[0], segment[1], 20, 20])

    # 8. ОНОВЛЕННЯ ДИСПЛЕЮ
    pygame.display.update()
    clock.tick(10)