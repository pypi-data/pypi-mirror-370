"""Query helper functions (data access abstraction)."""
from . import db

def feature_rows():
    return db.query(
        """
        SELECT f.feature_key as feature_key, f.name, f.status,
            (SELECT COUNT(*) FROM spec_item s WHERE s.feature_key=f.feature_key AND s.status='VERIFIED') as verified_count,
            (SELECT COUNT(*) FROM spec_item s WHERE s.feature_key=f.feature_key AND s.status='FAILING') as failing_count,
            (SELECT COUNT(*) FROM spec_item s WHERE s.feature_key=f.feature_key AND s.status='UNTESTED') as untested_count,
            (SELECT COUNT(*) FROM spec_item s WHERE s.feature_key=f.feature_key AND s.status='PARTIAL') as partial_count
        FROM feature f ORDER BY f.name
        """
    )

def spec_row(spec_id: str):
    return db.query_one("SELECT * FROM spec_item WHERE id=?", (spec_id,))

