# Copyright (C) 2023 Warren Usui, MIT License
"""
Reformat web information into board object used by chess solver
"""
import numpy as np

def list_to_board(plocs):
    """
    Convert a list ot 64 squares back to a board
    """
    return list(map(list, np.array_split(list(plocs), 8)))

def get_castle_info(board):
    """
    Given a board, return FEN-line castle notation
    """
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
        return full_setup({'moves': int(setup[0]) * 2 - 1,
                           'board': get_board(setup[1:3])})
    def full_setup(part_set):
        return {'moves': part_set['moves'],
                'board': part_set['board'],
                'castle_info': get_castle_info(part_set['board']),
                'ep_square': '-'}
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
            def mk_pdict():
                return dict(list(map(alg_to_boinfo, col_locs[1].split(','))))
            def mk_string(dinfo):
                def get_sq_char(indx):
                    if indx in dinfo.keys():
                        return dinfo[indx]
                    return ' '
                return list(map(get_sq_char, range(64)))
            return fix_side(''.join(list(map(str, mk_string(mk_pdict())))))
        return conv_plocs(part_info.split(":"))
    return parse_setup(setup.split('/'))

def alg_square_to_lindx(ploc):
    """
    Convert algebraic square value to linear index
    """
    return '12345678'.index(ploc[-1]) * 8 + 'abcdefgh'.index(ploc[-2])

def alg_to_boinfo(ploc):
    """
    Convert algebraic position to piece/coordinate information
    """
    def gp_inner():
        if len(ploc) == 2:
            return 'P'
        return ploc[0]
    return [alg_square_to_lindx(ploc), gp_inner()]

def get_sp_coord(ploc):
    """
    Convert algebraic position to [row, column] coordinates
    """
    return get_coords(alg_to_boinfo(ploc)[0])

def get_coords(indx):
    """
    Given a single number index, convert to board coordinates
    """
    return [indx // 8, indx % 8]

def coord_to_alg(coords):
    """
    Given coordinates, return the algebraic notation value
    """
    return 'abcdefgh'[coords[1]] + '12345678'[coords[0]]
