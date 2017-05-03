import os
import tinify
tinify.key = "ztlmPV5XG4sib4jGK5LYWX7X25hVhKhS"

ASSETS_DIR = '/home/lvisintini/src/xwing-data/images/'


def main():
    for dir_path, _, file_names in os.walk(ASSETS_DIR):
        for f in file_names:
            abs_path = os.path.join(dir_path, f)
            print(abs_path)
            source = tinify.from_file(abs_path)
            source.to_file(abs_path)

if __name__ == '__main__':
    main()
