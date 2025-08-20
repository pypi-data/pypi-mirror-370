import os
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError
from ..database.DatabaseManager import DatabaseManager, get_storage_path
from ..models.restricted_area_violation import RestrictedAreaViolationEntity

class RestrictedAreaRepository:
    """Handles storage and retrieval of restricted area violations in SQLite using SQLAlchemy."""

    def __init__(self):
        self.storage_dir = get_storage_path("restricted_violations")
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("default")
        os.makedirs(self.storage_dir, exist_ok=True)

    def get_latest_5_violations(self) -> list:
        """
        Retrieves the latest 5 restricted area violations ordered by the 'created_at' timestamp.

        Returns:
            list: A list of dictionaries representing restricted area violations.
        """
        try:
            latest_violations = (
                self.session.query(RestrictedAreaViolationEntity)
                .order_by(asc(RestrictedAreaViolationEntity.created_at))
                .limit(5)
                .all()
            )

            result = []
            for violation in latest_violations:
                timestamp = violation.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                result.append({
                    'person_id': violation.person_id,
                    'image': violation.image_path,
                    'image_tile': violation.image_tile_path,
                    'worker_source_id': violation.worker_source_id,
                    'worker_timestamp': timestamp,
                    'confidence_score': violation.confidence_score,
                    'b_box_x1': violation.b_box_x1,
                    'b_box_y1': violation.b_box_y1,
                    'b_box_x2': violation.b_box_x2,
                    'b_box_y2': violation.b_box_y2,
                })

            return result

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"❌ Database error while retrieving latest 5 violations: {e}")
            return []

    def delete_records_from_db(self, violation_data: list):
        """
        Deletes restricted area violation records from the database based on the provided data.

        Args:
            violation_data (list): List of dictionaries containing the violation data.
        """
        try:
            person_ids_to_delete = [data['person_id'] for data in violation_data]

            violations_to_delete = (
                self.session.query(RestrictedAreaViolationEntity)
                .filter(RestrictedAreaViolationEntity.person_id.in_(person_ids_to_delete))
                .all()
            )

            for violation in violations_to_delete:
                image_path = violation.image_path
                if not os.path.isabs(image_path):
                    image_path = str(get_storage_path("restricted_violations") / Path(image_path).relative_to("data/restricted_violations"))
                if os.path.exists(image_path):
                    os.remove(image_path)
                    logging.info(f"Deleted image file: {image_path}")
                else:
                    logging.warning(f"Image file not found for violation {violation.id}: {image_path}")

                self.session.delete(violation)

            self.session.commit()
            logging.info(f"Successfully deleted {len(violations_to_delete)} violation records.")

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"❌ Error occurred while deleting violation records: {e}")
