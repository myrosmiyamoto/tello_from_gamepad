#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
from djitellopy import Tello, TelloException
import pygame
from pygame.locals import JOYAXISMOTION, JOYBUTTONDOWN
from functools import cache


def main():
    host = '192.168.13.3'
    tello_from_gamepad = TelloFromGamepad(host)
    tello_from_gamepad.start()


class TelloFromGamepad():
    def __init__(self, host, joystick_num=0):
        # pygameの初期化
        pygame.init()

        # Joystickオブジェクトの作成
        self.joystick = pygame.joystick.Joystick(joystick_num)
        self.joystick.init()
        print(f'Gamepad Name: {self.joystick.get_name()}')

        # Telloの初期化
        # Wi-Fiアクセスポイントへ接続する設定（Wi-Fi子機になるモード）にしている場合は
        # hostを指定してIPアドレスは現物に合わせる
        Tello.RETRY_COUNT = 1          # retry_countは応答が来ないときのリトライ回数
        Tello.RESPONSE_TIMEOUT = 0.01  # 応答が来ないときのタイムアウト時間
        self.tello = Tello(host=host)


    def start(self):
        try:
            self.tello.connect()  # Telloへ接続
        except KeyboardInterrupt:
            print('\n[Finish] Press Ctrl+C to exit')
            sys.exit()
        except TelloException:
            print('[Finish] Connection timeout')
            sys.exit()
        time.sleep(1)

        while True:
            try:
                # イベントの取得
                for event in pygame.event.get():
                    # イベントがスティック操作の場合
                    if event.type == pygame.locals.JOYAXISMOTION:
                        self.send_tello('rc',
                                        self.map_axis(round(self.joystick.get_axis(3), 2)),
                                        self.map_axis(-round(self.joystick.get_axis(1), 2)),
                                        self.map_axis(-round(self.joystick.get_axis(4), 2)),
                                        self.map_axis(round(self.joystick.get_axis(0), 2))
                                        )
                    # イベントがボタン操作の場合
                    elif event.type == pygame.locals.JOYBUTTONDOWN:
                        if self.joystick.get_button(7):
                            self.send_tello('takeoff')
                        elif self.joystick.get_button(6):
                            self.send_tello('land')
                        elif self.joystick.get_button(3):
                            self.send_tello('flip_forward')
                        elif self.joystick.get_button(0):
                            self.send_tello('flip_back')
                        elif self.joystick.get_button(2):
                            self.send_tello('flip_left')
                        elif self.joystick.get_button(1):
                            self.send_tello('flip_right')
                        elif self.joystick.get_button(8):
                            print('[Finish] Press emergency button to exit')
                            self.send_tello('emergency')
            # Ctrl+Cが押された
            except KeyboardInterrupt:
                print('[Warnning] Press Ctrl+C to exit')
                self.send_tello('emergency')


    # スティックの出力数値を調整
    # -1.0 ~ 1.0 の数値を -100 ~ 100 の数値に変換
    # 線形補間を用いて計算している
    @cache
    def map_axis(self, val):
        # 小数点以下2桁に四捨五入

        # 入力の最小値と最大値
        in_min = -1
        in_max = 1
        # 出力の最小値と最大値
        out_min = -100
        out_max = 100
        # 線形補間を用いて計算
        return int(out_min + (out_max - out_min) * ((val - in_min) / (in_max - in_min)))


    # send_rc_control(left_right, forward_backward, up_down, yaw)
    # left_right                 left -100 ...  100 right
    # forward_backward           forw  100 ... -100 backw
    # up_down                      up  100 ... -100 down
    # yaw (rotate)      counter clock -100 ...  100 clock
    def send_tello(self, cmd, left_right=0, forward_backward=0, up_down=0, yaw=0):
        if cmd == 'land':
            self.tello.land()
        elif cmd == 'takeoff':
            self.tello.takeoff()
        elif cmd == 'flip_forward':
            self.tello.flip_forward()
        elif cmd == 'flip_back':
            self.tello.flip_back()
        elif cmd == 'flip_left':
            self.tello.flip_left()
        elif cmd == 'flip_right':
            self.tello.flip_right()
        elif cmd == 'rc':
            self.tello.send_rc_control(left_right, forward_backward, up_down, yaw)
        elif cmd == 'emergency':
            print('\nEmergency Stop!!\n')
            self.tello.emergency()
            print(f'[Battery] {self.tello.get_battery()}%')
            self.game_finish()


    def game_finish(self):
        print('[Finish] Game finish!')
        del self.tello
        sys.exit()


if __name__ == '__main__':
    main()
