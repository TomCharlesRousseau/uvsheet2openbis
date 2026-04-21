"""
openBIS object creation and linking manager.
Handles creation of UV sheet experimental steps and child samples.
"""

from typing import Any, Optional, List
from utils.logging_config import get_logger
from config import Config

logger = get_logger()


class ObjectManager:
    """Manage creation and linking of openBIS objects."""

    def __init__(self, openbis):
        """
        Initialize object manager.

        Args:
            openbis: Connected pybis.Openbis instance
        """
        self.openbis = openbis
        self.config = Config()
        self.project_path = self.config.openbis_project_path
        # Get collection paths from config
        self.collection_exp_step = self._get_collection_exp_step_path()
        self.collection_samples = self._get_collection_samples_path()

    def _get_collection_exp_step_path(self) -> str:
        """
        Get collection path for storing experimental steps.

        Returns:
            Collection path in format /SPACE/PROJECT/COLLECTION
        """
        # Get collection name from config
        collection_name = self.config.collection_exp_step

        # Build full collection path
        collection_path = f"{self.project_path}/{collection_name}"
        logger.debug(f"Using experimental step collection path: {collection_path}")

        return collection_path

    def _get_collection_samples_path(self) -> str:
        """
        Get collection path for storing sample sheets.

        Returns:
            Collection path in format /SPACE/PROJECT/COLLECTION
        """
        # Get collection name from config
        collection_name = self.config.collection_samples

        # Build full collection path
        collection_path = f"{self.project_path}/{collection_name}"
        logger.debug(f"Using samples collection path: {collection_path}")

        return collection_path

    def object_exists(self, code: str) -> bool:
        """
        Check if object with given code already exists.
        Handles case-insensitive search since openBIS converts codes to uppercase.

        Args:
            code: Object code to check

        Returns:
            True if object exists, False otherwise
        """
        try:
            # Search for object by code in the experiment step collection
            # openBIS is case-insensitive for codes
            results = self.openbis.get_samples(
                code=code, collection=self.collection_exp_step
            )

            if len(results) > 0:
                logger.debug(
                    f"Object '{code}' already exists in {self.collection_exp_step}"
                )
                return True

            # Also check in samples collection as a safety net
            results = self.openbis.get_samples(
                code=code, collection=self.collection_samples
            )
            if len(results) > 0:
                logger.debug(
                    f"Object '{code}' already exists in {self.collection_samples}"
                )
                return True

            return False
        except Exception as e:
            logger.error(f"Error checking if object '{code}' exists: {e}")
            return False

    def create_experimental_step(
        self,
        code: str,
        person: str,
        date: str,
        resin_perm_id: str,
        instrument_perm_id: str,
        spacer: Any,
        duration: Any,
    ) -> Optional[str]:
        """
        Create main experimental step object as a sample within collection.

        Args:
            code: Object code
            person: Responsible person
            date: Experiment date
            resin_perm_id: Parent Resin permID
            instrument_perm_id: Parent Instrument permID
            spacer: Spacer value
            duration: Duration in seconds

        Returns:
            permID of created object or None if failed
        """
        try:
            # Create sample of type EXPERIMENTAL_STEP within collection
            new_object = self.openbis.new_sample(
                type="EXPERIMENTAL_STEP", code=code, collection=self.collection_exp_step
            )

            # Set the $name property
            new_object.p["$name"] = code

            # Set properties from config (skip invalid ones)
            object_props = self.config.object_properties
            for prop_key, prop_value in object_props.items():
                try:
                    setattr(new_object.p, prop_key, prop_value)
                    logger.debug(f"Set property {prop_key}={prop_value}")
                except Exception as e:
                    logger.debug(
                        f"Skipped property {prop_key} (not valid for EXPERIMENTAL_STEP): {e}"
                    )

            # Set description with Date, Spacer and Duration
            description = self._build_description(date, spacer, duration)
            new_object.p["experimental_step.experimental_description"] = description

            # Link parent materials using permIDs
            # Both resin and instrument are parents of the experimental step
            parents = []
            if resin_perm_id:
                parents.append(resin_perm_id)
                logger.debug(f"Added parent (Resin): {resin_perm_id}")
            if instrument_perm_id:
                parents.append(instrument_perm_id)
                logger.debug(f"Added parent (Instrument): {instrument_perm_id}")

            if parents:
                new_object.parents = parents
                logger.debug(f"Set {len(parents)} parents using permIDs")

            # Save object
            new_object.save()
            logger.info(f"Created experimental step object: {code}")

            # Get created object's permID
            created = self.openbis.get_sample(f"{self.collection_exp_step}/{code}")
            created_perm_id = created.permId
            logger.debug(f"Object permID: {created_perm_id}")

            return created_perm_id

        except Exception as e:
            logger.error(f"Error creating experimental step '{code}': {e}")
            return None

    def create_child_samples(
        self, parent_code: str, parent_perm_id: str, num_sheets: int
    ) -> List[str]:
        """
        Create N child sample objects with parent relationship.

        Args:
            parent_code: Parent object code
            parent_perm_id: Parent object permID
            num_sheets: Number of child samples to create

        Returns:
            List of created child permIDs
        """
        created_children = []

        # Verify parent exists
        try:
            parent = self.openbis.get_sample(parent_perm_id)
            logger.debug(f"Retrieved parent object: {parent_code}")
        except Exception as e:
            logger.error(f"Could not retrieve parent object {parent_code}: {e}")
            return created_children

        # Create child objects
        for i in range(1, num_sheets + 1):
            child_code = f"{parent_code}-{i}"

            try:
                # Create child object in samples collection
                child = self.openbis.new_sample(
                    type="Sample", code=child_code, collection=self.collection_samples
                )

                # Set the $name property
                child.p["$name"] = child_code

                # Set properties from config (skip invalid ones)
                object_props = self.config.object_properties
                for prop_key, prop_value in object_props.items():
                    try:
                        setattr(child.p, prop_key, prop_value)
                        logger.debug(f"Set property {prop_key}={prop_value} on child")
                    except Exception as e:
                        logger.debug(f"Skipped property {prop_key} on child: {e}")

                try:
                    child.p.description = f"Child sample {i} of {parent_code}"
                except Exception as e:
                    logger.debug(f"Could not set description on child: {e}")

                # Link parent using permID (not parent object)
                child.parents = [parent_perm_id]
                logger.debug(f"Set parent for {child_code}: {parent_perm_id}")

                child.save()

                # Get created child's permID
                child_obj = self.openbis.get_sample(
                    f"{self.collection_samples}/{child_code}"
                )
                created_children.append(child_obj.permId)
                logger.info(
                    f"Created child sample: {child_code} with parent {parent_code}"
                )

            except Exception as e:
                logger.error(f"Error creating child sample '{child_code}': {e}")
                continue

        logger.info(
            f"Created {len(created_children)}/{num_sheets} child samples for {parent_code}"
        )
        return created_children

    def _build_description(
        self, date: Any = None, spacer: Any = None, duration: Any = None
    ) -> str:
        """
        Build object description from Date, Spacer and Duration.

        Args:
            date: Experiment date
            spacer: Spacer value
            duration: Duration value

        Returns:
            Formatted description string
        """
        parts = []

        if date and str(date).lower() not in ["nan", "none", ""]:
            parts.append(f"Date: {date}")

        if spacer and str(spacer).lower() not in ["nan", "none", ""]:
            parts.append(f"Spacer: {spacer}")

        if duration and str(duration).lower() not in ["nan", "none", ""]:
            parts.append(f"Duration: {duration} s")

        return " | ".join(parts) if parts else "UV Sheet Sample"
