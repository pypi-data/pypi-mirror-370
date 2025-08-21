import json
from typing import Any, List, Optional, Tuple

from nqs_sdk import MutBuilderSharedState, ProtocolFactoryAdapter, SimulationClock, Simulator, SimulatorBuilder
from nqs_sdk.bindings.protocols.protocol_infos import ProtocolInfos
from nqs_sdk.bindings.spots.spot_generator import SpotGenerator
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk.interfaces.protocol_factory import ProtocolFactory
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk.utils.json_decimal_encoder import DecimalEncoder


class Agent:
    def __init__(self, name: str, wallet: dict[str, float]) -> None:
        self.name = name
        self.wallet = wallet


class SimTxGenerator(ProtocolFactory):
    def __init__(self) -> None:
        self.tx_generators: list[TxGenerator] = []

    def id(self) -> str:
        return "sim_tx_generator"

    def register_tx_generator(self, tx_generator: TxGenerator) -> None:
        self.tx_generators.append(tx_generator)

    def build(
        self,
        clock: SimulationClock,
        builder_state: MutBuilderSharedState,
        common_config: Any,
        backtest: bool,
        config: Any,
    ) -> Tuple[List[Protocol], List[TxGenerator]]:
        return [], self.tx_generators


class SimulatorEnvBuilder:
    def __init__(
        self, common_args: Optional[dict[str, Any]] = None, save_config: Optional[str] = None, do_backtest: bool = False
    ) -> None:
        self.factories: dict[str, ProtocolMetaFactory] = {}

        # collect_all_observables is True by default
        if common_args is None:
            self.common_args: dict[str, Any] = {"collect_all_observables": False}
        else:
            self.common_args = common_args
            if "collect_all_observables" not in self.common_args:
                self.common_args["collect_all_observables"] = False

        self.tokens_info: dict[str, int] = {}

        self.sim_tx_generator = SimTxGenerator()
        self.spot_generators: list[SpotGenerator] = []
        self.agents: list[Agent] = []
        self.save_config = save_config
        self.do_backtest = do_backtest

    def set_simulator_time(self, start_block: int, end_block: int, block_step_metrics: int) -> None:
        self.common_args.update(
            {"block_number_start": start_block, "block_number_end": end_block, "block_step_metrics": block_step_metrics}
        )

    def set_numeraire(self, numeraire: str) -> None:
        self.common_args.update({"numeraire": numeraire})

    def set_gas_fee(self, gas_fee: float, gas_fee_ccy: Optional[str] = None) -> None:
        self.common_args.update({"gas_fee": gas_fee})

        if gas_fee_ccy is not None:
            self.common_args.update({"gas_fee_ccy": gas_fee_ccy})

    def register_factory(self, factory: ProtocolMetaFactory) -> None:
        self.factories[factory.id()] = factory

    def register_agent(self, agent_name: str, agent_wallet: dict[str, float]) -> None:
        self.agents.append(Agent(agent_name, agent_wallet))

    def register_spot_generator(self, spot_generator: SpotGenerator) -> None:
        self.spot_generators.append(spot_generator)

    def get_all_agents(self) -> list[Agent]:
        return self.agents

    def register_protocol(self, protocol: ProtocolInfos) -> None:
        assert protocol.factory_id in self.factories, f"Factory {protocol.factory_id} not registered"
        self.factories[protocol.factory_id].register_protocol(protocol)
        self.tokens_info.update(protocol.get_token_infos())

    def register_tx_generator(self, tx_generator: TxGenerator) -> None:
        self.sim_tx_generator.register_tx_generator(tx_generator)

    def get_common_args(self) -> dict:
        return self.common_args

    def build(self) -> Simulator:
        assert len(self.factories) > 0, "No factories registered"
        assert len(self.spot_generators) > 0, "No spot generators registered"
        assert "numeraire" in self.common_args, "Numeraire not registered"
        assert self.common_args["gas_fee_ccy"] in self.tokens_info, "Gas fee currency not registered"
        assert self.common_args["gas_fee"] >= 0, "Gas fee must be positive"
        assert self.common_args["block_number_start"] >= 0, "Start block must be positive"
        assert self.common_args["block_number_end"] >= self.common_args["block_number_start"], (
            "End block must be greater than start block"
        )
        assert self.common_args["block_step_metrics"] > 0, "Block step metrics must be positive"

        tokens_info = {token: {"decimals": decimals} for token, decimals in self.tokens_info.items()}

        spot_list = []
        environment: dict
        if self.do_backtest:
            for spot_generator in self.spot_generators:
                for name in spot_generator.names:
                    spot_list.append({"name": name, "historical": {}})

            factory_configs = {}
            for factory in self.factories.values():
                pools = []
                for k, v in factory.get_config().items():  # FIXME HACK OF INTERNAL STRUCTURES
                    pools.extend(v["initial_state"]["historical_state"]["pools"])
                factory_configs.update({k: {"pools": pools}})

            environment = {"backtest_environment": {"protocols_to_replay": factory_configs}}
        else:
            for spot_generator in self.spot_generators:
                spots = spot_generator.generate_spot(
                    self.common_args["block_number_start"], self.common_args["block_number_end"]
                )

                for name, spot in zip(spot_generator.names, spots):
                    spot_list.append({"name": name, "custom": {"timestamps": spot[0], "path": spot[1]}})

            factory_configs = {}
            for factory in self.factories.values():
                factory_configs.update(factory.get_config())

            environment = {
                "simulation_environment": {"tokens_info": tokens_info, "protocols_to_simulate": factory_configs}
            }

        # add the tx generator factory
        factory_configs.update({"sim_tx_generator": {}})

        config = {
            "version": "1.0.0",
            "common": self.common_args,
            "spot": {"spot_list": spot_list},
            **environment,
            "agents": [{"name": agent.name, "wallet": agent.wallet} for agent in self.agents],
        }

        # Save the configuration to a JSON file
        config_json = json.dumps(config, indent=2, cls=DecimalEncoder)
        if self.save_config:
            with open(self.save_config, "w") as f:
                f.write(config_json)

        builder = SimulatorBuilder.from_json(config_json)
        for factory in self.factories.values():
            subfactories = factory.get_factories()
            for subfactory in subfactories:
                if not isinstance(subfactory, ProtocolFactoryAdapter):
                    subfactory = ProtocolFactoryAdapter(subfactory)

                builder.add_factory(subfactory)

        # add the tx generator factory
        builder.add_factory(ProtocolFactoryAdapter(self.sim_tx_generator))

        sim = builder.build()

        return sim
