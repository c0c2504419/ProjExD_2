import math
import os
import pygame as pg
import random
import sys
import time


WIDTH, HEIGHT = 1100, 650

DELTA = {
        pg.K_UP:(0,-5),
        pg.K_DOWN:(0, +5),
        pg.K_LEFT:(-5,0),
        pg.K_RIGHT:(+5,0),
}  # 方向キー入力の辞書
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct:pg.Rect) -> tuple[bool,bool]:
    """
    引数で与えられたRectが画面内科画面外貨を判定する関数
    引数：こうかとんRectまたはばくだんRect
    戻り値：横方向判定結果，縦方向判定結果
    画面内ならTrue,画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH< obj_rct.right:  # 横方向判定
        yoko = False
    if obj_rct.top < 0 or HEIGHT< obj_rct.bottom:  # 縦方向判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    画面をブラックアウトし、泣いているこうかとん画像とゲームオーバーの文字列を5秒間表示する関数。
    """
    black_img = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(black_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    black_img.set_alpha(150)  # Surfaceの透明度変更

    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    cry_rct1 = cry_img.get_rect()
    cry_rct1.center = WIDTH//2 - 200, HEIGHT//2  # こうかとん1匹目
    cry_rct2 = cry_img.get_rect()
    cry_rct2.center = WIDTH//2 + 200, HEIGHT//2  # こうかとん2匹目

    fonto= pg.font.Font(None, 80)
    txt= fonto.render("Game Over",True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH//2, HEIGHT//2  

    screen.blit(black_img, [0, 0])  # ブラックアウト
    screen.blit(txt, txt_rct)  # 文字表示
    screen.blit(cry_img, cry_rct1)  # こうかとん1匹目表示
    screen.blit(cry_img, cry_rct2)  # こうかとん2匹目表示
    pg.display.update()
    time.sleep(5)  # 5秒間表示


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階程度の大きさを変えた爆弾Surfaceのリストと加速度のリストを準備する。
    戻り値：爆弾Surfaceのリスト, 加速度のリスト
    """
    bb_accs = [a for a in range(1, 11)]  # 加速度のリスト
    bb_imgs = []  # 爆弾Surfaceのリスト
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))  # 爆弾の背景透明化
        bb_imgs.append(bb_img)      
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルと対応する画像Surfaceの辞書を返す関数
    戻り値：{(横移動量, 縦移動量): Surface}
    """
    kk_img0 = pg.image.load("fig/3.png")  # こうかとんの画像
    kk_img_r = pg.transform.flip(kk_img0, True, False)  # 画像を左右または上下に反転させる
    
    return {
        ( 0,  0): pg.transform.rotozoom(kk_img_r, 0, 0.9),   # 静止（右向き）
        (+5,  0): pg.transform.rotozoom(kk_img_r, 0, 0.9),   # 右
        (+5, -5): pg.transform.rotozoom(kk_img_r, 45, 0.9),  # 右上
        ( 0, -5): pg.transform.rotozoom(kk_img_r, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(kk_img0, -45, 0.9),  # 左上
        (-5,  0): pg.transform.rotozoom(kk_img0, 0, 0.9),    # 左
        (-5, +5): pg.transform.rotozoom(kk_img0, 45, 0.9),   # 左下
        ( 0, +5): pg.transform.rotozoom(kk_img_r, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(kk_img_r, -45, 0.9),  # 右下
    }


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float])-> tuple[float, float]:
    """
    爆弾から見て,こうかとんRectがある方向,すなわち移動すべき方向をベクトル(vx, vy)を返す関数を実装
    org（爆弾を想定）から見てdst（こうかとんを想定）の座標ベクトル間の差ベクトルを求め、そのノルムが√50になるように正規化する。
    orgとdstの距離が300未満の場合は慣性としてcurrent_xyを維持する。
    """
    dx = dst.centerx - org.centerx  # 差ベクトルを求めるためcnterx使用
    dy = dst.centery - org.centery  # 上同様にcenteryを使用
    
    dist = math.sqrt(dx**2 + dy**2)  # 爆弾とこうかとんの間の直線距離(斜辺)

    if dist < 300:
        return current_xy
    
    norm = math.sqrt(50)
    vx = (dx / dist) * norm  # 差ベクトルdx正規化
    vy = (dy / dist) * norm  # 差ベクトルdy正規化
    
    return vx, vy


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)    
    kk_imgs = get_kk_imgs()  # こうかとんの方向変える関数に入れる
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img= pg.Surface((20, 20))  # 爆弾用の空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 爆弾の円を描く
    bb_img.set_colorkey((0, 0, 0))  # 黒い部分を透過
    bb_rct = bb_img.get_rect()  # 爆弾rectを取得

    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾変化の関数に入れる
    vx, vy = +5, +5  # 爆弾の速度
    bb_rct.center = random.randint(0, WIDTH),random.randint(0, HEIGHT)  # 爆弾の初期座標の設定

    clock = pg.time.Clock()
    tmr = 0

    while True:

        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)  # 画面ブラックアウト,こうかとんとGame Over表示
            return
 
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for key, mv in DELTA.items():  # 歩行キー辞書から持ってくる
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
            if tuple(sum_mv) in kk_imgs:
                kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)  # こうかとん動く
        
        
        if check_bound(kk_rct) != (True, True): # 画面外だったら
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 画面から出て行かないようにする
        
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1  # 壁反射の処理

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))  #追従型爆弾の関数に入れる

        avx= vx * bb_accs[min(tmr//500, 9)]  # 加速したxの速度
        avy = vy * bb_accs[min(tmr//500, 9)]  # 加速したyの速度
        bb_img = bb_imgs[min(tmr//500, 9)]  # 爆弾を大きいものに変更
        bb_rct.width = bb_img.get_width()  # 大きさが変わった場合にwidth属性更新
        bb_rct.height = bb_img.get_height()  # 大きさが変わった場合にheight属性更新
        bb_rct.move_ip(avx, avy)  # 爆弾動かす      

        screen.blit(bg_img, [0, 0])
        screen.blit(kk_img, kk_rct)  
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
