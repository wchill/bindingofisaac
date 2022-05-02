import argparse
import os
import json
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-folder", "-i", required=True)
    parser.add_argument("--output-folder", "-o", required=False)
    args = parser.parse_args()
    itempools_path = os.path.join(args.input_folder, "itempools.xml")
    metadata_path = os.path.join(args.input_folder, "items_metadata.xml")

    output_folder = args.output_folder if args.output_folder else args.input_folder

    output = {"itempools": {}, "metadata": {}}
    with open(itempools_path, "r") as f, open(metadata_path, "r") as g:
        item_pools = ET.fromstring(f.read())

        for idx, pool in enumerate(item_pools):
            assert pool.tag == "Pool"
            pool_list = []
            for item in pool:
                assert item.tag == "Item"
                pool_list.append(
                    {
                        "id": int(item.attrib["Id"]),
                        "weight": float(item.attrib["Weight"]),
                    }
                )
            output["itempools"][idx] = pool_list

        items_metadata = ET.fromstring(g.read())
        assert items_metadata.tag == "items"

        for item in items_metadata:
            if item.tag == "item":
                item_id = int(item.attrib["id"])
                item_quality = int(item.attrib["quality"])
                output["metadata"][item_id] = {"quality": item_quality}

    with open(os.path.join(output_folder, "itemdata.json"), "w") as f:
        json.dump(output, f)


if __name__ == "__main__":
    main()
