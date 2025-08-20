import ass
import dataclasses
import datetime
import enum
import types
import typing
import collections
import re
from .. import kbp
from .. import validators
from .. import kbs
from .. import kbpfont

__all__ = ['AssAlignment', 'AssPosition', 'AssOverflow', 'AssOptions', 'AssConverter']

class AssAlignment(enum.Enum):
    DEFAULT = 0
    BOTTOM_LEFT = 1
    BOTTOM_CENTER = 2
    BOTTOM_RIGHT = 3
    MIDDLE_LEFT = 4
    MIDDLE_CENTER = 5
    MIDDLE_RIGHT = 6
    TOP_LEFT = 7
    L = 7 # Alias
    TOP_CENTER = 8
    C = 8 # Alias
    TOP_RIGHT = 9
    R = 9 # Alias

@validators.validated_instantiation
class AssPosition(typing.NamedTuple):
    rotation: int
    alignment: AssAlignment
    x: int | float
    y: int | float

    def __str__(self):
        result = "{"
        if self.alignment != AssAlignment.DEFAULT:
            result += r"\an%d" % self.alignment.value
        if self.rotation:
            result += r"\frz%d" % self.rotation
        # Yes, %s, so it will stringify either an int or float and display properly
        result += r"\pos(%s,%s)}" % (self.x, self.y)
        return result

class AssOverflow(enum.Enum):
    NO_WRAP = 2
    EVEN_SPLIT = 0
    TOP_SPLIT = 1
    BOTTOM_SPLIT = 3

    def __str__(self):
        return self.name

@validators.validated_instantiation(replace="__init__")
@dataclasses.dataclass
class AssOptions:
    #position: bool
    #wipe: bool
    border: bool = dataclasses.field(default=True, metadata={"doc": "Add CDG-style borders to margins"})
    #display: int
    #remove: int
    float_font: bool = dataclasses.field(default=True, metadata={"doc": "Use floating point in output font sizes (well-supported in renderers)"})
    float_pos: bool = dataclasses.field(default=False, metadata={"doc": "Use floating point in \\pos and margins (supported by recent libass)"})
    target_x: int = dataclasses.field(default=300, metadata={"doc": "Output width"})
    target_y: int = dataclasses.field(default=216, metadata={"doc": "Output height"})
    fade_in: int = dataclasses.field(default=300, metadata={"doc": "Fade duration for line display (ms)"})
    fade_out: int = dataclasses.field(default=200, metadata={"doc": "Fade duration for line removal (ms)"})
    transparency: bool = dataclasses.field(default=True, metadata={"doc": "Treat palette index 1 as transparent"})
    offset: int | bool = dataclasses.field(default=True, metadata={"doc": "How to handle KBS offset. False => disable offset (same as 0), True => pull from KBS config, int is offset in ms"})
    overflow: AssOverflow = dataclasses.field(default=AssOverflow.EVEN_SPLIT, metadata={"doc": "How to handle lines wider than the screen"})
    allow_kt: bool = dataclasses.field(default=False, metadata={"doc": "Use \\kt if there are overlapping wipes on the same line (not supported by all ass implementations)"})
    experimental_spacing: bool = dataclasses.field(default=False, metadata={"doc": 'Calculate the "style 1" spacing instead of using Arial 12 bold default (only works for select fonts)'})
    #overflow_spacing: float # TODO? spacing value in styles that will apply for overflow (default 0). Multiplied by font height or based on default style?

    @staticmethod
    @validators.validated_types
    def __assert_valid(key: str, value):
        return validators.validate_and_coerce_values(AssOptions._fields, key, value)

    @validators.validated_structures(assert_function=__assert_valid)
    def update(self, **options):
        for opt in options:
            setattr(self, opt, options[opt])

# Not sure why dataclasses doesn't define something like this keyed by field name
AssOptions._fields = types.MappingProxyType(dict((f.name,f) for f in dataclasses.fields(AssOptions)))

