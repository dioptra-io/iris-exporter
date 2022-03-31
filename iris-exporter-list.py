#!/usr/bin/env python3
from iris_client import IrisClient


def main():
    with IrisClient() as client:
        measurements = client.all(
            "/measurements/",
            params=dict(
                only_mine=False, state="finished", tag="!public"
            ),  # TODO: Tag parameter
        )
        for measurement in measurements:
            for agent in measurement["agents"]:
                measurement_uuid = measurement["uuid"]
                agent_uuid = agent["agent_uuid"]
                print(measurement_uuid, agent_uuid)


if __name__ == "__main__":
    main()
