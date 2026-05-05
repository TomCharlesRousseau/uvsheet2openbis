"""Person lookup utilities for PERSON.BAM objects in openBIS"""
from utils.logging_config import get_logger

logger = get_logger()


def get_person_by_permid(o, permid, return_field=None):
    """
    Get person information by PermID.

    Args:
        o: Openbis connection object
        permid: PermID of the PERSON.BAM object
        return_field: Optional. Specific field(s) to return.
                     Can be a string (e.g., 'bam_username') or list (e.g., ['name', 'bam_username'])
                     If None, returns all properties as dictionary

    Returns:
        If return_field is None: Dictionary with all person properties
        If return_field is a string: The value of that property
        If return_field is a list: Dictionary with only those properties
        Returns None if person not found
    """
    try:
        person = o.get_sample(permid)

        if person is None:
            logger.warning(f"No person found with PermID: {permid}")
            return None

        # Extract all properties
        all_props = {
            "permid": person.permId,
            "name": getattr(person.props, "$name", None),
            "family_name": getattr(person.props, "family_name", None),
            "given_name": getattr(person.props, "given_name", None),
            "bam_username": getattr(person.props, "bam_username", None),
            "bam_oe": getattr(person.props, "bam_oe", None),
        }

        # Return based on return_field parameter
        if return_field is None:
            return all_props
        elif isinstance(return_field, str):
            return all_props.get(return_field, None)
        elif isinstance(return_field, list):
            return {k: all_props[k] for k in return_field if k in all_props}
        else:
            return all_props

    except Exception as e:
        logger.error(f"Error getting person by PermID: {e}")
        return None


def get_person_by_bam_username(o, bam_username, return_field=None):
    """
    Get person information by BAM username.

    Args:
        o: Openbis connection object
        bam_username: BAM username (bam_username property) of the PERSON.BAM object
        return_field: Optional. Specific field(s) to return.
                     Can be a string (e.g., 'permid') or list (e.g., ['permid', 'name'])
                     If None, returns all properties as dictionary

    Returns:
        If return_field is None: Dictionary with all person properties
        If return_field is a string: The value of that property
        If return_field is a list: Dictionary with only those properties
        Returns None if person not found
    """
    try:
        # Get all PERSON.BAM objects
        objects = list(o.get_samples(type="PERSON.BAM"))

        # Search for matching username
        for person in objects:
            username = getattr(person.props, "bam_username", None)
            if username and username.upper() == bam_username.upper():
                # Found matching person
                all_props = {
                    "permid": person.permId,
                    "name": getattr(person.props, "$name", None),
                    "family_name": getattr(person.props, "family_name", None),
                    "given_name": getattr(person.props, "given_name", None),
                    "bam_username": getattr(person.props, "bam_username", None),
                    "bam_oe": getattr(person.props, "bam_oe", None),
                }

                # Return based on return_field parameter
                if return_field is None:
                    return all_props
                elif isinstance(return_field, str):
                    return all_props.get(return_field, None)
                elif isinstance(return_field, list):
                    return {k: all_props[k] for k in return_field if k in all_props}
                else:
                    return all_props

        logger.warning(f"No person found with bam_username: {bam_username}")
        return None

    except Exception as e:
        logger.error(f"Error getting person by bam_username: {e}")
        return None


def get_person_by_name(o, name, return_field=None):
    """
    Get person information by name ($name property).

    Args:
        o: Openbis connection object
        name: Full name ($name property) of the PERSON.BAM object
        return_field: Optional. Specific field(s) to return.
                     Can be a string (e.g., 'bam_username') or list (e.g., ['name', 'bam_username'])
                     If None, returns all properties as dictionary

    Returns:
        If return_field is None: Dictionary with all person properties
        If return_field is a string: The value of that property
        If return_field is a list: Dictionary with only those properties
        Returns None if person not found
    """
    try:
        # Get all PERSON.BAM objects
        objects = list(o.get_samples(type="PERSON.BAM"))

        # Search for matching name
        for person in objects:
            person_name = getattr(person.props, "$name", None)
            if person_name and person_name.upper() == name.upper():
                # Found matching person
                all_props = {
                    "permid": person.permId,
                    "name": person_name,
                    "family_name": getattr(person.props, "family_name", None),
                    "given_name": getattr(person.props, "given_name", None),
                    "bam_username": getattr(person.props, "bam_username", None),
                    "bam_oe": getattr(person.props, "bam_oe", None),
                }

                # Return based on return_field parameter
                if return_field is None:
                    return all_props
                elif isinstance(return_field, str):
                    return all_props.get(return_field, None)
                elif isinstance(return_field, list):
                    return {k: all_props[k] for k in return_field if k in all_props}
                else:
                    return all_props

        logger.warning(f"No person found with name: {name}")
        return None

    except Exception as e:
        logger.error(f"Error getting person by name: {e}")
        return None


def get_persons_by_property(o, property_name, property_value, return_fields=None):
    """
    Get all persons matching a specific property value.

    Args:
        o: Openbis connection object
        property_name: Property to filter by (e.g., 'bam_oe', 'family_name')
        property_value: Value to match
        return_fields: Optional. Specific field(s) to return in each result.
                      Can be a string (e.g., 'bam_username') or list (e.g., ['name', 'bam_username'])
                      If None, returns all properties for each person

    Returns:
        List of dictionaries (or values if return_fields is a string) with person information
    """
    try:
        # Get all PERSON.BAM objects
        objects = list(o.get_samples(type="PERSON.BAM"))
        matching_persons = []

        # Search for matching property
        for person in objects:
            prop_value = getattr(person.props, property_name, None)
            if prop_value and str(prop_value).upper() == str(property_value).upper():
                # Found matching person
                all_props = {
                    "permid": person.permId,
                    "name": getattr(person.props, "$name", None),
                    "family_name": getattr(person.props, "family_name", None),
                    "given_name": getattr(person.props, "given_name", None),
                    "bam_username": getattr(person.props, "bam_username", None),
                    "bam_oe": getattr(person.props, "bam_oe", None),
                }

                # Filter based on return_fields parameter
                if return_fields is None:
                    matching_persons.append(all_props)
                elif isinstance(return_fields, str):
                    matching_persons.append(all_props.get(return_fields, None))
                elif isinstance(return_fields, list):
                    matching_persons.append(
                        {k: all_props[k] for k in return_fields if k in all_props}
                    )
                else:
                    matching_persons.append(all_props)

        return matching_persons

    except Exception as e:
        logger.error(f"Error getting persons by property: {e}")
        return []
