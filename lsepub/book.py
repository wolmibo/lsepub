# Copyright (c) 2024 wolmibo
# SPDX-License-Identifier: MIT

import xml.etree.ElementTree as ET
from zipfile import ZipFile, BadZipFile
import re


class Book:
    def __init__(self, path):
        self._path = path
        self._title = None
        self._identifier = None
        self._language = None
        self._creators = []
        self._subjects = []
        self._warnings = []

        self._load_archive()

    def is_epub(self):
        return self._is_epub

    def path(self):
        return self._path

    def identifier(self):
        return self._identifier

    def language(self):
        return self._language

    def title(self):
        return self._title

    def creators(self):
        return self._creators

    def subjects(self):
        return self._subjects

    def warnings(self):
        return self._warnings

    def _load_archive(self):
        try:
            with ZipFile(self._path, 'r') as archive:
                files = archive.namelist()

                if ('mimetype' not in files or
                        'META-INF/container.xml' not in files):
                    self._is_epub = False
                    return

                mimetype = archive.open('mimetype').read().decode('ascii')
                if mimetype != 'application/epub+zip':
                    self._is_epub = False
                    return

                opfs = Book._find_opfs(archive.open('META-INF/container.xml')
                                       .read()
                                       .decode('utf-8'))
                if opfs == []:
                    self._is_epub = False
                    self._warnings.append('Missing rootfile in archive')
                    return

                for opf in opfs:
                    if opf not in files:
                        self._warnings.append(
                            f'Listed rootfile "{opf}" missing from archive')
                        continue

                    self._append_metadata(archive.open(opf)
                                          .read()
                                          .decode('utf-8'))

            self._is_epub = True

        except BadZipFile:
            self._is_epub = False

    def _append_metadata(self, xml):
        root = ET.fromstring(xml)
        ns = re.match(r'{.*}', root.tag).group(0)

        if root.tag != f'{ns}package':
            return

        for meta in root.findall(f'{ns}metadata'):
            for child in meta:
                if child.tag.endswith('identifier'):
                    self._identifier = child.text
                elif child.tag.endswith('title'):
                    self._title = child.text
                elif child.tag.endswith('language'):
                    self._language = child.text
                elif child.tag.endswith('creator'):
                    self._creators.append(child.text)
                elif child.tag.endswith('subject'):
                    self._subjects.append(child.text)

    def _find_opfs(xml):
        root = ET.fromstring(xml)

        ns = re.match(r'{.*}', root.tag).group(0)

        if root.tag != f'{ns}container':
            return []

        candidates = []
        for rfs in root.findall(f'{ns}rootfiles'):
            for rf in rfs.findall(f'{ns}rootfile'):
                keys = rf.attrib.keys()

                if 'full-path' not in keys:
                    continue

                if 'media-type' in keys:
                    if (rf.attrib['media-type'] !=
                            'application/oebps-package+xml'):
                        continue

                candidates.append(rf.attrib['full-path'])

        return candidates
