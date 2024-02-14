import math

# Předpokládáme, že máme dva body s jejich souřadnicemi (x1, y1) a (x2, y2)
x1, y1 = 4, 4  # Příklad souřadnic prvního bodu
x2, y2 = 8, 2  # Příklad souřadnic druhého bodu

# Spočítáme rozdíl souřadnic mezi body
delta_x = x2 - x1
delta_y = y2 - y1

# Vypočítáme úhel spoje od osy x pomocí funkce atan2
angle_rad = math.atan2(delta_y, delta_x)

# Převedeme úhel na stupně, pokud je potřeba
angle_deg = math.degrees(angle_rad) % 360

print("Úhel spoje od osy x:", angle_deg)
