from vlc import MediaPlayer
from math import floor
from csv import reader
from pygame import mixer

def loadStations(path:str) -> list:
    '''Returns list of elements from csv file which path is given in path:str.'''
    with open(path) as csv_file:
        return list(enumerate(reader(csv_file),1))


def findStationIndex(stationFreq:float, listOfStations:list):
    '''Return index of the element from listOfStations based on stationFreq given where
    stationFreq matches the most freq from list'''
    minIndex = 0
    minDiff = 100
    for index, element in enumerate(listOfStations):
        if abs(stationFreq - float(element[1][2])) < minDiff:
            minIndex = index
            minDiff = abs(stationFreq - float(element[1][2]))

    return minIndex

mixer.init()
sound = mixer.Sound('radio_control_files\\radio_noise.mp3')
sound.set_volume(0)
sound.play(loops=-1)

class RadioPlayer:
    def __init__(self, stationsPath: str, defFreq: float, defVolume: int, minFreq: float, maxFreq: float, isSelected: bool, difference: float):
        self.stations = loadStations(stationsPath)
        self.currentFreqOfSimulation: float = defFreq
        self.currentStation = findStationIndex(defFreq, self.stations)
        self.prevStation = -1
        self.isSelected = isSelected
        self.realFreqOfRadiostation = self.getRealFrequencyOfRadioStation(self.currentStation)

        self.minFreq = minFreq
        self.maxFreq = maxFreq
        self.radiostationVolume = defVolume

        self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())
        self.difference = difference
        self.noisePlayer = sound

        if (self.isSelected):
            self.changeVolume(self.radiostationVolume)
            self.playRadio()
        else:
            self.stopRadio()

    def __str__(self):
        return f'StationFreq: {self.realFreqOfRadiostation}; deviceFreq: {self.currentFreqOfSimulation};Vol: {self.radiostationVolume}; StationVol: {self.radiostationPlayer.audio_get_volume()};noiseVol: {self.noisePlayer.get_volume()}'

    def changeCurrentFreqOfSimulation(self, value: float):
        '''Change currentFreqOfSimulation to value given. Limited by max and min freq of simulation'''
        if self.minFreq <= value <= self.maxFreq:
            self.currentFreqOfSimulation = round(value, 1)
            return 0
        return 1

    def changeStation(self, freq: float):
        '''Passing desired freq of simulation(from input i.e. button) to configure radio to play in the way it should work'''
        if (self.changeCurrentFreqOfSimulation(freq)): return
        # finding closest station

        temp = findStationIndex(self.currentFreqOfSimulation, self.stations)

        if temp != self.currentStation:
            self.prevStation = self.currentStation
            self.currentStation = temp
            self.realFreqOfRadiostation = self.getRealFrequencyOfRadioStation(self.currentStation)

        # checking distance to closest station
        localDifference = round(abs(self.currentFreqOfSimulation - self.realFreqOfRadiostation), 1)


        # if it is close enough start playing this station
        if localDifference == self.difference and self.currentStation != self.prevStation:
            self.stopRadio()
            self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())
            self.playRadio()
        # Takes care of proper volume levels depending on the distance to station
        self.changeVolume(self.radiostationVolume)

    def changeVolume(self, value: int):
        '''Changes volume to fit designed behaviour with noise and radiostation itself'''
        if value < 0 or value > 100: return

        self.radiostationVolume = value
        difference = round(abs(self.realFreqOfRadiostation - self.currentFreqOfSimulation), 1)
        if difference < self.difference and difference != 0:
            stationVolume = (self.difference-difference)/self.difference
            noiseVolume = 1-((self.difference-difference)/self.difference)
            print(stationVolume)
            self.radiostationPlayer.audio_set_volume(floor((stationVolume * self.radiostationVolume)))
            self.noisePlayer.set_volume(round((noiseVolume * self.radiostationVolume) / 100, 2))

        elif difference == 0:
            self.radiostationPlayer.audio_set_volume(self.radiostationVolume)
            self.noisePlayer.set_volume(0)

        else:
            self.radiostationPlayer.audio_set_volume(0)
            self.noisePlayer.set_volume(round(0.7 * self.radiostationVolume / 100, 2))

    def radiostationIsPlaying(self):
        '''Check whteher radiostation is currently playing
            if yes - return True'''
        return self.radiostationPlayer.is_playing()

    def getCurrentStationName(self):
        '''Returns the name of the radiostation given in list stations'''
        return self.stations[self.currentStation][1][0]

    def getRealFrequencyOfRadioStation(self, index: int):
        '''Returns the real frequency of the radiostation given in list stations
        to make the simulation more realistic'''
        return float(self.stations[index][1][2])

    def getCurrentStationAddress(self):
        '''Returns URL address to be able to play radiostation'''
        return self.stations[self.currentStation][1][1]

    def stopRadio(self):
        '''Stopping radio'''
        self.radiostationPlayer.stop()

    def playRadio(self):
        '''Playing radio'''
        self.radiostationPlayer.play()


def switchType(toMute: RadioPlayer, toPlay: RadioPlayer, freq: float):
    '''Function used to toogle between play types keeping configuration the same i.e. Volume
    Args:
    toMute (RadioPlayer): Object of the radio which needs to be muted
    toPlay (RadioPlayer): Object of the radio which needs to be played
    freq (float): value of the frequency passed as argument which needs to be set for specific type(i.e. FM and AM bandwiths differ)
    '''
    toMute.stopRadio()
    toMute.isSelected = False
    toPlay.changeStation(freq)
    toPlay.changeVolume(toMute.radiostationVolume)
    toPlay.isSelected = True