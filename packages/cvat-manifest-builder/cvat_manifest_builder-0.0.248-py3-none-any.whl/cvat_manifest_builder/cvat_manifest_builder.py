import argparse, hashlib, json, os, os.path
from loguru import logger
from PIL import Image
from beartype import beartype, typing


@beartype
def mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


@beartype
def get_file_parts(file_path: str) -> typing.Tuple[str, str]:
    extension = os.path.splitext(file_path)[1]
    return file_path.rstrip(extension), extension


@beartype
def get_files(input_data_path: str):
    logger.info("Input Directory: {}".format(input_data_path))
    for root, dirs, files in os.walk(input_data_path, topdown=False):
        for name in files:
            if name.endswith((".jpg", ".jpeg", ".gif", ".png")):
                # Get the full file path
                full_file_path = os.path.join(root, name)

                # Get the relative file path
                relative_file_path = os.path.relpath(
                    full_file_path,
                    input_data_path,
                )

                yield {
                    "name": name,
                    "root": root,
                    "full_file_path": full_file_path,
                    "relative_file_path": relative_file_path,
                }


@beartype
def get_file_md5(file_path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@beartype
def write_header(writer) -> None:
    writer.write('{"version":"1.0"}')
    writer.write("\n")
    writer.write('{"type":"images"}')
    writer.write("\n")


@beartype
def write_json_line(writer, line) -> None:
    writer.write(json.dumps(line))
    writer.write("\n")


@beartype
def writer_close(writer) -> None:
    writer.close()


def main(args):

    # Assert that the manifest file ends with jsonl
    assert args["output_manifest_file"].endswith(
        ".jsonl"
    ), "--output_manifest_file must have a .jsonl extension"

    # Create the directory structure
    mkdir(os.path.dirname(args["output_manifest_file"]))

    # Get all of the files in the input data path
    files = get_files(args["input_data_path"])

    # Open the jsonl output file writer
    with open(args["output_manifest_file"], "w") as writer:
        write_header(writer)

        for file in files:

            relative_file_path_without_extension, extension = get_file_parts(
                file["relative_file_path"]
            )

            image = Image.open(file["full_file_path"])

            line = {
                "name": relative_file_path_without_extension,
                "extension": extension,
                "width": image.width,
                "height": image.height,
                "checksum": get_file_md5(file["full_file_path"]),
                "meta": {"related_images": []},
            }

            write_json_line(writer, line)

            logger.debug("Saved {}{} to the manifest.".format(line["name"], extension))

        writer_close(writer)

        logger.debug(
            "Successfully created the manifest file {}".format(
                args["output_manifest_file"]
            )
        )


def app():
    parser = argparse.ArgumentParser(
        description="Builds a CVAT manifest file from a directory of images."
    )
    parser.add_argument(
        "--output_manifest_file",
        type=str,
        dest="output_manifest_file",
        default="./manifest.jsonl",
        help="Path to the output manifest file.",
        required=True,
    )

    parser.add_argument(
        "--input_data_path",
        type=str,
        dest="input_data_path",
        default="./data/",
        help="Path to the data directory.",
        required=True,
    )

    args = vars(parser.parse_args())

    main(args)
