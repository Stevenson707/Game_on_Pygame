import random


def bots_move():
    lead_x = 550
    lead_y = 550

    enemy_x = 500
    enemy_y = 400
    enemySpeed = 5
    min_dist = 200
    enemy_x_change = 0
    enemy_y_change = 0

    lead_x_change = 0
    lead_y_change = 0

    lead_x += lead_x_change
    lead_y += lead_y_change

    delta_x = lead_x - enemy_x
    delta_y = lead_y - enemy_y

    if abs(delta_x) <= min_dist and abs(delta_y) <= min_dist:
        enemy_move_x = abs(delta_x) > abs(delta_y)
        if abs(delta_x) > enemySpeed and abs(delta_x) > enemySpeed:
            enemy_move_x = random.random() < 0.5
        if enemy_move_x:
            enemy_x += min(delta_x, enemySpeed) if delta_x > 0 else max(delta_x, -enemySpeed)
        else:
            enemy_y += min(delta_y, enemySpeed) if delta_y > 0 else max(delta_y, -enemySpeed)