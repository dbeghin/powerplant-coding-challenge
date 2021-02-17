from models.powerplant import PowerPlant

# external packages
import json


def sortByCost(powerplant):
    return powerplant.cost


def makeListOfCostTiers(ordered_plants):
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



def getPowerSet(llist):
    power_set_size = pow(2, len(llist))
    
    power_set=[]
    for iPower in range(1, power_set_size):
        subset = []
        for iSet in range(0, len(llist)):
            if (iPower & (1 << iSet)) > 0:
                subset.append(llist[iSet])
        if subset != []: power_set.append(subset)
    return power_set



def mergeIntervals(interval1, interval2):
    interval_out = []
    merge_successful = False
    lmin = 0
    rmin = 0
    lmax = 0
    rmax = 0
    if interval1[0] <= interval2[0]:
        lmin = interval1[0]
        rmin = interval1[1]
        lmax = interval2[0]
        rmax = interval2[1]
    else:
        lmin = interval2[0]
        rmin = interval2[1]
        lmax = interval1[0]
        rmax = interval1[1]

    if lmin <= lmax <= rmin <= rmax:
        interval_out = [lmin, rmax]
        merge_successful = True
    elif lmin <= lmax <= rmax <= rmin:
        interval_out = [lmin, rmin]
        merge_successful = True
    else:
        merge_successful = False

    output = [merge_successful, interval_out]
    return output


def mergeIntervalsInList(list_of_intervals):
    list_cleaned = []
    list_copy=list_of_intervals.copy()
    iInd1 = 0
    while iInd1 < len(list_copy):
        interval1 = list_copy[iInd1]
            
        iInd2 = iInd1 + 1
        bMerge = False
        while iInd2 < len(list_copy):
            interval2 = list_copy[iInd2]
            merging = mergeIntervals(interval1, interval2)

            if merging[0]:
                list_copy[iInd1] = merging[1]
                list_copy.pop(iInd2)
                bMerge = True
                break
            else:
                iInd2 += 1

        if not bMerge or iInd1 == len(list_copy)-1:
            list_cleaned.append(list_copy[iInd1])
            iInd1 += 1
    list_cleaned = sorted(list_cleaned, key=lambda r: r[0])
    return list_cleaned


def belongsToInterval(number, list_of_intervals):
    belongs = False
    for interval in list_of_intervals:
        if interval[0] <= number <= interval[1]:
            belongs = True
            break
    return belongs



def addToPowerRange(old_power_range, new_element):
    new_power_range = old_power_range.copy()
    for new_sub_range in new_element:
        new_power_range.append(new_sub_range)
        for old_sub_range in old_power_range:
            sum_min = old_sub_range[0] + new_sub_range[0]
            sum_max = old_sub_range[1] + new_sub_range[1]
            new_power_range.append([sum_min, sum_max])
    cleaned_power_range = mergeIntervalsInList(new_power_range)
    return cleaned_power_range


def getPowerRanges(plants_byTier, wind_pc):
    power_ranges_byCostTier = []
    for iCostTier in range(0, len(plants_byTier)):
        power_range_sums = []
        for iPlant in range(0, len(plants_byTier[iCostTier])):
            power_range = plants_byTier[iCostTier][iPlant].getRange(wind_pc)
            power_range_sample = [ [power_range["min"], power_range["max"]] ]
            power_range_sums = addToPowerRange(power_range_sums, power_range_sample)
        power_range_cleaned = mergeIntervalsInList(power_range_sums)
        #power_range_cleaned = power_range_total
        power_ranges_byCostTier.append(power_range_cleaned)
    return power_ranges_byCostTier



def getMaxPower(power_range):
    max_power = 0
    if len(power_range) > 0:
        last_element = power_range[-1]
        max_power = last_element[1]
    return max_power


def getMinPower(power_range):
    min_power = 0
    if len(power_range) > 0:
        first_element = power_range[0]
        min_power = first_element[0]
    return min_power


def initialiseSol(nTiers):
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
    done = False
    tmp_load = load
    nTiers = len(power_ranges_byCostTier)
    solution = initialiseSol(nTiers)
    global_cost = 0
    for iTier in range(0, nTiers):
        tmp_range = power_ranges_byCostTier[iTier]
        if belongsToInterval(tmp_load, tmp_range):
            done = True
            cost = plants_byCostTier[iTier][0].cost * tmp_load
            global_cost += cost
            solution["detailsbytier"][iTier]["load"] = round(tmp_load, 1)
            solution["detailsbytier"][iTier]["cost"] = round(cost, 2)
            solution["globalcost"] = round(global_cost, 2)
            break
        elif tmp_load > getMaxPower(tmp_range):
            tmp_load = tmp_load - getMaxPower(tmp_range)
            cost = plants_byCostTier[iTier][0].cost * getMaxPower(tmp_range)
            solution["detailsbytier"][iTier]["load"] = round(getMaxPower(tmp_range), 1)
            solution["detailsbytier"][iTier]["cost"] = round(cost, 2)
        else:
            done = False
            break

    output = [done, solution]
    return output



def reduceRangeBy(power_range, number):
    subtracted_range = []
    for tmp_ran in power_range:
        sub_min = tmp_ran[0] - number
        if sub_min < 0: sub_min = 0
        sub_max = tmp_ran[1] - number
        if sub_max < 0: sub_max = 0
        
        subtracted_range.append([sub_min, sub_max])
    return subtracted_range


