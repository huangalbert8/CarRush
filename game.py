import pygame
import random
import os
import time
import neat

pygame.font.init()  # init font
WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
PAUSE_FONT = pygame.font.SysFont("comicsans", 30)
END_FONT = pygame.font.SysFont("comicsans", 100)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Car Game")

TRACK_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs","tracks.jpg")).convert_alpha(), (600, 800))
CAR_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs","car1.png")).convert_alpha(), (50,100))
BLOCK_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("imgs","Block1.png")).convert_alpha(), (50,100)),pygame.transform.scale(pygame.image.load(os.path.join("imgs","block2.png")).convert_alpha(), (50,100)), pygame.transform.scale(pygame.image.load(os.path.join("imgs","block3.png")).convert_alpha(), (50,100))]
EXPLOSION_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs","explosion.png")).convert_alpha(), (100,150))
TITLE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs","title.png")).convert_alpha(), (500,400))

gen = 0
pause = False


class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.IMG = CAR_IMG
        self.explode_img = EXPLOSION_IMG
        self.collided = False

    def slide_left(self):
        k = 0
        if self.x > 203:
            while(k < 75):
                self.x = self.x - 5
                k = k+5
        # else:
        #     self.collided = True

    def slide_right(self):
        if self.x < 347:
            for x in range(75):
                self.x = self.x + 1
        # else:
        #     self.collided = True

    def move(self):
        if 272 <= self.x <= 278:
            self.x = random.randint(273,277)
        elif 347 <= self.x <= 353:
            self.x = random.randint(348,352)
        elif 197 <= self.x <= 203:
            self.x = random.randint(198, 202)

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

    def explode(self, win):
        win.blit(self.explode_img, (self.x - 25, self.y - 25))
        pygame.display.update()


class Track:
    """
       Represents the moving floor of the game
       """
    HEIGHT = TRACK_IMG.get_height()
    IMG = TRACK_IMG

    def __init__(self, x):
        self.x = x
        self.y1 = 0
        self.y2 = self.HEIGHT
        self.vel = 40

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.y1 += self.vel
        self.y2 += self.vel
        if self.y1 > self.HEIGHT:
            self.y1 = self.y2 - self.HEIGHT

        if self.y2 > self.HEIGHT:
            self.y2 = self.y1 - self.HEIGHT

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x, self.y1))
        win.blit(self.IMG, (self.x, self.y2))


class Block:
    def __init__(self):
        self.x = 0
        self.y = -50
        self.IMG = random.choice(BLOCK_IMGS)
        self.passed = False
        self.vel = 20
        self.set_lane()

    def set_lane(self):
        lane = random.randint(0,2)
        self.x = 200 + (lane*75)
        #self.x = 275

    def move(self):
        self.y += self.vel

    def draw(self,win):
        win.blit(self.IMG, (self.x, self.y))

    def collide(self, car):
        car_mask = car.get_mask()
        block_mask = pygame.mask.from_surface(self.IMG)
        offset = (self.x - car.x, self.y - round(car.y))
        point = car_mask.overlap(block_mask,offset)
        if point:
            return True
        return False


class Button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False


def draw_window(win, track, car, blocks, exploded, score):
    track.draw(win)
    car.draw(win)
    if(exploded):
        car.explode(win)
    text = STAT_FONT.render("Score: "+str(score), True, (0, 0, 0))
    p = PAUSE_FONT.render("Press P to Pause", True, (0,0,0))
    win.blit(text, (10, 10))
    win.blit(p, (10, 50))
    for block in blocks:
        block.draw(win)
    pygame.display.update()


def unpause():
    global pause
    pause = False


def paused():
    global pause
    clock = pygame.time.Clock()
    while pause:
        playButton = Button((0, 255, 0), 50, 550, 200, 100, 'Resume')
        quitButton = Button((255, 0, 0), 350, 550, 200, 100, 'Leave')
        playButton.draw(WIN)
        quitButton.draw(WIN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            largeText = pygame.font.SysFont("comicsansms", 115)
            TextSurf = largeText.render('Paused', False, (0, 0, 0))
            TextRect = TextSurf.get_rect()
            TextRect.center = ((WIN_WIDTH / 2), (WIN_HEIGHT / 2))
            WIN.blit(TextSurf, TextRect)
            pos = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_p]:
                unpause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if playButton.isOver(pos):
                    unpause()
                if quitButton.isOver(pos):
                    startScreen()

        pygame.display.update()
        clock.tick(15)


