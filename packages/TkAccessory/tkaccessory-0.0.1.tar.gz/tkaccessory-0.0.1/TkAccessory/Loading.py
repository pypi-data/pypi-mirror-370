from customtkinter import CTkCanvas
from math import sin , cos , radians

class TkAtomicLoading:
    def __init__(self,canvas : CTkCanvas,tag : str,position : tuple[int,int],diagonal : int,bg_color : str = "darkblue",text : str = "CircularProgressBar",text_angle : int = 0,text_font = None,text_color : str = "white",loading_colors : tuple[str] = ["#0011ff","#0011ff","#303efc","#303efc","#5762ff","#5762ff"],loading_radiuses : tuple[int] = [1,2,3,4,5,6],speed : int = 5):
        if len(loading_colors) != len(loading_radiuses):
            raise ValueError("loading_colors ,and radiuses must have the same lenght")

        self.speed = speed
        self.canvas = canvas
        self.tag = tag
        self.position = position
        self.diagonal = diagonal
        self.colors = loading_colors
        self.circle_radiuses = loading_radiuses
        self.bg = bg_color
        self.color = text_color
        self.values = []

        self.text_angle = text_angle
        self.text_font = text_font
        self.text = text

        self.canvas.create_aa_circle(self.position[0],self.position[1],diagonal // 2,fill=self.bg)

        for i in range(len(loading_colors)):
            value = i * (360 / len(loading_colors))
            self.values.append(value)
            self.canvas.create_aa_circle(self.position[0]+(cos(radians(value)) * (self.diagonal / 2)),self.position[1]-(sin(radians(value)) * (self.diagonal / 2)),int(self.circle_radiuses[i]),fill=loading_colors[i],tags=f"circles-{self.tag}")

        self.canvas.create_text(self.position[0],self.position[1],anchor="center",fill=self.color,justify="center",angle=self.text_angle,font=self.text_font,text=text,tags=f"text-{self.tag}")

    def move(self,text : str | None = None,loading_colors : tuple[str] | None = None,loading_radiuses : tuple[int] | None = None):
        self.canvas.delete(f"circles-{self.tag}")
        self.canvas.delete(f"text-{self.tag}")

        if text == None:
            text = self.text
        
        if loading_colors == None:
            loading_colors = self.colors

        if loading_radiuses == None:
            loading_radiuses = self.circle_radiuses

        if len(loading_colors) != len(loading_radiuses):
            raise ValueError("loading_colors ,and radiuses must have the same lenght")

        for i in range(len(self.values)):
            self.canvas.create_aa_circle(self.position[0]+(cos(radians(self.values[i] + self.speed)) * (self.diagonal / 2)),self.position[1]-(sin(radians(self.values[i] + self.speed)) * (self.diagonal / 2)),int(loading_radiuses[i]),fill=loading_colors[i],tags=f"circles-{self.tag}")
            self.values[i] += self.speed

        self.canvas.create_text(self.position[0],self.position[1],anchor="center",fill=self.color,justify="center",angle=self.text_angle,font=self.text_font,text=text,tags=f"text-{self.tag}")