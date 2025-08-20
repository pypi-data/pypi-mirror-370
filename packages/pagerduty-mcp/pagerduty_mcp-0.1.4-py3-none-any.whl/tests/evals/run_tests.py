"""Test agent for evaluating LLM MCP tool call competency."""

import argparse
import asyncio
import json
import logging
import os
from collections.abc import Sequence
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel

from pagerduty_mcp.server import add_read_only_tool, add_write_tool
from pagerduty_mcp.tools import read_tools, write_tools
from tests.evals.competency_test import CompetencyTest
from tests.evals.mcp_tool_tracer import MockedMCPServer
from tests.evals.test_incidents import INCIDENT_COMPETENCY_TESTS
from tests.evals.test_teams import TEAMS_COMPETENCY_TESTS

test_mapping = {
    "incidents": INCIDENT_COMPETENCY_TESTS,
    "teams": TEAMS_COMPETENCY_TESTS,
    "all": INCIDENT_COMPETENCY_TESTS + TEAMS_COMPETENCY_TESTS,
}

load_dotenv()

logging.getLogger().setLevel(logging.WARNING)


class TestResult(BaseModel):
    """Model for test results."""

    query: str
    description: str
    expected_tools: list[dict[str, Any]]
    actual_tools: list[dict[str, Any]]
    success: bool
    gpt_response: str | None = None
    error: str | None = None


class TestReport(BaseModel):
    """Model for the test report."""

    llm_type: str
    total_tests: int
    successful_tests: int
    success_rate: float
    results: list[TestResult]


