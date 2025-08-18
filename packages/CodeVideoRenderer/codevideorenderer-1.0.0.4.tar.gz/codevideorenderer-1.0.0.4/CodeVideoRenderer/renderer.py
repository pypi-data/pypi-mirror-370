from manim import *
from contextlib import *
import random, logging, sys, os

def CodeVideo(video_name="CodeVideo", speed=0.2, interval=0.05, floating_interval=True, floating_pos=True, 
              paragraph_config={'font':'Consolas'}, **kwargs):
    logging.basicConfig(level=logging.INFO)
    config.output_file = video_name
    class code_video(MovingCameraScene):

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

        def move_camera_to_cursor(self):
            self.play(
                self.camera.frame.animate.move_to(cursor.get_center()).shift(UP*random.uniform(-0.05,0.05) if floating_pos else 0), 
                run_time=speed
            )
            self.wait(random.uniform(interval-0.01, interval+0.01) if floating_interval else interval)

        def construct(self):
            global cursor, line_number, code
            cursor = RoundedRectangle(height=0.5, width=0.01, corner_radius=0.005, 
                                      fill_opacity=1, fill_color=WHITE, color=WHITE)
            
            code_block = Code(paragraph_config=paragraph_config, **kwargs)
            window = code_block.submobjects[0]
            line_numbers = code_block.submobjects[1]
            code = code_block.submobjects[2]

            line_number = len(line_numbers)
            kwargs.pop("code_string", None)
            occupy = Code(
                code_string=line_number*(max([len(code[i]) for i in range(line_number)])*'#' + '\n'),
                paragraph_config=paragraph_config,
                **kwargs
            ).submobjects[2]
            
            self.camera.frame.scale(0.25).move_to(code[0][0].get_center())
            self.add(window, cursor, line_numbers[0])

            for line in range(len(code)):
                char_num = len(code[line])
                print(f"Rendering line {line+1}:   0%|          | 0/{char_num}" if char_num != 0 else f"Rendering line {line+1}: 100%|##########| 0/{char_num}", end='')

                cursor.next_to(occupy[line], LEFT, buff=-0.01)
                self.add(line_numbers[line])
                self.move_camera_to_cursor()
                line_y = line_numbers[line].get_y()
                
                for column in range(char_num):
                    char = code[line][column]
                    occupy_char = occupy[line][column]
                    self.add(char)
                    cursor.next_to(occupy_char, RIGHT, buff=0.05)
                    cursor.set_y(line_y)
                    self.move_camera_to_cursor()

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
