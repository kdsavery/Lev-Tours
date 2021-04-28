# Building management v1.7

#Imports
import os
import math
import wifi_scanning as ws
import logger as log

#Constants
INFINITY = float('inf')
PRIMARY = 100
SECONDARY = 101
NO_CONNECTION = 110

# Management operations for storing building data
BD_DIRECTORY = "buildings"
BD_DIRECTORY = os.path.join(os.getcwd(), BD_DIRECTORY)
if(not os.path.isdir(BD_DIRECTORY)):
    os.mkdir(BD_DIRECTORY)

# Flag turning on or off Wi-Fi operations
WiFi_Enabled = True

# A Building object contains a dictionary of Floor objects for each floor's map
class Building:
    def __init__(self, name):
        self.name = name.lower()
        self.floors = {}
        self.floor_keys = []
        self.floor_maps = {}
        self.tours = {}

    # Add a new floor to the building map
    # Note: this function will overwrite a floor
    def add_floor(self, floor_num, floor_map, map_file):
        if(not isinstance(floor_map, Floor)):
            raise TypeError("'floor_map' must be Floor object")
        self.floors[floor_num] = floor_map
        self.floor_keys.append(floor_num)
        self.floor_keys.sort()
        self.floor_maps[floor_num] = map_file

        log.logging.info("New floor, " + floor_num + ", created in " + self.name)

    def remove(self, name):
        node_floor = self.get_floor(name)
        try:
            self.floors[node_floor].remove_node(name)
            return True
        except KeyError:
            return False

    def is_connected(self):
        for floor in self.floors:
            if(not self.floors[floor].is_connected()):
                return False
        return True

    #Check if passed node has wifi currently stored
    def has_wifi(self, nodename):
        if(nodename.wifi_data == []):
            return "NO"
        return "YES"

    # Return list of node names
    def get_names(self, floor=None):
        try:
            return self.floors[floor].names
        except KeyError:
            names = []
            for floor in self.floors:
                names += self.floors[floor].names
            return names

    def get_dist(self, nameone, nametwo):
        floor = self.get_floor(nameone)
        floor = self.floors[floor]
        indexone = floor.names.index(nameone)
        indextwo = floor.names.index(nametwo)
        return floor.weights[indexone][indextwo]

    def format_multiname(self, floor=None):
        nodes = self.get_nodes(floor)
        formatted_names = []
        for node in nodes:
            init = True
            if node.associated == []:
                formatted_names.append(node.name + " - No Rooms")
            else:
                for associated in node.associated:
                    if(init):
                        init = False
                        formatted_names.append(node.name + " - " + associated)
                    else:
                        formatted_names.append(len(node.name)*"  " + " - " + associated)

        return formatted_names

    def get_node_by_multiname(self, associated):
        for node in self.get_nodes():
            if(associated == node.name or associated in node.associated):
                return node
        return None

    def get_nodes_by_names(self, names):
        nodes = self.get_nodes()
        return_nodes = []
        for node in nodes:
            if(node.name in names):
                return_nodes.append(node)
        return return_nodes

    def get_trans_by_name(self, floor=None):
        transitions = []
        for node in self.get_nodes(floor):
            if(node.transition):
                transitions.append(node.name)
        return transitions

    def get_floor(self, name):
        curr_floor = None
        for floor in self.floors:
            if(name in self.get_names(floor)):
                curr_floor = floor
                break
        if(curr_floor == None):
            return False
        return curr_floor

    def set_edge(self, start, dest, distance):
        curr_floor = None
        for floor in self.floors:
            floor_names = self.get_names(floor)
            if(start in floor_names and dest in floor_names ):
                curr_floor = floor
                break
        if(curr_floor == None):
            raise NameError("'Start' and 'Dest' do not exist on the same floor")

        node_start = self.get_node(start)
        node_dest = self.get_node(dest)

        try:
            distance = float(distance)
        except ValueError:
            distance = INFINITY

        self.floors[curr_floor].add_edge(start, dest, distance)
        return True

    def get_edges(self, floors=None):
        if(floors == None):
            # Return every edge in the building
            floors = self.floor_keys
        elif(not floors in self.floor_keys):
            return False

        else:
            floors = list(floors)

        # Create list of nodes, adj nodes, and distances to sort
        edges = []
        seen = []
        for floor in floors:
            current_floor = self.floors[floor]
            for name in current_floor.names:
                seen.append(name)
                for adj in current_floor.connected_to(name):
                    if(adj in seen):
                        continue
                    node_index = current_floor.names.index(name)

                    adj_index = current_floor.names.index(adj)
                    dist = round(current_floor.weights[node_index][adj_index], 1)
                    edges.append(name + " <-> " + adj + ": " + str(dist) + " ft")
        return edges



    def dist(self, node_one, node_two):
        if(node_one.location == None or node_two.location == None):
            raise TypeError("Node location never initialized")
        loc_1 = node_one.location
        loc_2 = node_two.location
        return math.sqrt((loc_2[0]-loc_1[0])**2 + (loc_2[1]-loc_1[1])**2)

    # Return a list of all nodes in the building or a given floor
    def get_nodes(self, floor=None):
        try:
            return self.floors[floor].nodes
        except KeyError:
            nodes = []
            for floor in self.floors:
                nodes += self.floors[floor].nodes
        return nodes

    # Return a single node based on its name
    def get_node(self, name):
        for node in self.get_nodes():
            if(node.name == name):
                return node

    # Set directions in the building to display to the user
    # This called on load and save of a building
    # Nodes can only be left,right, or in front/behind of each other
    def set_directions(self):
        for floor in self.floors:
            curr_floor = self.floors[floor]
            nodes = self.get_nodes(curr_floor)
            for row in range(0, len(curr_floor.weights)):
                set_node = curr_floor.nodes[row]
                adj_directions = {}
                for col in range(0, len(curr_floor.weights)):
                    adj_edge = curr_floor.weights[row][col]

                    if(adj_edge > 0 and adj_edge < INFINITY):
                        from_node = curr_floor.nodes[col]

                        rise = (set_node.location[1]-from_node.location[1])
                        run = (set_node.location[0]-from_node.location[0])
                        if(run == 0.0):
                            slope = INFINITY
                        else:
                            slope = rise/run

                        # Determine if this adj node is above, below, left, or
                        # right in relation to the map
                        if(abs(slope) < 1.0):
                            if(from_node.location[0] > set_node.location[0]):
                                from_desc = "right"
                            else:
                                from_desc = "left"
                        else:
                            if(from_node.location[1] > set_node.location[1]):
                                from_desc = "below"
                            else:
                                from_desc = "above"
                        # Set up directions for orientation coming from
                        # this adjacent node
                        adj_directions[from_node.name] = {from_node.name: "back"}
                        for adj_index in range(0, len(curr_floor.weights)):

                            to_node = curr_floor.nodes[adj_index]

                            if(to_node.name == set_node.name
                                or to_node.name == from_node.name):
                                continue

                            adj_edge = curr_floor.weights[row][adj_index]

                            if(adj_edge > 0 and adj_edge < INFINITY):

                                rise = (set_node.location[1]-to_node.location[1])
                                run = (set_node.location[0]-to_node.location[0])
                                if(run == 0.0):
                                    slope = INFINITY
                                else:
                                    slope = rise/run

                                if(abs(slope) < 1.0):
                                    if(to_node.location[0] > set_node.location[0]):
                                        to_desc = "right"
                                    else:
                                        to_desc = "left"
                                else:
                                    if(to_node.location[1] > set_node.location[1]):
                                        to_desc = "below"
                                    else:
                                        to_desc = "straight"
                                # Reset direction to next node based off from_node
                                if(from_desc == "above"):
                                    if(to_desc == "right"):
                                        to_desc = "left"
                                    elif(to_desc == "left"):
                                        to_desc = "right"
                                    else:
                                        to_desc = "straight"
                                elif(from_desc == "right"):
                                    if(to_desc == "straight"):
                                        to_desc = "right"
                                    elif(to_desc == "below"):
                                        to_desc = "left"
                                    else:
                                        to_desc = "straight"
                                elif(from_desc == "left"):
                                    if(to_desc == "straight"):
                                        to_desc = "left"
                                    elif(to_desc == "below"):
                                        to_desc = "right"
                                    else:
                                        to_desc = "straight"
                                adj_directions[from_node.name][to_node.name] = to_desc
                set_node.add_directions(adj_directions)

    def next_direction(self, path, current):
        transitions = self.get_trans_by_name()

        if(path[current] == path[-1]):
            return "You have arrived at " + path[-1]
        elif(path[current] == path[0]):
            return "Proceed straight to " + path[current+1]
        elif(path[current] in transitions and
            not path[current-1] in transitions):
            return "Proceed into the elevator"
        elif(path[current] in transitions and
            not path[current+1] in transitions):
            return "Exit the elevator and proceed straight to " + path[current+1]
        else:
            prev = path[current-1]
            toward = path[current+1]
            current = path[current]
            current_node = self.get_node(current)

            description = current_node.adj_directions[prev][toward]
            if(description == "straight"):
                return "Continue straight to " + toward
            elif(description == "left"):
                return "Turn left and continue straight to " + toward
            elif(description == "right"):
                return "Turn right and continue straight to " + toward
            else:
                return "Turn around and continue straight to " + toward

    # Used to format each nodes info to work with initializeNodesinGUI in Gui.py
    def get_node_info(self, floor=None):
        node_info = []
        all_nodes = self.get_nodes(floor)
        for node in all_nodes:
            to_add = [node.name, node.location[0], node.location[1]]
            if(node.transition):
                to_add.append('t')
            elif(node.status == SECONDARY):
                to_add.append('s')
            else:
                to_add.append('p')
            node_info.append(to_add)
        return node_info

    # Get shortest path between any two points in the building
    def get_path(self, start, dest):
        start_floor_found = False
        dest_floor_found = False
        for floor_num in self.floors:
            floor_names = self.get_names(floor_num)
            if(start in floor_names):
                start_floor_found = True
                start_floor = floor_num
            if(dest in floor_names):
                dest_floor_found = True
                dest_floor = floor_num

        if(not start_floor_found):
            raise NameError("name 'Start' is not defined")
        if(not dest_floor_found):
            raise NameError("name 'Dest' is not defined")

        if(start_floor == dest_floor):
            return self.floors[start_floor].get_path(start, dest)

        # Get names of transition nodes on starting/destination floors
        # Functionality to choose transition node based on shortest
        # distance never implemented, simply chooses the first transition node found
        for node in self.get_nodes(start_floor):
            if(node.transition):
                transition_start = node.name
        for node in self.get_nodes(dest_floor):
            if(node.transition):
                transition_dest = node.name

        first_path = self.floors[start_floor].get_path(start, transition_start)
        second_path = self.floors[dest_floor].get_path(transition_dest, dest)

        return first_path + second_path


    def save_tours(self, folder_path, filename):
        tour_file = filename + "_tours" + ".txt"
        tour_file = os.path.join(folder_path, tour_file)
        with open(tour_file, 'w') as fh:
            for tour in self.tours:
                fh.write(str(tour) + "\n")
                for node in self.tours[tour]:
                    fh.write(str(node)+"\n")
                fh.write("END TOUR\n")
            fh.write("END TOURS")

    def load_tours(self, folder_path):
        tour_file = self.name + "_tours" + ".txt"
        tour_file = os.path.join(folder_path, tour_file)

        if(not tour_file == ""):
            try:
                fh = open(tour_file, 'r')
            except FileNotFoundError:
                return # No tours to load

            line = fh.readline().strip("\n")
            while(not line == "END TOURS"):
                # Get this tour's name
                tour_name = line
                self.tours[tour_name] = []

                line = fh.readline().strip("\n")
                while(not line == "END TOUR"):
                    # Get this tours locations
                    self.tours[tour_name].append(line)
                    line = fh.readline().strip("\n")
                line = fh.readline().strip("\n")

    # Write the state of this object to a file
    def save(self, filename):
        filename = filename.lower()
        for node in self.get_nodes():
            if(node.location == None):
                return False # This node has no location

        self.set_directions()

        # Save building data
        folder_path = self.file_helper(filename, True)
        for floor in self.floors:
            floor_file = filename + "_floor_" + floor + ".txt"
            floor_file = os.path.join(folder_path, floor_file)

            with open(floor_file, 'w') as fh:
                fh.write("Floor:" + floor + "\n")

                # Write node name, status, location, wifi-data, and any adj nodes
                for node in self.floors[floor].nodes:
                    fh.write(node.name + "/")

                    for associated in node.associated:
                        fh.write(associated + "/")

                    if(node.status == PRIMARY):
                        fh.write("PRIMARY/")
                    else:
                        fh.write("SECONDARY/")

                    fh.write(str(node.location[0]) + "/" + str(node.location[1]))

                    # If node is transition put TRANSITION after node data
                    if(node.transition):
                        fh.write("/TRANSITION\n")
                    else:
                        fh.write("\n")

                    # Writing this nodes Wi-Fi data
                    fh.write("[\n")
                    for ap in node.wifi_data:
                        fh.write(str(ap) + "\n")
                    fh.write("]\n")

                fh.write("END NODES\n")
                edges = self.floors[floor].get_edges()
                for edge in edges:
                    fh.write(edge + "\n")
                fh.write("END EDGES\n")
                fh.write(self.floor_maps[floor] + "\n")
                fh.write("END FLOOR DATA\n")

        # Save this buildings tour data
        self.save_tours(folder_path, filename)

        log.logging.info("Building: " + self.name + ", saved")
        return True


    # Initialize this object via a file created with save()
    def load(self, bldg_name):
        # Keys for reading in wifi data
        keys = ['mac', 'minSig', 'minQual', 'maxQual', 'maxSig', 'avgSig', 'qualAvg']

        # everything in storage is lower cased
        bldg_name = bldg_name.lower()

        # Get path to building's directory if it exists
        folder_path = self.file_helper(bldg_name, False)

        # Loop through all floors
        files = os.listdir(folder_path)
        files.sort()
        for floor in os.listdir(folder_path):
            # Check if file is a txt doc or not floor file
            if((not ".txt" in floor) or (not "_floor_" in floor)):
                continue

            split_floor = floor.split("_floor_")[0]
            if(not split_floor == bldg_name):
                continue

            floor_file = os.path.join(folder_path, floor)
            with open(floor_file, 'r') as fh:
                line = fh.readline().strip("\n")
                floor_num = line.split(":")[1]
                new_floor = Floor(floor_num)

                # Read data for each node in this floor
                node = fh.readline().strip("\n")
                while(not node == "END NODES"):
                    split_node = node.split("/")

                    wrk_index = 0
                    # Get this node's name
                    node_name = split_node[wrk_index]

                    # Get locations associated with this node
                    associated = []
                    wrk_index += 1
                    while(not (split_node[wrk_index] == "PRIMARY"
                        or split_node[wrk_index] == "SECONDARY")):
                        associated.append(split_node[wrk_index])
                        wrk_index += 1

                    # Determine if it is primary or secondary
                    node_status = PRIMARY
                    if(split_node[wrk_index] == "SECONDARY"):
                        node_status = SECONDARY

                    # Get its coordinates
                    wrk_index += 1
                    x = int(split_node[wrk_index])
                    wrk_index += 1
                    y = int(split_node[wrk_index])

                    new_node = Node(node_name, node_status, (x,y))
                    new_node.associated = associated
                    # Determine if this node is a transition
                    try:
                        wrk_index += 1
                        if(split_node[wrk_index] == "TRANSITION"):
                            new_node.transition = True
                    except IndexError:
                        pass # Node is not a transition by default

                    # READ IN WIFI DATA
                    wifi_data = []
                    line = fh.readline().strip("\n") # skip past "["
                    line = fh.readline().strip("\n")
                    while(not line == "]"):
                        ap = {}
                        for key in keys:
                            start = line.find(key) + len(key) + 2 # Skip to value for this key
                            end = line.find(",", start)
                            ap[key] = line[start:end].strip(" ").strip("'")
                        wifi_data.append(ap)
                        line = fh.readline().strip("\n")

                    new_node.wifi_data = wifi_data

                    # Add this new node
                    new_floor.add_node(new_node)

                    node = fh.readline().strip("\n")

                # Write data for each initialized edge
                edge = fh.readline().strip("\n")
                while(not edge == "END EDGES"):
                    split_edge = edge.split(" ")
                    name_one = split_edge[0]
                    name_two = split_edge[1]
                    weight = float(split_edge[2])
                    new_floor.add_edge(name_one, name_two, weight)
                    edge = fh.readline().strip("\n")

                # Retrieve this floors map's file path
                floor_img = fh.readline().strip("\n")
                self.add_floor(floor_num, new_floor, floor_img)
                floor_img = fh.readline().strip("\n")

        # Set up directions within the building based off node positions
        self.set_directions()

        # Load any tours for this building
        self.load_tours(folder_path)

        log.logging.info("Building: " + bldg_name + ", loaded")
        return True

    def file_helper(self, bldg_name, make):
        bldg_folder = os.path.join(BD_DIRECTORY, bldg_name)
        if(not os.path.isdir(bldg_folder)):
            if(make):
                os.mkdir(bldg_folder)
            else:
                log.logging.critical("File: " + bldg_folder + " does not exist. Failure to load")
                raise FileNotFoundError(bldg_name + " does not exist")
        return bldg_folder


