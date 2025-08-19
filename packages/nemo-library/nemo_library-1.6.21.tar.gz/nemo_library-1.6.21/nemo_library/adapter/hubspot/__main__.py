import logging

from nemo_library.adapter.hubspot.flow import HubspotFlow

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.getLogger().setLevel(logging.INFO)
    logger_adapter = logging.getLogger("nemo_library.adapter.hubspot")

    hs = HubspotFlow()
    hs.flow()
