class VsScaleDimsCalculator:
    def __init__(self, square_size):
        self.square_size = square_size

    def _scale(self, dim):
        prod = dim * self.square_size
        scaled = prod // 16
        if prod % 16 >= 8:
            scaled += 1
        return scaled

    def rednum_h(self):
        return self._scale(21)

    def rednum_w(self):
        return self._scale(11)

    def smiley_size(self):
        return self._scale(26)

    def top_border_h(self):
        return 56

    def left_border_w(self):
        return 12

    def msx_l_w(self):
        return self._scale(12)

    def msx_r_w(self):
        return self._scale(12)

    def msx_t_h(self):
        return self._scale(11)

    def msx_m_h(self):
        return self._scale(11)

    def msx_b_h(self):
        return self._scale(12)

    def top_border_without_bottom_border_h(self):
        return self.top_border_h() - self._scale(11)

    def timer_pad(self):
        return self._scale(2)

    def timer_h(self):
        return 2 * self.timer_pad() + self.rednum_h()

    def timer_w(self):
        return 4 * self.timer_pad() + 3 * self.rednum_w()


class VsSkinOffsetCalculator(VsScaleDimsCalculator):
    def row2_y(self):
        return self.square_size

    def rednum_y(self):
        return self.row2_y() + self.square_size + 1

    def smiley_y(self):
        return self.rednum_y() + self.rednum_h() + 1

    def msx_l_x(self):
        return 0

    def msx_r_x(self):
        return self.msx_l_w() + 3

    def msx_t_y(self):
        return self.smiley_y() + self.smiley_size() + 1

    def msx_m_y(self):
        return self.msx_t_y() + self.msx_t_h() + 3

    def msx_b_y(self):
        return self.msx_m_y() + self.msx_m_h() + 3

    def msx_h(self):
        return self.msx_b_y() + self.msx_b_h()

    def timer_x(self):
        return self.msx_r_x() + self.msx_r_w() + 1

    def timer_y(self):
        return self.msx_t_y()
