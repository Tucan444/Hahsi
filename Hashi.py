from hashi_functions import *
import hashi_generator as hg
import hashi_game
import assets.palettes.palette_manager as pm
from menu_effect import Circle_effect
from game_effect import Rectangle_effect
from widget_engine import *
from s_engine import *
import sounds
import pygame
import sys
import json
from pygame.locals import *

# basic config
pygame.mixer.pre_init(48000, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(16)
available = pygame.font.get_fonts()
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

font = pygame.font.SysFont('calibri', 60, True)
small_font = pygame.font.SysFont('calibri', 40, True)
tiny_font = pygame.font.SysFont('calibri', 20, True)

Window_size = [600, 650]
Default_size = Window_size
screen = pygame.display.set_mode(Window_size)
display = pygame.Surface((600, 650))
pygame.display.set_caption("Hashi")
pygame.display.set_icon(pygame.image.load("assets/images/general/hashi_logo.png").convert())
clock = pygame.time.Clock()

soundsX = sounds.get_sounds()


def main_menu(screenX, Win_size):
    # PREP WORK
    # getting setup
    with open("assets/saves/setup.json", "r") as f:
        setup = json.load(f)
    # game variables
    game = Game()
    game.game_flow["ac"] = True
    game.game_flow["custom_string"] = setup["custom_num"]
    # next 3 lines for arrow buttons
    game.game_flow["dfs"] = ["easy", "medium", "hard", "extreme", "custom"]
    game.game_flow["df"] = setup["difficulty"]
    game.game_flow["df_change"] = False
    game.game_flow["dp"] = [0, 0]
    game.game_flow["back_from_game"] = False
    game.game_flow["Win_size"] = Win_size
    game.game_flow["cut_click"] = False
    game.game_flow["change_fs"] = False

    # mouse
    mouse = Mouse(pygame.mouse.get_pos())
    mouse.update(Win_size, Default_size)

    # dealing with palettes
    palette = pm.Palettes("assets/palettes")
    palette.current_palette = setup["palette"]
    palette.palette = palette.get_palette()

    menu_objects = []

    # loading images
    play_images = {"idle": pygame.image.load("assets/images/menu/play.png").convert(),
                   "hover": pygame.image.load("assets/images/menu/play_hover.png").convert()}
    # size 200

    palette_images = {"idle": pygame.image.load("assets/images/menu/palette.png").convert(),
                      "hover": pygame.image.load("assets/images/menu/palette_hover.png").convert()}
    # size 140

    new_game_images = {"idle": pygame.image.load("assets/images/menu/new_game.png").convert(),
                       "hover": pygame.image.load("assets/images/menu/new_game_hover.png").convert()}
    # size 300 150

    difficulty_images = {"idle": pygame.image.load("assets/images/menu/template.png").convert(),
                         "hover": pygame.image.load("assets/images/menu/template_hover.png").convert()}
    # size 250 100

    right_arrow_images = {"idle": pygame.image.load("assets/images/menu/arrow.png").convert(),
                          "hover": pygame.image.load("assets/images/menu/arrow_hover.png").convert()}
    left_arrow_images = {"idle": pygame.transform.flip(pygame.image.load("assets/images/menu/arrow.png").convert(),
                                                       True, False),
                         "hover": pygame.transform.flip(
                             pygame.image.load("assets/images/menu/arrow_hover.png").convert(),
                             True, False)}
    # size 100 100

    custom_size_images = {"idle": pygame.image.load("assets/images/menu/custom.png").convert(),
                          "hover": pygame.image.load("assets/images/menu/custom_pressed.png").convert()}
    # size 100 100

    fs_images = {"idle": pygame.image.load("assets/images/menu/fs.png").convert(),
                 "hover": pygame.image.load("assets/images/menu/fs_hover.png").convert()}
    ms_images = {"idle": pygame.image.load("assets/images/menu/ms.png").convert(),
                 "hover": pygame.image.load("assets/images/menu/ms_hover.png").convert()}
    # size 60 60

    menu_objects.append(CircleButton(200, [200, 220], play_images, play, [game, palette, mouse]))
    menu_objects.append(CircleButton(200, [440, 20], palette_images, next_palette, [palette]))
    menu_objects.append(Button([150, 450], [300, 150], new_game_images, new_game, [game, palette, mouse]))
    menu_objects.append(Button([20, 20], [250, 100], difficulty_images, play_click_sound, []))
    menu_objects.append(Button([440, 270], [100, 100], right_arrow_images, right_arrow, [game]))
    menu_objects.append(Button([60, 270], [100, 100], left_arrow_images, left_arrow, [game]))
    menu_objects.append(Button([480, 400], [100, 100], custom_size_images, activate_edit_text, [game], False))
    menu_objects.append(Button([20, 570], [60, 60], fs_images, change_fs, [game]))
    menu_objects[-1].name = "fs"
    menu_objects.append(Button([20, 570], [60, 60], ms_images, change_fs, [game], False))
    menu_objects[-1].name = "ms"
    difficulty_text = font.render(setup["difficulty"].capitalize(), False, palette.palette["outline-dark"])

    # setting up custom text

    custom_text = font.render(game.game_flow["custom_string"], False, palette.palette["outline-dark"])
    custom_text_hover = font.render(game.game_flow["custom_string"], False, palette.palette["background"])
    ct_images = {"idle": create_text_sur(custom_text, [20, 20], [100, 100]),
                 "hover": create_text_sur(custom_text_hover, [20, 20], [100, 100])}
    menu_objects.append(Button([480, 400], [100, 100], ct_images, activate_edit_text, [game], False))
    menu_objects[-1].name = "custom_text"

    custom_pointer = palette.swap_image(pygame.image.load("assets/images/menu/writing.png").convert(),
                                        "emerald", setup["palette"])
    custom_pointer.set_colorkey((0, 0, 0))

    # setting up custom

    if setup["difficulty"] == "custom":
        for item in menu_objects:
            if item.on_click == activate_edit_text:
                item.active = True

    # circle effect

    cE = Circle_effect
    cE.generate_circles(50, [-50, 50])
    cE.generate_circles(50, [480, 600])

    # last config

    menu_objects, setup = set_palette(setup, palette, setup["palette"], menu_objects, True)

    palette.create_cycle()
    game.game_flow["setup"] = setup
    game.game_flow["screen"] = screenX

    # checking tutorial
    if setup["tutorial"]:
        run_tutorial(screenX, setup, game, palette, mouse)

    # game loop
    while game.alive:
        # checking if returned
        if game.game_flow["back_from_game"]:
            game.game_flow["back_from_game"] = False
            Win_size = game.game_flow["Win_size"]

            with open("assets/saves/setup.json", "r") as f:
                setup = json.load(f)

            game.game_flow["setup"] = setup

        # background
        display.fill(palette.palette["background"])
        pygame.draw.rect(display, palette.palette["outline-shade"], pygame.Rect(180, 0, 240, 650))
        pygame.draw.rect(display, palette.palette["outline"], pygame.Rect(200, 0, 200, 650))

        # displaying effect

        for circle in cE.circles:
            circle.move(display, palette)

        if cE.timer == 0:
            cE.generate_circles(4, [-50, 50])
            cE.generate_circles(4, [480, 600])
            cE.timer += 10
        else:
            cE.timer -= 1

        # displaying widgets

        for widget in menu_objects:
            widget.blit(display)

        # dealing with difficulty

        if game.game_flow["df_change"]:
            game.game_flow["df_change"] = False

            # dealing with json
            setup["difficulty"] = game.game_flow["df"]
            with open("assets/saves/setup.json", "w") as f:
                json.dump(setup, f, indent=4)

            difficulty_text = font.render(setup["difficulty"].capitalize(), False, palette.palette["outline-dark"])

            # changing custom edit text
            if setup["difficulty"] == "custom":
                for item in menu_objects:
                    if item.on_click == activate_edit_text:
                        item.active = True
            else:
                for item in menu_objects:
                    if item.on_click == activate_edit_text:
                        item.active = False

        display.blit(difficulty_text, [40, 40])

        # checking palette

        if palette.changed:
            palette.changed = False
            menu_objects, setup = set_palette(setup, palette, palette.current_palette, menu_objects)
            difficulty_text = font.render(setup["difficulty"].capitalize(), False, palette.palette["outline-dark"])
            custom_pointer = palette.swap_image(pygame.image.load("assets/images/menu/writing.png").convert(),
                                                "emerald", setup["palette"])
            custom_pointer.set_colorkey((0, 0, 0))
            game.game_flow["setup"] = setup

        # custom pointer

        if game.game_flow["ac"] is False:
            display.blit(custom_pointer, [480, 350])

        # event loop

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)

            # keydown
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                elif event.key == K_f:
                    game.fs = not game.fs
                    if game.fs is False:
                        Win_size = Default_size
                        screenX = pygame.display.set_mode(Win_size)
                        game.game_flow["dp"] = [0, 0]
                        mouse.mouse_scroll = game.game_flow["dp"]

                        game.game_flow["Win_size"] = Win_size
                        game.game_flow["screen"] = screenX
                    else:
                        screenX = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
                        d = screenX
                        ratio = [Default_size[1] / Default_size[0], Default_size[0] / Default_size[1]]
                        # u chose width or height here

                        if Default_size[0] > Default_size[1]:
                            Win_size = [d.get_width(), int(d.get_width() * ratio[0])]
                            d = d.get_height()
                            dd = Win_size[1]
                            game.game_flow["dp"][1] = (d - dd) / 2
                            mouse.mouse_scroll = game.game_flow["dp"]
                        else:
                            Win_size = [int(d.get_height() * ratio[1]), d.get_height()]
                            d = pygame.display.get_surface().get_width()
                            dd = Win_size[0]
                            game.game_flow["dp"][0] = (d - dd) / 2
                            mouse.mouse_scroll = game.game_flow["dp"]

                        game.game_flow["Win_size"] = Win_size
                        game.game_flow["screen"] = screenX

            if game.game_flow["ac"]:
                # mouse stuff
                if event.type == MOUSEMOTION:
                    mouse.update(Win_size, Default_size)
                    for widget in menu_objects:
                        widget.hover_check(mouse.mouse_pos)

                # click
                if event.type == MOUSEBUTTONDOWN:
                    for widget in menu_objects:
                        widget.click_check(mouse.mouse_pos)
                        if game.game_flow["cut_click"]:
                            game.game_flow["cut_click"] = False
                            break
            else:
                if event.type == MOUSEBUTTONDOWN:
                    mouse.update(Win_size, Default_size)
                    game.game_flow["ac"] = True
                    for widget in menu_objects:
                        widget.hover_check(mouse.mouse_pos)
                    soundsX["click"].play()

                    # checking if num big enough
                    try:
                        if int(game.game_flow["custom_string"]) < 2 or len(
                                game.game_flow["custom_string"]) == 0:
                            game.game_flow["custom_string"] = "2"
                    except:
                        game.game_flow["custom_string"] = "2"
                    menu_objects, setup = update_text(menu_objects, setup, game, palette)

                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        try:
                            game.game_flow["custom_string"] = game.game_flow["custom_string"][:-1]

                            menu_objects, setup = update_text(menu_objects, setup, game, palette)
                        except:
                            pass
                    elif event.key == K_RETURN:
                        mouse.update(Win_size, Default_size)
                        game.game_flow["ac"] = True
                        for widget in menu_objects:
                            widget.hover_check(mouse.mouse_pos)
                        soundsX["click"].play()

                        # checking if num big enough
                        try:
                            if int(game.game_flow["custom_string"]) < 2 or len(game.game_flow["custom_string"]) == 0:
                                game.game_flow["custom_string"] = "2"
                        except:
                            game.game_flow["custom_string"] = "2"
                        menu_objects, setup = update_text(menu_objects, setup, game, palette)
                    else:
                        if len(game.game_flow["custom_string"]) < 2:
                            try:
                                int(event.unicode)
                                game.game_flow["custom_string"] += event.unicode

                                menu_objects, setup = update_text(menu_objects, setup, game, palette)
                            except:
                                pass

        # checking fs change
        if game.game_flow["change_fs"]:
            game.game_flow["change_fs"] = False

            for obj in menu_objects:
                if obj.name in ["fs", "ms"]:
                    obj.active = not obj.active

            game.fs = not game.fs
            if game.fs is False:
                Win_size = Default_size
                screenX = pygame.display.set_mode(Win_size)
                game.game_flow["dp"] = [0, 0]
                mouse.mouse_scroll = game.game_flow["dp"]

                game.game_flow["Win_size"] = Win_size
                game.game_flow["screen"] = screenX
            else:
                screenX = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
                d = screenX
                ratio = [Default_size[1] / Default_size[0], Default_size[0] / Default_size[1]]
                # u chose width or height here

                if Default_size[0] > Default_size[1]:
                    Win_size = [d.get_width(), int(d.get_width() * ratio[0])]
                    d = d.get_height()
                    dd = Win_size[1]
                    game.game_flow["dp"][1] = (d - dd) / 2
                    mouse.mouse_scroll = game.game_flow["dp"]
                else:
                    Win_size = [int(d.get_height() * ratio[1]), d.get_height()]
                    d = pygame.display.get_surface().get_width()
                    dd = Win_size[0]
                    game.game_flow["dp"][0] = (d - dd) / 2
                    mouse.mouse_scroll = game.game_flow["dp"]

                game.game_flow["Win_size"] = Win_size
                game.game_flow["screen"] = screenX

        # basic loop config

        screenX.blit(pygame.transform.scale(display, Win_size), game.game_flow["dp"])
        pygame.display.update()
        clock.tick(60)


