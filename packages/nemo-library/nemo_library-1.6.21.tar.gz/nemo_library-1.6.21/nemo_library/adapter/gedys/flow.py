from prefect import flow, task, get_run_logger
from nemo_library.adapter.gedys.extract import GedysExtract
from nemo_library.adapter.gedys.load import GedysLoad
from nemo_library.adapter.gedys.transform import GedysTransform


@flow(name="Gedys ETL Flow", log_prints=True)
def gedys_flow():
    logger = get_run_logger()
    logger.info("Starting Gedys ETL Flow")

    logger.info("Extracting objects from Gedys")
    extract()

    logger.info("Transform Gedys objects")
    transform()

    logger.info("Loading Gedys objects")
    load()

    logger.info("Gedys ETL Flow finished")


@task(name="Extract All Objects from Gedys")
def extract():
    logger = get_run_logger()
    logger.info("Extracting all Gedys objects")

    extractor = GedysExtract()
    extractor.extract()


@task(name="Transform Objects")
def transform():
    logger = get_run_logger()
    logger.info("Transforming Gedys objects")

    transformer = GedysTransform()
    transformer.sentiment_analysis()
    transformer.flatten()
    transformer.join()


@task(name="Load Objects into Nemo")
def load():
    logger = get_run_logger()
    logger.info("Loading Gedys objects into Nemo")

    loader = GedysLoad()
    loader.load()
