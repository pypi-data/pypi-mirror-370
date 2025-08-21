import sys
from .runner.runner import Runner
from .settings import command_line_execution

if __name__ == "__main__":
    # Get the values from user command
    command_line_kwargs = {key: value for key, value in zip(sys.argv[1::2], sys.argv[2::2])}
    # Initialise the Runner class
    runner = Runner(test_suite_path=command_line_kwargs.get(command_line_execution.test_suite_path),
                    test_result_path=command_line_kwargs.get(command_line_execution.test_result_path),
                    test_tags=command_line_kwargs.get(command_line_execution.test_tags),
                    env_path=command_line_kwargs.get(command_line_execution.env_path),
                    test_data_path=command_line_kwargs.get(command_line_execution.test_data_path), )
    # Run the test
    runner.run()
