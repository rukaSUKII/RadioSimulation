import pygame
import sys
from vlc import MediaPlayer
from math import floor
from csv import reader

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
        difference = round(abs(self.currentFreqOfSimulation - self.realFreqOfRadiostation), 1)

        # if it is close enough start playing this station
        if difference == self.difference and self.currentStation != self.prevStation:
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
    toPlay.playRadio()
    toPlay.isSelected = True


class Antenna:
    def __init__(self, image_path, position, angle_limits, start_angle=0, scale_factor=0.5):
        original_image = pygame.image.load(image_path).convert_alpha()
        scaled_size = (int(original_image.get_width() * scale_factor), int(original_image.get_height() * scale_factor))
        self.image = pygame.transform.scale(original_image, scaled_size)
        self.angle = start_angle
        self.prev_mouse_x = 0
        self.dragging = False
        self.angle_limits = angle_limits
        self.position = position
        self.rect = pygame.Rect((position[0]-400, position[1]-390), (437, 437))

    def update_angle(self, mouse_x):
        if self.dragging:
            dx = mouse_x - self.prev_mouse_x
            rotation_factor = dx / 1000.0
            self.angle += 360 * rotation_factor
            self.angle = max(self.angle_limits['min'], min(self.angle, self.angle_limits['max']))
            self.prev_mouse_x = mouse_x

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect()

        # Set the lower right corner as the rotation center
        rotated_rect.bottomright = self.rect.bottomright
        screen.blit(rotated_image, rotated_rect.topleft)


class Dot:
    def __init__(self, image_path, position, scale_factor=0.5):
        original_image = pygame.image.load(image_path).convert_alpha()
        scaled_size = (int(original_image.get_width() * scale_factor), int(original_image.get_height() * scale_factor))
        self.image = pygame.transform.scale(original_image, scaled_size)
        self.position = position
        self.rect = self.image.get_rect(center=self.position)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


class Knob:
    def __init__(self, image_path, initial_position, angle_limits, start_angle=0, scale_factor=0.5):
        original_image = pygame.image.load(image_path).convert_alpha()
        scaled_size = (int(original_image.get_width() * scale_factor), int(original_image.get_height() * scale_factor))
        self.image = pygame.transform.scale(original_image, scaled_size)
        self.angle = start_angle
        self.prev_mouse_x = 0
        self.dragging = False
        self.angle_limits = angle_limits
        self.position = initial_position
        self.rect = self.image.get_rect(center=self.position)

    def update_angle(self, mouse_x):
        if self.dragging:
            dx = mouse_x - self.prev_mouse_x
            rotation_factor = dx / 2000.0
            self.angle += 360 * rotation_factor
            self.angle = max(self.angle_limits['min'], min(self.angle, self.angle_limits['max']))
            self.prev_mouse_x = mouse_x

    def get_mapped_value(self, range_params):
        angle_range = self.angle_limits['max'] - self.angle_limits['min']
        mapped_value = ((self.angle - self.angle_limits['min']) / angle_range) * (range_params[1] - range_params[0]) + range_params[0]
        return max(range_params[0], min(range_params[1], round(mapped_value, 1)))

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)


