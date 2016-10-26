#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json

LOCAL_INFO_FILE = 'files.list'


class FileInfos:

    def __init__(self, infoPath):
        self.infoPath = infoPath
        text = None
        try:
            with open(infoPath, 'r') as f:
                text = f.read()

        except Exception, e:
            self.lists = {'add': [], 'del': []}

        if text:
            self.lists = json.loads(text)
            if 'add' not in self.lists or 'del' not in self.lists:
                raise Exception('%s format error' % infoPath)

    def update(self):
        # list cur files
        curFiles = []
        rootDir = os.path.dirname(self.infoPath)
        if len(rootDir) == 0:
            rootDir = '.'
        list_dirs = os.walk(rootDir)
        for root, dirs, files in list_dirs:
            for f in files:
                if rootDir == '.':
                    curFiles.append(os.path.join(root, f))
                else:
                    curFiles.append(os.path.join(root, f)[len(rootDir):])

        # add cur files to add list
        # remove cur files in del list
        for f in curFiles:
            if f not in self.lists['add'] and f not in self.lists['del']:
                self.lists['add'].append(f)
                print 'add %s' % f
            if f in self.lists['del']:
                try:
                    os.remove(f)
                    print 'remove %s' % f
                except Exception, e:
                    print e

        # move add list files not in cur to del list
        for f in self.lists['add']:
            if f not in curFiles and f not in self.lists['del']:
                self.lists['del'].append(f)
                print 'del %s' % f

    def save(self):
        text = json.dumps(self.lists, indent=2)
        try:
            with open(self.infoPath, 'w') as f:
                f.write(text)
                print 'save in %s' % self.infoPath
        except Exception, e:
            print e
