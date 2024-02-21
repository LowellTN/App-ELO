from math import *
from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from random import *
import os

def fr(nj1,nj2):
    p = 0
    if nj1 != 0 and nj2 != 0:
        p = nj1/(nj2+nj1)
    else:
        p = 0.5
    return p/(1-p)


def pg(nj1,nj2):
    return fr(nj1,nj2)/(1+fr(nj1,nj2))

def D(nj1,nj2):
    return 400*log10(fr(nj1,nj2))

def pD(nj1,nj2):
    return 1/(1+10**(-(D(nj1,nj2))/400))

def nelo(nj1,nj2,W,K):
    return nj1 + K*(W-pD(nj1,nj2))


def gentree(pl):
    tree_data = {}
    mpr= len(pl) // 2
    tl = pl[:]
    for rnum in range(1, len(tl)):
        rname = f"Round{rnum}"
        tree_data[rname] = []

        for mnum in range( mpr):
            mname = f"Match{mnum+1}"
            players = [tl[2*mnum][0], tl[2*mnum+1][0]]
            players_elo = [tl[2*mnum], tl[2*mnum+1]]
            tree_data[rname].append({mname: players})
        
        for match in tree_data[rname]:
            mname, players = list(match.items())[0]
            perdant = input(f"{rname}, {mname} - Saisir le perdant ({players[0]} ou {players[1]}): ")
            while perdant not in [players[0],players[1]]:
                perdant = input(f"Joueur invalide : {rname}, {mname} - Saisir le perdant ({players[0]} ou {players[1]}): ")
            match[mname] = [perdant]
            for k in range(len(tl)-1):
                if tl[k][0] == perdant:
                    tl.pop(k)

        mpr //= 2
        if mpr == 1:
            rnum +=1
            rname = f"round{rnum}"
            tree_data[rname] = []
            mname = f"finale"
            players = [tl[0][0], tl[1][0]]
            tree_data[rname].append({mname: players})
            gagnant = input(f"Saisir le grand gagnant du tournoi ({players[0]} ou {players[1]}): ")
            while gagnant not in players:
                gagnant = input(f"Joueur invalide : Saisir le grand gagnant du tournoi ({players[0]} ou {players[1]}): ")
            break
    
    return tree_data, f"Le grand gagnant est {gagnant} !!!"


def update_elo(player1, elo1, K1, player2, elo2, K2, winner):

    if winner == None:
        outcome1 = 0.5
        outcome2 = 0.5
    elif winner == player1:
        outcome1 = 1.0
        outcome2 = 0.0
    elif winner == player2:
        outcome1 = 0.0
        outcome2 = 1.0

    elo1 = int(round(nelo(elo1,elo2,outcome1,K1),0))
    elo2 = int(round(nelo(elo2,elo1,outcome2,K2),0))

    return [elo1,elo2]

def seeding(J):
    L = J[:]
    seed = [0 for i in range(len(J))]
    while 0 in seed:
        for i in range(len(seed)):
            if i%2==0:
                m = max([l[1] for l in L])
                for k in L:
                    if k[1] == m:
                        seed[i]=k
                        L.remove(k)
                        break
            else:
                m = min([l[1] for l in L])
                for k in L:
                    if k[1] == m:
                        seed[i]=k
                        L.remove(k)
                        break
    return seed


def vark(np,rg,k):
    w = False
    if np <= 20:
        k = 40
    elif np <= 30:
        k = 30
    else:
        cs = 1
        lg = 0
        for rp in range(len(rg)):
            if rg[rp] == 1:
                k += cs
                if lg == rg[rp]:
                    w = True
                    cs += 1
                else:
                    w = False
                    cs += 1
                lg = 1
            elif rg[rp] == -1:
                if lg == rg[rp]:
                    w = True
                    cs += 1
                else:
                    w = False
                    cs = 1
                lg = -1
                k -= cs
            else :
                lg = 0
            rp -= 1
    return k
            


            

        



if __name__ == "__main__":
    L=[0,1,-1,1,1,1,-1,0,1,-1,1]
    print(vark(42,L,26))

