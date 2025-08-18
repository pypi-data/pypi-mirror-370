def legend_colour_getter(expiry_list):
    
    list_of_colours = ["white", "red","blue",  "green", "yellow", "cyan", "magenta",
    "orange", "purple", "pink", "brown",
    
    "lightgray", "darkgray", "dimgray",
    "lightred", "darkred",
    "lightgreen", "darkgreen", "lime", "limegreen",
    "lightblue", "darkblue", "navy",
    "lightcyan", "darkcyan", "teal",
    "lightmagenta", "darkmagenta", "fuchsia",
    "lightyellow", "darkyellow", "gold", "goldenrod", "khaki",
    "lightpink", "darkpink", "hotpink",
    "lightsalmon", "darksalmon", "coral",
    "lightgoldenrod", "darkgoldenrod",]
    
    colourmap = {}
    for expiry, colour in zip(expiry_list, list_of_colours):
         colourmap[expiry] = colour
    return colourmap