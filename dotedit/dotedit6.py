#!/usr/bin/env python3
#coding: utf-8
""" dotedit.py """
import sys                          # 終了用
import os                           # ファイル保存、読み込み用
import pygame
from pygame.locals import *

WINDOW_RECT = Rect(0, 0, 987, 631)                  # ウィンドウのサイズ
FPS = 20                                            # ゲームのFPS

# ユーザーイベント
USEREVENT_MENU = pygame.USEREVENT                   # メニューボタン
USEREVENT_ALLUPDATE = pygame.USEREVENT + 1          # 全更新

# 線とか背景とかの色
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_SILVER = (192, 192, 192)
COLOR_WHITE = (255, 255, 255)

# メッセージボックスのタイプ
MSGBOX_TYPE_OK = 1
MSGBOX_TYPE_YESNO = 2
MSGBOX_TYPE_INPUT = 3

# パレットの色(そのうち設定ファイルとかから取得するようになるかも？)
PALETTE = {
    "black" : (0, 0, 0), "navy" : (0, 0, 128), "blue" : (0, 0, 255),
    "green" : (0, 128, 0), "teal" : (0, 128, 128), "lime" : (0, 255, 0),
    "aqua" : (0, 255, 255), "maroon" : (128, 0, 0), "purple" : (128, 0, 128),
    "olive" : (128, 128, 0), "gray" : (128, 128, 128), "silver" : (192, 192, 192),
    "red" : (255, 0, 0), "fuchsia" : (255, 0, 255), "yellow" : (255, 255, 0),
    "white" : (255, 255, 255)}

class SubScreen:
    """ サブスクリーン\n
    サブスクリーンの基本クラス """
    def __init__(self, name, rect, mainscreen):
        self.name = name                            # サブスクリーンの画面名
        self.rect = rect                            # サブスクリーンのrect
        self.mainscreen = mainscreen                # メイン画面の参照
        self.screen = pygame.Surface(rect.size)     # サブスクリーンのSurfaceオブジェクト
        self.screenlevel = 0                        # サブスクリーンの重なる順番
                                                    #   小さいほど下になる
        self.visible = True                         # サブスクリーンを表示するか？
        self.lock = False                           # サブスクリーンをロックするか？
        self.updateflg = False                      # サブスクリーンが更新されたか？
    def update(self):
        """ サブスクリーンの更新 """
        self.updateflg = True
    def mouse_button_down(self, pos, button):
        """ ボタンが押されたときの処理 """
    def mouse_motion(self, pos, ref, buttons):
        """ マウスが移動したときの処理 """
    def draw(self):
        """ サブスクリーンの描画 """
        self.screen.fill(COLOR_WHITE)
        pygame.draw.rect(self.screen, COLOR_BLACK, (0, 0, self.rect.width, self.rect.height), 6)
        self.mainscreen.blit(self.screen, self.rect)

