"""
openBIS object creation and linking manager.
Handles creation of UV sheet experimental steps and child samples.
"""

from typing import Dict, Any, Optional, List
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
    
    def object_exists(self, code: str) -> bool:
        """
        Check if object with given code already exists.
        
        Args:
            code: Object code to check
            
        Returns:
            True if object exists, False otherwise
        """
        try:
            # Search for object by code in the project
            results = self.openbis.get_samples(code=code, project=self.project_path)
            
            if len(results) > 0:
                logger.debug(f"Object '{code}' already exists")
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
        duration: Any
    ) -> Optional[str]:
        """
        Create main experimental step object.
        
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
            # Create object with type "Sample" and provided code
            new_object = self.openbis.new_sample(
                type="Sample",
                code=code,
                project=self.project_path
            )
            
            # Set properties
            new_object.p.responsible_person = person
            
            # Set description with Date, Spacer and Duration
            description = self._build_description(date, spacer, duration)
            new_object.p.description = description
            
            # Save object first
            new_object.save()
            logger.info(f"Created experimental step object: {code}")
            
            # Get created object's permID
            created = self.openbis.get_sample(f"{self.project_path}/{code}")
            created_perm_id = created.permId
            logger.debug(f"Object permID: {created_perm_id}")
            
            # Link parents
            parents = []
            
            # Add Resin parent
            if resin_perm_id:
                try:
                    resin = self.openbis.get_sample(resin_perm_id)
                    parents.append(resin)
                    logger.info(f"Linked parent Resin: {resin_perm_id}")
                except Exception as e:
                    logger.error(f"Could not find parent Resin with permID {resin_perm_id}: {e}")
            
            # Add Instrument parent
            if instrument_perm_id:
                try:
                    instrument = self.openbis.get_sample(instrument_perm_id)
                    parents.append(instrument)
                    logger.info(f"Linked parent Instrument: {instrument_perm_id}")
                except Exception as e:
                    logger.error(f"Could not find parent Instrument with permID {instrument_perm_id}: {e}")
            
            # Update with parents if any were found
            if parents:
                created.parents = parents
                created.save()
                logger.info(f"Updated {code} with {len(parents)} parent(s)")
            
            return created_perm_id
            
        except Exception as e:
            logger.error(f"Error creating experimental step '{code}': {e}")
            return None
    
    def create_child_samples(
        self,
        parent_code: str,
        parent_perm_id: str,
        num_sheets: int
    ) -> List[str]:
        """
        Create N child sample objects.
        
        Args:
            parent_code: Parent object code
            parent_perm_id: Parent object permID
            num_sheets: Number of child samples to create
            
        Returns:
            List of created child permIDs
        """
        created_children = []
        
        try:
            # Get parent object
            parent = self.openbis.get_sample(parent_perm_id)
            logger.debug(f"Retrieved parent object: {parent_code}")
        except Exception as e:
            logger.error(f"Could not retrieve parent object {parent_code}: {e}")
            return created_children
        
        # Create child objects
        for i in range(1, num_sheets + 1):
            child_code = f"{parent_code}-{i}"
            
            try:
                # Create child object
                child = self.openbis.new_sample(
                    type="Sample",
                    code=child_code,
                    project=self.project_path
                )
                child.p.description = f"Child sample {i} of {parent_code}"
                
                # Set parent relationship
                child.parents = [parent]
                child.save()
                
                child_obj = self.openbis.get_sample(f"{self.project_path}/{child_code}")
                created_children.append(child_obj.permId)
                logger.info(f"Created child sample: {child_code}")
                
            except Exception as e:
                logger.error(f"Error creating child sample '{child_code}': {e}")
                continue
        
        logger.info(f"Created {len(created_children)}/{num_sheets} child samples for {parent_code}")
        return created_children
    
    def _build_description(self, date: Any = None, spacer: Any = None, duration: Any = None) -> str:
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
        
        if date and str(date).lower() not in ['nan', 'none', '']:
            parts.append(f"Date: {date}")
        
        if spacer and str(spacer).lower() not in ['nan', 'none', '']:
            parts.append(f"Spacer: {spacer}")
        
        if duration and str(duration).lower() not in ['nan', 'none', '']:
            parts.append(f"Duration: {duration} s")
        
        return " | ".join(parts) if parts else "UV Sheet Sample"
