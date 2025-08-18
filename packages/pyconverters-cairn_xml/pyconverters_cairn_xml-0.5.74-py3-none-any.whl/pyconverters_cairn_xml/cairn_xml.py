import logging
import os
from enum import Enum
from typing import List, cast, Type

from inscriptis import Inscriptis
from inscriptis.css_profiles import RELAXED_CSS_PROFILE
from inscriptis.html_properties import Display
from inscriptis.model.config import ParserConfig
from inscriptis.model.css import HtmlElement
from lxml import etree as ET
from pydantic import Field, BaseModel
from pymultirole_plugins.v1.converter import ConverterParameters, ConverterBase
from pymultirole_plugins.v1.schema import Document, Sentence, Boundary
from starlette.datastructures import UploadFile

_home = os.path.expanduser("~")


class InputFormat(str, Enum):
    XML_Articles = "XML Articles"
    Url_List = "Url List"


class CairnInfoXmlParameters(ConverterParameters):
    input_format: InputFormat = Field(
        InputFormat.XML_Articles,
        description="""Format d'entrée du fichier, parmi:<br/>
        <li>`XML Articles`: fichier XML au format Cainr.info.<br/>
        <li>`Url List`: fichier texte contenant une url par ligne.""", extra="internal"
    )
    biblio: bool = Field(False, description="Extraire la bibliographie")
    notes: bool = Field(False, description="Extraire les notes")
    resume: bool = Field(True, description="Extraire le résumé")


logger = logging.getLogger("pymultirole")


