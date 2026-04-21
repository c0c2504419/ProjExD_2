import os
import sys
import pygame as pg
import random
import time

WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct:pg.Rect) -> tuple[bool,bool]:
    """
    引数：こうかとんRectかばくだんRect
    戻り値：タプル（横方向判定結果，縦方向判定結果）
    画面内ならTrue，画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH< obj_rct.right: # 横方向判定
        yoko = False
    if obj_rct.top < 0 or HEIGHT< obj_rct.bottom: # 縦方向判定
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    black_img = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(black_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    black_img.set_alpha(150)

    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    cry_rct1 = cry_img.get_rect()
    cry_rct1.center = WIDTH//2 - 200, HEIGHT//2
    cry_rct2 = cry_img.get_rect()
    cry_rct2.center = WIDTH//2 + 200, HEIGHT//2

    fonto= pg.font.Font(None, 80)
    txt= fonto.render("Game Over",True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH//2, HEIGHT//2

    screen.blit(black_img, [0, 0])
    screen.blit(txt, txt_rct)
    screen.blit(cry_img, cry_rct1)
    screen.blit(cry_img, cry_rct2)
    pg.display.update()
    time.sleep(5)

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img= pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH),random.randint(0, HEIGHT)
    vx = +5
    vy = +5

    DELTA = {
        pg.K_UP:(0,-5),
        pg.K_DOWN:(0, +5),
        pg.K_LEFT:(-5,0),
        pg.K_RIGHT:(+5,0),
    }

    clock = pg.time.Clock()
    tmr = 0

    while True:

        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(vx,vy)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
