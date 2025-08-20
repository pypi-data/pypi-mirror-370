# dto_to_stac.py
import logging
import os.path
from datetime import datetime, timezone
from typing import Any, Dict, List

import pystac
import shapely

from odp.client import OdpClient
from odp.dto import DataCollectionDto, DatasetDto, ObservableDto, ResourceDto
from odp.dto.registry.observables_class_definitions import (
    static_coverage_class,
    static_geometric_coverage_class,
    static_single_value_class,
)
from odp.stac import CATALOG_FRONTEND_URL, STAC_API_URL


def get_root_catalog() -> pystac.Catalog:
    root_catalog = pystac.Catalog(id="stac-root", description="Hub Ocean Public STAC API", href=STAC_API_URL)

    # Collections link
    root_catalog.add_link(
        pystac.Link(
            rel="data",
            target=os.path.join(STAC_API_URL, "collections"),
            media_type=pystac.MediaType.JSON,
        )
    )
    # Search link
    root_catalog.add_link(
        pystac.Link(
            rel="search",
            target=os.path.join(STAC_API_URL, "search"),
            media_type=pystac.MediaType.GEOJSON,
        )
    )

    # Link to webview for catalog
    root_catalog.add_link(
        pystac.Link(
            rel=pystac.RelType.ALTERNATE,
            target=CATALOG_FRONTEND_URL,
            media_type=pystac.MediaType.HTML,
            title="Hub Ocean Web Catalog",
        )
    )
    return root_catalog


def get_observables(dto: ResourceDto, odp_client: OdpClient) -> List[ObservableDto]:
    """
    Get observables associated with a dataset.
    """
    try:
        observables = odp_client.catalog.list(
            {"#AND": [{"#EQUALS": ["kind", ObservableDto.get_kind()]}, {"#EQUALS": ["$spec.ref", dto.qualified_name]}]}
        )
    except Exception as e:
        logging.info(f"Error fetching observables for dataset {dto.uuid}: {e}")
        observables = []

    return list(observables)


class ObservablesInfo:
    start_time: datetime = None
    end_time: datetime = None
    geometry: Dict[str, Any] = None
    bbox: List[float] = None
    time: datetime = None

    def add_observable(self, observable: ObservableDto):
        if observable.spec.observable_class == static_coverage_class.qualified_name:
            try:
                self.start_time = datetime.fromtimestamp(observable.spec.details["value"][0])
                self.end_time = datetime.fromtimestamp(observable.spec.details["value"][1])
            except ValueError as e:
                logging.info(f"Error parsing observable {observable.uuid}: {e}")
                raise
        elif observable.spec.observable_class == static_single_value_class.qualified_name:
            try:
                value = observable.spec.details["value"]
                if isinstance(value, (int, float)):
                    self.time = datetime.fromtimestamp(value)
                else:
                    self.time = datetime.fromisoformat(value)
            except (ValueError, TypeError) as e:
                logging.info(f"Error parsing observable {observable.uuid}: {e}")
                raise ValueError(f"Error parsing observable {observable.uuid}: {e}")
        elif observable.spec.observable_class == static_geometric_coverage_class.qualified_name:
            try:
                self.geometry = observable.spec.details.get("value")
                if self.geometry is None:
                    raise ValueError("Observable has no geometry")
                if "geometry" in self.geometry and "type" not in self.geometry:
                    self.geometry = self.geometry["geometry"]
                self.bbox = shapely.geometry.shape(self.geometry).bounds
            except (shapely.errors.ShapelyError, ValueError) as e:
                logging.info(f"Error parsing observable {observable.uuid}: {e}")
                raise ValueError(f"Invalid geometry in observable {observable.uuid}") from e
        else:
            raise ValueError(f"Observable class {observable.spec.observable_class} not supported")

    def get_default_time(self) -> datetime:
        """Returns default time to current time if no time is available."""
        if self.time is not None:
            return self.time
        if self.start_time is not None:
            return self.start_time
        return datetime.now(tz=timezone.utc)

    def get_temporal_extent(self) -> pystac.TemporalExtent:
        """Returns a pystac.TemporalExtent object based on the available time information."""
        if self.start_time and self.end_time:
            return pystac.TemporalExtent(intervals=[[self.start_time, self.end_time]])
        elif self.time:
            return pystac.TemporalExtent(intervals=[[self.time, None]])
        else:
            return pystac.TemporalExtent(intervals=[[None, None]])

    def get_spatial_extent(self) -> pystac.SpatialExtent:
        """Returns a pystac.SpatialExtent object based on the available spatial information.

        Defaults to the global extent if no spatial information is available.
        """
        if self.bbox:
            return pystac.SpatialExtent(bboxes=[self.bbox])
        return pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])

    @classmethod
    def from_observables(cls, observables: List[ObservableDto]) -> "ObservablesInfo":
        info = cls()
        for observable in observables:
            try:
                info.add_observable(observable)
            except ValueError:
                continue
        return info


