"""Tests for OGC Tiles API data models"""

import pyproj
import pytest
from pydantic import ValidationError

from xpublish_tiles.xpublish.tiles.types import CRSType, MD_ReferenceSystem


class TestCRSType:
    """Test CRSType model and conversion functionality"""

    def test_uri_crs(self):
        """Test CRS with URI reference"""
        crs = CRSType(uri="http://www.opengis.net/def/crs/EPSG/0/4326")
        assert crs.uri == "http://www.opengis.net/def/crs/EPSG/0/4326"
        assert crs.wkt is None
        assert crs.referenceSystem is None

    def test_wkt_crs(self):
        """Test CRS with WKT definition"""
        wkt_string = 'GEOGCS["WGS 84",DATUM["WGS_1984"]]'
        crs = CRSType(wkt=wkt_string)
        assert crs.wkt == wkt_string
        assert crs.uri is None
        assert crs.referenceSystem is None

    def test_reference_system_crs(self):
        """Test CRS with ISO 19115 MD_ReferenceSystem"""
        ref_sys = MD_ReferenceSystem(code="4326", codeSpace="EPSG", version="8.5")
        crs = CRSType(referenceSystem=ref_sys)
        assert crs.referenceSystem == ref_sys
        assert crs.uri is None
        assert crs.wkt is None

    def test_empty_crs(self):
        """Test CRS with no values"""
        crs = CRSType()
        assert crs.uri is None
        assert crs.wkt is None
        assert crs.referenceSystem is None

    def test_uri_validation_error(self):
        """Test URI validation with invalid type"""
        with pytest.raises(ValidationError):
            CRSType(uri=123)  # type: ignore[arg-type]

    def test_to_epsg_string_from_uri_epsg_colon(self):
        """Test EPSG string conversion from URI with colon format"""
        crs = CRSType(uri="http://www.opengis.net/def/crs/EPSG/0/4326")
        assert crs.to_epsg_string() == "EPSG:4326"

    def test_to_epsg_string_from_uri_epsg_slash(self):
        """Test EPSG string conversion from URI with slash format"""
        crs = CRSType(uri="epsg/3857")
        assert crs.to_epsg_string() == "EPSG:3857"

    def test_to_epsg_string_from_uri_epsg_case_insensitive(self):
        """Test EPSG string conversion is case insensitive"""
        crs = CRSType(uri="EPSG:4326")
        assert crs.to_epsg_string() == "EPSG:4326"

    def test_to_epsg_string_from_uri_non_epsg(self):
        """Test EPSG string conversion from non-EPSG URI"""
        crs = CRSType(uri="http://example.com/crs/custom")
        assert crs.to_epsg_string() == "http://example.com/crs/custom"

    def test_to_epsg_string_from_wkt(self):
        """Test EPSG string conversion from WKT"""
        wkt_string = 'GEOGCS["WGS 84",DATUM["WGS_1984"]]'
        crs = CRSType(wkt=wkt_string)
        assert crs.to_epsg_string() == wkt_string

    def test_to_epsg_string_from_reference_system_epsg(self):
        """Test EPSG string conversion from MD_ReferenceSystem with EPSG"""
        ref_sys = MD_ReferenceSystem(code="4326", codeSpace="EPSG")
        crs = CRSType(referenceSystem=ref_sys)
        assert crs.to_epsg_string() == "EPSG:4326"

    def test_to_epsg_string_from_reference_system_non_epsg(self):
        """Test EPSG string conversion from MD_ReferenceSystem without EPSG"""
        ref_sys = MD_ReferenceSystem(code="4326", codeSpace="OTHER")
        crs = CRSType(referenceSystem=ref_sys)
        assert crs.to_epsg_string() == "4326"

    def test_to_epsg_string_from_reference_system_no_code(self):
        """Test EPSG string conversion from MD_ReferenceSystem without code"""
        ref_sys = MD_ReferenceSystem(codeSpace="EPSG")
        crs = CRSType(referenceSystem=ref_sys)
        assert crs.to_epsg_string() is None

    def test_to_epsg_string_empty(self):
        """Test EPSG string conversion from empty CRS"""
        crs = CRSType()
        assert crs.to_epsg_string() is None

    def test_to_pyproj_crs_from_uri_epsg(self):
        """Test pyproj.CRS conversion from EPSG URI"""
        crs = CRSType(uri="http://www.opengis.net/def/crs/EPSG/0/4326")
        pyproj_crs = crs.to_pyproj_crs()

        assert pyproj_crs is not None
        assert isinstance(pyproj_crs, pyproj.CRS)
        assert pyproj_crs.to_epsg() == 4326

    def test_to_pyproj_crs_from_uri_web_mercator(self):
        """Test pyproj.CRS conversion from Web Mercator EPSG URI"""
        crs = CRSType(uri="http://www.opengis.net/def/crs/EPSG/0/3857")
        pyproj_crs = crs.to_pyproj_crs()

        assert pyproj_crs is not None
        assert isinstance(pyproj_crs, pyproj.CRS)
        assert pyproj_crs.to_epsg() == 3857

    def test_to_pyproj_crs_from_wkt(self):
        """Test pyproj.CRS conversion from WKT"""
        # Use a simple WGS84 WKT string
        wkt_string = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
        crs = CRSType(wkt=wkt_string)
        pyproj_crs = crs.to_pyproj_crs()

        assert pyproj_crs is not None
        assert isinstance(pyproj_crs, pyproj.CRS)
        # WKT should create a valid CRS (can't easily test EPSG code due to WKT variations)

    def test_to_pyproj_crs_from_reference_system(self):
        """Test pyproj.CRS conversion from MD_ReferenceSystem"""
        ref_sys = MD_ReferenceSystem(code="4326", codeSpace="EPSG")
        crs = CRSType(referenceSystem=ref_sys)
        pyproj_crs = crs.to_pyproj_crs()

        assert pyproj_crs is not None
        assert isinstance(pyproj_crs, pyproj.CRS)
        assert pyproj_crs.to_epsg() == 4326

    def test_to_pyproj_crs_empty(self):
        """Test pyproj.CRS conversion from empty CRS"""
        crs = CRSType()
        pyproj_crs = crs.to_pyproj_crs()
        assert pyproj_crs is None

    def test_to_pyproj_crs_invalid(self):
        """Test pyproj.CRS conversion with invalid CRS string"""
        crs = CRSType(uri="invalid:crs:string")
        pyproj_crs = crs.to_pyproj_crs()
        # Should return None for invalid CRS strings
        assert pyproj_crs is None
