import random
from collections import deque
import heapq
import math

class GreedyGridAgent:

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


class SimpleReflexAgent:

    def sense_and_act(self, percept):
        if percept['food_here']:
            return 'Stay'
        if percept['wall_ahead']:
            return random.choice(['Left', 'Right'])
        return 'Up'


class ModelBasedAgent:

    def __init__(self):
        self.visited_states = set()

    def sense_and_act(self, percept):
        state = (percept['food_here'], percept['wall_ahead'])

        if percept['food_here']:
            action = 'Stay'
        elif state in self.visited_states:
            action = 'Left'
        elif percept['wall_ahead']:
            action = 'Right'
        else:
            action = 'Up'

        self.visited_states.add(state)
        return action


class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def get_neighbors(self, state, grid_size, walls):

        x, y = state
        width, height = grid_size

        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]

        neighbors = []

        for action, next_state in moves:

            nx, ny = next_state

            if (
                0 <= nx < width
                and 0 <= ny < height
                and next_state not in walls
            ):
                neighbors.append((next_state, action))

        return neighbors

    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )

    def reconstruct_path(self, parents, actions, goal):

        path = []
        current = goal

        while parents[current] is not None:
            path.append(actions[current])
            current = parents[current]

        path.reverse()

        return path

    def bfs_search(self, start, goal, walls, grid_size):

        frontier = deque([start])
        reached = {start}

        parents = {
            start: None
        }

        actions = {}

        while frontier:

            current = frontier.popleft()

            if current == goal:
                return self.reconstruct_path(
                    parents,
                    actions,
                    goal
                )

            for next_state, action in self.get_neighbors(
                current,
                grid_size,
                walls
            ):

                if next_state not in reached:

                    reached.add(next_state)

                    parents[next_state] = current
                    actions[next_state] = action

                    frontier.append(next_state)

        return []

    def dfs_search(self, start, goal, walls, grid_size):

        frontier = [start]
        reached = {start}

        parents = {
            start: None
        }

        actions = {}

        while frontier:

            current = frontier.pop()

            if current == goal:
                return self.reconstruct_path(
                    parents,
                    actions,
                    goal
                )

            for next_state, action in self.get_neighbors(
                current,
                grid_size,
                walls
            ):

                if next_state not in reached:

                    reached.add(next_state)

                    parents[next_state] = current
                    actions[next_state] = action

                    frontier.append(next_state)

        return []

    def ucs_search(self, start, goal, walls, grid_size):

        frontier = []
        counter = 0

        heapq.heappush(
            frontier,
            (0, counter, start)
        )

        reached = {start}

        parents = {
            start: None
        }

        actions = {}

        costs = {
            start: 0
        }

        while frontier:

            current_cost, _, current = heapq.heappop(
                frontier
            )

            if current == goal:
                return self.reconstruct_path(
                    parents,
                    actions,
                    goal
                )

            for next_state, action in self.get_neighbors(
                current,
                grid_size,
                walls
            ):

                new_cost = current_cost + 1

                if (
                    next_state not in costs
                    or new_cost < costs[next_state]
                ):

                    costs[next_state] = new_cost

                    parents[next_state] = current
                    actions[next_state] = action

                    counter += 1

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            counter,
                            next_state
                        )
                    )

                    reached.add(next_state)

        return []

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        if heuristic_type == 'manhattan':
            heuristic = self.manhattan_distance
        elif heuristic_type == 'euclidean':
            heuristic = self.euclidean_distance
        else:
            raise ValueError(
                "heuristic_type must be 'manhattan' or 'euclidean'"
            )

        frontier = []
        counter = 0
        start_h = heuristic(start_pos, goal_pos)
        heapq.heappush(frontier, (start_h, 0, counter, start_pos, []))

        reached_states = set()
        best_costs = {start_pos: 0}

        while frontier:
            _, current_g, _, current_pos, path_taken = heapq.heappop(
                frontier
            )

            if current_pos in reached_states:
                continue

            if current_pos == goal_pos:
                return path_taken

            reached_states.add(current_pos)

            for next_pos, action in self.get_neighbors(
                current_pos,
                grid_size,
                walls
            ):
                if next_pos in reached_states:
                    continue

                new_g = current_g + 1
                if new_g < best_costs.get(next_pos, math.inf):
                    best_costs[next_pos] = new_g
                    new_h = heuristic(next_pos, goal_pos)
                    new_f = new_g + new_h
                    counter += 1
                    heapq.heappush(
                        frontier,
                        (
                            new_f,
                            new_g,
                            counter,
                            next_pos,
                            path_taken + [action]
                        )
                    )

        return []

    def find_closest_food(self, start, food_positions):

        if not food_positions:
            return None

        return min(
            food_positions,
            key=lambda food:
            abs(food[0] - start[0]) +
            abs(food[1] - start[1])
        )

    def sense_and_act(self, percept):

        if not self.plan:

            start = tuple(percept['agent_pos'])

            food_positions = [
                tuple(food)
                for food in percept['all_food']
            ]

            if not food_positions:
                return 'Stay'

            goal = self.find_closest_food(
                start,
                food_positions
            )

            grid_size = percept['grid_size']

            walls = {
                tuple(wall)
                for wall in percept['walls']
            }

            if self.active_algo == 'BFS':

                self.plan = self.bfs_search(
                    start,
                    goal,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'DFS':

                self.plan = self.dfs_search(
                    start,
                    goal,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'UCS':

                self.plan = self.ucs_search(
                    start,
                    goal,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(
                    start,
                    goal,
                    walls,
                    grid_size
                )

        if self.plan:
            return self.plan.pop(0)

        return 'Stay'
