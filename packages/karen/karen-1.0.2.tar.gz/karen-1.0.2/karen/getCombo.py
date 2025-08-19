from karen.evaluate import evaluate
from karen.classify import CLASSIFICATIONS

COMBO_SEQUENCES = {}

OVERRIDE_COMBO_SEQUENCES = {
    "Fast Panther" : "tGslptu",
    "Reverse Yo-Yo" : "tgdotu",
    "Master Manipulator" : "otslptu",
    "Further Beyond" : "otuwtotgwtuwtodto",
    "Yo-Yo" : "gdwtuwto",
    "Botched Yo-Yo" : "gdwtuototu",
    "Agni-Kai Yo-Yo" : "gdtutp",
    "Bald Slam" : "twGuot",
    "Vortex" : "uwtdGo",
    "In And Out" : "tbuwtg",
    "Hydro Combo" : "tgptalptu"
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
    "in&out" : "In And Out"
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
        
def listCombos():
    comboList = []
    sequenceList = []
    maxLength = 0

    for sequence in CLASSIFICATIONS:
        if not CLASSIFICATIONS[sequence] in comboList:
            comboList += [CLASSIFICATIONS[sequence]]
            sequenceList += [sequence]
            maxLength = max(maxLength, len(comboList[-1]))

    return "```\n" + "\n".join([comboList[i] + " " * (maxLength - len(comboList[i])) + " | " + sequenceList[i] for i in range(len(comboList))]) + "\n```"