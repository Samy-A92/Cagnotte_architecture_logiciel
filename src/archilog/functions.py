import uuid

from sqlalchemy import select, update, \
    insert, func, desc

from archilog.models import engine, table_cagnotte, membres_table, depenses_table
import datetime

def check_cagnotte(name):
    with engine.begin() as conn:
        stmt_cagnotte = select(table_cagnotte).where(table_cagnotte.c.name == name)
        res_cagnotte = conn.execute(stmt_cagnotte).fetchone()
        if res_cagnotte is None:
            return None
        return res_cagnotte


def create_db(name: str):

    message = check_cagnotte(name)
    if message is not None:
        return "La cagnotte existe déjà !"



    stmt = table_cagnotte.insert().values(name=name.upper(), montant=0, date=datetime.datetime.now())

    with engine.begin() as conn:
        conn.execute(stmt)
    message = f"Cagnotte {name} crée !"
    return message



def get_supp(name: str):
    name = name.upper()
    if check_cagnotte(name) is None:
        return "La cagnotte n'existe pas"

    stmt = table_cagnotte.delete().where(table_cagnotte.c.name == name)
    stmt2 = membres_table.delete().where(membres_table.c.cagnotte == name)
    stmt3 = depenses_table.delete().where(depenses_table.c.cagnotte == name)
    with engine.begin() as conn:
        conn.execute(stmt)
        conn.execute(stmt2)
        conn.execute(stmt3)
    return f"Suppression de {name} réussi !"


def get_cagnottes():
    stmt = select(table_cagnotte).order_by(table_cagnotte.c.date)

    result = []
    with engine.begin() as conn:
        for row in conn.execute(stmt):
            result.append(row)

    return result


def get_cagnotte(name: str):
    name = name.upper()
    res = dict()
    if check_cagnotte(name) is None:
        return "La cagnotte n'existe pas"

    stmt = select(table_cagnotte).where(table_cagnotte.c.name == name)
    with engine.begin() as conn:
        result = conn.execute(stmt)
        res["cagnotte"] =  list()
        for row in result:
            res["cagnotte"].append(row)
            print(row)



    print("Dépenses:")

    stmt = select(depenses_table).where(depenses_table.c.cagnotte == name)
    with engine.begin() as conn:

        res["depenses"] =  list()
        for row in conn.execute(stmt).fetchall():
            print(row)
            res["depenses"].append(row)



    print("Membres:")

    stmt = select(membres_table).where(membres_table.c.cagnotte == name)
    stmt2 = (
    select(
        depenses_table.c.nom,
        func.count(depenses_table.c.nom).label("nb_depenses")
    )
    .where(depenses_table.c.cagnotte == name)
    .group_by(depenses_table.c.nom)
)
    with engine.begin() as conn:

        counts = {row.nom: row.nb_depenses for row in conn.execute(stmt2)}

        membres = conn.execute(stmt).fetchall()

        res["membres"] = []
        for row in membres:
            membre_data = row._asdict()
            membre_data["nb_depenses"] = counts.get(row.nom, 0)
            res["membres"].append(membre_data)

    return res


def add_depense(name: str, person: str, count: int, depense: str):
    name = name.upper()
    person = person.upper()
    count = int(count)

    res_cagnotte = check_cagnotte(name)

    if res_cagnotte is None:
        return f"La table {name} n'existe pas."

    with engine.begin() as conn:



        stmt_dernier = (
            select(depenses_table.c.nom)
            .where(depenses_table.c.cagnotte == name)
            .order_by(desc(depenses_table.c.date))
            .limit(1)
        )
        dernier_depensier_row = conn.execute(stmt_dernier).fetchone()

        if dernier_depensier_row is not None and dernier_depensier_row.nom == person:
            return "Vous êtes déjà le dernier dépensier de cette cagnotte !"

        nouveau_montant = res_cagnotte.montant + count


        conn.execute(
            update(table_cagnotte)
            .where(table_cagnotte.c.name == name)
            .values(montant=nouveau_montant)
        )

        conn.execute(
            insert(depenses_table).values(
                cagnotte=name,
                nom=person,
                date=datetime.datetime.now(),
                montant=count,
                depense=depense
            )
        )

        stmt_membre_exist = select(membres_table).where(
            membres_table.c.cagnotte == name,
            membres_table.c.nom == person
        )
        if conn.execute(stmt_membre_exist).fetchone() is None:
            conn.execute(
                insert(membres_table).values(cagnotte=name, nom=person)
            )

    return f"Dépense ajoutée ! Nouveau montant de {name} : {nouveau_montant}€"


