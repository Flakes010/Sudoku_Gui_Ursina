from ursina import *
from ursina import curve
from time import gmtime, strftime
from random import choice
from sudoku_boards import *


empty_board = []
boxes = []


app = Ursina(borderless=True)
window.title = 'Sudoku App'


class SudokuCubes(Entity):
    board = []
    solved_board = board.copy()
    

    def __init__(self, pos, num, selectable = False, **kwargs):
        super().__init__()
        self.pos = pos
        self.num = num
        self.selectable = selectable
        self.model = 'quad'
        self.collider = 'box'
        self.solved_num = '0'
        self.color = color.white
        self.position = Vec3(pos, 8)
        self.text_entity = Text(text=str(num), position=self.position/11.5)
        self.text_entity.y += .02
        self.text_entity.x -= .015
        self.text_entity.color = color.black
        self.text_entity.scale = 2.2
        self.try_text = Text(text=" ", position=self.position/11.5)
        self.try_text.y += .02
        self.try_text.x -= .015
        self.try_text.color = color.gray
        self.try_text.scale = 2.2
        self.scale = 1
        self.on_click = self.select_box
        points = [Vec3(pos[0]-.5,pos[1]-.5,8), Vec3(pos[0]-.5,pos[1]+.5,8), Vec3(pos[0]+.5,pos[1]+.5,8),
                    Vec3(pos[0]+.5,pos[1]-.5,8), Vec3(pos[0]-.5,pos[1]-.5,8)]
        self.border = Entity(model=Mesh(vertices=points, mode='line', thickness=1), color=color.black)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def select_box(self):
        
        for box in boxes:
            if self.color != color.red or self.color != color.green :
                box.color = color.white
        
        if self.text_entity.text == ' ':
            click_sound.click.play()
            self.color = rgb(180, 213, 254)
            for box in boxes:
                box.selectable = False
            self.selectable = True
        
        
    def input(self, key):
        if (key in '123456789') and self.selectable:
            self.try_text.text = key
        
        if key == 'enter' and self.selectable:
            self.text_entity.text = self.try_text.text
            if self.text_entity.text == str(self.solved_num):
                correct_sound.correct.play()
                self.selectable = False
                self.color = rgb(0, 197, 144)
                self.animate("rotation_y", 360, 1, curve=curve.in_out_bounce_boomerang)
                self.text_entity.animate("rotation_x", 360, 1, curve=curve.in_out_bounce_boomerang)
                self.text_entity.color = color.black
                
            else:
                false_sound.false.volume = 5
                false_sound.false.play()
                print(self)
                self.selectable = True
                self.color = rgb(162, 74, 92)
                self.shake()
                self.text_entity.text = self.try_text.text
                self.text_entity.text = " "
            
            self.try_text.text = " "
        
        if (key == 'backspace' or key == 'delete'):
            self.try_text.text = " "
        
        
    def find_empty(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == " ":
                    return (i, j) #row, column

    def valid(self, num, pos):
        for i in range(len(self.board[0])):
            if num == self.board[pos[0]][i] and i != pos[1]:
                return False

        for i in range(len(self.board)):
            if num == self.board[i][pos[1]] and i != pos[0]:
                return False

        rangeX = (pos[1] // 3) * 3 # 0, 3 or 6
        rangeY = (pos[0] // 3) * 3 # 0, 3 or 6

        for i in range(rangeY, rangeY + 3):
            for j in range(rangeX, rangeX + 3):
                if self.board[i][j] == num and (i, j) != num:
                    return False

        return True

    def solve(self, new_board=False):
        find = self.find_empty()

        if not find:
            return True
        else:
            row, column = find

        for i in range(1,10):
            if self.valid(i, (row, column)):
                if new_board:
                    self.solved_board[row][column] = i
                    if self.solve():
                        return True

                    self.solved_board[row][column] = " "

                else:
                    self.board[row][column] = i

                    if self.solve():
                        return True

                    self.board[row][column] = " "

        return False

    def zero_empty(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == 0:
                    self.board[i][j] = " "
                    
        return self.board
    

class Solve_Button(Button):
    def __init__(self, **kwargs):
        super().__init__()

        self.scale = (0.2, 0.05)
        self.position = Vec3(0.6,0,0)
        self.color = color.white
        self.new_text = Text(text='Solve!', position=Vec3(0.56,0.01,-1), font='assets/Inter.ttf', color=color.black, eternal=True)
        self.eternal = True

        for key, value in kwargs.items():
            setattr(self, key, value)


class Timer_Clock(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.run = True
        self.text_obj = Text(text=strftime("%M:%S", gmtime(0)), eternal=True)
        self.text_obj.font = 'assets/Inter.ttf'
        self.text_obj.scale = 1.8
        self.text_obj.position = Vec3(.526,.153,0)
        self.text_obj.color = color.black
        self.text_obj.eternal = True
        self.start = time.time()

        self.circle = Entity(model = 'quad', texture='Circle.png', scale=1.4, position=(4.9,1.1), eternal=True)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        if self.run:
            self.seconds = time.time() - self.start
            self.text_obj.text = strftime("%M:%S", gmtime(self.seconds))


class Sound():
    def __init__(self, audio, **kwargs):
        self.audio = audio
        if self.audio == 'game_music': 
            self.game_music = Audio("sound/main_music.wav", loop=True) 
            self.game_music.volume = 0.4
        elif self.audio == 'click': 
            self.click = Audio("sound/click.wav", autoplay=False)
            self.click.volume = 1.5
        elif self.audio == 'false':
            self.false = Audio("sound/false.wav", autoplay=False)
        elif self.audio == 'correct':
            self.correct = Audio("sound/correct.wav", autoplay=False)

        for key, value in kwargs.items():
            setattr(self, key, value)

        
class Grid(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.border_points = [Vec3(-4,-4,5), Vec3(-4,4,5), Vec3(4,4,5), Vec3(4,-4,5), Vec3(-4,-4,5)]
        self.mid_points = [Vec3(-4,-1.3,5), Vec3(4,-1.3,5)]
        self.mid_points2 = [Vec3(-4,1.3,5), Vec3(4,1.3,5)]
        self.mid_points3 = [Vec3(-1.3,-4,5), Vec3(-1.3,4,5)]
        self.mid_points4 = [Vec3(1.3,-4,5), Vec3(1.3,4,5)]

        for key, value in kwargs.items():
            setattr(self, key, value)

    def back(self):
        click_sound.click.play()
        self.play_time = game_music.game_music.time
        self.timer.circle.eternal = False
        self.timer.text_obj.eternal = False
        self.button.eternal = False
        self.button.new_text.eternal = False
        
        for line in self.grid:
            line.eternal = False
            line.visible = False
        
        scene.clear()
        show_menu(no_music=True)

    
    def solve_and_show(self):
        click_sound.click.play()
        kup = SudokuCubes((99,99), 1)
        kup.visible = False
        kup.text_entity.visible = False
        scene.clear()
        self.timer.run = False
        kup.solve()
        self.bg = Entity(model = 'quad', texture = 'bg_sudoku.png', scale = (22.4,12.8), z = 10)
        self.create_box()

    def create_box(self):
        c = 0
        for i in range(-4,5):
            for j in range(-4,5):  
                kup = SudokuCubes((i,j), SudokuCubes.board[8-(j+4)][i+4])
                c += 1
                boxes.append(kup)
                kup.scale = 0.98
                kup.zero_empty()
                if kup.num == 0:
                    print(kup.num)

    def show_grid(self):
        self.create_box()
        
        self.bg_quad = Entity(model = 'quad', color = color.black, z=8.1, scale=9)
        self.border = Entity(model=Mesh(vertices=self.border_points, mode='line', thickness=8), color=color.black, eternal=True)
        self.mid = Entity(model=Mesh(vertices=self.mid_points, mode='line', thickness=5), color=color.black, eternal=True)
        self.mid2 = Entity(model=Mesh(vertices=self.mid_points2, mode='line', thickness=5), color=color.black, eternal=True)
        self.mid3 = Entity(model=Mesh(vertices=self.mid_points3, mode='line', thickness=5), color=color.black, eternal=True)
        self.mid4 = Entity(model=Mesh(vertices=self.mid_points4, mode='line', thickness=5), color=color.black, eternal=True)
        self.grid = [self.border, self.mid, self.mid2, self.mid3, self.mid4]

        self.sudoku_bg = Entity(model = 'quad', texture = 'bg_sudoku.png', scale = (22.4,12.8), z = 10)
        self.arrow = Entity(model = 'quad', collider='box', texture = 'arrow.png', position = (-6.5,-3.4), scale = .7, eternal = True)
        self.arrow.on_click = self.back

        self.button = Solve_Button()
        self.button.on_click = self.solve_and_show

        kup = SudokuCubes((99,99), 1)
        kup.visible = False
        kup.text_entity.visible = False
        kup.solve(new_board=True)

        self.timer = Timer_Clock()
        
        index = 0

        for i in range(-4,5):
            for j in range(-4,5): 
                boxes[index].solved_num = SudokuCubes.board[8-(j+4)][i+4]
                index += 1 

buttons = []
glows = []

class Menu_Buttons(Entity):
    
    def __init__(self, button_type, **kwargs):
        super().__init__()
        
        self.button_type = button_type
        self.model = 'quad'
        self.collider = 'box'
        self.glow_scale = (3.4, 1.9)
        self.default_scale = 0
        self.glow = 0
        self.lock = True

        self.on_click = self.selected

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.button_type == 'bg':
            self.texture = 'bg_png.png'
            self.scale = (15,8.5)
        elif self.button_type == 'easy':
            self.default_scale = (1.8, 0.7)
            self.texture = 'Easy_button.png'
            self.position = Vec3(-2.3, -2.1, -1)
            self.scale = self.default_scale
            self.easy_glow = Entity(model='quad', collider='box', texture='Easy_glow.png', scale=self.glow_scale, position=Vec3(-2.3, -2.1, -0.9), visible=False)
            self.glow = self.easy_glow
            buttons.append(self)
            glows.append(self.easy_glow)

            
        elif self.button_type == 'medium':
            self.default_scale = (1.8, 0.7)
            self.texture = 'Medium_button.png'
            self.position = Vec3(-.2, -2.1, -1)
            self.scale = self.default_scale
            self.medium_glow = Entity(model='quad', collider='box', texture='Medium_glow.png', scale=self.glow_scale, position=Vec3(-.2, -2.1, -0.9), visible=False)
            self.glow = self.medium_glow
            buttons.append(self)
            glows.append(self.medium_glow)
        elif self.button_type == 'hard':
            self.default_scale = (1.8, 0.7)
            self.texture = 'Hard_button.png'
            self.position = Vec3(1.95, -2.1, -1)
            self.scale = self.default_scale
            self.hard_glow = Entity(model='quad', collider='box', texture='Hard_glow.png', scale=self.glow_scale, position=Vec3(1.9, -2.1, -0.9), visible=False)
            self.glow = self.hard_glow
            buttons.append(self)
            glows.append(self.hard_glow)
        elif self.button_type == 'create':
            self.default_scale = (2, 1.1)
            self.texture = 'Create_button.png'
            self.position = Vec3(-0.15, -3.2, -1)
            self.scale = self.default_scale
            self.create_glow = Entity(model='quad', collider='box', texture='Create_glow.png', scale=self.glow_scale, position=Vec3(-0.15, -3.2, -0.9), visible=False)
        elif self.button_type == 'music':
            self.default_scale = .8
            self.texture = 'music.png'
            self.position = Vec3(-6, -3, -1)
            self.scale = self.default_scale
            self.stick = Entity(model='quad', texture='stick.png', z=-1, position=Vec3(-6, -3, -1.01), scale=self.default_scale, visible=False)


    def update(self):
        if self.hovered and self.button_type == 'easy' and self.lock:
            self.easy_glow.visible = True
        elif self.hovered == False and self.button_type == 'easy' and self.lock:
            self.easy_glow.visible = False
        
        if self.hovered and self.button_type == 'medium' and self.lock:
            self.medium_glow.visible = True
        elif self.hovered == False and self.button_type == 'medium' and self.lock:
            self.medium_glow.visible = False

        if self.hovered and self.button_type == 'hard' and self.lock:
            self.hard_glow.visible = True
        elif self.hovered == False and self.button_type == 'hard' and self.lock:
            self.hard_glow.visible = False

        if self.hovered and self.button_type == 'create' and self.lock:
            self.create_glow.visible = True
        elif self.hovered == False and self.button_type == 'create' and self.lock:
            self.create_glow.visible = False


    def selected(self):
        click_sound.click.play()
        if self.button_type not in ('create', 'bg', 'music'):
            for button in buttons:
                button.scale = self.default_scale
                button.glow.scale = self.glow_scale
                button.lock = True
            for glow in glows:
                glow.visible = False

            self.glow.visible = True
            self.lock = False

            self.glow.scale_x = self.glow.scale_x/10*12
            self.glow.scale_y = self.glow.scale_y/10*12
            self.scale_x = self.scale_x/10*12
            self.scale_y = self.scale_y/10*12

        if self.button_type == 'easy':
            SudokuCubes.board = choice(easy_boards)
            SudokuCubes.solved_board = SudokuCubes.board.copy()
        elif self.button_type == 'medium':
            SudokuCubes.board = choice(medium_boards)
            SudokuCubes.solved_board = SudokuCubes.board.copy()
        elif self.button_type == 'hard':
            SudokuCubes.board = choice(hard_boards)
            SudokuCubes.solved_board = SudokuCubes.board.copy()

        if self.button_type == 'music':
            if self.stick.visible == True:
                self.stick.blink(value=color.clear, duration=.3, delay=0, curve=curve.in_expo_boomerang)
                self.blink(value=color.clear, duration=.2, delay=0, curve=curve.in_expo_boomerang)
                self.stick.visible = False
                game_music.game_music.volume = 1
            elif self.stick.visible == False:
                self.stick.blink(value=color.clear, duration=.3, delay=0, curve=curve.in_expo_boomerang)
                self.blink(value=color.clear, duration=.2, delay=0, curve=curve.in_expo_boomerang)
                self.stick.visible = True
                game_music.game_music.volume = 0


        if self.button_type == 'create' and len(SudokuCubes.board) == 9:
            self.blink(value=color.clear, duration=.1, delay=0, curve=curve.in_expo_boomerang)
            self.start = game_music.game_music.time
            scene.clear()
            print("start", self.start)
            game_music.game_music.stop()
            game_music.game_music.play(int(self.start))
            grid = Grid()
            grid.show_grid()
            


def show_menu(no_music=False):
    global game_music, click_sound, correct_sound, false_sound
    if no_music == False:    
        game_music = Sound('game_music')
    click_sound = Sound('click')
    correct_sound = Sound('correct')
    false_sound = Sound('false')
    bg = Menu_Buttons('bg')
    easy_button = Menu_Buttons('easy')
    medium_button = Menu_Buttons('medium')
    hard_button = Menu_Buttons('hard')
    create_button = Menu_Buttons('create')
    music_button = Menu_Buttons('music')
    

show_menu()
app.run()