class CairnInfoXmlConverter(ConverterBase):
    """CairnInfoXml converter ."""

    def convert(
            self, source: UploadFile, parameters: ConverterParameters
    ) -> List[Document]:
        params: CairnInfoXmlParameters = cast(CairnInfoXmlParameters, parameters)

        docs = []
        try:
            MY_CSS_PROFILE = RELAXED_CSS_PROFILE.copy()
            MY_CSS_PROFILE["titre"] = HtmlElement('h1', display=Display.block, margin_before=1,
                                                  margin_after=1)
            MY_CSS_PROFILE["biblio"] = HtmlElement('h2', display=Display.block, margin_before=1,
                                                   margin_after=1)
            MY_CSS_PROFILE["divbiblio"] = HtmlElement('h3', display=Display.block, margin_before=1,
                                                      margin_after=1)
            MY_CSS_PROFILE["alinea"] = HtmlElement('p', display=Display.block,
                                                   padding=2)
            MY_CSS_PROFILE["refbiblio"] = HtmlElement('div', display=Display.block,
                                                      padding=2)
            MY_CSS_PROFILE["listenonord"] = HtmlElement('ul', display=Display.block, margin_before=0,
                                                        margin_after=0, padding=4)
            MY_CSS_PROFILE["listeord"] = HtmlElement('ol', display=Display.block, margin_before=0,
                                                     margin_after=0, padding=4)
            MY_CSS_PROFILE["elemliste"] = HtmlElement('li', display=Display.block)
            MY_CSS_PROFILE["renvoi"] = HtmlElement('q', prefix=' [', suffix=']') if params.notes else HtmlElement(
                display=Display.none)
            MY_CSS_PROFILE["no"] = HtmlElement('q', prefix='[', suffix=']') if params.notes else HtmlElement(
                display=Display.none)

            if params.input_format == InputFormat.Url_List:
                pass
            elif params.input_format == InputFormat.XML_Articles:
                tree = ET.parse(source.file)
                for article in tree.iter("article"):
                    sentences = []
                    boundaries = []
                    document_titles = {tree.getpath(titre.getparent()): titre.text for titre in
                                       article.xpath('.//titre') if titre.text is not None}
                    text = ""
                    identifier = article.get('idproprio')
                    typeart = article.get('typeart')
                    # lang = article.get('lang')
                    liminaire = article.find("liminaire")
                    title = None
                    metadata = {'typeart': typeart, 'id_article': identifier}
                    add_additional_fields(article, metadata)
                    if liminaire is not None:
                        grtitre = liminaire.find("grtitre")
                        if grtitre is not None:
                            titre = grtitre.find("titre")
                            if titre is not None:
                                title, text, sentences = add_paragraph(tree, text, sentences, None, titre,
                                                                       css=MY_CSS_PROFILE)
                            surtitre = grtitre.find("surtitre")
                            if surtitre is not None:
                                metadata["surtitre"] = surtitre.text
                            sstitre = grtitre.find("sstitre")
                            if sstitre is not None:
                                metadata["sstitre"] = sstitre.text
                        grauteur = liminaire.find("grauteur")
                        if grauteur is not None:
                            auteurs = {}
                            affiliations = set()
                            for iauteur, auteur in enumerate(grauteur.iter("auteur")):
                                _, text, sentences = add_paragraph(tree, text, sentences, None,
                                                                   auteur,
                                                                   css=MY_CSS_PROFILE)
                                id_auteur = auteur.find("id_auteur")
                                if id_auteur is not None:
                                    id_auteur = id_auteur.text
                                ordre = auteur.find("ordre")
                                order = iauteur + 1
                                if ordre is not None:
                                    order = int(ordre.text)
                                zonegeo = auteur.find("zonegeo")
                                if zonegeo is not None:
                                    zonegeo = zonegeo.text
                                prenom_nom = []
                                nompers = auteur.find("nompers")
                                if nompers is not None:
                                    prenom = nompers.find("prenom")
                                    if prenom is not None and prenom.text is not None:
                                        prenom_nom.append(prenom.text.strip())
                                    nomfamille = nompers.find("nomfamille")
                                    if nomfamille is not None and nomfamille.text is not None:
                                        nomfamille = nompers.find("nomfamille")
                                        prenom_nom.append(nomfamille.text.strip())
                                affiliation = auteur.find("affiliation")
                                if affiliation is not None:
                                    for alinea in affiliation.iter("alinea"):
                                        if alinea is not None and alinea.text is not None:
                                            alinea_txt = alinea.text.strip()
                                            if alinea_txt:
                                                affiliations.add(alinea.text)
                                if len(prenom_nom) > 0:
                                    auteur = ', '.join(prenom_nom)
                                    auteurs[order] = (auteur, id_auteur, zonegeo)
                            if len(auteurs) > 0:
                                sorted_auteurs = dict(sorted(auteurs.items()))
                                lauteurs, lid_auteurs, lzonegeos = zip(*sorted_auteurs.values())
                                metadata["auteur"] = list(lauteurs)
                                list_id_auteurs = list(lid_auteurs)
                                metadata["id_auteur"] = [id for id in list_id_auteurs if id is not None]
                                list_zonegeos = list(lzonegeos)
                                metadata["zonegeo"] = [z for z in list_zonegeos if z is not None]
                                metadata["auteur_12"] = list(lauteurs)[:2]
                                metadata["id_auteur_12"] = [id for id in list_id_auteurs[:2] if id is not None]
                                metadata["zonegeo_12"] = [z for z in list_zonegeos[:2] if z is not None]
                                metadata["affiliation"] = list(affiliations)
                        chapo = liminaire.find("chapo")
                        if chapo is not None:
                            _, text, sentences = add_paragraph(tree, text, sentences, None, chapo, css=MY_CSS_PROFILE)
                        if params.resume:
                            resume = liminaire.find("resume")
                            if resume is not None and resume.get('lang', 'fr') == 'fr':
                                _, text, sentences = add_paragraph(tree, text, sentences, None, resume,
                                                                   css=MY_CSS_PROFILE)

                    admin = article.find("admin")
                    if admin is not None:
                        infoarticle = admin.find("infoarticle")
                        if infoarticle is not None:
                            add_additional_fields(infoarticle, metadata)
                            section_sommaire = infoarticle.find("section_sommaire")
                            if section_sommaire is not None:
                                metadata["section_sommaire"] = section_sommaire.text
                            sous_section_sommaire = infoarticle.find("sous_section_sommaire")
                            if sous_section_sommaire is not None:
                                metadata["sous_section_sommaire"] = sous_section_sommaire.text
                            nbpage = infoarticle.find("nbpage")
                            if nbpage is not None:
                                metadata["nbpage"] = nbpage.text

                        numero = admin.find("numero")
                        if numero is not None:
                            theme = numero.find("theme")
                            if theme is not None:
                                metadata["titre_numero"] = theme.text
                            pub = numero.find("pub")
                            if pub is not None:
                                metadata["année"] = pub.findtext('annee')
                        revue = admin.find("revue")
                        if revue is not None:
                            id_revue = revue.get('id')
                            metadata["id_revue"] = id_revue
                            titrerev = revue.find("titrerev")
                            if titrerev is not None:
                                metadata["titre_revue"] = titrerev.text
                        editeur = admin.find("editeur")
                        if editeur is not None:
                            id_editeur = editeur.get('id')
                            metadata["id_editeur"] = id_editeur
                        collection = admin.find("collection")
                        if collection is None:
                            ouvrage = admin.find("ouvrage")
                            if ouvrage is not None:
                                collection = ouvrage.find("collection")
                        if collection is not None:
                            titrecol = collection.find("titre")
                            if titrecol is not None:
                                metadata["titre_collection"] = titrecol.text

                    corps = article.find("corps")
                    if corps is not None:
                        for section in corps:
                            if section.tag in ['section1', 'section2', 'section3', 'section4', 'section5', 'section6']:
                                text, sentences, boundaries = add_section(tree, text, sentences, boundaries,
                                                                          document_titles, section, css=MY_CSS_PROFILE)
                    partiesann = article.find("partiesann")
                    if partiesann is not None:
                        if params.biblio:
                            biblio = partiesann.find("biblio")
                            if biblio is not None:
                                text, sentences, boundaries = add_section(tree, text, sentences, boundaries,
                                                                          document_titles, biblio, css=MY_CSS_PROFILE,
                                                                          header='BIBILOGRAPHIE')
                        if params.notes:
                            grnote = partiesann.find("grnote")
                            if grnote is not None:
                                text, sentences, boundaries = add_section(tree, text, sentences, boundaries,
                                                                          document_titles, grnote, css=MY_CSS_PROFILE,
                                                                          header='NOTES')
                    doc = Document(identifier=identifier, title=title, text=text, metadata=metadata,
                                   sentences=sentences,
                                   boundaries={'SECTIONS': boundaries})
                    doc.metadata['original'] = source.filename
                    docs.append(doc)
        except BaseException as err:
            logger.warning(
                f"Cannot parse article {source.filename}",
                exc_info=True,
            )
            raise err
        return docs

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return CairnInfoXmlParameters


