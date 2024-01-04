from vlc import MediaPlayer
from pygame import mixer
from time import sleep
from csv import reader

def loadStations(path:str) -> list:  
    with open(path) as csv_file:
        return list(enumerate(reader(csv_file),1))
    
class RadioPlayer:
    def __init__(self, path:str):
        self.stations = loadStations(path)
        self.currentStation = 0
        self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())
        self.radiostationVolume = self.radiostationPlayer.audio_get_volume()

        mixer.init()
        mixer.music.load('radio_control_files\\radio_noise.mp3')
        mixer.music.set_volume(0.0)
        mixer.music.play(-1)

    def changeStation(self, direction: int):
        if((direction>=0 and self.currentStation+direction < len(self.stations))
           or
           (direction <  0 and self.currentStation + direction >= 0)):
            self.currentStation = self.currentStation + direction

        self.stopRadio()
        self.radiostationPlayer = MediaPlayer(self.getCurrentStationAddress())
        self.playRadio()

    def changeVolume(self, changeValue: int):
        if 0 < self.radiostationVolume + changeValue < 100:
            self.radiostationVolume = self.radiostationVolume + changeValue
            self.radiostationPlayer.audio_set_volume(self.radiostationVolume)

    def radiostationIsPlaying(self):
        return self.radiostationPlayer.is_playing()
        
    def getCurrentStationName(self):
        return self.stations[self.currentStation][1][0]
 
    def getRealFrequencyOfRadioStation(self):
        return self.stations[self.currentStation][1][2]

    def getCurrentStationAddress(self):
        return self.stations[self.currentStation][1][1]
    
    def stopRadio(self):
        self.radiostationPlayer.stop()

    def playRadio(self):
        self.radiostationPlayer.play()


    
radio = RadioPlayer('radio_control_files\\RadioFM.csv')
radio.changeVolume(-100)

#print(radio.stations)
'''
radio.playRadio()
sleep(2)
print(radio.radioIsPlaying())
radio.stopRadio()
sleep(2)
radio.playRadio()
sleep(4)
for x in range(len(radio.stations)):
    radio.changeStation(1)
    sleep(3)
    
sleep(10)
radio.changeStation(-2)
sleep(3)
radio.changeStation(1)
'''
while(True):
    True


