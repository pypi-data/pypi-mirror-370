CLASSIFICATIONS = {
    "tGu" : "Bread & Butter (BnB)",
    "tGuwtt" : "BnB Tracers",
    "tGuso" : "BnB Short Plink",
    "tGuwto" : "BnB Long Plink",
    "tGupt" : "BnB Punch",
    "tGutp" : "Reverse Panther",
    "tGuwpp+o" : "BnB U3H",
    "tGwtuwt" : "Weave Combo",
    "tGptu" : "Panther Combo",
    "tGsptu" : "Fast Panther",
    "tptu" : "One Two",
    "totu" : "Overhead One Two",
    "tgptu" : "Fishing Combo / Sekkombo",
    "tgotu" : "Reverse Yo-Yo",
    "tgktu" : "Grip Kick Rip (GKR)",
    "otG+u" : "Fast FFAmestack",
    "otuwtg" : "Overhead Burst",
    "otsptu" : "Master Manipulator",
    "otgwtu" : "Master Masher",
    "otgwtuwto" : "Fantastic Killer",
    "otuwtotgwtuwtoto" : "Further Beyond",
    "to+G+u" : "Saporen FFAmestack",
    "gwtuwto" : "Yo-Yo",
    "gwtuototu" : "Botched Yo-Yo",
    "gtutp" : "Agni-Kai Yo-Yo",
    "tuwtGu" : "Driveby",
    "twGuot" : "Bald Slam",
    "uwtGo" : "Vortex",
    "tgptsptu" : "Hydro Combo",

    "tGbu" : "Burn BnB / Fadeaway",
    "otbu" : "Burn Overhead Burst",
    "tgptbu" : "Fried Fish / Firehook",
    "tbuwtg" : "In And Out",
    "tptbu" : "Burn One Two",
    "tGbtu" : "Burn Weave",
    "tGwtbu" : "Burn Weave"
}

def classify(comboString):
    comboString = comboString.replace("j", "").replace("d", "").replace("l", "") # doesnt consider jumping/landing in classificaiton
    comboString = comboString.replace("a", "s") # autoswings are equivalent to swings for classification purposes

    if comboString in CLASSIFICATIONS:
        return CLASSIFICATIONS[comboString]
    
    # adding tracer to the end is considered the same combo
    if len(comboString) >= 1 and comboString[-1] == "t" and comboString[:-1] in CLASSIFICATIONS:
        return CLASSIFICATIONS[comboString[:-1]]
    if len(comboString) >= 2 and comboString[-2:] == "wt" and comboString[:-2] in CLASSIFICATIONS:
        return CLASSIFICATIONS[comboString[:-2]]
    
    # attempts classification assuming swing cancels are typos of whiff cancels
    if "st" in comboString:
        attempt = classify(comboString.replace("st", "wt")) 
        if attempt != "Undocumented":
            return "Wasteful " + attempt
    
    # attempts to classify as a slow variation of another combo by adding whiff cancels
    improveString = comboString.replace("ut", "uwt").replace("gt", "gwt").replace("ug", "uwg")
    if improveString != comboString:
        attempt = classify(improveString)
        if attempt != "Undocumented":
            return "Slow " + attempt
    
    return "Undocumented"