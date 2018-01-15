import os
import glob
import argparse
import pickle

import joblib
import tensorflow as tf

from rllab.sampler.utils import rollout
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('glob_patterns',
                        type=str,
                        nargs='+',
                        help='Glob patterns for paths of the snapshot files.')
    parser.add_argument('--max-path-length', '-l', type=int, default=1000)
    parser.add_argument('--deterministic', '-d', dest='deterministic',
                        action='store_true')
    parser.add_argument('--no-deterministic', '-nd', dest='deterministic',
                        action='store_false')
    parser.add_argument('--policy_h', type=int)
    parser.add_argument('--num_simulations', type=int, default=4)
    parser.add_argument('--path_save_path', type=str)
    parser.set_defaults(deterministic=True)

    args = parser.parse_args()

    return args

def default_path_save_path(snapshot_file_path):
    """generate path_save_path based on the snapshot_file_path"""
    parts = snapshot_file_path.split("/")
    snapshot_file_name, snapshot_file_extension = os.path.splitext(snapshot_file_path)
    path_save_path = snapshot_file_name + "_path" + snapshot_file_extension
    return path_save_path

def simulate_policy(snapshot_path,
                    num_simulations,
                    max_path_length,
                    path_save_path=None):
    with tf.Session() as sess:
        data = joblib.load(snapshot_path)
        if 'algo' in data.keys():
            policy = data['algo'].policy
            env = data['algo'].env
        else:
            policy = data['policy']
            env = data['env']

        paths = []
        for i in range(num_simulations):
            with policy.fix_h():
                path = rollout(env, policy,
                               max_path_length=max_path_length,
                               animated=False)
                paths.append(path)

    path_save_path = path_save_path or default_path_save_path(snapshot_path)

    with open(path_save_path, "wb") as f:
        pickle.dump(paths, f)

def simulate_policies(args):
    for glob_path in args.glob_patterns:
        for snapshot_path in glob.glob(glob_path):
            tf.reset_default_graph()
            simulate_policy(snapshot_path,
                            args.num_simulations,
                            args.max_path_length)

if __name__ == "__main__":
    args = parse_args()
    simulate_policies(args)