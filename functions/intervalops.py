"""
Custom library with functions useful for operations on intervals and sets.
"""


def getPowerSet(llist):
    """
    Get the power set (set of all subsets) of a given set.
    :param llist: input list (set)
    :return: power set
    """
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
    """
    Function that checks if two intervals overlap and if they do, merges them.
    Two intervals [a, b] and [c, d] overlap if e.g. a <= c <= b <= d.
    In that case, the function will return [ True, [a, d] ]
    :param interval1: first interval
    :param interval2: second interval
    :return: [ merge_successful, new_interval ]
    """
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
    """
    Merges all intervals that can be merged in a list of intervals, and returns a cleaned up list of intervals.
    :param list_of_intervals: original list of intervals
    :return: new list of intervals
    """
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
    """
    Checks if a given number belongs to one of the intervals in a list of intervals.
    :param number: number to be checked
    :param list_of_intervals: list of intervals
    :return: (boolean) whether the condition is True
    """
    belongs = False
    for interval in list_of_intervals:
        if interval[0] <= number <= interval[1]:
            belongs = True
            break
    return belongs



def addToPowerRange(old_power_range, new_element):
    """
    Useful for when a new power plant or a new set of power plants is taken into consideration.
    Will return a new global power range, with which e.g. we can check the compatibility of a given load.
    In more technical detail:
    Updates an old power range (list of intervals) when a new power range (list of intervals) is taken into consideration.
    The function first copies the old power range, then appends the new power range.
    Then it also appends all possible interval sums between one interval in the old range and one in the new range.
    Finally, it merges all intervals that can be merged.
    :param old_power_range: old power range
    :param new_element: new element to be added to the power range
    :return: increased power range
    """
    new_power_range = old_power_range.copy()
    for new_sub_range in new_element:
        new_power_range.append(new_sub_range)
        for old_sub_range in old_power_range:
            sum_min = old_sub_range[0] + new_sub_range[0]
            sum_max = old_sub_range[1] + new_sub_range[1]
            new_power_range.append([sum_min, sum_max])
    cleaned_power_range = mergeIntervalsInList(new_power_range)
    return cleaned_power_range



def getMaxPower(power_range):
    """
    Gets maximum number belonging to an ordered list of intervals.
    (Gets maximum power in a power range.)
    :param power_range: ordered list of intervals
    :return: maximum number
    """
    max_power = 0
    if len(power_range) > 0:
        last_element = power_range[-1]
        max_power = last_element[1]
    return max_power


def getMinPower(power_range):
    """
    Gets minimum number belonging to an ordered list of intervals.
    (Gets minimum power in a power range.)
    :param power_range: ordered list of intervals
    :return: minimum number
    """
    min_power = 0
    if len(power_range) > 0:
        first_element = power_range[0]
        min_power = first_element[0]
    return min_power


def reduceRangeBy(power_range, number):
    """
    Reduces by a given number the minimum and maximum boundaries of all intervals in a list of intervals.
    If the minimum and maximum would be set below zero, set them to zero instead.
    :param power_range: list of intervals
    :param number: number used to reduce the intervals
    :return: new list of intervals
    """
    subtracted_range = []
    for tmp_ran in power_range:
        sub_min = tmp_ran[0] - number
        if sub_min < 0: sub_min = 0
        sub_max = tmp_ran[1] - number
        if sub_max < 0: sub_max = 0
        
        subtracted_range.append([sub_min, sub_max])
    return subtracted_range
