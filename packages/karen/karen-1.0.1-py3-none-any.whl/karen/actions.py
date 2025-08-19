import copy

PUNCH_SEQUENCE_MAX_DELAY = 90 # punch/kick must start <90 frames after last punch to advance the sequence
TRACER_ACTIVE_TIME = 4 * 60
TRACER_PROC_DAMAGE = 45
TRACER_MAX_TRAVEL_TIME = 10

BURN_TRACER_ACTIVE_TIME = 3 * 60
BURN_TRACER_DPS = 15
BURN_TRACER_BURN_TIME = 240
BURN_TRACER_MAX_TRAVEL_TIME = 3
BURN_TRACER_BACKFLIP_DISTANCE = 7


ACTION_NAMES = {
    "j" : "j", "jump" : "j",
    "d" : "d", "double jump" : "d", "dj" : "d",
    "l" : "l", "land" : "l",
    "p" : "p", "punch" : "p", "puncha" : "p",  "punchb" : "p", "meleepunch" : "p",  "meleepuncha" : "p",  "meleepunchb" : "p",
    "k" : "k", "kick" : "k",  "meleekick" : "k",
    "o" : "o", "overheadslam" : "o",  "overhead" : "o", "over" : "o", "oh" : "o",  "meleeoverhead" : "o",  "slam" : "o",
    "t" : "t", "tracer" : "t",  "webtracer" : "t",  "cluster" : "t",  "webcluster" : "t",
    "s" : "s", "swing" : "s", "webswing" : "s",  "highswing" : "s",  "lowswing" : "s", "z" : "s", "zip" : "s", "webzip" : "s",
    "a" : "a", "automatic swing" : "a", "autoswing" : "a", "automatic" : "a", "auto" : "a", "easyswing" : "a", "easy" : "a", "simple swing" : "a", "simple" : "a",
    "w" : "w", "whiff" : "w", "webwhiff" : "w", "swingwhiff" : "w", "wiff" : "w", "web wiff" : "w", "swing wiff" : "w",
    "g" : "g", "getoverhere" : "g", "goh" : "g", "webpull" : "g", "pull" : "g",
    "G" : "G", "getoverheretargeting" : "G", "getoverheretargetting" : "G", "goht" : "G",
    "u" : "u", "uppercut" : "u", "upper" : "u", "amazingcombo" : "u",
    "b" : "b", "burn" : "b", "burntracer" : "b", "burncluster" : "b", "fire" : "b", "firetracer" : "b", "firecluster" : "b", "flame" : "b", "flametracer" : "b", "flamecluster" : "b",
    "+" : "+", "/" : "+",

    "G+u" : "G+u", "f" : "G+u", "ffame" : "G+u", "ffamestack" : "G+u",
    "o+G" : "o+G", "saporen" : "o+G", "sap" : "o+G", "overheadsaporen" : "o+G", "ohsap" : "o+G",
    "p+G" : "p+G", "punchsaporen" : "p+G", "punchsap" : "p+G",
    "k+G" : "k+G","kicksaporen" : "k+G", "kicksap" : "k+G",
    "o+G+u" : "o+G+u", "F" : "o+G+u", "saporenffamestack" : "o+G+u", "sapffamestack" : "o+G+u", "sapffame" : "o+G+u", "overheadsaporenffamestack" : "o+G+u", "ohsapffamestack" : "o+G+u", "ohsapffame" : "o+G+u",
    "p+G+u" : "p+G+u", "punchsaporenffamestack" : "p+G+u", "punchsapffamestack" : "p+G+u", "punchsapffame" : "p+G+u",
    "k+G+u" : "k+G+u", "kicksaporenffamestack" : "k+G+u", "kicksapffamestack" : "k+G+u", "kicksapffame" : "k+G+u",
    "u+w+G" : "u+w+G", "J" : "u+w+G", "spacejam" : "u+w+G", "sj" : "u+w+G", "u+s+G" : "u+w+G", "u+G" : "u+w+G",
    "p+t" : "p+t", "r" : "p+t", "reversetrigger" : "p+t", "rt" : "p+t", "backflash" : "p+t", "punchreversetrigger" : "p+t", "punchbackflash" : "p+t", "punchrt" : "p+t", "punchblackflash" : "p+t", "blackflash" : "p+t",
    "k+t" : "k+t", "kickreversetrigger" : "k+t", "kickbackflash" : "k+t", "kickrt" : "k+t", "jashflash" : "k+t", "kickblackflash" : "k+t",
    "o+t" : "o+t", "overheadreversetrigger" : "o+t", "overheadbackflash" : "o+t", "overheadrt" : "o+t", "ohreversetrigger" : "o+t", "ohbackflash" : "o+t", "ohrt" : "o+t", "overheadblackflash" : "o+t", "ohblackflash" : "o+t",
    "p+o" : "p+o", "punchoverheadstack" : "p+o", "punchohstack" : "p+o", "unique3hitpunchstack" : "p+o", "uniquethreehitpunchstack" : "p+o","unique3hitpunch" : "p+o", "uniquethreehitpunch" : "p+o", "u3hpunchstack" : "p+o", "u3hpunch" : "p+o",
    "k+o" : "k+o", "kickoverheadstack" : "k+o", "kickohstack" : "k+o", "unique3hitkickstack" : "k+o", "uniquethreehitkickstack" : "k+o","unique3hitkick" : "k+o", "uniquethreehitkick" : "k+o", "u3hkickstack" : "k+o", "u3hkick" : "k+o",

    "shortplink" : "so",
    "longplink" : "wto", "plink" : "wto",
    "breadandbutter" : "tGu", "breadnbutter" : "tGu", "bnb" : "tGu",
    "uniquethreehit" : "wpp+o", "unique3hit" : "wpp+o", "u3h" : "wpp+o",
    "slytech" : "suo", "sly" : "suo"
}


