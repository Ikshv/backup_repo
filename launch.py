from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler

# def init(df, user_agent, fresh):
#     reg = df.read_one(Register, user_agent)
#     if not reg:
#         reg = Register(user_agent, fresh)
#         df.add_one(Register, reg)
#         df.commit()
#         df.push_await()
#     while not reg.load_balancer:
#         df.pull_await()
#         if reg.invalid:
#             raise RuntimeError("User agent string is not acceptable.")
#         if reg.load_balancer:
#             df.delete_one(Register, reg)
#             df.commit()
#             df.push()
#     return reg.load_balancer

# # Define a wrapper function to match the expected signature
# def init_wrapper(dataframe, config, restart):
#     t = {
#         "dataframe": dataframe,
#         "user_agent": config.user_agent,
#         "fresh": restart or not os.path.exists(config.save_file)        
#     }
#     b = init(t)
#     return b

def main(config_file, restart):
    cparser = ConfigParser() # ConfigParser is a class that is used to read configuration files.
    cparser.read(config_file) # read() method reads the configuration file and returns a list of sections.
    config = Config(cparser) # Config is a class that is used to store the configuration settings.
    config.cache_server = get_cache_server(config, restart) # get_cache_server() method returns the cache server.
    crawler = Crawler(config, restart) # Crawler is a class that is used to start the crawler.
    crawler.start() # start() method is used to start the crawler.
    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart) # main() method is used to start the crawler.