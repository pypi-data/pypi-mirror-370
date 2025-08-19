# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path

from raillabel import Scene
from raillabel.json_format import JSONScene

from raillabel_providerkit.validation import Issue

from . import (
    validate_dimensions,
    validate_empty_frames,
    validate_horizon,
    validate_missing_ego_track,
    validate_ontology,
    validate_rail_side,
    validate_schema,
    validate_sensors,
    validate_uris,
)


def validate(  # noqa: C901, PLR0913
    scene_source: dict | Path,
    ontology_source: dict | Path | None = None,
    validate_for_empty_frames: bool = True,
    validate_for_rail_side_order: bool = True,
    validate_for_missing_ego_track: bool = True,
    validate_for_sensors: bool = True,
    validate_for_uris: bool = True,
    validate_for_dimensions: bool = True,
    validate_for_horizon: bool = True,
) -> list[Issue]:
    """Validate a scene based on the Deutsche Bahn Requirements.

    Args:
        scene_source: The scene either as a dictionary or as a Path to the scene source file.
        ontology_source: The dataset ontology as a dictionary or as a Path to the ontology YAML
            file. If not None, issues are returned if the scene contains annotations with invalid
            attributes or object types. Default is None.
        validate_for_empty_frames (optional): If True, issues are returned if the scene contains
            frames without annotations. Default is True.
        validate_for_rail_side_order: If True, issues are returned if the scene contains track with
            a mismatching rail side order. Default is True.
        validate_for_missing_ego_track: If True, issues are returned if the scene contains frames
            where the ego track (the track the recording train is driving on) is missing. Default is
            True.
        validate_for_sensors: If True, issues are returned if the scene contains sensors that are
            not supported or have the wrong sensor type.
        validate_for_uris: If True, issues are returned if the uri fields in the scene contain
            unsupported values.
        validate_for_dimensions: If True, issues are returned if the dimensions of cuboids are
            outside the expected values range.
        validate_for_horizon: If True, issues are returned if annotations cross the horizon.

    Returns:
        List of all requirement errors in the scene. If an empty list is returned, then there are no
        errors present and the scene is valid.
    """
    if isinstance(scene_source, Path):
        with scene_source.open() as scene_file:
            scene_source = json.load(scene_file)

    schema_errors = validate_schema(scene_source)
    if schema_errors != []:
        return schema_errors

    scene = Scene.from_json(JSONScene(**scene_source))
    errors = []

    if ontology_source is not None:
        errors.extend(validate_ontology(scene, ontology_source))

    if validate_for_empty_frames:
        errors.extend(validate_empty_frames(scene))

    if validate_for_rail_side_order:
        errors.extend(validate_rail_side(scene))

    if validate_for_missing_ego_track:
        errors.extend(validate_missing_ego_track(scene))

    if validate_for_sensors:
        errors.extend(validate_sensors(scene))

    if validate_for_uris:
        errors.extend(validate_uris(scene))

    if validate_for_dimensions:
        errors.extend(validate_dimensions(scene))

    if validate_for_horizon:
        errors.extend(validate_horizon(scene))

    return errors
