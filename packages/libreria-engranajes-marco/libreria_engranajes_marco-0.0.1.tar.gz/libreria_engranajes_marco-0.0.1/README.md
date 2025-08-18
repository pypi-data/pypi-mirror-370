##this library intents to help in the calculations needed to desing straight gears.
#this library contents 7 functions that helps with the calculations of primitive diameter, internal and external diameter;
#with the width of each teeth and even with the distance among each center of the gears.

#just to clarify, all the answers of the calculations are in milimeters and the answers are all float type.

#"num_diente" is a function that calculates the number of teeth of the gear. the values required for this calculation are
the external diameter and the module. watch out, sometimes the answer of this operation is a decimal number. if the number is,
for example, 5.5, it is better to round it up to 6. 
#"altura_diente" calculates the height of the teeth.
#"diametro_primitivo" calculates the primitive diameter, the operation is "M*z". the answer is a float number.
#"diametro_interior" calculates the inner diameter of the gear. the operation is "De-2h" , being De external diameter and
h the height of the teeth.
#"paso" calulates the circular passage, the operation is "P*pi".
#"espesor" calculates the tickness of teeth. 
#"distancia_centros" calculates how far away needs to be a gear next to other so that they can drive each other without
interfering. 
