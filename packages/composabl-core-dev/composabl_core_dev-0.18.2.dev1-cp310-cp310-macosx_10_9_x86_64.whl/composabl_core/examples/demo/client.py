# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core.networking.sim.server_composabl import ServerComposabl


class Client:
    def __init__(self, server_proxy: ServerComposabl):
        self.s = server_proxy

    def Close(self, req):
        return {}

    def Make(self, req):
        return {}

    def ActionSpaceSample(self, req):
        return self.s.ActionSpaceSample(req, {})

    def Reset(self, req):
        return self.s.Reset(req, {})

    def Step(self, req):
        return self.s.Step(req, {})

    def SensorSpaceInfo(self, req):
        return self.s.SensorSpaceInfo(req, {})

    def ActionSpaceInfo(self, req):
        return self.s.ActionSpaceInfo(req, {})

    def SetScenario(self, req):
        self.s.SetScenario(req, {})

    def GetScenario(self, req):
        return self.s.GetScenario(req, {})