class SubScreenGroup:
    """ サブスクリーンクラスをまとめて管理する """
    def __init__(self, mainscreen):
        self.sub_screens = []               # サブスクリーンをリストで管理
        self.mainscreen = mainscreen        # メインスクリーンにアクセスできるように

    def append(self, subscreen):
        """ サブスクリーンオブジェクトを追加 """
        self.sub_screens.append(subscreen)

    def get_subscreen(self, name):
        """ サブスクリーンの取得 """
        for subscreen in self.sub_screens:
            if subscreen.name == name:
                return subscreen
        return None

    def get_subscreen_in_pos(self, pos):
        """ posが指しているサブスクリーンの取得\n
        サブスクリーンの名前とサブスクリーン上のposを返す\n
        サブスクリーンが無いときはNone（文字）を返す\n
        重なっているときはscreenlevelで判定"""
        name = "None"
        sposx = 0
        sposy = 0
        screenlevel = -1
        for subscreen in self.sub_screens:
            if subscreen.visible\
                and subscreen.rect.collidepoint(pos)\
                and screenlevel < subscreen.screenlevel:
                # サブスクリーン上のposを計算
                name = subscreen.name
                sposx = pos[0] - subscreen.rect.x
                sposy = pos[1] - subscreen.rect.y
                screenlevel = subscreen.screenlevel

        return name, sposx, sposy

    def update(self):
        """ まとめて更新 """
        for subscreen in self.sub_screens:
            # 表示中かつロックされていない画面のみ更新
            if subscreen.visible and not subscreen.lock:
                subscreen.update()

        # エディタ画面の絵をビュー画面に反映
        if self.get_subscreen("EditScreen").updateflg:
            for i, cell in enumerate(self.get_subscreen("ViewScreen").blocks[\
                            self.get_subscreen("ViewScreen").select_block][1]):
                cell[0] = tuple(self.get_subscreen("EditScreen").cells[i][0])
            self.get_subscreen("ViewScreen").updateflg = True
        # ビュー画面の選択ブロックをエディタ画面に反映
        if self.get_subscreen("ViewScreen").updateflg:
            for i, cell in enumerate(self.get_subscreen("EditScreen").cells):
                cell[0] = tuple(self.get_subscreen("ViewScreen").blocks[\
                                self.get_subscreen("ViewScreen").select_block][1][i][0])
            self.get_subscreen("EditScreen").updateflg = True

        # パレット画面の色選択をエディタ画面に反映
        self.get_subscreen("EditScreen").drawcol1 = self.get_subscreen("PalettScreen").drawcol1
        self.get_subscreen("EditScreen").drawcol2 = self.get_subscreen("PalettScreen").drawcol2

    def event_handler(self, event):
        """ イベントハンドラー\n
        各サブスクリーンのイベント処理を実行する """
        # マウスがクリックされた時
        if event.type == MOUSEBUTTONDOWN:
            # クリックされたサブスクリーン名を取得
            name, posx, posy = self.get_subscreen_in_pos(event.pos)
            for subscreen in self.sub_screens:
                # 表示中かつロックされていない時だけ処理
                if subscreen.name == name and subscreen.visible and not subscreen.lock:
                    subscreen.mouse_button_down((posx, posy), event.button)
        # マウスが移動
        elif event.type == MOUSEMOTION:
            # クリックされたサブスクリーン名を取得
            name, posx, posy = self.get_subscreen_in_pos(event.pos)
            for subscreen in self.sub_screens:
                # 表示中かつロックされていない時だけ処理
                if subscreen.name == name and subscreen.visible and not subscreen.lock:
                    subscreen.mouse_motion((posx, posy), event.rel, event.buttons)
        # メニューバーの項目が押された時
        elif event.type == USEREVENT_MENU:
            if event.menu_type == "menu_clear":
                self.get_subscreen("EditScreen").cells_clear()
            elif event.menu_type == "menu_clearall":
                self.get_subscreen("EditScreen").cells_clear()
                self.get_subscreen("ViewScreen").blocks_clear()
            elif event.menu_type == "menu_save":
                self.get_subscreen("ViewScreen").save()
        # 全更新
        elif event.type == USEREVENT_ALLUPDATE:
            self.mainscreen.fill(COLOR_SILVER)
            for subscreen in self.sub_screens:
                subscreen.updateflg = True

    def draw(self):
        """ まとめて描画 """
        for subscreen in self.sub_screens:
            # 表示中かつ更新した画面のみ描画
            if subscreen.visible and subscreen.updateflg:
                subscreen.draw()
                subscreen.updateflg = False

