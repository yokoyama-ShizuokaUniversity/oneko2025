import sys
import random as rd
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import math # 算術計算 (距離や角度) のためにインポート

# --- 設定値 ---
print(sys.argv)
neko_type = sys.argv[1] if len(sys.argv) > 1 else 'white'
dir = f'neko/2023-icon-library/{neko_type}'
STANDARD_PNG = f'{dir}/still.png'
CAT_MOVE_PNG = {
    d: [f'{dir}/{d}run1.png', f'{dir}/{d}run2.png'] for d in ['e', 'w', 'n', 's', 'ne', 'nw', 'se', 'sw']
}
CAT_STAY_PNG = {
    "escratch": [f'{dir}/escratch1.png', f'{dir}/escratch2.png'],
    "nscratch": [f'{dir}/nscratch1.png', f'{dir}/nscratch2.png'],
    "wscratch": [f'{dir}/wscratch1.png', f'{dir}/wscratch2.png'],
    "sscratch": [f'{dir}/sscratch1.png', f'{dir}/sscratch2.png'],
    "itch": [f'{dir}/itch1.png', f'{dir}/itch2.png'],
    "sleep": [f'{dir}/sleep1.png', f'{dir}/sleep2.png'],
    "alert": [f'{dir}/alert.png'],
    "wash": [f'{dir}/wash.png'],
    "yawn": [f'{dir}/yawn.png']
}

FIXED_SPEED = 10     # 猫が1フレームに進むピクセル数 (この値で速度を調整)
STOP_DISTANCE = 25  # マウスがこの距離（ピクセル）以内なら停止
UPDATE_INTERVAL = 200 # 更新間隔 (ミリ秒)
# ---------------

class NekoWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        # 1. 枠を消す & 最前面に
        self.set_decorated(False)
        self.set_keep_above(True)
        
        # 2. 背景を透明にする
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        # 3. PNG画像を表示するGtk.Imageウィジェット
        self.image = Gtk.Image.new_from_file(STANDARD_PNG)
        self.add(self.image)
        
        # 4. マウス位置の取得と更新を開始
        # Gtk.Window へのポインタを渡す
        GLib.timeout_add(UPDATE_INTERVAL, self.update_neko, self)

        self.cat_move_state = {
            d: False for d in CAT_MOVE_PNG.keys()
        }

    def update_neko(self, user_data): # user_data を受け取る
        # 5. マウス座標の取得
        display = Gdk.Display.get_default()
        _, mouse_x, mouse_y = display.get_default_seat().get_pointer().get_position()
        
        # 6. 猫ウィンドウの座標とサイズを取得
        win_x, win_y = self.get_position()
        alloc = self.get_allocation()
        # 猫の中心座標を計算
        neko_center_x = win_x + (alloc.width / 2)
        neko_center_y = win_y + (alloc.height / 2)
        
        # 7. 移動ロジック (速度一定)
        dx = mouse_x - neko_center_x
        dy = mouse_y - neko_center_y
        
        # マウスまでの距離を計算 (三平方の定理)
        distance = math.hypot(dx, dy) # sqrt(dx*dx + dy*dy) と同じ

        # 速度調整 (マウスが一定距離より離れている場合のみ動く)
        if distance > STOP_DISTANCE:
            # マウスへの方向ベクトル (正規化) を計算
            # 距離が0でないことを保証 (distance > STOP_DISTANCE で保証済み)
            norm_dx = dx / distance
            norm_dy = dy / distance
            
            # 一定速度 (FIXED_SPEED) を方向に掛けて、移動量を計算
            step_x = norm_dx * FIXED_SPEED
            step_y = norm_dy * FIXED_SPEED
            print(norm_dx, norm_dy)
            new_x = int(win_x + step_x)
            new_y = int(win_y + step_y)
            self.move(new_x, new_y)
            
            # 8. アニメーション画像の切り替え (移動方向に基づく)
            if dx > 10: # Eに移動中
                if dy > 50: # SEに移動中
                    self.image.set_from_file(self.cat_png('se'))
                elif dy < -50: # NEに移動中
                    self.image.set_from_file(self.cat_png('ne'))
                else:
                    self.image.set_from_file(self.cat_png('e'))
            elif dx < -10: # 左に移動中
                if dy > 50: # SWに移動中
                    self.image.set_from_file(self.cat_png('sw'))
                elif dy < -50: # NWに移動中
                    self.image.set_from_file(self.cat_png('nw'))
                else:
                    self.image.set_from_file(self.cat_png('w'))
            elif dy > 10: # Sに移動中
                self.image.set_from_file(self.cat_png('s'))
            elif dy < -10: # Nに移動中
                self.image.set_from_file(self.cat_png('n'))

        else:
            # 停止時
            self.image.set_from_file(STANDARD_PNG)
            
        # 9. タイマーを継続する
        return True # GLib.timeout_add で True を返すとタイマーが継続される
    def cat_png(self, dir) -> str:
        if self.cat_move_state[dir]:
            self.cat_move_state[dir] = False
            return CAT_MOVE_PNG[dir][0]
        else:
            self.cat_move_state[dir] = True
            return CAT_MOVE_PNG[dir][1]
    def cat_staying_pngs(self):

# 実行
win = NekoWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()