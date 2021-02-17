# flask packages

# project resources
#from models.meals import Meals

# external packages



class PowerPlant:
    def __init__(self, name, ttype, efficiency, pmin, pmax):
        self.name = name
        self.ttype = ttype
        self.efficiency = efficiency
        self.pmin = pmin
        self.pmax = pmax
        self.p = 0

    def checkPower(self, power, wind_pc):
        allowed = False

        if self.ttype == "windturbine":
            wind_power = self.pmax * wind_pc/100
            if round(power, 1) == round(wind_power, 1):
                allowed = True
        elif (self.ttype == "gasfired" or self.ttype == "turbojet"):
            if round(power, 1) <= self.pmax and round(power, 1) >= self.pmin:
                allowed = True
        else:
            pass #raise error

        return allowed

    def setPower(self, power):
        power = round(power, 1)
        if round(self.pmin, 1) <= power <= round(self.pmax, 1):
            self.p = power
        else:
            print("Illegal power value") #raise error

    def setCost(self, cost):
        if cost >=0:
            self.cost = cost
        else:
            print("Illegal (negative) cost value") #raise error

    def costPerMWh(self, gas_price, kerosine_price):
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
        return round(cost, 2)


    def getRange(self, wind_pc):
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
        if len(rrange) == 2:
            for boundary in rrange:
                boundary = round(boundary, 1)
            self.rrange = rrange
        else:
            print("Non-recognised range") #raise error
    

    