class TestAgent:
    """Agent for testing LLM competency with MCP tools.

    This agent submits competency questions to an LLM and
    verifies that the correct MCP tools are called with
    the right parameters.
    """

    def __init__(self, llm_type: str = "gpt"):
        """Initialize the test agent.

        Args:
            llm_type: The type of LLM to test ("gpt" or other supported types)
        """
        self.llm_type = llm_type
        self.results = []
        self.mocked_mcp = MockedMCPServer()
        self.llm = self._initialize_llm(llm_type)

    def _initialize_llm(self, llm_type: str) -> OpenAI:
        """Initialize the specified LLM client.

        Args:
            llm_type: The type of LLM to initialize

        Returns:
            Initialized LLM client
        """
        if llm_type == "gpt":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for GPT testing")
            return OpenAI(api_key=api_key)
        raise ValueError(f"LLM type {llm_type} is not yet supported")

    def _get_available_tools(self) -> list[dict[str, Any]]:
        """Get tool schemas directly from MCP server (like dbt-labs approach)."""
        # Create temp MCP server with same setup as real server
        temp_mcp = FastMCP("test-server")

        for tool in read_tools:
            add_read_only_tool(temp_mcp, tool)
        for tool in write_tools:
            add_write_tool(temp_mcp, tool)

        # Get tools using MCP's built-in schema generation (async)
        async def get_mcp_tools():
            mcp_tools = await temp_mcp.list_tools()
            return [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or t.name,
                        "parameters": t.inputSchema or {"type": "object", "properties": {}},
                    },
                }
                for t in mcp_tools  # mcp_tools is already a list, not an object with .tools
            ]

        # Run async function in sync context
        return asyncio.run(get_mcp_tools())

    def _execute_tool_call(self, function_name: str, function_args: dict[str, Any]) -> Any:
        """Execute a tool call directly using the MCP client instead of going through OpenAI's function calling.

        Args:
            function_name: The name of the tool to call
            function_args: The arguments to pass to the tool

        Returns:
            The result of the tool call
        """
        print(f"Directly calling MCP tool: {function_name} with args: {function_args}")

        # Execute the tool call through our mock client
        return self.mocked_mcp.invoke_tool(function_name, **function_args)

    def test_competency(self, test_case: CompetencyTest) -> TestResult | None:
        """Test a single competency question.

        Args:
            test_case: The competency test case to run

        Returns:
            TestResult object with query, expected tools, actual tools, and success
        """
        # Reset the tool tracer for this test
        # TODO: add clear method to MockedMCPServer
        self.mocked_mcp = MockedMCPServer()

        # Register mock responses for the test case
        test_case.register_mock_responses(self.mocked_mcp)

        try:
            query = test_case.query
            print("-" * 40)
            print(f"Testing query: {query}")

            # Make actual call to GPT with function calling
            system_msg = ChatCompletionSystemMessageParam(
                {
                    "role": "system",
                    "content": (
                        "You are a PagerDuty assistant. Use the available tools to help users "
                        "with incident management tasks. Call the appropriate functions based on user requests."
                    ),
                }
            )

            user_msg = ChatCompletionUserMessageParam({"role": "user", "content": query})
            messages = [system_msg, user_msg]

            conversation_turns = 0
            response = None
            while conversation_turns < test_case.max_conversation_turns:
                response = self.llm.chat.completions.create(
                    model=test_case.model,  # TODO: Abstract model providers so we can support Claude etc ..
                    messages=messages,
                    tools=self._get_available_tools(),  # type: ignore TODO: fix type hint
                    tool_choice="auto",
                )

                # Process the function calls GPT wants to make
                if response.choices[0].message.tool_calls:
                    tool_called = None
                    for tool_call in response.choices[0].message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        print(f"GPT called: {function_name} with args: {function_args}")

                        # Execute the tool call directly using our MCP client
                        result = self._execute_tool_call(function_name, function_args)
                        print(f"Tool result: {result}")
                        # Add the tool call and its result to the conversation

                        assistant_msg = ChatCompletionAssistantMessageParam(
                            {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": tool_call.id,
                                        "type": "function",
                                        "function": {"name": function_name, "arguments": tool_call.function.arguments},
                                    }
                                ],
                            }
                        )
                        messages.append(assistant_msg)
                        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
                        tool_called = True

                    if tool_called:
                        conversation_turns += 1
                        continue
                break

            # Verify the tool calls
            success = test_case.verify_tool_calls(self.mocked_mcp)

            # Get expected tools in the right format for the result
            expected_tools = getattr(test_case, "expected_incident_tools", test_case.expected_tools)

            if response:
                return TestResult(
                    query=query,
                    description=test_case.description,
                    expected_tools=expected_tools,
                    actual_tools=self.mocked_mcp.tool_calls,
                    success=success,
                    gpt_response=response.choices[0].message.content or "No text response",
                )

        except Exception as e:  # noqa: BLE001
            print(f"Error during test: {e!s}")
            # Get expected tools in the right format for the result
            expected_tools = getattr(test_case, "expected_incident_tools", test_case.expected_tools)

            return TestResult(
                query=test_case.query,
                description=test_case.description,
                expected_tools=expected_tools,
                actual_tools=self.mocked_mcp.tool_calls,
                success=False,
                error=str(e),
            )

    def run_tests(self, test_cases: Sequence[CompetencyTest]) -> list[TestResult]:
        """Run all specified competency tests.

        Args:
            test_cases: List of test cases to run

        Returns:
            List of test results
        """
        results = []
        for test_case in test_cases:
            result = self.test_competency(test_case)
            if result:
                results.append(result)

        self.results = results
        return results

    def generate_report(self, output_file: str | None = None) -> None:
        """Generate a report of test results.

        Args:
            output_file: Optional file path to write the report to
        """
        if not self.results:
            print("No test results available. Run tests first.")
            return

        total = len(self.results)
        successful = sum(r.success for r in self.results)

        report = TestReport(
            llm_type=self.llm_type,
            total_tests=total,
            successful_tests=successful,
            success_rate=successful / total if total > 0 else 0,
            results=self.results,
        )

        # Print summary
        print(f"LLM: {self.llm_type}")
        print(f"Tests: {successful}/{total} ({report.success_rate:.2%})")

        # Save report if requested
        if output_file:
            with open(output_file, "w") as f:
                f.write(report.model_dump_json(indent=2))
            print(f"Report saved to {output_file}")


def main():
    """Main entry point for running the tests."""
    parser = argparse.ArgumentParser(description="Test LLM competency with MCP tools")
    parser.add_argument("--llm", choices=["gpt"], default="gpt", help="LLM provider to use for testing")
    parser.add_argument(
        "--domain", choices=["all", "incidents", "teams", "services"], default="all", help="Domain to test"
    )
    parser.add_argument("--output", type=str, help="Output file for test report")

    args = parser.parse_args()

    # Select test cases based on domain
    test_cases = test_mapping.get(args.domain, [])

    if not test_cases:
        print(f"No test cases available for domain: {args.domain}")
        return

    # Create and run the test agent
    agent = TestAgent(llm_type=args.llm)
    agent.run_tests(test_cases)

    # Generate report
    output_file = args.output or f"test_results_{args.llm}_{args.domain}.json"
    agent.generate_report(output_file)


if __name__ == "__main__":
    main()
