import pygame
import sys
import radioUtils as rad

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

    def updateAngle(self, mouse_x):
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
        self.sens = 2000

    def updateAngle(self, mouse_x):
        if self.dragging:
            dx = mouse_x - self.prev_mouse_x
            rotation_factor = dx / self.sens
            self.angle += 360 * rotation_factor
            self.angle = max(self.angle_limits['min'], min(self.angle, self.angle_limits['max']))
            self.prev_mouse_x = mouse_x

    def getMappedValue(self, range_params):
        angle_range = self.angle_limits['max'] - self.angle_limits['min']
        mapped_value = ((self.angle - self.angle_limits['min']) / angle_range) * (range_params[1] - range_params[0]) + range_params[0]
        return max(range_params[0], min(range_params[1], round(mapped_value, 1)))

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)


class RadioApp:
    def __init__(self):
        
        pygame.init()
        self.width, self.height = 1141, 1000
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
        self.knobs[1].sens = self.knobs[2].sens = 1000
        self.prev_fm_value = 88
        self.prev_volume_value = 0
        self.is_fm = True
        self.old_is_fm = True
        self.fm_changed = 0
        self.clock = pygame.time.Clock()
        self.dot = Dot("dot.png", (910, 802), scale_factor=0.5)
        self.antenna = Antenna("antenka.png", (900, 180), {'min': -85, 'max': -60}, start_angle=-85, scale_factor=0.5)

        self.radioFM = rad.RadioPlayer(stationsPath='radio_control_files\\RadioFM.csv',
                                  defFreq=88,
                                  defVolume=0,
                                  minFreq=88,
                                  maxFreq=108,
                                  isSelected=True,
                                  difference=0.4)
        self.radioAM = rad.RadioPlayer(stationsPath='radio_control_files\RadioAM.csv',
                                  defFreq=55,
                                  defVolume=0,
                                  minFreq=53,
                                  maxFreq=160,
                                  isSelected=False,
                                  difference=2)

    def run(self):
        while True:
            self.handleEvents()
            self.update()
            self.draw()
            self.old_is_fm = self.is_fm
            if self.knobs[1].getMappedValue((0, 100)) >= 50:
                self.is_fm = 0
            else:
                self.is_fm = 1

            if self.is_fm != self.old_is_fm:
                if self.is_fm == 1:
                    rad.switchType(self.radioAM, self.radioFM, self.knobs[0].getMappedValue((88, 108)))
                else:
                    rad.switchType(self.radioFM, self.radioAM, self.knobs[0].getMappedValue((55, 160)))

            volume_value = self.knobs[2].getMappedValue((0, 100))

            if self.is_fm == 1:
                if self.knobs[0].getMappedValue((88, 108)) != self.prev_fm_value:
                    self.printValues(self.knobs[0].getMappedValue((88, 108)), volume_value)
                    self.radioFM.changeStation(self.knobs[0].getMappedValue((88, 108)))
                self.prev_fm_value = self.knobs[0].getMappedValue((88, 108))
            elif self.is_fm == 0:
                if self.knobs[0].getMappedValue((55, 160)) != self.prev_fm_value:
                    self.printValues(self.knobs[0].getMappedValue((55, 160)), volume_value)
                    self.radioAM.changeStation(self.knobs[0].getMappedValue((55, 160)))
                self.prev_fm_value = self.knobs[0].getMappedValue((55, 160))

            if volume_value != self.prev_volume_value:
                if self.is_fm == 1:
                    self.radioFM.changeVolume(round(self.knobs[2].getMappedValue((0, 100))))
                else:
                    self.radioAM.changeVolume(round(self.knobs[2].getMappedValue((0, 100))))
                self.prev_volume_value = volume_value

            pygame.display.flip()
            self.clock.tick(60)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handleMouseButtonDown(event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.handleMouseButtonUp()
            elif event.type == pygame.MOUSEMOTION:
                self.handleMouseMotion(event)

    def handleMouseButtonDown(self, event):
        for knob in self.knobs:
            if knob.rect.collidepoint(event.pos):
                knob.dragging = True
                knob.prev_mouse_x = event.pos[0]

        if self.antenna.rect.collidepoint(event.pos):
            self.antenna.dragging = True
            self.antenna.prev_mouse_x = event.pos[1]

    def handleMouseButtonUp(self):
        for knob in self.knobs:
            knob.dragging = False
        self.antenna.dragging = False

    def handleMouseMotion(self, event):
        for knob in self.knobs:
            knob.updateAngle(event.pos[0])
        self.antenna.updateAngle(-event.pos[1])

    def update(self):
        pass

    def draw(self):
        temp_surface = self.white_surface.copy()

        self.antenna.draw(temp_surface)
        temp_surface.blit(self.radio_image, (0, 200))
        for knob in self.knobs:
            knob.draw(temp_surface)
        if self.knobs[2].getMappedValue((0, 100)) >= 1:
            self.dot.draw(temp_surface)

        # Blit the temporary surface onto the screen
        self.screen.blit(temp_surface, (0, 0))

    def printValues(self, fm_value, volume_value):
        band = "FM" if self.is_fm else "AM"
        print(f"{band} Frequency: {fm_value}, Volume: {volume_value}")

if __name__ == "__main__":
    
    app = RadioApp()
    app.run()
