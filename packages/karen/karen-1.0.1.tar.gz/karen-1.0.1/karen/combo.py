from karen.actions import *
from karen.state import State

def getComboSequence(inputString="", warnings=[]):

    if not ("G+u" in ACTIONS):
        loadMoveStacks()
    
    # removes anything in brackets from inputString string
    sequence = inputString
    while "(" in sequence and ")" in sequence[sequence.find("("):]:
        sequence = sequence[:sequence.find("(")] + sequence[sequence[sequence.find("("):].find(")") + sequence.find("(") + 1:]
    
    # removes leading/trailing spaces
    while sequence[0] == " ":
        sequence = sequence[1:]
    while sequence[-1] == " ":
        sequence = sequence[:-1]
    
    # uses long form if ">" is in sequence, there are invalid characters, or spaces
    if ">" in sequence or len([x for x in sequence if not (x.lower() in ACTION_NAMES or x in ["", " "])]) > 0 or len([x for x in sequence.split(" ")]) > 1:
        words = [x for x in sequence.replace("+", " + ").replace(">", " > ").split(" ") if x != ""]
        sequence = []
        while len(words) > 0:
            while words[0] == ">":
                words = words[1:]
            for j in range(0, len(words)):
                if ">" in words[0 : len(words) - j]: # ">" forces separation of actions
                    continue
                if ("".join(words[0 : len(words) - j])).lower() in ACTION_NAMES or len(words) - j == 1:
                    sequence += ["".join(words[0 : len(words) - j])]
                    words = words[len(words) - j:]
                    break
    
    # unrecognised actions
    warnings += [unknownAction + " is not a recognised action" for unknownAction in sequence if not unknownAction.lower() in ACTION_NAMES]
    
    # converts to a list of correctly formatted keys in ACTION_NAMES
    sequence = [(ACTION_NAMES[x] if x in ACTION_NAMES else x.lower()) for x in sequence if (x.lower() in ACTION_NAMES)] 
    sequence = list("".join(sequence))

    # folds movestack indicators into actions
    foldSequence = []
    for i in range(len(sequence)):
        if len(foldSequence) > 0 and sequence[i-1] == "+":
            foldSequence[-1] += "+" + sequence[i]
        elif sequence[i] != "+":
            foldSequence.append(sequence[i])
    
    # verify movestacks
    verifySequence = []
    for action in foldSequence:
        if action in ACTION_NAMES and ACTION_NAMES[action] in ACTIONS:
            verifySequence.append(ACTION_NAMES[action])
        else:
            warnings += [action + " is not a regocnised movestack"]
            verifySequence += action.split("+")

    return verifySequence

def simplify(sequence):
    newSequence = []

    for i in range(len(sequence) - 1):

        current = sequence[i]
        next = [j for j in sequence[i+1:] if not j in ["j", "d", "l"]][0]
        if next == "":
            newSequence += [current]
            continue

        # replace swing cancels with whiff cancels
        elif current == "s" and ACTIONS["w"].cancelTimes[next] <= ACTIONS["s"].cancelTimes[next]:
            newSequence += ["w"]

        # insert whiffs after actions with uppercuts where speed is increased
        elif "u" in current and ACTIONS[current].cancelTimes["w"] + ACTIONS["w"].cancelTimes[next] < ACTIONS[current].cancelTimes[next] and next != "":
            newSequence += [current, "w"]
        
        else:
            newSequence += [current]
    
    return newSequence + [""]
        

