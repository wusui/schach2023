from conv_to_bobj import conv_to_bobj
from gen_moves import gen_moves

def c_solver(board_obj):
    mlist = gen_moves(board_obj)
    return board_obj

def solver(layout):
    return c_solver(conv_to_bobj(layout))

if __name__ == '__main__':
    print(solver('2/W:b6,Ra1,Kc8/B:a7,b7,Ka8,Bb8'))
