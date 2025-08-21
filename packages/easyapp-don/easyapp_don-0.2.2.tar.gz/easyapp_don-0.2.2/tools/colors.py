"""
These are colors and themes for you. Specially, WC's sons can print text colorful.
"""
import os
import sys
from typing import Callable,ClassVar,Any,Tuple,TypeVar,Set,Optional,Union
class WC:

    if sys.platform.startswith("win"):
        os.system("color")
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALIC = "\033[3m"
    txt=""
    @classmethod
    def color(cls,text,*styles):

        code="".join(styles)
        print(f"{code}{text}{cls.RESET}")
    @classmethod
    def red(cls,text=txt):

        cls.color(text,cls.RED)
    @classmethod
    def green(cls,text=txt):

        cls.color(text,cls.GREEN)
    @classmethod
    def blue(cls,text=txt):

        cls.color(text,cls.BLUE)
    @classmethod
    def yellow(cls,text=txt):

        cls.color(text,cls.YELLOW)
    @classmethod
    def bold_red(cls,text=txt):

        cls.color(text,cls.BOLD,cls.RED)
    @classmethod
    def line_blue(cls,text=txt):

        cls.color(text,cls.UNDERLINE,cls.BLUE)
    @classmethod
    def magenta(cls, text=txt):

        cls.color(text, cls.MAGENTA)
    @classmethod
    def black(cls, text=txt):

        cls.color(text, cls.BLACK)
    @classmethod
    def cyan(cls, text=txt):

        cls.color(text, cls.CYAN)
    @classmethod
    def white(cls, text=txt):

        cls.color(text, cls.WHITE)
    @classmethod
    def bold(cls, text=txt):

        cls.color(text, cls.BOLD)
    @classmethod
    def line(cls, text=txt):

        cls.color(text, cls.UNDERLINE)
    @classmethod
    def italic(cls, text=txt):

        cls.color(text, cls.ITALIC)
    @classmethod
    def bg_black(cls, text=txt):

        cls.color(text, cls.BG_BLACK)
    @classmethod
    def bg_red(cls, text=txt):

        cls.color(text, cls.BG_RED)
    @classmethod
    def bg_green(cls, text=txt):

        cls.color(text, cls.BG_GREEN)
    @classmethod
    def bg_yellow(cls, text=txt):

        cls.color(text, cls.BG_YELLOW)
    @classmethod
    def bg_blue(cls, text=txt):

        cls.color(text, cls.BG_BLUE)
ColorTuple=Tuple[Union[float,int],Union[float,int],Union[float,int],Union[float,int]]
RED1=(0.9,0.2,0.2,1)
RED2=(0.95,0.1,0.1,1)
RED3=(1,0.1,0.1,1)
RED4=(1,0,0,1)
RED5=(0.9,0,0,1)
RED6=(0.8,0,0,1)
RED7=(0.7,0,0,1)
RED8=(0.6,0,0,1)
RED9=(0.5,0,0,1)
RED10=(0.4,0,0,1)
RED11=(0.3,0,0,1)
RED12=(0.2,0,0,1)
RED13=(0.15,0,0,1)
RED14=(0.1,0,0,1)
RED15=(0.08,0,0,1)
RED16=(0.05,0,0,1)
RED17=(0.03,0,0,1)
RED18=(0.02,0,0,1)

ORANGE1=(1,0.7,0.2,1)
ORANGE2=(1,0.65,0.1,1)
ORANGE3=(1,0.6,0,1)
ORANGE4=(1,0.55,0,1)
ORANGE5=(1,0.5,0,1)
ORANGE6=(1,0.45,0,1)
ORANGE7=(1,0.4,0,1)
ORANGE8=(0.95,0.35,0,1)
ORANGE9=(0.9,0.3,0,1)
ORANGE10=(0.85,0.25,0,1)
ORANGE11=(0.8,0.2,0,1)
ORANGE12=(0.75,0.15,0,1)
ORANGE13=(0.7,0.15,0,1)
ORANGE14=(0.65,0.1,0,1)
ORANGE16=(0.55,0.08,0,1)
ORANGE17=(0.5,0.05,0,1)
ORANGE18=(0.45,0.05,0,1)

