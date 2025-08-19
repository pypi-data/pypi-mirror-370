from quark.plugin_manager import factory

from quark_plugin_dwave.mis_qubo_mapping_dnx import MisQuboMappingDnx
from quark_plugin_dwave.simulated_annealer_dwave import SimulatedAnnealerDwave
from quark_plugin_dwave.tsp_qubo_mapping_dnx import TspQuboMappingDnx


def register() -> None:
    """
    Register all modules exposed to quark by this plugin.
    For each module, add a line of the form:
        factory.register("module_name", Module)

    The "module_name" will later be used to refer to the module in the configuration file.
    """
    factory.register("simulated_annealer_dwave", SimulatedAnnealerDwave)
    factory.register("tsp_qubo_mapping_dnx", TspQuboMappingDnx)
    factory.register("mis_qubo_mapping_dnx", MisQuboMappingDnx)