class MenuBar(SubScreen):
    """ メニューバー """
    def __init__(self, name, rect, mainscreen):
        super().__init__(name, rect, mainscreen)
        self.font = pygame.font.SysFont(None, 20)
        self.celheight = 40                             # 1個のセルのサイズ
        self.celwidth = 55                              # 1個のセルのサイズ
        self.cells = []                                 # メニュー項目のリスト
                                                        #  (name, rect)
        # メニュー項目の追加
        cellrect = Rect(5, 5, self.celwidth, self.celheight)        # セーブボタン
        self.cells.append(("save", cellrect))
        cellrect = Rect(62, 5, self.celwidth, self.celheight)       # ロードボタン
        self.cells.append(("load", cellrect))
        cellrect = Rect(119, 5, self.celwidth, self.celheight)      # クリアボタン
        self.cells.append(("clear", cellrect))
        cellrect = Rect(176, 5, self.celwidth, self.celheight)      # クリアボタン
        self.cells.append(("clearall", cellrect))

    def mouse_button_down(self, pos, button):
        """ ボタンが押されたときの処理 """
        if button == BUTTON_LEFT:
            # ボタンが押された項目のイベントを発行
            for cell in self.cells:
                if cell[1].collidepoint(pos):
                    if cell[0] in ["save", "load", "clear", "clearall"]:
                        userevent = pygame.event.Event(USEREVENT_MENU,
                                                       {"menu_type": "menu_" + cell[0]})
                        pygame.event.post(userevent)

    def draw(self):
        """ メニューバーの描画 """
        self.screen.fill(COLOR_GRAY)
        # メニュー項目の描画
        for cell in self.cells:
            pygame.draw.rect(self.screen, COLOR_SILVER, cell[1])            # セルの色
            self.screen.blit(self.font.render(cell[0], True, COLOR_BLACK),  # 項目名
                             (cell[1].left + 5, 10))
            pygame.draw.rect(self.screen, COLOR_BLACK, cell[1], 1)            # セルの枠
            # マウスカーソルが項目上にある場合は、枠を描画する
            posx, posy = pygame.mouse.get_pos()
            if cell[1].collidepoint((posx - self.rect.left, posy - self.rect.top)):
                pygame.draw.rect(self.screen, COLOR_BLACK, cell[1], 3)          # セルの枠
        # メニューバーの枠
        pygame.draw.rect(self.screen, COLOR_BLACK,
                         (0, 0, self.rect.width, self.rect.height), 5)
        # メニューバーをメイン画面に描画
        self.mainscreen.blit(self.screen, self.rect)

class EditScreen(SubScreen):
    """ エディタ部の画面 """
    def __init__(self, name, rect, mainscreen):
        super().__init__(name, rect, mainscreen)
        self.editcelx = 32              # 32 x 32 のドット絵を書く
        self.editcely = 32
        self.cellsize = 15               # 1個のセルのサイズ
        self.drawcol1 = COLOR_BLACK     # クリックした場所に塗る色１
        self.drawcol2 = COLOR_WHITE     # クリックした場所に塗る色２
        self.cells = []                 # １ドット情報のリスト
                                        # １ドットは (color, rect)
        # 全セルのRectと色（白）を設定
        self.cells_clear()

    def mouse_button_down(self, pos, button):
        """ ボタンが押されたときの処理 """
        for cell in self.cells:
            # ボタンが押されたセルの色を変更
            if cell[1].collidepoint(pos):
                if button == BUTTON_LEFT:
                    cell[0] = self.drawcol1
                elif button == BUTTON_RIGHT:
                    cell[0] = self.drawcol2
                self.updateflg = True               # 更新フラグセット

    def mouse_motion(self, pos, ref, buttons):
        """ マウスが移動したときの処理 """
        for cell in self.cells:
            # ボタンが押されたセルの色を変更
            if cell[1].collidepoint(pos):
                if buttons[0]:
                    cell[0] = self.drawcol1
                    self.updateflg = True               # 更新フラグセット
                elif buttons[2]:
                    cell[0] = self.drawcol2
                    self.updateflg = True               # 更新フラグセット

    def update(self):
        """ サブスクリーンの更新 """

    def draw(self):
        """ エディタ部の描画 """
        self.screen.fill(COLOR_BLACK)

        # セルの描画
        for cell in self.cells:
            pygame.draw.rect(self.screen, cell[0], cell[1])                 # セルの色
            pygame.draw.rect(self.screen, COLOR_GRAY, cell[1], 1)           # セルの枠
        # 真ん中に線を引く
        pygame.draw.line(self.screen, COLOR_BLACK, (self.rect.centerx - self.rect.left, 0),
                         (self.rect.centerx - self.rect.left, self.rect.bottom), 2)
        pygame.draw.line(self.screen, COLOR_BLACK, (0, self.rect.centery - self.rect.top),
                         (self.rect.width, self.rect.centery - self.rect.top), 2)

        # エディタ部をメイン画面に描画
        self.mainscreen.blit(self.screen, self.rect)

    def cells_clear(self):
        """ 全セルのクリア """
        self.cells.clear()
        # 全セルのRectと色（白）を設定
        for i in range(self.editcelx):
            for j in range(self.editcely):
                cellrect = Rect(i * self.cellsize +3, j * self.cellsize + 3,
                                self.cellsize, self.cellsize)
                self.cells.append([COLOR_WHITE, cellrect])
        self.updateflg = True

