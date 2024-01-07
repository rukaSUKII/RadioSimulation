from vlc import MediaPlayer, Instance
from math import floor
import threading
from time import sleep
from csv import reader
from pygame import mixer

def loadStations(path:str) -> list:  
    with open(path) as csv_file:
        return list(enumerate(reader(csv_file),1))

def findStationIndex(stationFreq:float, listOfStations:list):

    minIndex = 0 
    minDiff = 100
    for index, element in enumerate(listOfStations):
        if abs(stationFreq - float(element[1][2])) < minDiff:
            minIndex = index
            minDiff = abs(stationFreq - float(element[1][2]))

    return minIndex




class RadioPlayer:
    def __init__(self, stationsPath:str, noisePath:str, defFreq:float, defVolume:int, minFreq:float, maxFreq:float, isSelected: bool):
        self.stations = loadStations(stationsPath)
        self.currentFreqOfSimulation:float = defFreq
        self.currentStation = findStationIndex(defFreq, self.stations)
        self.prevStation = -1
        self.isSelected = True
        self.realFreqOfRadiostation = self.getRealFrequencyOfRadioStation(self.currentStation)

        self.minFreq = minFreq
        self.maxFreq = maxFreq
        self.radiostationVolume = defVolume

        self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())

        mixer.init()
        self.noisePlayer = mixer.Sound(noisePath)
        
        self.changeVolume(self.radiostationVolume)
        if(self.isSelected):
            self.playRadio()
        else:
            self.stopRadio()
        

    def __str__(self):
        return f'StationFreq: {self.realFreqOfRadiostation}; deviceFreq: {self.currentFreqOfSimulation};Vol: {self.radiostationVolume}; StationVol: {self.radiostationPlayer.audio_get_volume()};noiseVol: {self.noisePlayer.get_volume()}'
    
    def changeCurrentFreqOfSimulation(self, value:float):
        if self.minFreq <= value <= self.maxFreq:
            self.currentFreqOfSimulation = value
            return 0        
        return 1

    def changeStation(self, freq: float):
        if(self.changeCurrentFreqOfSimulation(freq)): return
        prevListFreq = nextListFreq = -1

        if self.currentStation - 1 >= 0:
            prevListFreq = self.getRealFrequencyOfRadioStation(self.currentStation - 1)
        if self.currentStation + 1 < len(self.stations):
            nextListFreq = self.getRealFrequencyOfRadioStation(self.currentStation + 1)

        difference = round(abs(self.currentFreqOfSimulation - self.realFreqOfRadiostation),1)
        if (round(abs(self.currentFreqOfSimulation - prevListFreq),1) < difference) and prevListFreq>=0:
            self.prevStation = self.currentStation
            self.currentStation = self.currentStation - 1
            self.realFreqOfRadiostation = self.getRealFrequencyOfRadioStation(self.currentStation)
        elif (round(abs(self.currentFreqOfSimulation - nextListFreq),1) < difference) and nextListFreq>=0:
            self.prevStation = self.currentStation
            self.currentStation = self.currentStation + 1
            self.realFreqOfRadiostation = self.getRealFrequencyOfRadioStation(self.currentStation)

        difference = round(abs(self.currentFreqOfSimulation - self.realFreqOfRadiostation),1)
        
        if difference == 0.2 and self.currentStation!=self.prevStation:
            self.stopRadio()
            self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())
            self.changeVolume(self.radiostationVolume)
            self.playRadio()
        else:
            self.changeVolume(self.radiostationVolume)


    def changeVolume(self, value: int):
        if value < 0 or value > 100: return
        
        self.radiostationVolume = value
        difference = round(abs(self.realFreqOfRadiostation - self.currentFreqOfSimulation),1)
        if difference == 0.1:
            self.radiostationPlayer.audio_set_volume(floor((0.6*self.radiostationVolume)))
            self.noisePlayer.set_volume(round((0.5*self.radiostationVolume)/100,2))
        
        elif difference == 0:
            self.radiostationPlayer.audio_set_volume(self.radiostationVolume)
            self.noisePlayer.set_volume(0)

        else:
            self.radiostationPlayer.audio_set_volume(0)
            self.noisePlayer.set_volume(round(self.radiostationVolume/100,2))
        
    def radiostationIsPlaying(self):
        return self.radiostationPlayer.is_playing()
        
    def getCurrentStationName(self):
        return self.stations[self.currentStation][1][0]
 
    def getRealFrequencyOfRadioStation(self, index: int):
        return float(self.stations[index][1][2])

    def getCurrentStationAddress(self):
        return self.stations[self.currentStation][1][1]
    
    def stopRadio(self):
        self.radiostationPlayer.pause()
        self.noisePlayer.stop()

    def playRadio(self):
        self.radiostationPlayer.play()
        self.noisePlayer.play(loops=-1)


def switchType(toMute:RadioPlayer, toPlay:RadioPlayer, freq:float, vol:int):
    toMute.stopRadio()
    toMute.isSelected = False
    toPlay.changeStation(freq)
    toPlay.changeVolume(vol)
    toPlay.playRadio()
    toPlay.isSelected = True