# Represents a single location within the building
class Node:
    def __init__(self, name, status=PRIMARY, location=None):
        self.name = name
        self.associated = []
        self.status = status
        self.transition = False
        self.location = location
        self.wifi_data = []
        self.adj_directions = {}

    # Create an independent copy of this node
    def copy(self):
        copy_name = self.name
        copy_status = self.status
        copy_loc = self.location
        return Node(copy_name, copy_status, copy_loc)

    # Store a list of dictionaries for each scanned access point (AP)
    def scan_wifi(self):
        self.wifi_data = ws.setup_scans()

    def add_directions(self, directions):
        self.adj_directions = directions

    def set_loc(self, xy_loc):
        self.location = xy_loc

# Represents a floor within a building as an adjacency matrix
class Floor:
    def __init__(self, name):
        self.nodes = []
        self.names = []
        self.weights = []
        self.name = name

    def add_node(self, node):
        if(isinstance(node, Node) and not node.name in self.names):
            self.nodes.append(node)
            self.names.append(node.name)

            # Add an entry for the new node in each row
            for row in self.weights:
                row.append(INFINITY)

            # Add a new row for the new node
            self.weights.append([INFINITY] * (len(self.weights)+1))

            # Set distance from node to itself to 0
            self.weights[-1][-1] = 0

            return True

        return False

    # Specify edge weight for two nodes
    def add_edge(self, name_one, name_two, weight):
        if(name_one == name_two or weight <= 0):
            return False

        try:
            name_one_ind = self.names.index(name_one)
            name_two_ind = self.names.index(name_two)

        except ValueError:
            return False

        # Initialize the edge weight in the adj matrix
        self.weights[name_one_ind][name_two_ind] = weight
        self.weights[name_two_ind][name_one_ind] = weight

        return True

    def remove_edge(self, name_one, name_two):
        self.add_edge(name_one, name_two, INFINITY)

    def get_edges(self):
        edge_strs = []
        for row in range(0, len(self.weights)):
            for col in range(row, len(self.weights)):
                if(not row == col and self.weights[row][col] < INFINITY):
                    edge_strs.append(self.names[row]
                                     + " " + self.names[col]
                                     + " " + str(self.weights[row][col]))
        return edge_strs


    # Remove a node from the floor
    def remove_node(self, name):
        if(not name in self.names):
            return False

        # Remove the node
        index = self.names.index(name)
        self.names.pop(index)
        self.nodes.pop(index)
        self.weights.pop(index)
        for row in self.weights:
            row.pop(index)

        return True

    def is_connected(self):
        if(self.names == []):
            return True

        #General test for connectedness
        result = self.dijkstra(self.names[0])
        for dist_desc in result:
            # dist_desc[2] is the node taken to reach a given vertex
            # if it is NO_CONNECTION, there is no way to reach the vertex
            if(dist_desc[2] == NO_CONNECTION):
                return False
        return True

    # Return connected nodes to nodename
    def connected_to(self, nodename):
        result = []
        col = self.names.index(nodename)
        for row in range(0, len(self.weights)):
            if(self.weights[row][col] < INFINITY and not row == col):
                result.append(self.names[row])
        return result

    # Return the shortest path from start to dest
    def get_path(self, start, dest):
        if(not start in self.names or not dest in self.names):
            return False

        shortest_paths = self.dijkstra(start)
        # Work backwards from the dest to find the path from start
        path = [dest]
        current = dest
        while(not current == start):
            for dist_desc in shortest_paths:
                if(dist_desc[0] == current):
                    path.insert(0, dist_desc[2])
                    current = dist_desc[2]
        return path

    # Find shortest path tree using Dijkstra'a Algorithm
    def dijkstra(self, start):
        complete = []
        working = [] #[[node-name, dist-to, via-node]...]

        # Initialize working queue for all nodes
        for node_name in self.names:
            if(not node_name == start):
                working.append([node_name, INFINITY, NO_CONNECTION])

        # Execute the algorithm
        current = [start, 0, start]
        complete.append(current)
        while(len(working) > 0):
            prev_dist = current[1]
            row = self.names.index(current[0])
            for col, adj in enumerate(self.names):
                dist = self.weights[row][col]
                if(dist < INFINITY and dist > 0):
                    for dist_desc in working:
                        if(dist_desc[0] == adj and dist + prev_dist < dist_desc[1]):
                            working.remove(dist_desc)
                            dist_desc[1] = dist + prev_dist
                            dist_desc[2] = current[0]
                            placed = False
                            cmp_ind = 0
                            while(not placed):
                                if(cmp_ind == len(working) or dist_desc[1] < working[cmp_ind][1]):
                                    working.insert(cmp_ind, dist_desc)
                                    placed = True
                                cmp_ind += 1
            current = working.pop(0)
            complete.append(current)

        # Return the distance to each node, N, from start, along with the node
        # that should be taken to reach N
        return complete

# Supporting functions for the building/node/floor classes

# Return a tuple of all available buildings
def get_buildings():
    buildings = os.listdir(BD_DIRECTORY)
    for ind_bd, file in enumerate(buildings):
        buildings[ind_bd] = capitalize(file.lower())

    buildings.sort()
    return buildings

def capitalize(name):
    name = name.split(" ")
    full_word = ""
    for word in name:
        if(not word == "and" and not word == "the"):
            full_word += word[0].upper() + word[1:] + " "
        else:
            full_word += word + " "
    return full_word.strip()

def img_path(bldg_name, map_file):
    path = os.path.join(BD_DIRECTORY, bldg_name.lower())
    return os.path.join(path, map_file)
