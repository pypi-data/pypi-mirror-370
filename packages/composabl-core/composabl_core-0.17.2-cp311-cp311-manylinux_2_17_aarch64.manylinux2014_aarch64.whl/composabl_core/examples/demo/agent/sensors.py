# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core.agent.sensors.sensor import Sensor

counter_value = Sensor("counter", "The value of the counter")
counter_value2 = Sensor("counter2", "The value of the counter")
counter_value3 = Sensor("counter3", "The value of the counter")

text_value = Sensor("text", "The value of the text")
# For multi-binary
counter_value_bit0 = Sensor("counter", "The value of the counter bit 0")
counter_value_bit1 = Sensor("counter_value_bit1", "The value of the counter bit 1")
counter_value_bit2 = Sensor("counter_value_bit2", "The value of the counter bit 2")
counter_value_bit3 = Sensor("counter_value_bit3", "The value of the counter bit 3")
counter_value_bit4 = Sensor("counter_value_bit4", "The value of the counter bit 4")
counter_value_bit5 = Sensor("counter_value_bit5", "The value of the counter bit 5")
counter_value_bit6 = Sensor("counter_value_bit6", "The value of the counter bit 6")

# The sim environment has multiple space types we can configure
# this thus means we can have different sensor configurations
sensors_discrete = [counter_value]
sensors_multi_discrete = [counter_value]
sensors_multi_binary = [
    counter_value_bit0,
    counter_value_bit1,
    counter_value_bit2,
    counter_value_bit3,
    counter_value_bit4,
    counter_value_bit5,
    counter_value_bit6,
]
sensors_box = [counter_value]
sensors_dictionary = [counter_value]
sensors_tuple = [counter_value, counter_value2, counter_value3]

sensors_text = [text_value, counter_value]
sensors_dict = {
    "discrete": sensors_discrete,
    "multidiscrete": sensors_multi_discrete,
    "multibinary": sensors_multi_binary,
    "box": sensors_box,
    "dictionary": sensors_dictionary,
    "tuple": sensors_tuple,
    "text": sensors_text,
}
