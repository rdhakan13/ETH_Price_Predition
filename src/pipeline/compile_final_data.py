import os
from src.common.utils import get_root_directory,timeit
from src.common.logger import get_logger
from src.common.config_loader import ConfigLoader
from src.preprocessing.data_cleaner import DataCleaner

logger = get_logger(os.environ.get("LOG_LEVEL"), __name__)
root_dir = str(os.path.join(str(get_root_directory()),'tmp'))
directory = str(os.path.join(root_dir,'data','final'))

config_loader = ConfigLoader()
config = config_loader.define_compile_final_data()
column_mapping = config_loader.define_column_mapping()
active = config.get("active", False)
tickers = config.get("tickers", [])

@timeit
def compile_final_data()-> None:
    """
    This function compiles the final data for the project.
    It reads the data from the sources, cleans it, and saves it to a final directory.
    """
    for ticker in tickers:
        sources = {}
        for source in list(ticker.get("sources", [])):
            sources.update({source.get("name","").lower(): source.get("columns_to_drop", [])})

        dc = DataCleaner(root_dir, ticker.get("name", None), source=list(sources.keys()))

        dc.read_data()

        dc.identify_nan()

        for source in list(sources.keys()):
            dc.drop_columns(source=source, columns=sources[source])
            dc.standardise_columns(source=source, column_mapping=column_mapping)

        dc.merge_sources()

        dc.interpolate_clean_data(method="time")

        dc.save_clean_data(directory=directory)


if __name__ == "__main__":
    if active:
        logger.info("Compiling final data...")
        compile_final_data()
        logger.info("Final data compiled successfully.")