def add_additional_fields(node, metadata):
    typepub = node.find("typepub")
    if typepub is not None:
        metadata["typepub"] = typepub.text
    consultations = node.find("consultations")
    if consultations is not None:
        metadata["consultations"] = consultations.text
    grdiscipline = node.find("grdiscipline")
    if grdiscipline is not None:
        disciplines = []
        for discipline in grdiscipline.iter("discipline"):
            if discipline is not None and discipline.text is not None:
                disciplines.append(discipline.text)
        metadata["discipline"] = disciplines
    grthematique = node.find("grthematique")
    if grthematique is not None:
        thematiques = []
        for thematique in grthematique.iter("thematique"):
            if thematique is not None and thematique.text is not None:
                thematiques.append(thematique.text)
        metadata["thematique"] = thematiques
    grtag = node.find("grtag")
    if grtag is not None:
        tags = []
        for tag in grtag.iter("tag"):
            if tag is not None and tag.text is not None:
                tags.append(tag.text)
        metadata["tag"] = tags


def compute_title_hierarchy(document_titles, item_path):
    headings = []
    if document_titles is not None:
        paths = item_path.split('/')
        for i in range(1, len(paths) + 1):
            xpath = '/'.join(paths[:i])
            if xpath in document_titles:
                headings.append(document_titles[xpath])
    return headings


def add_section(tree, text, sentences, boundaries, document_titles, section, css=None, header=None):
    bstart = len(text)
    if header is not None:
        text += header + '\n'
        metadata = {'xpath': tree.getpath(section)}
        sentences.append(Sentence(start=bstart, end=len(text), metadata=metadata))
    for child in section.iterdescendants():
        if child.tag in ['titre', 'para', 'encadre', 'listenonord', 'listeord', 'tableau', 'refbiblio', 'note']:
            _, text, sentences = add_paragraph(tree, text, sentences, document_titles, child, css=css)
    boundaries.append(Boundary(start=bstart, end=len(text), name=tree.getpath(section)))
    return text, sentences, boundaries


def add_paragraph(tree, text, sentences, document_titles, item, css=None):
    inscriptis = Inscriptis(
        item, ParserConfig(css=css)
    )
    item_text = inscriptis.get_text().strip()
    sstart = len(text)
    text += item_text + '\n'
    metadata = {'xpath': tree.getpath(item)}
    item_path = tree.getpath(item.getparent())
    headers = compute_title_hierarchy(document_titles, item_path)
    if headers:
        if item.tag == 'titre':
            headers.pop()
        metadata['headers'] = " / ".join(headers)
    if item.tag != 'titre':
        sentences.append(Sentence(start=sstart, end=len(text), metadata=metadata))
    return item_text, text, sentences
