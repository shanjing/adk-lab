import google.adk

MIN_ADK_VERSION = (1, 21)

def assert_adk_version():
    version = tuple(map(int, google.adk.__version__.split(".")))
    if version < MIN_ADK_VERSION:
        raise RuntimeError(
            f"adk-lab requires google-adk >= {MIN_ADK_VERSION}, "
            f"found {google.adk.__version__}"
        )