class Action:
    name = ""

    damage = 0
    procsTracer = False
    procTime = 0

    damageTime = 0 # number of frames between activation and all damage registering
    firstDamageTime = 0 # for movestacks with multiple hits
    maxTravelTime = 0 # max number of added frames that projectile actions can take to travel
    range = 0 # purely for travel time calculations
    cancelTimes = {} # dict maps action to how many frames into this actions' animation the given action can be used
    
    chargeActivations = {} # the cooldown charges used and how long before the recharge starts from the action start time (for activeTimer)
    endActivations = {} # some abilities cause others to start recharging immediately
    awaitCharges = {} # which cooldown charges have to be ready to use during the action, and how long into the action they're used (useful for stacks)

    def __init__(self, name, damage = 0, procsTracer=False, procTime = 0, damageTime = 0, firstDamageTime = 0, maxTravelTime = 0, range = 0, cancelTimes={}, chargeActivations={}, endActivations={}, awaitCharges={}):
        self.name = name
        self.damage = damage
        self.procsTracer = procsTracer
        self.procTime = damageTime if procTime == 0 else procTime
        self.damageTime = damageTime
        self.firstDamageTime = firstDamageTime if firstDamageTime != 0 else damageTime
        self.maxTravelTime = maxTravelTime
        self.range = range
        self.cancelTimes = cancelTimes
        self.chargeActivations = chargeActivations
        self.cancelTimes[""] = damageTime # time to transition to the end of the combo is damageTime
        self.endActivations = endActivations
        self.awaitCharges = awaitCharges


