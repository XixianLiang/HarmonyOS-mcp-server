# -*- coding: utf-8 -*-


class DeviceError(Exception):
    pass

class DeviceNotFoundError(DeviceError):
    pass

class DeviceAmbigiousError(DeviceError):
    pass

class HdcError(Exception):
    pass