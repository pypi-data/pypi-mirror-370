def legend_colourmap_getter(legend_labels):
    
    list_of_colours = ["white", "red", "blue", "green", "yellow", "cyan", "magenta",
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
                        "lightgoldenrod", "darkgoldenrod",
                        ]      
    colourmap = {}
    for expiry, colour in zip(legend_labels, list_of_colours):
         colourmap[expiry] = colour
    return colourmap


class MetricRounder:
     def __init__(self, metric_type):
          self.metric_type=metric_type

