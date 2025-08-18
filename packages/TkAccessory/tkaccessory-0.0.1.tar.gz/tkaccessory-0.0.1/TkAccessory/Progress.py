from customtkinter import CTkCanvas
from math import sin , cos , radians

class TkCircularProgress:
    def __init__(self,canvas : CTkCanvas,tag : str,position : tuple[int,int],diagonal : int,line_width : int = 8,start_value : float = 0,text : str = "CircularProgressBar",text_angle : int = 0,text_font = None,text_color : str = "white",progress_color : str = "blue",bg_color : str = "darkblue",fg_color : str = "lightblue",head_color_start : str = "blue",head_color_end : str = "blue"):
        if not (start_value <= 100) or not (start_value >= 0):
            raise ValueError("Invalid value passed !! ,circular progress bar value must be between 0 to 100")
        
        self.canvas = canvas
        self.value = start_value * (360/100)
        self.width = line_width
        self.diagonal = diagonal
        self.position = position
        self.tag = tag

        self.bg = bg_color
        self.fg = fg_color
        self.color = text_color
        self.prog_color = progress_color
        self.head_color_start = head_color_start
        self.head_color_end = head_color_end

        self.text_angle = text_angle
        self.text_font = text_font
        self.text = text

        self.canvas.create_aa_circle(self.position[0],self.position[1],(self.diagonal//2)+(self.width//2 + 5),fill=self.bg)
        self.canvas.create_aa_circle(self.position[0],self.position[1],(self.diagonal//2)-(self.width//2 + 5),fill=self.fg)
        self.canvas.create_text(self.position[0],self.position[1],anchor="center",fill=self.color,justify="center",angle=self.text_angle,font=self.text_font,text=text,tags=f"text-{self.tag}")

        self.canvas.after(1, lambda : self.set(start_value))

    def set(self,value : float,text : str | None = None):
        if not (value >= 0) or not (value <= 100):
            raise ValueError("Invalid value passed !! ,circular progress bar value must be between 0 to 100") 

        self.value = value * (360/100)

        self.canvas.delete(f"progress-{self.tag}")
        self.canvas.delete(f"progress-circle-{self.tag}")
        self.canvas.delete(f"text-{self.tag}")

        if text == None:
            text = self.text

        self.canvas.create_arc((self.position[0] - (self.diagonal // 2),self.position[1] - (self.diagonal // 2),self.position[0] + (self.diagonal // 2),self.position[1] + (self.diagonal // 2)),fill=self.prog_color,start=0,extent=self.value,outline=self.prog_color,style="arc",width=self.width,tags=f"progress-{self.tag}")
        self.canvas.create_aa_circle(self.position[0]+(cos(radians(self.value)) * (self.diagonal/2)),self.position[1]-(sin(radians(self.value)) * (self.diagonal/2)),self.width//2,fill=self.head_color_end,tags=f"progress-circle-{self.tag}")
        self.canvas.create_aa_circle(self.position[0]+(self.diagonal // 2),self.position[1],self.width//2,fill=self.head_color_start,tags=f"progress-circle-{self.tag}")
        self.canvas.create_text(self.position[0],self.position[1],anchor="center",fill=self.color,justify="center",angle=self.text_angle,font=self.text_font,text=text,tags=f"text-{self.tag}")


class CustomTkCircularProgress(TkCircularProgress):
    def __init__(self,canvas : CTkCanvas,tag : str,position : tuple[int,int],diagonal : int,line_width : int = 8,start_value : float = 0,text : str = "CircularProgressBar",text_angle : int = 0,text_font = None,text_color : str = "white", progress_colors : tuple[str] = ["#0011ff","#303efc","#5762ff"],bg_color : str = "darkblue",fg_color : str = "lightblue",head_color_start : str = "#0011ff",head_color_end : str = "#5762ff"):
        if len(progress_colors) == 0:
            raise ValueError("Must insert at least one color for progress bar")

        self.colors = progress_colors
        self.values = []

        for i in range(len(self.colors)-1):
            self.values.append((i+1) * (start_value / len(self.colors)))

        super().__init__(canvas, tag, position, diagonal, line_width, start_value, text, text_angle, text_font, text_color, progress_colors[-1], bg_color, fg_color, head_color_start, head_color_end)

    def set(self, value : float, text : str | None = None):
        super().set(value, text)

        for i in range(len(self.values)-1,-1,-1):
            self.canvas.create_arc((self.position[0] - (self.diagonal // 2),self.position[1] - (self.diagonal // 2),self.position[0] + (self.diagonal // 2),self.position[1] + (self.diagonal // 2)),fill=self.colors[i],outline=self.colors[i],start=0,extent=self.values[i],style="arc",width=self.width,tags=f"progress-{self.tag}")
            self.values[i] = (i+1) * (self.value / len(self.colors))