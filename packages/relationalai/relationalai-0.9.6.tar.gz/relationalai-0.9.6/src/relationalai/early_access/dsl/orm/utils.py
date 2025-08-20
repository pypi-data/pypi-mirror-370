from __future__ import annotations

import keyword
import re
from relationalai.early_access.dsl.core.utils import camel_to_snake, to_rai_way_string
import relationalai.early_access.dsl.orm.relationships as orm_qb


# This method generates a string containing a standard abbreviated name for the given reading, generated according
# to the rai way conventions.
def generate_rai_way_name(reading: orm_qb.RelationshipReading):
    # These two dict and the roles array are indexed in same way, using the role position in the madlib
    following_texts = extract_roles_data_from_madlib(reading)
    roles = reading._roles()

    # A role name must be different from player and player_i (used for multiple occurrences of the same player)
    def get_role_name(idx: int):
        player = roles[idx].player()._name.lower()
        role_name = reading._fields[idx].name
        if role_name != player and ("_" not in role_name or not role_name.split("_")[1].isdigit()):
            return role_name
        return ""

    # We invoke this method with an index to compose together the textual parts of a single role (prefix, role/player
    # name, postfix and following text.
    def compose_role_textual_parts(idx: int, drop_is_has=True):
        textual_parts = []
        role = roles[idx]
        if role.prefix:
            textual_parts.append(camel_to_snake(role.prefix))
        if idx > 0:
            role_name = get_role_name(idx)
            textual_parts.append(camel_to_snake(role_name) if role_name else camel_to_snake(role.player()._name))
        if role.postfix:
            textual_parts.append(camel_to_snake(role.postfix))
        if following_texts[idx]:
            rai_way_string = to_rai_way_string(following_texts[idx], drop_is_has)
            if rai_way_string:
                textual_parts.append(rai_way_string)
        return '_'.join(textual_parts).replace(" ", "_")

    # Generate the rai way name for the binary case, when most of the role data in not present.
    def generate_simple_binary_name():
        simple_name = to_rai_way_string(following_texts[0])
        if (simple_name and not following_texts[1] and not keyword.iskeyword(simple_name) and
                not roles[0].prefix and not roles[0].postfix and not roles[1].prefix and not roles[1].postfix):
            return simple_name
        return None

    # Unary case
    if len(roles) == 1:
        return compose_role_textual_parts(0)
    # Binary case
    elif len(roles) == 2:
        # If there exists a role name for the second player, use it as rai way name
        if get_role_name(1):
            return camel_to_snake(get_role_name(1))
        else:
            simple_binary_name = generate_simple_binary_name()
            if simple_binary_name:
                return simple_binary_name
            # General case: process all the components of both roles
            else:
                first_role_component = compose_role_textual_parts(0)
                second_role_component = compose_role_textual_parts(1, False)
                rel_name = f"{first_role_component}_{second_role_component}" if first_role_component != "" else second_role_component
                return rel_name
    # Ternary case and beyond
    else:
        all_roles_components = []
        for i, role in enumerate(roles):
            role_component = compose_role_textual_parts(i,False)
            all_roles_components.append(role_component)
        rel_name = "_".join(all_roles_components)
        return rel_name


# Returns the dictionary of texts following a role (empty string if not present) indexed by the role position
def extract_roles_data_from_madlib(reading: orm_qb.RelationshipReading):
    # This pattern capture the player name (with optional role name) and the following text for each
    # role in the madlib string
    # \{([^{}]*)\}   Player or role_name:Player
    # ([^{]*)       Following text
    pattern = r"\{([^{}]*)\}([^{]*)"

    matches = re.findall(pattern, reading._madlib)
    following_texts = dict()

    for i, (_, follows) in enumerate(matches):
        following_texts[i] = follows.strip()
    return following_texts