YELLOW1=(1,1,0.7,1)
YELLOW2=(1,1,0.5,1)
YELLOW3=(1,1,0.3,1)
YELLOW4=(1,1,0.1,1)
YELLOW5=(1,1,0,1)
YELLOW6=(1,0.95,0,1)
YELLOW7=(1,0.9,0,1)
YELLOW8=(1,0.85,0,1)
YELLOW9=(1,0.8,0,1)
YELLOW10=(1,0.75,0,1)
YELLOW11=(1,0.7,0,1)
YELLOW12=(0.95,0.65,0,1)
YELLOW13=(0.9,0.6,0,1)
YELLOW14=(0.85,0.55,0,1)
YELLOW15=(0.8,0.5,0,1)
YELLOW16=(0.75,0.45,0,1)
YELLOW17=(0.7,0.4,0,1)
YELLOW18=(0.65,0.35,0,1)

GREEN1=(0.2,1,0.2,1)
GREEN2=(0.1,1,0.1,1)
GREEN3=(0,1,0,1)
GREEN4=(0,0.95,0,1)
GREEN5=(0,0.9,0,1)
GREEN6=(0,0.85,0,1)
GREEN7=(0,0.8,0,1)
GREEN8=(0,0.75,0,1)
GREEN9=(0,0.7,0,1)
GREEN10=(0,0.65,0,1)
GREEN11=(0,0.6,0,1)
GREEN12=(0,0.55,0,1)
GREEN13=(0,0.5,0,1)
GREEN14=(0,0.45,0,1)
GREEN15=(0,0.4,0,1)
GREEN16=(0,0.35,0,1)
GREEN17=(0,0.3,0,1)
GREEN18=(0,0.25,0,1)

BLUE1=(0.2,0.2,1,1)
BLUE2=(0.1,0.1,1,1)
BLUE3=(0,0,1,1)
BLUE4=(0,0,0.95,1)
BLUE5=(0,0,0.9,1)
BLUE6=(0,0,0.85,1)
BLUE7=(0,0,0.8,1)
BLUE8=(0,0,0.75,1)
BLUE9=(0,0,0.7,1)
BLUE10=(0,0,0.65,1)
BLUE11=(0,0,0.6,1)
BLUE12=(0,0,0.55,1)
BLUE13=(0,0,0.5,1)
BLUE14=(0,0,0.45,1)
BLUE15=(0,0,0.4,1)
BLUE16=(0,0,0.35,1)
BLUE17=(0,0,0.3,1)
BLUE18=(0,0,0.25,1)

INDIGO1=(0.4,0.2,1,1)
INDIGO2=(0.35,0.15,1,1)
INDIGO3=(0.3,0.1,1,1)
INDIGO4=(0.25,0.05,1,1)
INDIGO5=(0.2,0,1,1)
INDIGO6=(0.2,0,0.9,1)
INDIGO7=(0.2,0,0.8,1)
INDIGO8=(0.18,0,0.7,1)
INDIGO9=(0.15,0,0.6,1)
INDIGO10=(0.15,0,0.5,1)
INDIGO11=(0.12,0,0.4,1)
INDIGO12=(0.1,0,0.35,1)
INDIGO13=(0.1,0,0.3,1)
INDIGO14=(0.08,0,0.25,1)
INDIGO15=(0.05,0,0.2,1)
INDIGO16=(0.05,0,0.15,1)
INDIGO17=(0.03,0,0.1,1)
INDIGO18=(0.02,0,0.08,1)

