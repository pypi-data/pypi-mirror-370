import argparse
import logging
from pathlib import Path
import pyaxml
from pyaxml import conf
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

import zipfile


def main() -> int:
    """cli function"""

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=[
        "axml2xml",
        "xml2axml",
        "arsc2xml"
    ]) 
    parser.add_argument("-i", "--input", help="Specify the apk input file")
    parser.add_argument("-o", "--output", help="Specify the apk output file")
    parser.add_argument("-p", "--path", help="path of specific file in zip")
    parser.add_argument("-v", "--version", help="version of pyaxml", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(f"version {conf.VERSION}")
        return 0
    
    if not args.input:
        logging.error("No input provided")
        parser.print_help()
        return 1
    
    if args.command == "axml2xml":
        with open(args.input, "rb") as f:
            xml = None
            signature = f.read(2)
            f.seek(0)
            if signature != b'\x50\x4B':
                # Read AXML
                axml, _ = pyaxml.AXML.from_axml(f.read())
                xml = axml.to_xml()
            else:
                try:
                    with zipfile.ZipFile(f) as zip_file:
                        if args.path:
                            if args.path in zip_file.namelist():
                                with zip_file.open(args.path) as file:
                                    axml, _ = pyaxml.AXML.from_axml(file.read())
                                    xml = axml.to_xml()
                        else:
                            if 'AndroidManifest.xml' in zip_file.namelist():
                                with zip_file.open('AndroidManifest.xml') as manifest_file:
                                    axml, _ = pyaxml.AXML.from_axml(manifest_file.read())
                                    xml = axml.to_xml()
                except zipfile.BadZipFile:
                    print("It look like a ZIP file but it is not")
                    return 1
        # Rewrite the file
        if xml is None:
            print("path not found")
        else:
            if args.output:
                with open(args.output, "w") as f:
                    f.write(etree.tostring(xml, encoding='unicode', pretty_print=True))
            else:
                print(etree.tostring(xml, encoding='unicode', pretty_print=True))
    elif args.command == "xml2axml":
        if not args.output:
            logging.error("No output provided")
            parser.print_help()
            return 1
        with open(args.input, "r") as f:
            # Read XML
            root = etree.fromstring(f.read())
            axml_object = pyaxml.AXML()
            axml_object.from_xml(root)
        # Rewrite the file
        with open(args.output, "wb") as f:
            f.write(axml_object.pack())
    elif args.command == "arsc2xml":
        with open(args.input, "rb") as f:
            signature = f.read(2)
            f.seek(0)
            if signature != b'\x50\x4B':
                # Read AXML
                axml, _ = pyaxml.ARSC.from_axml(f.read())
                xml = axml.list_packages()
            else:
                try:
                    with zipfile.ZipFile(f) as zip_file:
                        if 'resources.arsc' in zip_file.namelist():
                            with zip_file.open('resources.arsc') as manifest_file:
                                axml, _ = pyaxml.ARSC.from_axml(manifest_file.read())
                                xml = axml.list_packages()
                except zipfile.BadZipFile:
                    print("It look like a ZIP file but it is not")
                    return 1
        # Rewrite the file
        if args.output:
            with open(args.output, "w") as f:
                f.write(xml)
        else:
            print(xml)