class ViewScreen(SubScreen):
    """ 全体の画像を表示する画面 """
    def __init__(self, name, rect, mainscreen):
        super().__init__(name, rect, mainscreen)
        self.editcelx = 32              # エディタ画面のサイズ（32 x 32
        self.editcely = 32
        self.blockx = 5                 # エディタ画面何個分か
        self.blocky = 5
        self.cellsize = 3               # 1個のセルのサイズ
        self.blocks = []                # １ブロック情報のリスト
                                        # １ブロックは (color, rect)
        self.select_block = 0           # 選択中のブロック
        self.save_dir = os.path.dirname(__file__) + "/pictures/" # 保存場所
        self.save_filename = "newfile.png"   # 保存ファイル名
        self.blocks_clear()

    def mouse_button_down(self, pos, button):
        """ ボタンが押されたときの処理 """
        if button == BUTTON_LEFT:
            for i, block in enumerate(self.blocks):
                if block[0].collidepoint(pos):
                    self.select_block = i
                    self.updateflg = True

    def update(self):
        """ サブスクリーンの更新 """

    def draw(self):
        """ 全体の画像を表示する画面の描画 """
        self.screen.fill(COLOR_BLACK)

        # セルの描画
        for block in self.blocks:
            # ブロック内のセルの描画
            for cell in block[1]:
                pygame.draw.rect(self.screen, cell[0], cell[1])             # セルの色

            pygame.draw.rect(self.screen, COLOR_GRAY, block[0], 1)          # ブロックの枠

        pygame.draw.rect(self.screen, COLOR_BLACK,
                         self.blocks[self.select_block][0], 3)

        # 全体の画像を表示する画面をメイン画面に描画
        self.mainscreen.blit(self.screen, self.rect)

    def blocks_clear(self):
        """ ブロックのクリア """
        self.blocks.clear()
        cells = []
        for i in range(self.blockx):
            for j in range(self.blocky):
                blockrect = Rect(i * self.cellsize * self.editcelx + 3,
                                 j * self.cellsize * self.editcely + 3,
                                 self.cellsize * self.editcelx, self.cellsize * self.editcely)
                cells.clear()
                # 全セルのRectと色（白）を設定
                for k in range(self.editcelx):
                    for l in range(self.editcely):
                        cellrect = Rect(k * self.cellsize + blockrect.left,
                                        l * self.cellsize + blockrect.top,
                                        self.cellsize, self.cellsize)
                        cells.append([COLOR_WHITE, cellrect])

                self.blocks.append([blockrect, list(cells)])

    def save(self):
        """ 画像ファイルに保存する """
        msgs = []               # メッセージ用

        # 保存ファイル名入力
        msgs.append("save filename?")
        msgbox = MsgBox(MSGBOX_TYPE_INPUT, msgs, self.mainscreen,
                        os.path.splitext(self.save_filename)[0])
        if not msgbox.return_value:
            return
        else:
            self.save_filename = msgbox.return_value + ".png"

        # 保存フォルダの存在を確認
        if not os.path.isdir(self.save_dir):
            # 保存フォルダの作成
            os.mkdir(self.save_dir)
        # 保存ファイルの存在確認
        if os.path.isfile(self.save_dir + self.save_filename):
            # 上書き確認
            msgs.clear()
            msgs.append("overwrite " + self.save_filename + "?")
            msgbox = MsgBox(MSGBOX_TYPE_YESNO, msgs, self.mainscreen)
            if not msgbox.return_value:
                return

        savescreen = pygame.Surface((self.editcelx * self.blockx,
                                     self.editcely * self.blocky))
        # save用画面にblock情報を描画する
        for i, block in enumerate(self.blocks):
            for j, cell in enumerate(block[1]):
                # x座標の計算
                posx = i // self.blockx * self.editcelx + j // self.editcelx
                # y座標の計算
                posy = i % self.blocky * self.editcely + j % self.editcely
                savescreen.fill(cell[0], Rect(posx, posy, 1, 1))

        # save
        pygame.image.save(savescreen, self.save_dir + self.save_filename)

        # メッセージボックスを表示
        msgs.clear()
        msgs.append("Saved " + self.save_filename)
        MsgBox(MSGBOX_TYPE_OK, msgs, self.mainscreen)