# new_game_btn
def new_game(args):
    game = args[0]
    palette = args[1]
    mouse = args[2]
    setup = game.game_flow["setup"]
    screenX = game.game_flow["screen"]
    setup[setup["difficulty"]] = True

    if setup["difficulty"] == "easy":
        hashi = hg.Hashi(5)
    elif setup["difficulty"] == "medium":
        hashi = hg.Hashi(10)
    elif setup["difficulty"] == "hard":
        hashi = hg.Hashi(15)
    elif setup["difficulty"] == "extreme":
        hashi = hg.Hashi(20)
    elif setup["difficulty"] == "custom":
        hashi = hg.Hashi(int(setup["custom_num"]))
    else:
        sys.exit(55)

    hashi.generate_map()
    hashi.save(f"assets/maps/{setup['difficulty']}.txt")
    soundsX["click"].play()

    run_game(screenX, setup, game, palette, mouse, "new")
    game.game_flow["cut_click"] = True


# play_btn
def play(args):
    game = args[0]
    palette = args[1]
    mouse = args[2]
    setup = game.game_flow["setup"]
    screenX = game.game_flow["screen"]

    if setup[setup["difficulty"]] is False:
        new_game(args)
    else:
        soundsX["click"].play()
        run_game(screenX, setup, game, palette, mouse, "continue")
        game.game_flow["cut_click"] = True