def convert_dataset(dto: DatasetDto) -> pystac.Item:
    """
    Converts a Dataset DTO to a STAC Item.
    """
    observables_info = ObservablesInfo.from_observables(dto.spec.observables)

    if observables_info.geometry is None:
        observables_info.geometry = {
            "type": "Polygon",
            "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
        }
        observables_info.bbox = [-180, -90, 180, 90]

    if dto.spec.data_collection is None:
        # Raise an error if the dataset does not belong to a collection. The
        # reason for this is that this stac api implementation assumes that all
        # items follow the format /collections/{collection_id}/items/{feature_id}
        raise AssertionError(f"Dataset does not belong to a collection: {dto}")

    dataset_identifier = dto.metadata.name
    collection_identifier = dto.spec.data_collection.split("/")[-1]

    dataset_api_url = os.path.join(STAC_API_URL, "collections", collection_identifier, "items", dataset_identifier)

    # item_bbox = observables_info.bbox or [-180, -90, 180, 90]  # guarantee bbox is never None

    # Create a STAC Item
    item = pystac.Item(
        stac_extensions=[],
        href=dataset_api_url,
        id=str(dto.uuid),
        geometry=observables_info.geometry,
        bbox=observables_info.bbox,
        properties={},
        datetime=observables_info.get_default_time(),
        start_datetime=observables_info.start_time,
        end_datetime=observables_info.end_time,
        assets={},
        collection=str(collection_identifier),
    )

    # Add links

    # Update self link to make sure it has the correct media type
    item.remove_links("self")
    item.add_link(pystac.Link(rel="self", target=dataset_api_url, media_type=pystac.MediaType.GEOJSON))

    # Set root object (this is to get the correct root link)
    item.set_root(get_root_catalog())

    # Add link to parent collection
    item.add_link(
        pystac.Link(
            rel=pystac.RelType.COLLECTION,
            target=os.path.join(STAC_API_URL, "collections", collection_identifier),
            title=collection_identifier,
            media_type=pystac.MediaType.JSON,
        )
    )

    # Link to webview for catalog
    item.add_link(
        pystac.Link(
            rel=pystac.RelType.ALTERNATE,
            target=os.path.join(CATALOG_FRONTEND_URL, "dataset", dataset_identifier),
            media_type=pystac.MediaType.HTML,
            title="Hub Ocean Web Catalog",
        )
    )

    # Validate STAC Item
    try:
        item.validate()
    except pystac.STACValidationError as e:
        logging.warning("Validation failed for DatasetDto %s converted to a STAC Item %s: %s", dto.uuid, item, e)
        raise

    return item


def convert_collection(dto: DataCollectionDto) -> pystac.Collection:
    """
    Converts a DataCollection DTO to a STAC Collection.
    """
    observables_info = ObservablesInfo.from_observables(dto.spec.observables)

    extent = pystac.Extent(
        spatial=observables_info.get_spatial_extent(),
        temporal=observables_info.get_temporal_extent(),
    )

    # Determine the license name (default to "proprietary")
    license_name = "proprietary"
    license_href = None

    if dto.spec.distribution and dto.spec.distribution.license:
        license_obj = dto.spec.distribution.license  # This is an instance of License

        def normalize_license(li_name):
            li_name = li_name.replace(" ", "_")
            li_name = li_name.replace("(", "")
            li_name = li_name.replace(")", "")
            return li_name

        license_name = normalize_license(license_obj.name or license_name)  # License name
        license_href = license_obj.href  # URL to license text

    collection_api_url = os.path.join(STAC_API_URL, "collections", dto.metadata.name)

    # Create pystac.Collection
    collection = pystac.Collection(
        id=dto.metadata.name,
        description=dto.metadata.description or "",
        href=collection_api_url,
        title=dto.metadata.name,
        license=license_name,
        extent=extent,
    )

    # Add links for collection
    # Set root object (this is to get the correct root link)
    collection.set_root(get_root_catalog())

    # Parent link
    collection.add_link(
        pystac.Link(
            rel=pystac.RelType.PARENT,
            target=os.path.join(STAC_API_URL, "collections"),
            media_type=pystac.MediaType.JSON,
        )
    )

    # Items link
    collection.add_link(
        pystac.Link(
            rel=pystac.RelType.ITEMS,
            target=os.path.join(collection_api_url, "items"),
            media_type=pystac.MediaType.GEOJSON,
        )
    )

    # Link to webview for catalog
    collection.add_link(
        pystac.Link(
            rel=pystac.RelType.ALTERNATE,
            target=os.path.join(CATALOG_FRONTEND_URL, "collection", str(dto.metadata.name)),
            media_type=pystac.MediaType.HTML,
            title="Hub Ocean Web Catalog",
        )
    )

    # Add license link if href is available
    if license_href:
        collection.add_link(
            pystac.Link(
                rel="license",
                target=license_href,
                title=f"License: {license_name}",
            )
        )

    # Validate STAC collection
    try:
        collection.validate()
    except pystac.STACValidationError as e:
        logging.warning(
            "Validation failed for DatasetDto %s converted to a STAC Collection %s: %s", dto.uuid, collection, e
        )
        raise

    return collection
