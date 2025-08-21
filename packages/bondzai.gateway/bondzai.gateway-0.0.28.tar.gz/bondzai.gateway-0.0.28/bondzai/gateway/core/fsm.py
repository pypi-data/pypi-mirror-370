# coding: utf-8

import os


def dir_exists(dir_path):
    return os.path.isdir(dir_path)

def file_exists(file_path):
    return os.path.exists(file_path)

def create_dir(dir_path):
    if not dir_exists(dir_path):
        os.makedirs(dir_path)

def get_sub_dir(dir_path):
    results = []
    if dir_exists(dir_path):
        for f in os.listdir(dir_path):
            if os.path.isdir(dir_path + "/" + f):
                results.append(f)
    return results

def get_files(dir_path, extension=None):
    results = []
    if dir_exists(dir_path):
        for f in os.listdir(dir_path):
            if os.path.isfile(dir_path + "/" + f) and (not extension or f.endswith("." + extension)):
                results.append(f)
    return results

def remove_file(file_path):
    if file_exists(file_path):
        os.remove(file_path)
