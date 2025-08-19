from manim import *
from contextlib import *
import random, logging, sys, os, re

def CodeVideo(video_name="CodeVideo", interval=0.05, floating_interval=True, floating_camera=True, 
              paragraph_config={'font':'Consolas'}, **kwargs):

    logging.basicConfig(level=logging.INFO)
    config.output_file = video_name

    # check interval
    min_second = 0.0166667
    if floating_interval and interval < min_second-0.01:
        raise ValueError(f"interval is too small, please set a larger value not less than {min_second-0.01}")
    if not floating_interval and interval < min_second:
        raise ValueError(f"interval is too small, please set a larger value not less than {min_second}")

    class code_video(MovingCameraScene):

        # whether the text has chinese characters or punctuation
        def has_chinese(self, text):
            pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uf900-\ufaff]')
            return bool(pattern.search(text))
        
        # no manim output
        @contextmanager
        def _no_manim_output(self):
            manim_logger = logging.getLogger("manim")
            original_manim_level = manim_logger.getEffectiveLevel()
            original_stderr = sys.stderr
            try:
                manim_logger.setLevel(logging.WARNING)
                sys.stderr = open(os.devnull, 'w')
                yield
            finally:
                manim_logger.setLevel(original_manim_level)
                sys.stderr = original_stderr

        # move the camera to the cursor position
        def move_camera_to_cursor(self):
            self.play(
                self.camera.frame.animate.move_to(cursor.get_center()).shift(
                    UP*random.uniform(-0.05,0.05)+LEFT*random.uniform(-0.05,0.05) if floating_camera else 0
                ), 
                run_time=0.2
            )
            self.wait(random.uniform(interval-0.01, interval+0.01) if floating_interval else interval)

        def construct(self):
            """
            ┌───────────────────────────────────┬───────────────────┐
            │ self.successfully_rendered_info() │ line_number, code │
            ├───────────────────────────────────┼───────────────────┤
            │ self.move_camera_to_cursor()      │ cursor            │
            └───────────────────────────────────┴───────────────────┘
            """
            global line_number, code, cursor

            # check arguments
            if {"code_string", "code_file"}.issubset(kwargs):
                raise ValueError("Only one of code_string and code_file can be passed in")
            
            # get code string and check if it contains chinese characters or punctuation
            if "code_string" in kwargs:
                code_strlines = kwargs["code_string"]
                if self.has_chinese(code_strlines):
                    raise ValueError("There are Chinese characters or punctuation in the code, please use English")
            elif "code_file" in kwargs:
                with open(os.path.abspath(kwargs["code_file"]), "r") as f:
                    try:
                        code_strlines = f.read()
                    except UnicodeDecodeError:
                        raise ValueError("There are Chinese characters or punctuation in the code, please use English") from None

            # split each line of code, so that code_strlines can be accessed using code_strlines[line][column]
            code_strlines = code_strlines.split("\n")

            # replace tab with 4 spaces
            if "code_string" in kwargs:
                kwargs["code_string"] = kwargs["code_string"].replace("\t", "    ")
            elif "code_file" in kwargs:
                with open(os.path.abspath(kwargs["code_file"]), "r") as f:
                    kwargs["code_string"] = f.read().replace("\t", "    ")
                    kwargs.pop("code_file")

            # initialize cursor
            cursor_width = 0.005
            cursor = RoundedRectangle(height=0.35, width=cursor_width, corner_radius=cursor_width/2, fill_opacity=1, fill_color=WHITE, color=WHITE)
            
            # initialize code block
            code_block = Code(paragraph_config=paragraph_config, **kwargs)
            window = code_block.submobjects[0] # code window
            line_numbers = code_block.submobjects[1] # line numbers
            code = code_block.submobjects[2] # code

            # occupy block
            # use '#' to occupy, prevent no volume space
            line_number = len(line_numbers)
            kwargs.pop("code_string") # pop code_string parameter, prevent Code class error
            occupy = Code(
                code_string=line_number*(max([len(code[i]) for i in range(line_number)])*'#' + '\n'),
                paragraph_config=paragraph_config,
                **kwargs
            ).submobjects[2]

            code_line_rectangle = SurroundingRectangle(occupy[0], stroke_color=WHITE, stroke_width=0.2)
            
            self.camera.frame.scale(0.3).move_to(occupy[0][0].get_center())
            self.add(window, cursor, line_numbers[0], code_line_rectangle)
            cursor.next_to(occupy[0][0], LEFT, buff=-cursor_width) # cursor move to the left of occupy block
            self.wait()
            
            # traverse code lines
            for line in range(len(code)):
                char_num = len(code[line]) # code line character number
                
                print(f"\033[34mRendering line {line+1}/{len(code)}:\033[0m {code_strlines[line].lstrip()}")
                print(f"      0%|          | 0/{char_num}" if char_num != 0 else f"    100%|##########| 0/0", end='')

                # if the line is empty, move the cursor to the left of the occupy block and wait
                if code_strlines[line] == '':
                    cursor.next_to(occupy[line], LEFT, buff=-cursor_width) # cursor move to the left of occupy block
                    self.move_camera_to_cursor() # move camera to cursor position
                
                code_line_rectangle.set_y(occupy[line].get_y())
                
                self.add(line_numbers[line]) # add line number
                line_y = line_numbers[line].get_y() # line number y coordinate
                
                # traverse code line characters
                is_leading_space = True # whether it is a leading space
                for column in range(char_num):

                    # if it is a leading space, skip
                    if code_strlines[line][column] == ' ' and is_leading_space:
                        pass
                    else:
                        is_leading_space = False

                        char = code[line][column] # code line character
                        occupy_char = occupy[line][column] # occupy block character
                        self.add(char) # add code line character
                        cursor.next_to(occupy_char, RIGHT, buff=0.05) # cursor move to the right of occupy block
                        cursor.set_y(line_y-0.05) # cursor y coordinate in the same line
                        self.move_camera_to_cursor() # move camera to cursor position

                    # output progress
                    percent = int((column+1)/char_num*100)
                    percent_spaces = (4-len(str(percent)))*' '
                    hashtags = percent//10*'#'
                    number = percent%10 if percent%10 != 0 else ''
                    progress_bar_spaces = (10-percent//10 if percent%10 == 0 else 10-percent//10-1)*' '
                    print(f"\r   {percent_spaces}{percent}%|{hashtags}{number}{progress_bar_spaces}| {column+1}/{char_num}", end='')

                print("\n")
                logging.info(f"Successfully rendered line {line+1}")
                print()

            self.wait()
            logging.info("Combining to Movie file.")
            print()

        def render(self, **kwargs):
            with self._no_manim_output():
                super().render(**kwargs)

            quality_map = {
                "high_quality": "1080p60",
                "medium_quality": "720p30",
                "low_quality": "480p15",
                "fourk_quality": "2160p60",
                "twok_quality": "1440p60"
            }
            full_path = os.path.join(
                config.media_dir,
                "videos",
                quality_map[config.quality],
                f"{video_name}.mp4"
            )
            logging.info(f"File ready at '{os.path.abspath(full_path)}'")
            print()
            logging.info(f"Rendered {video_name}\nTyping {sum(len(code[line]) for line in range(line_number))} characters")

    return code_video()
