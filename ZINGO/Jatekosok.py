import pygame as pg
import sys
from tkinter import filedialog
import tkinter as tk

class Jatekos:
    def __init__(self, nev, kep=None, pontszam=0):
        self.nev = nev
        self.kep = kep
        self.pontszam = pontszam

def keretbe_helyez(kep, cel_meret):
    if kep:
        kep_meret = kep.get_size()
        uj_kep = pg.transform.smoothscale(kep, cel_meret)
        kep_keret = pg.Surface(cel_meret, pg.SRCALPHA)

        kep_keret.fill((255, 255, 255, 0))  # Átlátszó háttér

        # Kör rajzolása a kép helyett
        kor_atmero = min(cel_meret)
        pg.draw.circle(kep_keret, (255, 255, 255, 128), (cel_meret[0] // 2, cel_meret[1] // 2), kor_atmero // 2)

        # Kép középre igazítása a kereten belül
        kep_poz = ((cel_meret[0] - uj_kep.get_width()) // 2, (cel_meret[1] - uj_kep.get_height()) // 2)
        kep_keret.blit(uj_kep, kep_poz)

        return kep_keret
    else:
        return None

def nev_bekerese(screen, font):
    pg.display.set_caption('Nevek megadása')
    input_text = ''
    clock = pg.time.Clock()

    while True:
        screen.fill((255, 255, 255))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return input_text
                elif event.key == pg.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        text_surface = font.render('Kérem a játékos nevét:', True, (0, 0, 0))
        screen.blit(text_surface, (50, 50))

        text_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(text_surface, (50, 100))

        pg.display.flip()
        clock.tick(30)

def fajl_betolto_dialog():
    root = tk.Tk()
    root.withdraw()
    fajl_nev = filedialog.askopenfilename()
    root.destroy()
    return fajl_nev

pg.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (255, 255, 255)
FONT_COLOR = (0, 0, 0)
FONT_SIZE = 32

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Játékosok')

jatekosok = []

font = pg.font.SysFont(None, FONT_SIZE)

# Maximum 5 játékos nevének bekérése
i = 0
while i < 5:
    nev = nev_bekerese(screen, font)
    if not nev:
        break

    kep_file = fajl_betolto_dialog()
    if kep_file:
        kep = pg.image.load(kep_file).convert()
    else:
        kep = None
    jatekosok.append(Jatekos(nev, kep))
    i += 1

# Háttérkép létrehozása
hatter = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
hatter.fill(BACKGROUND_COLOR)

# Játékosok kirajzolása
y = 50
for jatekos in jatekosok:
    nev_text = font.render(jatekos.nev, True, FONT_COLOR)
    hatter.blit(nev_text, (50, y))

    kep_keret = keretbe_helyez(jatekos.kep, (150, 150))
    if kep_keret:
        kep_keret_meret = kep_keret.get_size()
        kep_keret_poz = (200 + (150 - kep_keret_meret[0]) // 2, y + (150 - kep_keret_meret[1]) // 2)
        hatter.blit(kep_keret, kep_keret_poz)

    pontszam_text = font.render(f"Pontszám: {jatekos.pontszam}", True, FONT_COLOR)
    hatter.blit(pontszam_text, (400, y))

    y += 200




screen.blit(hatter, (0, 0))

# Képernyő frissítése
pg.display.flip()

# Fő eseményhurok
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
