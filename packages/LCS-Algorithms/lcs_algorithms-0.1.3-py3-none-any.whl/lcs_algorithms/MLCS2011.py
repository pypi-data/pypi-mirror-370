def generate_transition_matrix(S, Sigma):
    """
    Generates the transition matrix for the given sequences and alphabet.
    
    Parameters:
    S (list of strings): The input sequences.
    Sigma (set): The alphabet.
    
    Returns:
    dict: The transition matrix.
    """
    T = {e: [[] for _ in range(len(S))] for e in Sigma}
    for seq_idx, seq in enumerate(S):
        next_pos = {e: len(seq) for e in Sigma}
        for i in reversed(range(len(seq) + 1)):
            for e in Sigma:
                if i < len(seq):
                    T[e][seq_idx].append(next_pos[e])
                if i > 0 and seq[i-1] == e:
                    next_pos[e] = i - 1
        for e in Sigma:
            T[e][seq_idx].reverse()
    return T

def parents(q, e, T):
    p = [0] * len(q)
    for i in range(len(q)):
        if q[i]+1<len(T[e][i]):
            p[i] = T[e][i][q[i]+1]
        else:
            p[i] = len(T[e][i])
            #print("Error\t",e,p,q,i)
    return tuple(p)

def gen_Pars(Sigma,d):
    Pars={Sigma[0]: {(-1,) * d}}
    for e in Sigma:
        Pars[e] = set()
    return Pars


def genDzero(d,T,Sigma):
    D = {0: {(-1,) * d}}
    D[0]=set()
    p = [0] * d
    for i,e in enumerate(Sigma):
        for j in range(d):
            p[j]=T[e][j][0]
        #print(p)
        D[0].add(tuple(p))
    #print("D before max\t",D)    
    D[0]=removeMax(D[0])
    return D

def find_child(e,ary):
    for elem in ary:
        for i in range(len(e)):
            if(e[i]<=elem[i]):
                break
            elif(i==len(e)-1):
                return elem

def removeMax(ary):
    for elem in ary.copy():
        #print("Chiled of ",elem," is ",find_child(elem,ary))
        if(find_child(elem,ary)):
            ary.remove(elem)
    return ary

def validVal(ary,n):
    return max(ary)<n

def lcs_back(D,sequences):
    maxd=0
    lcs_result = []
    K=len(D)-2
    if(len(D)<2):
        return lcs_result
    if(len(D[len(D)-2])):
        return lcs_result
    element=D[K].pop()
    #find_child(e,ary)
    for k in range(len(D)-3,-1,-1):
        if(maxd<len(D[k])):
            maxd=len(D[k])
        #print("Finding",element,D[k])
        element=find_child(element,list(D[k]))
        #print(element)
        if(element):
            lcs_result=[sequences[0][element[0]]]+lcs_result
    #print(maxd)
    return lcs_result

def generateD_MLCS2011(sequences,Sigma):
    d = len(sequences)
    k = 0
    #print("Pars",Pars)
    #Pars = set()
    n=max([len(s) for s in sequences])
    T = generate_transition_matrix(sequences, Sigma)
    #print(sequences)
    #print(T)
    D=genDzero(d,T,Sigma)
    #print("D zero\t",D)
    while D[k]:
        D[k + 1] = set()
        Pars=gen_Pars(Sigma,d)
        for q in D[k]:
            Parall=set()
            for e in Sigma:
                p = parents(q, e, T)
                #print(e," Parent of ",q," is ",p)
                if validVal(p,n):
                    Parall.add(p)
            B=removeMax(Parall)
            #print("B\t",B)
            for p in B:
                #if p not in D[k] and validVal(p,n):
                e=sequences[0][p[0]]
                #print(k,p,e)
                Pars[e].add(p)
                #print("Pars\t",Pars)
        for pare in Pars:
            #print("All parents\t",Pars)
            #print("Processing",pare,"\t",Pars[pare])
            
            Pars[pare]=removeMax(Pars[pare])
            
            #print("Non Max Parents\t",Pars)
            for elem in Pars[pare]:
                D[k + 1].add(elem)
        #print("D when k is\t",k,"\t",D)
        D[k+1]=removeMax(D[k+1])
        #print("D when k is\t",k+1,"\t",len(D[k+1]))
        k += 1
        if(k>n):
            break
    return D
def mlcsdpa(sequences,Sigma):
    D=generateD_MLCS2011(sequences,Sigma)
    return lcs_back(D,sequences)