
"""
This file contains the non-constant variable requirements for specific quantities that are not quoted.
E.g. For calculating implied volatility we will need a price source, for calculating delta we will need an ivol source (which will then need a price source...).
We wouldn't need an expiry source since we already know that and we wouldn't need an underlying price source since that's already quoted. 

I have chosen this manner because otherwise we would be computing every quantity at runtime, which is obviously sub-optimal. 

"""

"ivol"  = "px_type"
"delta" = "ivol"
"gamma" = "ivol"
"vega" = "ivol"
"rho" = "ivol"
"theta" = "ivol"
"standardised_moneyness" = "ivol"