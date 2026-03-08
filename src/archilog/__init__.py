import click
from sqlalchemy import select

from archilog.models import init_db, table_cagnotte, membres_table, depenses_table, engine
from archilog.functions import (
    create_db, check_cagnotte, get_supp, get_cagnottes,
    get_cagnotte, supp_depense, supp_membre, add_depense, afficher_remboursement
)

init_db()

@click.group()
def cli():
    pass

@cli.command()
@click.option("-n", "--name", prompt="Name", help="Créer une cagnotte." )
@click.option("-a", "--montant", prompt="Montant deposé", help="Quel est le montant que vous voulez deposer.", default=0)
def create(name: str, montant: int):
    return click.echo(create_db(name, montant))

@cli.command()
@click.option("-n", "--name", prompt="Name", help="Supprimer une cagnotte." )
def delete(name: str):
    test = input("Etes vous sur ? (y/n)")
    if test.lower() != "y":
        click.echo("Annulation.")
        return "Annulation."
    return click.echo( get_supp(name))


@cli.command()
def afficher_cagnottes():
    click.echo("Afficher cagnottes:")
    for row in get_cagnottes():
        print(row)
    click.echo("Fins des cagnottes")


@cli.command()
@click.option("-n", "--name", prompt="Name", help="Affiche une cagnotte." )
def afficher_cagnotte(name: str):
    get_cagnotte(name)

@cli.command()
@click.option("--count", prompt="montant a ajouter", default=1)
@click.option("--person", prompt="nom donnateur")
@click.option("--depense", prompt="nom de la depense")
@click.option("--name", prompt="Nom de la cagnotte")
def ajout_depense(name:str, person:str, count:int, depense:str ):
    test = input("Etes vous sur ? (y/n)")
    if test.lower() != "y":
        click.echo("Annulation.")
        return

    click.echo(add_depense(name,person,count,depense))


@cli.command()
@click.option("-n", "--name", prompt="Nom de la personne")
def afficher_dep_personne(name: str):

    stmt = select(depenses_table).where(depenses_table.c.nom == name.upper())
    with engine.begin() as conn:
        r = conn.execute(stmt)
        for row in r:
            print(row)
            return



@cli.command()
@click.option("--cagnotte_name", prompt="Nom de la cagnotte")
@click.option("--depense_id", prompt="ID de la depense")
def supprimer_depense(cagnotte_name: str, depense_id: str ):
    test = input("Etes vous sur ? (y/n)")
    if test.lower() != "y":
        click.echo("Annulation.")
        return
    click.echo(supp_depense(cagnotte_name,depense_id))


@cli.command()
@click.option("-n", "--name", prompt="Nom de la cagnotte")
def ajouter_membres(name: str):
    name = name.upper()

    if check_cagnotte(name) is None:
        click.echo("Le table inexistant.")
        return "Le table inexistant."


    n = int(input("Nombre de membres a ajouter : "))
    if n<=0:
        click.echo(f"erreur impossible d'ajouter {n} membres.")
        return None


    for x in range(n):
        membre = str(input(f"Nom du membre n°{x+1}: "))
        stmt = select(membres_table).where(membres_table.c.cagnotte == name, membres_table.c.nom == membre.upper())
        stmt2 = membres_table.insert().values(cagnotte=name, nom=membre.upper())
        with engine.begin() as conn:
            if conn.execute(stmt).fetchone() is not None:
                print(f"Le membre '{membre} existe déjà !'")

            else:
                conn.execute(stmt2)

                print("Ajout !")
    return None



@cli.command()
@click.option("-n", "--name", prompt="Nom de la cagnotte")
@click.option("-m", "--membre", prompt="Nom du membre à supprimer")
def supprimer_membre_cli(name, membre):
    print(supp_membre(name, membre))


@cli.command()
@click.option("-n", "--name", prompt="Nom de la cagnotte", help="Affiche le bilan des remboursements.")
def bilan(name: str):

    data = afficher_remboursement(name)

    if isinstance(data, str):
        click.echo(data)
        return

    click.echo(f"\n=== BILAN DE LA CAGNOTTE : {data['cagnotte']} ===")
    click.echo(f"Montant total dépensé : {data['total']} €")
    click.echo(f"Part théorique par personne : {data['part_par_personne']} €")
    click.echo("-" * 40)

    for membre in data['bilan']:
        nom = membre['nom']
        paye = membre['paye']
        diff = membre['diff']

        if diff > 0:
            status = click.style(f"DOIT RECEVOIR {diff} €")
        elif diff < 0:
            status = click.style(f"DOIT DONNER {abs(diff)} €")
        else:
            status = click.style("EST À L'ÉQUILIBRE")

        click.echo(f"{nom.ljust(15)} | Payé: {str(paye).ljust(6)} € | {status}")

    click.echo("-" * 40 + "\n")