# at this point the whole menu is done and the game is ready to be run so here we go
def run_game(screenX, setup, gameMenu, palette, mouse, state):
    game = Game()
    game.game_flow["dp"] = gameMenu.game_flow["dp"]
    game.fs = gameMenu.fs
    hashi = None
    Win_size = gameMenu.game_flow["Win_size"]
    game.game_flow["scroll_length"] = (Win_size[0] - 60) / 2
    game.game_flow["quit"] = False

    scroll = Scroll([-20, -20])

    mid_point_scroll_mouse = [game.game_flow["dp"][0] + (Win_size[0] / 2),
                              game.game_flow["dp"][1] + (Win_size[1] / 2)]

    back_btn = Button([200, 350], [200, 100], get_back_images(palette), go_back, [game])
    win_image = get_win_image()

    # initing rectangle effect
    rE = Rectangle_effect
    rE.generate_rects()

    # initializing game by state
    if state == "new":
        hashi = hashi_game.HashiG("file.txt", f"assets/maps/{setup['difficulty']}.txt", palette, mouse)
    elif state == "continue":
        hashi = hashi_game.HashiG("file.json", f"assets/saves/game_saves/{setup['difficulty']}.json", palette, mouse)

    hashi_top_lim = [(hashi.get_length() + 40) - 600, (hashi.get_length() + 40) - 650]

    # pre scrolling
    scroll.move_scroll_based_on_pos(mouse.get_scrolled(scroll), [600, 650], "both", 40)

    scroll.scroll_lim(scroll, [-40, -40], hashi_top_lim)

    while game.alive:
        # dealing with hashi locked
        if hashi.locked:
            hashi.on_locked(mouse, scroll)

        # background
        display.fill(palette.palette["background"])

        # dealing with bg effect
        for item in rE.rects:
            item.move(display, palette)

        if rE.timer == 0:
            rE.generate_rects(5, [1, 3])
            rE.timer = 10
        else:
            rE.timer -= 1

        # dealing with scroll
        # not using mouse.mouse_pos because screen size affects
        if distance_indicator(pygame.mouse.get_pos(), mid_point_scroll_mouse) > game.game_flow["scroll_length"]:
            scroll.move_scroll_based_on_pos(mouse.get_scrolled(scroll), [600, 650], "both", 40)

            scroll.scroll_lim(scroll, [-40, -40], hashi_top_lim)

        # game

        hashi.blit(display, palette, scroll)

        # win screen

        if hashi.win:
            display.blit(win_image, [50, 50])

            back_btn.blit(display)

            setup[setup["difficulty"]] = False

        # event loop

        for event in pygame.event.get():
            if event.type == QUIT:
                # saving before quiting
                with open("assets/saves/setup.json", "w") as f:
                    json.dump(setup, f, indent=4)

                if hashi.win is False:
                    hashi.save(setup)

                pygame.quit()
                sys.exit(0)

            # keydown
            if event.type == KEYDOWN:
                if hashi.locked is False:
                    if event.key == K_ESCAPE:
                        gameMenu.fs = game.fs
                        gameMenu.game_flow["dp"] = game.game_flow["dp"]
                        gameMenu.game_flow["back_from_game"] = True
                        gameMenu.game_flow["Win_size"] = Win_size
                        game.alive = False

                        with open("assets/saves/setup.json", "w") as f:
                            json.dump(setup, f, indent=4)

                        if hashi.win is False:
                            hashi.save(setup)
                else:
                    if event.key == K_ESCAPE:
                        hashi.locked = False
                        hashi.clear_temp()
                        hashi.clear_temp_remove()

                        mouse.update(Win_size, Default_size)
                        hashi.hover(mouse, scroll)

                if event.key == K_f:
                    game.fs = not game.fs
                    if game.fs is False:
                        Win_size = Default_size
                        screenX = pygame.display.set_mode(Win_size)
                        game.game_flow["dp"] = [0, 0]
                        mouse.mouse_scroll = game.game_flow["dp"]
                        # specifics
                        mid_point_scroll_mouse = [game.game_flow["dp"][0] + (Win_size[0] / 2),
                                                  game.game_flow["dp"][1] + (Win_size[1] / 2)]
                        game.game_flow["scroll_length"] = (Win_size[0] - 100) / 2

                    else:
                        screenX = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
                        d = screenX
                        ratio = [Default_size[1] / Default_size[0], Default_size[0] / Default_size[1]]
                        # u chose width or height here

                        if Default_size[0] > Default_size[1]:
                            Win_size = [d.get_width(), int(d.get_width() * ratio[0])]
                            d = d.get_height()
                            dd = Win_size[1]
                            game.game_flow["dp"][1] = (d - dd) / 2
                        else:
                            Win_size = [int(d.get_height() * ratio[1]), d.get_height()]
                            d = pygame.display.get_surface().get_width()
                            dd = Win_size[0]
                            game.game_flow["dp"][0] = (d - dd) / 2

                        mouse.mouse_scroll = game.game_flow["dp"]
                        # specifics
                        mid_point_scroll_mouse = [game.game_flow["dp"][0] + (Win_size[0] / 2),
                                                  game.game_flow["dp"][1] + (Win_size[1] / 2)]
                        game.game_flow["scroll_length"] = (Win_size[0] - 60) / 2

            if hashi.win is False:
                if hashi.locked is False:
                    # mouse stuff
                    if event.type == MOUSEMOTION:
                        mouse.update(Win_size, Default_size)
                        hashi.hover(mouse, scroll)

                    # click
                    elif event.type == MOUSEBUTTONDOWN:
                        hashi.click(mouse, scroll)
                        if hashi.locked:
                            soundsX["click"].play()
                else:
                    if event.type == MOUSEMOTION:
                        mouse.update(Win_size, Default_size)

                    elif event.type == MOUSEBUTTONDOWN:
                        hashi.locked = False
                        hashi.click_on_locked(mouse, scroll)
                        hashi.check_win()

                        mouse.update(Win_size, Default_size)
                        hashi.hover(mouse, scroll)
            else:
                if event.type == MOUSEMOTION:
                    mouse.update(Win_size, Default_size)
                    back_btn.hover_check(mouse.mouse_pos)

                elif event.type == MOUSEBUTTONDOWN:
                    back_btn.click_check(mouse.mouse_pos)

        # quiting on back button (same as esc)

        if game.game_flow["quit"]:
            gameMenu.fs = game.fs
            gameMenu.game_flow["dp"] = game.game_flow["dp"]
            gameMenu.game_flow["back_from_game"] = True
            gameMenu.game_flow["Win_size"] = Win_size
            game.alive = False

            with open("assets/saves/setup.json", "w") as f:
                json.dump(setup, f, indent=4)

        # basic loop config

        screenX.blit(pygame.transform.scale(display, Win_size), game.game_flow["dp"])
        pygame.display.update()
        clock.tick(60)


