from PIL import Image
from .dims import VsSkinOffsetCalculator
from .paster import Paster


def rescale(inim, outpx, bgc):
    inpx = inim.width // 9
    incalc = VsSkinOffsetCalculator(inpx)
    outcalc = VsSkinOffsetCalculator(outpx)
    outim = Image.new(
        "RGB",
        (outpx * 9, outcalc.msx_h()),
        bgc,
    )
    paster = Paster(inim, outim)

    # squares
    paster.row(9, 0, inpx, inpx, 0, outpx, outpx, ingap=0, outgap=0)
    paster.row(8, inpx, inpx, inpx, outpx, outpx, outpx, ingap=0, outgap=0)

    # timer numbers
    paster.row(
        11,
        incalc.rednum_y(),
        incalc.rednum_w(),
        incalc.rednum_h(),
        outcalc.rednum_y(),
        outcalc.rednum_w(),
        outcalc.rednum_h(),
    )

    # smiley states
    paster.row(
        5,
        incalc.smiley_y(),
        incalc.smiley_size(),
        incalc.smiley_size(),
        outcalc.smiley_y(),
        outcalc.smiley_size(),
        outcalc.smiley_size(),
    )

    # ui edges/corners
    paster.ui_corners(
        incalc.msx_t_y(),
        incalc.msx_t_h(),
        incalc.msx_l_w(),
        incalc.msx_r_w(),
        outcalc.msx_t_y(),
        outcalc.msx_t_h(),
        outcalc.msx_l_w(),
        outcalc.msx_r_w(),
    )
    paster.ui_corners(
        incalc.msx_t_y() + incalc.msx_t_h() + 1,
        1,
        incalc.msx_l_w(),
        incalc.msx_r_w(),
        outcalc.msx_t_y() + outcalc.msx_t_h() + 1,
        1,
        outcalc.msx_l_w(),
        outcalc.msx_r_w(),
        middle=False,
    )
    paster.ui_corners(
        incalc.msx_m_y(),
        incalc.msx_m_h(),
        incalc.msx_l_w(),
        incalc.msx_r_w(),
        outcalc.msx_m_y(),
        outcalc.msx_m_h(),
        outcalc.msx_l_w(),
        outcalc.msx_r_w(),
    )
    paster.ui_corners(
        incalc.msx_m_y() + incalc.msx_m_h() + 1,
        1,
        incalc.msx_l_w(),
        incalc.msx_r_w(),
        outcalc.msx_m_y() + outcalc.msx_m_h() + 1,
        1,
        outcalc.msx_l_w(),
        outcalc.msx_r_w(),
        middle=False,
    )
    paster.ui_corners(
        incalc.msx_b_y(),
        incalc.msx_b_h(),
        incalc.msx_l_w(),
        incalc.msx_r_w(),
        outcalc.msx_b_y(),
        outcalc.msx_b_h(),
        outcalc.msx_l_w(),
        outcalc.msx_r_w(),
    )

    # timer
    xx = incalc.timer_x()
    yy = incalc.timer_y()
    inbox = (xx, yy, xx + incalc.timer_w(), yy + incalc.timer_h())
    outcoords = (outcalc.timer_x(), outcalc.timer_y())
    outdims = (outcalc.timer_w(), outcalc.timer_h())
    paster.paste(inbox, outcoords, outdims)
    paster.row(
        3,
        incalc.timer_y() + incalc.timer_pad(),
        incalc.rednum_w(),
        incalc.rednum_h(),
        outcalc.timer_y() + outcalc.timer_pad(),
        outcalc.rednum_w(),
        outcalc.rednum_h(),
        inxx=incalc.timer_x() + incalc.timer_pad(),
        outxx=outcalc.timer_x() + outcalc.timer_pad(),
        ingap=incalc.timer_pad(),
        outgap=outcalc.timer_pad(),
    )

    # bg pixel
    xx = incalc.timer_x() + incalc.timer_w() + 1
    yy = incalc.timer_y()
    inbox = (xx, yy, xx + 1, yy + 1)
    outcoords = (outcalc.timer_x() + outcalc.timer_w() + 1, outcalc.timer_y())
    outdims = (1, 1)
    paster.paste(inbox, outcoords, outdims)

    return outim
