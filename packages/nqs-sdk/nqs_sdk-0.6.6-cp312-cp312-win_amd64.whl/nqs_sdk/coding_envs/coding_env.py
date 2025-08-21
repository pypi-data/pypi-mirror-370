# mypy: disable-error-code="return-value,no-untyped-def,operator,var-annotated,assignment,union-attr,list-item"

import json
import pickle
import signal
from typing import List, Literal, Optional, Tuple

import pandas as pd
from llm_sandbox import SandboxSession
from RestrictedPython import compile_restricted, safe_globals

from nqs_sdk import MetricName, Metrics, RefSharedState, SealedParameters, SimulationClock, TxRequest
from nqs_sdk.bindings.env_builder import SimulatorEnvBuilder
from nqs_sdk.bindings.spots.spot_generator import SpotGenerator
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction
from nqs_sdk.interfaces.observable_consumer import ObservableConsumer
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk.utils.json_decimal_encoder import DecimalEncoder
from nqs_sdk.utils.logging import local_logger

from .policy_caller import PolicyCaller
from .protocols.agent.agent_coding_env import AgentProtocol
from .protocols.coding_protocol import CodingProtocol
from .restriction_policy import CodingNodeTransformer, implement_policy
from .utils import policy_caller_static_analysis


logger = local_logger(__name__)


def timeout_handler(signum, frame):
    raise TimeoutError("Policy execution timed out")


sandboxing_execution = """
import pickle
import os

from nqs_sdk.coding_envs.protocols.coding_protocol import CodingProtocol
from nqs_sdk.coding_envs.policy_caller import PolicyCaller

agents_code = {agents}
agents_obj = dict()

if os.path.exists("agents.pkl"):
    for _, (_, agent_code) in agents_code.items():
        exec(agent_code)
    with open("agents.pkl", "rb") as f:
        agents_obj = pickle.load(f)

with open("protocols.pkl", "rb") as f:
    protocols = pickle.load(f)

for agent_name, (agent_class_name, agent_code) in agents_code.items():
    # update current agent for all protocols
    for protocol in protocols.values():
        protocol.set_current_agent(agent_name)

    if agent_name not in agents_obj:
        exec(agent_code)
        exec("result_agent = " + agent_class_name + "()")
        agents_obj[agent_name] = result_agent

    agents_obj[agent_name].policy({block}, protocols)

with open("protocols.pkl", "wb") as f:
    pickle.dump(protocols, f)

with open("agents.pkl", "wb") as f:
    pickle.dump(agents_obj, f)

"""


class CoderSimTxGenerator(TxGenerator, ObservableConsumer):
    def __init__(self) -> None:
        self.transactions: dict[str, list[Transaction]] = {}
        self.observables: list[str] = []

    def id(self) -> str:
        return "coder_sim_tx_generator"

    def initialize(self, parameters: SealedParameters) -> None:
        return

    def next(
        self, clock: SimulationClock, state: RefSharedState, metrics: Metrics
    ) -> Tuple[List[TxRequest], Optional[int]]:
        txns: list[TxRequest] = []

        # update wallet addr for all transactions
        for agent_name, transactions in self.transactions.items():
            agent_addr = state.agent_name_to_addr(agent_name)
            for txn in transactions:
                tx_request = txn.to_tx_request(
                    protocol="",
                    source=agent_name,
                    sender=agent_addr,
                    order=float("-inf"),  # -inf: before any other transactions
                )
                txns.append(tx_request)

        return txns, None

    def consume(self, parameters: SealedParameters, clock: SimulationClock) -> Tuple[List[MetricName], Optional[int]]:
        metrics_names = []

        for metric_str in self.observables:
            metrics_names.append(parameters.str_to_metric(metric_str))

        return metrics_names, None


