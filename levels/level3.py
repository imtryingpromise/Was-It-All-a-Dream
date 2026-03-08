import pygame

def run(screen):

    font = pygame.font.SysFont("arial", 40)

    text = font.render("LEVEL 3 PLACEHOLDER", True, (255,255,255))

    screen.blit(text, (450,350))