ACTIONS = {

    "p" : Action (
        name = "Punch",
        damage = 25, 
        procsTracer = True, 
        
        damageTime = 14,
        range = 3,
        cancelTimes = {
            "p" : 23,
            "k" : 23,
            "o" : 23,
            "t" : 11,
            "s" : 11,
            "a" : 11,
            "w" : 11,
            "g" : 11,
            "G" : 11,
            "u" : 11,
            "b" : 11
        }
    ),

    "k" : Action (
        name = "Kick",
        damage = 40, 
        procsTracer = True,
        
        damageTime = 24,
        range = 4,
        cancelTimes = {
            "p" : 49,
            "k" : 49,
            "o" : 49,
            "t" : 22,
            "s" : 22,
            "a" : 22,
            "w" : 22,
            "g" : 22,
            "G" : 22,
            "u" : 22,
            "b" : 22
        }
    ),

    "o" : Action (
        name = "Overhead",
        damage = 55, 
        procsTracer = True, 
        
        damageTime = 38,
        range = 4,
        cancelTimes = {
            "p" : 53,
            "k" : 53,
            "o" : 53,
            "t" : 33,
            "s" : 33,
            "a" : 33,
            "w" : 33,
            "g" : 33,
            "G" : 33,
            "u" : 33,
            "b" : 33
        }
    ),

    "t" : Action (
        name = "Tracer",
        damage = 30, 
        
        damageTime = 12,
        range = 20,
        cancelTimes = {
            "p" : 30,
            "k" : 30,
            "o" : 30,
            "t" : 30,
            "s" : 6,
            "a" : 6,
            "w" : 6,
            "g" : 6,
            "G" : 6,
            "u" : 6,
            "b" : 6
        },

        chargeActivations = { "t" : 0 },
        endActivations = ["s"],
        awaitCharges = { "t" : 0 }
    ),

    "s" : Action (
        name = "Swing",
        
        maxTravelTime = 7,
        range = 30,
        cancelTimes = {
            "p" : 10,
            "k" : 10,
            "o" : 10,
            "t" : 10,
            "s" : 10,
            "a" : 10,
            "w" : 10,
            "g" : 1,
            "G" : 1,
            "u" : 1,
            "b" : 1
        },

        chargeActivations = { "s" : 10 },
        endActivations = ["g", "u", "b"],
        awaitCharges = { "s" : 0 }
    ),

    "a" : Action (
        name = "Auto Swing",
        
        cancelTimes = {
            "p" : 1,
            "k" : 1,
            "o" : 1,
            "t" : 1,
            "s" : 19,
            "a" : 19,
            "w" : 19,
            "g" : 1,
            "G" : 1,
            "u" : 1,
            "b" : 1
        },

        chargeActivations = { "s" : 1 },
        endActivations = ["g", "u", "b"],
    ),

    "w" : Action (
        name = "Whiff",
        
        cancelTimes = {
            "p" : 27,
            "k" : 27,
            "o" : 27,
            "t" : 10,
            "s" : 53,
            "a" : 25,
            "w" : 53,
            "g" : 1,
            "G" : 1,
            "u" : 1,
            "b" : 1
        },

        chargeActivations = { "s" : 53 },
        endActivations = ["g", "u", "b"],
        awaitCharges = { "s" : 0 }
    ),

    "g" : Action (
        name = "Get Over Here",
        damage = 25,
        
        damageTime = 17,
        maxTravelTime = 12,
        range = 20,
        cancelTimes = {
            "p" : 50,
            "k" : 50,
            "o" : 50,
            "t" : 46,
            "s" : 14,
            "a" : 14,
            "w" : 14,
            "g" : 102,
            "G" : 50,
            "u" : 47,
            "b" : 14
        },

        chargeActivations = { "g" : 102 },
        awaitCharges = { "g" : 0 }
    ),

    "G" : Action (
        name = "Get Over Here Targeting",
        damage = 55,

        damageTime = 37,
        maxTravelTime = 13,
        range = 24,
        cancelTimes = {
            "p" : 61,
            "k" : 61,
            "o" : 61,
            "t" : 61,
            "s" : 28,
            "a" : 28,
            "w" : 28,
            "g" : 61,
            "G" : 61,
            "u" : 32,
            "b" : 28
        },

        chargeActivations = { "g" : 61 },
        awaitCharges = { "g" : 0 }
    ),

    "u" : Action (
        name = "Uppercut",
        damage = 60, 
        procsTracer = True,
        
        damageTime = 23,
        range = 4,
        cancelTimes = {
            "p" : 48,
            "k" : 48,
            "o" : 48,
            "t" : 56,
            "s" : 19,
            "a" : 19,
            "w" : 19,
            "g" : 48,
            "G" : 48,
            "u" : 70,
            "b" : 19
        },

        chargeActivations = { "u" : 70 },
        awaitCharges = { "u" : 0 }
    ),

    "b" : Action (
        name = "Burn Tracer",
        damage = 30,
        
        damageTime = 17,
        range = 8,
        cancelTimes = {
            "p" : 30,
            "k" : 30,
            "o" : 30,
            "t" : 10,
            "s" : 10,
            "a" : 10,
            "w" : 10,
            "g" : 10,
            "G" : 10,
            "u" : 1,
            "b" : 70
        },

        chargeActivations = { "b" : 70 },
        awaitCharges = { "b" : 0 }
    )
}


