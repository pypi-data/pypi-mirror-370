# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "BrandStyleguideResponse",
    "Styleguide",
    "StyleguideColors",
    "StyleguideComponents",
    "StyleguideComponentsButton",
    "StyleguideComponentsButtonLink",
    "StyleguideComponentsButtonPrimary",
    "StyleguideComponentsButtonSecondary",
    "StyleguideComponentsCard",
    "StyleguideElementSpacing",
    "StyleguideShadows",
    "StyleguideTypography",
    "StyleguideTypographyHeadings",
    "StyleguideTypographyHeadingsH1",
    "StyleguideTypographyHeadingsH2",
    "StyleguideTypographyHeadingsH3",
    "StyleguideTypographyHeadingsH4",
    "StyleguideTypographyP",
]


class StyleguideColors(BaseModel):
    accent: Optional[str] = None
    """Accent color of the website (hex format)"""

    background: Optional[str] = None
    """Background color of the website (hex format)"""

    text: Optional[str] = None
    """Text color of the website (hex format)"""


class StyleguideComponentsButtonLink(BaseModel):
    background_color: Optional[str] = FieldInfo(alias="backgroundColor", default=None)

    border_color: Optional[str] = FieldInfo(alias="borderColor", default=None)

    border_radius: Optional[str] = FieldInfo(alias="borderRadius", default=None)

    border_style: Optional[str] = FieldInfo(alias="borderStyle", default=None)

    border_width: Optional[str] = FieldInfo(alias="borderWidth", default=None)

    box_shadow: Optional[str] = FieldInfo(alias="boxShadow", default=None)

    color: Optional[str] = None

    font_size: Optional[str] = FieldInfo(alias="fontSize", default=None)

    font_weight: Optional[float] = FieldInfo(alias="fontWeight", default=None)

    padding: Optional[str] = None

    text_decoration: Optional[str] = FieldInfo(alias="textDecoration", default=None)


class StyleguideComponentsButtonPrimary(BaseModel):
    background_color: Optional[str] = FieldInfo(alias="backgroundColor", default=None)

    border_color: Optional[str] = FieldInfo(alias="borderColor", default=None)

    border_radius: Optional[str] = FieldInfo(alias="borderRadius", default=None)

    border_style: Optional[str] = FieldInfo(alias="borderStyle", default=None)

    border_width: Optional[str] = FieldInfo(alias="borderWidth", default=None)

    box_shadow: Optional[str] = FieldInfo(alias="boxShadow", default=None)

    color: Optional[str] = None

    font_size: Optional[str] = FieldInfo(alias="fontSize", default=None)

    font_weight: Optional[float] = FieldInfo(alias="fontWeight", default=None)

    padding: Optional[str] = None

    text_decoration: Optional[str] = FieldInfo(alias="textDecoration", default=None)


class StyleguideComponentsButtonSecondary(BaseModel):
    background_color: Optional[str] = FieldInfo(alias="backgroundColor", default=None)

    border_color: Optional[str] = FieldInfo(alias="borderColor", default=None)

    border_radius: Optional[str] = FieldInfo(alias="borderRadius", default=None)

    border_style: Optional[str] = FieldInfo(alias="borderStyle", default=None)

    border_width: Optional[str] = FieldInfo(alias="borderWidth", default=None)

    box_shadow: Optional[str] = FieldInfo(alias="boxShadow", default=None)

    color: Optional[str] = None

    font_size: Optional[str] = FieldInfo(alias="fontSize", default=None)

    font_weight: Optional[float] = FieldInfo(alias="fontWeight", default=None)

    padding: Optional[str] = None

    text_decoration: Optional[str] = FieldInfo(alias="textDecoration", default=None)


class StyleguideComponentsButton(BaseModel):
    link: Optional[StyleguideComponentsButtonLink] = None
    """Link button style"""

    primary: Optional[StyleguideComponentsButtonPrimary] = None
    """Primary button style"""

    secondary: Optional[StyleguideComponentsButtonSecondary] = None
    """Secondary button style"""


class StyleguideComponentsCard(BaseModel):
    background_color: Optional[str] = FieldInfo(alias="backgroundColor", default=None)

    border_color: Optional[str] = FieldInfo(alias="borderColor", default=None)

    border_radius: Optional[str] = FieldInfo(alias="borderRadius", default=None)

    border_style: Optional[str] = FieldInfo(alias="borderStyle", default=None)

    border_width: Optional[str] = FieldInfo(alias="borderWidth", default=None)

    box_shadow: Optional[str] = FieldInfo(alias="boxShadow", default=None)

    padding: Optional[str] = None

    text_color: Optional[str] = FieldInfo(alias="textColor", default=None)


