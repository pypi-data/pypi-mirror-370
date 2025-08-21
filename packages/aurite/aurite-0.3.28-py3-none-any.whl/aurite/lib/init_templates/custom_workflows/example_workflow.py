# tests/fixtures/custom_workflows/example_workflow.py
import logging
from typing import Any, Optional

# Import BaseCustomWorkflow for inheritance (needed at runtime)
from aurite import AgentRunResult, AuriteEngine, BaseCustomWorkflow

logger = logging.getLogger(__name__)


class ExampleCustomWorkflow(BaseCustomWorkflow):
    """
    A simple example of a custom workflow that demonstrates how to use the
    AuriteEngine to run a pre-configured agent.
    """

    async def run(
        self,
        initial_input: Any,
        executor: "AuriteEngine",
        session_id: Optional[str] = None,
    ) -> Any:
        """
        Executes a linear workflow that runs a single agent.

        This workflow expects an `initial_input` dictionary with a "city" key,
        e.g., `{"city": "New York"}`. It uses this to query the "Weather Agent".

        Args:
            initial_input: The input data for the workflow.
            executor: The AuriteEngine instance to run other components.
            session_id: The session ID for the execution.

        Returns:
            The primary text output from the agent, or an error message.
        """
        logger.info(f"ExampleCustomWorkflow started with input: {initial_input}")

        try:
            # 1. Define which agent to run and prepare the input.
            # This agent name must match an agent configured in your project.
            agent_name = "Weather Agent"
            # Support both dict and string input for initial_input
            if isinstance(initial_input, dict):
                city = initial_input.get("city", "London")
            elif isinstance(initial_input, str):
                city = initial_input or "London"
            else:
                city = "London"
            user_message = f"What is the weather in {city}?"

            logger.info(f"Running agent '{agent_name}' with message: '{user_message}'")

            # 2. Use the executor to run the agent.
            # The executor handles finding the agent, its LLM, its tools, and running the conversation.
            agent_result: "AgentRunResult" = await executor.run_agent(
                agent_name=agent_name,
                user_message=user_message,
                session_id=session_id,
            )

            # 3. Process and return the result.
            if agent_result.status != "success":
                logger.error(f"Agent execution failed: {agent_result.error_message}")
                return {"status": "failed", "error": agent_result.error_message}

            # For simplicity, we'll just return the main text from the agent's response.
            if agent_result.final_response:
                final_response = agent_result.final_response.content
                logger.info(f"Workflow finished successfully. Returning: {final_response}")
                return {"status": "ok", "response": final_response}
            else:
                logger.error("Agent run was successful but returned no final response.")
                return {"status": "failed", "error": "Agent returned no response."}

        except Exception as e:
            logger.error(f"An unexpected error occurred in the workflow: {e}", exc_info=True)
            return {"status": "failed", "error": f"Internal workflow error: {str(e)}"}

    def get_input_type(self):
        """Specifies the expected input type for this workflow."""
        return dict

    def get_output_type(self):
        """Specifies the output type of this workflow."""
        return dict
