# flask packages

# project resources

# external packages



class PowerPlant:
    """
    Template for a power plant as defined by the problem set.
    Intialise:  new_powerplant = PowerPlant(
		                            name,
		                            type,
                                            efficiency,
                                            pmin,
                                            pmax
                                           )
    """

    
    def __init__(self, name, ttype, efficiency, pmin, pmax):
        """
        Initialise PowerPlant object
        :param name: (str) power plant name
        :param ttype: (str) power plant type, must be one of 'gasfired', 'turbojet', 'windturbine'
        :param efficiency: (float) power plant efficiency, must verify 0 < efficiency <= 1
        :param pmin: (float) minimum power for the plant, must be positive
        :param pmax: (float) maximum power for the plant, must be positive and higher than pmin
        """
        self.name = name
        self.ttype = ttype
        self.efficiency = efficiency
        self.pmin = pmin
        self.pmax = pmax
        if (efficiency <= 0):
            self.pmin = 0
            self.pmax = 0
        self.p = 0

    def checkPower(self, power, wind_pc):
        """
        Check if the plant can supply this amount of power, given a wind percentage
        :param power: power to be checked
        :param wind_pc: wind percentage
        :return: (boolean) checkPower
        """
        allowed = False

        if self.ttype == "windturbine":
            wind_power = self.pmax * wind_pc/100
            if round(power, 1) == round(wind_power, 1):
                allowed = True
        elif (self.ttype == "gasfired" or self.ttype == "turbojet"):
            if round(power, 1) <= self.pmax and round(power, 1) >= self.pmin:
                allowed = True
        else:
            pass

        return allowed

    def setPower(self, power):
        """
        Set the power supplied to the plant to a given number.
        Only numbers between pmin and pmax are allowed
        :param power: power to be supplied
        :param wind_pc: wind percentage
        """
        power = round(power, 1)
        if round(self.pmin, 1) <= power <= round(self.pmax, 1):
            self.p = power
        else:
            print("Illegal power value") #raise error

    def setCost(self, cost):
        """
        Set the cost (per MWh) of the power plant.
        Only positive numbers are allowed.
        :param cost: cost to be set
        """
        if cost >=0:
            self.cost = cost
        else:
            print("Illegal (negative) cost value") #raise error

    def costPerMWh(self, gas_price, kerosine_price):
        """
        Get the cost per MWh of the plant, given fuel prices.
        :param gas_price: gas price
        :param kerosine_price: kerosine price
        :return: (float) cost per MWh
        """
        fuel_price = 0
        if self.ttype == "windturbine":
            fuel_price = 0
        elif self.ttype == "gasfired":
            fuel_price = gas_price
        elif self.ttype == "turbojet":
            fuel_price = kerosine_price
        else:
            pass #raise error
        cost = 0
        if self.efficiency > 0:
            cost = fuel_price/self.efficiency
        else:
            pass 
        return round(cost, 2)


    def getRange(self, wind_pc):
        """
        Get range of power that can effectively be supplied by the plant, given a wind percentage.
        For a windturbine type, this will differ for pmin and pmax.
        :param wind_pc: wind percentage
        :return: power range
        """
        if self.ttype == "windturbine":
            min_power = round(self.pmax * wind_pc/100, 1)
            max_power = min_power
        elif (self.ttype == "gasfired" or self.ttype == "turbojet"):
            min_power = round(self.pmin, 1)
            max_power = round(self.pmax, 1)
        else:
            pass #raise error

        power_range = {"min": min_power, "max":max_power}
        return power_range

    def setRange(self, rrange):
        """
        Set (by fiat) range of power that can effectively be supplied by the plant.
        There is no guarantee that this is compatible with pmin and pmax!
        :param rrange: power range to be set
        """
        if len(rrange) == 2:
            for boundary in rrange:
                boundary = round(boundary, 1)
            self.rrange = rrange
        else:
            print("Non-recognised range") #raise error
    

    

