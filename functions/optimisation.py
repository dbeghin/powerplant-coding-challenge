#internal packages
from models.powerplant import PowerPlant
import functions.intervalops as intervalops

# external packages
import logging


def makeListOfCostTiers(ordered_plants):
    """
    Function that groups together power plants with the same cost and returns a list of 'cost tiers'.
    Each 'cost tier' is itself a list of PowerPlant objects with the same cost
    :param ordered_plant: list of PowerPlant objects sorted by cost
    :return: list of cost tiers
    """
    plants_byCostTier = []
    last_costTier = []
    last_cost = -1
    for iPlant in range(0, len(ordered_plants)):
        cost = ordered_plants[iPlant].cost
        if iPlant == 0 or cost == last_cost:
            last_costTier.append(ordered_plants[iPlant])
            last_cost = cost
        else:
            plants_byCostTier.append(last_costTier)
            last_costTier = [ordered_plants[iPlant]]
            last_cost = cost
    plants_byCostTier.append(last_costTier)
    return plants_byCostTier



def getPowerRanges(plants_byTier, wind_pc):
    """
    Function that takes a list of cost tiers and the wind percentage, and returns allowed power ranges for each cost tier.
    Each cost tier may be composed of several plants, so the calculation of the allowed power range may not be trivial.
    :param plants_byTier: list of cost tiers
    :param wind_pc: wind percentage
    :return: power ranges by cost tier
    """
    power_ranges_byCostTier = []
    for iCostTier in range(0, len(plants_byTier)):
        power_range_sums = []
        for iPlant in range(0, len(plants_byTier[iCostTier])):
            power_range = plants_byTier[iCostTier][iPlant].getRange(wind_pc)
            power_range_sample = [ [power_range["min"], power_range["max"]] ]
            power_range_sums = intervalops.addToPowerRange(power_range_sums, power_range_sample)
        power_range_cleaned = intervalops.mergeIntervalsInList(power_range_sums)
        #power_range_cleaned = power_range_total
        power_ranges_byCostTier.append(power_range_cleaned)
    return power_ranges_byCostTier



def initialiseSol(nTiers):
    """
    Function that intialises the solution by tier with the proper format.
    The solution by tier is not supposed to be the final solution with power supplied by individual plants.
    Instead, it's the power supplied by each cost tier.
    :param nTiers: number of cost tiers
    :return: initialised solution by tier
    """
    tmp_dic = {
        "load": 0,
        "cost": 0
    }
    solution = {
        "globalcost": 0,
        "detailsbytier": []
    }
    for iTier in range(0, nTiers):
        solution["detailsbytier"].append(tmp_dic.copy())
    return solution


def tryGoldenPath(load, plants_byCostTier, power_ranges_byCostTier):
    """
    Function that tries to find the 'obvious' solution by tier.
    Returns a boolean telling whether a solution was found, and if so, the solution (by tier).
    The 'obvious' solution is to set as much power as possible on the cheaper tiers and only then move on to more expensive tiers.
    This may not be possible due to minimum power constraints.
    :param load: total load to be distributed 
    :param plants_byCostTier: list of plants by cost tier
    :param power_ranges_byCostTier: list of power ranges by cost tier
    :return: [ whether solution is found, solution by tier ]
    """
    done = False
    tmp_load = load
    nTiers = len(power_ranges_byCostTier)
    solution = initialiseSol(nTiers)
    global_cost = 0
    for iTier in range(0, nTiers):
        tmp_range = power_ranges_byCostTier[iTier]
        if intervalops.belongsToInterval(tmp_load, tmp_range):
            done = True
            cost = plants_byCostTier[iTier][0].cost * tmp_load
            global_cost += cost
            solution["detailsbytier"][iTier]["load"] = round(tmp_load, 1)
            solution["detailsbytier"][iTier]["cost"] = round(cost, 2)
            solution["globalcost"] = round(global_cost, 2)
            break
        elif tmp_load > intervalops.getMaxPower(tmp_range):
            tmp_load = tmp_load - intervalops.getMaxPower(tmp_range)
            cost = plants_byCostTier[iTier][0].cost * intervalops.getMaxPower(tmp_range)
            solution["detailsbytier"][iTier]["load"] = round(intervalops.getMaxPower(tmp_range), 1)
            solution["detailsbytier"][iTier]["cost"] = round(cost, 2)
        else:
            done = False
            break

    output = [done, solution]
    return output



