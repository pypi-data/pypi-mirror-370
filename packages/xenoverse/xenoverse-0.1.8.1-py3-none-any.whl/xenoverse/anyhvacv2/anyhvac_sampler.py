import sys
import numpy
from numpy import random as rnd
from .anyhvac_utils import BaseSensor, HeaterUnc, Cooler

def HVACTaskSampler(control_type='Temperature',
                    target_temperature=None):
    nw = rnd.randint(5, 16) # width of the building, in cell number
    nl = rnd.randint(5, 16) # length of the building, in cell number
    cell_size = rnd.uniform(1, 3)
    floor_height = rnd.uniform(2, 8)

    dw = nw * cell_size
    dl = nl * cell_size

    dh = rnd.uniform(3, 12)  # height of the building
    area = dw * dl # area of the building
    cell_volume = floor_height * cell_size * cell_size # volume of each cell

    chtc_array = numpy.random.uniform(1.5, 25.0, size=(nw + 1, nl + 1, 2)) # Convective Heat Transfer Coefficients
    hc_array = numpy.random.uniform(1000, 4000, size=(nw, nl)) * cell_volume # heat capacity inside the building
    wall_chtc = rnd.uniform(1.5, 3.0)
    chtc_array[0, :, 0] = wall_chtc
    chtc_array[nw, :, 0] = wall_chtc
    chtc_array[:, 0, 1] = wall_chtc
    chtc_array[:, nl, 1] = wall_chtc
    cell_walls = chtc_array < 5.0

    n_sensors = max(int(area * rnd.uniform(0.10, 0.30)), 1)
    n_heaters = max(int(area * rnd.uniform(0.10, 0.30)), 1)
    n_coolers = max(int(area * rnd.uniform(0.05, 0.15)), 1)

    eps = rnd.uniform(0.0, 1.0)
    if(eps < 0.33):
        t_ambient = rnd.uniform(0, 40) # ambient temperature
    elif(eps < 0.66):
        t_ambient = rnd.uniform(15, 40)
    else:
        t_ambient = rnd.uniform(30, 40)


    print(f"t_ambient: {t_ambient}")
    sensors = []
    equipments = []
    coolers = []

    for i in range(n_sensors):
        sensors.append(BaseSensor(nw, nl, cell_size, cell_walls, min_dist=1.2,
                    avoidance=sensors))
    for i in range(n_heaters):
        equipments.append(HeaterUnc(nw, nl, cell_size, cell_walls, min_dist=1.2,
                    avoidance=equipments))
        # hc_array[equipments[-1].nloc] += rnd.uniform(20000, 80000)
        hc_array[equipments[-1].nloc[0], equipments[-1].nloc[1]] += rnd.uniform(20000, 80000)
    for i in range(n_coolers):
        coolers.append(Cooler(nw, nl, cell_size, cell_walls, min_dist=min(cell_size, 2.0),
                    avoidance=coolers,
                    control_type=control_type))
        
    if(target_temperature is not None):
        target_temperature = target_temperature
    else:
        if(rnd.choice([True, False])):
            target_temperature = rnd.uniform(24, 28)
        else:
            target_temperature = rnd.uniform(24, 28, size=(n_sensors))

    return {
        'width': dw,
        'length': dl,
        'height': dh,
        'n_width': nw,
        'n_length': nl,
        'cell_size': cell_size,
        'floor_height': floor_height,
        'sensors': sensors,
        'convection_coeffs': chtc_array,
        'heat_capacity': hc_array,
        'ambient_temp': t_ambient,
        'sensors': sensors,
        'equipments': equipments,
        'coolers': coolers,
        'control_type': control_type,
        'target_temperature': target_temperature,
    }