def checkIfAllNeeded(load, subset, power_ranges_byCostTier):
    all_needed = False
    tmp_load = load
    range_after_subtraction = []
    for iTier in subset:
        min_power = getMinPower(power_ranges_byCostTier[iTier])
        if min_power < 0.1:
            min_power = 0.1
        tmp_load = tmp_load - min_power
        tmp_ran = reduceRangeBy(power_ranges_byCostTier[iTier], min_power)
        range_after_subtraction = addToPowerRange(range_after_subtraction, tmp_ran)
        
        
    if tmp_load >= 0 and belongsToInterval(tmp_load, range_after_subtraction):
        all_needed = True
    return all_needed


def bruteForceSolution(load, subset, plants_byCostTier, power_ranges_byCostTier):
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
            for iTier in range(0, len(tmp_interval_list)):
                if len(tmp_interval_list[iTier]) == 0:
                    continue
                else:
                    tmp_range = tmp_interval_list[iTier]
                    if belongsToInterval(tmp_load, tmp_range):
                        done = True
                        cost = plants_byCostTier[iTier][0].cost * tmp_load
                        global_cost += cost
                        solution["detailsbytier"][iTier]["load"] = round(tmp_load, 1)
                        solution["detailsbytier"][iTier]["cost"] = round(cost, 2)
                        solution["globalcost"] = round(global_cost, 2)
                        list_of_solutions.append(solution)
                        break
                    elif tmp_load > getMaxPower(tmp_range):
                        tmp_load = tmp_load - getMaxPower(tmp_range)
                        cost = plants_byCostTier[iTier][0].cost * getMaxPower(tmp_range)
                        solution["detailsbytier"][iTier]["load"] = round(getMaxPower(tmp_range), 1)
                        solution["detailsbytier"][iTier]["cost"] = round(cost, 2)
                    else:
                        pass #this shouldn't happen
                        

    list_of_solutions = sorted(list_of_solutions, key=lambda s: s["globalcost"])
    return list_of_solutions[0]



def distributeLoadInEquivalentPlants(tier_load, plants, wind_pc):
    powerset_plants = getPowerSet(plants)
    output_plants = []
    for subset in powerset_plants:
        tmp_range = []
        for plant in subset:
            range_dic = plant.getRange(wind_pc)
            range_list = [[range_dic["min"], range_dic["max"]]]
            plant.setRange(range_list[0])
            tmp_range = addToPowerRange(tmp_range, range_list)

        tmp_load = tier_load
        if belongsToInterval(tier_load, tmp_range):
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
                    

def optimise(data_json):
    #data = json.loads(data_json)
    data = data_json

    load = data["load"]
    gas_price = data["fuels"]["gas(euro/MWh)"]
    kerosine_price = data["fuels"]["kerosine(euro/MWh)"]
    wind_pc = data["fuels"]["wind(%)"]

    powerplants = []
    
    for iPlant in range(0, len(data["powerplants"])):
        tmp_powerplant = PowerPlant(
            data["powerplants"][iPlant]["name"],
            data["powerplants"][iPlant]["type"],
            data["powerplants"][iPlant]["efficiency"],
            data["powerplants"][iPlant]["pmin"],
            data["powerplants"][iPlant]["pmax"],
        )

        cost = round(tmp_powerplant.costPerMWh(gas_price, kerosine_price), 2)
        tmp_powerplant.setCost(cost)
        powerplants.append(tmp_powerplant)

        
    #list of plants by cost
    ordered_plants = sorted(powerplants, key=lambda p: sortByCost(p))

    #organisation by cost tiers (plants with same cost), range of power available for each tier
    plants_byCostTier = makeListOfCostTiers(ordered_plants)
    power_ranges_byCostTier = getPowerRanges(plants_byCostTier, wind_pc)
    

    power_ranges_bySubSet = {}
    subset_tiers = []
    tmp_pow_ran = []
    global_solution_flag = False
    for iTier in range(0, len(power_ranges_byCostTier)):
        subset_tiers.append(iTier)
        tmp_pow_ran = addToPowerRange(tmp_pow_ran, power_ranges_byCostTier[iTier])
        tuple_subset = tuple(subset_tiers)
        power_ranges_bySubSet[tuple_subset] = tmp_pow_ran
        if belongsToInterval(load, tmp_pow_ran):
            global_solution_flag = True

    print(tmp_pow_ran)
    if not global_solution_flag:
        return ["unable to distribute load"]

    global_solution_byCostTier = []
    golden_path = tryGoldenPath(load, plants_byCostTier, power_ranges_byCostTier)
    if golden_path[0]:
        global_solution_byCostTier = golden_path[1]
    else:
        local_solutions = []
        powerset_tiers = getPowerSet(subset_tiers)

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
                    tmp_range = addToPowerRange(tmp_range, power_ranges_byCostTier[iTier])

                power_ranges_bySubSet[subset_tuple] = tmp_range


            if belongsToInterval(load, power_ranges_bySubSet[subset_tuple]):
                if not checkIfAllNeeded(load, subset, power_ranges_byCostTier):
                    continue
                else:
                    tmp_loc_sol = bruteForceSolution(load, subset, plants_byCostTier, power_ranges_byCostTier)
                    local_solutions.append(tmp_loc_sol)
                    

        local_solutions = sorted(local_solutions, key=lambda s: s["globalcost"])
        global_solution_byCostTier = local_solutions[0]

    output_list = []
    print(global_solution_byCostTier)
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