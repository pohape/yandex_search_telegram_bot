import json
import os
import sys


class DataManager:
    def __init__(self):
        script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.data_directory = script_directory + '/data/'

        if not os.path.isdir(self.data_directory):
            os.mkdir(self.data_directory, mode=0o777)

    def get_user_last_search_results(self, user_id: int):
        user_filepath = self.data_directory + str(user_id) + '.json'

        if os.path.isfile(user_filepath):
            with open(user_filepath, mode="r") as f:
                file_content = f.readlines()

                return json.loads(file_content[0])

        return None

    def set_user_last_search_results(self, user_id: int, search_results: list):
        user_filepath = self.data_directory + str(user_id) + '.json'

        with open(user_filepath, mode="w") as f:
            f.write(json.dumps(search_results, ensure_ascii=False))
