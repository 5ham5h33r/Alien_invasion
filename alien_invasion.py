import sys
from time import sleep

import pygame

from settings import Settings
from ship import Ship
from alien import Alien
from bullet import Bullet
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """Overall class to manage the game assets and behaviour"""

    def __init__(self):
        """Initialize tha game and create game resources"""

        pygame.init()
        self.settings = Settings()

        # self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # Instance to store game statistics
        self.stats = GameStats(self)

        # Instance to display scoreboard
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Making play button
        self.play_button = Button(self, "PLAY!")

    def run_game(self):
        """Start the main loop for tha game"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self.bullets.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks PLAY!"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self._start_game()


    def _start_game(self):
        # Reset the game stats
        self.settings.initialize_dynamic_settings() #Reset game settings
        pygame.mouse.set_visible(False)             #Hide mouse cursor

        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # Getting rid of any remaining aliens and bullets
        self.aliens.empty()
        self.bullets.empty()

        # Create a new fleet and center the ship
        self._create_fleet()
        self.ship.center_ship()

    def _write_highscore(self):
        with open("scores\highscore.txt", 'w') as file:
            file.write(str(self.stats.high_score))
        sys.exit()

    def _check_events(self):
        # Watch for kb/m events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._write_highscore()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            # Set ship move right flag to true
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._write_highscore()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        if not self.stats.game_active:
            if event.key == pygame.K_p:
                self._start_game()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _ship_hit(self):
        """Respond to ship being hit by alien"""
        if self.stats.ships_left > 0:

            # Decrement ships left and update scoreboard
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Getting rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Creating a new fleet and center ship
            self._create_fleet()
            self.ship.center_ship()

            # Pause
            sleep(0.5)

        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Create the fleet of alien"""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien nis equal to width of one alien
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determining number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Creating complete alien fleet row-wise
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)



    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _update_screen(self):
        # Redraw the screen during each pass through the loop

        # Working code
        # self.screen.fill(self.settings.bg_color)
        # self.ship.blitme()
        # for bullet in self.bullets.sprites():
        #     bullet.draw_bullet()
        # self.aliens.draw(self.screen)


        # Experimental
        self.screen.fill(self.settings.bg_color)
        if self.stats.game_active:
            self.ship.blitme()
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            self.aliens.draw(self.screen)

            # Draw scoreboard
            self.sb.show_score()
        # Experimental ends here

        # Drawing play button if game is inactive
        if not self.stats.game_active:
            self.play_button.draw_bullet()

        pygame.display.flip()

    def _update_bullets(self):
        # Getting rid of bullets running off-screen
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()



    def _check_bullet_alien_collisions(self):
        # Check for any bullets that have hit aliens
        # If hit, destroy bullet and alien ship
        collisions = pygame.sprite.groupcollide(self.bullets,
                                                self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        Check if fleet is at edge
        Correspondingly update the positions of all aliens in fleet
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien colliding with ship
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            #print("SHIP HAS TAKEN A HIT!")
            self._ship_hit()

        # Looking for aliens hitting bottom of screen
        self._check_aliens_bottom()

    def _change_fleet_direction(self):
        """Drop entire fleet and change its direction (Left/Right movement)"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_fleet_edges(self):
        """Checking if aliens have reached an edge and responding"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #Treating same as ship being hit (life lost)
                self._ship_hit()
                break

if __name__ == '__main__':
    # Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()
