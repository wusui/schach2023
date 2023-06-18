# Copyright (C) 2023 Warren Usui, MIT License
"""
Handle pawn promotion and castling
"""
import itertools

from conv_to_bobj import list_to_board, alg_square_to_lindx
from make_moves import board_to_linear

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
    return {'O-O': {"moves": "bogus king side castle"},
            'O-O-O': {"moves": "bogus queen side castle"}}
