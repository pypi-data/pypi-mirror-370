from karen.actions import *

class Charge:
    MAX_CHARGES = 0
    currentCharge = 0
    RECHARGE_TIME = 0
    COOLDOWN_TIME = 0
    cooldownTimer = 0
    activeTimer = 0 # cooldown refresh= doesn't start until icon is no longer yellow

    def __init__(self, MAX_CHARGES, RECHARGE_TIME, COOLDOWN_TIME = 0):
        self.MAX_CHARGES = MAX_CHARGES
        self.currentCharge = MAX_CHARGES * RECHARGE_TIME
        self.RECHARGE_TIME = RECHARGE_TIME
        self.COOLDOWN_TIME = COOLDOWN_TIME


class State:

    # charges/cooldowns - to avoid floating point innacuracy, using an ability takes charge equal to the number of frames it will take to recharge
    charges = {}
    tracerActiveTimer = 0 # frames remaining until tracer on opponent expires
    burnTracerActiveTimer = 0
    burnActiveTimer = 0 # timer for while burn tracer deals damage after procced
    gohtWaitTime = 0 # countdown from when tracer fired at unmarked target to when goht can be used

    maxPossibleRange = 24 # for lowering the upper bound when factoring in travel time

    # airborne
    isAirborn = False

    # overheads
    hasDoubleJump = True
    hasJumpOverhead = False
    hasSwingOverhead = False
    removeSwingOnEnd = False
    swingWaitTimer = 0 # frames until swing/whiff can be used after autoswing

    # punch sequence
    punchSequence = 0 # 0 & 1 correspond to punches, 2 corresponds to kick
    punchSequenceTimer = 0 # frames remaining until punch sequence resets
    punchWaitTimer = 0 # frames until a punch can be used

    # seasonal boost
    damageMultiplier = 1

    # tracking metrics
    damageDealt = 0
    timeTaken = 0
    firstDamageTime = 0
    timeFromDamage = 0 # only computed when resolve() is called
    minTimeTaken = 0 # makes sure swing cancels at the end don't cut the timer short

    # sequence output
    sequence = ""

    def __init__(self):

        self.charges = {
            "t" : Charge(
                MAX_CHARGES = 5, 
                RECHARGE_TIME = 2.5 * 60,
                COOLDOWN_TIME = 0.5 * 60
            ),
            "s" : Charge(
                MAX_CHARGES = 3, 
                RECHARGE_TIME = 6 * 60
            ),
            "g" : Charge(
                MAX_CHARGES = 1, 
                RECHARGE_TIME = 8 * 60
            ),
            "u" : Charge(
                MAX_CHARGES = 2, 
                RECHARGE_TIME = 6 * 60,
                COOLDOWN_TIME = 2 * 60
            ),
            "b" : Charge(
                MAX_CHARGES = 1, 
                RECHARGE_TIME = 12 * 60
            )
        }

    def incrementTime(self, frames, warnings):

        if frames <= 0:
            return
        
        self.timeTaken += frames

        for chargeType in self.charges:
            self.charges[chargeType].currentCharge = min(self.charges[chargeType].currentCharge + frames, self.charges[chargeType].MAX_CHARGES * self.charges[chargeType].RECHARGE_TIME)
            self.charges[chargeType].cooldownTimer = max(self.charges[chargeType].cooldownTimer - frames, 0)

            if self.charges[chargeType].activeTimer > 0 and self.charges[chargeType].activeTimer <= frames:
                excessTime = frames - self.charges[chargeType].activeTimer
                self.endAction(chargeType)
                self.charges[chargeType].currentCharge += excessTime
            
            elif self.charges[chargeType].activeTimer > 0:
                self.charges[chargeType].activeTimer -= frames

        if self.tracerActiveTimer > 0 and self.tracerActiveTimer <= frames:
           warnings += ["tracer expired without proc after " + self.sequence]
        if self.burnTracerActiveTimer > 0 and self.burnTracerActiveTimer <= frames:
           warnings += ["burn tracer expired without proc after " + self.sequence]    

        # burn tracer damage ticks 5 times per second (12 frames)
        burnFrames = frames
        if self.burnActiveTimer > BURN_TRACER_BURN_TIME:
            if burnFrames + BURN_TRACER_BURN_TIME >= self.burnTracerActiveTimer:
                burnFrames -= self.burnActiveTimer - BURN_TRACER_BURN_TIME
                self.burnActiveTimer = BURN_TRACER_BURN_TIME
                self.damageDealt += BURN_TRACER_DPS / 5
            else:
                self.burnActiveTimer -= burnFrames
                burnFrames = 0
        while burnFrames >= 12 and self.burnActiveTimer >= 12:
            burnFrames -= 12
            self.burnActiveTimer -= 12
            if self.burnActiveTimer != 0:
                self.damageDealt += BURN_TRACER_DPS / 5
        if burnFrames > self.burnActiveTimer:
            self.burnActiveTimer = 0
        elif burnFrames > 0:
            if (self.burnActiveTimer % 12) <= burnFrames and (self.burnActiveTimer % 12) != 0  and self.burnActiveTimer > 12:
                self.damageDealt += BURN_TRACER_DPS / 5
            self.burnActiveTimer -= burnFrames

        self.tracerActiveTimer = max(self.tracerActiveTimer - frames, 0)
        self.burnTracerActiveTimer = max(self.burnTracerActiveTimer - frames, 0)
        self.gohtWaitTime = max(self.gohtWaitTime - frames, 0)

        self.punchWaitTimer = max(0, self.punchWaitTimer - frames)
        self.swingWaitTimer = max(0, self.swingWaitTimer - frames)


        self.punchSequenceTimer = max(self.punchSequenceTimer - frames, 0)
        if self.punchSequenceTimer == 0:
            self.punchSequence = 0

    # if not all damage has actually taken place, await the final damage ticks
    def resolve(self, warnings=[]):
        self.incrementTime(self.minTimeTaken - self.timeTaken, warnings)
        self.timeFromDamage = self.timeTaken - self.firstDamageTime

    def endAction(self, action): # ends current action and takes away the associated cooldown charge
        self.charges[action].activeTimer = 0
        if action != "s" or self.removeSwingOnEnd:
            self.charges[action].currentCharge -= self.charges[action].RECHARGE_TIME
        if action == "s":
            self.hasSwingOverhead |= self.isAirborn and self.hasDoubleJump
            self.hasJumpOverhead |= self.isAirborn and not self.hasDoubleJump

    def inferInitialState(self, comboSequence, warnings=[]):
        foldSequence = "".join(comboSequence)

        # pre-tag if GOHT used before tracer / burn tracer
        if "G" in foldSequence and ((not ("t" in foldSequence or "b" in foldSequence)) or foldSequence.index("G") < min((foldSequence+"bt").index("t"), (foldSequence+"bt").index("b"))):
            self.tracerActiveTimer = TRACER_ACTIVE_TIME
            warnings += ["inferred target starts with tracer applied to enable GOHT"]
        
        # pre-punch if kick is used before two punches
        if "k" in foldSequence:
            priorPunches = foldSequence.count("p", 0, foldSequence.index("k"))
            self.punchSequence = max(0, 2 - priorPunches)
            self.punchSequenceTimer = PUNCH_SEQUENCE_MAX_DELAY - ACTIONS["p"].cancelTimes[foldSequence.replace("j", "").replace("l", "")[0]] # set punch sequence timer as if pre-punching was the last thing done before the combo
        
        # airborne if overhead/land is used before jump/swing/uppercut/burn tracer
        temp = foldSequence + "jdsub" # ensures index funtions don't error
        preAirborne = temp[:min(temp.index("j"), temp.index("s"), temp.index("d"), temp.index("u"), temp.index("b"))]
        self.isAirborn = "o" in preAirborne or "l" in preAirborne

        # also airborne if only one jump is used before overhead
        if "o" in foldSequence and not self.isAirborn:
            preOH = foldSequence[:temp.index("o")]
            self.isAirborn = not ("s" in preOH or "w" in preOH or "b" in preOH or preOH.count("j") >= 2)

        # has swing overhead if overhead is used before payout
        temp = foldSequence + "jjdswb"
        if not self.isAirborn: # ignore the first jump for overhead payouts if not airborne
            temp = temp[:temp.index("j")] + temp[temp.index("j") + 1:]
        preOverheadPayout = temp[:min(temp.index("j"), temp.index("d"), temp.index("s"), temp.index("w"), temp.index("b"))]
        self.hasSwingOverhead = preOverheadPayout.count("o") >= 1

        # has jump ovehead if two overheads are used before payout
        if preOverheadPayout.count("o") >= 2:
            self.hasJumpOverhead = True
            self.hasDoubleJump = False

        # infers jump overhead being preserved through goht
        if "G" in preOverheadPayout and (not ("sG" in preOverheadPayout or "wG" in preOverheadPayout)) and "o" in preOverheadPayout[preOverheadPayout.index("G"):]:
            self.hasJumpOverhead = True
            self.hasDoubleJump = False

        # infers starting within 5m if melee is used before goht/goh
        preGOH = foldSequence + "gG"
        preGOH = preGOH[:min(preGOH.index("G"), preGOH.index("g"))]
        for a in preGOH:
            if a in "pkou":
                self.maxPossibleRange = 5
                break
        

    def correctSequence(self, combo):

        # Converts relevant jumps to double jumps
        isAirborne = self.isAirborn
        correctedCombo = []
        for action in combo:
            if isAirborne and action == "j":
                correctedCombo += ["d"]
            else:
                correctedCombo += [action]
            
            if action in ["j", "s", "d", "u", "b"]:
                isAirborne = True
            elif action == "l":
                isAirborne = False
        
        # Corrects action sequences
        temp = correctedCombo
        correctedCombo = []
        i = 0
        while i in range(len(temp)):

            # space jam
            if i+2 < len(temp) and ("".join(temp[i:i+3]) in ["uwG", "usG"]):
                correctedCombo += ["u+w+G"]
                i += 3
                continue
                
            if i+1 < len(temp):
                sequence = "".join(temp[i:i+2])
                
                # space jam
                if sequence == "uG":
                    correctedCombo += ["u+w+G"]
                    i += 2
                    continue

                # double jump
                if sequence == "jd":
                    correctedCombo += ["d"]
                    i += 2
                    continue
                
                if i > 0 and temp[i] == "d" and temp[i - 1] in "jd":
                    i += 1
                    continue

                # saporens
                if sequence in ["pG", "kG", "oG"]:
                    correctedCombo += [sequence[0] + "+G"]
                    i += 2
                    continue

            correctedCombo += [temp[i]]
            i += 1
        
        return correctedCombo