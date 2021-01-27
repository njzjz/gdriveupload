"""Upload via GDDrive."""

import requests
import os
import uuid
import math
import json
import logging
import shutil
import tempfile
import argparse
from glob import glob
from tqdm.autonotebook import tqdm, trange


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(TqdmLoggingHandler())


def read_env(key, default=None):
    value = os.environ.get(key, default)
    if value is None:
        raise RuntimeError("Environment varible %s is not setting."%key)
    return value


class Uploader:
    def __init__(self):
        # read varible
        self.website = read_env("GDRIVEUPLOAD_WEBSITE")
        self.username = read_env("GDRIVEUPLOAD_USERNAME")
        self.password = read_env("GDRIVEUPLOAD_PASSWORD")
        self.tmpdir = read_env("GDRIVEUPLOAD_TMPDIR", "tmp/")

    def upload(self, file_name, to_path):
        self.decide_file_size(file_name, to_path)

    def decide_file_size(self, file_name, to_path):
        chunk_size = 100000000
        size = os.path.getsize(file_name)
        log.info("file size is %d" % size)
        if size <= chunk_size:
            # if size<100MB, upload directly
            with open(file_name, 'rb') as f:
                self.upload_to_cloudflare(f.read(), to_path)
        else:
            # split to several files
            u = str(uuid.uuid1())
            chunk_number = math.ceil(size/chunk_size)
            log.info("split into %d files" % chunk_number)
            file_list = [to_path]
            with open(file_name, 'rb') as f:
                for ii in trange(chunk_number):
                    chunk_path = os.path.join(self.tmpdir, u + "." + str(ii))
                    self.upload_to_cloudflare(f.read(chunk_size), chunk_path)
                    file_list.append(chunk_path)
            path_data = "\n".join(file_list)
            self.upload_to_cloudflare(
                path_data, os.path.join(self.tmpdir, u + ".path"))

    def upload_to_cloudflare(self, data, to_path, retry=0):
        log.info("Upload to %s" % to_path)
        url = "/".join((self.website, to_path))
        response = requests.put(
            url, data=data, auth=(self.username, self.password))
        if response.status_code == requests.codes.ok:
            try:
                if response.json() is None:
                    raise ValueError("null response")
                json.loads(response.text)
                log.info(response.text)
            except ValueError:
                if retry<5:
                    log.warning("Upload %s failed. Retry..."%to_path)
                    self.upload_to_cloudflare(data, to_path, retry=retry+1)
        elif retry<5:
            log.warning("Upload %s failed. Retry..."%to_path)
            self.upload_to_cloudflare(data, to_path, retry=retry+1)
        else:
            raise RuntimeError("Upload %s failed"%to_path)



class Combiner:
    def __init__(self):
        self.root_path = read_env("GDRIVEUPLOAD_ROOT")
        self.tmpdir = read_env("GDRIVEUPLOAD_TMPDIR", "tmp/")

    def combine(self):
        for pp in glob(os.path.join(self.root_path, self.tmpdir, "*.path")):
            log.info("combining %s" % pp)
            with open(pp) as f:
                file_list = [x.strip() for x in f.readlines()]
            to_path = os.path.join(self.root_path, file_list[0])
            with tempfile.NamedTemporaryFile('wb') as wfd:
                for ff in tqdm(file_list[1:]):
                    from_path = os.path.join(self.root_path, ff)
                    log.info("copying %s to %s" % (from_path, wfd.name))
                    with open(from_path, 'rb') as fd:
                        shutil.copyfileobj(fd, wfd)
                log.info("copy %s to %s"%(wfd.name, to_path))
                shutil.copyfile(wfd.name, to_path)
            log.info("removing files...")
            file_list.append(pp)
            for ff in tqdm(file_list[1:]):
                remove_path = os.path.join(self.root_path, ff)
                log.info("removing %s"%remove_path)
                os.remove(remove_path)

def upload(args):
    file_name=args.file_name
    to_path=args.to_path
    Uploader().upload(file_name, to_path)

def combine(args):
    Combiner().combine()

def cmd():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_upload = subparsers.add_parser("upload")
    parser_upload.add_argument('--file_name', '-f', type=str)
    parser_upload.add_argument('--to_path', '-t', type=str)
    parser_upload.set_defaults(func=upload)
    parser_combine = subparsers.add_parser("combine")
    parser_combine.set_defaults(func=combine)
    args = parser.parse_args()
    args.func(args)

# tst
if __name__ == "__main__":
    cmd()
