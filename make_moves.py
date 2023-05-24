# Copyright (C) 2023 Warren Usui, MIT License
"""
Make moves on the board
"""
import itertools
from conv_to_bobj import conv_to_bobj, get_sp_coord

def are_they_in_check(board_obj):
    """
    Determine if opponent is in check at start of move.  This means that
    the previous move made was illegal.
    """
    return list(filter(None, find_moves(board_obj)(['K'])))

def find_moves(board_obj):
    """
    Find moves.  If sq_info (inner function parameter) is K or k, use the
    location of that k as the square to move to.  Otherwise, sq_info
    should be the coordinates of the square to which we are finding moves.
    """
    def find_moves_inner(sq_info):
        def set_side_ind(mpos):
            def atic_inner(lin_board):
                def find_ek():
                    return lin_board.index(['K', 'k'][mpos])
                def get_coords(indx):
                    return [indx // 8, indx % 8]
                def set_kloc(kcoord):
                    def find_us(sq_val):
                        if mpos == 1:
                            return sq_val.isupper()
                        return sq_val.islower()
                    def find_our_locs(our_loc_bits):
                        def get_ourp(indx):
                            if our_loc_bits[indx]:
                                return [get_coords(indx), lin_board[indx]]
                            return False
                        return make_a_move([board_obj, kcoord,
                                        list(filter(lambda a: a,
                                        list(map(get_ourp, range(64)))))])
                    return find_our_locs(list(map(find_us, lin_board)))
                if len(sq_info)  == 1:
                    return set_kloc(get_coords(find_ek()))
                return set_kloc(sq_info)
            return atic_inner(list(itertools.chain.from_iterable(
                               board_obj['board'])))
        return set_side_ind(board_obj['moves'] % 2)
    return find_moves_inner

def pnts_between(two_points):
    """
    List points in line between two coordinate points
    """
    def set_dxy(dxy):
        def s1off(value):
            if value == 0:
                return value
            return value // abs(value)
        def set_offset(offst):
            def plt_pt(indx):
                return [two_points[0][0] + offst[0] * indx,
                        two_points[0][1] + offst[1] * indx]
            return list(map(plt_pt, range(1, max(abs(dxy[0]),abs(dxy[1])))))
        return set_offset([s1off(dxy[0]), s1off(dxy[1])])
    return set_dxy([two_points[1][0] - two_points[0][0],
                   two_points[1][1] - two_points[0][1]])

def make_a_move(info):
    """
    Return a list of moves possible
    """
    def set_board(board_obj):
        def opp_cases(squares):
            if board_obj['board'][squares[0][0]][squares[0][1]] == ' ':
                return False
            if board_obj['board'][squares[1][0]][squares[1][1]] == ' ':
                return False
            if board_obj['board'][squares[0][0]][squares[0][1]].isupper() ==\
                    board_obj['board'][squares[1][0]][squares[1][1]].isupper():
                return False
            return True
        def set_tosq_coords(tosq_coords):
            def ep_check(from_to):
                if abs(from_to[0][1] - from_to[1][1]) != 1:
                    return False
                if from_to[0][0] != {2:3, 5:4}[from_to[1][0]]:
                    return False
                return [from_to[0], from_to[1], 'ep']
            def analyze(piece):
                def offsets(dloc):
                    if board_obj['board'][dloc[0]][dloc[1]] == ' ':
                        return False
                    return True
                def not_all_clear_between(aloc):
                    return list(filter(offsets, pnts_between(
                               [aloc, tosq_coords])))
                def rook_move_works(aloc):
                    if aloc[0] - tosq_coords[0] != 0 and (
                                aloc[1] - tosq_coords[1] != 0):
                        return False
                    if not_all_clear_between(aloc):
                        return False
                    return [aloc, tosq_coords]
                def bishop_move_works(aloc):
                    if abs(aloc[0] - tosq_coords[0]) != abs(
                           aloc[1] - tosq_coords[1]):
                        return False
                    if not_all_clear_between(aloc):
                        return False
                    return [aloc, tosq_coords]
                def ksolve(aloc):
                    if max([abs(aloc[0] - tosq_coords[0]), abs(
                           aloc[1] - tosq_coords[1])]) < 2:
                        return [aloc, tosq_coords]
                    return False
                def qsolve(aloc):
                    return rook_move_works(aloc) or bishop_move_works(aloc)
                def rsolve(aloc):
                    if rook_move_works(aloc):
                        return([aloc, tosq_coords])
                    return False
                def bsolve(aloc):
                    if bishop_move_works(aloc):
                        return([aloc, tosq_coords])
                    return False
                def nsolve(aloc):
                    if sorted([abs(aloc[0] - tosq_coords[0]), abs(
                           aloc[1] - tosq_coords[1])]) == [1, 2]:
                        return [aloc, tosq_coords]
                    return False
                def psolve(aloc):
                    def pdirect(pdir):
                        def pwdtpos(dmv_row):
                            if tosq_coords[1] == aloc[1]:
                                if tosq_coords[0] == aloc[0] + pdir and \
                                        board_obj['board'][tosq_coords[0]] \
                                        [tosq_coords[1]] == ' ':
                                    return [aloc, tosq_coords]
                                if tosq_coords[0] == dmv_row and \
                                        tosq_coords[0] == aloc[0] + 2 * pdir \
                                        and board_obj['board'] \
                                        [tosq_coords[0]][tosq_coords[1]] == \
                                        ' ' and board_obj['board'] \
                                        [tosq_coords[0]][tosq_coords[1] - \
                                        pdir] == ' ':
                                    return [aloc, tosq_coords]
                            if abs(tosq_coords[1] - aloc[1]) == 1 and \
                                    tosq_coords[0] == aloc[0] + pdir:
                                if opp_cases([aloc, tosq_coords]):
                                    return [aloc, tosq_coords]
                            if board_obj['ep_square'] != '-':
                                return ep_check([aloc, get_sp_coord(
                                        board_obj['ep_square'])])
                            return False
                        return pwdtpos([4, 3][(pdir + 1) // 2])
                    return pdirect([-1, 1][board_obj['moves'] % 2])
                return {'K': ksolve, 'Q': qsolve, 'R': rsolve,
                        'B': bsolve, 'N': nsolve, 'P': psolve
                       }[piece[1]](piece[0])
            def opinfo(our_pcs):
                return list(map(analyze, our_pcs))
            return opinfo(info[2])
        # TO DO: Handle pawn promotion
        # TO DOL Handle castling
        return set_tosq_coords(info[1])
    return set_board(info[0])

if __name__ == "__main__":
    print(are_they_in_check(
        conv_to_bobj('2/W:b6,Ra1,Kc8/B:a7,b7,Ka8,Bb8')))
    print(are_they_in_check(
        conv_to_bobj('2/W:Kc8/B:Kd7,Bb8')))
    print(are_they_in_check(
        conv_to_bobj('2/W:Ka1,Bh1,Nf3/B:Ka8')))
    print(are_they_in_check(
        conv_to_bobj('2/W:Ka1,Nh1/B:Kg3')))
    print(are_they_in_check(
        conv_to_bobj('2/W:Ka1,Rh3/B:Kg3')))
    print(are_they_in_check(
        conv_to_bobj('2/W:Ka1,Qa3,Bh1/B:Ka8')))
    print(are_they_in_check(
        conv_to_bobj('2/W:Ka1,b5,Nh1/B:Ka6')))
