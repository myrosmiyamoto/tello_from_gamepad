#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
from djitellopy import Tello
import pygame
from pygame.locals import *

def main():
    # pygameの初期化
    pygame.init()

    # Joystickオブジェクトの作成
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f'Gamepad Name: {joystick.get_name()}')

    # Telloの初期化
    # Wi-Fiアクセスポイントへ接続する設定（Wi-Fi子機になるモード）にしている場合は
    # hostを指定してIPアドレスは現物に合わせる
    tello = Tello(host='192.168.13.3', retry_count=1)  # retry_countは応答が来ないときのリトライ回数
    Tello.RESPONSE_TIMEOUT = 0.1  # 応答が来ないときのタイムアウト時間
    Tello.TAKEOFF_TIMEOUT = 1  # 離陸時のタイムアウト時間
    tello.connect() # Telloへ接続
    time.sleep(1)

    while True:
        try:
            # イベントの取得
            for event in pygame.event.get():
                # イベントがスティック操作の場合
                if event.type == pygame.locals.JOYAXISMOTION:
                    send_tello(tello, 'rc', (map_axis(joystick.get_axis(3)), -map_axis(joystick.get_axis(4)), -map_axis(joystick.get_axis(1)), map_axis(joystick.get_axis(0))))
                # イベントがボタン操作の場合
                elif event.type == pygame.locals.JOYBUTTONDOWN:
                    if joystick.get_button(7):
                        send_tello(tello, 'takeoff')
                    elif joystick.get_button(6):
                        send_tello(tello, 'land')
                    elif joystick.get_button(3):
                        send_tello(tello, 'flip_forward')
                    elif joystick.get_button(0):
                        send_tello(tello, 'flip_back')
                    elif joystick.get_button(2):
                        send_tello(tello, 'flip_left')
                    elif joystick.get_button(1):
                        send_tello(tello, 'flip_right')
                    elif joystick.get_button(8):
                        send_tello(tello, 'emergency')
        # キーボードからの終了
        except KeyboardInterrupt:
            send_tello(tello, 'emergency')
            print('[Finish] Press Ctrl+C to exit')
            sys.exit()
        # ゲームパッドからの終了
        except SystemExit:
            print('[Finish] Press emergency button to exit')
            sys.exit()


# スティックの出力数値を調整
# -1.0 ~ 1.0 の数値を -100 ~ 100 の数値に変換
# 線形補間を用いて計算している
def map_axis(val):
    # 小数点以下2桁に四捨五入
    val = round(val, 2)
    # 入力の最小値と最大値
    in_min = -1
    in_max = 1
    # 出力の最小値と最大値
    out_min = -100
    out_max = 100
    # 線形補間を用いて計算
    return int(out_min + (out_max - out_min) * ((val - in_min)  / (in_max - in_min)))


############# send_rc_control(a, b, c, d)
# a: left right          left -100 ..  100 right
# b: forward backward    forw  100 .. -100 backw
# c: up down               up  100 .. -100 down
# d: rotate  (yaw)       left -100 ..  100 right
def send_tello(tello, cmd, rc_args = (0, 0, 0, 0)):
    try:
        if cmd == 'land':
            tello.land()
        elif cmd == 'takeoff':
            tello.takeoff()
        elif cmd == 'flip_forward':
            tello.flip_forward()
        elif cmd == 'flip_back':
            tello.flip_back()
        elif cmd == 'flip_left':
            tello.flip_left()
        elif cmd == 'flip_right':
            tello.flip_right()
        elif cmd == 'rc':
            tello.send_rc_control(rc_args[0], rc_args[1], rc_args[2], rc_args[3])
        elif cmd == 'emergency':
            print('\nEmergency Stop!!\n')
            tello.emergency()
            print(f'[Battery] {tello.get_battery()}%')
            raise SystemExit
    except Exception as e:
        print(e, file=sys.stderr)


if __name__ == '__main__':
    main()
