from vlc import MediaPlayer
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

class SingleSoundThread(threading.Thread):
    def __init__(self, path:str, volume:int):
        threading.Thread.__init__(self)
        self.filePath = path
        self.stopped = False
        self.player = MediaPlayer(self.filePath)
        self.player.audio_set_volume(volume)
    def start(self):
        while self.stopped==False:
            self.player.play()
            sleep(self.player.get_length())
            self.player.stop()

    def stop(self):
        self.stopped(True)



class RadioPlayer:
    def __init__(self, stationsPath:str, noisePath:str, defFreq:float, defVolume:int, minFreq:float, maxFreq:float):
        self.stations = loadStations(stationsPath)
        self.currentFreqOfSimulation = defFreq
        self.currentStation = findStationIndex(defFreq, self.stations)
        self.realFreqOfRadiostation = float(self.getRealFrequencyOfRadioStation(self.currentStation))
        self.minFreq = minFreq
        self.maxFreq = maxFreq
        self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())
        self.radiostationVolume = defVolume
        self.changeVolume(self.radiostationVolume)

        self.noisePlayer = SingleSoundThread(noisePath, self.radiostationVolume)

        self.playRadio()
        self.noisePlayer.start()

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
        if difference == 0.1:
            self.stopRadio()
            self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())  
            self.playRadio()

        self.changeVolume(self.radiostationVolume)

    def changeVolume(self, value: int):
        if 0 < value < 100 and value!=self.radiostationVolume:
            self.radiostationVolume = value

        difference = abs(self.realFreqOfRadiostation - self.currentFreqOfSimulation)
        if difference == 0.1:
            self.radiostationPlayer.audio_set_volume(0.7 * self.radiostationVolume)
            self.noisePlayer.player.audio_set_volume(0.5 * self.radiostationVolume)
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
        return self.stations[index][1][2]

    def getCurrentStationAddress(self):
        return self.stations[self.currentStation][1][1]
    
    def stopRadio(self):
        self.radiostationPlayer.stop()
        self.noisePlayer.stop()

    def playRadio(self):
        self.radiostationPlayer.play()
        self.noisePlayer.start()

    
radio = RadioPlayer(stationsPath='radio_control_files\\RadioFM.csv',
                    noisePath='radio_control_files\\radio_noise.mp3', 
                    defFreq=90.5,
                    defVolume=80,
                    minFreq=88,
                    maxFreq=108)

while(True):
    sleep(2)
    True