class PalettScreen(SubScreen):
    """ パレットの画面 """
    def __init__(self, name, rect, mainscreen):
        super().__init__(name, rect, mainscreen)
        self.font = pygame.font.SysFont(None, 20)
        self.editcelx = 8              # 32 x 32 のドット絵を書く
        self.editcely = 2
        self.cellsize = 20              # 1個のセルのサイズ
        self.drawcol1 = COLOR_BLACK     # クリックした場所に塗る色１
        self.drawcol2 = COLOR_WHITE     # クリックした場所に塗る色２
        self.cells = []                 # 色情報のリスト
                                        # 1マスは (color, rect)

        # パレットの色の設定
        for i, col in enumerate(PALETTE.values()):
            cellrect = Rect(110 + (i % self.editcelx) * (self.cellsize + 2),
                            20 + (i // self.editcelx) * (self.cellsize + 2),
                            self.cellsize, self.cellsize)
            self.cells.append([col, cellrect])

    def mouse_button_down(self, pos, button):
        """ ボタンが押されたときの処理 """
        for cell in self.cells:
            # ボタンが押されたセルの色を変更
            if cell[1].collidepoint(pos):
                if button == BUTTON_LEFT:
                    self.drawcol1 = cell[0]
                elif button == BUTTON_RIGHT:
                    self.drawcol2 = cell[0]

    def draw(self):
        """ パレット画面の描画 """
        self.screen.fill(COLOR_GRAY)

        # 選択中の色表示
        self.screen.blit(self.font.render(" left      right", True, COLOR_BLACK), (15, 5))
        pygame.draw.rect(self.screen, self.drawcol1, (10, 20, 42, 42))
        pygame.draw.rect(self.screen, self.drawcol2, (55, 20, 42, 42))

        # パレットの表示
        for cell in self.cells:
            pygame.draw.rect(self.screen, cell[0], cell[1])

        # パレット画面の枠
        pygame.draw.rect(self.screen, COLOR_BLACK,
                         (0, 0, self.rect.width, self.rect.height), 5)

        # パレット画面をメイン画面に描画
        self.mainscreen.blit(self.screen, self.rect)

class MsgBox():
    """ メッセージ表示用画面 画面中央にメッセージを表示する画面
        この画面は個別に呼び出される """
    def __init__(self, msgbox_type, msgs, mainscreen, value=None):
        self.mainscreen = mainscreen
        self.rect = Rect(0, 0, 300, 150)
        self.rect.center = WINDOW_RECT.center       # メッセージボックスはメイン画面中央に配置
        self.screen = pygame.Surface(self.rect.size)# サブスクリーンのSurfaceオブジェクト
        self.font = pygame.font.SysFont(None, 30)
        self.msgs = msgs
        self.cells = []                             # ボタンのリスト
        self.msgbox_type = msgbox_type              # メッセージボックスのタイプ
        self.return_value = value                   # メッセージボックスの戻り値

        # メッセージボックスの要素の追加
        if self.msgbox_type == MSGBOX_TYPE_OK:
            self.cells.append(["O K", Rect(122, 100, 55, 40)])
        elif self.msgbox_type == MSGBOX_TYPE_YESNO:
            self.cells.append(["YES", Rect(64, 100, 55, 40)])
            self.cells.append(["N O", Rect(180, 100, 55, 40)])
        elif self.msgbox_type == MSGBOX_TYPE_INPUT:
            self.cells.append(["INPUT", Rect(30, 50, 230, 40)])
            self.cells.append(["O K", Rect(30, 100, 100, 40)])
            self.cells.append(["CANCEL", Rect(160, 100, 100, 40)])

        # ループ
        while True:
            self.draw()
            event = pygame.event.poll()
            if event.type == MOUSEBUTTONDOWN:
                for cell in self.cells:
                    if cell[1].collidepoint(event.pos[0] - self.rect.left,
                                            event.pos[1] - self.rect.top):
                        if cell[0] == "O K" and self.msgbox_type == MSGBOX_TYPE_OK:
                            userevent = pygame.event.Event(USEREVENT_ALLUPDATE)
                            pygame.event.post(userevent)
                            return
                        elif cell[0] == "YES":
                            self.return_value = True
                            userevent = pygame.event.Event(USEREVENT_ALLUPDATE)
                            pygame.event.post(userevent)
                            return
                        elif cell[0] == "N O":
                            self.return_value = False
                            userevent = pygame.event.Event(USEREVENT_ALLUPDATE)
                            pygame.event.post(userevent)
                            return
                        elif cell[0] == "O K" and self.msgbox_type == MSGBOX_TYPE_INPUT:
                            userevent = pygame.event.Event(USEREVENT_ALLUPDATE)
                            pygame.event.post(userevent)
                            return
                        elif cell[0] == "CANCEL":
                            self.return_value = False
                            userevent = pygame.event.Event(USEREVENT_ALLUPDATE)
                            pygame.event.post(userevent)
                            return
            # インプットボックスのときのみキー入力受付
            elif event.type == KEYDOWN and self.msgbox_type == MSGBOX_TYPE_INPUT:
                if event.key == K_BACKSPACE:            # バックスペース
                    self.return_value = self.return_value[0:-1]
                elif K_0 <= event.key <= K_9:           # 数字
                    self.return_value = self.return_value + pygame.key.name(event.key)
                elif K_KP0 <= event.key <= K_KP9:       # テンキー
                    self.return_value = self.return_value + pygame.key.name(event.key)[1]
                elif K_a <= event.key <= K_z:           # アルファベット
                    if event.mod & KMOD_SHIFT:          # シフト＋で大文字
                        self.return_value = self.return_value +\
                            str.upper(pygame.key.name(event.key))
                    else:                               # 小文字
                        self.return_value = self.return_value + pygame.key.name(event.key)
                elif event.key == K_BACKSLASH:         # シフト＋バックスラッシュ＝アンダーバー
                    if event.mod & KMOD_SHIFT:
                        self.return_value = self.return_value + pygame.key.name(K_UNDERSCORE)

            pygame.display.update()

    def draw(self):
        """ メッセージ画面の描画 """
        self.screen.fill(COLOR_GRAY)

        # メッセージの表示
        for i, msg in enumerate(self.msgs):
            self.screen.blit(self.font.render(msg, True, COLOR_BLACK),  # ボタン名
                             (30, i * 20 + 20))

        # ボタンの表示
        for cell in self.cells:
            if cell[0] == "INPUT":      # INPUTはキー入力
                pygame.draw.rect(self.screen, COLOR_WHITE, cell[1])
                pygame.draw.rect(self.screen, COLOR_BLACK, cell[1], 1)
                self.screen.blit(self.font.render(self.return_value,       # 入力値
                                                  True, COLOR_BLACK),
                                 (cell[1].left + 8, cell[1].top + 10))

            else:
                pygame.draw.rect(self.screen, COLOR_SILVER, cell[1])
                pygame.draw.rect(self.screen, COLOR_BLACK, cell[1], 1)
                self.screen.blit(self.font.render(cell[0], True, COLOR_BLACK),  # ボタン名
                                 (cell[1].left + 8, cell[1].top + 10))
                # マウスカーソルが項目上にある場合は、枠を描画する
                posx, posy = pygame.mouse.get_pos()
                if cell[1].collidepoint((posx - self.rect.left, posy - self.rect.top)):
                    pygame.draw.rect(self.screen, COLOR_BLACK, cell[1], 3)          # セルの枠

        # 画面の枠
        pygame.draw.rect(self.screen, COLOR_BLACK,
                         (0, 0, self.rect.width, self.rect.height), 5)
        # メイン画面に描画
        self.mainscreen.blit(self.screen, self.rect)


class MsgScreen(SubScreen):
    """ メッセージの画面（デバック用？） """
    def __init__(self, name, rect, mainscreen):
        super().__init__(name, rect, mainscreen)
        self.font = pygame.font.SysFont(None, 30)
        self.msgs = []

    def draw(self):
        """ メッセージ画面の描画 """
        self.screen.fill(COLOR_GRAY)
        pygame.draw.rect(self.screen, COLOR_BLACK, (0, 0, self.rect.width, self.rect.height), 6)
        #メッセージの表示
        for i, msg in enumerate(self.msgs):
            self.screen.blit(self.font.render(msg, True, COLOR_BLACK), (5, i * 20 + 5))

        self.mainscreen.blit(self.screen, self.rect)

def main():
    """ メイン処理 """
    pygame.init()
    pygame.mixer.quit()                 # CPU使用率を下げるため
    screen = pygame.display.set_mode(WINDOW_RECT.size)
    screen.fill(COLOR_SILVER)
    pygame.display.set_caption("dotedit")
    clock = pygame.time.Clock()

    # サブスクリーングループ
    subscreengroup = SubScreenGroup(screen)
    # サブスクリーンを生成しグループに追加
    subscreengroup.append(MenuBar("MenuBar", Rect(5, 5, WINDOW_RECT.width - 10, 50), screen))
    subscreengroup.append(EditScreen("EditScreen", Rect(5, 60, 486, 486), screen))
    subscreengroup.append(PalettScreen("PalettScreen", Rect(5, 551, 486, 75), screen))
    subscreengroup.append(ViewScreen("ViewScreen", Rect(496, 60, 486, 486), screen))
    msgscreen = MsgScreen("MsgScreen", Rect(496, 551, 486, 75), screen)     # デバッグ用画面
    subscreengroup.append(msgscreen)
    msgscreen.visible = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            else:
                # イベント処理
                subscreengroup.event_handler(event)

        # サブ画面の更新
        subscreengroup.update()

        # デバック情報の表示設定
        if msgscreen.visible:
            msgscreen.msgs.clear()
            msgscreen.msgs.append('mouse pos(x, y):%s, %s' % pygame.mouse.get_pos())
            msgscreen.msgs.append('%s pos(x, y):%s, %s' % \
                                  subscreengroup.get_subscreen_in_pos(pygame.mouse.get_pos()))

        # サブ画面の描画
        subscreengroup.draw()
        # タイトルにファイル名を表示
        pygame.display.set_caption("dotedit : " \
                                   + subscreengroup.get_subscreen("ViewScreen").save_filename)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
