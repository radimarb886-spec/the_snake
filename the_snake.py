"""Игра «Змейка» (Изгиб Питона).

Реализация классической игры «Змейка» на Pygame с использованием ООП.
Змейка проходит сквозь границы поля, растёт при поедании яблок,
а при самоукусе сбрасывается в исходное состояние.
"""

from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (0, 0, 0)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None):
        """Инициализирует позицию и цвет объекта."""
        self.position = (
            (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE,
            (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE,
        )
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод отрисовки объекта (переопределяется)."""
        pass

    def draw_cell(self, position, color):
        """Закрашивает одну ячейку игрового поля.

        Args:
            position: кортеж координат ячейки (x, y).
            color: RGB-цвет заливки.
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока, которое поедает змейка."""

    def __init__(self):
        """Создаёт яблоко красного цвета в случайной позиции."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
        """Устанавливает случайную позицию яблока на поле.

        Args:
            snake_positions: список занятых змейкой координат, чтобы
                яблоко не появилось на теле змейки.
        """
        occupied = set(snake_positions or ())
        all_cells = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
        ]
        free_cells = [cell for cell in all_cells if cell not in occupied]
        self.position = choice(free_cells)

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    def __init__(self):
        """Инициализирует начальное состояние змейки."""
        super().__init__(body_color=SNAKE_COLOR)
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.length = 1
        self.last = None

    def update_direction(self):
        """Применяет отложенное направление движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        self.positions.insert(0, (new_x, new_y))
        
        # ВОТ ЗДЕСЬ МЫ ЗАПОМИНАЕМ ХВОСТ
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        # Затираем прошлый хвост черным цветом
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)
            
        # Рисуем тело змейки
        for position in self.positions[:-1]:
            self.draw_cell(position, self.body_color)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в исходное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для смены направления."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Запускает основной игровой цикл."""
    pygame.init()
    snake = Snake()
    apple = Apple()
    
    # Если вы передаете позиции змейки в яблоко, чтобы оно не спавнилось на ней:
    apple.randomize_position(snake.positions)

    while True:
        clock.tick(SPEED)

        # 1. Обработка нажатий и движения
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # 2. Проверка, съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # 3. ВОТ СЮДА ВСТАВЛЯЕМ ПРОВЕРКУ САМОУКУСА
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            # Очищаем экран от остатков старой змеи:
            screen.fill(BOARD_BACKGROUND_COLOR)
            pygame.display.update()
            # Пропускаем текущий шаг (отрисовку), чтобы змейка не нарисовалась поверх
            continue
        
        # 4. Отрисовка (если не было самоукуса)
        snake.draw()
        apple.draw()
        
        # 5. Обновление экрана
        pygame.display.update()

if __name__ == '__main__':
    main()
