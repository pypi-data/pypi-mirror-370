from pathlib import Path
from typing import List

import pytest
from pymultirole_plugins.v1.schema import Document, DocumentList
from starlette.datastructures import UploadFile

from pyconverters_cairn_xml.cairn_xml import (
    CairnInfoXmlConverter,
    CairnInfoXmlParameters,
)
from pyconverters_cairn_xml.cairn_xml import InputFormat


@pytest.mark.skip(reason="Not a test")
def test_cairn_xml_list():
    model = CairnInfoXmlConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == CairnInfoXmlParameters
    converter = CairnInfoXmlConverter()
    parameters = CairnInfoXmlParameters(input_format=InputFormat.Url_List)
    testdir = Path(__file__).parent
    source = Path(testdir, "data/list.txt")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "text/plain"), parameters
        )
        assert len(docs) == 4
        assert docs[0].identifier == "21886606"
        assert docs[1].identifier == "21886599"
        assert docs[1].metadata["DOI"] == "10.2174/157015911795017263"
        assert docs[2].identifier == "10.18585/inabj.v12i2.1171"
        assert docs[2].metadata["DOI"] == "10.18585/inabj.v12i2.1171"
        assert docs[3].identifier == "21886588"
        assert docs[3].metadata["PMC"] == "3137179"


def test_cairn_xml_xml():
    converter = CairnInfoXmlConverter()
    parameters = CairnInfoXmlParameters(
        input_format=InputFormat.XML_Articles
    )
    testdir = Path(__file__).parent
    source = Path(testdir, "data/corpus_resumes_3_4_pages.xml")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "text/xml"), parameters
        )
        assert len(docs) == 28
        assert docs[0].identifier == 'CONST_058_0014'
        dl = DocumentList(__root__=docs)
        result = Path(testdir, "data/corpus_resumes_3_4_pages.json")
        with result.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)

    source = Path(testdir, "data/CorpusResume_20pages&plus.xml")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "text/xml"), parameters
        )
        assert len(docs) == 19
        assert docs[0].identifier == 'KART_PIOT_2008_01_0099'
        dl = DocumentList(__root__=docs)
        result = Path(testdir, "data/CorpusResume_20pages&plus.json")
        with result.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)

    source = Path(testdir, "data/POESI_177_0399.xml")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "text/xml"), parameters
        )
        assert len(docs) == 1
        assert docs[0].identifier == 'POESI_177_0399'
        dl = DocumentList(__root__=docs)
        result = Path(testdir, "data/POESI_177_0399.json")
        with result.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)

    parameters.biblio = False
    parameters.notes = False
    source = Path(testdir, "data/cairn.xml")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "text/xml"), parameters
        )
        assert len(docs) == 1
        assert docs[0].identifier == 'CPC_052_0025'
        dl = DocumentList(__root__=docs)
        result = Path(testdir, "data/cairn.json")
        with result.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)

    source = Path(testdir, "data/formatted_AATC_125_0001.xml")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "text/xml"), parameters
        )
        assert len(docs) == 1
        assert docs[0].identifier == 'AATC_125_0001'
        assert 'tag' in docs[0].metadata
        dl = DocumentList(__root__=docs)
        result = Path(testdir, "data/formatted_AATC_125_0001.json")
        with result.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


@pytest.mark.skip(reason="Not a test")
def test_cairn_xml_corpus():
    converter = CairnInfoXmlConverter()
    parameters = CairnInfoXmlParameters(
        input_format=InputFormat.XML_Articles,
        biblio=False,
        notes=False
    )
    testdir = Path("/media/olivier/DATA/corpora/CAIRNInfo/corpus RAG/fichiers_kairntech")
    for xml_file in testdir.glob("*.xml"):
        with xml_file.open("rb") as fin:
            try:
                docs: List[Document] = converter.convert(
                    UploadFile(xml_file.name, fin, "application/xml"), parameters
                )
                dl = DocumentList(__root__=docs)
                json_file = xml_file.with_suffix(".json")
                with json_file.open("w") as fout:
                    print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
            except Exception:
                print(f"Error processing file: {xml_file}")


def test_cairn_avec_ordre():
    converter = CairnInfoXmlConverter()
    parameters = CairnInfoXmlParameters(
        input_format=InputFormat.XML_Articles
    )
    testdir = Path(__file__).parent
    source = Path(testdir, "data/avec_ordre.xml")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "text/xml"), parameters
        )
        assert len(docs) == 1
        assert docs[0].identifier == 'AATC_125_0015'
        assert docs[0].metadata['id_article'] == 'AATC_125_0015'
        assert len(docs[0].metadata['auteur_12']) == 2
        assert len(docs[0].metadata['id_auteur_12']) == 2
        assert len(docs[0].metadata['auteur']) > 2
        assert len(docs[0].metadata['id_auteur']) > 2
        dl = DocumentList(__root__=docs)
        result = Path(testdir, "data/avec_ordre.json")
        with result.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)

    source = Path(testdir, "data/batch_psychologie_2.xml")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "text/xml"), parameters
        )
        assert len(docs) == 1
        assert docs[0].identifier == 'ADO_052_0273'
        assert docs[0].metadata['id_revue'] == 'ADO'
        assert docs[0].metadata['id_editeur'] == 'EDT'
        assert len(docs[0].metadata['zonegeo']) == 1
        assert len(docs[0].metadata['zonegeo_12']) == 1
        dl = DocumentList(__root__=docs)
        result = Path(testdir, "data/batch_psychologie_2.json")
        with result.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
