import argparse
import logging

from tensorflow.io import gfile

def read_from_gcs(file_name: str):
    logging.info('Reading %s from GCS' % (file_name))
    with gfile.GFile(file_name, 'r') as f_in:
        print(f_in.readlines())


def main():
    parser = argparse.ArgumentParser(description='Print the content of file in GCS')
    parser.add_argument(
        '--input-file-name',
        type=str,
        required=True,
        help='Local or GCS path to the output file'
    )

    known_args, _ = parser.parse_known_args()
    read_from_gcs(known_args.input_file_name)


if __name__ == '__main__':
    main()




