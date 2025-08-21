"""
Python bindings for Civilization 7's SDK.

Example:

    ```python
    import pyciv7
    from pyciv7.modinfo import *

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
                actions=[UpdateDatabase(items=["data/antiquity-traditions.xml"])],
            )
        ],
    )

    pyciv7.build(mod)
    ```

    Will produce the same XML as shown in the `Getting Started` guide:

    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <Mod id="fxs-new-policies" version="1"
        xmlns="ModInfo">
        <Properties>
            <Name>Antiquity Policies</Name>
            <Description>Adds new policies to the Antiquity Age</Description>
            <Authors>Firaxis</Authors>
            <AffectsSavedGames>1</AffectsSavedGames>
        </Properties>
        <Dependencies>
        </Dependencies>
        <References>
        </References>
        <ActionCriteria>
            <Criteria id="antiquity-age-current">
                <AgeInUse>AGE_ANTIQUITY</AgeInUse>
            </Criteria>
        </ActionCriteria>
        <ActionGroups>
            <ActionGroup id="antiquity-game" scope="game" criteria="antiquity-age-current">
                <Actions>
                    <UpdateDatabase>
                        <Item>data/antiquity-traditions.xml</Item>
                    </UpdateDatabase>
                </Actions>
            </ActionGroup>
        </ActionGroups>
    </Mod>
    ```
"""

from pyciv7.modinfo import *
from pyciv7.runner import build, run
import pyciv7.databases

__all__ = ["build", "run"]
