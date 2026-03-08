import pygame

def run(screen):

    font = pygame.font.SysFont("arial", 40)

    text = font.render("LEVEL 1 PLACEHOLDER", True, (255,255,255))

    screen.blit(text, (450,350))