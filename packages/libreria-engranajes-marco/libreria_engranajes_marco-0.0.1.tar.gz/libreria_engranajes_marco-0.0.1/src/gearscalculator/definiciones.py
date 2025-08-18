def num_diente (de,m):
    z=float((de/m)-2)
    return z

def altura_diente(m):
    h=float(m*2.25)
    return h

def diametro_primitivo(m,z):
    dp=float(m*z)
    return dp

def diametro_interior(de,h):
    di=float(de-2*h)
    return di
def paso(m):
    p=float(m*3.1416)
    return p

def espesor(p):
    e=float(0.5*p)
    return e
def distancia_centros(z1,z2,m):
    a=float(m*((z1+z2)/2))
    return a