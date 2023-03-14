def get_new_perk_time(edu_index, is_prem):

    if edu_index == 11:
        edu_index_residency = 20

    # GOLD
    time = (1 - edu_index/50) * next_perk_level**2 * 0.72
    # MONEY
    time = (1 - edu_index/50) * next_perk_level**2 * 9.6

    if is_prem:
        time = time / 2

    if next_perk_level <= 100:
        time = time / 2

    if next_perk_level <= 50:
        time = time / 2

    return time


# ИЗМЕНИТЬ ЗНАЧЕНИЯ
edu_index = 5  # индекс образования
is_prem = True  # с премиумом = True, без = False
start_perk = 30  # с какого навыка
end_perk = 100  # до какого

# теперь запускай скрипт

result_time = 0
for next_perk_level in range(start_perk + 1, end_perk + 1):
    result_time += get_new_perk_time(edu_index, is_prem)

print(f"От {start_perk} до {end_perk}")
print("Дней: ", result_time/60/60/24)
