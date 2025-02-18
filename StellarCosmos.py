import pygame
import random


class Player(pygame.sprite.Sprite):
    def __init__(self, image, scale, x, y, hBound, speed):
        pygame.sprite.Sprite.__init__(self)
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hBound = hBound
        self.speed = speed
        self.fired = False
        self.maxProj = 5

    def update(self):
        keyStates = pygame.key.get_pressed()

        if keyStates[pygame.K_a]:
            self.rect.x -= self.speed
        if keyStates[pygame.K_d]:
            self.rect.x += self.speed
        if keyStates[pygame.K_SPACE] and len(playerProjectileSprites) < self.maxProj and not self.fired:
            proj = Projectile(playerProjImage, 0.2,
                              self.rect.center[0], self.rect.center[1], 0, -4)
            allSprites.add(proj)
            playerProjectileSprites.add(proj)
            self.fired = True
        elif not keyStates[pygame.K_SPACE]:
            self.fired = False

        # check right side bounds
        if self.rect.right >= self.hBound:
            self.rect.right = self.hBound
        # check left side bounds
        if self.rect.left <= 0:
            self.rect.left = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, scale, targetX, targetY, speed):
        pygame.sprite.Sprite.__init__(self)
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.initial_position = (random.randint(0, screenWidth), -50)
        self.rect.center = (self.initial_position[0], self.initial_position[1])
        self.speed = speed
        self.path_position = 0
        self.phase = "entry"  # "entry", "attack", "idle", or "return"
        self.target_position = (targetX, targetY)
        self.atHome = False
        self.entryControlPoint = (random.randint(
            0, screenWidth), screenHeight * 2/3)
        self.strafeReady = False
        self.fireFrequency = 1/5
        self.nextFirePosition = self.fireFrequency

    def update(self):
        if self.phase == "entry":
            self.SwoopToTargetPosition(self.entryControlPoint)
        elif self.phase == "attack":
            self.swoopAndStrafe()
        elif self.phase == "return":
            self.SwoopToTargetPosition((screenWidth/2, screenHeight/2))
        elif self.phase == "idle":
            pass

    def SwoopToTargetPosition(self, control):

        # Define the start, control, and end points for the Bézier curve
        start = (self.rect.x, self.rect.y)
        control = control
        end = self.target_position

        # Use a quadratic Bézier curve formula to calculate position
        t = self.path_position
        self.rect.x = (1 - t)**2 * start[0] + 2 * (1 - t) * \
            t * control[0] + t**2 * end[0]
        self.rect.y = (1 - t)**2 * start[1] + 2 * (1 - t) * \
            t * control[1] + t**2 * end[1]

        # Increment t to move further along the curve
        # Adjust this value to control entry speed
        self.path_position += self.speed * 0.001

        # Transition to attack phase once the enemy reaches its target position
        if self.path_position > 1:
            self.phase = "idle"
            self.path_position = 0  # Reset for the attack phase

    def swoop_towards_player(self, player_position):
        # Implementing Bézier curve for swooping dive
        if self.path_position <= 1:
            # Quadratic Bézier Curve: B(t) = (1 - t)^2 * P0 + 2 * (1 - t) * t * P1 + t^2 * P2

            start = self.initial_position
            control = (screenWidth/2, screenHeight * 2/3)
            end = self.target_position
            # Use a quadratic Bézier curve formula to calculate position
            t = self.path_position
            self.rect.x = (1 - t)**2 * start[0] + 2 * (1 - t) * \
                t * control[0] + t**2 * end[0]
            self.rect.y = (1 - t)**2 * start[1] + 2 * (1 - t) * \
                t * control[1] + t**2 * end[1]

        # Move along the curve by incrementing t
            self.path_position += 0.02
        else:
            # If dive misses (i.e., after completing curve), switch to return phase
            self.phase = "return"

    def swoopAndStrafe(self):
        if not self.strafeReady:
            # Define the start, control, and end points for the Bézier curve
            start = self.target_position
            control = (self.target_position[0],
                       self.target_position[1]-screenHeight/4)
            end = (0, screenHeight-200)

            # Use a quadratic Bézier curve formula to calculate position
            t = self.path_position
            self.rect.x = (1 - t)**2 * start[0] + 2 * (1 - t) * \
                t * control[0] + t**2 * end[0]
            self.rect.y = (1 - t)**2 * start[1] + 2 * (1 - t) * \
                t * control[1] + t**2 * end[1]

            # Increment t to move further along the curve
            # Adjust this value to control entry speed
            self.path_position += self.speed * 0.0025

           # Transition to attack phase once the enemy reaches its target position
            if self.path_position > 1:
                self.path_position = 0  # Reset for the attack phase
                self.strafeReady = True
        else:
            # Define the start, control, and end points for the Bézier curve
            start = (self.rect.x, self.rect.y)
            control = (self.rect.x, self.rect.y-5)
            end = (screenWidth-60, screenHeight-200)

            # Use a quadratic Bézier curve formula to calculate position
            t = self.path_position
            self.rect.x = (1 - t)**2 * start[0] + 2 * (1 - t) * \
                t * control[0] + t**2 * end[0]
            self.rect.y = (1 - t)**2 * start[1] + 2 * (1 - t) * \
                t * control[1] + t**2 * end[1]

            # Increment t to move further along the curve
            # Adjust this value to control entry speed
            self.path_position += self.speed * 0.0005

            if self.path_position >= self.nextFirePosition * 0.3:
                self.nextFirePosition += self.fireFrequency
                self.FireProjectile()

           # Transition to attack phase once the enemy reaches its target position
            if self.path_position > .3:
                self.path_position = 0  # Reset for the attack phase
                self.strafeReady = False
                self.nextFirePosition = self.fireFrequency
                self.phase = "return"

    def FireProjectile(self):
        proj = Projectile(enemyProjImage, 0.3,
                          self.rect.center[0], self.rect.center[1], 0, 4)
        allSprites.add(proj)
        enemyProjectileSprites.add(proj)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, scale, x, y, xVelocity, yVelocity):
        pygame.sprite.Sprite.__init__(self)
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.xVelocity = xVelocity
        self.yVelocity = yVelocity

    def update(self):
        self.rect.x += self.xVelocity
        self.rect.y += self.yVelocity

        if self.rect.right < 0 or self.rect.left > screenWidth or self.rect.top > screenHeight or self.rect.bottom < 0:
            self.kill()


