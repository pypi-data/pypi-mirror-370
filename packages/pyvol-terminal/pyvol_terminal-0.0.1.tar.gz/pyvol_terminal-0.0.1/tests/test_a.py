#%%
import math 
import numpy as np

def tickSpacing2(minVal: float, maxVal: float, size: float):
    _tickDensity=1
    style = {"maxTickLevel" : 1} 
    dif = abs(maxVal - minVal)
    if dif == 0:
        return []

    ref_size = 300. # axes longer than this display more than the minimum number of major ticks
    minNumberOfIntervals = max(
        2.25,       # 2.0 ensures two tick marks. Fudged increase to 2.25 allows room for tick labels.
        2.25 * _tickDensity * math.sqrt(size/ref_size) # sub-linear growth of tick spacing with size
    )

    majorMaxSpacing = dif / minNumberOfIntervals

    mantissa, exp2 = math.frexp(majorMaxSpacing) # IEEE 754 float already knows its exponent, no need to calculate
    p10unit = 10. ** ( # approximate a power of ten base factor just smaller than the given number
        math.floor(            # int would truncate towards zero to give wrong results for negative exponents
            (exp2-1)      # IEEE 754 exponent is ceiling of true exponent --> estimate floor by subtracting 1
            / 3.32192809488736 # division by log2(10)=3.32 converts base 2 exponent to base 10 exponent
        ) - 1             # subtract one extra power of ten so that we can work with integer scale factors >= 5
    )
    # neglecting the mantissa can underestimate by one power of 10 when the true value is JUST above the threshold.
    if 100. * p10unit <= majorMaxSpacing: # Cheaper to check this than to use a more complicated approximation.
        majorScaleFactor = 10
        p10unit *= 10.
    else:
        for majorScaleFactor in (50, 20, 10):
            if majorScaleFactor * p10unit <= majorMaxSpacing:
                break # find the first value that is smaller or equal
    majorInterval = majorScaleFactor * p10unit
    # manual sanity check: print(f"{majorMaxSpacing:.2e} > {majorInterval:.2e} = {majorScaleFactor:.2e} x {p10unit:.2e}")
    levels = [
        (majorInterval, 0),
    ]

    if style['maxTickLevel'] >= 1:
        minorMinSpacing = 2 * dif/size   # no more than one minor tick per two pixels
        trials = (5, 10) if majorScaleFactor == 10 else (10, 20, 50)
        for minorScaleFactor in trials:
            minorInterval = minorScaleFactor * p10unit
            if minorInterval >= minorMinSpacing:
                break # find the first value that is larger or equal to allowed minimum of 1 per 2px
        levels.append((minorInterval, 0))

    # extra ticks at 10% of major interval are pretty, but eat up CPU
    if style['maxTickLevel'] >= 2: # consider only when enabled
        if majorScaleFactor == 10:
            trials = (1, 2, 5, 10) # start at 10% of major interval, increase if needed
        elif majorScaleFactor == 20:
            trials = (2, 5, 10, 20) # start at 10% of major interval, increase if needed
        elif majorScaleFactor == 50:
            trials = (5, 10, 50) # start at 10% of major interval, increase if needed
        else: # invalid value
            trials = () # skip extra interval
            extraInterval = minorInterval
        for extraScaleFactor in trials:
            extraInterval = extraScaleFactor * p10unit
            if extraInterval >= minorMinSpacing or extraInterval == minorInterval:
                break # find the first value that is larger or equal to allowed minimum of 1 per 2px
        if extraInterval < minorInterval: # add extra interval only if it is visible
            levels.append((extraInterval, 0))
    return levels

def tickSpacing(minVal: float, maxVal: float, size: float):
    _tickDensity=1
    style = {"maxTickLevel" : 1} 
    dif = abs(maxVal - minVal)
    if dif == 0:
        return []

    ref_size = 300. # axes longer than this display more than the minimum number of major ticks
    minNumberOfIntervals = max(
        2.25,       # 2.0 ensures two tick marks. Fudged increase to 2.25 allows room for tick labels.
        2.25 * _tickDensity * math.sqrt(size/ref_size) # sub-linear growth of tick spacing with size
    )

    majorMaxSpacing = dif / minNumberOfIntervals

    mantissa, exp2 = math.frexp(majorMaxSpacing)
    p10unit = 10. ** (
        math.floor(
            (exp2-1)
            / 3.32192809488736
        ) - 1
    )
    
    if 100. * p10unit <= majorMaxSpacing:
        majorScaleFactor = 10
        p10unit *= 10.
    else:
        for majorScaleFactor in (50, 20, 10):
            if majorScaleFactor * p10unit <= majorMaxSpacing:
                break
    
    majorInterval = majorScaleFactor * p10unit
    levels = [
        (majorInterval, 0),
    ]

    if style['maxTickLevel'] >= 1:
        # Modified this section to choose a smaller interval for minor ticks
        if majorScaleFactor == 10:
            minorScaleFactor = 5  # Half of major interval for minor ticks
        elif majorScaleFactor == 20:
            minorScaleFactor = 10  # Half of major interval
        elif majorScaleFactor == 50:
            minorScaleFactor = 25  # Half of major interval
        else:
            minorScaleFactor = majorScaleFactor / 2  # Default to half
        
        minorInterval = minorScaleFactor * p10unit
        levels.append((minorInterval, 0))

    if style['maxTickLevel'] >= 2:
        # Keep the extra level logic but ensure it's smaller than minor interval
        if majorScaleFactor == 10:
            extraScaleFactor = 2  # Smaller than minor interval
        elif majorScaleFactor == 20:
            extraScaleFactor = 5  # Smaller than minor interval
        elif majorScaleFactor == 50:
            extraScaleFactor = 10  # Smaller than minor interval
        else:
            extraScaleFactor = minorScaleFactor / 2  # Default to half
        
        extraInterval = extraScaleFactor * p10unit
        if extraInterval < minorInterval:
            levels.append((extraInterval, 0))
            
    return levels


def tickValues(minVal:float, maxVal:float, size: float):
    scale=1
    minVal, maxVal = sorted((minVal, maxVal))

    minVal *= scale
    maxVal *= scale

    ticks = []
    tickLevels = tickSpacing(minVal, maxVal, size)
    print(f"tickLevels: {tickLevels}")
    allValues = np.array([])
    for i in range(len(tickLevels)):
        spacing, offset = tickLevels[i]

        ## determine starting tick
        start = (math.ceil((minVal-offset) / spacing) * spacing) + offset

        ## determine number of ticks
        num = int((maxVal-start) / spacing) + 1
        values = (np.arange(num) * spacing + start) / scale
        ## remove any ticks that were present in higher levels
        ## we assume here that if the difference between a tick value and a previously seen tick value
        ## is less than spacing/100, then they are 'equal' and we can ignore the new tick.
        close = np.any(
            np.isclose(
                allValues,
                values[:, np.newaxis],
                rtol=0,
                atol=spacing/scale*0.01
            ),
            axis=-1
        )
        values = values[~close]
        allValues = np.concatenate([allValues, values])
        ticks.append((spacing/scale, values.tolist()))

    return ticks
ax_range = [50300., 7000]
tickLevels = tickValues(*ax_range, 1)


from pprint import pprint
nticks = 0
base_pos=[]
print("")
print(ax_range)
print(f"tickLevels:")
pprint(tickLevels)

