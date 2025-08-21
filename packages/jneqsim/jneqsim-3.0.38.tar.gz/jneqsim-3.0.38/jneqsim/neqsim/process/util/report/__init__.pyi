
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import jneqsim.neqsim.process.equipment
import jneqsim.neqsim.process.processmodel
import jneqsim.neqsim.thermo.system
import typing



class Report:
    @typing.overload
    def __init__(self, processEquipmentBaseClass: jneqsim.neqsim.process.equipment.ProcessEquipmentBaseClass): ...
    @typing.overload
    def __init__(self, processModel: jneqsim.neqsim.process.processmodel.ProcessModel): ...
    @typing.overload
    def __init__(self, processModule: jneqsim.neqsim.process.processmodel.ProcessModule): ...
    @typing.overload
    def __init__(self, processModuleBaseClass: jneqsim.neqsim.process.processmodel.ProcessModuleBaseClass): ...
    @typing.overload
    def __init__(self, processSystem: jneqsim.neqsim.process.processmodel.ProcessSystem): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface): ...
    def generateJsonReport(self) -> java.lang.String: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.util.report")``.

    Report: typing.Type[Report]
