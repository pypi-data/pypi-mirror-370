<!-- markdownlint-disable first-line-heading -->
![Build Status](https://github.com/dmanuel64/pyciv7/actions/workflows/test.yml/badge.svg?branch=main)
![PyPI](https://img.shields.io/pypi/v/pyciv7)
![Python Version](https://img.shields.io/pypi/pyversions/pyciv7)
![License](https://img.shields.io/github/license/dmanuel64/pyciv7)


# `pyciv7`

Python bindings for the **Sid Meier’s Civilization VII SDK**.

Easily build, validate, and package Civilization 7 mods using Python instead of hand-writing `.modinfo` XML.

## Features

- **High-level mod definition**: Define your mods in Pydantic models and export `.modinfo` XML automatically.
- **Validation & recommendations**: Get warnings when mod metadata is missing or incorrectly formatted.
- **SQLAlchemy integration**: Embed SQLAlchemy queries directly into your mods instead of writing raw SQL files.
- **Settings auto-detection**: Automatically detects Civ7 installation and settings directories across Windows, macOS, and Linux.

## Quick Example

```python
import pyciv7
from pyciv7.modinfo import *
from sqlalchemy import text

sql_statement = text(
    "INSERT INTO Types"
    "\n        (Type,                              Kind)"
    "\nVALUES  ('TRADITION_FXS_CYLINDER_SEALS',    'KIND_TRADITION');"
    "\n"
    "\nINSERT INTO TraditionModifiers"
    "\n  ("
    "\n   TraditionType,"
    "\n   ModifierId"
    "\n  )"
    "\nVALUES ("
    "\n   'TRADITION_PANJI',"
    "\n   'MOD_FXS_TRADITION_PANJI_QUARTER_CULTURE'"
    "\n  ),"
    "\n  ("
    "\n   'TRADITION_PANJI',"
    "\n   'MOD_FXS_TRADITION_PANJI_QUARTER_CULTURE_ISLAND'"
    "\n  );"
)

mod = Mod(
    id="fxs-new-policies",
    version="1",
    properties=Properties(
        name="Antiquity Policies",
        description="Adds new policies to the Antiquity Age",
        authors="Firaxis",
        affects_saved_games=True,
    ),
    action_criteria=[
        Criteria(
            id="antiquity-age-current",
            conditions=[AgeInUse(age="AGE_ANTIQUITY")],
        )
    ],
    action_groups=[
        ActionGroup(
            id="antiquity-game",
            scope="game",
            criteria="antiquity-age-current",
            # Items can still be a relative path to a SQL/XML file
            actions=[UpdateDatabase(items=[sql_statement])],
        )
    ],
)

# If you want to use a dictionary instead of importing all the models, you can also do
# Mod.model_validate({"id": "fxs-new-policies", "properties": {"name": "Antiquity Policies"}, ... etc.})
pyciv7.build(mod)
```

This Python snippet produces a `.modinfo` XML similar to the SDK's "Getting Started" example:

```xml
<Mod id="fxs-new-policies" version="1" xmlns="ModInfo">
    <Properties>
        <Name>Antiquity Policies</Name>
        <Description>Adds new policies to the Antiquity Age</Description>
        <Authors>Firaxis</Authors>
        <AffectsSavedGames>1</AffectsSavedGames>
    </Properties>
    <ActionCriteria>
        <Criteria id="antiquity-age-current">
            <AgeInUse>AGE_ANTIQUITY</AgeInUse>
        </Criteria>
    </ActionCriteria>
    <ActionGroups>
        <ActionGroup id="antiquity-game" scope="game" criteria="antiquity-age-current">
            <Actions>
                <UpdateDatabase>
                    <Item>sql_statements/65a41eff-c3b5-4982-92d1-ee02ea02e9b8.sql</Item>
                </UpdateDatabase>
            </Actions>
        </ActionGroup>
    </ActionGroups>
</Mod>
```

## Installation

With `uv` (preferred):

```bash
uv add pyciv7
```

Or with `pip`:

```bash
pip install pyciv7
```
