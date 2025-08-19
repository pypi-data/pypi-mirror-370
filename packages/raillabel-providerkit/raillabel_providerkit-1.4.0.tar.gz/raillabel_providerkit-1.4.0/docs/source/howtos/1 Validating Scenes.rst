..
   Copyright DB InfraGO AG and contributors
   SPDX-License-Identifier: Apache-2.0

===================
1 Validating Scenes
===================

Motivation
##########
The validation of the project requirements should ideally be done as close to the source of the data as possible. This devkit therefore provides functionality to check for basic errors on the supplier side. If you are unsure whether your applications produce valid annotations, simply use the functions provided here to check. **Only send us data, if the methods below say that no errors are present.** If you find any bugs in the code, just hit us up and we will fix them as soon as possible (or you can create a PR).

Usage
#####

.. code-block:: python

    from pathlib import Path

    from raillabel_providerkit import validate

    scene_path = Path("path/to/scene.json")
    ontology_path = Path("path/to/ontology.yaml")  # ontology file that should be provided by us
    issues_in_scene = validate(scene_path, ontology_path)
    assert issues_in_scene == []

If this code does not raise any errors, you are good to go. If it does, read the content of the list `validate` returns carefully. It should tell you where the errors are. If you are unsure, contact your project partner or raise an issue on GitHub.

Under certain circumstances you might want to switch off certain validations. This should only be done if agreed upon with us. In this case, validate excepts use something like this

.. code-block:: python

    from pathlib import Path

    from raillabel_providerkit import validate

    scene_path = Path("path/to/scene.json")
    issues_in_scene = validate(scene_path, validate_for_dimensions=False)

If you have not been provided with an ontology file, just leave the field empty. The scene is then not checked against ontology issues.
