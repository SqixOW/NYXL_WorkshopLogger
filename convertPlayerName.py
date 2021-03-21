import re
import os
import sys

def relpace(fileName, srcStr, dstStr):
    fd = open(fileName)
    newFile = fd.read()
    newFile = re.subn(srcStr, dstStr, newFile)[0]
    return newFile
    
def main():
    fileName = sys.argv[1:]
    

if __name__ == '__main__':
    main()