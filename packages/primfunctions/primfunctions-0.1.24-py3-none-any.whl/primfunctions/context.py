from typing import List, Dict, Any
import json

from .configuration import Configuration, LLMProvider
from .testing import Testing, Test, Outcome


class Context:
    def __init__(
        self,
        agent_id: str = "",
        environment: str = "",
        session_id: str = "",
        configuration: Configuration = Configuration(),
        data: dict = {},
        variables: Dict[str, float] = {},
    ):
        self.agent_id = agent_id
        self.environment = environment
        self.session_id = session_id
        self.configuration = configuration
        self.data = data
        self.variables = variables
        self.history = []
        self.testing = Testing(runTest=json.loads(self.data.get("runTest", "{}")))
        self.function_id = self.data.get("functionId", "")
        if "runTest" in self.data:
            del self.data["runTest"]  # Remove runTest from data
        if "functionId" in self.data:
            del self.data["functionId"]  # Remove functionId from data

    def add_test(self, name, options, description="", stop={}):
        """
        Add a test to the context.

        Args:
            name: The name of the test.
            options: The options for the test as option:weight pairs.
            description: The description of the test.
            stop: The stop conditions for the test as
                iterations:integer greater than 0,
                confidence:integer between 0 and 100,
                target_outcome:string name of outcome,
                stop_on:1 (either) or 2 (both),
                default:value (required),
                notify:list of email addresses (optional).

        Returns:
            The value of the test.
        """
        return self.testing.add_test(name, options, description, stop)

    def get_test(self, name):
        """
        Get the value of a test.

        Args:
            name: The name of the test.

        Returns:
            The value of the test.
        """
        return self.testing.get_test(name)

    def add_tests(self, tests: list[dict]):
        """
        Add a list of tests to the context.

        Args:
            tests: A list of tests as dictionaries with name, options, description (optional), and stop (optional).
        """
        self.testing.add_tests(tests)

    def add_outcome(self, name, type, description=""):
        """
        Add an outcome to the context.

        Args:
            name: The name of the outcome.
            type: The type of the outcome as boolean, integer, float, or string.
            description: The description of the outcome.

        Returns:
            The value of the outcome.
        """
        self.testing.add_outcome(name, type, description)

    def get_outcome(self, name):
        """
        Get the value of an outcome.

        Args:
            name: The name of the outcome.

        Returns:
            The value of the outcome.
        """
        return self.testing.get_outcome(name)

    def set_outcome(self, name, value):
        """
        Set the value of an outcome.

        Args:
            name: The name of the outcome.
            value: The value of the outcome.
            type: The type of the outcome (optional, in case the outcome is not yet defined).
            description: The description of the outcome (optional, in case the outcome is not yet defined).

        Returns:
            The previous value of the outcome (None if the outcome was not yet defined).
        """
        return self.testing.set_outcome(name, value)

    def trigger_outcome(self, name):
        """
        Trigger an outcome.

        Args:
            name: The name of the outcome (must be a boolean or integer).
            type: The type of the outcome (optional, in case the outcome is not yet defined).
            description: The description of the outcome (optional, in case the outcome is not yet defined).

        Returns:
            The previous value of the outcome (None if the outcome was not yet defined).
        """
        return self.testing.trigger_outcome(name)

    def reset_outcome(self, name):
        """
        Reset an outcome.

        Args:
            name: The name of the outcome.
            type: The type of the outcome (optional, in case the outcome is not yet defined).
            description: The description of the outcome (optional, in case the outcome is not yet defined).

        Returns:
            The previous value of the outcome (None if the outcome was not yet defined).
        """
        return self.testing.reset_outcome(name)

    def add_outcomes(self, outcomes: list[dict]):
        """
        Add a list of outcomes to the context.

        Args:
            outcomes: A list of outcomes as dictionaries with name, type, and description (optional).
        """
        self.testing.add_outcomes(outcomes)

    def serialize(self) -> dict:
        """
        Serialize the context.

        Returns:
            The serialized context.
        """
        return {
            "agent_id": self.agent_id,
            "environment": self.environment,
            "session_id": self.session_id,
            "function_id": self.function_id,
            "configuration": self.configuration.__dict__(),
            "data": self.data,
            "history": self.history,
            "variables": self.variables,
            "testing": self.testing.__dict__(),
        }

    def deserialize(self, state: dict):
        """
        Deserialize the context.

        Args:
            state: The serialized context.
        """
        self.agent_id = state.get("agent_id", self.agent_id)
        self.environment = state.get("environment", self.environment)
        self.session_id = state.get("session_id", self.session_id)
        self.function_id = state.get("function_id", self.function_id)
        self.configuration = Configuration(
            **state.get("configuration", self.configuration.__dict__())
        )
        self.data = state.get("data", self.data)
        self.history = state.get("history", self.history)
        self.variables = state.get("variables", self.variables)

        testing_state: dict = state.get("testing", {})
        tests_dict: Dict[str, dict] = testing_state.get("tests", {})
        outcomes_dict: Dict[str, dict] = testing_state.get("outcomes", {})
        runTest: Dict[str, bool] = testing_state.get("runTest", {})

        tests = {}
        for name, test_data in tests_dict.items():
            # Test expects: name, options, description, stop, runTest
            tests[name] = Test(
                name=test_data.get("name", name),
                options=test_data.get("options", {}),
                description=test_data.get("description", ""),
                stop=test_data.get("stop", {}),
                runTest=runTest.get(name, True),
                value=test_data.get("value", None),
            )

        outcomes = {}
        for name, outcome_data in outcomes_dict.items():
            # Outcome expects: name, type, description
            outcomes[name] = Outcome(
                name=outcome_data.get("name", name),
                type=outcome_data.get("type", "boolean"),
                description=outcome_data.get("description", ""),
                value=outcome_data.get("value", None),
            )

        self.testing = Testing(tests=tests, outcomes=outcomes, runTest=runTest)

    def set_data(self, key: str, value: Any):
        """
        Set the value of a data key.

        Args:
            key: The key of the data.
            value: The value of the data.
        """
        self.data[key] = value

    def get_data(self, key: str, default: Any = None):
        """
        Get the value of a data key.

        Args:
            key: The key of the data.
            default: The default value if the key is not found.
        """
        return self.data.get(key, default)

    # Backward compatible methods - these work with OpenAI format internally
    def add_system_message(self, message: str):
        """
        Add system message. For Gemini, this will be converted when getting formatted history.

        Args:
            message: The message to add.
        """
        self.history.append({"role": "system", "content": message})

    def add_assistant_message(self, message: str):
        """
        Add assistant message. For Gemini, this will be converted to 'model' role when getting formatted history.

        Args:
            message: The message to add.
        """
        self.history.append({"role": "assistant", "content": message})

    def add_user_message(self, message: str):
        """
        Add user message. Works the same for both OpenAI and Gemini.

        Args:
            message: The message to add.
        """
        self.history.append({"role": "user", "content": message})

    # New generic methods for flexibility
    def add_message(self, role: str, content: str):
        """
        Generic method to add any message with specified role.

        Args:
            role: The role of the message.
            content: The content of the message.
        """
        self.history.append({"role": role, "content": content})

    def get_history(self, turns: int = 0) -> List[Dict[str, str]]:
        """
        Get history in original OpenAI format for backward compatibility.

        Args:
            turns: The number of turns to get.
        """
        if turns == 0:
            return self.history
        return self.history[-(turns * 2) :]

    def get_history_message(self, turns: int = 0) -> List[Dict[str, str]]:
        """
        Get history formatted for the current model provider.

        Args:
            turns: The number of turns to get.
        """
        history = self.get_history(turns)

        if self.configuration.llm_provider == LLMProvider.OPENAI:
            return history
        elif self.configuration.llm_provider == LLMProvider.GEMINI:
            return self._convert_to_gemini_format(history)
        else:
            return history

    def _convert_to_gemini_format(
        self, history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Convert OpenAI format to Gemini format.

        Args:
            history: The history to convert.
        """
        converted = []
        system_messages = []

        for message in history:
            role = message["role"]
            content = message["content"]

            if role == "system":
                # Collect system messages to prepend to first user message
                system_messages.append(content)
            elif role == "assistant":
                # Convert assistant to model for Gemini
                converted.append({"role": "model", "content": content})
            elif role == "user":
                # If we have accumulated system messages, prepend them to this user message
                if system_messages:
                    system_context = "\n".join(system_messages)
                    content = f"System: {system_context}\n\nUser: {content}"
                    system_messages = []  # Clear after using
                converted.append({"role": "user", "content": content})
            else:
                # Unknown role, keep as is
                converted.append(message)

        # If there are remaining system messages at the end, add them as a user message
        if system_messages:
            system_content = "\n".join(system_messages)
            converted.append({"role": "user", "content": f"System: {system_content}"})

        return converted

    def set_llm_provider(self, provider: LLMProvider):
        """
        Change the llm provider for this context.

        Args:
            provider: The llm provider to set.
        """
        self.configuration.llm_provider = provider

    def get_llm_provider(self) -> LLMProvider:
        """
        Get the current llm provider.

        Returns:
            The current llm provider.
        """
        return self.configuration.llm_provider
