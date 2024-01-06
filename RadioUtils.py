from vlc import MediaPlayer, Instance
from math import floor
import threading
from time import sleep
from csv import reader

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

def run(player: Instance):
    while True:
            player.play()
            sleep(9)
            player.stop()
class SingleSoundThread:
    def __init__(self, path:str):

        self.path = path
        self.instance = Instance("--no-xlib")
        self.player = self.instance.media_player_new()
        self.media = self.instance.media_new(self.path)
        self.player.set_media(self.media)
        self.sound_thread = threading.Thread(target=run, args=(self.player,))      

    def start(self):
        self.sound_thread.start()



class RadioPlayer:
    def __init__(self, stationsPath:str, noisePath:str, defFreq:float, defVolume:int, minFreq:float, maxFreq:float):
        self.stations = loadStations(stationsPath)
        self.currentFreqOfSimulation:float = defFreq
        self.currentStation = findStationIndex(defFreq, self.stations)
        self.realFreqOfRadiostation = self.getRealFrequencyOfRadioStation(self.currentStation)
        self.minFreq = minFreq
        self.maxFreq = maxFreq
        self.radiostationVolume = defVolume
        self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())
        
        self.noisePlayer = SingleSoundThread(noisePath)
        self.changeVolume(self.radiostationVolume)
        self.playRadio()
        

    def __str__(self):
        return f'StationFreq: {self.realFreqOfRadiostation}; deviceFreq: {self.currentFreqOfSimulation};Vol: {self.radiostationVolume}; StationVol: {self.radiostationPlayer.audio_get_volume()};noiseVol: {self.noisePlayer.player.audio_get_volume()}'
    
    def changeCurrentFreqOfSimulation(self, value:float):
        if self.minFreq <= value <= self.maxFreq:
            self.currentFreqOfSimulation = value
            return 0        
        return 1

    def changeStation(self, freq: float):
        if(self.changeCurrentFreqOfSimulation(freq)): return
        prevListFreq = nextListFreq = 0

        if self.currentStation - 1 > 0:
            prevListFreq = self.getRealFrequencyOfRadioStation(self.currentStation - 1)
        if self.currentStation + 1 < len(self.stations):
            nextListFreq = self.getRealFrequencyOfRadioStation(self.currentStation + 1)

        if abs(self.currentFreqOfSimulation - prevListFreq) < abs(self.currentFreqOfSimulation - self.realFreqOfRadiostation) and prevListFreq != 0:
            self.currentStation = self.currentStation - 1
            self.realFreqOfRadiostation = self.getRealFrequencyOfRadioStation(self.currentStation)
        if abs(self.currentFreqOfSimulation - nextListFreq) < abs(self.currentFreqOfSimulation - self.realFreqOfRadiostation) and nextListFreq != 0:
            self.currentStation = self.currentStation + 1
            self.realFreqOfRadiostation = self.getRealFrequencyOfRadioStation(self.currentStation)

        difference = abs(self.realFreqOfRadiostation - self.currentFreqOfSimulation)
        if difference <= 0.1:
            self.stopRadio()
            self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())  
            self.playRadio()

        self.changeVolume(self.radiostationVolume)

    def changeVolume(self, value: int):
        if value < 0 or value > 100: return
        
        self.radiostationVolume = value
        difference = abs(self.realFreqOfRadiostation - self.currentFreqOfSimulation)
        if difference == 0.1:
            self.radiostationPlayer.audio_set_volume(floor(0.5 * self.radiostationVolume))
            self.noisePlayer.player.audio_set_volume(floor(0.7 * self.radiostationVolume))
        elif difference == 0:
            self.radiostationPlayer.audio_set_volume(self.radiostationVolume)
            self.noisePlayer.player.audio_set_volume(0)
        else:
            self.radiostationPlayer.audio_set_volume(0)
            self.noisePlayer.player.audio_set_volume(self.radiostationVolume)
        
    def radiostationIsPlaying(self):
        return self.radiostationPlayer.is_playing()
        
    def getCurrentStationName(self):
        return self.stations[self.currentStation][1][0]
 
    def getRealFrequencyOfRadioStation(self, index: int):
        return float(self.stations[index][1][2])

    def getCurrentStationAddress(self):
        return self.stations[self.currentStation][1][1]
    
    def stopRadio(self):
        self.radiostationPlayer.stop()
        self.noisePlayer.player.stop()

    def playRadio(self):
        self.radiostationPlayer.play()
        self.noisePlayer.player.play()


