# -*- coding: utf-8 -*-
"""
Created on Tue Aug 08 16:21:18 2017

@author: rmillet
@source: http://files.magusgeek.com/csb/csb.html
"""

import math
import random

SHIELD_PROB = 20
SHIELD = -1


class Solution(object):
    """
    """
    def __init__(self, moves1, moves2, **kwargs):
        super().__init__(**kwargs)
        self.moves1 = moves1
        self.moves2 = moves2

    @property
    def moves1(self):
        return self.moves1

    @moves1.setter
    def moves1(self, a):
        self.moves1 = a

    @property
    def moves2(self):
        return self.moves2

    @moves2.setter
    def moves2(self, a):
        self.moves2 = a

#    def score(self):
#        """
#        La methode va simuler sur le nombre de tours voulus la solution, et utiliser la fonction d evaluation a la fin de la simulation pour connaitre le score de la solution.
#        """
#        # on joue les tours
#        for i in range(len(self.moves1)):
#            # on applique les mouvements aux pods avant de jouer
#            myPod1.apply(self.moves1[i])
#            myPod2.apply(self.moves2[i])
#            play()
#        # on calcul le score
#        result = evaluation()
#        # on remet tout le monde au point de depart
#        load()
#        return result


class Move(Solution):
    """
    """
    def __init__(self, angle, thrust, **kwargs):
        super().__init__(**kwargs)
        self.angle = angle  # entre -18.0 et +18.0
        self.thrust = thrust  # entre -1 et 200

    @property
    def angle(self):
        return self.angle

    @angle.setter
    def angle(self, a):
        self.angle = a

    @property
    def thrust(self):
        return self.thrust

    @thrust.setter
    def thrust(self, a):
        self.thrust = a

    def mutate(self, amplitude):
        """
        Il existe 2 facons de faire evoluer une solution.
        Soit par mutation, soit par croisement.
        La mutation se resume a prendre un ou plusieurs mouvements au hasard dans une solution deja existante et a changer ce mouvement aleatoirement.
        Le croisement consiste a prendre 2 solutions et creer une (ou plusieurs parfois) nouvelle solution en piochant des mouvements au hasard entre les 2 solutions.
        Mais attention, il ne faut pas le faire n importe comment.
        Pour que l evolution marche correctement, il faut d abord faire de "grandes" evolutions et plus on avance, plus on fait de petites evolutions.
        Comme le code le montre, j ai un parametre amplitude qui me sert a "doser" a quel point je veux faire muter aleatoirement un Move.
        Au debut du tour de mon IA, ce parametre est a 1.0 pour avoir des mutations maximales.
        Et plus j avance dans mes evolutions et mes simulations, plus il devient petit avec un minimum de 0.1 a la fin du tour.
        Cela permet d avoir les meilleurs resultats avec l evolution.
        """
        ramin = self.angle - 36.0 * amplitude
        ramax = self.angle + 36.0 * amplitude
        if ramin < -18.0:
            ramin = -18.0
        if ramax > 18.0:
            ramax = 18.0
        self.angle = float(random.randint(ramin, ramax))
        if not self.shield and random.randint(0, 100) < SHIELD_PROB:
            self.shield = True
        else:
            pmin = self.thrust - 200 * amplitude
            pmax = self.thrust + 200 * amplitude
            if pmin < 0:
                pmin = 0
            if pmax > 0:
                pmax = 200
            self.thrust = random.randint(pmin, pmax)
            self.shield = False


class Collision(object):
    """
    Represente une collision entre 2 Unit avec l instant t auquel la collision va arriver.
    """
    def __init__(self, a, b, t, **kwargs):
        super().__init__(**kwargs)
        self.a = a
        self.b = b
        self.t = t

    @property
    def a(self):
        return self.a

    @a.setter
    def a(self, a):
        self.a = a

    @property
    def b(self):
        return self.b

    @b.setter
    def b(self, a):
        self.b = a

    @property
    def t(self):
        return self.t

    @t.setter
    def t(self, a):
        self.t = a


