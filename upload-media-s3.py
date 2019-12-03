import threading
import boto3
import os
import sys
from boto3.s3.transfer import TransferConfig
import click


def multi_part_upload_with_s3(bucket, key, secret, file):
    s3 = boto3.resource('s3', aws_access_key_id=key, aws_secret_access_key=secret)

    # Multipart upload
    config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
                            multipart_chunksize=1024 * 25, use_threads=True)

    key_path = 'inputs/{}'.format(os.path.basename(file))
    s3.meta.client.upload_file(file, bucket, key_path,
                               ExtraArgs={'ACL': 'public-read', 'ContentType': 'video/mp4'},
                               Config=config,
                               Callback=ProgressPercentage(file)
                               )


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


@click.command()
@click.option('--bucket', '-b', required=True, help='S3 Bucket')
@click.option('--key', '-k', required=True, help='AWS Key')
@click.option('--secret', '-s', required=True, help='AWS Secret')
@click.option('--file', '-f', required=True, help='File to upload')
def cli(bucket, key, secret, file):
    print('Hello')
    multi_part_upload_with_s3(bucket, key, secret, file)


if __name__ == "__main__":
    cli()