class Collectible(pygame.sprite.Sprite):
    pass


class Button(pygame.sprite.Sprite):
    pass


def draw_text(color, text, font, size, x, y, surface):
    font_name = pygame.font.match_font(font)
    Font = pygame.font.Font(font_name, size)
    text_surface = Font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)


# Game Variables
screenWidth = 700
screenHeight = 600

# Pygame setup
pygame.init()
clock = pygame.time.Clock()  # The clock tracks how fast the game is running.
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Stellar Cosmos")


# load images
playerImage = pygame.image.load("_images/SCPlayer.png")
enemy1Image = pygame.image.load("_images/SCEnemy1.png")
enemy2Image = pygame.image.load("_images/SCEnemy2.png")
enemy3Image = pygame.image.load("_images/SCEnemy3.png")
enemy4Image = pygame.image.load("_images/SCEnemy4.png")
playerProjImage = pygame.image.load("_images/proj2.png")
enemyProjImage = pygame.image.load("_images/proj1.png")
temp = pygame.image.load("_images/StarryBackground.jpg").convert()
tempW = temp.get_width()
tempH = temp.get_height()
background = pygame.transform.scale(
    temp, (tempW * (screenWidth/tempW), tempH*(screenHeight/tempH)))

# Create initial objects
player = Player(playerImage, 0.25, screenWidth/2,
                screenHeight-60, screenWidth, 5)

# Create sprite groups
allSprites = pygame.sprite.Group()
enemySprites = pygame.sprite.Group()
playerProjectileSprites = pygame.sprite.Group()
enemyProjectileSprites = pygame.sprite.Group()
collectibleSprites = pygame.sprite.Group()

# Add objects to sprite groups
allSprites.add(player)

# Global variables
scroll_y = 0  # scroll pos
backgroundScrollSpeed = 3.5
maxSwoopingEnemies = 1
currentSwoopingEnemies = 0
score = 0
reset = 0
rfReset = 0
enemySwoopTimer = 5
randomFireTimer = 3
gameState = "running"

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
lightBlue = (121, 196, 242)

# Enemies
for i in range(9):
    enemy = Enemy(enemy1Image, 0.15, i*70 + 35, 50, 5)
    enemySprites.add(enemy)
    allSprites.add(enemy)
for i in range(9):
    enemy = Enemy(enemy2Image, 0.15, i*70 + 35, 120, 5)
    enemySprites.add(enemy)
    allSprites.add(enemy)

# GAME LOOP
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    if gameState == "gameover":
        screen.fill(black)
        draw_text(white, "Score: " + str(score),
                  'agencyfb', 30, screenWidth/2, screenHeight/2, screen)
    else:
        # Collision detection player proj -> enemy
        for proj in playerProjectileSprites:
            for enemy in enemySprites:
                if pygame.sprite.collide_rect(proj, enemy):
                    enemy.kill()
                    proj.kill()
                    score += 1

        # Collision detection enemy proj -> player
        for proj in enemyProjectileSprites:
            if pygame.sprite.collide_rect(proj, player):
                gameState = "gameover"

        # swoop enemies
        if currentSwoopingEnemies < maxSwoopingEnemies:
            # get random enemy at "home"
            # increment currentSE
            # swoop

            for enemy in enemySprites:
                if enemy.atHome:
                    pass

        # Timer for enemy swoop
        milliseconds = pygame.time.get_ticks() - reset
        if milliseconds >= enemySwoopTimer*1000:
            reset += enemySwoopTimer*1000
            # set enemy to swoop attack player
            randomEnemy = random.choice(enemySprites.sprites())
            randomEnemy.phase = "attack"

        # Timer for random fire
        milliseconds = pygame.time.get_ticks() - rfReset
        if milliseconds >= randomFireTimer*1000:
            rfReset += randomFireTimer*1000
            # set enemy to swoop attack player
            randomEnemy = random.choice(enemySprites.sprites())
            if randomEnemy.phase == "idle":
                randomEnemy.FireProjectile()

        if pygame.key.get_pressed()[pygame.K_l]:
            random.choice(enemySprites.sprites()).phase = "attack"

        # BACKGROUND
        # Scroll the background down
        scroll_y += backgroundScrollSpeed  # Adjust speed as needed
        if scroll_y >= background.get_height():
            scroll_y = 0  # Reset scroll position when the image has fully scrolled
        # Draw background
        screen.blit(background, (0, scroll_y - background.get_height()))
        screen.blit(background, (0, scroll_y))

        pygame.draw.rect(screen, lightBlue, (0, 0, screenWidth, 40))
        draw_text((0, 0, 0), "Score: " + str(score),
                  'agencyfb', 30, screenWidth/2, 20, screen)

        # Update sprites
        allSprites.update()

        # Draw sprites
        allSprites.draw(screen)

    pygame.display.update()
    clock.tick(60)
