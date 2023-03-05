parameters_meanings = {"temperature": "Temperature",
                       "frequency_penalty": "Frequency penalty", "presence_penalty": "Presence penalty"}


def get_parameter_values(parameter):
    parameter_values = []
    if parameter == "temperature":
        parameter_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                            1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2]
    elif parameter == "frequency_penalty":
        parameter_values = [-2.0, -1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0,
                            -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,
                            0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                            1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    elif parameter == "presence_penalty":
        parameter_values = [-2.0, -1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0,
                            -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,
                            0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                            1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    else:
        print("got wrong parameter")
    return parameter_values


def get_next_value_and_action(operator, value, parameter):
    parameter_values = get_parameter_values(parameter)
    what_to_return = []
    if operator == "plus":
        element_position = parameter_values.index(value) + 1
        if element_position < len(parameter_values) - 1:
            what_to_return.append(parameter_values[element_position])
            what_to_return.append("regular")
        else:
            what_to_return.append(parameter_values[element_position])
            what_to_return.append("max")
    if operator == "minus":
        element_position = parameter_values.index(value) - 1
        if element_position > 0:
            what_to_return.append(parameter_values[element_position])
            what_to_return.append("regular")
        else:
            element_position = parameter_values.index(value) - 1
            what_to_return.append(parameter_values[element_position])
            what_to_return.append("min")
    return what_to_return
