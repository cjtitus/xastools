def inferColTypes(cols):
    motorNames = ['Seconds', 'ENERGY_ENC', 'MONO']
    sensorNames = ['TEMP']
    coltypes = []
    for c in cols:
        if c in motorNames:
            coltypes.append('motor')
        elif c in sensorNames:
            coltypes.append('sensor')
        else:
            coltypes.append('detector')
    return coltypes
