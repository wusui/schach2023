# Copyright (C) 2023 Warren Usui, MIT License
"""
Handle pawn promotion and castling
"""
import itertools

from conv_to_bobj import list_to_board, alg_square_to_lindx
from make_moves import board_to_linear, are_we_in_check, castle_field

def pawn_promotion(binfo):
    """
    Look through generated moves and make sure all possible pawn promotions
    can happen.
    """
    def promo_inn(promo_p):
        def non_promo():
            return dict(list(map(lambda a: [a, binfo[a]],
                        list(filter(lambda a: a not in promo_p,
                                    list(binfo.keys()))))))
        def do_promo():
            def hndl_a_pawn(ploc):
                def exec_promo(piece):
                    def new_bp(bpos):
                        def ppro(pboard):
                            def promote(linboard):
                                def fixit(chg_loc):
                                    def fix_it_in(indx):
                                        def promc(cpiece):
                                            if bpos['moves'] % 2 == 1:
                                                return cpiece.lower()
                                            return cpiece
                                        if indx != chg_loc:
                                            return linboard[indx]
                                        return promc(piece)
                                    return fix_it_in
                                return list(map(fixit(
                                        alg_square_to_lindx(ploc)),
                                        list(range(64))))
                            return list_to_board(promote(
                                    board_to_linear(pboard)))
                        return {'moves': bpos['moves'],
                                'board': ppro(bpos['board']),
                                'castle_info': bpos['castle_info'],
                                'ep_square': bpos['ep_square']}
                    return [f'{ploc} ({piece})', new_bp(binfo[ploc])]
                return list(map(exec_promo, ['Q', 'R', 'B', 'N']))
            return dict(list(itertools.chain.from_iterable(
                        list(map(hndl_a_pawn, promo_p)))))
        if not promo_p:
            return binfo
        return non_promo() | do_promo()
    return promo_inn(list(filter(lambda a: a[0] in 'abcdefgh' and
                                a[-1] in '18', binfo.keys())))

def castling(board_obj):
    """
    Handle castling as a completely separate operation
    """
    def castle_dir(indx):
        if indx == 1:
            return list(filter(lambda a: a.isupper(),
                               board_obj['castle_info']))
        return list(filter(lambda a: a.islower(), board_obj['castle_info']))
    def castle_work(dir_info):
        def all_clear(side_info):
            def ac_inner(brange):
                if list(filter(lambda a:
                        board_obj['board'][[7, 0][board_obj['moves'] % 2]][a]
                                   == ' ', brange)) != brange:
                    return False
                return True
            return ac_inner({'K': list(range(5,7)),
                             'Q': list(range(1,4))}[side_info])
        def chg_row_in_brd(orow):
            def mvdc_inner(nrow):
                if orow == 7:
                    return board_obj['board'][0:7] + [nrow]
                return [nrow] + board_obj['board'][1:8]
            return mvdc_inner
        def kmokay(side_info):
            def km_inner(offset):
                def km2_inner(orow):
                    #def chg_row_in_brd(nrow):
                    #    if orow == 7:
                    #        return board_obj['board'][0:7] + [nrow]
                    #    return [nrow] + board_obj['board'][1:8]
                    def new_crow(rval):
                        if rval == 4:
                            return ' '
                        if rval == 4 + offset:
                            if orow == 7:
                                return 'k'
                            return 'K'
                        return board_obj['board'][orow][rval]
                    if are_we_in_check({
                        'moves': board_obj['moves'],
                        'board': chg_row_in_brd(orow)(list(map(new_crow,
                                                    list(range(0,8))))),
                        'castle_info': board_obj['castle_info'],
                        'ep_square': board_obj['ep_square']}):
                        return False
                    return True
                return km2_inner([7, 0][board_obj['moves'] % 2])
            return km_inner({'K': 1, 'Q': -1}[side_info])
        def cnew_board_obj(side_info):
            def cline(all_info):
                def cset_sq(indx):
                    if indx == all_info[side_info]['rwas']:
                        return ' '
                    if indx == all_info[side_info]['kto']:
                        return ['K', 'k'][all_info[side_info]['orow'] // 7]
                    if indx == all_info[side_info]['rto']:
                        return ['R', 'r'][all_info[side_info]['orow'] // 7]
                    if indx == 4:
                        return ' '
                    return board_obj['board'][all_info[side_info] \
                                              ['orow']][indx]
                return list(map(cset_sq, range(8)))
            def cboard(all_info):
                if all_info[side_info]['orow'] == 7:
                    return board_obj['board'][0:7] + [cline(all_info)]
                return [cline(all_info)] + board_obj['board'][1:]
            def c_set_move(all_info):
                def cset_in(cboardv):
                    return {all_info[side_info]['ccode']:
                        {'moves': board_obj['moves'] - 1,
                         'board': cboardv,
                         'castle_info': castle_field([cboardv,
                                        board_obj['castle_info']]),
                         'ep_square': '-'}}
                return cset_in(cboard(all_info))
            return c_set_move({'Q': {'rwas': 0, 'kto': 2, 'rto': 3,
                                'orow': [7, 0][board_obj['moves'] % 2],
                                'ccode': 'O-O-O'},
                               'K': {'rwas': 7, 'kto': 6, 'rto': 5,
                                'orow': [7, 0][board_obj['moves'] % 2],
                                'ccode': 'O-O'}})
        def ccheck(svalues):
            if len(dir_info) == 2 or dir_info[0] in svalues:
                if all_clear(svalues[0]) and kmokay(svalues[0]):
                    return cnew_board_obj(svalues[0])
            return {}
        if not dir_info:
            return {}
        return ccheck(['K', 'k']) | ccheck(['Q', 'q'])
    if board_obj['castle_info'] == '----':
        return {}
    if are_we_in_check(board_obj):
        return {}
    return castle_work(castle_dir(board_obj['moves'] % 2))
    #return {'O-O': {"moves": "bogus king side castle"},
    #        'O-O-O': {"moves": "bogus queen side castle"}}
