import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    
    # make 'large' the default directory
    directory = sys.argv[1] if len(sys.argv) == 2 else "large" 

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # get starting node, with parent None and no action
    node = Node(source, None, None)

    # initialize frontier as a queue for BFS
    frontier = QueueFrontier()

    # add the starting node to the frontier
    frontier.add(node)

    # explored is the set of nodes that have been explored by the algo
    explored = set()

    while True:
        
        # if frontier is empty, no path exists (all paths exhausted)
        if frontier.empty():
            return None
        
        # remove the "last-in" (oldest) node from the frontier
        node = frontier.remove()

        # add that node to the explored set
        explored.add(node)

        # get all the neighbors of the removed node
        # neighbors is a list of (movie_id, person_id pairs)
        neighbors = neighbors_for_person(node.state)
        
        # state -> person, movie -> action
        for movie, person in neighbors:

            # if the person node hasn't been explored yet and
            # is not present in the frontier (due to removal)
            if person not in explored and not frontier.contains_state(person):

                # get the child node (neighbor to parent)
                child = Node (state=person, parent=node, action=movie)

                # check if the node is the target and then return path
                # before adding to frontier
                # this speeds up the algo, significantly
                if child.state == target:
                    path = []

                    # if child doesn't have a parent
                    # it must be the parent/root/source node
                    # so loop until parent is None
                    while child.parent is not None:

                        # path is a list of (action, state) pairs
                        path.append((child.action, child.state))
                        child = child.parent

                    # we went from target to source; so reverse (in-place)
                    path.reverse()
                    return path
                
                # if child is not the target, add it to the 
                frontier.add(child)       


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """

    # get the names (keys) from names as a set and cast to list
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
