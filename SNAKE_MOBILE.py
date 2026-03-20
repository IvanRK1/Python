import pygame
import random

pygame.init()
# Для телефона краще зробити екран вертикальним, наприклад 400x600
width, height = 400, 600
dis = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Кольори
white = (255, 255, 255)
green = (0, 130, 0)
wgreen = (0, 50, 0)
red = (213, 50, 80)
bgreen = (0, 85, 0)

# Початкові налаштування
x1, y1 = 200, 300
x_change, y_change = 0, 0
snake_list = []
lenght_of_snake = 1

# Координати для свайпів
start_x, start_y = 0, 0

# Їжа (randrange під нові розміри екрана)
foodx = random.randrange(0, width, 10)
foody = random.randrange(0, height, 10)

while True:
    dis.fill(green)
    pygame.display.set_caption("Snake Mobile Edition")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        # ЛОГІКА СВАЙПІВ
        if event.type == pygame.MOUSEBUTTONDOWN:
            start_x, start_y = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONUP:
            end_x, end_y = pygame.mouse.get_pos()
            diff_x = end_x - start_x
            diff_y = end_y - start_y

            # Визначаємо напрямок (потрібен рух хоча б на 20 пікселів)
            if abs(diff_x) > abs(diff_y):
                if diff_x > 20 and x_change == 0:
                    x_change, y_change = 10, 0  # Вправо
                elif diff_x < -20 and x_change == 0:
                    x_change, y_change = -10, 0  # Вліво
            else:
                if diff_y > 20 and y_change == 0:
                    x_change, y_change = 0, 10  # Вниз
                elif diff_y < -20 and y_change == 0:
                    x_change, y_change = 0, -10  # Вгору

    # Перевірка виходу за межі
    if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
        pygame.quit()
        quit()

    x1 += x_change
    y1 += y_change

    snake_head = [x1, y1]
    snake_list.append(snake_head)

    if len(snake_list) > lenght_of_snake:
        del snake_list[0]

    for x in snake_list[:-1]:
        if x == snake_head:
            pygame.quit()
            quit()

    if x1 == foodx and y1 == foody:
        foodx = random.randrange(0, width, 10)
        foody = random.randrange(0, height, 10)
        lenght_of_snake += 1

    # МАЛЮВАННЯ (Оптимізоване)
    pygame.draw.rect(dis, red, [foodx, foody, 10, 10])  # Їжа

    for segment in snake_list[:-1]:  # Хвіст
        pygame.draw.rect(dis, wgreen, [segment[0], segment[1], 10, 10])

    pygame.draw.rect(dis, bgreen, [x1, y1, 10, 10])  # Голова

    pygame.display.update()
    clock.tick(10)