class StyleguideComponents(BaseModel):
    button: Optional[StyleguideComponentsButton] = None
    """Button component styles"""

    card: Optional[StyleguideComponentsCard] = None
    """Card component style"""


class StyleguideElementSpacing(BaseModel):
    lg: Optional[str] = None
    """Large spacing value"""

    md: Optional[str] = None
    """Medium spacing value"""

    sm: Optional[str] = None
    """Small spacing value"""

    xl: Optional[str] = None
    """Extra large spacing value"""

    xs: Optional[str] = None
    """Extra small spacing value"""


class StyleguideShadows(BaseModel):
    inner: Optional[str] = None
    """Inner shadow value"""

    lg: Optional[str] = None
    """Large shadow value"""

    md: Optional[str] = None
    """Medium shadow value"""

    sm: Optional[str] = None
    """Small shadow value"""

    xl: Optional[str] = None
    """Extra large shadow value"""


class StyleguideTypographyHeadingsH1(BaseModel):
    font_family: Optional[str] = FieldInfo(alias="fontFamily", default=None)

    font_size: Optional[str] = FieldInfo(alias="fontSize", default=None)

    font_weight: Optional[float] = FieldInfo(alias="fontWeight", default=None)

    letter_spacing: Optional[str] = FieldInfo(alias="letterSpacing", default=None)

    line_height: Optional[str] = FieldInfo(alias="lineHeight", default=None)


class StyleguideTypographyHeadingsH2(BaseModel):
    font_family: Optional[str] = FieldInfo(alias="fontFamily", default=None)

    font_size: Optional[str] = FieldInfo(alias="fontSize", default=None)

    font_weight: Optional[float] = FieldInfo(alias="fontWeight", default=None)

    letter_spacing: Optional[str] = FieldInfo(alias="letterSpacing", default=None)

    line_height: Optional[str] = FieldInfo(alias="lineHeight", default=None)


class StyleguideTypographyHeadingsH3(BaseModel):
    font_family: Optional[str] = FieldInfo(alias="fontFamily", default=None)

    font_size: Optional[str] = FieldInfo(alias="fontSize", default=None)

    font_weight: Optional[float] = FieldInfo(alias="fontWeight", default=None)

    letter_spacing: Optional[str] = FieldInfo(alias="letterSpacing", default=None)

    line_height: Optional[str] = FieldInfo(alias="lineHeight", default=None)


class StyleguideTypographyHeadingsH4(BaseModel):
    font_family: Optional[str] = FieldInfo(alias="fontFamily", default=None)

    font_size: Optional[str] = FieldInfo(alias="fontSize", default=None)

    font_weight: Optional[float] = FieldInfo(alias="fontWeight", default=None)

    letter_spacing: Optional[str] = FieldInfo(alias="letterSpacing", default=None)

    line_height: Optional[str] = FieldInfo(alias="lineHeight", default=None)


class StyleguideTypographyHeadings(BaseModel):
    h1: Optional[StyleguideTypographyHeadingsH1] = None

    h2: Optional[StyleguideTypographyHeadingsH2] = None

    h3: Optional[StyleguideTypographyHeadingsH3] = None

    h4: Optional[StyleguideTypographyHeadingsH4] = None


class StyleguideTypographyP(BaseModel):
    font_family: Optional[str] = FieldInfo(alias="fontFamily", default=None)

    font_size: Optional[str] = FieldInfo(alias="fontSize", default=None)

    font_weight: Optional[float] = FieldInfo(alias="fontWeight", default=None)

    letter_spacing: Optional[str] = FieldInfo(alias="letterSpacing", default=None)

    line_height: Optional[str] = FieldInfo(alias="lineHeight", default=None)


class StyleguideTypography(BaseModel):
    headings: Optional[StyleguideTypographyHeadings] = None
    """Heading styles"""

    p: Optional[StyleguideTypographyP] = None
    """Paragraph text styles"""


class Styleguide(BaseModel):
    colors: Optional[StyleguideColors] = None
    """Primary colors used on the website"""

    components: Optional[StyleguideComponents] = None
    """UI component styles"""

    element_spacing: Optional[StyleguideElementSpacing] = FieldInfo(alias="elementSpacing", default=None)
    """Spacing system used on the website"""

    shadows: Optional[StyleguideShadows] = None
    """Shadow styles used on the website"""

    typography: Optional[StyleguideTypography] = None
    """Typography styles used on the website"""


class BrandStyleguideResponse(BaseModel):
    code: Optional[int] = None
    """HTTP status code"""

    domain: Optional[str] = None
    """The normalized domain that was processed"""

    status: Optional[str] = None
    """Status of the response, e.g., 'ok'"""

    styleguide: Optional[Styleguide] = None
    """Comprehensive styleguide data extracted from the website"""
