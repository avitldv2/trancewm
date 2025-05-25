from Xlib.display import Display
from Xlib import X, XK
import subprocess
from config import KEYBINDS, TERMINAL, FOCUSED_BORDER_COLOR, UNFOCUSED_BORDER_COLOR, BORDER_WIDTH, MIN_WIDTH, MIN_HEIGHT, MODKEY

dpy = Display()
root = dpy.screen().root

from Xlib.protocol import request

def get_color_pixel(color_str):
    cmap = dpy.screen().default_colormap
    color = cmap.alloc_named_color(color_str).pixel
    return color

FOCUSED_COLOR_PIXEL = get_color_pixel(FOCUSED_BORDER_COLOR)
UNFOCUSED_COLOR_PIXEL = get_color_pixel(UNFOCUSED_BORDER_COLOR)

mod_value = eval(MODKEY, {'X': X})
for kb in KEYBINDS:
    mod = eval(kb['mod'], {'X': X, 'MODKEY': mod_value})
    keycode = dpy.keysym_to_keycode(XK.string_to_keysym(kb['key']))
    dpy.screen().root.grab_key(keycode, mod, 1, X.GrabModeAsync, X.GrabModeAsync)

dpy.screen().root.grab_button(1, X.Mod1Mask, 1, X.ButtonPressMask|X.ButtonReleaseMask|X.PointerMotionMask,
        X.GrabModeAsync, X.GrabModeAsync, X.NONE, X.NONE)
dpy.screen().root.grab_button(3, X.Mod1Mask, 1, X.ButtonPressMask|X.ButtonReleaseMask|X.PointerMotionMask,
        X.GrabModeAsync, X.GrabModeAsync, X.NONE, X.NONE)
root.change_attributes(event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask | X.ButtonPressMask)

start = None
focused_win = None
maximized = {}
while 1:
    ev = dpy.next_event()
    if ev.type == X.MapRequest:
        ev.window.map()
        try:
            ev.window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
            ev.window.configure(stack_mode=X.Above)
        except Exception:
            pass
    elif ev.type == X.KeyPress:
        handled = False
        for kb in KEYBINDS:
            mod = eval(kb['mod'], {'X': X, 'MODKEY': mod_value})
            keycode = dpy.keysym_to_keycode(XK.string_to_keysym(kb['key']))
            if ev.detail == keycode and (ev.state & mod) == mod:
                if kb['action'] == 'spawn_terminal':
                    subprocess.Popen([TERMINAL])
                    handled = True
                elif kb['action'] == 'raise' and ev.child != X.NONE:
                    ev.child.configure(stack_mode = X.Above)
                    handled = True
                elif kb['action'] == 'maximize' and ev.child != X.NONE:
                    win = ev.child
                    if win.id not in maximized:
                        geo = win.get_geometry()
                        maximized[win.id] = (geo.x, geo.y, geo.width, geo.height)
                        scr = dpy.screen()
                        win.configure(x=0, y=0, width=scr.width_in_pixels, height=scr.height_in_pixels)
                    handled = True
                elif kb['action'] == 'unmaximize' and ev.child != X.NONE:
                    win = ev.child
                    if win.id in maximized:
                        x, y, w, h = maximized[win.id]
                        win.configure(x=x, y=y, width=w, height=h)
                        del maximized[win.id]
                    handled = True
                elif kb['action'] == 'close' and ev.child != X.NONE:
                    wm_protocols = dpy.intern_atom('WM_PROTOCOLS')
                    wm_delete = dpy.intern_atom('WM_DELETE_WINDOW')
                    try:
                        protocols = ev.child.get_wm_protocols()
                        if wm_delete in protocols:
                            ev.child.send_event(
                                Xlib.protocol.event.ClientMessage(
                                    window=ev.child,
                                    client_type=wm_protocols,
                                    data=(32, [wm_delete, X.CurrentTime, 0, 0, 0])
                                ),
                                event_mask=0,
                            )
                        else:
                            ev.child.destroy()
                    except Exception:
                        ev.child.destroy()
                    handled = True
        if not handled and ev.child != X.NONE:
            ev.child.configure(stack_mode = X.Above)
        if ev.child != X.NONE:
            if focused_win and focused_win.id != ev.child.id:
                try:
                    focused_win.configure(border_width=BORDER_WIDTH)
                    focused_win.change_attributes(border_pixel=UNFOCUSED_COLOR_PIXEL)
                except Exception:
                    pass
            try:
                ev.child.configure(border_width=BORDER_WIDTH)
                ev.child.change_attributes(border_pixel=FOCUSED_COLOR_PIXEL)
                ev.child.configure(stack_mode = X.Above)
                focused_win = ev.child
            except Exception:
                pass
    elif ev.type == X.ButtonPress and ev.child != X.NONE:
        if ev.state & X.Mod1Mask:
            attr = ev.child.get_geometry()
            start = ev
        else:
            start = None
        if focused_win and focused_win.id != ev.child.id:
            try:
                focused_win.configure(border_width=BORDER_WIDTH)
                focused_win.change_attributes(border_pixel=UNFOCUSED_COLOR_PIXEL)
            except Exception:
                pass
        try:
            ev.child.configure(border_width=BORDER_WIDTH)
            ev.child.change_attributes(border_pixel=FOCUSED_COLOR_PIXEL)
            ev.child.configure(stack_mode = X.Above)
            focused_win = ev.child
        except Exception:
            pass
        dpy.allow_events(X.ReplayPointer, X.CurrentTime)
    elif ev.type == X.MotionNotify and start:
        xdiff = ev.root_x - start.root_x
        ydiff = ev.root_y - start.root_y
        win = start.child
        if win.id in maximized:
            del maximized[win.id]
        new_width = attr.width + (start.detail == 3 and xdiff or 0)
        new_height = attr.height + (start.detail == 3 and ydiff or 0)
        win.configure(
            x = attr.x + (start.detail == 1 and xdiff or 0),
            y = attr.y + (start.detail == 1 and ydiff or 0),
            width = max(MIN_WIDTH, new_width),
            height = max(MIN_HEIGHT, new_height))
    elif ev.type == X.ButtonRelease:
        start = None
