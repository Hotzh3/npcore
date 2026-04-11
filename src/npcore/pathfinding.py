from heapq import heappush, heappop


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(pos, env):
    x, y = pos
    candidates = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]

    return [p for p in candidates if env.is_within_bounds(*p)]


def a_star(start, goal, env):
    open_set = []
    heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in get_neighbors(current, env):
            tentative = g_score[current] + 1

            if neighbor not in g_score or tentative < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                f = tentative + manhattan(neighbor, goal)
                heappush(open_set, (f, neighbor))

    return []


def get_neighbors(pos, env):
    x, y = pos
    candidates = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]

    valid = []
    for p in candidates:
        if env.is_within_bounds(*p) and not env.is_blocked(*p):
            valid.append(p)

    return valid