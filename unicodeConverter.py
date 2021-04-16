#-*- coding: utf-8 -*-
import os
import sys
import codecs
from logConverter import LogPattern
from userDatabase import Database

class Converter:
    def __init__(self, fileName):
        self.fileName = fileName
        self.database = Database()
        self.logPattern = LogPattern()
    
    def define_basket_list(self,line): # define basket list (delete [hh:mm:ss])
        basket_list = line[11:].split(',')
        basket_list[len(basket_list)-1] = basket_list[len(basket_list)-1].rstrip()
        return basket_list

    def replace(self):
        readFd = codecs.open(self.fileName)
        readFile = readFd.read()
        readFd.close()

        fd = codecs.open(self.fileName,'w')
        
        for line in readFile.split('\n'):
            if self.logPattern.pattern_playerInfo.match(line):
                self.playerInfo_stream_handler(line,fd)
            
            elif self.logPattern.pattern_playerData.match(line):
                self.playerData_stream_handler(line,fd)
                
            elif self.logPattern.pattern_finalblows.match(line):
                self.finalBlow_stream_handler(line,fd)
                
            elif self.logPattern.pattern_dupstart.match(line) or self.logPattern.pattern_dupend.match(line) or self.logPattern.pattern_resurrect.match(line) or self.logPattern.pattern_suicide.match(line):
                self.common_stream_handler(line,fd)
                
            else:
                fd.write(line)
                fd.write('\n')

    def playerInfo_stream_handler(self, line, fd):        
        basket_list = self.define_basket_list(line)
        
        for i in range(0, len(basket_list)):
            if basket_list[i] in list(self.database.player.keys()):          
                line = line.replace(basket_list[i],self.database.player[basket_list[i]])
        
        fd.write(line)
        fd.write('\n')
    
    def playerData_stream_handler(self, line, fd):
        basket_list = self.define_basket_list(line)

        if basket_list[1] in list(self.database.player.keys()):
            line = line.replace(basket_list[1], self.database.player[basket_list[1]])
        if basket_list[2] in list(self.database.hero.keys()):
            line = line.replace(basket_list[2], self.database.hero[basket_list[2]])
        if basket_list[19] in list(self.database.player.keys()):
            line = line.replace(basket_list[19], self.database.player[basket_list[19]])          
        
        fd.write(line)
        fd.write('\n')

    def finalBlow_stream_handler(self, line, fd):
        basket_list = self.define_basket_list(line)

        if basket_list[2] in list(self.database.player.keys()):
            line = line.replace(basket_list[2], self.database.player[basket_list[2]])
        if basket_list[3] in list(self.database.player.keys()):
            line = line.replace(basket_list[3], self.database.player[basket_list[3]])

        fd.write(line)
        fd.write('\n')
        
    def common_stream_handler(self, line, fd): # include suicide / duplicate start / duplicate end / resurrect
        basket_list = self.define_basket_list(line)

        if basket_list[2] in list(self.database.player.keys()):
            line = line.replace(basket_list[2], self.database.player[basket_list[2]])

        fd.write(line)
        fd.write('\n')
        

def main():
    fileName = sys.argv[1:][0]
    converter = Converter(fileName)
    converter.replace()

if __name__ == '__main__':
    main()