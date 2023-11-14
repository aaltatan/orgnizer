import math
import json
import datetime
from multiprocessing import Pool
from typing import List


class Taxes:
    def __init__(self, ordinance: str, min_rate: float) -> None:
        self.MIN_RATE = min_rate
        self.ordinance = ordinance
        with open("tax/layers.json", "r") as f:
            file = json.load(f)
        self.layers = file

    def layers_tax(self, salary: int) -> int:
        tax = 0
        for x in self.layers[self.ordinance]["ordinance"].keys():
            if salary > int(x):
                tax = (
                    (salary - int(x)) * self.layers[self.ordinance]["ordinance"][x][0]
                ) + self.layers[self.ordinance]["ordinance"][x][1]
                return int(math.ceil(tax / 100) * 100)

        return int(math.ceil(tax / 100) * 100)

    def gross_fixed_salary(self, salary: int) -> int:
        if self.layers_tax(salary=salary) == 0:
            return int(round(salary, 0))

        min_salary = salary
        max_salary = round(salary * 1.5, 0)

        while True:
            mid_salary = round((min_salary + max_salary) / 2, 0)
            mid_net_salary = mid_salary - self.layers_tax(mid_salary)

            if mid_net_salary > salary:
                max_salary = mid_salary
            elif mid_net_salary < salary:
                min_salary = mid_salary
            else:
                return int(round(mid_salary, 0))

    def gross_salary(self, target_salary: int, rate: float) -> int:
        fixed_salary = round(target_salary * (1 - rate), 0)
        components = round(target_salary * rate, 0)

        gross_fixed_salary = self.gross_fixed_salary(fixed_salary)
        components = int(
            round(components * self.layers[self.ordinance]["one_time_rate_fr"], 0)
        )
        total = gross_fixed_salary + components

        components_rate = round((gross_fixed_salary / total) * 100, 2)

        layers_tax = self.layers_tax(gross_fixed_salary)
        one_time_tax = int(
            round(components * self.layers[self.ordinance]["one_time_rate"], 0)
        )
        taxes_total = layers_tax + one_time_tax

        net_salary = total - taxes_total

        return (
            gross_fixed_salary,
            components,
            gross_fixed_salary + components,
            components_rate,
            layers_tax,
            one_time_tax,
            taxes_total,
            net_salary,
        )

    def rate_sequence(self, salary):
        # with Pool() as exe:
        #     return exe.map(self.gross_salary, [(salary, (rate / 400)) for rate in range(400)])
        return (self.gross_salary(salary, (rate / 400)) for rate in range(400))

    def best_salary(self, salary):
        best_sal = [
            sal
            for sal in self.rate_sequence(salary=salary)
            if sal[0] > self.layers[self.ordinance]["min_sal"]
            and (sal[0] / sal[2]) > self.MIN_RATE
        ]
        if not best_sal:
            return self.gross_salary(salary, 0)
        return min(best_sal, key=lambda x: x[2])

    def all_sequence(self, min_sal, max_sal, step) -> List[tuple]:
        with Pool() as exe:
            return exe.map(self.best_salary,[salary for salary in range(min_sal,max_sal + step,step)])
    

if __name__ == "__main__":

    tax = Taxes("30",0.25)
    start = datetime.datetime.now()

    step = 25_000

    all =  tax.all_sequence(500_000,20_000_000 + 50_000,step)

    end =  datetime.datetime.now() - start

    print(f"{end = }")
        
