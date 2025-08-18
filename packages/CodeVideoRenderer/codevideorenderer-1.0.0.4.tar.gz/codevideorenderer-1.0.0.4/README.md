本库用于渲染并生成输入代码的视频，视频视角跟随光标移动。

# 说明

使用`manim`进行动画渲染，使用前请确保`manim`能够正常运行。

# 如何使用

本库提供`CodeVideo`函数，你可以使用它创建一个视频对象。参数如下：

```python
CodeVideo(video_name="CodeVideo", speed=0.2, interval=0.05, floating_interval=True, 
          floating_pos=True, paragraph_config={'font':'Consolas'}, **kwargs)
```

## 参数说明

`video_name`：用于设置视频名称，**必须**为字符串类型。

`speed`：用于设置每个字符停留时间（秒），**必须**为数值类型。

`interval`：用于设置每个字符之间的间隔（秒），**必须**为数值类型。

`floating_interval`：用于设置间隔是否上下浮动，如果为`True`则间隔会上下浮动0.01秒。

`floating_pos`：用于设置镜头是否上下浮动，如果为`True`则镜头会在**上方0.05单位长度**和**下方0.05单位长度**间上下浮动。

`paragraph_config`：Manim原版参数，原设置为`None`，更改为常用编程字体`Consolas`。

`**kwargs`：可以传入Manim原版`Code`代码块中的其余参数，详见[Code](https://docs.manim.community/en/stable/reference/manim.mobject.text.code_mobject.Code.html#)。

## 生成视频

你可以对`CodeVideo`对象使用 `render`方法进行视频生成，你可以在终端查看视频的保存位置。

# 示例

```python
from CodeVideoRenderer import *
video = CodeVideo(code_string="print('Hello World!')", language='python')
video.render()
```

## 渲染结果

![渲染结果](https://s3.bmp.ovh/imgs/2025/08/16/d0dcac60fc26b629.gif)