class AssConverter:
    
    @validators.validated_types
    def __init__(self, kbpFile: kbp.KBPFile, options: AssOptions = None, **kwargs):
        self.kbpFile = kbpFile
        self.kbpFile.resolve_wipes()
        # Allow for applying specific overrides to defaults in kwargs, or
        # providing a template for defaults then overriding items there
        self.options = options or AssOptions()
        self.options.update(**kwargs)

    # Delegate to options if not present in the object itself
    def __getattr__(self,attr):
        return getattr(self.options, attr)

    # Move coordinates based on scaling the canvas size
    # If the target aspect ratio is wider than 300:216, x coordinates are
    # scaled more than y and vice versa
    # For example:
    #  - target_x, target_y = 384, 216
    #    - this behaves like -W 384 in the javascript kbp2ass
    #    - Text would not be scaled by scale_font, but this adjusts x positions to expand to fit the space
    #    - y positions would stay the same
    #  - target_x, target_y = 600, 600
    #    - Text would be scaled 2x by scale_font (min(600/300, 600/216))
    #    - x coordinates would be adjusted for the scaling factor
    #    - y coordinates would be further adjusted to fit the space
    #
    # NOTE: Original plan was to provide a letterboxed version as well, but
    # unfortunately .ass cannot reliably do that, as the margins are only used
    # for soft word wrapping. To letterbox, scale to a resolution with aspect
    # ratio the same as CDG, then letterbox when rendering the video
    @staticmethod
    @validators.validated_types
    def rescale_coords(x: int, y: int, target_x: int, target_y: int, allow_float: bool = False, border: bool = True) -> tuple:
        cdg_res = (300, 216) if border else (288, 192)
        res = (x * target_x / cdg_res[0], y * target_y / cdg_res[1])
        if allow_float:
            # Still return ints if they happen to be just as accurate
            return tuple(i if (i := int(r)) == r else r for r in res)
        else:
            return tuple(round(coord) for coord in res)

    # Scale scalars like font, border, shadow
    # These are scaled by a factor of the minimum of the scaling factor of x
    # and y to avoid going off screen
    # If font is true, additional scaling factor of 1.4 is applied to account for line height vs cap height
    @staticmethod
    @validators.validated_types
    def rescale_scalar(size: float, target_x: int, target_y: int, allow_float: bool = True, border: bool = True, font: bool = False) -> int | float:
        cdg_res = (300, 216) if border else (288, 192)
        scale = min(target_x / cdg_res[0], target_y / cdg_res[1])
        res = size * scale * (1.4 if font else 1) # Find way to calculate line_height(fontsize) instead of using this constant
        return res if (allow_float and int(res) != res) else round(res)

    @validators.validated_types
    def get_pos(self, line: kbp.KBPLine, num: int) -> AssPosition:
        cdg_res_x = 300 if self.border else 288
        margins = self.kbpFile.margins
        result = {}
        y = margins["top"] + \
            line.down + \
            num * (self.kbpFile.margins["spacing"] + (kbpfont.spacing(self.kbpFile.styles[1]) if self.experimental_spacing else 19)) + \
            (12 if self.border else 0)

        result["alignment"] = AssAlignment.DEFAULT if line.align == self.style_alignments[line.style] else AssAlignment[line.align]

        if line.align == 'L':
            x = margins["left"] + line.right + (6 if self.border else 0)
        elif line.align == 'C':
            x = cdg_res_x / 2 + line.right
        else: #line.align == 'R' or the file is broken
            x = cdg_res_x - margins["right"] + line.right - (6 if self.border else 0)

        result["x"], result["y"] = AssConverter.rescale_coords(x, y, self.target_x, self.target_y, border=self.border, allow_float=self.float_pos)

        return AssPosition(**result, rotation=line.rotation)

    @validators.validated_types
    def get_line_margins(self, line: kbp.KBPLine, pos: AssPosition | types.NoneType = None, num: int = 1) -> tuple:
        if pos is None:
            pos = self.get_pos(line, num)

        page_margins = self.kbpFile.margins

        left = page_margins["left"] - (0 if line.align == 'L' or (line.align == 'C' and line.right > 0) else line.right)
        right = page_margins["right"] + (0 if line.align == 'R' or (line.align == 'C' and line.right < 0) else line.right)
        left, _ = AssConverter.rescale_coords(left, pos.y, self.target_x, self.target_y, border=self.border, allow_float=self.float_pos)
        right, _ = AssConverter.rescale_coords(right, pos.y, self.target_x, self.target_y, border=self.border, allow_float=self.float_pos)

        return (left, right)
    
    # Determine the most-used line alignment for each style to minimize \anX tags in result
    # (since alignment is not part of the KBP style, but is part of the ASS style)
    def _calc_style_alignments(self):
        # dict of alpha-keyed style to dict of alignment to frequency
        # E.g.
        # { 'A' : {'C': 5, 'L': 2}}
        # would indicate style A was centered 5 times and left-aligned twice
        freqs = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
        for page in self.kbpFile.pages:
            for line in page.lines:
                freqs[line.style][line.align] += 1
        self.style_alignments = {}
        for style in freqs:
            self.style_alignments[style] = max(freqs[style], key = freqs[style].get)

    @validators.validated_types
    def fade(self) -> str:
        return r"{\fad(%d,%d)}" % (self.options.fade_in, self.options.fade_out)

    # Apply escape sequences needed when converting syllables in .kbp to .ass
    @staticmethod
    @validators.validated_types
    def kbpsyl2ass(syltext: str, firstSyl: bool = False):
        res = syltext.replace("{~}","/") # Literal / in .kbp, because / itself ends the syllable
        res = re.sub(r"\\(?=[Nnh])", "\\\u200b", res) # These escapes have special meaning in .ass, so add zero-width char in the middle
        res = re.sub(r"[{}]", r"\\1", res) # Escape literal {} so not to create a tag
        if firstSyl:
            res = re.sub(r"^ ", re.escape(r"\h"), res) # Spaces at the start of a line are ignored in .ass, so insert a \h
        return res

    # Convert a line of syllables into the text of a dialogue event including wipe tags
    @validators.validated_types
    def kbp2asstext(self, line: kbp.KBPLine, pos: AssPosition):
        result = str(pos) + self.fade()
        if self.kbpFile.styles[line.style].fixed:
            return result + line.text()
        if line.start < 0:
            line = line._replace(start = 0)
        cur = line.start
        for (n, s) in enumerate(line.syllables):
            if s.start < line.start:
                s = s._replace(start=line.start)
            if s.end < s.start:
                s = s._replace(end=s.start)
            delay = s.start - cur
            dur = s.end - s.start

            if delay > 0:
                # Gap between current position and start of next syllable
                result += r"{\k%d}" % delay
                cur += delay
            elif delay < 0:
                # Playing catchup
                if self.allow_kt:
                    # Reset time so wipes can overlap (\kt takes a time in centiseconds from line start)
                    result += r"{\kt%d}" % (s.start - line.start)
                    cur = s.start
                else:
                    # Shorten syllable to compensate for missing time (keep in mind delay is negative)
                    dur += delay

            # By default a syllable ends 1 centisecond before the next, so
            # special casing so we don't need a bunch of \k1 and the slight
            # errors don't catch up with us on a long line
            if len(line.syllables) > n+1 and line.syllables[n+1].start - s.end == 1:
                dur += 1

            if dur < 0:
                dur = 0

            # Using == False explicitly because it's technically a tri-state with None meaning undefined
            # Though that scenario shouldn't come up since we are allowing KBPFile to resolve wipedetail
            wipe = r"\k" if s.isprogressive() == False else r"\kf"

            result += r"{%s%d}%s" % (wipe, dur, self.kbpsyl2ass(s.syllable, n==0))
            cur += dur
        return result

    @validators.validated_types
    @staticmethod
    def ass_style_name(index: int, kbpName: str):
        return f"Style{abs(index):02}_{kbpName}"

    @validators.validated_types(coerce_types=False)
    @staticmethod
    def kbp2asscolor(kbpcolor: int | str, palette: kbp.KBPPalette | types.NoneType = None, transparency: bool = False):
        alpha = "&H00"
        if isinstance(kbpcolor, int):
            if transparency and kbpcolor == 0:
                alpha = "&HFF"
            # This will intentionally raise an exception if colors are unresolved and palette is not provided
            kbpcolor = palette[kbpcolor]
        return alpha + "".join(x+x for x in reversed(list(kbpcolor)))

    def ass_document(self):
        result = ass.Document()
        result.info.update(
            Title="",
            ScriptType="v4.00+",
            WrapStyle=self.overflow.value,
            ScaledBorderAndShadow="yes",
            Collisions="Normal",
            PlayResX=self.options.target_x,
            PlayResY=self.options.target_y,
            ) 

        if self.options.offset is False:
            self.options.offset = 0
        elif self.options.offset is True:
            self.options.offset = kbs.offset * 10
        # else already resolved to an int

        styles = self.kbpFile.styles
        self._calc_style_alignments()
        for page in self.kbpFile.pages:
            for num, line in enumerate(page.lines):
                if line.isempty():
                    continue
                pos = self.get_pos(line, num)
                line_margins = self.get_line_margins(line, pos)
                line_style = styles[line.style]
                result.events.append(ass.Dialogue(
                    start=datetime.timedelta(milliseconds = max(0, line.start * 10 + self.options.offset)),
                    end=datetime.timedelta(milliseconds = max(0, line.end * 10 + self.options.offset)),
                    style=AssConverter.ass_style_name(line_style.style_no, line_style.name), # Undefined styles get default style number
                    effect="karaoke",
                    text=self.kbp2asstext(line, pos),
                    margin_l=line_margins[0],
                    margin_r=line_margins[1],
                    ))
        for idx in styles:
            style = styles[idx]
            result.styles.append(ass.Style(
                name=AssConverter.ass_style_name(idx, style.name),
                fontname=style.fontname,
                fontsize=AssConverter.rescale_scalar(style.fontsize, self.target_x, self.target_y, font = True, border=self.border),
                secondary_color=AssConverter.kbp2asscolor(style.textcolor, palette=self.kbpFile.colors, transparency=self.options.transparency),
                primary_color=AssConverter.kbp2asscolor(style.textwipecolor, palette=self.kbpFile.colors, transparency=self.options.transparency),
                outline_color=AssConverter.kbp2asscolor(style.outlinecolor, palette=self.kbpFile.colors, transparency=self.options.transparency),
                # NOTE: no outline wipe in .ass
                back_color=AssConverter.kbp2asscolor(style.outlinewipecolor, palette=self.kbpFile.colors, transparency=self.options.transparency),
                bold = 'B' in style.fontstyle,
                italic = 'I' in style.fontstyle,
                underline = 'U' in style.fontstyle,
                strike_out = 'S' in style.fontstyle,
                outline = AssConverter.rescale_scalar(sum(style.outlines), self.target_x, self.target_y, border=self.border)/4, # NOTE: only one outline, but it's a float, so maybe averaging will be helpful
                shadow = AssConverter.rescale_scalar(sum(style.shadows), self.target_x, self.target_y, border=self.border)/2,
                margin_l = 0, # TODO: Decide if these should be set (and overridden on lines only when different)
                margin_r = 0, # TODO cont: Potentially could also be set by style like alignment based on most-used positions
                margin_v = 0,
                encoding = style.charset,
                alignment=AssAlignment[self.style_alignments.get(kbp.KBPStyleCollection.key2alpha(idx), 'C')].value,
                ))
            
        return result