def play():
    global pause
    clock = pygame.time.Clock()
    track = Track(0)
    car = Car(275, 650)
    blocks = [Block()]
    run = True
    score = 0
    distance = 800
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                car.slide_left()
            if keys[pygame.K_RIGHT]:
                car.slide_right()
            if keys[pygame.K_p]:
                pause = True
                paused()
        add_block = False
        rem = []
        for block in blocks:
            block.move()
            if block.collide(car) or car.collided:
                run = False
            if not block.passed and block.y > distance:
                block.passed = True
                add_block = True
            if block.y > car.y + 150:
                rem.append(block)
                score+=1
                if score%10 == 0 and not score == 0 and score <= 60:
                    distance -= 100
                    track.vel += 2.5
        if add_block:
            blocks.append(Block())
        for r in rem:
            blocks.remove(r)
        track.move()
        car.move()
        draw_window(WIN, track, car, blocks, not run, score)

def draw_sim_window(win, cars, blocks, score, track, gen):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    track.draw(WIN)
    if gen == 0:
        gen = 1

    for block in blocks:
        block.draw(win)

    for car in cars:
        car.draw(win)
    # score
    score_label = STAT_FONT.render("Score: " + str(score), False ,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # pause
    score_label = PAUSE_FONT.render("Press P to Pause", False, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 50))


    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1), False,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(cars)),False,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()

def eval_genomes(genomes, config): # doesnt work
    global WIN, gen, pause
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    cars = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        cars.append(Car(275,650))
        ge.append(genome)
    blocks = [Block()]
    track = Track(0)
    score = 0

    clock = pygame.time.Clock()

    run = True
    distance = 800
    while run and len(cars) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
            keys = pygame.key.get_pressed()
            if keys[pygame.K_p]:
                pause = True
                paused()

        block_ind = 0
        if len(blocks) > 0:
            if len(blocks) > 1 and cars[0].y < blocks[0].y + 100:  # determine whether to use the first or second
                block_ind = 1  # pipe on the screen for neural network input

        for x, car in enumerate(cars):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            car.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[cars.index(car)].activate(
                (car.x, (car.x-blocks[block_ind].x), blocks[block_ind].y))

            if output[
                0] > 0:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                car.slide_left()

            elif output[0] < 0:
                car.slide_right()


        track.move()
        rem = []
        add_block = False
        for block in blocks:
            block.move()
            # check for collision
            for car in cars:
                if block.collide(car) or car.collided:
                    ge[cars.index(car)].fitness -= 1
                    nets.pop(cars.index(car))
                    ge.pop(cars.index(car))
                    cars.pop(cars.index(car))

            if block.y > car.y + 150:
                rem.append(block)
                score+=1
                if score%10 == 0 and not score == 0 and score <= 60:
                    distance -= 100
            if not block.passed and block.y > distance:
                block.passed = True
                add_block = True

        if add_block:
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 10
            blocks.append(Block())

        for r in rem:
            blocks.remove(r)

        draw_sim_window(WIN, cars, blocks, score, track, gen)


def run_sim(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))
    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 20)
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


def startScreen():
    run = True
    while run:
        WIN.blit(TRACK_IMG, (0, 0))
        car = Car(275, 650)
        car.draw(WIN)
        greenbutton = Button((0, 255, 0), 50, 550, 200, 100, 'Simulate')
        bluebutton = Button((255, 0, 0), 350, 550, 200, 100, 'Play')

        text = END_FONT.render("CAR RUSH", False, (0,0,0))
        WIN.blit(TITLE_IMG, (80,00))
        WIN.blit(text, (125, 175))
        greenbutton.draw(WIN)
        bluebutton.draw(WIN)

        pygame.display.update()

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                play()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if greenbutton.isOver(pos):
                    local_dir = os.path.dirname(__file__)
                    config_path = os.path.join(local_dir, 'config-feedforward.txt')
                    run_sim(config_path)
                if bluebutton.isOver(pos):
                    play()


if __name__ == '__main__':
    startScreen()