def supp_depense(cagnotte_name: str, depense_id: str):
    cagnotte_name = cagnotte_name.upper()

    try:
        id_obj = uuid.UUID(depense_id)
    except (ValueError, AttributeError):
        return "ID de dépense invalide."

    with engine.begin() as conn:
        stmt_depense = select(depenses_table).where(
            depenses_table.c.id == id_obj,
            depenses_table.c.cagnotte == cagnotte_name
        )
        res_depense = conn.execute(stmt_depense).fetchone()

        if not res_depense:
            return "Dépense introuvable."

        stmt_cagnotte = select(table_cagnotte.c.montant).where(
            table_cagnotte.c.name == cagnotte_name
        )
        res_cagnotte = conn.execute(stmt_cagnotte).fetchone()

        nouveau_montant = res_cagnotte.montant - res_depense.montant

        conn.execute(
            update(table_cagnotte)
            .where(table_cagnotte.c.name == cagnotte_name)
            .values(montant=nouveau_montant)
        )

        conn.execute(
            depenses_table.delete().where(depenses_table.c.id == id_obj)
        )

    return f"Dépense supprimée. Nouveau montant : {nouveau_montant}€"


def ajouter_membres_db(cagnotte_name: str, liste_noms: list):
    cagnotte_name = cagnotte_name.upper()
    messages = []
    if check_cagnotte(cagnotte_name) is None:
        return "Le table inexistant."
    with engine.begin() as conn:


        for nom in liste_noms:
            if not nom.strip(): continue

            nom_upper = nom.upper()

            stmt_check = select(membres_table).where(
                membres_table.c.cagnotte == cagnotte_name,
                membres_table.c.nom == nom_upper
            )

            if conn.execute(stmt_check).fetchone() is not None:
                messages.append(f"Le membre '{nom}' existe déjà !")
            else:
                conn.execute(membres_table.insert().values(cagnotte=cagnotte_name, nom=nom_upper))
                messages.append(f"Ajout de '{nom}' réussi !")

    return " | ".join(messages)

def supp_membre(cagnotte_name: str, membre_nom: str):
    cagnotte_name = cagnotte_name.upper()
    membre_nom = membre_nom.upper()

    with engine.begin() as conn:
        stmt_check = select(depenses_table).where(
            depenses_table.c.cagnotte == cagnotte_name,
            depenses_table.c.nom == membre_nom
        )
        if conn.execute(stmt_check).fetchone():
            return f"Erreur : Impossible de supprimer {membre_nom}, il a des dépenses enregistrées."

        stmt_del = membres_table.delete().where(
            membres_table.c.cagnotte == cagnotte_name,
            membres_table.c.nom == membre_nom
        )
        result = conn.execute(stmt_del)

        if result.rowcount == 0:
            return "Le membre n'existe pas dans cette cagnotte."

    return f"Membre {membre_nom} supprimé avec succès de {cagnotte_name}."


def afficher_remboursement(cagnotte_name: str):
    cagnotte_name = cagnotte_name.upper()

    with engine.begin() as conn:
        stmt_membres = select(membres_table.c.nom).where(membres_table.c.cagnotte == cagnotte_name)
        membres = [row.nom for row in conn.execute(stmt_membres)]

        if not membres:
            return "Aucun membre dans cette cagnotte."

        stmt_cagnotte = select(table_cagnotte.c.montant).where(table_cagnotte.c.name == cagnotte_name)
        res_cagnotte = conn.execute(stmt_cagnotte).fetchone()
        total_depense = res_cagnotte.montant if res_cagnotte else 0

        part_theorique = total_depense / len(membres)

        stmt_paye = (
            select(depenses_table.c.nom, func.sum(depenses_table.c.montant).label("total"))
            .where(depenses_table.c.cagnotte == cagnotte_name)
            .group_by(depenses_table.c.nom)
        )

        deja_paye = {row.nom: row.total for row in conn.execute(stmt_paye)}

        equilibre = []
        for m in membres:
            paye = deja_paye.get(m, 0)
            diff = paye - part_theorique
            equilibre.append({
                "nom": m,
                "paye": paye,
                "diff": round(diff, 2)
            })

    return {
        "cagnotte": cagnotte_name,
        "total": total_depense,
        "part_par_personne": round(part_theorique, 2),
        "bilan": equilibre
    }
