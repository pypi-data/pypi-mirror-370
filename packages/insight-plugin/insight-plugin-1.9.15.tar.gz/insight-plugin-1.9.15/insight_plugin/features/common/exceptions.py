class InsightException(Exception):
    def __init__(
        self, message: str, troubleshooting: list[str]
    ):  # pylint: disable=unsubscriptable-object
        super().__init__(message)
        self.troubleshooting = troubleshooting

    def __str__(self):
        return f"Error Message: {self.args[0]} Troubleshooting information: {self.troubleshooting}"

    def __repr__(self):
        return (
            f"InsightException(message={self.args[0]}, troubleshooting={self.args[1]})"
        )


class RunCommandExceptions:
    ERROR_INVOKING_SHELL_MESSAGE = "Error invoking shell in docker container."
    ERROR_INVOKING_SHELL_TROUBLESHOOTING = (
        "Check Dockerfile config and make sure either bash or sh exists."
        "Other possible errors may exist, check the output above for more "
        "information."
    )

    LAST_OUTPUT_NOT_JSON_MESSAGE = (
        "Run command from docker did not end with output block."
    )
    LAST_OUTPUT_NOT_JSON_TROUBLESHOOTING = (
        "Check output without the assessment flag on first."
    )

    JQ_COMPILE_FAIL_MESSAGE = "Bad JQ Pattern for output."
    JQ_COMPILE_FAIL_TROUBLESHOOTING = "Check the JQ error message."

    JQ_PARSE_ERROR_MESSAGE = "Failed to apply JQ pattern to output."
    JQ_PARSE_ERROR_TROUBLESHOOTING = (
        "Try running without -j and check for other errors."
    )

    JSON_TYPE_NOT_IN_JSON_TROUBLESHOOTING = (
        "Add the field back in with (action/trigger/task)_start, "
        'e.g. "action_start".'
    )

    TEST_FILE_INVALID_JSON_TROUBLESHOOTING = (
        "Check the test file and ensure it is valid json."
    )
    TEST_FILE_NOT_FOUND_TROUBLESHOOTING = (
        "Check that the file exists and is in the provided path."
    )
