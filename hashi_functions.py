import json
import pygame
import sounds

# basic config
pygame.mixer.pre_init(48000, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(16)

font = pygame.font.SysFont('calibri', 60, True)
small_font = pygame.font.SysFont('calibri', 40, True)
tiny_font = pygame.font.SysFont('calibri', 20, True)

soundsX = sounds.get_sounds()


def set_palette(setup, palette, name_of_new_palette, menu_objects, first=False):
    if first:
        old_palette = "emerald"
    else:
        old_palette = setup["palette"]
    palette.current_palette = name_of_new_palette
    palette.palette = palette.get_palette()

    # saving new json
    setup["palette"] = name_of_new_palette
    with open("assets/saves/setup.json", "w") as f:
        json.dump(setup, f, indent=4)

    # iterates over images and sets new palette
    for obj in range(len(menu_objects)):
        for img in menu_objects[obj].images.keys():
            menu_objects[obj].images[img] = palette.swap_image(menu_objects[obj].images[img],
                                                               old_palette, name_of_new_palette)
            menu_objects[obj].images[img].set_colorkey((0, 0, 0))
        menu_objects[obj].display_image = palette.swap_image(menu_objects[obj].display_image,
                                                             old_palette, name_of_new_palette)
        menu_objects[obj].display_image.set_colorkey((0, 0, 0))

    return menu_objects, setup


# function for palette btn
def next_palette(palette):
    palette = palette[0]
    palette.current_palette = next(palette.cycle)
    palette.changed = True
    soundsX["click"].play()


# function for right arrow
def right_arrow(game):
    game = game[0]
    index = game.game_flow["dfs"].index(game.game_flow["df"])
    if index != len(game.game_flow["dfs"]) - 1:
        game.game_flow["df"] = game.game_flow["dfs"][index + 1]
        game.game_flow["df_change"] = True
    soundsX["click"].play()


# function for left arrow
def left_arrow(game):
    game = game[0]
    index = game.game_flow["dfs"].index(game.game_flow["df"])
    if index != 0:
        game.game_flow["df"] = game.game_flow["dfs"][index - 1]
        game.game_flow["df_change"] = True
    soundsX["click"].play()


# input
def activate_edit_text(game):
    game[0].game_flow["ac"] = False
    soundsX["click"].play()


def update_text(menu_objects, setup, game, palette):
    custom_text = font.render(game.game_flow["custom_string"], False,
                              palette.palette["outline-dark"])
    custom_text_hover = font.render(game.game_flow["custom_string"], False,
                                    palette.palette["background"])
    ct_images = {"idle": create_text_sur(custom_text, [20, 20], [100, 100]),
                 "hover": create_text_sur(custom_text_hover, [20, 20], [100, 100])}
    for image in ct_images.keys():
        ct_images[image].set_colorkey((0, 0, 0))

    for item in range(len(menu_objects)):
        if menu_objects[item].on_click == activate_edit_text:
            if menu_objects[item].name == "custom_text":
                menu_objects[item].images = ct_images
                menu_objects[item].display_image = ct_images["hover"]

    # saving json
    setup["custom_num"] = game.game_flow["custom_string"]
    with open("assets/saves/setup.json", "w") as f:
        json.dump(setup, f, indent=4)

    return menu_objects, setup


def create_text_sur(text, pos, size):
    sur = pygame.Surface(size)
    sur.fill((0, 0, 0))
    sur.blit(text, pos)
    return sur


def get_num_circles(palette, size_multiplier=1):
    circle_num = pygame.image.load("assets/images/game/num_circle.png").convert()
    circle_num_hover = pygame.image.load("assets/images/game/num_circle_hover.png").convert()

    circle_num = palette.swap_image(circle_num, "emerald", palette.current_palette)
    circle_num_hover = palette.swap_image(circle_num_hover, "emerald", palette.current_palette)

    nums = [tiny_font.render(str(num), False, palette.palette["outline-dark"]) for num in range(1, 9)]
    for i in range(len(nums)):
        nums[i] = create_text_sur(nums[i], [10, 6], [30, 30])
        nums[i].set_colorkey((0, 0, 0))

    num_dict = {}

    size = 0
    for i in range(len(nums)):
        cn = circle_num.copy()
        cnh = circle_num_hover.copy()

        cn.blit(nums[i], [0, 0])
        cnh.blit(nums[i], [0, 0])

        cn.set_colorkey((0, 0, 0))
        cnh.set_colorkey((0, 0, 0))

        size = int(30 * size_multiplier)
        cn = pygame.transform.scale(cn, [size for _ in range(2)])
        cnh = pygame.transform.scale(cnh, [size for _ in range(2)])

        num_dict[str(i + 1)] = {"idle": cn,
                                "hover": cnh}

    return num_dict, size


def get_images(palette, size):
    circle_num = pygame.image.load("assets/images/game/num_circle.png").convert()
    circle_num_hover = pygame.image.load("assets/images/game/num_circle_hover.png").convert()

    circle_num = palette.swap_image(circle_num, "emerald", palette.current_palette)
    circle_num_hover = palette.swap_image(circle_num_hover, "emerald", palette.current_palette)

    nums = [tiny_font.render(str(num), False, palette.palette["backgroundShade"]) for num in range(1, 9)]
    for i in range(len(nums)):
        nums[i] = create_text_sur(nums[i], [10, 6], [30, 30])
        nums[i].set_colorkey((0, 0, 0))

    num_dict = {}

    for i in range(len(nums)):
        cn = circle_num.copy()
        cnh = circle_num_hover.copy()

        cn.blit(nums[i], [0, 0])
        cnh.blit(nums[i], [0, 0])

        cn.set_colorkey((0, 0, 0))
        cnh.set_colorkey((0, 0, 0))

        cn = pygame.transform.scale(cn, [size for _ in range(2)])
        cnh = pygame.transform.scale(cnh, [size for _ in range(2)])

        num_dict[str(i + 1)] = {"idle": cn,
                                "hover": cnh}

    return num_dict


def get_back_images(palette):
    back_images = {"idle": pygame.image.load("assets/images/game/back.png").convert(),
                   "hover": pygame.image.load("assets/images/game/back_hover.png").convert()}

    for image in back_images.keys():
        back_images[image] = palette.swap_image(back_images[image], "emerald", palette.current_palette)
        back_images[image].set_colorkey((0, 0, 0))

    return back_images


def get_win_image():
    surf = pygame.Surface([500, 550])
    surf.fill((80, 80, 80))
    surf.set_alpha(180)

    text = font.render("Congratulations!", False, (10, 10, 10))
    surf.blit(text, [60, 120])

    return surf


def go_back(args):
    game = args[0]

    game.game_flow["quit"] = True
    soundsX["click"].play()


def change_fs(args):
    args[0].game_flow["change_fs"] = True
    soundsX["click"].play()


def get_tutorial_circle_images(size_multiplier):
    tutorial_circle_images = {"idle": pygame.image.load("assets/images/game/tutorial_circle.png").convert(),
                              "hover": pygame.image.load("assets/images/game/tutorial_circle_hover.png").convert()}

    size = int(30 * size_multiplier)

    for image in tutorial_circle_images.keys():
        tutorial_circle_images[image].set_alpha(120)
        tutorial_circle_images[image].set_colorkey((0, 0, 0))
        tutorial_circle_images[image] = pygame.transform.scale(tutorial_circle_images[image], [size for _ in range(2)])

    return tutorial_circle_images, size


def move_in_tutorial(args):
    args[0].game_flow["tf"] = True


def play_click_sound(args):
    soundsX["click"].play()