class RadioApp:
    def __init__(self, sound):
        self.sound = sound
        pygame.init()
        self.width, self.height = 1141, 965
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Radio Tuner")
        self.radio_image = pygame.image.load("radio.png").convert_alpha()
        self.radio_image = pygame.transform.scale(self.radio_image, (1141, 765))
        self.white_surface = pygame.Surface((self.width, self.height))
        self.white_surface.fill((255, 255, 255))
        self.knobs = [
            Knob("mainKnob.png", (843, 448), {'min': -20, 'max': 120}, start_angle=-20, scale_factor=0.5),
            Knob("smallKnob.png", (706, 767), {'min': 140, 'max': 190}, start_angle=140, scale_factor=0.5),
            Knob("smallKnob.png", (978, 768), {'min': 25, 'max': 130}, start_angle=25, scale_factor=0.5)
        ]
        self.prev_fm_value = 88
        self.prev_volume_value = 0
        self.is_fm = True
        self.old_is_fm = True
        self.fmchanged = 0
        self.clock = pygame.time.Clock()
        self.dot = Dot("dot.png", (910, 802), scale_factor=0.5)
        self.antenna = Antenna("antenka.png", (900, 180), {'min': -85, 'max': -60}, start_angle=-85, scale_factor=0.5)
        self.radioFM = RadioPlayer(stationsPath='radio_control_files\\RadioFM.csv',
                                  defFreq=88,
                                  defVolume=0,
                                  minFreq=88,
                                  maxFreq=108,
                                  isSelected=True,
                                  difference=0.5)
        self.radioAM = RadioPlayer(stationsPath='radio_control_files\RadioAM.csv',
                                  defFreq=55,
                                  defVolume=0,
                                  minFreq=53,
                                  maxFreq=160,
                                  isSelected=False,
                                  difference=2)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.old_is_fm = self.is_fm
            if self.knobs[1].get_mapped_value((0, 100)) >= 50:
                self.is_fm = 0
            else:
                self.is_fm = 1

            if self.is_fm != self.old_is_fm:
                if self.is_fm == 1:
                    switchType(self.radioAM, self.radioFM, self.knobs[0].get_mapped_value((88, 108)))
                else:
                    switchType(self.radioFM, self.radioAM, self.knobs[0].get_mapped_value((55, 160)))

            volume_value = self.knobs[2].get_mapped_value((0, 100))

            if self.is_fm == 1:
                if self.knobs[0].get_mapped_value((88, 108)) != self.prev_fm_value:
                    self.print_values(self.knobs[0].get_mapped_value((88, 108)), volume_value)
                    self.radioFM.changeStation(self.knobs[0].get_mapped_value((88, 108)))
                self.prev_fm_value = self.knobs[0].get_mapped_value((88, 108))
            elif self.is_fm == 0:
                if self.knobs[0].get_mapped_value((55, 160)) != self.prev_fm_value:
                    self.print_values(self.knobs[0].get_mapped_value((55, 160)), volume_value)
                    self.radioAM.changeStation(self.knobs[0].get_mapped_value((55, 160)))
                self.prev_fm_value = self.knobs[0].get_mapped_value((55, 160))

            if volume_value != self.prev_volume_value:
                if self.is_fm == 1:
                    self.radioFM.changeVolume(round(self.knobs[2].get_mapped_value((0, 100))))
                else:
                    self.radioAM.changeVolume(round(self.knobs[2].get_mapped_value((0, 100))))
                self.prev_volume_value = volume_value

            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_button_down(event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.handle_mouse_button_up()
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)

    def handle_mouse_button_down(self, event):
        for knob in self.knobs:
            if knob.rect.collidepoint(event.pos):
                knob.dragging = True
                knob.prev_mouse_x = event.pos[0]

        if self.antenna.rect.collidepoint(event.pos):
            self.antenna.dragging = True
            self.antenna.prev_mouse_x = event.pos[1]

    def handle_mouse_button_up(self):
        for knob in self.knobs:
            knob.dragging = False
        self.antenna.dragging = False

    def handle_mouse_motion(self, event):
        for knob in self.knobs:
            knob.update_angle(event.pos[0])
        self.antenna.update_angle(-event.pos[1])

    def update(self):
        pass

    def draw(self):
        temp_surface = self.white_surface.copy()

        self.antenna.draw(temp_surface)
        temp_surface.blit(self.radio_image, (0, 200))
        for knob in self.knobs:
            knob.draw(temp_surface)
        if self.knobs[2].get_mapped_value((0, 100)) >= 1:
            self.dot.draw(temp_surface)

        # Blit the temporary surface onto the screen
        self.screen.blit(temp_surface, (0, 0))

    def print_values(self, fm_value, volume_value):
        band = "FM" if self.is_fm else "AM"
        print(f"{band} Frequency: {fm_value}, Volume: {volume_value}")

if __name__ == "__main__":
    pygame.mixer.init()
    sound = pygame.mixer.Sound('radio_control_files\\radio_noise.mp3')
    sound.set_volume(0)
    sound.play(loops=-1)
    app = RadioApp(sound)
    app.run()
