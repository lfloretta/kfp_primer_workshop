import argparse
import logging
import os
from tensorflow.io import gfile

def write_to_gcs(file_name : str, content : str):
    logging.info('Dumping content in %s' % (file_name))
    with gfile.GFile(file_name, 'w') as f_out:
        f_out.write(content)


def dump_file(path: str, content: str):
    """Dumps string into local file.

    Args:
        path: the local path to the file.
        content: the string content to dump.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    elif os.path.exists(path):
        logging.warning('The file {} will be overwritten.'.format(path))
    with open(path, 'w') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description='Write a string to a file system')
    parser.add_argument(
        '--output-file-name',
        type=str,
        required=True,
        help='Local or GCS path to the output file'
    )
    parser.add_argument(
        '--output-file-name-store',
        type=str,
        default='/tmp/kfp/output/write_to_gcs/output_file_store.txt',
        help='Local file to store the value of --output-file-name'
    )
    parser.add_argument(
        '--content',
        type=str,
        default='Ciao',
        help='String to write to file'
    )

    known_args, _ = parser.parse_known_args()

    write_to_gcs(
        file_name=known_args.output_file_name,
        content=known_args.content
    )

    dump_file(
        path=known_args.output_file_name_store,
        content=known_args.output_file_name)


if __name__ == '__main__':
    main()