class CodingEnv:
    def __init__(
        self,
        sandboxing_method: Optional[Literal["restricted_python", "llm_sandbox"]] = None,
        sandbox_docker_image: Optional[str] = None,
        do_backtest: bool = False,
        timeout: int = 30,
        common_args: dict = {},
        allowed_libraries: list[str] = [],
        use_float_observables: bool = False,
    ):
        self.common_args = common_args
        self.do_backtest = do_backtest
        self.use_float_observables = use_float_observables

        self.numeraire = None
        self.gas_fee = None
        self.gas_fee_ccy = None

        self.agents: dict[str, tuple[dict, PolicyCaller | tuple[str, str]]] = {}
        self.protocols: dict[str, CodingProtocol] = {}
        self.registered_protocol_factories: list[ProtocolMetaFactory] = []
        self.spot_generators: list[SpotGenerator] = []

        self.sandboxing_method = sandboxing_method
        self.timeout = timeout
        self.allowed_libraries = allowed_libraries

        self.sandbox_session = None
        if sandboxing_method == "llm_sandbox" and sandbox_docker_image is not None:
            self.sandbox_session = SandboxSession(lang="python", execution_timeout=10.0, image=sandbox_docker_image)
            self.sandbox_session.open()
            self.sandbox_session.execute_command(
                "/tmp/venv/bin/pip install pydantic pyquantlib nqs_sdk rl4defi --find-links /packages"
            )

    def __del__(self) -> None:
        if self.sandbox_session is not None:
            self.sandbox_session.close()

    def register_protocol(self, protocol: CodingProtocol | str) -> None:
        assert isinstance(protocol, CodingProtocol), "Protocol must be a CodingProtocol"
        assert protocol.id() not in self.protocols, f"Protocol {protocol.id()} already registered"

        # register the protocol
        self.protocols[protocol.id()] = protocol

        protocol_factory = protocol.get_protocol_factory()
        if protocol_factory is not None and protocol_factory not in self.registered_protocol_factories:
            self.registered_protocol_factories.append(protocol_factory)

    def register_agent(self, agent_name: str, wallet: dict[str, float], object: PolicyCaller | str) -> None:
        if isinstance(object, str):
            try:
                agent_class_name = policy_caller_static_analysis(object, libraries=self.allowed_libraries)
            except Exception as e:
                raise Exception(f"Failed to parse the agent code: {e}")

        agent_locals = {}
        if self.sandboxing_method == "restricted_python":
            compiled_object = compile_restricted(object, "<inline>", "exec", policy=CodingNodeTransformer)
            # set up the globals
            implement_policy(
                safe_globals,
                {"PolicyCaller": globals()["PolicyCaller"], "CodingProtocol": globals()["CodingProtocol"]},
                libraries=self.allowed_libraries,
                allowed_write_classes=[agent_class_name, "list", "dict", "tuple", "set"],
            )
            exec(compiled_object, safe_globals, agent_locals)
            exec(f"result_agent = {agent_class_name}()", safe_globals, agent_locals)
            object = agent_locals["result_agent"]
            assert isinstance(object, PolicyCaller), "The compiled object must be a PolicyCaller"

        if isinstance(object, tuple) and self.sandboxing_method is None:
            agent_class_name = object[0]
            agent_source_code = object[1]

            exec(agent_source_code, globals(), agent_locals)
            exec(f"result_agent = {agent_class_name}()", globals(), agent_locals)
            object = agent_locals["result_agent"]
            assert isinstance(object, PolicyCaller), "The compiled object must be a PolicyCaller"

        self.agents[agent_name] = (wallet, object)

    def register_spot_generator(self, spot_generator: SpotGenerator | str) -> None:
        if isinstance(spot_generator, str):
            raise NotImplementedError("Spot generator must be a SpotGenerator")

        self.spot_generators.append(spot_generator)

    def set_numeraire(self, numeraire: str) -> None:
        self.numeraire = numeraire

    def set_gas_fee(self, gas_fee: float, gas_fee_ccy: Optional[str] = None) -> None:
        self.gas_fee = gas_fee
        self.gas_fee_ccy = gas_fee_ccy

    def _build_env(
        self, coder_sim_tx_generator: CoderSimTxGenerator, simulation_time: tuple[int, int, int]
    ) -> tuple[SimulatorEnvBuilder, AgentProtocol]:
        env_builder = SimulatorEnvBuilder(common_args=self.common_args, do_backtest=self.do_backtest)
        env_builder.set_simulator_time(simulation_time[0], simulation_time[1], simulation_time[2])

        if self.numeraire is not None:
            env_builder.set_numeraire(self.numeraire)
        if self.gas_fee is not None:
            env_builder.set_gas_fee(self.gas_fee, self.gas_fee_ccy)

        # register tx generator
        env_builder.register_tx_generator(coder_sim_tx_generator)

        # register factories
        for protocol_factory in self.registered_protocol_factories:
            env_builder.register_factory(protocol_factory())

        # register protocols
        for protocol in self.protocols.values():
            env_builder.register_protocol(protocol.protocol)

        # register all tx generators
        for tx_generator in protocol.get_tx_generators():
            env_builder.register_tx_generator(tx_generator)

        # register spot generators
        for spot_generator in self.spot_generators:
            env_builder.register_spot_generator(spot_generator)

        # register agents
        for agent_name, (wallet, _) in self.agents.items():
            env_builder.register_agent(agent_name, wallet)

        # Add the agent protocol
        tokens_list = list(env_builder.tokens_info.keys()) + [env_builder.common_args["numeraire"]]
        tokens_list = list(set(tokens_list))

        agent_protocol = AgentProtocol(tokens_list)

        return env_builder.build(), agent_protocol

    def run_live(self) -> dict[str, pd.Series]:
        return {}

    def run_simulation(self, simulation_time: tuple[int, int, int]) -> dict[str, pd.Series]:
        coder_sim_tx_generator = CoderSimTxGenerator()
        sim, agent_protocol = self._build_env(coder_sim_tx_generator, simulation_time)

        # set all agents in protocols and initialize observables
        for protocol in self.protocols.values():
            protocol.set_all_agents(list(self.agents.keys()))
            coder_sim_tx_generator.observables.extend(protocol.get_observables_names())

        out = None
        observables = {}
        for out in sim:
            block_number = out.block
            current_time = out.time

            for observable, data in out.observables.items():
                series = pd.Series([data], index=[current_time], dtype=float if self.use_float_observables else None)

                if observable not in observables:
                    observables[observable] = series
                else:
                    observables[observable] = pd.concat([observables[observable], series])

            # update protocols
            for protocol in list(self.protocols.values()) + [agent_protocol]:
                protocol.set_current_block(block_number)
                protocol.set_current_time(current_time)
                protocol.update_observables(observables)

            # SandBoxing execution
            if self.sandboxing_method == "llm_sandbox":
                assert self.sandbox_session is not None, "Sandbox session must be set for llm_sandbox"

                # pickle the protocols
                with open("protocols.pkl", "wb") as f:
                    pickle.dump(self.protocols, f)

                self.sandbox_session.copy_to_runtime("protocols.pkl", "/sandbox/protocols.pkl")

                # run the sandboxing execution
                result = self.sandbox_session.run(
                    sandboxing_execution.format(block=block_number, agents=json.dumps(self.agents, cls=DecimalEncoder)),
                    libraries=["pickle", "pydantic", "pyquantlib", "nqs_sdk", "rl4defi"] + self.allowed_libraries,
                    timeout=self.timeout,
                )

                if result.exit_code != 0:
                    logger.error(f"Sandboxing execution failed: {result.stderr}")
                    raise Exception("Sandboxing execution failed")

                # get the new agents and protocols out of the sandbox
                self.sandbox_session.copy_from_runtime("/sandbox/protocols.pkl", "protocols.pkl")

                # get the new protocols out of the sandbox
                with open("protocols.pkl", "rb") as f:
                    self.protocols = pickle.load(f)

            else:
                for agent_name, (_, obj) in self.agents.items():
                    # update current agent for all protocols
                    for protocol in list(self.protocols.values()) + [agent_protocol]:
                        protocol.set_current_agent(agent_name)

                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(self.timeout)

                    try:
                        obj.policy(block_number, agent_protocol, self.protocols)
                    finally:
                        signal.alarm(0)  # Cancel the alarm

            # update transactions for the agent
            coder_sim_tx_generator.transactions = {}
            for protocol in self.protocols.values():
                for agent_name, txns in protocol.get_transactions().items():
                    if agent_name not in coder_sim_tx_generator.transactions:
                        coder_sim_tx_generator.transactions[agent_name] = []
                    coder_sim_tx_generator.transactions[agent_name].extend(txns)
                protocol.clear_transactions()

            # order transactions by timestamp
            for agent_name, txns in coder_sim_tx_generator.transactions.items():
                coder_sim_tx_generator.transactions[agent_name] = sorted(txns, key=lambda x: x.timestamp)

            # update the observables for the next step
            coder_sim_tx_generator.observables = []
            for protocol in list(self.protocols.values()) + [agent_protocol]:
                coder_sim_tx_generator.observables.extend(protocol.get_observables_names())

        return observables

    def run(self, simulation_time: Optional[tuple[int, int, int]] = None) -> dict[str, pd.Series]:
        if simulation_time is not None:
            return self.run_simulation(simulation_time)
        else:
            return self.run_live()
