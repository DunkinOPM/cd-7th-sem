
class GeneralizedAddressGenerator:

    def __init__(self):
        self.temp_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def generate(self, result):

        instructions = []

        base = result["base_address"]
        constant = result["CONSPART"]
        coefficients = result["VARPART_coefficients"]

        terms = []

        for variable, coefficient in coefficients.items():

            temp = self.new_temp()

            instructions.append(
                f"{temp} = {variable} * {coefficient}"
            )

            terms.append(temp)

        if constant != 0:
            terms.append(str(constant))

        if not terms:
            instructions.append(f"ADDRESS = {base}")
            return instructions

        current = terms[0]

        for term in terms[1:]:
            temp = self.new_temp()

            instructions.append(
                f"{temp} = {current} + {term}"
            )

            current = temp

        instructions.append(
            f"ADDRESS = {base} + {current}"
        )

        return instructions
