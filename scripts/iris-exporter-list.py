#!/usr/bin/env python3
from argparse import ArgumentParser
from os import environ

from iris_client import IrisClient


def main():
    parser = ArgumentParser()
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    with IrisClient(
        base_url=environ.get("IRIS_BASE_URL", "http://api.docker.localhost"),
        username=environ.get("IRIS_USERNAME", "admin@example.org"),
        password=environ.get("IRIS_PASSWORD", "admin"),
    ) as client:
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