class Point(object):
    """
    Cette classe sert uniquement a representer un point sur la carte.
    Je fais heriter la plupart de mes classes de Point car c est beaucoup plus simple pour la suite.
    """
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y

    @property
    def x(self):
        return self.x

    @x.setter
    def x(self, a):
        self.x = a

    @property
    def y(self):
        return self.y

    @y.setter
    def y(self, a):
        self.y = a

    def distance2(self, point):
        return (self.x - point.x)*(self.x - point.x) + (self.y - point.y)*(self.y - point.y)

    def distance(self, point):
        """
        Pourquoi 2 fonctions de distance ?
        Tout simplement parce math.sqrt est lent, quelque soit le langage.
        Il vaut mieux l eviter si on en a pas vraiment besoin.
        Et parfois on a besoin de la distance au carre dans certains calculs, donc on appellera distance2 directement.
        """
        return math.sqrt(self.distance2(point))

    def closest(self, pointA, pointB):
        """
        Nous rentrons maintenant dans la partie la plus complique pour simuler un tour completement : les collisions.
        Nous avons 2 objets de classe Unit et nous voulons savoir si et quand ces 2 objets vont entrer en collision dans le tour.
        C est ce que fait la methode collision de Unit.
        Mais avant d entrer dans le code en detail, un peu de theorie.
        Deja il y a des collisions qu on peut detecter immediatement car les 2 objets sont deja assez proches l un de l autre.
        Si la distance entre les 2 objets est inferieure a la somme des rayons, alors on a une collision immediatement.
        Ensuite, comment detecter que 2 objets en mouvement vont entrer en collision ?
        Deja on peut simplifier le probleme.
        Il faut changer de referentiel et se placer dans le referentiel de l une des 2 unites.
        De cette façon le probleme est plus simple : comment detecter qu un objet en mouvement va entrer en collision avec un objet immobile ?
        C est la qu entre en jeu la geometrie.
        L objet qui se deplace le fait forcement sur une droite.
        Pour savoir si les objets vont entrer en collision, il faut regarder la distance entre notre objet immobile et son point le plus proche sur cette droite.
        Si cette distance est inferieur a la somme des rayons des 2 objets, alors nous avons une chance de collision.
        Pour confirmer cette chance de collision, il faut ensuite regarder la vitesse de l objet qui se deplace (pour verifier s il s eloigne ou s il se rapproche de l objet immobile).
        Et s il se rapproche il faut regarder dans combien de temps il va atteindre l objet immobile.
        Si une collision se passe a un temps t superieur a 1.0, cela veut dire qu elle se passera dans plus d un tour et on peut donc l ignorer.
        La méthode permet de trouver le point le plus proche sur une droite (decrite ici par 2 points) depuis un point.
        """
        da = pointB.y - pointA.y
        db = pointA.x - pointB.x
        c1 = da*pointA.x + db*pointA.y
        c2 = -db * self.x + da*self.y
        det = da * da + db * db
        cx = 0
        cy = 0
        if det != 0:
            cx = (da*c1 - db*c2)/det
            cy = (da*c2 + db*c1)/det
        else:  # le point est deja sur la droite
            cx = self.x
            cy = self.y
        return Point(cx, cy)


