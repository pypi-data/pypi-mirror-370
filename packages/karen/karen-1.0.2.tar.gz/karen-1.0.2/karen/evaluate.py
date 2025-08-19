from karen.state import State
from karen.combo import *
from karen.classify import classify
from math import floor
from karen.actions import *

def evaluate(inputString, printWarnings = True, simpleMode = False):
    warnings = []

    state = State()
    comboSequence = getComboSequence(inputString, warnings) + [""]

    # runs a second evaluation with maximum action ranges
    maxTravelTimeState = State()
    maxTravelTimeState.inferInitialState(comboSequence)

    # infer initial state being airborne/having overhead
    state.inferInitialState(comboSequence, warnings)
    comboSequence = state.correctSequence(comboSequence)

    if simpleMode:
        comboSequence = simplify(comboSequence)

    for i in range(len(comboSequence) - 1):
        nextAction = [j for j in comboSequence[i+1:] if not j in ["j", "d", "l"]][0]
        addAction(state, comboSequence[i], nextAction, warnings, simpleMode=simpleMode)
        addAction(maxTravelTimeState, comboSequence[i], nextAction, maxTravelTimes=True)
    state.resolve(warnings)
    maxTravelTimeState.resolve()

    # checks for continued burn tracer damage after final action
    burnTracerBonusDamage = ""
    if state.burnActiveTimer > 12:
        burnTracerBonusDamage = "(plus " + str(int(floor((state.burnActiveTimer - 1) / 12) * BURN_TRACER_DPS / 5)) +" burn over time)"

    comboName = classify("".join(comboSequence))

    timeSecondsMin = round(state.timeTaken / 60, 2)
    timeSecondsMax = round(maxTravelTimeState.timeTaken / 60, 2)
    showTimeRange = maxTravelTimeState.timeTaken != state.timeTaken and not simpleMode
    timeSeconds = str(timeSecondsMin) + (f"-{timeSecondsMax}" if showTimeRange else "")
    timeFrames = str(state.timeTaken) + (f"-{maxTravelTimeState.timeTaken}" if showTimeRange else "")

    timeFromDamageSecondsMin = round(state.timeFromDamage / 60, 2)
    timeFromDamageSecondsMax = round(maxTravelTimeState.timeFromDamage / 60, 2)
    showTimeFromDamageRange = maxTravelTimeState.timeFromDamage != state.timeFromDamage and not simpleMode
    timeFromDamageSeconds = str(timeFromDamageSecondsMin) + (f"-{timeFromDamageSecondsMax}" if showTimeFromDamageRange else "")
    timeFromDamageFrames = str(state.timeFromDamage) + (f"-{maxTravelTimeState.timeFromDamage}" if showTimeFromDamageRange else "")

    output = ( f"### {comboName}"
    f"\n> {state.sequence}"
    f"\n**Time:** {timeSeconds} seconds ({timeFrames} frames)"
    f"{f"\n**Time From Damage:** {timeFromDamageSeconds} seconds ({timeFromDamageFrames} frames)" if state.damageDealt > 0 else ""}"
    f"\n**Damage:** {int(state.damageDealt)} {burnTracerBonusDamage}" )

    if len(warnings) > 0 and printWarnings:
        warninglist = ["\nWARNING: " + x for x in warnings]

        output += "\n```"
        while len(warninglist) > 0 and len(output) + len(warninglist[0]) + len(f"\n...({len(warninglist)} warnings)\n```") < 2000:
            output += warninglist[0]
            warninglist = warninglist[1:]
        if len(warninglist) > 0:
            output += f"\n...({len(warninglist)} warnings)"
        output += "\n```"

    if len(output) >= 2000:
        return "```\nERROR: Combo too long for Discord API\n```"  
    
    return output