PURPLE1=(0.8,0.2,1,1)
PURPLE2=(0.7,0.1,1,1)
PURPLE3=(0.6,0,1,1)
PURPLE4=(0.55,0,0.95,1)
PURPLE5=(0.5,0,0.9,1)
PURPLE6=(0.45,0,0.85,1)
PURPLE7=(0.4,0,0.8,1)
PURPLE8=(0.35,0,0.75,1)
PURPLE9=(0.3,0,0.7,1)
PURPLE10=(0.25,0,0.65,1)
PURPLE11=(0.2,0,0.6,1)
PURPLE12=(0.18,0,0.55,1)
PURPLE13=(0.15,0,0.5,1)
PURPLE14=(0.12,0,0.45,1)
PURPLE15=(0.1,0,0.4,1)
PURPLE16=(0.08,0,0.35,1)
PURPLE17=(0.05,0,0.3,1)
PURPLE18=(0.03,0,0.25,1)

BLACK1=(0.1,0.1,0.1,1)
BLACK2=(0.08,0.08,0.08,1)
BLACK3=(0.06,0.06,0.06,1)
BLACK4=(0.05,0.05,0.05,1)
BLACK5=(0.04,0.04,0.04,1)
BLACK6=(0.03,0.03,0.03,1)
BLACK7=(0.02,0.02,0.02,1)
BLACK8=(0.01,0.01,0.01,1)
BLACK9=(0,0,0,1)

WHITE1=(1,1,1,1)
WHITE2=(0.98,0.98,0.98,1)
WHITE3=(0.96,0.96,0.96,1)
WHITE4=(0.94,0.94,0.94,1)
WHITE5=(0.92,0.92,0.92,1)
WHITE6=(0.9,0.9,0.9,1)
WHITE7=(0.88,0.88,0.88,1)
WHITE8=(0.86,0.86,0.86,1)
WHITE9=(0.84,0.84,0.84,1)
WHITE10=(0.82,0.82,0.82,1)
WHITE11=(0.8,0.8,0.8,1)
WHITE12=(0.78,0.78,0.78,1)
WHITE13=(0.76,0.76,0.76,1)
WHITE14=(0.74,0.74,0.74,1)
WHITE15=(0.72,0.72,0.72,1)
WHITE16=(0.7,0.7,0.7,1)
WHITE17=(0.68,0.68,0.68,1)
WHITE18=(0.66,0.66,0.66,1)

GREY1=(0.9,0.9,0.9,1)
GREY2=(0.85,0.85,0.85,1)
GREY3=(0.8,0.8,0.8,1)
GREY4=(0.75,0.75,0.75,1)
GREY5=(0.7,0.7,0.7,1)
GREY6=(0.65,0.65,0.65,1)
GREY7=(0.6,0.6,0.6,1)
GREY8=(0.55,0.55,0.55,1)
GREY9=(0.5,0.5,0.5,1)
GREY10=(0.45,0.45,0.45,1)
GREY11=(0.4,0.4,0.4,1)
GREY12=(0.35,0.35,0.35,1)
GREY13=(0.3,0.3,0.3,1)
GREY14=(0.25,0.25,0.25,1)
GREY15=(0.2,0.2,0.2,1)
GREY16=(0.15,0.15,0.15,1)

PINK1=(1,0.8,0.9,1)
PINK2=(1,0.7,0.85,1)
PINK3=(1,0.6,0.8,1)
PINK4=(1,0.5,0.75,1)
PINK5=(1,0.4,0.7,1)
PINK6=(1,0.3,0.65,1)
PINK7=(1,0.2,0.6,1)
PINK8=(1,0.15,0.55,1)
PINK9=(1,0.1,0.5,1)
PINK10=(0.95,0.08,0.45,1)
PINK11=(0.9,0.05,0.4,0.1)
PINK12=(0.85,0.05,0.35,1)
PINK13=(0.8,0.03,0.3,1)
PINK14=(0.75,0.02,0.25,1)
PINK15=(0.7,0,0.2,1)
PINK16=(0.65,0,0.18,1)
PINK17=(0.6,0,0.15,1)
PINK18=(0.55,0,0.12,1)

