import json

import requests
from decouple import config
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from orders.models import Order


def create_distance_matrix(cluster, now):
    api_key = config('GM_API_KEY')
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_lat}%2C{origin_long}&destinations="
    # the google distance matrix api is in this form
    # url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key=YOUR_API_KEY"
    orders = Order.objects.filter(
        cluster=cluster, status='created', created_date__lt=now).order_by('id')

    # creating a list with all locations that has to be covered by the rider
    locations = [order.location for order in orders]

    origin = cluster.location
    # inserting the depot (ie. the starting point of the ride) location to the list of points that has to be covered at the first position
    locations.insert(0, origin)
    # google matrix api destinations are bounded to 25 destinations per request
    # so we have to repeat sending requests until every destination is been included in the request
    points_to_cover = len(locations)
    req_dest_limit = 25
    reps = points_to_cover // req_dest_limit
    remainder = points_to_cover % req_dest_limit
    distance_matrix = [[] for y in range(points_to_cover)]
    # this set of nested for loop for including every destination as origin
    for rep in range(0, reps):
        for i in range(rep*req_dest_limit, (rep+1)*req_dest_limit):
            origin = locations[i]
            origin_lat, origin_long = origin.split(',')
            # this set of for loop is to include every location as the destination in the google maps distance matrix api
            for ite in range(0, reps):
                ind_url = url.format(origin_lat=origin_lat,
                                     origin_long=origin_long)
                for j in range(ite*req_dest_limit, (ite+1)*req_dest_limit):
                    destination = locations[j]
                    destination_lat, destination_long = destination.split(',')
                    ind_url += (destination_lat + "%2C" + destination_long)
                    if j != (ite+1)*req_dest_limit - 1:
                        ind_url += "%7C"
                ind_url += '&key={}'.format(api_key)

                # send a request at this point with an origin and a set of destinations
                response = requests.request(url=ind_url, method='GET')
                res_text = response.text
                res_dict = json.loads(res_text)
                distance_array = []
                for result in res_dict['rows'][0]['elements']:
                    distance = result['distance']['text'][:-3]
                    distance_array.append(
                        (float(distance)*1000) if distance != '' else 0)
                # save the data from the response in the distance matrix
                distance_matrix[i].extend(distance_array)

            # to include the remaining locations as destinations which doesn't comes in the repetition loop
            if remainder:
                ind_url = url.format(origin_lat=origin_lat,
                                     origin_long=origin_long)
                for rem in range((ite+1)*req_dest_limit, ((ite+1)*req_dest_limit)+remainder):
                    destination = locations[rem]
                    destination_lat, destination_long = destination.split(',')
                    ind_url += (destination_lat + "%2C" + destination_long)
                    if j != ((ite+1)*req_dest_limit)+remainder-1:
                        ind_url += "%7C"
                ind_url += '&key={}'.format(api_key)

                # send a request at this point with an origin and a set of destinations
                response = requests.request(url=ind_url, method='GET')
                res_text = response.text
                res_dict = json.loads(res_text)
                distance_array = []
                for result in res_dict['rows'][0]['elements']:
                    distance = result['distance']['text'][:-3]
                    distance_array.append(
                        (float(distance)*1000) if distance != '' else 0)
                # save the data from the response in the distance matrix
                distance_matrix[i].extend(distance_array)

    if remainder:
        if reps == 0:
            rep = 0
        else:
            rep += 1

        for i in range(rep*req_dest_limit, rep*req_dest_limit + remainder):
            origin = locations[i]
            origin_lat, origin_long = origin.split(',')
            # this set of for loop is to include every location as the destination in the google maps distance matrix api
            for ite in range(0, reps):
                ind_url = url.format(origin_lat=origin_lat,
                                     origin_long=origin_long)
                for j in range(ite*req_dest_limit, (ite+1)*req_dest_limit):
                    destination = locations[j]
                    destination_lat, destination_long = destination.split(',')
                    ind_url += (destination_lat + "%2C" + destination_long)
                    if j != (ite+1)*req_dest_limit - 1:
                        ind_url += "%7C"
                ind_url += '&key={}'.format(api_key)

                # send a request at this point with an origin and a set of destinations
                response = requests.request(url=ind_url, method='GET')
                res_text = response.text
                res_dict = json.loads(res_text)
                distance_array = []
                for result in res_dict['rows'][0]['elements']:
                    distance = result['distance']['text'][:-3]
                    distance_array.append(
                        (float(distance)*1000) if distance != '' else 0)
                # save the data from the response in the distance matrix
                distance_matrix[i].extend(distance_array)

            # to include the remaining locations as destinations which doesn't comes in the repetition loop
            ind_url = url.format(origin_lat=origin_lat,
                                 origin_long=origin_long)
            if reps == 0:
                ite = 0
            else:
                ite += 1
            for rem in range((ite)*req_dest_limit, ((ite)*req_dest_limit)+remainder):
                destination = locations[rem]
                destination_lat, destination_long = destination.split(',')
                ind_url += (destination_lat + "%2C" + destination_long)
                if rem != ((ite)*req_dest_limit)+remainder-1:
                    ind_url += "%7C"
            ind_url += '&key={}'.format(api_key)

            # send a request at this point with an origin and a set of destinations
            response = requests.request(url=ind_url, method='GET')
            res_text = response.text
            res_dict = json.loads(res_text)
            distance_array = []
            for result in res_dict['rows'][0]['elements']:
                distance = result['distance']['text'][:-3]
                distance_array.append(
                    (float(distance)*1000) if distance != '' else 0)
            # save the data from the response in the distance matrix
            distance_matrix[i].extend(distance_array)

    return distance_matrix


def create_data_model(cluster, now):
    """Stores the data for the problem."""
    data = {}
    distance_matrix = create_distance_matrix(cluster, now)

    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""

    # print(f'Objective: {solution.ObjectiveValue()}')
    # max_route_distance = 0
    routes = {}
    for vehicle_id in range(data['num_vehicles']):
        routes[vehicle_id] = {'path': []}
        index = routing.Start(vehicle_id)
        # plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        index = solution.Value(routing.NextVar(index))
        while not routing.IsEnd(index):
            routes[vehicle_id]['path'].extend([index])
            # plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        # plan_output += '{}\n'.format(manager.IndexToNode(index))
        # plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        routes[vehicle_id]['distance'] = route_distance
        # print(plan_output)
        # max_route_distance = max(route_distance, max_route_distance)
    # print('Maximum of the route distances: {}m'.format(max_route_distance))
    print(routes)
    return routes


def main(cluster, now):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(cluster, now)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        300000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    # Print solution on console.
    if solution:
        routes = print_solution(data, manager, routing, solution)
    else:
        routes = None
    return routes
