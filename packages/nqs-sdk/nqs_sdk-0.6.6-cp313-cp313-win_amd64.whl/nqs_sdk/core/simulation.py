import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from nqs_sdk.interfaces import ProtocolFactory
from nqs_sdk.nqs_sdk import ProtocolFactoryAdapter, Simulator, SimulatorBuilder

from .config import ConfigLoader


class Simulation:
    """
    Main orchestrator for running simulations.

    This class serves as the primary interface for users to configure, build, and execute
    simulations involving multiple DeFi protocols. It handles the coordination between
    protocol factories, configuration loading, and simulation execution.

    Protocols and configuration are provided during initialization, and the simulation
    can be run multiple times with different parameters.

    Attributes:
        protocols: List of protocol factories or protocol factory adapters that define the DeFi protocols to simulate
        config: Configuration data (file path, dict, or YAML/JSON content)
        simulator: Internal rust-based simulator instance (built lazily)
    """

    def __init__(
        self,
        protocols: Union[ProtocolFactory | ProtocolFactoryAdapter, List[ProtocolFactory | ProtocolFactoryAdapter]],
        config: Union[str, dict, Path],
        namespace: Optional[str] = None,
    ):
        """
        Initialize a new simulation with specified protocols and configuration.

        Args:
            protocols: Single ProtocolFactory or ProtocolFactoryAdapter,
                       or list of ProtocolFactorys or ProtocolFactoryAdapters defining
                       the protocols to include in the simulation
            config: Configuration for the simulation. Can be:
                   - Path to a YAML/JSON configuration file
                   - Dictionary containing configuration parameters
                   - String containing YAML/JSON configuration content

        Example:
            >>> from nqs_sdk import Simulation
            >>> from nqs_sdk.protocols import UniswapV3Factory
            >>> from nqs_sdk_extension.protocols import CompoundV2Factory
            >>> uniswap = UniswapV3Factory()
            >>> compound = CompoundV2Factory()
            >>> sim = Simulation([uniswap, compound], "config.yaml")
        """
        self.protocols = [protocols] if not isinstance(protocols, list) else protocols
        self.config = config
        self.simulator = None
        self.is_backtest = False  # FIXME: get this from binding instead
        self._build()

    def _build(self) -> None:
        """
        Internal method to construct the simulation from protocols and configuration.

        This method:
        1. Loads and parses the configuration (YAML or JSON)
        2. Creates a SimulatorBuilder with the parsed configuration
        3. Registers all protocol factories with the builder
        4. Builds the final simulator instance

        Raises:
            ValueError: If configuration format is invalid
            FileNotFoundError: If configuration file doesn't exist
        """
        config_content, config_format = ConfigLoader.load(self.config)

        if isinstance(config_content, str):
            self.is_backtest = "backtest" in config_content.lower()
        elif isinstance(self.config, dict):
            self.is_backtest = "backtest" in self.config or any(
                "backtest" in str(k).lower() for k in self.config.keys()
            )

        if config_format == "yaml":
            builder = SimulatorBuilder.from_yaml(config_content)
        else:
            builder = SimulatorBuilder.from_json(config_content)

        for protocol in self.protocols:
            if not isinstance(protocol, ProtocolFactoryAdapter):
                protocol = ProtocolFactoryAdapter(protocol)
            builder.add_factory(protocol)

        self.simulator = builder.build()

    def get_protocol(self, protocol_id: str) -> Any:
        """
        Retrieve a protocol instance by its identifier.

        Args:
            protocol_id: Unique identifier for the protocol (e.g., "uniswap_v3")

        Returns:
            The protocol instance corresponding to the given ID

        Raises:
            RuntimeError: If simulation hasn't been built yet
            KeyError: If protocol_id doesn't exist in the simulation

        Example:
            >>> uniswap_protocol = sim.get_protocol("uniswap_v3")
            >>> current_price = uniswap_protocol.get_current_price()
        """
        if not self.simulator:
            raise RuntimeError("Simulation has not been built yet")

        return self.simulator.get_py_protocol(protocol_id)

    def run(self) -> Dict[str, Any]:
        """
        Execute the simulation and return results.

        This method runs the entire simulation from start to end block/timestamp,
        processing all transactions and collecting metrics along the way.

        Returns:
            SimulationResults: Object containing all simulation data including:
                - Protocol states at each block
                - Agent portfolio values over time
                - Transaction logs and fees
                - Observable metrics and KPIs

        Raises:
            RuntimeError: If simulation hasn't been built yet

        Example:
            >>> results = sim.run()
            >>> portfolio_value = results.get_agent_metric("alice", "total_holding")
        """
        if not self.simulator:
            raise RuntimeError("Simulation has not been built yet")
        logging.info("Simulation starting...")
        results = self.simulator.run_to_dict()
        logging.info("Simulation ended")
        return results

    def to_json(self) -> str:
        """
        Serialize the simulation configuration to JSON.

        Returns:
            JSON representation of the complete simulation configuration,
            including all protocols, agents, and parameters

        Raises:
            RuntimeError: If simulation hasn't been built yet
        """
        if not self.simulator:
            raise RuntimeError("Simulation has not been built yet")

        return self.simulator.to_json()

    @classmethod
    def from_json(cls, json_data: str) -> "Simulation":
        """
        Deserialize a simulation from JSON configuration.

        This class method allows reconstructing a Simulation instance from
        a previously serialized JSON configuration.

        Args:
            json_data: JSON string containing simulation configuration

        Returns:
            New Simulation instance configured from the JSON data

        Raises:
            ValueError: If JSON is malformed or contains invalid configuration

        Example:
            >>> json_config = previous_sim.to_json()
            >>> new_sim = Simulation.from_json(json_config)
        """
        simulation = cls([], {})
        simulation.simulator = Simulator.from_json(json_data)
        return simulation
