# -*- coding: utf-8 -*-
# :Project:   SoL -- Generation of PDF printouts
# :Created:   ven 31 ott 2008 10:32:29 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013-2016, 2018, 2020, 2022-2025 Lele Gaifax
#

"""
This module uses ReportLab to produce all the needed printouts.
"""

from __future__ import annotations

import logging
from copy import copy

logger = logging.getLogger(__name__)

BASE_FONT_NAME = 'DejaVuSans'

from reportlab import rl_settings  # noqa

rl_settings.canvas_basefontname = BASE_FONT_NAME

from reportlab.pdfbase import pdfmetrics  # noqa
from reportlab.pdfbase.ttfonts import TTFont, TTFError  # noqa

try:
    for variant in ('', '-Bold', '-Oblique', '-BoldOblique'):
        pdfmetrics.registerFont(
            TTFont(BASE_FONT_NAME + variant, BASE_FONT_NAME + '%s.ttf' % variant)
        )
except TTFError:  # pragma: no cover
    from reportlab import rl_config

    logger.error(
        'Could not find the "%s" font, using PDF default fonts', BASE_FONT_NAME
    )

    BASE_FONT_NAME = 'Times-Roman'
    rl_config.canvas_basefontname = rl_settings.canvas_basefontname = BASE_FONT_NAME
    BOLD_FONT_NAME = 'Times-Bold'
    BOLD_ITALIC_FONT_NAME = 'Times-BoldItalic'
    ITALIC_FONT_NAME = 'Times-Italic'
else:
    BOLD_FONT_NAME = BASE_FONT_NAME + '-Bold'
    BOLD_ITALIC_FONT_NAME = BASE_FONT_NAME + '-BoldOblique'
    ITALIC_FONT_NAME = BASE_FONT_NAME + '-Oblique'

    from reportlab.lib.fonts import addMapping

    addMapping(BASE_FONT_NAME, 0, 0, BASE_FONT_NAME)
    addMapping(BASE_FONT_NAME, 0, 1, ITALIC_FONT_NAME)
    addMapping(BASE_FONT_NAME, 1, 0, BOLD_FONT_NAME)
    addMapping(BASE_FONT_NAME, 1, 1, BOLD_ITALIC_FONT_NAME)

from reportlab.lib.enums import TA_CENTER  # noqa
from reportlab.lib.styles import getSampleStyleSheet  # noqa
from reportlab.lib.units import cm  # noqa


base_style = getSampleStyleSheet()
'The base style used to build the document'

title_style = copy(base_style['Title'])
'The style used for the title of the document'

title_style.fontSize = 28
title_style.leading = title_style.fontSize * 1.1

subtitle_style = copy(base_style['Heading1'])
'The style used for the subtitle of the document'

subtitle_style.fontSize = 20
subtitle_style.leading = subtitle_style.fontSize * 1.1
subtitle_style.alignment = TA_CENTER
subtitle_style.fontName = ITALIC_FONT_NAME

heading_style = copy(base_style['Heading2'])
'The style used for the heading paragraphs of the document'

heading_style.alignment = TA_CENTER

normal_style = copy(base_style['Normal'])
'The style used for most of the paragraphs of the document'

normal_style.fontSize = 14
normal_style.leading = normal_style.fontSize * 1.1

caption_style = copy(base_style['Italic'])
"The style used for the caption of the table's columns"

caption_style.fontSize = 9
caption_style.leading = caption_style.fontSize * 1.1

cardtitle_style = copy(base_style['Normal'])
'The style used for the title of the score cards'

cardtitle_style.alignment = TA_CENTER
cardtitle_style.leading = 6

cardsmall_style = copy(base_style['Normal'])
'The style used for most of the text on the score cards'

cardsmall_style.fontSize = 6
cardsmall_style.leading = 7

cardinfo_style = copy(base_style['Italic'])
'The style used for the additional info on the score cards'

cardinfo_style.alignment = TA_CENTER

badgename_style = copy(cardinfo_style)
'The style used for the player name on the badges'

badgename_style.fontName = BOLD_ITALIC_FONT_NAME
badgename_style.fontSize = 12
badgename_style.leading = 13

cardname_style = copy(badgename_style)
'The style used for the player name on the score cards'

cardname_style.fontSize = 9
cardname_style.leading = 10

rank_width = 0.8 * cm
'The width of the `rank` columns'

country_width = 0.9 * cm
'The width of the `country` columns'

scores_width = 1.3 * cm
'The width of the `scores` columns'

prizes_width = 2 * cm
'The width of the `prizes` columns'

boardnumber_style = copy(base_style['Title'])
'The style used for the number of the board'

boardnumber_style.fontSize = 56
boardnumber_style.leading = boardnumber_style.fontSize * 1.1


from .badges import BadgesPrintout as BadgesPrintout  # noqa
from .boardlabels import BoardLabelsPrintout as BoardLabelsPrintout  # noqa
from .cranking import ChampionshipRankingPrintout as ChampionshipRankingPrintout  # noqa
from .matches import MatchesPrintout as MatchesPrintout  # noqa
from .nranking import NationalRankingPrintout as NationalRankingPrintout  # noqa
from .participants import ParticipantsPrintout as ParticipantsPrintout  # noqa
from .playbill import PlaybillPrintout as PlaybillPrintout  # noqa
from .results import ResultsPrintout as ResultsPrintout  # noqa
from .rranking import RatingRankingPrintout as RatingRankingPrintout  # noqa
from .scorecards import ScoreCardsPrintout as ScoreCardsPrintout  # noqa
from .tranking import TourneyOverRankingPrintout as TourneyOverRankingPrintout  # noqa
from .tranking import TourneyRankingPrintout as TourneyRankingPrintout  # noqa
from .tranking import TourneyUnderRankingPrintout as TourneyUnderRankingPrintout  # noqa
from .tranking import TourneyWomenRankingPrintout as TourneyWomenRankingPrintout  # noqa
