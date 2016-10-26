#!/usr/bin/env python
# -*- coding: utf-8 -*-

import util


def syncLocal():
    '''
    update local file changes
    '''
    # load self files info list
    fileInfos = util.FileInfos(util.LOCAL_INFO_FILE)
    if fileInfos:
        # update infos
        fileInfos.update()
        # save local files
        fileInfos.save()

if __name__ == '__main__':
    try:
        syncLocal()
    except Exception, e:
        print e
