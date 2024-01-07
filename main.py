import pygame
import numpy as np
import sys


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
            rotation_factor = dx / 1000.0
            self.angle += 360 * rotation_factor
            self.angle = max(self.angle_limits['min'], min(self.angle, self.angle_limits['max']))
            self.prev_mouse_x = mouse_x

    def get_mapped_value(self, range_params):
        angle_range = self.angle_limits['max'] - self.angle_limits['min']
        mapped_value = ((self.angle - self.angle_limits['min']) / angle_range) * (range_params[1] - range_params[0]) + range_params[0]
        return max(range_params[0], min(range_params[1], round(mapped_value)))

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)


class RadioApp:
    def __init__(self):
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
            Knob("smallKnob.png", (842, 767), {'min': 0, 'max': 320}, start_angle=160, scale_factor=0.5),
            Knob("smallKnob.png", (978, 768), {'min': 25, 'max': 130}, start_angle=25, scale_factor=0.5)
        ]
        self.prev_fm_value = None
        self.prev_volume_value = None
        self.is_fm = True
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.dot = Dot("dot.png", (910, 802), scale_factor=0.5)
        self.antenna = Antenna("antenka.png", (900, 180), {'min': -85, 'max': -60}, start_angle=-85, scale_factor=0.5)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            if self.knobs[1].get_mapped_value((0, 100)) >= 50:
                self.is_fm = 0
            else:
                self.is_fm = 1
            frequencies = [knob.get_mapped_value((100, 10000)) for knob in self.knobs]
            volume_value = self.knobs[3].get_mapped_value((0, 100))
            if self.knobs[0].angle != self.prev_fm_value or volume_value != self.prev_volume_value:
                if self.is_fm == 1:
                    self.print_values(self.knobs[0].get_mapped_value((88, 108)), volume_value)
                else:
                    self.print_values(self.knobs[0].get_mapped_value((550, 1600)), volume_value)

                self.prev_volume_value = volume_value
                self.prev_fm_value = self.knobs[0].angle
            if self.knobs[3].get_mapped_value((0, 100)) >= 1:
                self.play_tone(frequencies[0], volume_value)
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
        if self.knobs[3].get_mapped_value((0, 100)) >= 1:
            self.dot.draw(temp_surface)

        # Blit the temporary surface onto the screen
        self.screen.blit(temp_surface, (0, 0))

    def print_values(self, fm_value, volume_value):
        band = "FM" if self.is_fm else "AM"
        print(f"{band} Frequency: {fm_value}, Volume: {volume_value}")

    def play_tone(self, frequency, volume):
        sample_rate = 48000
        duration = 0.01
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        tone = volume * np.sin(2 * np.pi * frequency * t) * 10
        tone_pcm = np.column_stack((tone, tone)).astype(np.int16)
        sound = pygame.sndarray.make_sound(tone_pcm)
        sound.set_volume(1)
        sound.play()

if __name__ == "__main__":
    app = RadioApp()
    app.run()