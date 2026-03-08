import os

from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint



from archilog.functions import get_cagnottes, create_db, get_supp, get_cagnotte, supp_depense, add_depense, supp_membre, \
    ajouter_membres_db, afficher_remboursement



web_ui = Blueprint("web_ui", __name__)
@web_ui.route("/")
@web_ui.route("/<name>")
def index(name=None):

    result = get_cagnottes()

    return render_template("index.html", cagnottes=result)
@web_ui.route("/create/")
def create_page():
    return render_template("create.html")

@web_ui.route("/actions/cagnottes/create", methods=["POST"])
def action_create():
    nom = request.form.get("name").upper()
    message = create_db(nom)
    flash(message)
    return redirect(url_for('web_ui.index'))

@web_ui.route("/actions/cagnottes/supprimer", methods=["POST"])
def supprimer_cagnotte():

    result = get_supp(request.form.get("nom"))
    flash(result)
    return redirect(url_for('web_ui.index'))


@web_ui.route("/actions/cagnottes/plus_info", methods=["POST"])
def plus_info():


    result = get_cagnotte(request.form.get("nom"))
    bilan = afficher_remboursement(request.form.get("nom"))
    return render_template("cagnotte.html", cagnotte=result, bilan=bilan)

@web_ui.route("/actions/depenses/supprimer_depense", methods=["POST"])
def supprimer_depense():
    message = supp_depense(
        request.form.get("nom"),
        request.form.get("depense_id")
    )
    flash(message)
    return redirect(url_for('web_ui.index'))

@web_ui.route("/actions/depenses/ajouter_depense_form", methods=["POST"])
def ajouter_depense_form():
    return render_template("ajouter_depense_form.html", cagnotte=get_cagnotte(request.form.get("nom")))

@web_ui.route("/actions/depenses/ajouter_depense", methods=["POST"])
def ajouter_depense():

    try:
        montant = int(request.form.get("montant", 0))
    except ValueError:
        flash("Le montant doit être un nombre valide.")
        return redirect(url_for('web_ui.index'))

    result = add_depense(
        request.form.get("cagnotte"),
        request.form.get("membre"),
        montant,
        request.form.get("description")
    )
    flash(result)
    return redirect(url_for('web_ui.index'))

@web_ui.route("/actions/membres/supprimer_membre", methods=["POST"])
def supprimer_membre():
    message = supp_membre(request.form.get("cagnotte"), request.form.get("membre"))
    flash(message)
    return redirect(url_for('web_ui.index'))

@web_ui.route("/actions/membres/ajouter_membre_form", methods=["POST"])
def form_ajouter_membres():
    return render_template("ajouter_membre_form.html", cagnotte_name=(request.form.get("nom")))


@web_ui.route("/actions/membres/ajouter_membre", methods=["POST"])
def action_ajouter_membres():
    cagnotte_name = request.form.get("cagnotte")

    noms = request.form.getlist("noms_membres")

    message = ajouter_membres_db(cagnotte_name, noms)
    flash(message)
    return redirect(url_for('web_ui.index'))



