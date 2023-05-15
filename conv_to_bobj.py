# Copyright (C) 2023 Warren Usui, MIT License
"""
Reformat web information into board object used by chess solver
"""
import numpy as np

def conv_to_bobj(setup):
    """
    Input: A string consisting of the following three parts separated by
           slashes:
        -- The number of moves to mate in this puzzle
        -- The layout of the white pieces
        -- The layout of the black pieces
        layout: a 'W' or 'B' followed by a comma separated list of piece
                representations.  The last two digits of a piece
                representation is a character representing a piece and
                the algebraic value of a location.  The piece is skipped
                if it's a pawn.  So Re7 represents a rook on e7.  d5
                represents a pawn on d5.

    Output: a dict with the following fields:
        -- moves: the number of half-turns required for mate.
        -- board: an 8x8 representation of the board. Element (0,0)
                  corresponds to a1.  A blank is an empty square, a
                  capitalized letter is a white piece, a lower case
                  letter is a black piece. Pieces are marked by their
                  algebraic representation.
        -- castle_info: FEN-like castle information
        -- ep_square: FEN-like en passant information
    """
    def parse_setup(setup):
        return full_setup({'moves': int(setup[0]) *2 - 1,
                           'board': get_board(setup[1:3])})
    def full_setup(part_set):
        return {'moves': part_set['moves'],
                'board': part_set['board'],
                'castle_info': get_castle_info(part_set['board']),
                'ep_square': '-'}
    def get_castle_info(board):
        def ceval(indx):
            def lvalue(col_indx):
                if col_indx == 0:
                    return 'Qq'[indx // 7]
                return 'Kk'[indx // 7]
            def test_rside(col_indx):
                if (indx == 0 and board[indx][col_indx] != 'R') or (
                    indx == 7 and board[indx][col_indx] != 'r'):
                    return '-'
                return lvalue(col_indx)
            if (indx == 0 and board[indx][4] != 'K') or (
                indx == 7 and board[indx][4] != 'k'):
                return '--'
            return test_rside(7) + test_rside(0)
        return ceval(0) + ceval(7)
    def get_board(pparts):
        return list_to_board(list(map(merge_sides(conv_side(pparts[0])),
                                      enumerate(conv_side(pparts[1])))))
    def merge_sides(w_info):
        def mrg_inner(eb_info):
            if w_info[eb_info[0]] != ' ':
                return w_info[eb_info[0]]
            return eb_info[1]
        return mrg_inner
    def conv_side(part_info):
        def conv_plocs(col_locs):
            def fix_side(pstring):
                if col_locs[0] == 'B':
                    return pstring.lower()
                return pstring
            def get_pindx(ploc):
                def gp_inner():
                    if len(ploc) == 2:
                        return 'P'
                    return ploc[0]
                return ['12345678'.index(ploc[-1]) * 8 +
                        'abcdefgh'.index(ploc[-2]), gp_inner()]
            def mk_pdict():
                return dict(list(map(get_pindx, col_locs[1].split(','))))
            def mk_string(dinfo):
                def get_sq_char(indx):
                    if indx in dinfo.keys():
                        return dinfo[indx]
                    return ' '
                return list(map(get_sq_char, range(64)))
            return fix_side(''.join(list(map(str, mk_string(mk_pdict())))))
        return conv_plocs(part_info.split(":"))
    def list_to_board(plocs):
        return list(map(list, np.array_split(list(plocs), 8)))
    return parse_setup(setup.split('/'))

if __name__ == "__main__":
    print(conv_to_bobj('2/W:b6,Ra1,Kc8/B:a7,b7,Ka8,Bb8'))
    print(conv_to_bobj(
        '2/W:c5,Rg5,Bf4,d3,c2,e2,f2,Ra1,Qc1,Ke1/B:Rc3,f3,a2,Nb1,Kh1'))
