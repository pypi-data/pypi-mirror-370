import math

def specific_growth_rate_from_doubling_time(dt):
    return math.log(2)/dt

def time_to_titer(titer, qp, cell_seed_volume, doubling_time, growth='exponential', titer_unit='g/l', qp_unit='g/cell.hr', seed_unit='cell/l', time_unit='hr'):
    qp_time_unit = qp_unit.split('/')[1].split('.')[1]
    unit_match = [False, False, False]
    if qp_time_unit != time_unit:    
        pass    # convert time units
    else:
        unit_match[0]=True
    seed_vol_unit = seed_unit.split('/')[1]
    titer_vol_unit = titer_unit.split('/')[1]
    if seed_vol_unit!=titer_vol_unit:
        if seed_vol_unit == 'ml' and titer_vol_unit == 'l':
            cell_seed_volume *= 1000
            seed_vol_unit = 'l'
        elif seed_vol_unit == 'l' and titer_vol_unit == 'ml':
            cell_seed_volume /= 1000
            seed_vol_unit = 'ml'
        unit_match[1] = True
    else:
       unit_match[1] = True
    qp_mass_unit = qp_unit.split('/')[0]
    titer_mass_unit = titer_unit.split('/')[0]
    if qp_mass_unit!=titer_mass_unit:
        pass    # convert mass units
    else:
        unit_match[2]=True

    if unit_match[0] == True and unit_match[1] == True and unit_match[2] == True and growth == 'exponential':
        specific_growth_rate = specific_growth_rate_from_doubling_time(doubling_time)
        a = 1/specific_growth_rate
        b = specific_growth_rate*titer
        c = qp*cell_seed_volume
        d = b/c
        t = a * math.log(d)
        return {'value': int(round(t,0)), 'unit':time_unit}
    else:
        print('unit mismatch\nplease run again with correct units')
        return None