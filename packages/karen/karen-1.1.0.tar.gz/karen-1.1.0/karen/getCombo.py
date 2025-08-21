from karen.evaluate import evaluate
from karen.classify import CLASSIFICATIONS
from karen.combo import getComboSequence, simplify

COMBO_SEQUENCES = {}

OVERRIDE_COMBO_SEQUENCES = {
    "Reverse Yo-Yo" : "tgdotu",
    "Further Beyond" : "otuwtotgwtuwtodto",
    "Yo-Yo" : "gdwtuwto",
    "Pre-Tag Yo-Yo" : "tgduwto",
    "Botched Yo-Yo" : "gdwtuototu",
    "Agni-Kai Yo-Yo" : "gdtutp",
    "Vortex" : "uwtdGo",
    "Hydro Combo" : "tgptaptu",
    "Alternate Hydro Combo" : "tptaptu",
    "Burn Weave" : "tGwtbu",
    "Evil Combo" : "o+tgatu",
}

COMBO_ALIASES = {
    "bnb" : "Bread & Butter (BnB)",
    "bnbplink" : "BnB Long Plink",
    "fishing" : "Fishing Combo / Sekkombo",
    "fish" : "Fishing Combo / Sekkombo",
    "sekkombo" : "Fishing Combo / Sekkombo",
    "sekombo" : "Fishing Combo / Sekkombo",
    "gripkickrip" : "Grip Kick Rip (GKR)",
    "gkr" : "Grip Kick Rip (GKR)",
    "ohburst" : "Overhead Burst",
    "fantastic" : "Fantastic Killer",
    "sapstack" : "Saporen FFAmestack",
    "agnikai" : "Agni-Kai Yo-Yo",
    "bald" : "Bald Slam",
    "skypull" : "Yo-Yo",
    "spc" : "Yo-Yo",
    "skyyoink" : "Yo-Yo",
    "preyoyo" : "Pre-Tag Yo-Yo",
    "tagyoyo" : "Pre-Tag Yo-Yo",
    "althydro" : "Alternate Hydro Combo",

    "burnbnb" : "Burn BnB / Fadeaway",
    "fadeaway" : "Burn BnB / Fadeaway",
    "burnohburst" : "Burn Overhead Burst",
    "burnoverhead" : "Burn Overhead Burst",
    "burnoh" : "Burn Overhead Burst",
    "friedfish" : "Fried Fish / Firehook",
    "fried" : "Fried Fish / Firehook",
    "burnsekkombo" : "Fried Fish / Firehook",
    "burnsekombo" : "Fried Fish / Firehook",
    "firehook" : "Fried Fish / Firehook",
    "innout" : "In And Out",
    "in&out" : "In And Out",
}

def loadComboSequences():
    for sequence in CLASSIFICATIONS:
        COMBO_SEQUENCES[CLASSIFICATIONS[sequence]] = sequence
    for combo in OVERRIDE_COMBO_SEQUENCES:
        COMBO_SEQUENCES[combo] = OVERRIDE_COMBO_SEQUENCES[combo]

    for sequence in CLASSIFICATIONS:
        filterName = CLASSIFICATIONS[sequence].replace(" ", "").replace("-", "").lower()
        if len(filterName) > 5 and filterName[-5:] == "combo":
            filterName = filterName[:-5]
        COMBO_ALIASES[filterName] = CLASSIFICATIONS[sequence]

    for name in COMBO_ALIASES.copy():
        if "bnb" in name:
            COMBO_ALIASES[name.replace("bnb", "b&b")] = COMBO_ALIASES[name]
            COMBO_ALIASES[name.replace("bnb", "bandb")] = COMBO_ALIASES[name]
            COMBO_ALIASES[name.replace("bnb", "breadnbutter")] = COMBO_ALIASES[name]
            COMBO_ALIASES[name.replace("bnb", "bread&butter")] = COMBO_ALIASES[name]
            COMBO_ALIASES[name.replace("bnb", "breadandbutter")] = COMBO_ALIASES[name]


def getCombo(name):
    if len(COMBO_SEQUENCES) == 0:
        loadComboSequences()

    filterName = name.replace(" ", "").replace("-", "").lower()
    if len(filterName) > 5 and filterName[-5:] == "combo":
            filterName = filterName[:-5]

    if not filterName in COMBO_ALIASES or not COMBO_ALIASES[filterName] in COMBO_SEQUENCES:
        return "```\nERROR: Combo not found\n```"
    
    return evaluate(COMBO_SEQUENCES[COMBO_ALIASES[filterName]], simpleMode=True)
        
def listCombos(inputString=""):

    # resolve the initial sequence
    comboSequence = getComboSequence(inputString) + [""]
    initialSequence = "".join(comboSequence)
    reducedSequence = initialSequence.replace("j", "").replace("d", "").replace("l", "").replace("a", "s")
    simpleSequence = "".join(simplify(comboSequence))
    reducedSimpleSequence = simpleSequence.replace("j", "").replace("d", "").replace("l", "").replace("a", "s")

    if len(COMBO_SEQUENCES) == 0:
        loadComboSequences()
    comboList = []
    sequenceList = []
    maxLength = 0

    for combo in COMBO_SEQUENCES:
        if len(COMBO_SEQUENCES[combo]) >= len(reducedSequence) and COMBO_SEQUENCES[combo][:len(reducedSequence)] == reducedSequence:
            comboList += [combo]
            sequenceList += [initialSequence + COMBO_SEQUENCES[combo][len(reducedSequence):]]
            maxLength = max(maxLength, len(comboList[-1]))
        elif len(COMBO_SEQUENCES[combo]) >= len(reducedSimpleSequence) and COMBO_SEQUENCES[combo][:len(reducedSimpleSequence)] == reducedSimpleSequence:
            comboList += [combo]
            sequenceList += [simpleSequence + COMBO_SEQUENCES[combo][len(reducedSimpleSequence):]]
            maxLength = max(maxLength, len(comboList[-1]))

    return "### Karen Combo List\n" + ("" if reducedSequence == "" else f"Requirement: starts with \"{initialSequence}\"\n") + "```\n" + "\n".join([comboList[i] + " " * (maxLength - len(comboList[i])) + " | " + sequenceList[i] for i in range(len(comboList))]) + "\n```"