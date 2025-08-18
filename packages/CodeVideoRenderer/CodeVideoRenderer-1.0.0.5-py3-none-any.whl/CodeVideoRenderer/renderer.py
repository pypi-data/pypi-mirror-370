from manim import *
from contextlib import *
import random, logging, sys, os, re

def CodeVideo(video_name="CodeVideo", speed=0.2, interval=0.05, floating_interval=True, floating_camera=True, 
              paragraph_config={'font':'Consolas'}, **kwargs):

    logging.basicConfig(level=logging.INFO)
    config.output_file = video_name
    class code_video(MovingCameraScene):

        # 判断是否含有中文字符及标点
        def has_chinese(self, text):
            pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uf900-\ufaff]')
            return bool(pattern.search(text))
        
        # 阻止manim输出
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

        # 将相机移动到光标位置
        def move_camera_to_cursor(self):
            self.play(
                self.camera.frame.animate.move_to(cursor.get_center()).shift(UP*random.uniform(-0.05,0.05) if floating_camera else 0), 
                run_time=speed
            )
            self.wait(random.uniform(interval-0.01, interval+0.01) if floating_interval else interval)

        # 渲染完成后输出信息
        def successfully_rendered_info(self):
            logging.info("Combining to Movie file.")
            print()
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

        def construct(self):
            """
            ┌───────────────────────────────────┬───────────────────┐
            │ self.successfully_rendered_info() │ line_number, code │
            ├───────────────────────────────────┼───────────────────┤
            │ self.move_camera_to_cursor()      │ cursor            │
            └───────────────────────────────────┴───────────────────┘
            """
            global line_number, code, cursor

            # 检查参数
            if {"code_string", "code_file"}.issubset(kwargs):
                raise ValueError("Only one of code_string and code_file can be passed in")
            
            # 获取代码字符串并检测是否包含中文字符或标点
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

            # 分割每行代码，使code_strlines可以使用code_strlines[line][column]的方式来访问字符
            code_strlines = code_strlines.split("\n")

            # 将Tab替换为4个空格
            if "code_string" in kwargs:
                kwargs["code_string"] = kwargs["code_string"].replace("\t", "    ")
            elif "code_file" in kwargs:
                with open(os.path.abspath(kwargs["code_file"]), "r") as f:
                    kwargs["code_string"] = f.read().replace("\t", "    ")
                    kwargs.pop("code_file")

            # 初始化光标
            cursor_width = 0.005
            cursor = RoundedRectangle(height=0.35, width=cursor_width, corner_radius=cursor_width/2, fill_opacity=1, fill_color=WHITE, color=WHITE)
            
            # 初始化代码块
            code_block = Code(paragraph_config=paragraph_config, **kwargs)
            window = code_block.submobjects[0] # 代码窗口
            line_numbers = code_block.submobjects[1] # 行号
            code = code_block.submobjects[2] # 代码

            # 占用块
            line_number = len(line_numbers)
            kwargs.pop("code_string") # 弹出code_string参数，防止Code类报错
            occupy = Code(
                code_string=line_number*(max([len(code[i]) for i in range(line_number)])*'#' + '\n'), # 使用'#'占位，防止无体积的空格
                paragraph_config=paragraph_config,
                **kwargs
            ).submobjects[2]
            
            self.camera.frame.scale(0.3).move_to(occupy[0][0].get_center())
            self.add(window, cursor, line_numbers[0]) # 添加代码窗口、光标、行号
            cursor.next_to(occupy[0][0], LEFT, buff=-cursor_width) # 光标移动到占用块左侧
            self.wait()
            
            # 遍历代码行
            for line in range(len(code)):
                char_num = len(code[line]) # 代码行字符数
                print(f"Rendering line {line+1}:   0%|          | 0/{char_num}" if char_num != 0 else f"Rendering line {line+1}: 100%|##########| 0/0", end='')

                # 如果是空格直接等待循环将光标移动到行首
                if code_strlines[line] == '':
                    cursor.next_to(occupy[line], LEFT, buff=-cursor_width) # 光标移动到占用块左侧
                    self.move_camera_to_cursor() # 移动相机到光标位置
                
                self.add(line_numbers[line]) # 添加行号
                line_y = line_numbers[line].get_y() # 行号y坐标
                
                # 遍历代码行字符
                is_leading_space = True # 是否是前导空格
                for column in range(char_num):

                    # 如果是前导空格，跳过
                    if code_strlines[line][column] == ' ' and is_leading_space:
                        pass
                    else:
                        is_leading_space = False

                        char = code[line][column] # 代码行字符
                        occupy_char = occupy[line][column] # 占用块字符
                        self.add(char) # 添加代码行字符
                        cursor.next_to(occupy_char, RIGHT, buff=0.05) # 光标移动到占用块右侧
                        cursor.set_y(line_y-0.05) # 光标y坐标在同一行不变
                        self.move_camera_to_cursor() # 移动相机到光标位置
                    
                    # 输出进度
                    percent = int((column+1)/char_num*100)
                    print(f"\rRendering line {line+1}:{(4-len(str(percent)))*' '}{percent}%|{percent//10*'#'}{percent%10 if percent%10 != 0 else ''}{(10-percent//10 if percent%10 == 0 else 10-percent//10-1)*' '}| {column+1}/{char_num}", end='')

                print("\n")
                logging.info(f"Successfully rendered\nline {line+1}")
                print()

            self.wait()
            self.successfully_rendered_info()

        def render(self, **kwargs):
            with self._no_manim_output():
                super().render(**kwargs)

    return code_video()
