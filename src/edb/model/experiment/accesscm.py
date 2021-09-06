from .base import Experiment


class ACCESSCM(Experiment):
    pass


class ACCESSCMScript(ACCESSCM):
    type = "access-cm-script"
    description = "ACCESS-CM 1.x run by CSIRO ksh script"


class ACCESSCMPayu(ACCESSCM):
    type = "access-cm-payu"
    description = "ACCESS-CM 1.x run by Payu"


class ACCESSCMRose(ACCESSCM):
    type = "access-cm-rose"
    description = "ACCESS-CM 2.x run by Rose/Cylc"