# generate movestack timings procedurally to simplify code/maintenence
def loadMoveStacks(): 

    # ffamestack (G+u)
    for action in ACTIONS:
        ACTIONS[action].cancelTimes["G+u"] = ACTIONS[action].cancelTimes["G"]

    ffamestackCancelTimes = ACTIONS["G"].cancelTimes.copy()
    for key in ffamestackCancelTimes:
        ffamestackCancelTimes[key] = max(ACTIONS["u"].cancelTimes[key] + 1, ffamestackCancelTimes[key])

    ACTIONS["G+u"] = Action (
        name = "FFAmestack",
        damage = ACTIONS["G"].damage + ACTIONS["u"].damage,
        procsTracer = True,
        procTime = ACTIONS["u"].procTime + 1,
        damageTime = ACTIONS["G"].damageTime,
        firstDamageTime = ACTIONS["u"].firstDamageTime + 1,
        maxTravelTime = int(ACTIONS["G"].maxTravelTime * 4 / 20),
        cancelTimes = ffamestackCancelTimes,
        chargeActivations = {
            "g" : ACTIONS["G"].chargeActivations["g"],
            "u" : ACTIONS["u"].chargeActivations["u"] + 1
        },
        awaitCharges = { 
            "g" : 0,
            "u" : 1 
        }
    )

    # saporen (p+G, k+G, o+G)
    for action in ACTIONS:
        ACTIONS[action].cancelTimes["p+G"] = ACTIONS[action].cancelTimes["p"]
        ACTIONS[action].cancelTimes["k+G"] = ACTIONS[action].cancelTimes["k"]
        ACTIONS[action].cancelTimes["o+G"] = ACTIONS[action].cancelTimes["o"]

    punchSaporenCancelTimes = ACTIONS["G"].cancelTimes.copy()
    kickSaporenCancelTimes = ACTIONS["G"].cancelTimes.copy()
    overheadSaporenCancelTimes = ACTIONS["G"].cancelTimes.copy()
    for key in punchSaporenCancelTimes:
        punchSaporenCancelTimes[key] += ACTIONS["p"].cancelTimes["G"] - 1
        kickSaporenCancelTimes[key] += ACTIONS["k"].cancelTimes["G"] - 1
        overheadSaporenCancelTimes[key] += ACTIONS["o"].cancelTimes["G"]  -1

    ACTIONS["p+G"] = Action (
        name = "Punch Saporen",
        damage = ACTIONS["p"].damage + ACTIONS["G"].damage,
        procsTracer = True,
        procTime = ACTIONS["p"].procTime,
        damageTime = ACTIONS["p"].cancelTimes["G"] + ACTIONS["G"].damageTime - 1,
        firstDamageTime = ACTIONS["p"].damageTime,
        maxTravelTime = int(ACTIONS["G"].maxTravelTime * ACTIONS["p"].range / ACTIONS["G"].range),
        cancelTimes = punchSaporenCancelTimes,
        chargeActivations = {
            "g" : ACTIONS["p"].cancelTimes["G"] + ACTIONS["G"].chargeActivations["g"] - 1
        },
        awaitCharges = { 
            "g" :  ACTIONS["p"].cancelTimes["G"] - 1
        }
    )

    ACTIONS["k+G"] = Action (
        name = "Kick Saporen",
        damage = ACTIONS["k"].damage + ACTIONS["G"].damage,
        procsTracer = True,
        procTime = ACTIONS["k"].procTime,
        damageTime = ACTIONS["k"].cancelTimes["G"] + ACTIONS["G"].damageTime - 1,
        firstDamageTime = ACTIONS["k"].damageTime,
        maxTravelTime = int(ACTIONS["G"].maxTravelTime * ACTIONS["k"].range / ACTIONS["G"].range),
        cancelTimes = kickSaporenCancelTimes,
        chargeActivations = {
            "g" : ACTIONS["k"].cancelTimes["G"] + ACTIONS["G"].chargeActivations["g"] - 1
        },
        awaitCharges = { 
            "g" :  ACTIONS["k"].cancelTimes["G"] - 1
        }
    )

    ACTIONS["o+G"] = Action (
        name = "Overhead Saporen",
        damage = ACTIONS["o"].damage + ACTIONS["G"].damage,
        procsTracer = True,
        procTime = ACTIONS["o"].procTime,
        damageTime = ACTIONS["o"].cancelTimes["G"] + ACTIONS["G"].damageTime - 1,
        firstDamageTime = ACTIONS["o"].damageTime,
        maxTravelTime = int(ACTIONS["G"].maxTravelTime * ACTIONS["o"].range / ACTIONS["G"].range),
        cancelTimes = overheadSaporenCancelTimes,
        chargeActivations = {
            "g" : ACTIONS["o"].cancelTimes["G"] + ACTIONS["G"].chargeActivations["g"] - 1
        },
        awaitCharges = { 
            "g" :  ACTIONS["o"].cancelTimes["G"] - 1
        }
    )

    # saporen ffamestack (p+G+u, k+G+u, o+G+u)
    for action in ACTIONS:
        ACTIONS[action].cancelTimes["p+G+u"] = ACTIONS[action].cancelTimes["p"]
        ACTIONS[action].cancelTimes["k+G+u"] = ACTIONS[action].cancelTimes["k"]
        ACTIONS[action].cancelTimes["o+G+u"] = ACTIONS[action].cancelTimes["o"]

    punchSaporenFfamestackCancelTimes = ACTIONS["G+u"].cancelTimes.copy()
    kickSaporenFfamestackCancelTimes = ACTIONS["G+u"].cancelTimes.copy()
    overheadSaporenFfamestackCancelTimes = ACTIONS["G+u"].cancelTimes.copy()
    for key in punchSaporenFfamestackCancelTimes:
        punchSaporenFfamestackCancelTimes[key] += ACTIONS["p"].cancelTimes["G"] - 1
        kickSaporenFfamestackCancelTimes[key] += ACTIONS["k"].cancelTimes["G"] - 1
        overheadSaporenFfamestackCancelTimes[key] += ACTIONS["o"].cancelTimes["G"] - 1

    ACTIONS["p+G+u"] = Action (
        name = "Punch Saporen FFAmestack",
        damage = ACTIONS["p"].damage + ACTIONS["G"].damage + ACTIONS["u"].damage,
        procsTracer = True,
        procTime = ACTIONS["p"].procTime,
        damageTime = ACTIONS["p"].cancelTimes["G"] + ACTIONS["G+u"].damageTime -1,
        firstDamageTime = ACTIONS["p"].damageTime,
        maxTravelTime = int(ACTIONS["G"].maxTravelTime * ACTIONS["p"].range / ACTIONS["G"].range),
        cancelTimes = punchSaporenFfamestackCancelTimes,
        chargeActivations = {
            "g" : ACTIONS["p"].cancelTimes["G"] + ACTIONS["G"].chargeActivations["g"] - 1,
            "u" : ACTIONS["p"].cancelTimes["G"] + ACTIONS["u"].chargeActivations["u"]
        },
        awaitCharges = { 
            "g" :  ACTIONS["p"].cancelTimes["G"] - 1,
            "u" : ACTIONS["p"].cancelTimes["G"]
        }
    )

    ACTIONS["k+G+u"] = Action (
        name = "Kick Saporen FFAmestack",
        damage = ACTIONS["k"].damage + ACTIONS["G"].damage + ACTIONS["u"].damage,
        procsTracer = True,
        procTime = ACTIONS["k"].procTime,
        damageTime = ACTIONS["k"].cancelTimes["G"] + ACTIONS["G+u"].damageTime - 1,
        firstDamageTime = ACTIONS["k"].damageTime,
        maxTravelTime = int(ACTIONS["G"].maxTravelTime * ACTIONS["k"].range / ACTIONS["G"].range),
        cancelTimes = kickSaporenFfamestackCancelTimes,
        chargeActivations = {
            "g" : ACTIONS["k"].cancelTimes["G"] + ACTIONS["G"].chargeActivations["g"] - 1,
            "u" : ACTIONS["k"].cancelTimes["G"] + ACTIONS["u"].chargeActivations["u"]
        },
        awaitCharges = { 
            "g" :  ACTIONS["k"].cancelTimes["G"] - 1,
            "u" : ACTIONS["k"].cancelTimes["G"]
        }
    )

    ACTIONS["o+G+u"] = Action (
        name = "Overhead Saporen FFAmestack",
        damage = ACTIONS["o"].damage + ACTIONS["G"].damage + ACTIONS["u"].damage,
        procsTracer = True,
        procTime = ACTIONS["o"].procTime,
        damageTime = ACTIONS["o"].cancelTimes["G"] + ACTIONS["G+u"].damageTime - 1,
        firstDamageTime = ACTIONS["o"].damageTime,
        maxTravelTime = int(ACTIONS["G"].maxTravelTime * ACTIONS["o"].range / ACTIONS["G"].range),
        cancelTimes = overheadSaporenFfamestackCancelTimes,
        chargeActivations = {
            "g" : ACTIONS["o"].cancelTimes["G"] + ACTIONS["G"].chargeActivations["g"] - 1,
            "u" : ACTIONS["o"].cancelTimes["G"] + ACTIONS["u"].chargeActivations["u"]
        },
        awaitCharges = { 
            "g" :  ACTIONS["o"].cancelTimes["G"] - 1,
            "u" : ACTIONS["o"].cancelTimes["G"]
        }
    )

    # space jam (u+w+G)
    for action in ACTIONS:
        ACTIONS[action].cancelTimes["u+w+G"] = ACTIONS[action].cancelTimes["u"]

    spacejamCancelTimes = ACTIONS["G"].cancelTimes
    for key in spacejamCancelTimes:
        spacejamCancelTimes[key] += ACTIONS["u"].cancelTimes["s"] + ACTIONS["s"].cancelTimes["G"]

    ACTIONS["u+w+G"] = Action (
        name = "Space Jam",
        damage = ACTIONS["G"].damage + ACTIONS["u"].damage,
        procsTracer = True,
        procTime = ACTIONS["u"].procTime,
        damageTime =  ACTIONS["u"].cancelTimes["s"] + ACTIONS["s"].cancelTimes["G"] + ACTIONS["G"].damageTime,
        firstDamageTime = ACTIONS["u"].damageTime,
        maxTravelTime = int(ACTIONS["G"].maxTravelTime * ACTIONS["u"].range / ACTIONS["G"].range),
        cancelTimes = spacejamCancelTimes,
        chargeActivations = {
            "u" : ACTIONS["u"].cancelTimes["u"],
            "g" : ACTIONS["u"].cancelTimes["s"] + ACTIONS["s"].cancelTimes["G"] + ACTIONS["G"].chargeActivations["g"]
        },
        awaitCharges = { 
            "u" :  0,
            "s" : ACTIONS["u"].cancelTimes["s"],
            "g" : ACTIONS["u"].cancelTimes["s"]
        }
    )

    # reverse trigger (p+t, k+t, o+t) 
    for action in ACTIONS:
        ACTIONS[action].cancelTimes["p+t"] = ACTIONS[action].cancelTimes["p"]
        ACTIONS[action].cancelTimes["k+t"] = ACTIONS[action].cancelTimes["k"]
        ACTIONS[action].cancelTimes["o+t"] = ACTIONS[action].cancelTimes["o"]

    punchReverseTriggerCancelTimes = ACTIONS["t"].cancelTimes.copy()
    kickReverseTriggerCancelTimes = ACTIONS["t"].cancelTimes.copy()
    overheadReverseTriggerCancelTimes = ACTIONS["t"].cancelTimes.copy()
    for action in punchReverseTriggerCancelTimes:
        punchReverseTriggerCancelTimes[action] += ACTIONS["p"].damageTime - 1 - ACTIONS["t"].damageTime
        kickReverseTriggerCancelTimes[action] += ACTIONS["k"].damageTime - 1 - ACTIONS["t"].damageTime
        overheadReverseTriggerCancelTimes[action] += ACTIONS["o"].damageTime - 1 - ACTIONS["t"].damageTime

    ACTIONS["p+t"] = Action (
        name = "Punch Reverse Trigger",
        damage = ACTIONS["p"].damage + ACTIONS["t"].damage,
        procsTracer = True,
        procTime = 0,
        damageTime = ACTIONS["p"].damageTime,
        firstDamageTime = ACTIONS["p"].damageTime - 1,
        cancelTimes = punchReverseTriggerCancelTimes,
        chargeActivations = {
            "t" : ACTIONS["p"].damageTime - 1  - ACTIONS["t"].damageTime + ACTIONS["t"].chargeActivations["t"]
        },
        awaitCharges = { 
            "t" :  ACTIONS["p"].damageTime - 1 - ACTIONS["t"].damageTime
        }
    )

    ACTIONS["k+t"] = Action (
        name = "Kick Reverse Trigger",
        damage = ACTIONS["k"].damage + ACTIONS["t"].damage,
        procsTracer = True,
        procTime = 0,
        damageTime = ACTIONS["k"].damageTime,
        firstDamageTime = ACTIONS["k"].damageTime - 1,
        cancelTimes = kickReverseTriggerCancelTimes,
        chargeActivations = {
            "t" : ACTIONS["k"].damageTime - 1  - ACTIONS["t"].damageTime + ACTIONS["t"].chargeActivations["t"]
        },
        awaitCharges = { 
            "t" :  ACTIONS["k"].damageTime - 1 - ACTIONS["t"].damageTime
        }
    )

    ACTIONS["o+t"] = Action (
        name = "Overhead Reverse Trigger",
        damage = ACTIONS["o"].damage + ACTIONS["t"].damage,
        procsTracer = True,
        procTime = 0,
        damageTime = ACTIONS["o"].damageTime,
        firstDamageTime = ACTIONS["o"].damageTime - 1,
        cancelTimes = overheadReverseTriggerCancelTimes,
        chargeActivations = {
            "t" : ACTIONS["o"].damageTime - 1  - ACTIONS["t"].damageTime + ACTIONS["t"].chargeActivations["t"]
        },
        awaitCharges = { 
            "t" :  ACTIONS["o"].damageTime - 1 - ACTIONS["t"].damageTime
        }
    )

    # unique 3 hit (p+o, k+o)
    for action in ACTIONS:
        ACTIONS[action].cancelTimes["p+o"] = ACTIONS[action].cancelTimes["p"]
        ACTIONS[action].cancelTimes["k+o"] = ACTIONS[action].cancelTimes["k"]

    ACTIONS["p+o"] = Action (
        name = "Punch OH Stack",
        damage = ACTIONS["p"].damage + ACTIONS["o"].damage,
        procsTracer = True,
        procTime = ACTIONS["p"].procTime,
        damageTime = ACTIONS["o"].damageTime,
        firstDamageTime = ACTIONS["p"].damageTime,
        cancelTimes = ACTIONS["o"].cancelTimes.copy()
    )

    ACTIONS["k+o"] = Action (
        name = "Kick OH Stack",
        damage = ACTIONS["k"].damage + ACTIONS["o"].damage,
        procsTracer = True,
        procTime = ACTIONS["k"].procTime,
        damageTime = ACTIONS["o"].damageTime,
        firstDamageTime = ACTIONS["k"].damageTime,
        cancelTimes = ACTIONS["o"].cancelTimes.copy()
    )

    ACTIONS["j"] = Action (
        name = "Jump",
        cancelTimes = { a : 0 for a in ACTIONS }
    )

    ACTIONS["d"] = Action (
        name = "Double Jump",
        cancelTimes = { a : 0 for a in ACTIONS }
    )

    ACTIONS["l"] = Action (
        name = "Land",
        cancelTimes = { a : 0 for a in ACTIONS }
    )