BROWN1=(0.8,0.6,0.4,1)
BROWN2=(0.75,0.55,0.35,1)
BROWN3=(0.7,0.5,0.3,1)
BROWN4=(0.65,0.45,0.25,1)
BROWN5=(0.6,0.4,0.2,1)
BROWN6=(0.55,0.35,0.18,1)
BROWN7=(0.5,0.3,0.15,1)
BROWN8=(0.45,0.28,0.12,1)
BROWN9=(0.4,0.25,0.1,1)
BROWN10=(0.35,0.22,0.08,1)
BROWN11=(0.3,0.2,0.07,1)
BROWN12=(0.28,0.18,0.06,1)
BROWN13=(0.25,0.15,0.05,1)
BROWN14=(0.22,0.12,0.04,1)
BROWN15=(0.2,0.2,0.03,1)
BROWN16=(0.18,0.09,0.02,1)
BROWN17=(0.15,0.07,0.01,1)
BROWN18=(0.12,0.05,0,1)

CYAN1=(0.6,1,1,1)
CYAN2=(0.5,1,1,1)
CYAN3=(0.4,1,1,1)
CYAN4=(0.3,1,1,1)
CYAN5=(0.2,1,1,1)
CYAN6=(0.1,1,1,1)
CYAN7=(0,1,1,1)
CYAN8=(0,0.95,0.95,1)
CYAN9=(0,0.9,0.9,1)
CYAN10=(0,0.85,0.85,1)
CYAN11=(0,0.8,0.8,1)
CYAN12=(0,0.75,0.75,1)
CYAN13=(0,0.7,0.7,1)
CYAN14=(0,0.65,0.65,1)
CYAN15=(0,0.6,0.6,1)
CYAN16=(0,0.55,0.55,1)
CYAN17=(0,0.5,0.5,1)
CYAN18=(0,0.45,0.45,1)

SILVER1=(0.95,0.95,0.98,1)
SILVER2=(0.9,0.9,0.95,1)
SILVER3=(0.88,0.88,0.92,1)
SILVER4=(0.85,0.85,0.9,1)
SILVER5=(0.82,0.82,0.88,1)
SILVER6=(0.8,0.8,0.85,1)
SILVER7=(0.78,0.78,0.82,1)
SILVER8=(0.75,0.75,0.8,1)
SILVER9=(0.72,0.72,0.78,1)
SILVER10=(0.7,0.7,0.75,1)
SILVER11=(0.68,0.68,0.72,1)
SILVER12=(0.65,0.65,0.7,1)
SILVER13=(0.62,0.62,0.68,1)
SILVER14=(0.6,0.6,0.65,1)
SILVER15=(0.58,0.58,0.62,1)
SILVER16=(0.55,0.55,0.6,1)
SILVER17=(0.52,0.52,0.58,1)
SILVER18=(0.5,0.5,0.55,1)

GOLD1=(1,0.9,0.5,1)
GOLD2=(1,0.85,0.45,1)
GOLD3=(1,0.8,0.4,1)
GOLD4=(1,0.75,0.35,1)
GOLD5=(1,0.7,0.3,1)
GOLD6=(0.95,0.65,0.28,1)
GOLD7=(0.9,0.6,0.25,1)
GOLD8=(0.85,0.55,0.22,1)
GOLD9=(0.8,0.5,0.2,1)
GOLD10=(0.75,0.45,0.18,1)
GOLD11=(0.7,0.4,0.15,1)
GOLD12=(0.65,0.35,0.12,1)
GOLD13=(0.6,0.3,0.1,1)
GOLD14=(0.55,0.55,0.28,1)
GOLD15=(0.5,0.25,0.07,1)
GOLD16=(0.45,0.22,0.06,1)
GOLD17=(0.4,0.2,0.05,1)
GOLD18=(0.35,0.18,0.04,1)

LIGHT="Light"
DARK="Dark"