class Unit(Point):
    """
    Une classe que j ai cree sur Poker Chip Race au depart mais que j ai utilise presque telle quelle pour ce contest.
    Elle represente simplement une "unite" sur le jeu qui possede un identifiant unique, un rayon, une vitesse sur x et une vitesse sur y.
    Elle herite de Point pour avoir les attributs x et y, mais aussi pour que ce soit beaucoup plus pratique dans certaines fonctions.
    """
    def __init__(self, id, r, vx, vy, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.r = r
        self.vx = vx
        self.vy = vy

    @property
    def id(self):
        return self.id

    @id.setter
    def id(self, a):
        self.id = a

    @property
    def r(self):
        return self.r

    @r.setter
    def r(self, a):
        self.r = a

    @property
    def vx(self):
        return self.vx

    @vx.setter
    def vx(self, a):
        self.vx = a

    @property
    def vy(self):
        return self.vy

    @vy.setter
    def vy(self, a):
        self.vy = a

    def collision(self, unit):
        dist = self.distance2(unit)  # distance carre
        sr = (self.r + unit.r)*(self.r + unit.r)  # somme des rayons au carre
        # on prend tout au carre pour eviter d avoir a appeler un sqrt inutilement
        # c est mieux pour les performances
        if dist < sr:
            # les objets sont deja l un sur l autre, on a donc une collision immediate
            return Collision(self, unit, 0.0)
        # optimisation
        # les objets ont la meme vitesse ils ne pourront jamais se rentrer dedans
        if self.vx == unit.vx and self.vy == unit.vy:
            return None
        # on se met dans le referentiel de unit
        # unit est donc immobile et se trouve sur le point (0,0) apres ça
        x = self.x - unit.x
        y = self.y - unit.y
        myp = Point(x, y)
        vx = self.vx - unit.vx
        vy = self.vy - unit.vy
        up = Point(0, 0)
        # on cherche le point le plus proche de unit (qui est donc en (0,0)) sur la droite decrite par notre vecteur de vitesse
        p = up.closest(myp, Point(x + vx, y + vy))
        # distance au carre entre unit et le point le plus proche sur la droite decrite par notre vecteur de vitesse
        pdist = up.distance2(p)
        # distance au carre entre nous et ce point
        mypdist = myp.distance2(p)
        # si la distance entre unit et cette droite est inferieur a la somme des rayons, alors il y a possibilite de collision
        if pdist < sr:
            # notre vitesse sur la droite
            length = math.sqrt(vx*vx + vy*vy)
            # on deplace le point sur la droite pour trouver le point d impact
            backdist = math.sqrt(sr - pdist)
            p.x = p.x - backdist*(vx/length)
            p.y = p.y - backdist*(vy/length)
            # si le point s est eloigne de nous par rapport a avant, c est que notre vitesse ne va pas dans le bon sens
            if myp.distance2(p) > mypdist:
                return None
            pdist = p.distance(myp)
            # le point d impact est plus loin que ce qu on peut parcourir en un seul tour
            if pdist > length:
                return None
            # temps necessaire pour atteindre le point d impact
            t = pdist / length
            return Collision(self, unit, t)
        return None

    def bounce(self, unit):
        """
        Ici il faut separer plusieurs types de collision.
        Il y a d abord une collision tres simple a gerer, c est celle d un Pod avec un Checkpoint.
        Il n y a pas de rebond, on doit juste s assurer d incrementer le compteur des checkpoints passes pour le pod et de remettre le timeout du pod a 100.
        Maintenant le cas complexe : 2 pods se rentrent dedans.
        Les collisions dans ce contest sont des collisions elastiques parfaites avec une demi impulsion de 120 minimum.
        Attention : Cette methode repose sur l hypothese que les 2 pods se sont deplaces jusqu a leur point d impact respectifs.
        """
        # si un pod a son bouclier d active, sa masse est de 10, sinon elle est de 1
        m1 = 10 if self.shield else 1
        m2 = 10 if unit.shield else 1
        # si les masses sont egales, le coefficient sera de 2
        # sinon il sera de 11/10
        mcoeff = (m1+m2)/(m1*m2)
        nx = self.x - unit.x
        ny = self.y - unit.y
        # distance au carre entre les 2 pods
        # cette valeur pourrait etre ecrite en dure car ce sera toujours 800²
        nxnysquare = nx*nx + ny*ny
        dvx = self.vx - unit.vx
        dvy = self.vy - unit.vy
        # fx et fy sont les composantes du vecteur d impact
        # product est juste la pour optimiser
        product = nx*dvx + ny*dvy
        fx = (nx * product) / (nxnysquare * mcoeff)
        fy = (ny * product) / (nxnysquare * mcoeff)
        # on applique une fois le vecteur d impact a chaque pod proportionnellement a sa masse
        self.vx = self.vx - fx / m1
        self.vy = self.vy - fy / m1
        unit.vx = unit.vx + fx / m2
        unit.vy = unit.vy + fy / m2
        # si la norme du vecteur d impact est inferieur a 120, on change sa norme pour le mettre a 120
        impulse = math.sqrt(fx*fx + fy*fy)
        if impulse < 120.0:
            fx = fx * 120.0 / impulse
            fy = fy * 120.0 / impulse
        # on applique une deuxieme fois le vecteur d impact a chaque pod proportionnellement a sa masse
        self.vx = self.vx - fx / m1
        self.vy = self.vy - fy / m1
        unit.vx = unit.vx + fx / m2
        unit.vy = unit.vy + fy / m2
        # c est l un des rares endroits où avoir une classe Vector aurait rendu le code beaucoup plus lisible.
        # mais cet endroit est appelle beaucoup trop souvent dans mon code pour que je me permette de le rendre plus lisible au prix de la performance


class Checkpoint(Unit):
    """
    Represente un checkpoint sur le jeu.
    """
    def bounce(self, unit):
        """
        Ici il faut separer plusieurs types de collision.
        Il y a d abord une collision tres simple a gerer, c est celle d un Pod avec un Checkpoint.
        Il n y a pas de rebond, on doit juste s assurer d incrementer le compteur des checkpoints passes pour le pod et de remettre le timeout du pod a 100.
        Maintenant le cas complexe : 2 pods se rentrent dedans.
        Les collisions dans ce contest sont des collisions elastiques parfaites avec une demi impulsion de 120 minimum.
        Attention : Cette methode repose sur l hypothese que les 2 pods se sont deplaces jusqu a leur point d impact respectifs.
        """
        if isinstance(unit, Checkpoint):
            # on entre en collision avec un checkpoint
            self.bounce(unit)
        else:
            # si un pod a son bouclier d active, sa masse est de 10, sinon elle est de 1
            m1 = 10 if self.shield else 1
            m2 = 10 if unit.shield else 1
            # si les masses sont egales, le coefficient sera de 2
            # sinon il sera de 11/10
            mcoeff = (m1+m2)/(m1*m2)
            nx = self.x - unit.x
            ny = self.y - unit.y
            # distance au carre entre les 2 pods
            # cette valeur pourrait etre ecrite en dure car ce sera toujours 800²
            nxnysquare = nx*nx + ny*ny
            dvx = self.vx - unit.vx
            dvy = self.vy - unit.vy
            # fx et fy sont les composantes du vecteur d impact
            # product est juste la pour optimiser
            product = nx*dvx + ny*dvy
            fx = (nx * product) / (nxnysquare * mcoeff)
            fy = (ny * product) / (nxnysquare * mcoeff)
            # on applique une fois le vecteur d impact a chaque pod proportionnellement a sa masse
            self.vx = self.vx - fx / m1
            self.vy = self.vy - fy / m1
            unit.vx = unit.vx + fx / m2
            unit.vy = unit.vy + fy / m2
            # si la norme du vecteur d impact est inferieur a 120, on change sa norme pour le mettre a 120
            impulse = math.sqrt(fx*fx + fy*fy)
            if impulse < 120.0:
                fx = fx * 120.0 / impulse
                fy = fy * 120.0 / impulse
            # on applique une deuxieme fois le vecteur d impact a chaque pod proportionnellement a sa masse
            self.vx = self.vx - fx / m1
            self.vy = self.vy - fy / m1
            unit.vx = unit.vx + fx / m2
            unit.vy = unit.vy + fy / m2
            # c est l un des rares endroits où avoir une classe Vector aurait rendu le code beaucoup plus lisible.
            # mais cet endroit est appelle beaucoup trop souvent dans mon code pour que je me permette de le rendre plus lisible au prix de la performance


class Pod(Unit):
    """
    Represente un pod sur le jeu.
    Avec une angle, l identifiant du prochain checkpoint, le nombre de checkpoints que ce pod a deja passe, le nombre de tours avant son timeout, et son pod partenaire.
    """
    def __init__(self, angle, netCheckPointId, checked, timeout, partner, shield, **kwargs):
        super().__init__(**kwargs)
        self.angle = angle
        self.netCheckPointId = netCheckPointId
        self.checked = checked
        self.timeout = timeout
        self.partner = partner
        self.shield = shield

    @property
    def angle(self):
        return self.angle

    @angle.setter
    def angle(self, a):
        self.angle = a

    @property
    def netCheckPointId(self):
        return self.netCheckPointId

    @netCheckPointId.setter
    def netCheckPointId(self, a):
        self.netCheckPointId = a

    @property
    def checked(self):
        return self.checked

    @checked.setter
    def checked(self, a):
        self.checked = a

    @property
    def timeout(self):
        return self.timeout

    @timeout.setter
    def timeout(self, a):
        self.timeout = a

    @property
    def partner(self):
        return self.partner

    @partner.setter
    def partner(self, a):
        self.partner = a

    @property
    def shield(self):
        return self.shield

    @shield.setter
    def shield(self, a):
        self.shield = a

    def getAngle(self, point):
        """
        Pour savoir comment un pod va tourner, il faut deja savoir la difference d angle entre l angle actuel du pod et le point vise.
        L angle actuel du pod est donne dans les inputs du programme entre 0 et 359.
        0 veut dire que le pod regarde plein est.
        90 c est plein sud.
        180 plein ouest.
        Et enfin 270 plein nord.
        """
        d = self.distance(point)
        dx = (point.x - self.x) / d
        dy = (point.y - self.y) / d
        # trigonometrie simple.
        # on multiplie par 180.0 / PI pour convertir en degre.
        a = math.acos(dx) * 180.0 / math.pi
        # si le point qu on veut est en dessus de nous, il faut decaler l angle pour qu il soit correct.
        if dy < 0:
            a = 360.0 - a
        return a

    def diffAngle(self, point):
        """
        Cette fonction renvoie l angle que devrait avoir le pod pour faire face au point donne.
        Donc si le point se trouve par exemple exactement en haut a droite du pod, cette fonction donnera 315.
        Il faut ensuite savoir de combien (et dans quel sens) le pod doit tourner pour viser ce point.
        """
        a = self.getAngle(point)
        # pour connaitre le sens le plus proche, il suffit de regarder dans les 2 sens et on garde le plus petit
        # Les operateurs ternaires sont la uniquement pour eviter l utilisation d un operateur % qui serait plus lent
        right = a - self.angle if self.angle <= a else 360.0 - self.angle + a
        left = self.angle - a if self.angle >= a else self.angle + 360.0 - a
        if right < left:
            return right
        else:
            # on donne un angle negatif s il faut tourner a gauche
            return -left

    def rotate(self, point):
        """
        Nous avons donc un angle et un sens pour tourner vers un point.
        Le sens est donne par le signe du resultat.
        S il est negatif, alors on doit tourner vers la gauche, sinon c est vers la droite.
        Il ne reste plus qu a vraiment tourner.
        """
        a = self.diffAngle(point)
        # on ne peut pas tourner de plus de 18° en un seul tour
        if a > 18.0:
            a = 18.0
        elif a < -18.0:
            a = -18.0
        self.angle = self.angle + a
        # l operateur % est lent.
        # si on peut l eviter, c est mieux.
        if self.angle >= 360.0:
            self.angle = self.angle - 360.0
        elif self.angle < 0.0:
            self.angle = self.angle + 360.0

    def boost(self, thrust):
        """
        Une fois que le pod a tourne, il faut maintenant appliquer le thrust.
        """
        # n oubliez pas qu un pod qui a active un shield ne peut pas accelerer pendant 3 tours
        if self.shield:
            return
        # conversion de l angle en radian
        ra = self.angle * math.pi / 180.0
        # trigonometrie
        self.vx = self.vx + math.cos(ra) * thrust
        self.vy = self.vy + math.sin(ra) * thrust

    def move(self, t):
        """
        A quoi sert le parametre t ?
        Il servira plus tard quand on voudra simuler un tour entier en prenant en compte les collisions.
        Il sert a indiquer de combien le pod doit avancer.
        Si t vaut 1.0, alors le pod va avancer d un tour entier.
        S il vaut 0.5, alors il n avancera que de la moitie d un tour.
        Si vous ne simulez pas les collisions, alors vous pouvez toujours mettre 1.0 a la place de t.
        """
        self.x = self.x + self.vx * t
        self.y = self.y + self.vy * t

    def end(self):
        """
        Une fois que le pod s est deplace, il faut appliquer la friction et arrondir (ou tronquer) des valeurs
        """
        self.x = round(self.x)
        self.y = round(self.y)
        self.vx = int(self.vx * 0.85)
        self.vy = int(self.vy * 0.85)
        # n oubliez pas que le timeout descend de 1 chaque tour.
        # il revient a 100 quand on passe par un checkpoint
        self.timeout = self.timeout - 1

    def play(self, point, thrust):
        """
        Vous etes maintenant capable de faire jouer le deplacement complet d un pod et donc predire a quelle position un pod sera au prochain tour s il vise un point specifique.
        """
        self.rotate(point)
        self.boost(thrust)
        self.move(1.0)
        self.end()

    def bounce(self, unit):
        """
        Ici il faut separer plusieurs types de collision.
        Il y a d abord une collision tres simple a gerer, c est celle d un Pod avec un Checkpoint.
        Il n y a pas de rebond, on doit juste s assurer d incrementer le compteur des checkpoints passes pour le pod et de remettre le timeout du pod a 100.
        Maintenant le cas complexe : 2 pods se rentrent dedans.
        Les collisions dans ce contest sont des collisions elastiques parfaites avec une demi impulsion de 120 minimum.
        Attention : Cette methode repose sur l hypothese que les 2 pods se sont deplaces jusqu a leur point d impact respectifs.
        """
        if isinstance(unit, Checkpoint):
            # on entre en collision avec un checkpoint
            self.bounce(unit)
        else:
            # si un pod a son bouclier d active, sa masse est de 10, sinon elle est de 1
            m1 = 10 if self.shield else 1
            m2 = 10 if unit.shield else 1
            # si les masses sont egales, le coefficient sera de 2
            # sinon il sera de 11/10
            mcoeff = (m1+m2)/(m1*m2)
            nx = self.x - unit.x
            ny = self.y - unit.y
            # distance au carre entre les 2 pods
            # cette valeur pourrait etre ecrite en dure car ce sera toujours 800²
            nxnysquare = nx*nx + ny*ny
            dvx = self.vx - unit.vx
            dvy = self.vy - unit.vy
            # fx et fy sont les composantes du vecteur d impact
            # product est juste la pour optimiser
            product = nx*dvx + ny*dvy
            fx = (nx * product) / (nxnysquare * mcoeff)
            fy = (ny * product) / (nxnysquare * mcoeff)
            # on applique une fois le vecteur d impact a chaque pod proportionnellement a sa masse
            self.vx = self.vx - fx / m1
            self.vy = self.vy - fy / m1
            unit.vx = unit.vx + fx / m2
            unit.vy = unit.vy + fy / m2
            # si la norme du vecteur d impact est inferieur a 120, on change sa norme pour le mettre a 120
            impulse = math.sqrt(fx*fx + fy*fy)
            if impulse < 120.0:
                fx = fx * 120.0 / impulse
                fy = fy * 120.0 / impulse
            # on applique une deuxieme fois le vecteur d impact a chaque pod proportionnellement a sa masse
            self.vx = self.vx - fx / m1
            self.vy = self.vy - fy / m1
            unit.vx = unit.vx + fx / m2
            unit.vy = unit.vy + fy / m2
            # c est l un des rares endroits où avoir une classe Vector aurait rendu le code beaucoup plus lisible.
            # mais cet endroit est appelle beaucoup trop souvent dans mon code pour que je me permette de le rendre plus lisible au prix de la performance

    def output(self, move):
        """
        La derniere etape est de convertir le premier Move de la solution gagnante de l evolution pour l ecrire dans la sortie standard.
        Mais la sortie standard ne peut pas prendre directement un Move composee uniquement d un deplacement d angle et d un thrust.
        Il faut utiliser un peu de trigonometrie.
        """
        a = move.angle + move.angle
        if a >= 360.0:
            a = a - 360.0
        elif a < 0.0:
            a = a + 360.0
        # on cherche un point pour correspondre a l angle qu on veut
        # on multiplie par 10000.0 pour eviter les arrondis
        a = a * math.pi / 180.0
        px = self.x + math.cos(a) * 10000.0
        py = self.y + math.sin(a) * 10000.0
        if move.shield:
            print round(px), round(py), "SHIELD"
            self.activateShield()
        else:
            print round(px), round(py), move.power

    def score(self):
        """
        C est tout simplement le nombre de checkpoint que j ai passe multiplie par 50000 moins la distance entre le pod et son prochain checkpoint.
        50000 est evidemment une valeur arbitraire.
        Il faut juste choisir un nombre assez grand pour que le nombre de checkpoints passes soit toujours le plus important.
        """
        return self.checked*50000 - self.distance(self.checkpoint())

    def activateShield(self):
        self.shield = True


def play(pods, checkpoints):
    # il faut conserver le temps ou on en est dans le tour.
    # le but est d arriver a 1.0
    t = 0.0
    while t < 1.0:
        firstCollision = None
        # on cherche toutes les collisions qui vont arriver pendant ce tour
        for i in range(len(pods)):
            # collision avec un autre pod ?
            for j in range(i+1, len(pods)):
                col = pods[i].collision(pods[j])
                # si la collision arrive plus tot que celle qu on, alors on la garde
                if col is not None and col.t + t < 1.0 and (firstCollision is None or col.t < firstCollision.t):
                    firstCollision = col
            # collision avec un checkpoint ?
            # inutile de tester toutes les checkpoints ici.
            # on test juste le prochain checkpoint du pod.
            # on pourrait chercher les collisions du pod avec tous les checkpoints, mais si une telle collision arrive elle n aura aucun impact sur le jeu de toutes façons
            col = pods[i].collision(checkpoints[pods[i].nextCheckpointId])
            # si la collision arrive plus tôt que celle qu'on, alors on la garde
            if col is not None and col.t + t < 1.0 and (firstCollision is None or col.t < firstCollision.t):
                firstCollision = col
        if firstCollision is None:
            # aucune collision, on peut juste deplacer les pods jusqu à la fin du tour
            for i in range(len(pods)):
                pods[i].move(1.0 - t)
            # fin du tour
            t = 1.0
        else:
            # on bouge les pods du temps qu il faut pour arriver sur l instant t de la collision
            for i in range(len(pods)):
                pods[i].move(firstCollision.t)
            # on joue la collision
            firstCollision.a.bounce(firstCollision.b)
            t = t + firstCollision.t
    # on arrondi les positions et on tronque les vitesses pour tout le monde
    for i in range(len(pods)):
        pods[i].end()


def test(pods, checkpoints):
    for i in range(len(pods)):
        pods[i].rotate(Point(8000, 4500))
        pods[i].boost(200)
    play(pods, checkpoints)


if __name__ == "__main__":
    while True:
        # x & y pour la position de votre pod.
        # nextCheckpointX & nextCheckpointY pour les coordonnees du prochain checkpoint que votre pod doit atteindre.
        # nextCheckpointDist pour la distance calcule entre votre pod et son prochain checkpoint.
        # nextCheckpointAngle pour l angle en degre entre l orientation de votre pod et la direction que votre pod doit viser pour aller au prochain checkpoint (de -180 a 180).
        x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in raw_input().split()]
        # 2 entiers opponentX & opponentY pour la position du pod de votre adversaire.
        opponent_x, opponent_y = [int(i) for i in raw_input().split()]
        # 2 entiers pour le point de destination du pod, suivis par thrust, la puissance a donner au pod.
        # vous pouvez remplacer la puissance par BOOST.
        print str(next_checkpoint_x) + " " + str(next_checkpoint_y) + " " + "BOOST"
