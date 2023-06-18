# Copyright (C) 2023 Warren Usui, MIT License
"""
Generate all the moves that a player can make
"""
from functools import reduce

from conv_to_bobj import conv_to_bobj, list_to_board, coord_to_alg
from make_moves import are_they_in_check, find_moves, board_to_linear, \
            get_coords
from odd_moves import castling, pawn_promotion

def are_we_in_check(board_obj):
    """
    List opponents moves that attack our king
    """
    def shift_back(board_obj):
        return {'moves': board_obj['moves'] + 1,
                'board': board_obj['board'],
                'castle_info': board_obj['castle_info'],
                'ep_square': board_obj['ep_square']}
    return are_they_in_check(shift_back(board_obj))

def gen_all_moves(board_obj):
    """
    Run find_moves for all positions
    """
    def find_moves_wrap(intv):
        return find_moves(board_obj)(get_coords(intv))
    if are_they_in_check(board_obj):
        #return 'They are in check'
        return {}
    return list(map(find_moves_wrap, list(range(64))))

def mk_move_list_moves(board_obj):
    """
    Organize moves into one list
    """
    def sq_loop(sq_mdata):
        return list(filter(bool, sq_mdata))
    def gam_inner(move_data):
        if not move_data:
            return {}
        return reduce(lambda a, b: a + b, list(map(sq_loop, move_data)))
    return gam_inner(gen_all_moves(board_obj))

def get_all_moves(board_obj):
    """
    Given a board, find all piece moves
    """
    def filter_no_moves(mv_md):
        if board_obj['board'][mv_md[1][0]][mv_md[1][1]] == ' ':
            return True
        if board_obj['board'][mv_md[0][0]][mv_md[0][1]].isupper() == \
                board_obj['board'][mv_md[1][0]][mv_md[1][1]].isupper():
            return False
        return True
    return list(filter(filter_no_moves, mk_move_list_moves(board_obj)))

def gen_moves(board_obj):
    """
    Generate a list of new moves.  Each list entry contains a move
    and a new board_obj
    """
    def gm_inner(mv_lst):
        def get_alg(aimove):
            return 'abcdefgh'[aimove[1]] + '12345678'[aimove[0]]
        def new_label(amove):
            def uniqify(d_data):
                if not d_data:
                    return ''
                if amove[0][1] not in list(map(lambda a: a[1], d_data)):
                    return get_alg(amove[0])[0]
                if amove[0][0] not in list(map(lambda a: a[0], d_data)):
                    return get_alg(amove[0])[1]
                return get_alg(amove[0])
            def find_dups(dupv):
                if dupv == amove:
                    return False
                if dupv[1] == amove[1]:
                    if board_obj['board'][amove[0][0]][amove[0][1]] == \
                            board_obj['board'][dupv[0][0]][dupv[0][1]]:
                        return True
                return False
            def blnk_or_ind(binfo):
                if not binfo:
                    return ''
                return binfo
            def xfactor():
                if len(amove) == 3 and amove[2] == 'ep':
                    return 'abcdefgh'[amove[0][1]] + 'x'
                if board_obj['board'][amove[1][0]][amove[1][1]] != ' ':
                    if board_obj['board'][amove[0][0]][amove[0][1]] \
                                in ['p', 'P']:
                        return 'abcdefgh'[amove[0][1]] + 'x'
                    return 'x'
                return ''
            def get_piece_nm(piece):
                if piece in ['p', 'P']:
                    return ''
                return piece.upper()
            return ''.join([get_piece_nm(board_obj['board'][amove[0][0]]
                    [amove[0][1]]),
                    uniqify(list(map(lambda a: a[0],
                    blnk_or_ind(list(filter(find_dups, mv_lst)))))),
                    xfactor(), get_alg(amove[1])])
        def new_bobj(amove):
            def mk_phys_mv(orig_board):
                def findx(anum):
                    return amove[anum][0] * 8 + amove[anum][1]
                def mpm_in1(lin_brd):
                    def mpm_in2(chg_dict):
                        def set_lsq(indx):
                            if indx in chg_dict.keys():
                                return chg_dict[indx]
                            return lin_brd[indx]
                        return list(map(set_lsq, list(range(64))))
                    return mpm_in2({findx(1):
                            orig_board[amove[0][0]][amove[0][1]],
                            findx(0): ' '})
                return list_to_board(mpm_in1(board_to_linear(orig_board)))

            def fix_brd(inner_brd):
                def fix_brd2(inner_brd2):
                    if are_they_in_check(inner_brd2):
                        return {}
                    return inner_brd2
                if inner_brd['moves'] == 1:
                    if not are_they_in_check(inner_brd):
                        return {}
                def new_ep_val():
                    if amove[0][1] == amove[1][1]:
                        if abs(amove[0][0] - amove[1][0]) == 2:
                            if inner_brd['board'][amove[1][0]] \
                                    [amove[1][1]] in ['p', 'P']:
                                return coord_to_alg([
                                        (amove[0][0] + amove[1][0]) // 2,
                                        amove[1][1]])
                    return '-'
                return fix_brd2({
                    'moves': inner_brd['moves'] - 1,
                    'board': inner_brd['board'],
                    'castle_info': inner_brd['castle_info'],
                    'ep_square': new_ep_val()})
            def ep_squash(ret_board):
                def isqh(mnumb):
                    def sqepsq(numb):
                        if numb != mnumb:
                            return ret_board[numb]
                        return ' '
                    return list(map(sqepsq, range(64)))
                return isqh(amove[0][0] * 8 + amove[1][1])
            def ep_extra(ret_bobj):
                if len(amove) == 3 and amove[2] == "ep":
                    return {'moves': ret_bobj['moves'],
                            'board': list_to_board(
                                ep_squash(board_to_linear(
                                    ret_bobj['board']))),
                            'castle_info': ret_bobj['castle_info'],
                            'ep_square': '-'}
                return ret_bobj
            if not amove:
                return {}
            return ep_extra(fix_brd({
                'moves': board_obj['moves'],
                'board': mk_phys_mv(board_obj['board']),
                'castle_info': board_obj['castle_info'],
                'ep_square': board_obj['ep_square']}))
        def check_check(lpmv):
            def set_chk_ind():
                if lpmv[1]['moves'] == 0:
                    return "#"
                return "+"
            if not lpmv[1]:
                return lpmv
            if are_we_in_check(lpmv[1]):
                return [lpmv[0] + set_chk_ind(), lpmv[1]]
            return lpmv
        def handle_pmove(amove):
            return check_check([new_label(amove), new_bobj(amove)])
        return list(map(handle_pmove, mv_lst))
    return pawn_promotion(dict(list(filter(lambda a: a[1],
                            gm_inner(get_all_moves(board_obj)))))) | \
                            castling(board_obj)

if __name__ == "__main__":
    #epw_obj = conv_to_bobj('2/W:g4,Ka1/B:a7,f4,Kc8')
    #epw_obj['ep_square'] = 'g3'
    #epw_obj['moves'] += 1
    #epw_obj = conv_to_bobj('2/W:g7,Ka1/B:f4,Kc8')
    epw_obj = conv_to_bobj('2/W:Ka1/B:f2,g2,Kh8')
    epw_obj['moves'] += 1
    answer = gen_moves(epw_obj)
    import pdb; pdb.set_trace()