# tutorial
def run_tutorial(screenX, setup, gameMenu, palette, mouse):
    game = Game()
    game.game_flow["dp"] = gameMenu.game_flow["dp"]
    game.fs = gameMenu.fs
    Win_size = gameMenu.game_flow["Win_size"]
    game.game_flow["scroll_length"] = (Win_size[0] - 60) / 2
    game.game_flow["quit"] = False
    game.game_flow["tf"] = False  # tutorial forward
    game.game_flow["t_step"] = 0

    scroll = Scroll([-20, -20])

    mid_point_scroll_mouse = [game.game_flow["dp"][0] + (Win_size[0] / 2),
                              game.game_flow["dp"][1] + (Win_size[1] / 2)]

    back_btn = Button([200, 350], [200, 100], get_back_images(palette), go_back, [game])
    win_image = get_win_image()

    # initing rectangle effect
    rE = Rectangle_effect
    rE.generate_rects()

    # initializing tutorial
    hashi = hashi_game.HashiG("file.json", f"assets/tutorial/tutorial.json", palette, mouse)

    hashi_top_lim = [(hashi.get_length() + 40) - 600, (hashi.get_length() + 40) - 650]

    # preparing tutorial circle
    tutorial_circle_images, size = get_tutorial_circle_images(math.sqrt(hashi.indent/hashi.indent_default)**1.5)
    tutorial_circle = CircleButton(size, [120 - (size/2), 120 - (size/2)],
                                   tutorial_circle_images, move_in_tutorial, [game])

    # pre scrolling
    scroll.move_scroll_based_on_pos(mouse.get_scrolled(scroll), [600, 650], "both", 40)

    scroll.scroll_lim(scroll, [-40, -40], hashi_top_lim)

    while game.alive:
        # dealing with tutorial
        if game.game_flow['tf']:
            game.game_flow["tf"] = False

            if game.game_flow["t_step"] == 0:
                game.game_flow["t_step"] += 1
                hashi.click(mouse, scroll)
                tutorial_circle.move([0, 240])
                tutorial_circle.hover_check(mouse.get_scrolled(scroll))
                soundsX["click"].play()

            elif game.game_flow["t_step"] == 1:
                game.game_flow["t_step"] += 1
                hashi.locked = False
                hashi.click_on_locked(mouse, scroll)
                hashi.check_win()

                mouse.update(Win_size, Default_size)
                hashi.hover(mouse, scroll)

                tutorial_circle.move([240, -240])
                tutorial_circle.hover_check(mouse.get_scrolled(scroll))
                soundsX["join"].play()

            elif game.game_flow["t_step"] == 2:
                game.game_flow["t_step"] += 1
                hashi.click(mouse, scroll)
                tutorial_circle.move([0, -60])
                tutorial_circle.hover_check(mouse.get_scrolled(scroll))
                soundsX["click"].play()

            elif game.game_flow["t_step"] == 3:
                game.game_flow["t_step"] += 1
                hashi.locked = False
                hashi.click_on_locked(mouse, scroll)
                hashi.check_win()

                mouse.update(Win_size, Default_size)
                hashi.hover(mouse, scroll)

                tutorial_circle.move([0, -60])
                tutorial_circle.hover_check(mouse.get_scrolled(scroll))
                soundsX["join"].play()

            elif game.game_flow["t_step"] == 4:
                game.game_flow["t_step"] += 1
                hashi.click(mouse, scroll)
                tutorial_circle.move([-240, 0])
                tutorial_circle.hover_check(mouse.get_scrolled(scroll))
                soundsX["click"].play()

            elif game.game_flow["t_step"] == 5:
                hashi.locked = False
                hashi.click_on_locked(mouse, scroll)
                hashi.check_win()

                mouse.update(Win_size, Default_size)
                hashi.hover(mouse, scroll)
                soundsX["join"].play()

                tutorial_circle.active = False

        # dealing with hashi locked
        if hashi.locked:
            hashi.on_locked(mouse, scroll)

        # background
        display.fill(palette.palette["background"])

        # dealing with bg effect
        for item in rE.rects:
            item.move(display, palette)

        if rE.timer == 0:
            rE.generate_rects(5, [1, 3])
            rE.timer = 10
        else:
            rE.timer -= 1

        # dealing with scroll
        # not using mouse.mouse_pos because screen size affects
        if distance_indicator(pygame.mouse.get_pos(), mid_point_scroll_mouse) > game.game_flow["scroll_length"]:
            scroll.move_scroll_based_on_pos(mouse.get_scrolled(scroll), [600, 650], "both", 40)

            scroll.scroll_lim(scroll, [-40, -40], hashi_top_lim)

        # game

        hashi.blit(display, palette, scroll)

        # tutorial

        tutorial_circle.blit(display, scroll)

        # win screen

        if hashi.win:
            display.blit(win_image, [50, 50])

            back_btn.blit(display)

            setup["tutorial"] = False

        # event loop

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)

            # keydown
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameMenu.fs = game.fs
                    gameMenu.game_flow["dp"] = game.game_flow["dp"]
                    gameMenu.game_flow["back_from_game"] = True
                    gameMenu.game_flow["Win_size"] = Win_size
                    game.alive = False

                    with open("assets/saves/setup.json", "w") as f:
                        json.dump(setup, f, indent=4)

                if event.key == K_f:
                    game.fs = not game.fs
                    if game.fs is False:
                        Win_size = Default_size
                        screenX = pygame.display.set_mode(Win_size)
                        game.game_flow["dp"] = [0, 0]
                        mouse.mouse_scroll = game.game_flow["dp"]
                        # specifics
                        mid_point_scroll_mouse = [game.game_flow["dp"][0] + (Win_size[0] / 2),
                                                  game.game_flow["dp"][1] + (Win_size[1] / 2)]
                        game.game_flow["scroll_length"] = (Win_size[0] - 100) / 2

                    else:
                        screenX = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
                        d = screenX
                        ratio = [Default_size[1] / Default_size[0], Default_size[0] / Default_size[1]]
                        # u chose width or height here

                        if Default_size[0] > Default_size[1]:
                            Win_size = [d.get_width(), int(d.get_width() * ratio[0])]
                            d = d.get_height()
                            dd = Win_size[1]
                            game.game_flow["dp"][1] = (d - dd) / 2
                        else:
                            Win_size = [int(d.get_height() * ratio[1]), d.get_height()]
                            d = pygame.display.get_surface().get_width()
                            dd = Win_size[0]
                            game.game_flow["dp"][0] = (d - dd) / 2

                        mouse.mouse_scroll = game.game_flow["dp"]
                        # specifics
                        mid_point_scroll_mouse = [game.game_flow["dp"][0] + (Win_size[0] / 2),
                                                  game.game_flow["dp"][1] + (Win_size[1] / 2)]
                        game.game_flow["scroll_length"] = (Win_size[0] - 60) / 2

            if hashi.win is False:
                if hashi.locked is False:
                    # mouse stuff
                    if event.type == MOUSEMOTION:
                        mouse.update(Win_size, Default_size)
                        hashi.hover(mouse, scroll)
                        tutorial_circle.hover_check(mouse.get_scrolled(scroll))

                    # click
                    elif event.type == MOUSEBUTTONDOWN:
                        tutorial_circle.click_check(mouse.get_scrolled(scroll))
                else:
                    if event.type == MOUSEMOTION:
                        mouse.update(Win_size, Default_size)
                        tutorial_circle.hover_check(mouse.get_scrolled(scroll))

                    elif event.type == MOUSEBUTTONDOWN:
                        tutorial_circle.click_check(mouse.get_scrolled(scroll))
            else:
                if event.type == MOUSEMOTION:
                    mouse.update(Win_size, Default_size)
                    back_btn.hover_check(mouse.mouse_pos)

                elif event.type == MOUSEBUTTONDOWN:
                    back_btn.click_check(mouse.mouse_pos)

        # quiting on back button (same as esc)

        if game.game_flow["quit"]:
            gameMenu.fs = game.fs
            gameMenu.game_flow["dp"] = game.game_flow["dp"]
            gameMenu.game_flow["back_from_game"] = True
            gameMenu.game_flow["Win_size"] = Win_size
            game.alive = False

            with open("assets/saves/setup.json", "w") as f:
                json.dump(setup, f, indent=4)

        # basic loop config

        screenX.blit(pygame.transform.scale(display, Win_size), game.game_flow["dp"])
        pygame.display.update()
        clock.tick(60)


main_menu(screen, Window_size)
