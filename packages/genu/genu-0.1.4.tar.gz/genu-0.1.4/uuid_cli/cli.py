import uuid
import argparse
from typing import List

try:
    from uuid6 import uuid7
    has_uuid7 = True
except ImportError:
    has_uuid7 = False


def generate_uuid(uuid_version: int, count: int, namespace: str = None) -> List[uuid.UUID]:
    uuids = []
    for _ in range(count):
        if uuid_version == 1:
            uuids.append(uuid.uuid1())
        elif uuid_version == 3:
            if not namespace:
                raise ValueError("Namespace is required for UUID version 3.")
            uuids.append(uuid.uuid3(uuid.NAMESPACE_URL, namespace))
        elif uuid_version == 4:
            uuids.append(uuid.uuid4())
        elif uuid_version == 5:
            if not namespace:
                raise ValueError("Namespace is required for UUID version 5.")
            uuids.append(uuid.uuid5(uuid.NAMESPACE_URL, namespace))
        elif uuid_version == 7 and has_uuid7:
            uuids.append(uuid7())
        else:
            raise ValueError("Unsupported UUID version. Use 1, 3, 4, 5, or 7.")
    return uuids


def main() -> None:
    version = '0.1.4'

    parser = argparse.ArgumentParser(description="Generate UUIDs of different types.")
    parser.add_argument("-u", "--uuid-version", type=int, choices=[1, 3, 4, 5, 7], help="UUID version to generate (1, 3, 4, 5, 7)")
    parser.add_argument("-c", "--count", type=int, default=1, help="Number of UUIDs to generate")
    parser.add_argument("--namespace", type=str, help="Namespace URL for UUID version 3 or 5")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {version}")
    args = parser.parse_args()

    try:
        uuid_version = args.uuid_version if args.uuid_version else 4
        uuids = generate_uuid(uuid_version, args.count, args.namespace)
        for u in uuids:
            print(u)
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()