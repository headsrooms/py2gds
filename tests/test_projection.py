from py2gds.projection import Projection


def test_check_projection(pages_and_links_projection: Projection):
    if pages_and_links_projection.exists():
        pages_and_links_projection.delete()
    pages_and_links_projection.create()
    assert pages_and_links_projection.exists()
