import pygame
import random
import sys


def main():
    # 1. Ініціалізація саме для мобільних
    pygame.init()

    # Використовуємо FULLSCREEN, щоб Android не ламався об розміри вікна
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    width, height = screen.get_size()

    clock = pygame.time.Clock()

    # Використовуємо вбудований шрифт (SysFont None), щоб не було помилок з файлами
    font = pygame.font.SysFont(None, int(width / 15))

    # Налаштування гри
    cell_size = width // 20
    snake = [[10, 10], [10, 11], [10, 12]]
    direction = [0, -1]
    food = [random.randint(0, (width // cell_size) - 1), random.randint(0, (height // cell_size) - 1)]
    score = 0

    running = True
    while running:
        # 2. Обробка керування (тапи по екрану)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Просте керування: тапнув зліва — повернув, справа — повернув
                mx, my = event.pos
                if mx < width / 2:
                    if direction == [0, -1]:
                        direction = [-1, 0]
                    elif direction == [-1, 0]:
                        direction = [0, 1]
                    elif direction == [0, 1]:
                        direction = [1, 0]
                    else:
                        direction = [0, -1]
                else:
                    if direction == [0, -1]:
                        direction = [1, 0]
                    elif direction == [1, 0]:
                        direction = [0, 1]
                    elif direction == [0, 1]:
                        direction = [-1, 0]
                    else:
                        direction = [0, -1]

        # 3. Логіка руху
        new_head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]

        # Перевірка меж (щоб не вилітало)
        if (new_head[0] < 0 or new_head[0] >= width // cell_size or
                new_head[1] < 0 or new_head[1] >= height // cell_size or
                new_head in snake):
            running = False  # Програв

        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            food = [random.randint(0, (width // cell_size) - 1), random.randint(0, (height // cell_size) - 1)]
        else:
            snake.pop()

        # 4. Малювання
        screen.fill((30, 30, 30))  # Темний фон

        # Малюємо їжу
        pygame.draw.rect(screen, (255, 0, 0), (food[0] * cell_size, food[1] * cell_size, cell_size - 2, cell_size - 2))

        # Малюємо змійку
        for segment in snake:
            pygame.draw.rect(screen, (0, 255, 0),
                             (segment[0] * cell_size, segment[1] * cell_size, cell_size - 2, cell_size - 2))

        # Вивід рахунку
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