def checkIfAllNeeded(load, subset, power_ranges_byCostTier):
    """
    Function that considers a subset of cost tiers, and checks if all of them can be used to supply a given load.
    It does so by distributing the load by giving the minimum possible power to each tier belonging to the subset.
    The power ranges of each tier are updated accordingly.
    If the remaining load is positive and can still be distributed to the updated power range, then all tiers can be used.
    :param load: total load to be distributed 
    :param subset: subset of tiers to be considered 
    :param power_ranges_byCostTier: power ranges for all cost tiers
    :return: (boolean) whether the tiers in the subset can all be used
    """
    all_needed = False
    tmp_load = load
    range_after_subtraction = []
    for iTier in subset:
        min_power = intervalops.getMinPower(power_ranges_byCostTier[iTier])
        if min_power < 0.1:
            min_power = 0.1
        tmp_load = tmp_load - min_power
        tmp_ran = intervalops.reduceRangeBy(power_ranges_byCostTier[iTier], min_power)
        range_after_subtraction = intervalops.addToPowerRange(range_after_subtraction, tmp_ran)
        
        
    if tmp_load >= 0 and intervalops.belongsToInterval(tmp_load, range_after_subtraction):
        all_needed = True
    return all_needed



def bruteForceSolution(load, subset, plants_byCostTier, power_ranges_byCostTier):
    """
    Function that searches for solutions by tier (like tryGoldenPath).
    This function considers a subset of cost tiers and searches for all possible solutions that make use of ALL cost tiers in the subset.
    A solution will assign a load and a cost for each tier, as well as calculating a global cost.
    The search for all possible solutions proceeds as follows:
    (1) Making a list of all possible interval combinations, with exactly one interval from each tier.
    Generically, the power range in each tier is a list of intervals rather than a single interval.
    However, the optimal load HAS to belong to only ONE of the intervals.
    (2) For each interval combination, check if a solution can be found using ALL intervals.
    (3) If that's possible, assign the minimum load to each interval.
    (4) Then assign the maximum load to intervals ordered by cheapness, until done.
    (5) Append solution to list of possible solutions.
    Then sort the solutions by cost and return cheapest.
    This will be the cheapest solution using ALL tiers in the subset.
    Attention: the function assumes the existence of a solution!
    :param load: total load to be distributed 
    :param subset: subset of tiers to be considered 
    :param plants_byCostTier: list of plants by cost tier
    :param power_ranges_byCostTier: list of power ranges by cost tier
    :return: cheapest solution using all tiers in the subset
    """
    nTiers = len(power_ranges_byCostTier)

    number_of_combinations = 1
    combinations = {}
    for iSub in range(0, len(subset)):
        iTier = subset[iSub]
        combinations[iTier] = [number_of_combinations, len(power_ranges_byCostTier[iTier])]
        number_of_combinations = number_of_combinations * len(power_ranges_byCostTier[iTier])

    list_of_solutions = []
    for iComb in range(0, number_of_combinations):
        tmp_interval_list = []
        for iTier in range(0, len(power_ranges_byCostTier)):
            if iTier in subset:
                divide = int(combinations[iTier][0])
                modulo = int(combinations[iTier][1])
                iInt = (iComb//divide) % modulo
                tmp_interval_list.append([power_ranges_byCostTier[iTier][iInt]])
            else:
                tmp_interval_list.append([])

        if not checkIfAllNeeded(load, subset, tmp_interval_list):
            continue
        else:
            solution = initialiseSol(nTiers)
            global_cost = 0
            tmp_load = load
            tmp_interval_after_subtraction = []
            for iTier in range(0, len(tmp_interval_list)):
                if len(tmp_interval_list[iTier]) == 0:
                    tmp_interval_after_subtraction.append([])
                else:
                    min_power = intervalops.getMinPower(tmp_interval_list[iTier])
                    tmp_load = tmp_load - min_power
                    tmp_load = round(tmp_load, 1)
                    cost = plants_byCostTier[iTier][0].cost * min_power
                    global_cost += cost
                    solution["detailsbytier"][iTier]["load"] = round(min_power, 1)
                    solution["detailsbytier"][iTier]["cost"] = round(cost, 2)
                    tmp_ran = intervalops.reduceRangeBy(tmp_interval_list[iTier], min_power)
                    tmp_interval_after_subtraction.append(tmp_ran)
            for iTier in range(0, len(tmp_interval_after_subtraction)):
                if len(tmp_interval_after_subtraction[iTier]) == 0:
                    continue
                else:
                    tmp_range = tmp_interval_after_subtraction[iTier]
                    if intervalops.belongsToInterval(tmp_load, tmp_range):
                        cost = plants_byCostTier[iTier][0].cost * tmp_load
                        global_cost += cost
                        solution["detailsbytier"][iTier]["load"] += tmp_load
                        solution["detailsbytier"][iTier]["load"] = round(solution["detailsbytier"][iTier]["load"], 1)
                        solution["detailsbytier"][iTier]["cost"] += cost
                        solution["detailsbytier"][iTier]["cost"] = round(solution["detailsbytier"][iTier]["cost"], 2)
                        solution["globalcost"] = round(global_cost, 2)
                        list_of_solutions.append(solution)
                        break
                    elif tmp_load > intervalops.getMaxPower(tmp_range):
                        tmp_load = tmp_load - intervalops.getMaxPower(tmp_range)
                        tmp_load = round(tmp_load, 1)
                        cost = plants_byCostTier[iTier][0].cost * intervalops.getMaxPower(tmp_range)
                        global_cost += cost
                        solution["detailsbytier"][iTier]["load"] += intervalops.getMaxPower(tmp_range)
                        solution["detailsbytier"][iTier]["load"] = round(solution["detailsbytier"][iTier]["load"], 1)
                        solution["detailsbytier"][iTier]["cost"] += cost
                        solution["detailsbytier"][iTier]["cost"] = round(solution["detailsbytier"][iTier]["cost"], 2)
                    else:
                        pass #this shouldn't happen
                        

    list_of_solutions = sorted(list_of_solutions, key=lambda s: s["globalcost"])
    return list_of_solutions[0]



def distributeLoadInEquivalentPlants(tier_load, plants, wind_pc):
    """
    Function that distributes a given load to a list of equivalent power plants (belonging to the same tier).
    It considers the power set of plants and tries to find a solution for each subset.
    When there is a solution, the search terminates and the function returns the subset for which a solution exists.
    The correct power is assigned to the PowerPlant objects in the solution subset.
    Attention: the function assumes the existence of a solution!
    :param tier_load: load to be distributed 
    :param plants: list of PowerPlant objects
    :param wind_pc: wind percentage
    :return: subset of power plants for which there is a solution
    """
    powerset_plants = intervalops.getPowerSet(plants)
    output_plants = []
    for subset in powerset_plants:
        tmp_range = []
        for plant in subset:
            range_dic = plant.getRange(wind_pc)
            range_list = [[range_dic["min"], range_dic["max"]]]
            plant.setRange(range_list[0])
            tmp_range = intervalops.addToPowerRange(tmp_range, range_list)

        tmp_load = tier_load
        if intervalops.belongsToInterval(tier_load, tmp_range):
            for plant in subset:
                min_power = plant.rrange[0]
                plant.setPower(min_power)
                tmp_load = tmp_load - plant.rrange[0]
                tmp_load = round(tmp_load, 1)
            if tmp_load < 0:
                continue
            else:
                for plant in subset:
                    if tmp_load > plant.rrange[1] - plant.rrange[0]:
                        plant.setPower(plant.rrange[1])
                        tmp_load = tmp_load - plant.rrange[1] + plant.rrange[0]
                        tmp_load = round(tmp_load, 1)
                    elif 0.1 <= tmp_load <= plant.rrange[1] - plant.rrange[0]:
                        plant.setPower(plant.rrange[0]+tmp_load)
                        output_plants = subset.copy()
                        break
                    elif 0 <= tmp_load < 0.1:
                        output_plants = subset.copy()
                        break
        if len(output_plants) > 0: break
    return output_plants
                    


def optimiseCheckForErrors(data):
    """
    Function that takes the raw JSON data and makes sure
    (1) It's in the proper format (variable types, dictionary keys)
    (2) Variables are in the allowed ranges
    If everything is fine, it returns the input data with no modification.
    Otherwise it returns an error message.
    :param data: input data
    :return: data or error
    """
    #check input format
    load = 0
    gas_price = 0
    kerosine_price = 0
    wind_pc = 0
    try:
        load = float(data["load"])
        gas_price = float(data["fuels"]["gas(euro/MWh)"])
        kerosine_price = float(data["fuels"]["kerosine(euro/MWh)"])
        wind_pc = float(data["fuels"]["wind(%)"])
    except KeyError:
        error_output = "Key error in payload. At least one of the 'load' or 'fuel' keys is wrong. Check JSON file."
        logging.error(error_output)
        return {"msg:": error_output}
    except TypeError:
        error_output = "Type error in payload. Got list when expecting dictionary or vice-versa. Check JSON file."
        logging.error(error_output)
        return {"msg:": error_output}
    except ValueError:
        error_output = "Value error in payload. Expecting floats in 'load' and 'fuel', but at least one of the values is not a float. Check JSON file."
        logging.error(error_output)
        return {"msg:": error_output}

    if load < 0 or gas_price < 0 or kerosine_price < 0:
        error_output = "Negative load or fuel price. Values must be >=0. Check JSON."
        logging.error(error_output)
        return {"msg:": error_output}
    if wind_pc < 0 or wind_pc > 100:
        error_output = "Wind percentage '%s' not valid. Value needs to be between 0 and 100. Check JSON."%wind_pc
        logging.error(error_output)
        return {"msg:": error_output}
        

    nPlants = 0
    try:
        nPlants = len(data["powerplants"])
    except KeyError:
        error_output = "Key error: can't find 'powerplants' entry. Check JSON file."
        logging.error(error_output)
        return {"msg:": error_output}
    except TypeError:
        error_output = "Type error in payload. Got list when expecting dictionary or vice-versa. Check JSON file."
        logging.error(error_output)
        return {"msg:": error_output}
    
        
    powerplants = []
    for iPlant in range(0, nPlants):
        try:
            tmp_powerplant = PowerPlant(
                str(data["powerplants"][iPlant]["name"]),
                str(data["powerplants"][iPlant]["type"]),
                float(data["powerplants"][iPlant]["efficiency"]),
                float(data["powerplants"][iPlant]["pmin"]),
                float(data["powerplants"][iPlant]["pmax"]),
            )
        except KeyError:
            error_output = "Key error in powerplant number %s. Check JSON file." %iPlant
            logging.error(error_output)
            return {"msg:": error_output}
        except TypeError:
            error_output = "Type error in payload. Got list when expecting dictionary or vice-versa. Check JSON file."
            logging.error(error_output)
            return {"msg:": error_output}
        except ValueError:
            error_output = "Value error in powerplant number %s. Check JSON file." %iPlant
            logging.error(error_output)
            return {"msg:": error_output}
        
        acceptable_types = ["gasfired", "turbojet", "windturbine"]
        if not tmp_powerplant.ttype in acceptable_types:
            error_output = "Type '%s' of power plant number %s not valid. Type needs to be one of %s. Check JSON file." %(tmp_powerplant.ttype, iPlant, acceptable_types)
            logging.error(error_output)
            return {"msg:": error_output}
        if tmp_powerplant.efficiency <= 0 or tmp_powerplant.efficiency > 1:
            error_output = "Efficiency '%s' of power plant number %s not valid. Value needs to be: 0 < '%s' <= 1. Check JSON file." %(tmp_powerplant.efficiency, iPlant, tmp_powerplant.efficiency)
            logging.error(error_output)
            return {"msg:": error_output}
        if tmp_powerplant.pmin < 0 or tmp_powerplant.pmax < 0 or tmp_powerplant.pmax < tmp_powerplant.pmin:
            error_output = "[pmin, pmax] = '[%s, %s]' of power plant number %s not valid. Both values need to be positive, and pmax >= pmin. Check JSON file." %(tmp_powerplant.pmin, tmp_powerplant.pmax, iPlant)
            logging.error(error_output)
            return {"msg:": error_output}

    #if everything is fine just return the data
    return data



def optimise(data_raw):
    """
    Function that takes the raw JSON data.
    If there is a formatting error, this information is passed through to the API interface.
    If not, the optimisation attempt starts.
    The PowerPlant objects are initialised, put on a list and ordered by cost.
    Then a list of cost tiers is established, with each tier containing a list of PowerPlant objects with the same cost per MWh.
    The global power range available is calculate and the function checks if the load is one of the allowed intervals.
    If not, an error is returned.
    If there is a solution, the function tries to find an obvious solution (see tryGoldenPath).
    If that's not possible, a search for all possible solutions starts.
    The power set of the cost tiers is obtained, and for each subset an allowed power range is calculated.
    For power ranges which contain the load as a solution, a brute force search for solutions is performed (see bruteForceSolution).
    The cheapest solution of each subset is appended to a list of possible solutions.
    Then the list of possible solutions is ordered by cost, and the cheapest is retained.
    The correct power is distributed to the PowerPlant objects in each tier of the solution.
    The JSON output is constructed and returned.
    :param data: input data
    :return: JSON solution or error
    """
    #check input format and value ranges
    data = optimiseCheckForErrors(data_raw)
    if "msg:" in data.keys():
        #return error message if any
        return data
    #now we're assured data is in the proper format
    
    load = float(data["load"])
    gas_price = float(data["fuels"]["gas(euro/MWh)"])
    kerosine_price = float(data["fuels"]["kerosine(euro/MWh)"])
    wind_pc = float(data["fuels"]["wind(%)"])
        

    nPlants = len(data["powerplants"])
    powerplants = []
    for iPlant in range(0, nPlants):
        tmp_powerplant = PowerPlant(
            str(data["powerplants"][iPlant]["name"]),
            str(data["powerplants"][iPlant]["type"]),
            float(data["powerplants"][iPlant]["efficiency"]),
            float(data["powerplants"][iPlant]["pmin"]),
            float(data["powerplants"][iPlant]["pmax"]),
        )
        cost = round(tmp_powerplant.costPerMWh(gas_price, kerosine_price), 2)
        tmp_powerplant.setCost(cost)
        powerplants.append(tmp_powerplant)
        

    #list of plants by cost
    ordered_plants = sorted(powerplants, key=lambda plant: plant.cost)

    #organisation by cost tiers (plants with same cost), range of power available for each tier
    plants_byCostTier = makeListOfCostTiers(ordered_plants)
    power_ranges_byCostTier = getPowerRanges(plants_byCostTier, wind_pc)
    

    power_ranges_bySubSet = {}
    subset_tiers = []
    tmp_pow_ran = []
    global_solution_flag = False
    for iTier in range(0, len(power_ranges_byCostTier)):
        subset_tiers.append(iTier)
        tmp_pow_ran = intervalops.addToPowerRange(tmp_pow_ran, power_ranges_byCostTier[iTier])
        tuple_subset = tuple(subset_tiers)
        power_ranges_bySubSet[tuple_subset] = tmp_pow_ran
        if intervalops.belongsToInterval(load, tmp_pow_ran):
            global_solution_flag = True

    logging.info("Load is '%s'. Available power range is '%s'", load, tmp_pow_ran)
    if not global_solution_flag:
        error_output = "Unable to distribute load. No solution found."
        logging.error(error_output)
        return {"msg:": error_output}

    global_solution_byCostTier = []
    golden_path = tryGoldenPath(load, plants_byCostTier, power_ranges_byCostTier)
    if golden_path[0]:
        global_solution_byCostTier = golden_path[1]
        logging.info("Found straightforward solution.")
    else:
        logging.info("Found no straightforward solution, brute forcing.")
        local_solutions = []
        powerset_tiers = intervalops.getPowerSet(subset_tiers)

        for subset in powerset_tiers:
            subset_tuple = tuple(subset)
            if not subset_tuple in power_ranges_bySubSet.keys():
                tmp_subset = subset.copy()
                last_sub = -1
                for iSub in range(1, len(subset)):
                    tmp_subset.pop()
                    tmp_tuple = tuple(tmp_subset)
                    if tmp_tuple in power_ranges_bySubSet.keys():
                        last_sub = iSub
                        break
                    
                if last_sub >= 1:
                    tmp_range = power_ranges_bySubSet[tmp_tuple]
                else:
                    tmp_range = []
                    last_sub = 0
                    
                for iSub in range(last_sub, len(subset)):
                    iTier = subset[iSub]
                    tmp_range = intervalops.addToPowerRange(tmp_range, power_ranges_byCostTier[iTier])

                power_ranges_bySubSet[subset_tuple] = tmp_range


            if intervalops.belongsToInterval(load, power_ranges_bySubSet[subset_tuple]):
                if not checkIfAllNeeded(load, subset, power_ranges_byCostTier):
                    continue
                else:
                    tmp_loc_sol = bruteForceSolution(load, subset, plants_byCostTier, power_ranges_byCostTier)
                    local_solutions.append(tmp_loc_sol)
                    

        local_solutions = sorted(local_solutions, key=lambda s: s["globalcost"])
        global_solution_byCostTier = local_solutions[0]

    logging.info("Solution total cost: %s", global_solution_byCostTier["globalcost"])
    logging.info("Solution details by cost tier: %s", global_solution_byCostTier["detailsbytier"])
    
    output_list = []
    for iTier in range(0, len(global_solution_byCostTier["detailsbytier"])):
        tier_load = global_solution_byCostTier["detailsbytier"][iTier]["load"]
        tmp_plants = distributeLoadInEquivalentPlants(tier_load, plants_byCostTier[iTier], wind_pc)

        for plant in plants_byCostTier[iTier]:
            output_element = {}
            if plant in tmp_plants:
                output_element = {
                    "name": plant.name,
                    "p": plant.p
                }
            else:
                output_element = {
		    "name": plant.name,
                    "p": 0
                }
            output_list.append(output_element.copy())

    return output_list
