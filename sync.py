#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
import win32file
import win32com.client as com


INFO_FILE = 'files.list'

DEST_DISK = None


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
        list_dirs = os.walk(rootDir)
        for root, dirs, files in list_dirs:
            for f in files:
                curFiles.append(os.path.join(root, f)[len(rootDir) + 1:])

        # add cur files to add list
        # remove cur files in del list
        for f in curFiles:
            if f not in self.lists['add']:
                self.lists['add'].append(f)
                if f in self.lists['del']:
                    self.lists['del'].remove(f)
                pmsg('add %s' % f)

        # move add list files not in cur to del list
        for f in self.lists['add']:
            if f not in curFiles and f not in self.lists['del']:
                self.lists['del'].append(f)
                pmsg('del %s' % f)

        self.lists['add'] = curFiles

        # make del list unique
        delFiles = []
        for f in self.lists['del']:
            if f not in delFiles:
                delFiles.append(f)
        self.lists['del'] = delFiles

    def save(self):
        text = json.dumps(self.lists, indent=2)
        print text
        try:
            with open(self.infoPath, 'w') as f:
                f.write(text)
                pmsg('save in %s' % self.infoPath)
        except Exception, e:
            pmsg(e)


def pmsg(msg):
    print '[sync] %s' % msg


def sync():
    try:
        # update local file infos
        localRoot = os.path.dirname(os.path.abspath(__file__))
        local = FileInfos(os.path.join(localRoot, INFO_FILE))
        local.update()
        pmsg('local updated')

        # search other disks for copies
        disks = otherDisks()
        # get cur file path without disk
        subFile = os.path.abspath(__file__)[2:]
        remoteCur = None
        for d in disks:
            p = os.path.join(d, subFile)
            if os.path.exists(p):
                remoteCur = p
                break

        # if not found, find largest free disk
        if not remoteCur:
            disk = largestFreeDisk(disks)
            if disk:
                remoteCur = os.path.join(disk, subFile)
                # make root dir
                os.makedirs(os.path.dirname(remoteCur))
            else:
                raise Exception('no largest disk')

        remoteRoot = os.path.dirname(remoteCur)
        pmsg('remote root %s' % remoteRoot)

        # if found,load remote file infos
        remote = FileInfos(os.path.join(remoteRoot, INFO_FILE))
        # update remote file infos
        remote.update()
        pmsg('remote updated')

        # add files from local to remote
        for f in local.lists['add']:
            if not f.endswith(INFO_FILE) and f not in remote.lists['add']:
                src = os.path.join(localRoot, f)
                dest = os.path.join(remoteRoot, f)
                copyFile(src, dest)
                remote.lists['add'].append(f)
                pmsg('copy file %s to %s' % (src, dest))

        # add files from remote to local
        for f in remote.lists['add']:
            if not f.endswith(INFO_FILE) and f not in local.lists['add']:
                src = os.path.join(remoteRoot, f)
                dest = os.path.join(localRoot, f)
                copyFile(src, dest)
                local.lists['add'].append(f)
                pmsg('copy file %s to %s' % (src, dest))

        # del files from local to remote
        for f in local.lists['del']:
            delFile(os.path.join(remoteRoot, f))
            pmsg('del file %s' % os.path.join(remoteRoot, f))

        # del files from remote to local
        for f in remote.lists['del']:
            delFile(os.path.join(localRoot, f))
            pmsg('del file %s' % os.path.join(localRoot, f))

        # save file infos
        remote.save()
        local.save()

        pmsg('sync finished')

    except Exception, e:
        pmsg(e)


def copyFile(src, dest):
    try:
        destDir = os.path.dirname(dest)
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        win32file.CopyFile(src, dest, 0)
    except Exception, e:
        pmsg(e)


def delFile(f):
    try:
        os.remove(f)
    except Exception, e:
        pmsg(e)


def otherDisks():
    if DEST_DISK:
        return [DEST_DISK]
    else:
        curDisk = os.path.abspath(__file__)[:2].upper()
        disks = []
        for i in range(65, 91):
            vol = chr(i) + ':'
            if os.path.isdir(vol)and vol != curDisk:
                disks.append(vol)
        return disks


def largestFreeDisk(disks):
    size = 0.
    disk = None
    for d in disks:
        if FreeSpace(d) > size:
            size = FreeSpace(d)
            disk = d
    return disk


def FreeSpace(drive):
    """ Return the FreeSpace of a shared drive [GB]"""
    try:
        fso = com.Dispatch("Scripting.FileSystemObject")
        drv = fso.GetDrive(drive)
        return drv.FreeSpace / 2**30
    except:
        return 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        DEST_DISK = sys.argv[1]
    sync()
