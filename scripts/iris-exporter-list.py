#!/usr/bin/env python3
from argparse import ArgumentParser

from iris_client import IrisClient


def main():
    parser = ArgumentParser()
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    with IrisClient() as client:
        measurements = client.all(
            "/measurements/",
            params=dict(only_mine=False, state="finished", tag=args.tag),
        )
        for measurement in measurements:
            for agent in measurement["agents"]:
                measurement_uuid = measurement["uuid"]
                agent_uuid = agent["agent_uuid"]
                print(measurement_uuid, agent_uuid)


if __name__ == "__main__":
    main()