def addAction(state=State(), action="", nextAction="", warnings=[], maxTravelTimes=False, simpleMode=False):

    if not ("G+u" in ACTIONS):
        loadMoveStacks()

    # awaits required cooldowns
    for a in ACTIONS[action].awaitCharges:
        state.incrementTime(state.charges[a].activeTimer, warnings) 
        state.incrementTime(state.charges[a].cooldownTimer - ACTIONS[action].awaitCharges[a], warnings)
        state.incrementTime(state.charges[a].RECHARGE_TIME - state.charges[a].currentCharge - ACTIONS[action].awaitCharges[a], warnings)

    # awaits tracer register for GOHT
    if "g" in ACTIONS[action].awaitCharges:
        state.incrementTime(state.gohtWaitTime - ACTIONS[action].awaitCharges["g"], warnings)

    # awaits kick expiration for punch
    if "p" in action and state.punchSequence == 2:
        state.incrementTime(state.punchSequenceTimer, warnings)

    if "k" in action and state.punchSequence < 2:
        warnings += ["uses impossible kick after " + state.sequence]
    
    if "G" in action and (state.tracerActiveTimer == 0 or state.tracerActiveTimer < ACTIONS[action].awaitCharges["g"]) and (state.burnTracerActiveTimer == 0 or state.burnTracerActiveTimer < ACTIONS[action].awaitCharges["g"]):
        warnings += ["uses GOHT on nonxistent or expired tracer after " + state.sequence]

    if "p" in action and (state.hasSwingOverhead or state.hasJumpOverhead) and not simpleMode:
        warnings += ["uses punch when overhead was expected after " + state.sequence]
    if "k" in action and (state.hasSwingOverhead or state.hasJumpOverhead and not simpleMode):
        warnings += ["uses kick when overhead was expected after " + state.sequence]

    # awaits whiff end for overhead
    if "o" in action and (not state.hasJumpOverhead) and (not state.hasSwingOverhead) and state.charges["s"].activeTimer > 0:
        print(f"TIME ELAPSED: {state.timeTaken}")
        print(f"ACTIVE TIMER: {state.charges["s"].activeTimer}")
        state.incrementTime(state.charges["s"].activeTimer, warnings)

    # awaits punch timer for punch
    if "p" in action or "k" in action:
        state.incrementTime(state.punchWaitTimer, warnings)

    # awaits swing timer for swing/whiff
    if "s" in action or "w" in action:
        state.incrementTime(state.swingWaitTimer - ACTIONS[action].awaitCharges["s"], warnings)

    # precomputes max travel time, factoring in the known max range
    travelTime = 0 if not maxTravelTimes else ACTIONS[action].maxTravelTime
    if action != "s" and ACTIONS[action].range > state.maxPossibleRange:
        travelTime = int(travelTime / ACTIONS[action].range * state.maxPossibleRange)
    if action == "s" and nextAction == "":
        travelTime = 0

    # handling changes of max possible range
    if action != "s" and ACTIONS[action].range != 0:
        state.maxPossibleRange = min(state.maxPossibleRange, ACTIONS[action].range)
    if action == "b":
        state.maxPossibleRange += BURN_TRACER_BACKFLIP_DISTANCE
    if action == "G":
        state.maxPossibleRange = 0

    # punch sequence increment
    if "p" in action:
        state.punchSequence += 1
        state.punchSequenceTimer = PUNCH_SEQUENCE_MAX_DELAY
    if "k" in action:
        state.punchSequence = 0
    
    # processes overhead logic
    if "o" in action and (not state.hasSwingOverhead) and (not state.hasJumpOverhead) and not simpleMode:
        warnings += ["uses impossible overhead after " + state.sequence]

    if action == "l":
        state.isAirborn = False
        state.hasDoubleJump = True
        state.hasSwingOverhead = False
        state.hasJumpOverhead = False
   
    if action == "j" and state.isAirborn:
        if not state.hasDoubleJump and not simpleMode: 
            warnings += ["uses impossible double jump after " + state.sequence]
        state.hasDoubleJump = False
        state.hasJumpOverhead = True

    elif action in ["j", "s", "a", "b"] or "u" in action:
        state.isAirborn = True

    if action == "d":
        if not state.hasDoubleJump and not simpleMode: 
            warnings += ["uses impossible double jump after " + state.sequence]
        state.isAirborn = True
        state.hasDoubleJump = False
        state.hasJumpOverhead = True

    if action in ["o", "G", "G+u", "p+G", "k+G", "p+G+u", "k+G+u", "p+G+u", "k+G+u", "o+t", "p+o", "k+o"]:
        if state.hasSwingOverhead:
            state.hasSwingOverhead = False
        else:
            state.hasJumpOverhead = False
    if action in ["o+G", "o+G+u"]:
        state.hasSwingOverhead = False
        state.hasJumpOverhead = False
    if action == "u+w+G":
        state.hasSwingOverhead = True
        state.hasJumpOverhead = False

    if action in ["s", "a", "b"] or "u" in action:
        state.hasDoubleJump = True
        state.hasJumpOverhead = False
    
    if action == "b":
        state.hasSwingOverhead = True

    # ends current cancellable actions
    for cancelCharge in ACTIONS[action].endActivations:
        if state.charges[cancelCharge].activeTimer > 0:
            state.endAction(cancelCharge)

    # activating actions/consuming cooldowns
    if action in ["s", "a"]:
        state.removeSwingOnEnd = True
    if "w" in action:
        state.removeSwingOnEnd = False

    for charge in ACTIONS[action].chargeActivations:
        state.charges[charge].cooldownTimer = state.charges[charge].COOLDOWN_TIME
        if ACTIONS[action].chargeActivations[charge] == 0:
            state.charges[charge].currentCharge -= state.charges[charge].RECHARGE_TIME
        else:
            state.charges[charge].activeTimer = ACTIONS[action].chargeActivations[charge] + travelTime
        
    # adding tracer tags
    if action == "t":
        state.tracerActiveTimer = TRACER_ACTIVE_TIME + ACTIONS["t"].damageTime + travelTime
        if state.tracerActiveTimer == 0 and state.burnTracerActiveTimer == 0:
            state.gohtWaitTime = ACTIONS[action].damageTime + (0 if not maxTravelTimes else TRACER_MAX_TRAVEL_TIME)
    if action == "b":
        state.burnTracerActiveTimer = BURN_TRACER_ACTIVE_TIME + ACTIONS["b"].damageTime + travelTime  
        if state.tracerActiveTimer == 0 and state.burnTracerActiveTimer == 0:
            state.gohtWaitTime = ACTIONS[action].damageTime + (0 if not maxTravelTimes else BURN_TRACER_MAX_TRAVEL_TIME)

    # proccing tracers
    if ACTIONS[action].procsTracer and state.tracerActiveTimer >= ACTIONS[action].procTime or action in ["p+t", "k+t", "o+t"]:
        state.damageDealt += TRACER_PROC_DAMAGE
        state.tracerActiveTimer = 0
    if ACTIONS[action].procsTracer and state.burnTracerActiveTimer >= ACTIONS[action].procTime:
        state.burnActiveTimer = BURN_TRACER_BURN_TIME + ACTIONS[action].procTime
        state.burnTracerActiveTimer = 0

    if state.firstDamageTime == 0 and ACTIONS[action].damage > 0:
        state.firstDamageTime = state.timeTaken + ACTIONS[action].firstDamageTime + (travelTime if not "+G" in action else 0)

    # autoswing delays next swing/whiff
    if action == "a":
        state.swingWaitTimer = ACTIONS["a"].cancelTimes["s"]

    state.damageDealt += ACTIONS[action].damage
    state.minTimeTaken = max(state.minTimeTaken, state.timeTaken + ACTIONS[action].damageTime + travelTime)
    state.incrementTime((ACTIONS[action].damageTime if nextAction == "" else ACTIONS[action].cancelTimes[nextAction]) + travelTime, warnings)

    state.sequence += ("" if state.sequence == "" else " > ") + ACTIONS[action].name