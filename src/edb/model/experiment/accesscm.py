from .base import Experiment


class ACCESSCM(Experiment):
    pass


class ACCESSCMScript(ACCESSCM):
    type = "access-cm-script"


class ACCESSCMPayu(ACCESSCM):
    type = "access-cm-payu"


class ACCESSCMRose(ACCESSCM):
    type = "access-cm-rose"
