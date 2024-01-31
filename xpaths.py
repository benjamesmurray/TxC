import os
import zipfile
import xml.etree.ElementTree as ET
import json
import datetime


def get_full_xpath(elem, current_path, paths, seen):
    """
    Recursively build the full XPath for an element, omitting the namespace URL.
    """
    if elem is None:
        return

    # Separate the namespace URL and the local tag name
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

    # Include the tag name in the path
    tag_path = current_path + '/' + tag if current_path else tag

    if tag_path not in seen:
        paths.append(tag_path)
        seen.add(tag_path)

    # Recursively get paths for each child
    for child in elem:
        get_full_xpath(child, tag_path, paths, seen)


def get_xpaths(xml_file):
    """
    Parse the XML file and get a list of unique XPaths.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    xpaths = []
    seen_xpaths = set()
    get_full_xpath(root, '', xpaths, seen_xpaths)
    return xpaths


def process_operator_zip(operator_zip_file, temp_directory):
    with zipfile.ZipFile(operator_zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)
        extracted_files = [os.path.join(temp_directory, file) for file in zip_ref.namelist()]
        zip_data = {}
        for xml_file in extracted_files:
            if xml_file.endswith('.xml'):
                xpaths = get_xpaths(xml_file)
                zip_data[xml_file] = xpaths
        return zip_data


def process_archive(archive_zip_path, temp_directory):
    with zipfile.ZipFile(archive_zip_path, 'r') as archive_zip:
        archive_data = {}
        for file in archive_zip.namelist():
            if file.endswith('.zip'):  # Operator zip files
                # Extract operator zip file to temporary directory
                operator_zip_path = archive_zip.extract(file, temp_directory)
                operator_data = process_operator_zip(operator_zip_path, temp_directory)
                archive_data[file] = operator_data
    return archive_data


archive_zip_path = r"C:\Users\benja\PycharmProjects\TxC\Data\bodds_archive_20240131_hhyMz1y.zip"
temp_directory = "temp_extracted"
data = process_archive(archive_zip_path, temp_directory)

# Generate a timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Use the timestamp in the output file name
output_filename = f"output_{timestamp}.json"

# Save the data to the timestamped output file
with open(output_filename, "w") as outfile:
    json.dump(data, outfile, indent=4)
