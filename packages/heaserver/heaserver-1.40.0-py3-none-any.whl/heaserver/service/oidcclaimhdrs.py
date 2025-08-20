"""
Header constants for the Open ID Connect standard claims, and additional claims specific to HEA, that are set by the
HEA reverse proxy. The standard claim headers are prefixed by OIDC_CLAIM_.

Definitions of the standard claims may be found at
https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims. This document also specifies requirements
for using additional claims, which HEA follows.

The following constants contain the names of the claim headers:
SUB: the sub claim.
AUD: the aud (audience) claim.
CLAIM_HEADERS: a tuple containing all of the claim header names.
"""

SUB = 'OIDC_CLAIM_sub'  # currently logged in user ("subject")
AUD = 'OIDC_CLAIM_aud'  # intended user
AZP = 'OIDC_CLAIM_azp'  # client id
ISS = 'OIDC_CLAIM_iss'  # OIDC provider URL

CLAIM_HEADERS = (SUB, AUD, AZP, ISS)
